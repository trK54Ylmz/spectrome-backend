from db.service import UserService
from flask import Blueprint, request
from server import app
from server.message import Message
from server.session import redis, Session
from validation.session import SessionForm

session = Blueprint('session', app.name)


@session.route('/check', methods=['GET'])
def check():
    """
    Check session

    :rtype: flask.Response
    """
    m = Message()

    session_code = request.headers.get('x-authorization')

    # get session by session code
    session = Session.get()

    if session is None:
        m.expired = True
    else:
        # update expire time of session
        Session.refresh(session_code)

        m.expired = False

    # check if session in redis
    m.session = session_code
    m.status = True

    return m.json()


@session.route('/refresh', methods=['POST'])
def refresh():
    """
    Refresh session

    :rtype: flask.Response
    """
    m = Message()
    form = SessionForm()

    # return error if validation failed
    if not form.validate():
        m.message = form.error()
        return m.json()

    # check if session exists on Redis
    if Session.exists(form.session.data):
        m.status = True
        m.session = form.session.data
        return m.json()

    # read token has from session data
    token_content = Session.get_token(form.session.data)
    if token_content is None:
        m.exists = False
        return m.json()

    # delete old token key
    redis.delete(f'st.{form.session.data}')

    # decrypt token content
    user_id = token_content.get('id')

    user_service = UserService()

    # get user by using user id
    user = user_service.get_by_id(user_id)

    # create user session
    session_code = Session.create(user)

    # set session code to response object
    m.session = session_code
    m.status = True

    return m.json()
