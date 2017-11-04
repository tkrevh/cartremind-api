# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from rest_framework import status, mixins, viewsets
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.permissions import HasAPIAccess
from .serializers import CampaignEventSerializer
from .models import RecordedEvent, CampaignEvent, Campaign


# Create your views here.
class RecordEventView(APIView):
    permission_classes = (IsAuthenticated, HasAPIAccess)

    def post(self, request, campaign, code, format=None):
        data = request.data
        user = request.user
        token = data.get('token')
        try:
            campaign_event = CampaignEvent.objects.get(
                campaign_id=campaign,
                code=code
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
