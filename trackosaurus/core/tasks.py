import json
import requests
from django.apps import apps
import celery
from django.conf import settings

app = celery.Celery('trackosaurus')
app.conf.update(BROKER_URL=settings.REDIS_URL,
                CELERY_RESULT_BACKEND=settings.REDIS_URL)


@app.task
def register_user_to_topic(token, topic):
    API_KEY = "AAAAry4xbXQ:APA91bFM6lFskgOsjsPXhdHhdCRA4CafRDw5RNE4RdZjrDeSAgKiTKo0Z9M_spLufLH6rJOUA1xwfnnt0tExqTyig612p3Pu9EiLNcsZj80UHbWA2Dtyu0vyA3jpxblI5vhAgkrQ17dE"
    HEADERS = {
        "Content-Type": "application/json",
        "Authorization": "key={}".format(API_KEY)
    }
    URL = 'https://iid.googleapis.com/iid/v1/{}/rel/topics/{}'.format(token, topic)
    r = requests.get(URL, headers=HEADERS)
    if r.status_code == requests.codes.ok:
        RecordedEventToken = apps.get_model('core', 'RecordedEventToken')
        RecordedEventToken.objects.filter(token=token).update(subscribed=True)
