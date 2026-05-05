from .celery import celery_app
from . import tasks
from . import beat  # registers the beat schedule