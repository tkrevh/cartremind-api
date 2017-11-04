# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import Campaign, StandardEvent, CampaignEvent

# Register your models here.
@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    pass


@admin.register(StandardEvent)
class StandardEventAdmin(admin.ModelAdmin):
    pass


@admin.register(CampaignEvent)
class CampaignEventAdmin(admin.ModelAdmin):
    pass


