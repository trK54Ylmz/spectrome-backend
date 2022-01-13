import bcrypt
import pytz
from flask import Blueprint
from datetime import datetime
from db.model import Forgot, SessionToken, User, UserStatus
from db.service import ForgotService, SessionTokenService, UserService
from random import randint
from server import app
from server.message import Message
from server.session import Session
from task.account import create_account_task, activation_task, forgot_task
from util.hash import Hash
from validation.account import (
    ActivateForm, ActivationForm, ForgotForm, ResetForm, SignInForm, SignUpForm
)

account = Blueprint('account', app.name)


@account.route('/login', methods=['POST'])
def login():
    """
    Sign in to user account

    :rtype: flask.Response
    """
    m = Message()
    form = SignInForm()

    # return error if validation failed
    if not form.validate():
        m.message = form.error()
        return m.json()

    login_id = form.login_id.data
    password = form.password.data

    user_service = UserService()

    # get user by e-mail address or username
    user = user_service.get_by_email_or_username(login_id, login_id)

    # we don't have this user details in our database
    if user is None:
        m.message = 'User could not found.'
        return m.json()

    # generate hash password and check
    hp = user.password.encode('utf-8')
    if not bcrypt.checkpw(password.encode('utf-8'), hp):
        m.message = 'User could not found.'
        return m.json()

    # user must be activated
    if user.status != UserStatus.ACTIVATED:
        st_service = SessionTokenService()

        # delete session tokens of the current user
        st_service.delete_by_user_id(user.uid)

        token_hash = Hash.uuid()

        # create session token
        token = SessionToken()
        token.user_id = user.uid
        token.token = token_hash
        token.create_time = datetime.now(tz=pytz.UTC)

        # create session token service
        st_service.create(token)

        m.message = 'User is not activated.'
        m.activation = False
        m.token = token_hash
        return m.json()

    # update last login time
    user.last_login = datetime.now(tz=pytz.UTC)
    user_service.update(user)

    m.status = True

    # create user session
    session_code = Session.create(user)

    # set session code to response object
    m.session = session_code

    return m.json()


@account.route('/create', methods=['POST'])
def create():
    """
    Create new user account

    :rtype: flask.Response
    """
    m = Message()
    form = SignUpForm()

    # return error if validation failed
    if not form.validate():
        m.message = form.error()
        return m.json()

    # predefined blocked username list
    blocked_names = ['me']
    if form.username.data in blocked_names:
        m.message = 'Cannot use this username.'
        return m.json()

    user_service = UserService()

    # check if username already exists
    user = user_service.get_by_username(form.username.data)
    if user is not None:
        m.message = 'This username already taken.'
        m.exists = True
        return m.json()

    # check if e-mail address already exists
    user = user_service.get_by_email(form.email.data)
    if user is not None:
        m.message = 'This e-mail address already exists. Would you like to sign in.'
        m.exists = True
        return m.json()

    # generate e-mail authentication code
    codes = []
    for _ in range(6):
        codes.append(str(randint(0, 9)))

    # hash password
    hp = bcrypt.hashpw(form.password.data.encode('utf-8'), bcrypt.gensalt())

    # create user instance
    user = User()
    user.phone = form.phone.data
    user.email = form.email.data
    user.username = form.username.data
    user.password = hp.decode('utf-8')
    user.name = form.name.data
    user.code = ''.join(codes)
    user.status = UserStatus.CREATED
    user.create_time = datetime.now(tz=pytz.UTC)

    # crete new user
    user_service.create(user)

    # send e-mail to user
    create_account_task.delay(user_id=user.uid)

    st_service = SessionTokenService()

    # delete session tokens of the current user
    st_service.delete_by_user_id(user.uid)

    token_hash = Hash.uuid()

    # create session token
    token = SessionToken()
    token.user_id = user.uid
    token.token = token_hash
    token.create_time = datetime.now(tz=pytz.UTC)

    # create session token service
    st_service.create(token)

    m.status = True
    m.token = token_hash
    return m.json()


@account.route('/activation', methods=['POST'])
def activation():
    """
    Send activation code

    :rtype: flask.Response
    """
    m = Message()
    form = ActivationForm()

    # return error if validation failed
    if not form.validate():
        m.message = form.error()
        return m.json()

    st_service = SessionTokenService()

    # get session token by token and user id
    token = st_service.get_by_token(form.token.data)
    if token is None:
        m.message = 'Activation token does not exists.'
        return m.json()

    now = datetime.now(tz=pytz.UTC)
    diff = (now - token.create_time).seconds
    if diff < 10:
        m.message = 'You have just requested for activation code. Try a bit later.'
        return m.json()

    user_service = UserService()

    # get user by using user id
    user = user_service.get_by_id(token.user_id)
    if user is None:
        m.message = 'User could not found.'
        return m.json()

    # user account must be activation wait
    if user.status != UserStatus.ACTIVATION_WAIT:
        m.message = 'This account is not able to activate.'
        return m.json()

    # delete current session token
    st_service.delete_by_user_id(user.uid)

    token_hash = Hash.uuid()

    # create session token
    token = SessionToken()
    token.user_id = user.uid
    token.token = token_hash
    token.create_time = datetime.now(tz=pytz.UTC)

    # create session token service
    st_service.create(token)

    # generate e-mail authentication code
    codes = []
    for _ in range(6):
        codes.append(str(randint(0, 9)))

    # generate new user code
    user.code = ''.join(codes)
    user.update_time = datetime.now(tz=pytz.UTC)

    # update user instance
    user_service.update(user)

    m.token = token_hash
    m.status = True
    return m.json()


@account.route('/activate', methods=['POST'])
def activate():
    """
    Activate user account

    :rtype: flask.Response
    """
    m = Message()
    form = ActivateForm()

    # return error if validation failed
    if not form.validate():
        m.message = form.error()
        return m.json()

    user_service = UserService()

    # get user by code
    code = str(form.code.data)
    user = user_service.get_by_code(code)
    if user is None:
        m.message = 'Activation code does not exists.'
        return m.json()

    st_service = SessionTokenService()

    # get session token by token and user id
    token = st_service.get_by_token_and_user_id(form.token.data, user.uid)
    if token is None:
        m.message = 'Activation token does not exists.'
        return m.json()

    # create time and sent time should be so close
    sent_time = token.create_time
    now = datetime.now(tz=pytz.UTC)
    diff = (now - sent_time).days

    # expired activation code
    if diff > 2:
        m.expired = True
        m.message = 'Activation code is expired.'
        return m.json()

    # update user status
    user.code = None
    user.status = UserStatus.ACTIVATED

    # update user instance
    user_service.update(user)

    # create user session
    session_code = Session.create(user)

    # set session code to response object
    m.session = session_code
    m.status = True

    # activation task
    activation_task.delay(user_id=user.uid)

    return m.json()


@account.route('/forgot', methods=['POST'])
def forgot():
    """
    Send forgot password mail

    :rtype: flask.Response
    """
    m = Message()
    form = ForgotForm()

    # return error if validation failed
    if not form.validate():
        m.message = form.error()
        return m.json()

    us = UserService()

    # get user by username
    user = us.get_by_username(form.username.data)
    if user is None or user.phone != form.phone.data:
        m.message = 'User could not found.'
        return m.json()

    fs = ForgotService()

    # get forgot password by user id
    forgot = fs.get_by_user_id(user.uid)
    if forgot is not None:
        now = datetime.now(tz=pytz.UTC)
        diff = (now - forgot.create_time).seconds

        if diff < 10:
            m.message = 'Forgot password e-mail has been sent recently.'
            return m.json()

        # remove old forgot password instance
        fs.remove(forgot)

    # generate forgot passwordcode
    codes = []
    for _ in range(6):
        codes.append(str(randint(0, 9)))

    forgot = Forgot()
    forgot.user_id = user.uid
    forgot.code = ''.join(codes)
    forgot.token = Hash.uuid()
    forgot.create_time = datetime.now(tz=pytz.UTC)

    # create new forgot password
    fs.create(forgot)

    # send e-mail
    forgot_task.delay(user_id=user.uid)

    m.status = True
    m.token = forgot.token

    return m.json()


@account.route('/reset', methods=['POST'])
def reset():
    """
    Reset user password

    :rtype: flask.Response
    """
    m = Message()
    form = ResetForm()

    # validate form
    if not form.validate():
        m.message = form.error()
        return m.json()

    fs = ForgotService()

    # get forgot password by code
    forgot = fs.get_by_code(form.code.data)
    if forgot is None or forgot.token != form.token.data:
        m.message = 'The code could not match.'
        return m.json()

    now = datetime.now(tz=pytz.UTC)
    diff = (now - forgot.create_time).days

    if diff > 1:
        m.message = 'The forgot request is too old. Please get new one.'
        return m.json()

    us = UserService()

    # get user by user id
    user = us.get_by_id(forgot.user_id)
    if user is None:
        m.message = 'The user could not found.'
        return m.json()

    # user should not be banned or something
    if user.status != UserStatus.ACTIVATED:
        m.message = 'The user must be activated.'
        return m.json()

    # remove old record
    fs.remove(forgot)

    # hash password
    hp = bcrypt.hashpw(form.password.data.encode('utf-8'), bcrypt.gensalt())

    user.password = hp.decode('utf-8')

    # update password and save
    us.update(user)

    m.status = True

    return m.json()


@account.route('/out', methods=['GET'])
def sign_out():
    """
    Sign out from current session

    :rtype: flask.Response
    """
    m = Message(status=True)

    # get user session
    session = Session.get()

    # remove session
    Session.remove(session.user_id)

    return m.json()
