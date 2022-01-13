from task import celery
from task.post import disposable_task
from util import logger

logger.info('Celery app created ' + celery.main)


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **_kwargs):
    """
    Run periodic tasks

    :param celery.app.base.Celery sender: celery app
    """
    sender.add_periodic_task(sig=disposable_task.s(), schedule=10 * 60)
