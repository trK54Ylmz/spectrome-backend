import pytz
from flask import Blueprint
from datetime import datetime
from db.model import Post
from db.service import HistoryService
from server import app
from server.cache import redis
from server.message import Message
from server.session import Session
from util import Strings
from validation.history import HistoryGetForm


history = Blueprint('history', app.name)


@history.route('/request/count', methods=['GET'])
def count_history():
    """
    Get number of unseen histories

    :return: flask.Response
    """
    m = Message()

    session = Session.get()

    # get request count
    count = redis.get(f'history.{session.username}')
    if count is None:
        count = 0

    # set count value
    m.count = int(count)
    m.status = True

    return m.json()


@history.route('/request/seen', methods=['POST'])
def history_seen():
    """
    Set unseen history as seen

    :return: flask.Response
    """
    m = Message()

    session = Session.get()

    # update history count to zero
    redis.set(f'history.{session.username}', 0)

    m.status = True

    return m.json()


@history.route('/comment', methods=['POST'])
def get_history():
    """
    Get history of comments

    :rtype: flask.Response
    """
    m = Message()

    form = HistoryGetForm()

    # validate form
    if not form.validate():
        m.message = form.error()
        return m.json()

    # get timestamp of last post iterator
    if Strings.is_empty(form.timestamp.data):
        dt = datetime.now(tz=pytz.UTC)
    else:
        dt = datetime.fromisoformat(form.timestamp.data)

    session = Session.get()

    hs = HistoryService()

    # get histories by user id
    results = hs.get_by_user(
        user_id=session.user_id,
        timestamp=dt,
    )

    if len(results) == 0:
        m.posts = []
        m.status = True
        return m.json()

    m.posts = []
    for result in results:
        post = Post()
        post.pid = result.pid
        post.user_id = result.user_id
        post.code = result.code
        post.disposable = result.disposable
        post.size = result.size
        post.items = result.items
        post.types = result.types
        post.number_of_comments = result.number_of_comments
        post.number_of_users = result.number_of_users
        post.create_time = result.create_time

        item = {
            'post': post.to_json(),
            'username': result.username,
        }

        m.posts.append(item)

    return m.json()
