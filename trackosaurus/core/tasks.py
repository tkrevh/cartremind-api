import json
import requests
from django.apps import apps
from celery import task
from django.conf import settings

@task()
def register_user_to_topic(token, topic):
    """
    https://iid.googleapis.com/iid/v1:batchAdd
    Content-Type:application/json
    Authorization:key=API_KEY
    {
       "to": "/topics/<YOUR TOPIC NAME HERE>",
       "registration_tokens": ["<YOUR TOKEN HERE>"]
    }
    """
    API_KEY = "AAAAry4xbXQ:APA91bFM6lFskgOsjsPXhdHhdCRA4CafRDw5RNE4RdZjrDeSAgKiTKo0Z9M_spLufLH6rJOUA1xwfnnt0tExqTyig612p3Pu9EiLNcsZj80UHbWA2Dtyu0vyA3jpxblI5vhAgkrQ17dE"
    HEADERS = {
        "Content-Type": "application/json",
        "Authorization": "key={}".format(API_KEY)
    }
    payload = {
        "to": "/topics/{}".format(topic),
        "registration_tokens": [token]
    }
    URL = 'https://iid.googleapis.com/iid/v1:batchAdd'.format(token, topic)
    r = requests.post(URL, data=json.dumps(payload), headers=HEADERS)
    if r.status_code == requests.codes.ok:
        RecordedEventToken = apps.get_model('core', 'RecordedEventToken')
        RecordedEventToken.objects.filter(token=token).update(subscribed=True)


