from __future__ import absolute_import

import os
from celery import Celery
# from hirefire.procs.celery import CeleryProc
from django.conf import settings

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config")
# os.environ.setdefault("DJANGO_CONFIGURATION", "Production")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trackosaurus.config.production')

app = Celery('trackosaurus')
app.conf.update(BROKER_URL=os.environ.get('REDISTOGO_URL', 'redis://127.0.0.1:6379/1'),
                CELERY_RESULT_BACKEND=os.environ.get('REDISTOGO_URL', 'redis://127.0.0.1:6379/1'))
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


# class WorkerProc(CeleryProc):
#     name = 'worker'
#     queues = ['celery']
#     app = app