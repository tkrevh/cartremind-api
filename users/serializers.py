from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):

    api_key = serializers.SerializerMethodField()

    def get_api_key(self, user):
        return user.api_key.key

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'api_key', 'subscribers_limit')
        read_only_fields = ('username', 'subscribers_limit', 'api_key')


class CreateUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'email', 'auth_token')
        read_only_fields = ('auth_token',)
        extra_kwargs = {'password': {'write_only': True}}
