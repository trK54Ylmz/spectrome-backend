import pytz
from db.service import CircleService, IntentionService, UserService
from datetime import datetime
from flask import Blueprint, request
from server import app
from server.message import Message
from server.session import Session
from util import Strings
from validation.profile import CircleUserForm
from werkzeug.datastructures import MultiDict

profile = Blueprint('profile', app.name)


@profile.route('/user/<username>', methods=['GET'])
def get(username):
    """
    Get user profile

    :param str username: username of the user
    :rtype: flask.Response
    """
    m = Message()

    us = UserService()

    # get requested user id
    session = Session.get()

    if username in ['me', session.username]:
        # get user by user id
        user = us.get_by_id(session.user_id)
        if user is None:
            m.message = 'The user could not found.'
            return m.json()
    else:
        # get user by username
        user = us.get_by_username(username)
        if user is None:
            m.message = 'The user could not found.'
            return m.json()

        cs = CircleService()
        iss = IntentionService()

        # get circle by user id
        f = cs.get_by_from_to(
            from_id=session.user_id,
            to_id=user.uid
        )

        if f is not None:
            m.circle = True
        else:
            # get intention by user id
            it = iss.get_by_from_to(
                from_id=session.user_id,
                to_id=user.uid
            )

            # set request true if circle request has been sent
            if it is not None:
                m.request = True

    m.status = True
    m.user = user.to_json()

    return m.json()


@profile.route('/circle/user/<username>', methods=['GET'])
def circle(username):
    """
    Get list of circle users

    :param str username: username of the user
    :rtype: flask.Response
    """
    m = Message()

    # extend arguments
    args = MultiDict(request.args)
    args.add('username', username)

    form = CircleUserForm(args)

    # validate form
    if not form.validate():
        m.message = form.error()
        return m.json()

    # get timestamp of last post iterator
    if Strings.is_empty(form.timestamp.data):
        dt = datetime.now(tz=pytz.UTC)
    else:
        dt = datetime.fromisoformat(form.timestamp.data)

    us = UserService()

    # get requested user id
    session = Session.get()

    if username in ['me', session.username]:
        # get user by user id
        user = us.get_by_id(session.user_id)
        if user is None:
            m.message = 'The user could not found.'
            return m.json()

        cs = CircleService()

        # get circles by user id
        circles = cs.get_all(user_id=user.uid, timestamp=dt)

        if len(circles) > 0:
            m.users = []

            # create list of users for response
            for circle in circles:
                m.users.append(circle.to_json())
    else:
        # get user by username
        user = us.get_by_username(username)
        if user is None:
            m.message = 'The user could not found.'
            return m.json()

        cs = CircleService()

        # check if current user added in circles to target user
        circle = cs.get_by_from_to(
            from_id=session.user_id,
            to_id=user.uid
        )

        if circle is None:
            m.message = 'The user should be added in the circles first.'
            return m.json()

        # get circles by user id
        circles = cs.get_all(user_id=user.uid, timestamp=dt)

        if len(circles) > 0:
            m.users = []

            # create list of users for response
            for circle in circles:
                m.users.append(circle.to_json())

    m.status = True
    return m.json()
