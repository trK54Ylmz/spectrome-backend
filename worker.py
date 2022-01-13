from task import celery
from util import logger

logger.info('Celery app created ' + celery.main)
