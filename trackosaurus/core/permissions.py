from rest_framework import permissions
from rest_framework.authentication import get_authorization_header


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):

        return obj.user == request.user

class IsOwnerOfCampaign(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):

        return obj.campaign.user == request.user
