from task import celery
from util import logger
from db.service import UserService
from search import ElasticService
from search.model import UserDocument


@celery.task(serializer='json')
def activation_task(user_id):
    """
    Create and update record after activation

    :param int user_id: user primary key
    """
    logger.info('Task creating')

    us = UserService()

    # get user by user id
    user = us.get_by_id(user_id)
    if user is None:
        logger.error(f'User with "{user.uid}" is empty')
        return

    es = ElasticService()

    u = UserDocument()
    u.name = user.name
    u.username = user.username
    u.photo_id = user.token

    # create document id
    doc_id = str(user.uid)

    # create or update user document
    u.save(using=es.client, id=doc_id)

    logger.info('Task completed.')
