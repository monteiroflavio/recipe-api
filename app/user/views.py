from rest_framework import generics, authentication, permissions
from rest_framework.settings import api_settings
from rest_framework.authtoken.views import ObtainAuthToken
from user.serializers import UserSerializer, AuthTokenSerializer


class CreateUserView(generics.CreateAPIView):
    """Creates a new user."""
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """Creates a new auth token for a user."""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manages the authenticated user."""
    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication, ]
    permission_classes = [permissions.IsAuthenticated, ]

    def get_object(self):
        """Retrieves and returns an authenticated user."""
        return self.request.user
