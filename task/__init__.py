from .task import BackgroundTask
from server.server import app

# initialize celery application
backgound_task = BackgroundTask(app)

# get celery object
celery = backgound_task.get()
