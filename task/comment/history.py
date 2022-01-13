import pytz
from datetime import datetime
from task import celery
from util import logger
from db.model import History
from pyfcm import FCMNotification
from server.cache import redis
from server.session import Session
from util.config import config
from db.service import (
    CommentService, HistoryService, PostRestrictionService, PostService, UserService
)


@celery.task(serializer='json')
def history_task(code, comment_id, from_id, owner_id, user_ids):
    """
    Create comment history

    :param str code: post code
    :param int comment_id: comment identity
    :param int from_id: comment owner identity
    :param int owner_id: post owner identity
    :param list[int] user_ids: list of user ids
    """
    ps = PostService()

    # get post by post code
    post = ps.get_by_code(code)

    if post is None:
        logger.error('The post could not found.')
        return

    us = UserService()
    prs = PostRestrictionService()

    # get restrictions by post id
    restrictions = prs.get_by_post_id(post.pid)

    user_ids = []
    for restriction in restrictions:
        # get user by user id
        user = us.get_by_id(restriction.user_id)

        # skip if user could not be found
        if user is None:
            logger.error(f'The user #{restriction.user_id} could not found.')
            continue

        # populate user id list
        user_ids.append(user.uid)

        # increase history unread count
        redis.incr(f'history.{user.username}')

    hs = HistoryService()

    history = History()
    history.post_id = post.pid
    history.user_id = from_id
    history.comment_id = comment_id
    history.user_ids = user_ids
    history.create_time = datetime.now(tz=pytz.UTC)

    # create history
    hs.create(history)

    # get comment owner user by user id
    from_user = us.get_by_id(from_id)

    if from_user is None:
        logger.error(f'The user #{from_id} is missing.')
        return

    cs = CommentService()

    # get comment by comment id
    comment = cs.get_by_id(comment_id)

    if comment is None:
        logger.error(f'The comment #{comment_id} is missing.')
        return

    tokens = []
    for user_id in user_ids + [owner_id]:
        # the comment owner should not receive any notification about the comment
        if user_id == from_id:
            continue

        # get user by user id
        user = us.get_by_id(user_id)

        if user is None:
            logger.error(f'The user #{user_id} is missing.')
            return

        # get list of tokens
        members = Session.get_tokens(user_id)

        # populate tokens
        if members is not None:
            tokens += members

    ps = FCMNotification(api_key=config.firebase.key)

    # notification title
    title = user.username

    # check iOS character limit, iOS limit is 180
    if len(comment.message) > 180:
        limit = 200 if len(comment.message) > 200 else len(comment.message)
        location = comment.message[180:limit].find(' ')

        if location > -1:
            message = comment.message[0:180 + location] + ' ...'
        else:
            message = comment.message[0:180] + ' ...'
    else:
        message = comment.message

    # send notification to multiple device
    ps.notify_multiple_devices(
        registration_ids=tokens,
        message_title=title,
        message_body=message,
    )

    logger.info(f'Comment history created for #{comment_id}.')
