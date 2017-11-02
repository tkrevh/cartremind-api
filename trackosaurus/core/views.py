# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from rest_framework import status, mixins, viewsets
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import RecordedEvent, CampaignEvent, Campaign


# Create your views here.
class RecordEventView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, code, format=None):
        data = request.data
        user = request.user
        token = data.get('token')
        campaign_event = CampaignEvent.objects.get(code=code)

        if campaign_event.user.pk != user.pk:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        RecordedEvent.objects.create(
            event = campaign_event,
            token = token
        )

        return Response(status=status.HTTP_201_CREATED)


class ListCampaignEventsView(ListAPIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, campaign, format=None):
        data = request.data
        user = request.user
        token = data.get('token')
        campaign_event = CampaignEvent.objects.get(code=code)

        if campaign_event.user.pk != user.pk:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        RecordedEvent.objects.create(
            event = campaign_event,
            token = token
        )

        return Response(status=status.HTTP_201_CREATED)
