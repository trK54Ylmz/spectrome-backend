from celery import Celery
from util.config import config


class BackgroundTask:
    def __init__(self, app):
        """
        Initialize background task

        :param flask.Flask app: flask application
        """
        host = config.celery.host
        port = config.celery.port
        db = config.celery.db
        uri = f'redis://{host}:{port}/{db}'

        includes = [
            'task.account',
            'task.comment',
            'task.post',
            'task.profile',
            'task.share',
            'task.user',
        ]

        celery = Celery(
            app.import_name,
            backend=uri,
            broker=uri,
            worker_hijack_root_logger=False,
            include=includes,
        )

        # use UTC
        celery.conf['CELERY_ENABLE_UTC'] = True

        # create celery context
        class ContextTask(celery.Task):
            def __call__(self, *args, **kwargs):
                with app.app_context():
                    return self.run(*args, **kwargs)

        # update flask config
        celery.conf.update(app.config)
        celery.Task = ContextTask

        self._celery = celery

    def get(self):
        """
        Get celery app

        :return: celery application
        :rtype: celery.Celery
        """
        return self._celery
