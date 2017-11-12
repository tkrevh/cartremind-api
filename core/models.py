# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import uuid

import requests
from django.conf import settings
from django.db import models


# Create your models here.
from core.constants import CAMPAIGN_TYPE_CHOICES
from django.urls import reverse
from django.utils.encoding import python_2_unicode_compatible

from .constants import CAMPAIGN_TYPE_OTHER


class TimedModel(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


@python_2_unicode_compatible
class Campaign(TimedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('users.User', related_name='campaigns', null=False, blank=False)
    name = models.CharField(max_length=256, null=False, blank=False)
    base_url = models.CharField(max_length=256, null=False, blank=False)
    description = models.TextField(max_length=1024, null=True, blank=True)
    type = models.PositiveIntegerField(choices=CAMPAIGN_TYPE_CHOICES, default=CAMPAIGN_TYPE_OTHER)

    def __str__(self):
        return '{}'.format(self.name)

    class Meta:
        verbose_name = 'Campaign'
        verbose_name_plural = 'Campaigns'
        ordering = ['-date_created']


@python_2_unicode_compatible
class StandardEvent(TimedModel):
    """
    This is a collection of predefined standard events
    that will be offered to user when creating a campaign
    """
    name = models.CharField(max_length=128, null=False, blank=False)
    description = models.CharField(max_length=128, null=True, blank=True)
    type = models.PositiveIntegerField(choices=CAMPAIGN_TYPE_CHOICES)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Standard Event'
        verbose_name_plural = 'Standard Events'
        ordering = ['-date_created']


@python_2_unicode_compatible
class CampaignEvent(TimedModel):
    """
    Users will be able to click on these events on popup
    """
    campaign = models.ForeignKey(Campaign, related_name='campaign_events', null=False, blank=False)
    name = models.CharField(max_length=128, null=False, blank=False)
    description = models.CharField(max_length=128, null=True, blank=True)
    type = models.PositiveIntegerField(choices=CAMPAIGN_TYPE_CHOICES, default=CAMPAIGN_TYPE_OTHER)

    def __str__(self):
        return '{}({})'.format(self.name, self.campaign.name)

    class Meta:
        verbose_name = 'Campaign Event'
        verbose_name_plural = 'Campaign Events'
        ordering = ['-date_created']


@python_2_unicode_compatible
class RecordedEvent(TimedModel):
    """
    Once user clicks on the event on which he wants to be notified of,
    we get his permission to send him push notification and with it,
    we get a token, which we need to store.
    """
    event = models.ForeignKey(CampaignEvent, related_name='recorded_events', null=False, blank=False)
    url = models.TextField(null=False, blank=False, default="http://placeholder")
    page_title = models.CharField(max_length=1204, null=False, blank=False, default='page_title')

    def get_topic_name(self):
        return '{}-{}'.format(self.event.campaign.id, self.id)

    def __str__(self):
        MAX_PAGE_TITLE_DISPLAY_LENGTH = 30
        shortened_page_title = self.page_title
        if len(shortened_page_title) > MAX_PAGE_TITLE_DISPLAY_LENGTH:
            shortened_page_title = '{}...'.format(shortened_page_title[:MAX_PAGE_TITLE_DISPLAY_LENGTH])
        return '{}/{}'.format(self.event.name, shortened_page_title)

    class Meta:
        verbose_name = 'Recorded Event'
        verbose_name_plural = 'Recorded Events'
        ordering = ['-date_created']
        unique_together = ('event', 'url')


class RecordedEventToken(TimedModel):
    recorded_event = models.ForeignKey(RecordedEvent, related_name='tokens', null=False, blank=False)
    token = models.CharField(max_length=256, null=False, blank=False, db_index=True)
    subscribed = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Recorded Event Token'
        verbose_name_plural = 'Recorded Event Tokens'
        ordering = ['-date_created']
        unique_together = ('recorded_event', 'token')


class EventNotification(TimedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recorded_event = models.ForeignKey(RecordedEvent, related_name='notifications', null=False, blank=False)
    title = models.CharField(max_length=128, null=False, blank=False)
    body = models.CharField(max_length=1024, null=False, blank=False)
    icon = models.ImageField(upload_to='notification_icons', null=False, blank=False)
    url = models.TextField(null=False, blank=False)
    number_sent = models.PositiveIntegerField(default=0)
    number_opened = models.PositiveIntegerField(default=0)

    def get_tracked_url(self, request):
        return '{}://{}{}'.format(
            'https' if request.is_secure() else 'http',
            request.get_host(),
            reverse('track-by-redirect', args=(self.id,))
        )

    def send_notification_to_topic(self, request):
        """
        https://fcm.googleapis.com/fcm/send
        Content-Type:application/json
        Authorization:key=AIzaSyZ-1u...0GBYzPu7Udno5aA
        {
          "to" : /topics/foo-bar",
          "priority" : "high",
          "notification" : {
            "body" : "This is a Firebase Cloud Messaging Topic Message!",
            "title" : "FCM Message",
          }
        }
        """
        topic = self.recorded_event.get_topic_name()
        URL = "https://fcm.googleapis.com/fcm/send"
        API_KEY = "AAAAry4xbXQ:APA91bFM6lFskgOsjsPXhdHhdCRA4CafRDw5RNE4RdZjrDeSAgKiTKo0Z9M_spLufLH6rJOUA1xwfnnt0tExqTyig612p3Pu9EiLNcsZj80UHbWA2Dtyu0vyA3jpxblI5vhAgkrQ17dE"
        HEADERS = {
            "Content-Type": "application/json",
            "Authorization": "key={}".format(API_KEY)
        }

        payload = {
            "notification": {
                "title": self.title,
                "body": self.body,
                "icon": self.icon.url,
                "click_action": self.get_tracked_url(request)
            },
            "to": '/topics/{}'.format(topic)
        }

        r = requests.post(URL, data=json.dumps(payload), headers=HEADERS)
        if r.status_code == requests.codes.ok:
            self.number_sent = self.recorded_event.tokens.count()
            self.save()
            return True

        return False

    class Meta:
        verbose_name = 'Event Notification'
        verbose_name_plural = 'Event Notifications'
        ordering = ['-date_created']


class SubscriptionPlan(TimedModel):
    name = models.CharField(max_length=128, null=False, blank=False)
    external_plan_name = models.CharField(max_length=128, null=True, blank=True)
    price = models.FloatField(null=False, blank=False)
    currency = models.CharField(max_length=5, default='usd')
    max_campaigns = models.PositiveIntegerField(default=1)
    max_events_per_campaign = models.PositiveIntegerField(default=3)
    max_notifications_per_event = models.PositiveIntegerField(default=1000)
    max_notifications_per_day = models.PositiveIntegerField(default=3)
    powered_by_link_hidden = models.BooleanField(default=False)
    custom_notification_icon = models.BooleanField(default=False)
    modify_notification_url = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Subscription Plan'
        verbose_name_plural = 'Subscription Plans'
        ordering = ['-date_created']