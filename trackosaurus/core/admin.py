# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import Campaign, StandardEvent, CampaignEvent, RecordedEvent


# Register your models here.
@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'user', 'id', 'date_modified', 'date_created',
    )


@admin.register(StandardEvent)
class StandardEventAdmin(admin.ModelAdmin):
    list_display = (
        'code', 'name', 'id', 'description', 'date_modified', 'date_created',
    )


@admin.register(CampaignEvent)
class CampaignEventAdmin(admin.ModelAdmin):
    list_display = (
        'campaign', 'code', 'name', 'id', 'description', 'date_modified', 'date_created',
    )


@admin.register(RecordedEvent)
class CampaignEventAdmin(admin.ModelAdmin):
    list_display = (
        'event', 'campaign', 'token', 'date_modified', 'date_created',
    )

    def get_queryset(self, request):
        return RecordedEvent.objects.select_related('event', 'event__campaign')

    def campaign(self, instance):
        return instance.event.campaign

