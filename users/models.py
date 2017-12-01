from __future__ import unicode_literals

import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.encoding import python_2_unicode_compatible

from .helpers import generate_key


@python_2_unicode_compatible
class APIKey(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    key = models.CharField(max_length=40, unique=True)

    def __str__(self):
        return self.key

    class Meta:
        verbose_name_plural = "API Keys"
        ordering = ['-created']


@python_2_unicode_compatible
class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    api_key = models.OneToOneField(APIKey, null=True, related_name='user', on_delete=models.CASCADE)
    subscribers_limit = models.PositiveIntegerField(default=1000)

    company_name = models.CharField(max_length=256, null=True, blank=True)
    vat_id = models.CharField(max_length=20, null=True, blank=True)
    street = models.CharField(max_length=256, null=True, blank=True)
    zip = models.CharField(max_length=64, null=True, blank=True)
    city = models.CharField(max_length=128, null=True, blank=True)
    country = models.CharField(max_length=128, null=True, blank=True)


    @property
    def has_subscription(self):
        return hasattr(self, 'btsubscription')

    @property
    def can_access_advanced_configuration(self):
        return self.has_perm('users.can_access_advanced_configuration')

    @property
    def can_segment_notifications(self):
        return self.has_perm('users.can_segment_notifications')

    @property
    def can_use_autoresponder(self):
        return self.has_perm('users.can_use_autoresponder')

    @property
    def can_use_timed_messages(self):
        return self.has_perm('users.can_use_timed_messages')

    @property
    def can_use_advanced_triggers(self):
        return self.has_perm('users.can_use_advanced_triggers')

    def save(self, *args, **kwargs):

        # create an API key for new users
        if not self.api_key:
            self.api_key = APIKey(
                key=generate_key()
            )
            self.api_key.save()

        super(AbstractUser, self).save(*args, **kwargs)

    def __str__(self):
        return self.email

    class Meta:
        permissions = (
            ('can_access_advanced_configuration', 'Can user access advanced configuration'),
            ('can_segment_notifications', 'Can user segment notifications'),
            ('can_use_autoresponder', 'Can user use autoresponder'),
            ('can_use_timed_messages', 'Can user use timed messages'),
            ('can_use_advanced_triggers', 'Can user use advanced triggers'),
        )
