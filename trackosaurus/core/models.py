# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


# Create your models here.
from core.constants import CAMPAIGN_TYPE_CHOICES


class TimedModel(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Campaign(TimedModel):
    user = models.ForeignKey('users.User', related_name='campaigns', null=False, blank=False)
    name = models.CharField(max_length=256, null=False, blank=False)
    base_url = models.CharField(max_length=256, null=False, blank=False)
    description = models.TextField(max_length=1024, null=True, blank=True)
    type = models.PositiveIntegerField(choices=CAMPAIGN_TYPE_CHOICES)

    class Meta:
        verbose_name = 'Campaign'
        verbose_name_plural = 'Campaigns'
        ordering = ['-date_created']


class StandardEvent(TimedModel):
    """
    This is a collection of predefined standard events
    that will be offered to user when creating a campaign
    """
    code = models.CharField(max_length=16, null=False, blank=False)
    name = models.CharField(max_length=128, null=False, blank=False)
    description = models.CharField(max_length=128, null=True, blank=True)
    type = models.PositiveIntegerField(choices=CAMPAIGN_TYPE_CHOICES)

    class Meta:
        verbose_name = 'Standard Event'
        verbose_name_plural = 'Standard Events'
        ordering = ['-date_created']


class CampaignEvent(TimedModel):
    """
    Users will be able to click on these events on popup
    """
    campaign = models.ForeignKey(Campaign, related_name='campaign_events', null=False, blank=False)
    code = models.CharField(max_length=16, null=False, blank=False)
    name = models.CharField(max_length=128, null=False, blank=False)
    description = models.CharField(max_length=128, null=True, blank=True)
    type = models.PositiveIntegerField(choices=CAMPAIGN_TYPE_CHOICES)

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
        verbose_name_plural = 'Recorded Evente'
        ordering = ['-date_created']
