from db.service import IntentionService, UserService
from flask import Blueprint
from server import app
from server.message import Message
from server.session import Session

notification = Blueprint('notification', app.name)


@notification.route('/intention', methods=['GET'])
def intention():
    """
    Get list of circle requests

    :return: flask.Response
    """
    m = Message()

    session = Session.get()

    iss = IntentionService()

    # get unsent intentions
    it = iss.get_by_unsent(session.user_id)

    # there are no any requests
    if it is None:
        m.status = True
        return m.json()

    us = UserService()

    # get user by id
    from_user = us.get_by_id(it.from_id)
    if from_user is None:
        m.status = True
        return m.json()

    it.sent = True

    # update intention as sent
    iss.update(it)

    # set intention code
    m.code = it.code
    m.create_time = it.create_time
    m.user_name = from_user.username
    m.status = True

    return m.json()
