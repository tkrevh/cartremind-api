from rest_framework import permissions
from rest_framework.authentication import get_authorization_header

from .models import APIKey


class IsUserOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):

        if request.method in permissions.SAFE_METHODS:
            return True

        return obj == request.user


class HasAPIAccess(permissions.BasePermission):
    message = 'Invalid or missing API Key.'

    def has_permission(self, request, view):
        try:
            api_key = request.META.get('HTTP_AUTHORIZATION', ' ').split()[1]
            return APIKey.objects.filter(key=api_key).exists()
        except:
            return False