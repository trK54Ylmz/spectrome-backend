import pytz
import time
from flask import Blueprint
from datetime import datetime
from db.model import Comment, User
from db.service import CommentService, PostService, PostRestrictionService, UserService
from server import app
from server.message import Message
from server.session import Session
from task.comment import history_task
from util import Strings
from util.hash import Hash
from werkzeug.datastructures import MultiDict
from validation.comment import (
    CommentAddForm, CommentHistoryForm, CommentRecentForm, OwnedForm
)


comment = Blueprint('comment', app.name)


@comment.route('/owned/<code>', methods=['GET'])
def get_owned(code):
    """
    Get owned comment by post code

    :rtype: flask.Response
    """
    m = Message()

    # create form arguments
    args = MultiDict()
    args.add('code', code)

    form = OwnedForm(args)

    # validate form
    if not form.validate():
        m.message = form.error()
        return m.json()

    # get session
    session = Session.get()

    ps = PostService()

    # get post by code
    post = ps.get_by_code(code)

    if post is None:
        m.message = 'The post could not found.'
        return m.json()

    if post.user_id != session.user_id:
        rs = PostRestrictionService()

        # get restrictions
        pr = rs.get_by_post_id(post.pid)

        user_ids = list(map(lambda r: r.uid, pr))

        # user is not allowed
        if session.user_id not in user_ids:
            m.message = 'The post could not found.'
            return m.json()

    cs = CommentService()

    # get owned comment
    c = cs.get_owned_by_post_id(post.pid)

    if c is None:
        m.message = 'The message could not found.'
        return m.json()

    m.comment = c.to_json()
    m.status = True

    return m.json()


@comment.route('/recent/<code>', methods=['GET'])
def get_recent(code):
    """
    Get recent comments of the post

    :rtype: flask.Response
    """
    m = Message()

    # create form arguments
    args = MultiDict()
    args.add('code', code)

    form = CommentRecentForm(args)

    # validate form
    if not form.validate():
        m.message = form.error()
        return m.json()

    # get session
    session = Session.get()

    ps = PostService()

    # get post by code
    post = ps.get_by_code(form.code.data)

    if post is None:
        m.message = 'The post could not found.'
        return m.json()

    if post.user_id != session.user_id:
        rs = PostRestrictionService()

        # get restrictions
        pr = rs.get_by_post_id(post.pid)

        user_ids = list(map(lambda r: r.uid, pr))

        # user is not allowed
        if session.user_id not in user_ids:
            m.message = 'The post could not found.'
            return m.json()

    cs = CommentService()

    # get recent comments
    results = cs.get_recent(post_id=post.pid)

    m.status = True

    if len(results) == 0:
        m.comments = None
        return m.json()

    m.comments = []
    for result in results:
        user = User()
        user.name = result.name
        user.username = result.username
        user.token = result.token
        user.number_of_posts = result.number_of_posts
        user.number_of_circles = result.number_of_circles

        comment = Comment()
        comment.code = result.code
        comment.message = result.message
        comment.create_time = result.create_time

        item = {
            'comment': comment.to_json(),
            'user': user.to_json(),
            'me': session.username == user.username,
        }

        m.comments.append(item)

    return m.json()


@comment.route('/history', methods=['POST'])
def get_history():
    """
    Get comment history of the post

    :rtype: flask.Response
    """
    m = Message()

    form = CommentHistoryForm()

    # validate form
    if not form.validate():
        m.message = form.error()
        return m.json()

    # get session
    session = Session.get()

    ps = PostService()

    # get post by code
    post = ps.get_by_code(form.code.data)

    if post is None:
        m.message = 'The post could not found.'
        return m.json()

    if post.user_id != session.user_id:
        rs = PostRestrictionService()

        # get restrictions
        pr = rs.get_by_post_id(post.pid)

        user_ids = list(map(lambda r: r.uid, pr))

        # user is not allowed
        if session.user_id not in user_ids:
            m.message = 'The post could not found.'
            return m.json()

    cs = CommentService()

    # get timestamp of last post iterator
    if Strings.is_empty(form.timestamp.data):
        dt = datetime.now(tz=pytz.UTC)
    else:
        dt = datetime.fromisoformat(form.timestamp.data)

    # get history of comments
    results = cs.get_history(
        post_id=post.pid,
        timestamp=dt
    )

    m.status = True

    if len(results) == 0:
        m.comments = None
        return m.json()

    m.comments = []
    for result in results:
        user = User()
        user.name = result.name
        user.username = result.username
        user.token = result.token
        user.number_of_posts = result.number_of_posts
        user.number_of_circles = result.number_of_circles

        comment = Comment()
        comment.code = result.code
        comment.message = result.message
        comment.create_time = result.create_time

        item = {
            'comment': comment.to_json(),
            'user': user.to_json(),
            'me': session.username == user.username,
        }

        m.comments.append(item)

    return m.json()


@comment.route('/add', methods=['POST'])
def add_comment():
    """
    Add comment to the post

    :rtype: flask.Response
    """
    m = Message()

    form = CommentAddForm()

    # validate form
    if not form.validate():
        m.message = form.error()
        return m.json()

    # get session
    session = Session.get()

    ps = PostService()

    # get post by code
    post = ps.get_by_code(form.code.data)

    if post is None:
        m.message = 'The post could not found.'
        return m.json()

    rs = PostRestrictionService()

    # get restrictions
    pr = rs.get_by_post_id(post.pid)

    user_ids = list(map(lambda r: r.uid, pr))

    # user is not allowed
    if post.user_id != session.user_id and session.user_id not in user_ids:
        m.message = 'The post could not found.'
        return m.json()

    cs = CommentService()

    # create comment code
    unique_id = Hash.uuid()
    tm = time.time()
    code = Hash.md5(f'{unique_id} - {tm}')

    comment = Comment()
    comment.post_id = post.pid
    comment.user_id = session.user_id
    comment.code = code
    comment.message = form.message.data
    comment.owned = False
    comment.create_time = datetime.now(tz=pytz.UTC)

    # create new comment
    cs.create(comment)

    # increase number of comments
    post.number_of_comments = post.number_of_comments + 1

    # update post comment count
    ps.update(post)

    us = UserService()

    # get user by user id
    user = us.get_by_id(session.user_id)

    item = {
        'comment': comment.to_json(),
        'user': user.to_json(),
    }

    # create history creation in the background
    history_task.delayed(
        code=post.code,
        comment_id=comment.cid,
        from_id=session.user_id,
        owner_id=post.user_id,
        user_ids=user_ids,
    )

    m.status = True
    m.comment = item

    return m.json()
