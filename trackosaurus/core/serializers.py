from rest_framework import serializers

from .models import CampaignEvent, Campaign, EventNotification


class CampaignEventSerializer(serializers.ModelSerializer):

    class Meta:
        model = CampaignEvent
        fields = ('id', 'name', 'description', 'type')


class CampaignSerializer(serializers.ModelSerializer):

    campaign_events = CampaignEventSerializer(many=True, read_only=True)

    class Meta:
        model = Campaign
        fields = (
            'id', 'name', 'base_url', 'description', 'type', 'date_created', 'date_modified',
            'campaign_events'
        )
        read_only_fields = ('id', )


class CreateCampaignSerializer(serializers.ModelSerializer):

    class Meta:
        model = Campaign
        fields = ('id', 'name', 'base_url', 'description', )
        read_only_fields = ('id',)


class CreateEventNotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = EventNotification
        fields = ('id', 'title', 'body', 'icon', 'url')
        read_only_fields = ('id',)
