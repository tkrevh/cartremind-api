# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import requests
import json
from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import redirect

from rest_framework import status, mixins, viewsets
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from users.permissions import HasAPIAccess

from .permissions import IsOwner, IsOwnerOfCampaign
from .serializers import (
    CampaignEventSerializer,
    CampaignSerializer,
    CreateCampaignSerializer
)
from .models import RecordedEvent, CampaignEvent, Campaign


# Create your views here.
class RecordEventView(APIView):
    permission_classes = (IsAuthenticated, HasAPIAccess)

    def post(self, request, campaign, event_id, format=None):
        data = request.data
        user = request.user
        token = data.get('token')
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

        RecordedEvent.objects.create(
            event=campaign_event,
            token=token
        )

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


def send_test_notification(request, recorded_event_id):

    URL = "https://fcm.googleapis.com/fcm/send"
    API_KEY = "AAAAry4xbXQ:APA91bFM6lFskgOsjsPXhdHhdCRA4CafRDw5RNE4RdZjrDeSAgKiTKo0Z9M_spLufLH6rJOUA1xwfnnt0tExqTyig612p3Pu9EiLNcsZj80UHbWA2Dtyu0vyA3jpxblI5vhAgkrQ17dE"
    HEADERS = {
        "Content-Type": "application/json",
        "Authorization": "key={}".format(API_KEY)
    }

    recorded_event = RecordedEvent.objects.get(pk=recorded_event_id)

    payload = {
       "notification": {
         "title": "Free delivery",
         "body": "Get your free delivery now!",
         "icon": "https://t6.rbxcdn.com/b76c17b045192b22d881f24d8c4dd813",
         "click_action": "https://www.nike.com/si/en_gb/?cp=euns_kw_bra!si!goo!core!c!b!%2Bnike%20%2Bstore!164850714626&gclid=Cj0KCQiArYDQBRDoARIsAMR8s_TkhWJ_LeU_5Op3RWtBUgAHDEgLdJUOF1qJNhhjXE5LKfhv6WwzcXsaAk4mEALw_wcB&gclsrc=aw.ds"
       },
       "to": recorded_event.token
     }
    r = requests.post(URL, data=json.dumps(payload), headers=HEADERS)
    messages.info(request, 'Notification sent')
    return redirect('admin:core_recordedevent_changelist')


class DashboardView(APIView):
    """
    View to list all users in the system.

    * Requires token authentication.
    * Only admin users are able to access this view.
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        user = request.user

        user_campaigns = Campaign.objects.filter(user=user)
        number_of_campaigns = user_campaigns.count()
        campaign_events = CampaignEvent.objects.filter(campaign__in=user_campaigns)
        number_of_campaign_events = campaign_events.count()
        number_of_registered_signups = RecordedEvent.objects.filter(event__in=campaign_events).count()

        data = {
            'number_of_campaigns': number_of_campaigns,
            'number_of_campaign_events': number_of_campaign_events,
            'number_of_registered_signups': number_of_registered_signups,
            'number_of_sent_notifications': 0
        }

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
