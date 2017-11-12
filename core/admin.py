# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.urls import reverse

from .models import Campaign, StandardEvent, CampaignEvent, RecordedEvent, RecordedEventToken, EventNotification, \
    SubscriptionPlan


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
        'event', 'campaign', 'date_modified', 'date_created'
    )

    def get_list_display(self, request):
        self.request = request
        return self.list_display

    def get_queryset(self, request):
        return RecordedEvent.objects.select_related('event', 'event__campaign')

    def campaign(self, instance):
        return instance.event.campaign


@admin.register(RecordedEventToken)
class RecordedEventTokenAdmin(admin.ModelAdmin):
    list_display = (
        'campaign', 'recorded_event', 'subscribed', 'token', 'date_modified', 'date_created', 'test_notification',
    )

    def get_list_display(self, request):
        self.request = request
        return self.list_display

    def get_queryset(self, request):
        return RecordedEventToken.objects.select_related('recorded_event', 'recorded_event__event', 'recorded_event__event__campaign')

    def campaign(self, instance):
        return instance.recorded_event.event.campaign

    def test_notification(self, instance):
        return "<a href='http://{}{}' class=\"btn btn-info\">Send</a>".format(
            self.request.get_host(), reverse(
                'send-test-notification', args=(instance.pk,)
            ))
    test_notification.allow_tags = True
    test_notification.short_description = "Send test notification"


@admin.register(EventNotification)
class EventNotificationAdmin(admin.ModelAdmin):
    list_display = (
        'campaign', 'event', 'event_url', 'page', 'title', 'number_sent', 'number_opened', 'date_modified', 'date_created',
    )

    def get_list_display(self, request):
        self.request = request
        return self.list_display

    def get_queryset(self, request):
        return EventNotification.objects.select_related('recorded_event', 'recorded_event__event', 'recorded_event__event__campaign')

    def campaign(self, instance):
        return instance.recorded_event.event.campaign

    def event(self, instance):
        return instance.recorded_event.event.name

    def event_url(self, instance):
        return instance.recorded_event.url

    def page(self, instance):
        return instance.recorded_event.page_title


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'external_plan_name', 'price', 'currency', 'max_campaigns',
        'max_events_per_campaign', 'max_notifications_per_event',
        'max_notifications_per_day', 'powered_by_link_hidden', 'custom_notification_icon',
        'modify_notification_url', 'date_modified', 'date_created',
    )

    def get_list_display(self, request):
        self.request = request
        return self.list_display

    def get_queryset(self, request):
        return SubscriptionPlan.objects.all()



