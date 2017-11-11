# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import requests
import json

from django.core.exceptions import ValidationError
from django.db import transaction, IntegrityError
from django.db.models import Count
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import redirect
from django.conf import settings

from rest_framework import status, mixins, viewsets
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from users.permissions import HasAPIAccess

from .tasks import register_user_to_topic
from .permissions import IsOwner, IsOwnerOfCampaign
from .serializers import (
    CampaignEventSerializer,
    CampaignSerializer,
    CreateCampaignSerializer,
    RecordedEventSerializer,
    EventNotificationSerializer, CreateEventNotificationSerializer)
from .models import (
    RecordedEvent,
    CampaignEvent,
    Campaign,
    RecordedEventToken,
    EventNotification
)


# Create your views here.
class RecordEventView(APIView):
    permission_classes = (IsAuthenticated, HasAPIAccess)

    def get_or_create_recorded_event(self, campaign_event, url, page_title):
        try:
            obj = RecordedEvent.objects.create(
                event=campaign_event,
                url=url,
                page_title=page_title
            )
        except (IntegrityError, ValidationError):
            obj = RecordedEvent.objects.prefetch_related(
                'event', 'event__campaign'
            ).get(
                event=campaign_event,
                url=url
            )
        return obj

    def post(self, request, campaign, event_id, format=None):
        data = request.data
        user = request.user
        token = data.get('token')
        url = data.get('url')
        page_title = data.get('title')
        try:
            campaign_event = CampaignEvent.objects.get(
                campaign_id=campaign,
                pk=event_id
            )
        except CampaignEvent.DoesNotExist:
            return Response(
                status=status.HTTP_404_BAD_REQUEST,
                data={
                    'error': 'Such event does not exist'
                }
            )

        if campaign_event.campaign.user.pk != user.pk:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data = {
                    'error': 'Invalid event for this customer'
                }
            )

        recorded_event = self.get_or_create_recorded_event(
            campaign_event=campaign_event,
            url=url,
            page_title=page_title
        )
        with transaction.atomic():
            try:
                RecordedEventToken.objects.create(
                    recorded_event=recorded_event,
                    token=token
                )
                register_user_to_topic.delay(token, recorded_event.get_topic_name())
            except IntegrityError:
                # don't allow duplicate registrations
                pass

        return Response(status=status.HTTP_201_CREATED)


class ListCampaignEventsView(ListAPIView):
    permission_classes = (IsAuthenticated, HasAPIAccess)

    def get(self, request, campaign, format=None):
        user = request.user

        campaign_events = CampaignEvent.objects.filter(
            campaign_id=campaign,
            campaign__user=user
        )

        data = CampaignEventSerializer(campaign_events, many=True).data

        return Response(data=data)


def send_test_notification(request, recorded_event_token_id):

    URL = "https://fcm.googleapis.com/fcm/send"
    API_KEY = "AAAAry4xbXQ:APA91bFM6lFskgOsjsPXhdHhdCRA4CafRDw5RNE4RdZjrDeSAgKiTKo0Z9M_spLufLH6rJOUA1xwfnnt0tExqTyig612p3Pu9EiLNcsZj80UHbWA2Dtyu0vyA3jpxblI5vhAgkrQ17dE"
    HEADERS = {
        "Content-Type": "application/json",
        "Authorization": "key={}".format(API_KEY)
    }

    recorded_event_token = RecordedEventToken.objects.get(pk=recorded_event_token_id)

    payload = {
       "notification": {
         "title": "Free delivery",
         "body": "Get your free delivery now!",
         "icon": "https://t6.rbxcdn.com/b76c17b045192b22d881f24d8c4dd813",
         "click_action": "https://www.nike.com/si/en_gb/?cp=euns_kw_bra!si!goo!core!c!b!%2Bnike%20%2Bstore!164850714626&gclid=Cj0KCQiArYDQBRDoARIsAMR8s_TkhWJ_LeU_5Op3RWtBUgAHDEgLdJUOF1qJNhhjXE5LKfhv6WwzcXsaAk4mEALw_wcB&gclsrc=aw.ds"
       },
       "to": recorded_event_token.token
     }
    r = requests.post(URL, data=json.dumps(payload), headers=HEADERS)
    messages.info(request, 'Notification sent')
    return redirect('admin:core_recordedeventtoken_changelist')


class DashboardView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        user = request.user

        user_campaigns = Campaign.objects.filter(user=user)
        number_of_campaigns = user_campaigns.count()
        campaign_events = CampaignEvent.objects.filter(campaign__in=user_campaigns)
        number_of_campaign_events = campaign_events.count()
        number_of_registered_signups = RecordedEventToken.objects.filter(recorded_event__event__in=campaign_events).count()
        number_of_sent_notifications = EventNotification.objects.filter(recorded_event__event__campaign__user=user).count()
        data = {
            'number_of_campaigns': number_of_campaigns,
            'number_of_campaign_events': number_of_campaign_events,
            'number_of_registered_signups': number_of_registered_signups,
            'number_of_sent_notifications': number_of_sent_notifications,
            'max_subscribers': user.subscribers_limit
        }

        return Response(data)


class CampaignStatisticsView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        user = request.user

        user_campaigns = Campaign.objects.filter(user=user).prefetch_related(
            'campaign_events', 'campaign_events__recorded_events'
        )

        campaing_statistics = []
        for campaign in user_campaigns:
            campaign_events = campaign.campaign_events.all()
            recorded_events = RecordedEvent.objects.filter(
                event__in=campaign_events
            ).annotate(
                subscribers=Count('tokens')
            ).order_by('-subscribers')
            campaing_statistics.append({
                'name': campaign.name,
                'events': RecordedEventSerializer(recorded_events, many=True).data
            })

        data = campaing_statistics

        return Response(data)


class CampaignViewSet(mixins.CreateModelMixin,
                      mixins.ListModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin,
                      viewsets.GenericViewSet):
    """
    Creates, Updates, and retrives Campaigns
    """
    queryset = Campaign.objects.all()
    serializer_class = CampaignSerializer
    permission_classes = (IsOwner,)

    def get_queryset(self):
        return Campaign.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        self.serializer_class = CreateCampaignSerializer
        self.permission_classes = (IsAuthenticated,)
        return super(CampaignViewSet, self).create(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        self.permission_classes = (IsOwner,)
        return super(CampaignViewSet, self).list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        self.permission_classes = (IsOwner,)
        return super(CampaignViewSet, self).create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        self.permission_classes = (IsOwner,)
        return super(CampaignViewSet, self).update(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CampaignEventViewSet(viewsets.ModelViewSet):
    """
    Creates, Updates, and retrives Campaigns
    """
    queryset = CampaignEvent.objects.all()
    serializer_class = CampaignEventSerializer
    permission_classes = (IsOwnerOfCampaign,)

    def get_queryset(self):
        return CampaignEvent.objects.filter(campaign_id=self.kwargs['campaign'])

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(campaign=Campaign.objects.get(id=self.kwargs['campaign']))


class EventNotificationView(APIView):
    queryset = EventNotification.objects.all()
    serializer_class = EventNotificationSerializer
    permission_classes = (IsOwner,)

    def get(self, request):

        qs = EventNotification.objects.filter(
            recorded_event__event__campaign__user=self.request.user
        ).select_related('recorded_event').prefetch_related(
            'recorded_event__event__campaign'
        ).order_by('-date_created')

        data = EventNotificationSerializer(qs, many=True).data

        return Response(data)


class PostEventNotificationView(APIView):
    queryset = EventNotification.objects.all()
    serializer_class = CreateEventNotificationSerializer
    permission_classes = (IsOwner,)

    def post(self, request, recorded_event_id):
        user = self.request.user

        try:
            recorded_event = RecordedEvent.objects.prefetch_related(
                'event', 'event__campaign',
            ).get(
                id=recorded_event_id,
                event__campaign__user=user
            )
        except RecordedEvent.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        data = {
            'recorded_event': recorded_event_id,
            'number_sent': recorded_event.tokens.count()
        }
        data.update(request.data)

        instance = CreateEventNotificationSerializer(
            data=data
        )
        if instance.is_valid():
            event_notification = instance.save()

            return Response(
                data=EventNotificationSerializer(event_notification).data
            )
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


def notification_redirection(request, notification_id):

    try:
        notification = EventNotification.objects.get(id=notification_id)
    except EventNotification.DoesNotExist:
        return HttpResponseRedirect(settings.HOMEPAGE_URL)

    notification.number_opened += 1
    notification.save()

    return HttpResponseRedirect(notification.url)