from task import celery
from util import logger
from db.service import UserService
from search import ElasticService
from search.model import CircleDocument


@celery.task(serializer='json')
def circle_task(from_id, to_id):
    """
    Increase user circle counter

    :param int from_id: from user id
    :param int to_id: to user id
    """
    us = UserService()

    # get user by user id
    from_user = us.get_by_id(from_id)
    if from_user is None:
        return

    from_user.number_of_circles = from_user.number_of_circles + 1

    logger.info('User is updating.')

    # update user
    us.update(from_user)

    logger.info('User updated.')

    # get user by user id
    to_user = us.get_by_id(to_id)
    if to_user is None:
        logger.error(f'The user with {to_id} ID is missing.')
        return

    # update follow
    to_user.number_of_circles = to_user.number_of_circles + 1

    # update user
    us.update(to_user)

    es = ElasticService()

    left = CircleDocument()
    left.from_id = str(from_user.uid)
    left.to_id = str(to_user.uid)
    left.name = to_user.name
    left.username = to_user.username
    left.photo_id = to_user.token

    right = CircleDocument()
    right.from_id = str(to_user.uid)
    right.to_id = str(from_user.uid)
    right.name = from_user.name
    right.username = from_user.username
    right.photo_id = from_user.token

    # create document id
    left_doc_id = f'{from_user.uid}-{to_user.uid}'
    right_doc_id = f'{to_user.uid}-{from_user.uid}'

    logger.info('Circle document is saving.')

    # create or update elastic document
    left.save(using=es.client, id=left_doc_id)
    right.save(using=es.client, id=right_doc_id)

    logger.info('Circle document saved.')
