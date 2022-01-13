import pytz
from datetime import datetime
from db.model import Circle, Intention, UserStatus
from db.service import CircleService, IntentionService, UserService
from flask import Blueprint
from server import app
from server.cache import redis
from server.message import Message
from server.session import Session
from task.user import invitation_task
from validation.user import CircleAcceptForm, InviteForm, LocationForm, NotificationForm
from task.user import circle_task, uncircle_task
from util.config import config
from util.hash import Hash

user = Blueprint('user', app.name)


@user.route('/request', methods=['GET'])
def get_requests():
    """
    Get list of circles requests

    :return: flask.Response
    """
    m = Message()

    session = Session.get()

    iss = IntentionService()

    # get unsent intentions
    intentions = iss.get_by_target_id(session.user_id)

    # return empty response
    if len(intentions) == 0:
        m.intentions = []
        m.status = True
        return m.json()

    items = []
    for it in intentions:
        intention = {
            'code': it.code,
            'create_time': it.create_time.isoformat()
        }

        name = 'default' if it.token is None else it.token
        user = {
            'name': it.name,
            'username': it.username,
            'photo_url': f'https://{config.app.cdn}/profile/{name}/1.jpg',
        }

        item = {
            'intention': intention,
            'user': user,
        }

        items.append(item)

    m.intentions = items
    m.status = True

    return m.json()


@user.route('/request/count', methods=['GET'])
def count_request():
    """
    Get number of cicles requests

    :return: flask.Response
    """
    m = Message()

    session = Session.get()

    # create user code by using target user id
    user_code = Hash.md5(str(session.user_id))

    # get request count
    count = redis.get(f'cr.{user_code}')
    if count is None:
        count = 0

    # set count value
    m.count = int(count)
    m.status = True

    return m.json()


@user.route('/request/seen', methods=['POST'])
def request_seen():
    """
    Set circle requests as seen

    :return: flask.Response
    """
    m = Message()

    session = Session.get()

    # create user code by using target user id
    user_code = Hash.md5(str(session.user_id))

    # update request count to zero
    redis.set(f'cr.{user_code}', 0)

    m.status = True

    return m.json()


@user.route('/add/p/<username>', methods=['POST'])
def add_circle(username):
    """
    Add user in circles by given username

    :param str username: username of the user
    :rtype: flask.Response
    """
    m = Message()

    session = Session.get()

    # these user names are not allowed
    if username in ['me', session.username]:
        m.message = 'The user could not found.'
        return m.json()

    us = UserService()

    # get user by username
    from_user = us.get_by_username(session.username)
    if from_user is None:
        m.message = 'The user could not found.'
        return m.json()

    # get user by username
    to_user = us.get_by_username(username)
    if to_user is None:
        m.message = 'The user could not found.'
        return m.json()

    if to_user.status != UserStatus.ACTIVATED:
        m.message = 'The user should be activated.'
        return m.json()

    iss = IntentionService()

    # get intention by from and to ids
    intention = iss.get_by_from_to(
        from_id=from_user.uid,
        to_id=to_user.uid
    )

    # user already had an intention
    if intention is not None:
        m.status = True
        return m.json()

    intention = Intention()
    intention.from_id = from_user.uid
    intention.to_id = to_user.uid
    intention.code = Hash.uuid()
    intention.sent = False
    intention.create_time = datetime.now(tz=pytz.UTC)

    # create new intention
    iss.create(intention)

    # create user code by using target user id
    user_code = Hash.md5(str(to_user.uid))

    # increase request count
    redis.incr(f'cr.{user_code}')

    m.status = True
    return m.json()


@user.route('/remove/p/<username>', methods=['POST'])
def remove_circle(username):
    """
    Remove user from circle by given username

    :param str username: username of the user
    :rtype: flask.Response
    """
    m = Message()

    session = Session.get()

    # these user names are not allowed
    if username in ['me', session.username]:
        m.message = 'The user could not found.'
        return m.json()

    us = UserService()

    # get user by username
    from_user = us.get_by_username(session.username)
    if from_user is None:
        m.message = 'The user could not found.'
        return m.json()

    # get user by username
    to_user = us.get_by_username(username)
    if to_user is None:
        m.message = 'The user could not found.'
        return m.json()

    if to_user.status != UserStatus.ACTIVATED:
        m.message = 'The user should be activated.'
        return m.json()

    cs = CircleService()

    # get circle user
    circle = cs.get_by_from_to(
        from_id=from_user.uid,
        to_id=to_user.uid
    )

    # user already circle
    if circle is None:
        m.status = True
        return m.json()

    # remove circle
    cs.remove(circle)

    # decrease number of circle
    uncircle_task.delay(from_id=from_user.uid, to_id=to_user.uid)

    m.status = True
    return m.json()


@user.route('/cancel/p/<username>', methods=['POST'])
def cancel_request(username):
    """
    Cancel circle request

    :param str username: username of the user
    :rtype: flask.Response
    """
    m = Message()

    session = Session.get()

    # these user names are not allowed
    if username in ['me', session.username]:
        m.message = 'The user could not found.'
        return m.json()

    us = UserService()

    # get user by username
    from_user = us.get_by_username(session.username)
    if from_user is None:
        m.message = 'The user could not found.'
        return m.json()

    # get user by username
    to_user = us.get_by_username(username)
    if to_user is None:
        m.message = 'The user could not found.'
        return m.json()

    if to_user.status != UserStatus.ACTIVATED:
        m.message = 'The user should be activated.'
        return m.json()

    iss = IntentionService()

    # get intention by from and to ids
    intention = iss.get_by_from_to(
        from_id=from_user.uid,
        to_id=to_user.uid
    )

    # user already had an intention
    if intention is None:
        m.status = True
        return m.json()

    # cancel circle add request
    iss.remove(intention)

    m.status = True
    return m.json()


@user.route('/circle/accept', methods=['POST'])
def accept_request():
    """
    Accept circle request

    :retype: flask.Response
    """
    m = Message()

    form = CircleAcceptForm()

    # validate form
    if not form.validate():
        m.message = form.error()
        return m.json()

    # get active session
    session = Session.get()

    iss = IntentionService()

    # get intention by code
    it = iss.get_by_code(form.code.data)
    if it is None:
        m.message = 'The circle request could not found.'
        return m.json()

    # only active session can accept their own request
    if session.user_id != it.to_id:
        m.message = 'The circle request could not found.'
        return m.json()

    # remove current circle request
    iss.remove(it)

    # create user code by using target user id
    user_code = Hash.md5(str(it.to_id))

    # increase request count
    redis.decr(f'cr.{user_code}')

    cs = CircleService()

    left = Circle()
    left.from_id = it.from_id
    left.to_id = it.to_id
    left.create_time = datetime.now(tz=pytz.UTC)

    right = Circle()
    right.from_id = it.to_id
    right.to_id = it.from_id
    right.create_time = datetime.now(tz=pytz.UTC)

    # create circle instances
    cs.create(left)
    cs.create(right)

    # increase number of circle
    circle_task.delay(from_id=it.from_id, to_id=it.to_id)

    m.status = True
    return m.json()


@user.route('/invite', methods=['POST'])
def invite_user():
    """
    Invite users by using e-mail address group

    :rtype: flask.Response
    """
    m = Message()

    form = InviteForm()

    # validate form
    if not form.validate():
        m.error = form.error()
        return m.json()

    session = Session.get()

    us = UserService()

    # get user by user id
    user = us.get_by_id(session.user_id)
    if user is None:
        m.error = 'User could not found.'
        return m.json()

    # users should not invite themselves
    if user.email in form.email.data:
        m.error = 'You cannot invite yourself.'
        return m.json()

    # send e-mail addresses in the background
    invitation_task.delay(
        user_id=user.uid,
        emails=form.email.data,
    )

    m.status = True

    return m.json()


@user.route('/location', methods=['POST'])
def set_location():
    """
    Set user location

    :rtype: flask.Response
    """
    m = Message()

    form = LocationForm()

    # validate form
    if not form.validate():
        m.error = form.error()
        return m.json()

    session = Session.get()

    us = UserService()

    # get user by user id
    user = us.get_by_id(session.user_id)
    if user is None:
        return m.json()

    user.language = form.language.data
    user.country = form.country.data

    # update user country and language
    us.update(user)

    m.status = True

    return m.json()


@user.route('/notification', methods=['POST'])
def set_notification():
    """
    Set user notification token

    :rtype: flask.Response
    """
    m = Message()

    form = NotificationForm()

    # validate form
    if not form.validate():
        m.error = form.error()
        return m.json()

    session = Session.get()

    # update session data
    Session.set_token(session.user_id, form.token.data)

    m.status = True

    return m.json()
