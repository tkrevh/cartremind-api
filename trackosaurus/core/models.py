# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import uuid

from django.db import models


# Create your models here.
from core.constants import CAMPAIGN_TYPE_CHOICES
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
        return self.name

    class Meta:
        verbose_name = 'Campaign Event'
        verbose_name_plural = 'Campaign Events'
        ordering = ['-date_created']


class RecordedEvent(TimedModel):
    """
    Once user clicks on the event on which he wants to be notified of,
    we get his permission to send him push notification and with it,
    we get a token, which we need to store.
    """
    event = models.ForeignKey(CampaignEvent, related_name='recorded_events', null=False, blank=False)
    token = models.CharField(max_length=256, null=False, blank=False)

    class Meta:
        verbose_name = 'Recorded Event'
        verbose_name_plural = 'Recorded Events'
        ordering = ['-date_created']

