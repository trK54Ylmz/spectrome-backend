from task import celery
from util import logger
from db.service import UserService
from search import ElasticService
from search.model import CircleDocument


@celery.task(serializer='json')
def uncircle_task(from_id, to_id):
    """
    Decrease user circle counter

    :param int from_id: from user id
    :param int to_id: to user id
    """
    us = UserService()

    # get user by user id
    from_user = us.get_by_id(from_id)
    if from_user is None:
        return

    from_user.number_of_circles = from_user.number_of_circles - 1

    logger.info('User is updating.')

    # update user
    us.update(from_user)

    logger.info('User updated.')

    # get user by user id
    to_user = us.get_by_id(to_id)
    if to_user is None:
        logger.error(f'The user with {to_id} ID is missing.')
        return

    # update uncircle
    to_user.number_of_circles = to_user.number_of_circles - 1

    # update user
    us.update(to_user)

    es = ElasticService()

    # create document id
    doc_id = f'{from_user.uid}-{to_user.uid}'

    circle = CircleDocument.get(id=doc_id)

    # delete circle document
    circle.delete(using=es.client)
