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
