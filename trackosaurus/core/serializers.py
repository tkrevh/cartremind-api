from rest_framework import serializers

from .models import CampaignEvent


class CampaignEventSerializer(serializers.ModelSerializer):

    class Meta:
        model = CampaignEvent
        fields = ('id', 'code', 'name')
