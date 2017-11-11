from __future__ import absolute_import

import os

# from hirefire.procs.celery import CeleryProc

# set the default Django settings module for the 'celery' program.
import celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config")
os.environ.setdefault("DJANGO_CONFIGURATION", "Production")

from django.conf import settings

app = celery.Celery('trackosaurus')
app.conf.update(BROKER_URL=settings.REDIS_URL,
                CELERY_RESULT_BACKEND=settings.REDIS_URL)
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


# class WorkerProc(CeleryProc):
#     name = 'worker'
#     queues = ['celery']
#     app = app