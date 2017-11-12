from rest_framework import serializers

from .models import CampaignEvent, Campaign, EventNotification, RecordedEvent


class Base64ImageField(serializers.ImageField):
    """
    A Django REST framework field for handling image-uploads through raw post data.
    It uses base64 for encoding and decoding the contents of the file.

    Heavily based on
    https://github.com/tomchristie/django-rest-framework/pull/1268

    Updated for Django REST framework 3.
    """

    def to_internal_value(self, data):
        from django.core.files.base import ContentFile
        import base64
        import six
        import uuid

        # Check if this is a base64 string
        if isinstance(data, six.string_types):
            # Check if the base64 string is in the "data:" format
            if 'data:' in data and ';base64,' in data:
                # Break out the header from the base64 content
                header, data = data.split(';base64,')

            # Try to decode the file. Return validation error if it fails.
            try:
                decoded_file = base64.b64decode(data)
            except TypeError:
                self.fail('invalid_image')

            # Generate file name:
            file_name = str(uuid.uuid4())[:12]  # 12 characters are more than enough.
            # Get the file name extension:
            file_extension = self.get_file_extension(file_name, decoded_file)

            complete_file_name = "%s.%s" % (file_name, file_extension,)

            data = ContentFile(decoded_file, name=complete_file_name)

        return super(Base64ImageField, self).to_internal_value(data)

    def get_file_extension(self, file_name, decoded_file):
        import imghdr

        extension = imghdr.what(file_name, decoded_file)
        extension = "jpg" if extension == "jpeg" else extension

        return extension


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


class RecordedEventSerializer(serializers.ModelSerializer):

    event_name = serializers.SerializerMethodField()
    campaign_name = serializers.SerializerMethodField()
    number_of_subscribers = serializers.SerializerMethodField()

    def get_event_name(self, instance):
        return instance.event.name

    def get_campaign_name(self, instance):
        return instance.event.campaign.name

    def get_number_of_subscribers(self, instance):
        return instance.tokens.count()

    class Meta:
        model = RecordedEvent
        fields = (
            'id', 'event_name', 'campaign_name', 'url', 'page_title', 'date_created', 'date_modified',
            'number_of_subscribers'
        )


class CreateCampaignSerializer(serializers.ModelSerializer):

    class Meta:
        model = Campaign
        fields = ('id', 'name', 'base_url', 'description', )
        read_only_fields = ('id',)


class CreateEventNotificationSerializer(serializers.ModelSerializer):

    icon = Base64ImageField(max_length=None, use_url=True, required=True)

    class Meta:
        model = EventNotification
        fields = ('title', 'body', 'icon', 'url', 'number_sent', 'recorded_event')


class EventNotificationSerializer(serializers.ModelSerializer):

    campaign_name = serializers.SerializerMethodField()
    event_name = serializers.SerializerMethodField()
    event_url = serializers.SerializerMethodField()
    event_page_title = serializers.SerializerMethodField()

    def get_campaign_name(self, instance):
        return instance.recorded_event.event.campaign.name

    def get_event_name(self, instance):
        return instance.recorded_event.event.name

    def get_event_url(self, instance):
        return instance.recorded_event.url

    def get_event_page_title(self, instance):
        return instance.recorded_event.page_title

    # read only serializer
    class Meta:
        model = EventNotification
        fields = (
            'id', 'title', 'body', 'url', 'number_sent', 'number_opened', 'campaign_name',
            'event_name', 'event_url', 'event_page_title'
        )
        read_only_fields = (
            'id', 'title', 'body', 'url', 'number_sent', 'number_opened', 'campaign_name',
            'event_name', 'event_url', 'event_page_title'
        )
