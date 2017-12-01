from rest_framework import viewsets, mixins, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from djbraintree.models import BTPlan
from .models import User
from .permissions import IsUserOrReadOnly
from .serializers import CreateUserSerializer, UserSerializer, UpdateUserInfoSerializer


class UserViewSet(mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  viewsets.GenericViewSet):
    """
    Creates, Updates, and retrives User accounts
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsUserOrReadOnly,)

    def create(self, request, *args, **kwargs):
        self.serializer_class = CreateUserSerializer
        self.permission_classes = (AllowAny,)
        return super(UserViewSet, self).create(request, *args, **kwargs)


class RegisterUserView(APIView):
    permission_classes = (AllowAny, )

    def post(self, request, format=None):
        instance = CreateUserSerializer(data=request.data)
        if instance.is_valid():
            user = User.objects.create_user(
                instance.validated_data['username'],
                instance.validated_data['email'],
                instance.validated_data['password']
            )
            plan = BTPlan.objects.get(name='free')
            plan.user_group.user_set.add(user)
            data = {
                'token': user.auth_token.key
            }
            return Response(data, status=status.HTTP_201_CREATED)
        else:
            return Response(instance._errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateUserInfoView(APIView):
    permission_classes = (IsUserOrReadOnly, )

    def post(self, request, format=None):
        user = request.user
        instance = UpdateUserInfoSerializer(data=request.data)
        if instance.is_valid():
            user.email = instance.validated_data.get('email')
            user.first_name = instance.validated_data.get('first_name')
            user.last_name = instance.validated_data.get('last_name')
            user.company_name = instance.validated_data.get('company_name')
            user.vat_id = instance.validated_data.get('vat_id')
            user.street = instance.validated_data.get('street')
            user.city = instance.validated_data.get('city')
            user.zip = instance.validated_data.get('zip')
            user.country = instance.validated_data.get('country')
            user.save()
            return Response(
                data=UserSerializer(user).data,
                status=status.HTTP_200_OK
            )
        else:
            return Response(instance._errors, status=status.HTTP_400_BAD_REQUEST)


class UserInfoView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):

        data = UserSerializer(request.user).data

        return Response(data, status=status.HTTP_200_OK)