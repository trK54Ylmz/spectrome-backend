from flask import Blueprint, request
from server import app
from search.service import CircleSearchService, UserSearchService
from server.message import Message
from server.session import Session
from validation.query import UserForm, CircleForm
from util.config import config

query = Blueprint('query', app.name)


@query.route('/circle', methods=['GET'])
def circle():
    """
    Get circle users by given query parameter

    :rtype: flask.Response
    """
    m = Message()

    form = CircleForm(request.args)

    # validate form
    if not form.validate():
        m.message = form.error()
        return m.json()

    # get user id of current user
    session = Session.get()

    cs = CircleSearchService()

    # get autocomplete results
    res = cs.complete(form.query.data, session.user_id)

    is_empty = len(res.username) == 0 and len(res.name) == 0
    if res is None or is_empty:
        m.status = True
        m.users = []
        return m.json()

    ids = []
    m.users = []
    for suggest in [res.username, res.name]:
        for option in suggest[0].options:
            if option._id in ids:
                continue

            source = option._source

            # update non-exists parameter
            if 'photo_id' not in source:
                source.photo_id = None

            name = 'default' if source.photo_id is None else source.photo_id
            user = {
                'name': source.name,
                'username': source.username,
                'photo_url': f'https://{config.app.cdn}/profile/{name}/1.jpg',
            }

            ids.append(option._id)
            m.users.append(user)

    m.status = True
    return m.json()


@query.route('user', methods=['GET'])
def user():
    """
    Get users by given query parameter

    :rtype: flask.Response
    """
    m = Message()

    form = UserForm(request.args)

    # validate form
    if not form.validate():
        m.message = form.error()
        return m.json()

    us = UserSearchService()

    # get autocomplete results
    res = us.complete(form.query.data)

    is_empty = len(res.username) == 0 and len(res.name) == 0
    if res is None or is_empty:
        m.status = True
        m.users = []
        return m.json()

    # get session
    session = Session.get()

    ids = []
    m.users = []
    for suggest in [res.username, res.name]:
        for option in suggest[0].options:
            if option._id in ids:
                continue

            source = option._source

            # update non-exists parameter
            if 'photo_id' not in source:
                source.photo_id = None

            name = 'default' if source.photo_id is None else source.photo_id
            user = {
                'name': source.name,
                'username': source.username,
                'photo_url': f'https://{config.app.cdn}/profile/{name}/1.jpg',
            }

            ids.append(option._id)
            m.users.append(user)

    m.status = True
    m.me = session.username
    return m.json()
