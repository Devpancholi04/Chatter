import os
from celery import Celery

#set the default Django settings module for the 'celery' program
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chatter.settings')

app = Celery('chatter')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.

app.config_from_object('django.conf:settings', namespace="CELERY")

#loading task modules from all the registered  Django app
app.autodiscover_tasks()
app.conf.timezone = 'Asia/Kolkata'
app.conf.enable_utc = False


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
