from rest_framework.authentication import TokenAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed
from .models import APIKey


class ApiKeyAuthentication(TokenAuthentication):

    def get_token_from_auth_header(self, auth):
        auth = auth.split()
        if not auth or auth[0].lower() != b'api-key':
            return None

        if len(auth) == 1:
            raise AuthenticationFailed('Invalid token header. No credentials provided.')
        elif len(auth) > 2:
            raise AuthenticationFailed('Invalid token header. Token string should not contain spaces.')

        try:
            return auth[1].decode()
        except UnicodeError:
            raise AuthenticationFailed('Invalid token header. Token string should not contain invalid characters.')

    def authenticate(self, request):
        auth = get_authorization_header(request)
        token = self.get_token_from_auth_header(auth)

        if not token:
            token = request.GET.get('api-key', request.POST.get('api-key', None))

        if token:
            return self.authenticate_credentials(token)

    def authenticate_credentials(self, key):
        try:
            token = APIKey.objects.get(key=key)
        except APIKey.DoesNotExist:
            raise AuthenticationFailed('Invalid Api key.')

        if not token.is_active:
            raise AuthenticationFailed('Api key inactive or deleted.')

        user = token.company.users.first()  # what ever you want here
        return (user, token)