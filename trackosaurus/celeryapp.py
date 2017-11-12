from __future__ import absolute_import, unicode_literals
import os
from celery import Celery, task

# from hirefire.procs.celery import CeleryProc

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "trackosaurus.config")
os.environ.setdefault("DJANGO_CONFIGURATION", "Production")
#os.environ.setdefault("DJANGO_SETTINGS_MODULE", "trackosaurus.config.production")

from configurations import importer
importer.install()

from django.conf import settings

app = Celery('trackosaurus')
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
# app.conf.update(BROKER_URL=os.environ.get('REDISCLOUD_URL', 'redis://127.0.0.1:6379/1'), CELERY_RESULT_BACKEND=os.environ.get('REDISCLOUD_URL', 'redis://127.0.0.1:6379/1'))
# app.config_from_object('django.conf:settings', namespace='CELERY')
#app.autodiscover_tasks(['core'])


@task
def debug_task(self):
    print('Request: {0!r}'.format(self.request))

# class WorkerProc(CeleryProc):
#     name = 'worker'
#     queues = ['celery']
#     app = app