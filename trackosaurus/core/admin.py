# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.urls import reverse

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
        'name', 'id', 'description', 'date_modified', 'date_created',
    )


@admin.register(CampaignEvent)
class CampaignEventAdmin(admin.ModelAdmin):
    list_display = (
        'campaign', 'name', 'id', 'description', 'date_modified', 'date_created',
    )


@admin.register(RecordedEvent)
class RecordedEventAdmin(admin.ModelAdmin):
    list_display = (
        'event', 'campaign', 'token', 'date_modified', 'date_created', 'test_notification',
    )

    def get_list_display(self, request):
        self.request = request
        return self.list_display

    def get_queryset(self, request):
        return RecordedEvent.objects.select_related('event', 'event__campaign')

    def campaign(self, instance):
        return instance.event.campaign

    def test_notification(self, instance):
        return "<a href='http://{}{}' class=\"btn btn-info\">Send</a>".format(
            self.request.get_host(), reverse(
                'send-test-notification', args=(instance.pk,)
            ))
    test_notification.allow_tags = True
    test_notification.short_description = "Send test notification"

