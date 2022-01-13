import pytz
from datetime import datetime
from db.model import Post, User, UserStatus
from flask import Blueprint, request
from server import app
from server.message import Message
from server.session import Session
from util import Strings
from validation.post import PostGetForm, ProfilePostForm, WaterFallGetForm
from werkzeug.datastructures import MultiDict
from db.service import (
    CommentService, CircleService, PostRestrictionService, PostService, UserService
)

post = Blueprint('post', app.name)


@post.route('/post/<code>', methods=['GET'])
def get_post(code):
    """
    Get post by code

    :param str code: post code
    """
    m = Message()

    # extend arguments
    args = MultiDict(request.args)
    args.add('code', code)

    form = PostGetForm(args)

    # validate form
    if not form.validate():
        m.message = form.error()
        return m.json()

    ps = PostService()

    # get post by code
    post = ps.get_by_code(code)
    if post is None:
        m.message = 'The post could not found.'
        return m.json()

    # get user id
    session = Session.get()

    # do not need any circle check etc.
    if session.user_id == post.user_id:
        # convert post instance to dictionary
        m.post = post.to_json()

    us = UserService()

    # get user by user id of post instance
    user = us.get_by_id(post.user_id)
    if user is None:
        m.message = 'The post could not found.'
        return m.json()

    # set user for response
    m.user = user.to_json()

    cs = CommentService()

    # get owner comment
    comment = cs.get_owned_by_post_id(post.pid)
    if comment is not None:
        m.comment = comment.to_json()
    else:
        m.comment = None

    # get comments by post id
    comments = cs.get_by_post_id(post.pid)
    if len(comments) == 0:
        m.comments = []
    else:
        m.comments = list(map(lambda c: c.to_json(), comments))

    return m.json()


@post.route('/user/<username>', methods=['POST'])
def get_posts(username):
    """
    Get posts of selected user

    :param str username: selected username of user
    :rtype: flask.Response
    """
    m = Message()

    # extend arguments
    args = MultiDict(request.form)
    args.add('username', username)

    form = ProfilePostForm(args)

    # validate form
    if not form.validate():
        m.message = form.error()
        return m.json()

    # get user session
    session = Session.get()

    ps = PostService()

    # get timestamp of last post iterator
    if Strings.is_empty(form.timestamp.data):
        dt = datetime.now(tz=pytz.UTC)
    else:
        dt = datetime.fromisoformat(form.timestamp.data)

    us = UserService()

    # update username if username is me
    if username == 'me':
        username = session.username

    # get user by username
    user = us.get_by_username(username)

    if user is None or user.status != UserStatus.ACTIVATED:
        m.message = 'The user could not found.'
        return m.json()

    if username == session.username:
        # get own posts
        posts = ps.get_all(
            user_id=session.user_id,
            timestamp=dt
        )
    else:
        cs = CircleService()

        # check if circle exists
        f = cs.get_by_from_to(
            from_id=session.user_id,
            to_id=user.uid,
        )

        if f is None:
            m.message = 'You cannot see the posts of this user.'
            return m.json()

        # get circle user posts
        posts = ps.get_by_from_to(
            from_id=session.user_id,
            to_id=user.uid,
            timestamp=dt
        )

    m.posts = []

    if len(posts) == 0:
        m.status = True
        m.posts = None
        return m.json()

    prs = PostRestrictionService()

    for post in posts:
        item = {
            'post': post.to_json(),
            'user': user.to_json(),
            'users': [],
            'me': session.username == user.username,
        }

        # get restrictions by post id
        pr = prs.get_by_post_id(post.pid)

        if pr is not None:
            item['users'] = list(map(lambda u: u.to_json(), pr))

        m.posts.append(item)

    m.status = True

    return m.json()


@post.route('/waterfall', methods=['POST'])
def get_waterfall():
    """
    Get posts of waterfall

    :rtype: flask.Response
    """
    m = Message()

    form = WaterFallGetForm()

    # validate form
    if not form.validate():
        m.message = form.error()
        return m.json()

    # get user id
    session = Session.get()

    ps = PostService()

    # get timestamp of last post iterator
    if Strings.is_empty(form.timestamp.data):
        dt = datetime.now(tz=pytz.UTC)
    else:
        dt = datetime.fromisoformat(form.timestamp.data)

    # get waterfall posts
    results = ps.get_waterfall(
        user_id=session.user_id,
        timestamp=dt
    )

    m.status = True

    if len(results) == 0:
        m.status = True
        m.posts = None
        return m.json()

    prs = PostRestrictionService()

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

        user = User()
        user.name = result.name
        user.username = result.username
        user.token = result.token
        user.number_of_posts = result.number_of_posts
        user.number_of_circles = result.number_of_circles

        item = {
            'post': post.to_json(),
            'user': user.to_json(),
            'users': [],
            'me': session.username == user.username,
        }

        # get restrictions by post id
        pr = prs.get_by_post_id(post.pid)

        if pr is not None:
            item['users'] = list(map(lambda u: u.to_json(), pr))

        m.posts.append(item)

    return m.json()
