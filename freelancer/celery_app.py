import os

from celery import Celery
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "freelancer.settings")

app = Celery("freelancer")
app.config_from_object("django.conf:settings")
app.conf.broker_url = settings.CELERY_BROKER_URL
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'create-iam-token-every-1-hour': {
        'task': 'projects.tasks.create_iam_token',
        'schedule': 1.0 * 60 * 60,
    },
}

app.conf.timezone = 'UTC'
