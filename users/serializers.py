from rest_framework import serializers

from djbraintree.serializers import BTCurrentSubscriptionSerializer
from .models import User


class UserPermissionsSerializer(serializers.ModelSerializer):

    can_access_advanced_configuration = serializers.SerializerMethodField()
    can_segment_notifications = serializers.SerializerMethodField()
    can_use_autoresponder = serializers.SerializerMethodField()
    can_use_timed_messages = serializers.SerializerMethodField()
    can_use_advanced_triggers = serializers.SerializerMethodField()

    def get_can_access_advanced_configuration(self, user):
        return user.can_access_advanced_configuration

    def get_can_segment_notifications(self, user):
        return user.can_segment_notifications

    def get_can_use_autoresponder(self, user):
        return user.can_use_autoresponder

    def get_can_use_timed_messages(self, user):
        return user.can_use_timed_messages

    def get_can_use_advanced_triggers(self, user):
        return user.can_use_advanced_triggers

    class Meta:
        model = User
        fields = (
            'can_access_advanced_configuration', 'can_segment_notifications',
            'can_use_autoresponder', 'can_use_timed_messages', 'can_use_advanced_triggers'
        )
        read_only_fields = (
            'can_access_advanced_configuration', 'can_segment_notifications',
            'can_use_autoresponder', 'can_use_timed_messages', 'can_use_advanced_triggers'
        )


class UserSerializer(serializers.ModelSerializer):

    api_key = serializers.SerializerMethodField()
    subscription = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()

    def get_permissions(self, user):
        return UserPermissionsSerializer(user).data

    def get_subscription(self, user):
        if user.has_subscription:
            return BTCurrentSubscriptionSerializer(user.btsubscription.first()).data
        else:
            return None

    def get_api_key(self, user):
        return user.api_key.key

    class Meta:
        model = User
        fields = (
            'id', 'username', 'first_name', 'last_name', 'email', 'api_key',
            'subscribers_limit', 'subscription', 'permissions', 'email',
            'first_name', 'last_name', 'company_name', 'vat_id', 'street', 'zip',
            'city', 'country'
        )
        read_only_fields = (
            'username', 'subscribers_limit', 'api_key', 'subscription', 'permissions',
            'email', 'first_name', 'last_name', 'company_name', 'vat_id', 'street', 'zip',
            'city', 'country'
        )


class CreateUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'email', 'auth_token')
        read_only_fields = ('auth_token',)
        extra_kwargs = {'password': {'write_only': True}}


class UpdateUserInfoSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'email', 'first_name', 'last_name', 'company_name', 'vat_id', 'street', 'zip', 'city',
            'country'
        )
