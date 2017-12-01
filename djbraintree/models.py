# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import braintree
from django.contrib.auth.models import Group
from django.db import models
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

# Create your models here.
class TimedModel(models.Model):
    date_created = models.DateTimeField(auto_now_add=True, db_index=True)
    date_modified = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        abstract = True


class BTPlanManager(models.Manager):

    def sync_with_bt(self):
        plans = braintree.Plan.all()

        for plan in plans:
            if not BTPlan.objects.filter(plan_id=plan.id).exists():
                btplan = BTPlan.objects.create(
                    plan_id=plan.id,
                    name=plan.name,
                    billing_frequency=plan.billing_frequency,
                    currency_iso_code=plan.currency_iso_code,
                    description=plan.description,
                    price=plan.price,
                    active=True,
                    created_at=plan.created_at,
                    updated_at=plan.updated_at
                )
                if plan.trial_period:
                    btplan.trial_duration=plan.trial_duration,
                    btplan.trial_duration_unit=plan.trial_duration_unit,
                    btplan.trial_period=plan.trial_period,
                    btplan.save()

                logger.info('[djbraintree] sync_with_bt - synced plan {} ({})'.format(
                    btplan.name, btplan.price
                ))


class BTPlan(TimedModel):
    plan_id = models.CharField(max_length=256, null=False, blank=False)
    name = models.CharField(max_length=256, null=False, blank=False)
    billing_frequency = models.PositiveIntegerField(null=False, blank=False)
    currency_iso_code = models.CharField(max_length=5, null=False, blank=False)
    description = models.CharField(max_length=256, null=False, blank=False)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    trial_duration = models.PositiveIntegerField(null=True, blank=True)
    trial_duration_unit = models.CharField(max_length=5, null=False, blank=False, default='month') # day or month
    trial_period = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    # we must set the user Group users of this plan
    # belong to manually after plans are imported from BT
    user_group = models.ForeignKey(Group, null=True, blank=True)

    objects = BTPlanManager()

    def __unicode__(self):
        return '{}'.format(self.name)

    class Meta:
        verbose_name = 'Braintree Plan'
        verbose_name_plural = 'Braintree Plans'


class BTCurrentSubscription(TimedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='btsubscription',
        on_delete=models.CASCADE
    )
    customer_id = models.CharField(
        max_length=256,
        null=False,
        blank=False,
    )
    subscription_id = models.CharField(max_length=256, null=False, blank=False)
    plan = models.ForeignKey(BTPlan, related_name='btsubscriptions')
    status = models.CharField(max_length=16, null=False, blank=False)
    billing_period_start_date = models.DateTimeField()
    billing_period_end_date = models.DateTimeField()
    expire_at_period_end = models.BooleanField(default=False)

    def update_from_subscription(self, subscription, plan, expire_at_period_end=False, save=True):
        self.subscription_id = subscription.id
        self.plan = plan
        self.status = subscription.status
        self.billing_period_start_date = subscription.billing_period_start_date
        self.billing_period_end_date = subscription.billing_period_end_date
        self.expire_at_period_end = expire_at_period_end
        if not self.is_active:
            self.plan.user_group.user_set.remove(self.user)
        if save:
            self.save()

    @property
    def is_active(self):
        return self.status == 'Active'

    class Meta:
        verbose_name = 'Braintree Subscription'
        verbose_name_plural = 'Braintree Subscriptions'