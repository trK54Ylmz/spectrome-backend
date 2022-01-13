import pytz
import shutil
import time
from datetime import datetime
from db.model import Comment, Post, PostRestriction, PostStatus, PostType
from process import PhotoProcess, VideoProcess
from pyfcm import FCMNotification
from server.cache import redis
from server.session import Session
from task import celery
from util import logger
from util.config import config
from util.hash import Hash
from db.service import (
    CommentService, CircleService, PostRestrictionService, PostService, UserService
)


@celery.task(serializer='json')
def create_post_task(
    user_id, code, disposable, size, message,
    path, files, types, scales, users, session_code,
):
    """
    Create post in the background. Check the content,
    resize and upload files to the object storage

    :param str code: post code
    :param bool disposable: post is disposable or not
    :param int size: post screen size
    :param float device: device width size
    :param list[str] files: location of files as list
    :param list[int] files: file types as list
    :param list[float] scales: file scales as list
    :param list[str] users: list of users for restriction
    :param str session_code: user active session code
    """
    logger.info('Task creating')

    redis.set(f'ps.{code}', str(PostStatus.PROCESSING))

    us = UserService()
    cs = CircleService()

    # list of notification tokens
    tokens = []

    # list of shared users
    restricteds = []
    for username in users:
        # get user by username
        user = us.get_by_username(username)

        # skip if user does not exists
        if user is None:
            continue

        # get circle
        circle = cs.get_by_from_to(
            from_id=user_id,
            to_id=user.uid
        )

        # if circle user is empty so user cannot share with this user
        # means user does not circle the owner
        if circle is None:
            continue

        # populate restricted users by using circle user's user id
        restricteds.append(user.uid)

        # get notification tokens
        items = Session.get_tokens(user_id=user.uid)

        # populate list of tokens
        if items is not None:
            tokens += items

    # this is a restricted post but there is not any restricted
    # users in the list so post won't be created
    if len(restricteds) == 0:
        logger.warn('Restricted post has no any users.')
        # clear directory
        shutil.rmtree(path)

        redis.set(f'ps.{code}', str(PostStatus.DELETED))
        return

    logger.info('Post instance creating.')

    post = Post()
    post.code = code
    post.size = size
    post.disposable = disposable
    post.user_id = user_id
    post.types = types
    post.number_of_comments = 0
    post.number_of_users = len(restricteds)
    post.status = PostStatus.CREATED
    post.create_time = datetime.now(tz=pytz.UTC)

    logger.info('Objects are uploading.')

    objects = []

    try:
        for i in range(len(files)):
            # create content according to the type
            if types[i] == PostType.PHOTO:
                process = PhotoProcess(
                    post_code=code,
                    file=files[i],
                    scale=scales[i],
                    size=size,
                    session_code=session_code,
                )

                # create and upload photo
                name = process.create()
            else:
                process = VideoProcess(
                    post_code=code,
                    file=files[i],
                    scale=scales[i],
                    size=size,
                    session_code=session_code,
                )

                # create and upload video
                name = process.create()

            # something happened while creating content. error or invalid content
            if name is None:
                continue

            # populate after creation
            objects.append(name)
    except Exception as e:
        logger.exception(e)

        if 'NSFW' in e.args[0]:
            redis.set(f'ps.{code}', str(PostStatus.BANNED))
        else:
            redis.set(f'ps.{code}', str(PostStatus.FAILED))

        return

    # update post as created and almost done
    redis.set(f'ps.{code}', str(PostStatus.CREATED))

    post.items = objects

    ps = PostService()

    # create post
    ps.create(post)

    logger.info('Post created.')

    cs = CommentService()

    # create comment code
    unique_id = Hash.uuid()
    tm = time.time()
    comment_code = Hash.md5(f'{unique_id} - {tm}')

    comment = Comment()
    comment.post_id = post.pid
    comment.user_id = user_id
    comment.code = comment_code
    comment.owned = True
    comment.message = message
    comment.create_time = datetime.now(tz=pytz.UTC)

    # create owned comment
    cs.create(comment)

    rs = PostRestrictionService()

    # create restrictions at the end of the post creation
    restrictions = []
    for ru in restricteds:
        pr = PostRestriction()
        pr.post_id = post.pid
        pr.user_id = ru

        # create post restriction
        restrictions.append(pr)

    # create all restrictions
    rs.create_all(restrictions)

    # get user by user id
    user = us.get_by_id(user_id)

    user.number_of_posts = user.number_of_posts + 1

    # update user posts count
    us.update(user)

    post.status = PostStatus.ACTIVATED

    # update post status
    ps.update(post)

    # clear directory
    shutil.rmtree(path)

    # post is created and ready to go
    redis.set(f'ps.{code}', str(PostStatus.ACTIVATED))

    ps = FCMNotification(api_key=config.firebase.key)

    # notification title
    title = 'There is a new post'
    message = f'{user.name} ({user.username}) shared a new post with you.'

    # send notification to multiple device
    ps.notify_multiple_devices(
        registration_ids=tokens,
        message_title=title,
        message_body=message,
    )
