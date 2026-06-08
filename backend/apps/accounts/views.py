from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from drf_spectacular.utils import extend_schema

from .models import User
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
    UserListSerializer,
    ChangePasswordSerializer,
    get_tokens_for_user,
)
from .permissions import IsSuperAdmin, IsOwnerOrSuperAdmin


@extend_schema(tags=['Auth'])
class RegisterView(APIView):
    """
    Create a new user account.

    - Without authentication: only allowed for the very first Super Admin setup.
    - Authenticated as Super Admin: can create any role.
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = UserRegistrationSerializer

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        requested_role = serializer.validated_data.get('role', User.EMPLOYEE)

        if not request.user.is_authenticated:
            if requested_role != User.SUPER_ADMIN:
                return Response(
                    {'detail': 'Unauthenticated registration is only for initial Super Admin setup.'},
                    status=status.HTTP_403_FORBIDDEN,
                )
            if User.objects.filter(role=User.SUPER_ADMIN).exists():
                return Response(
                    {'detail': 'Super Admin already exists. Contact your administrator.'},
                    status=status.HTTP_403_FORBIDDEN,
                )
        elif not request.user.is_super_admin:
            return Response(
                {'detail': 'Only Super Admin can create user accounts.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        user = serializer.save()
        return Response(
            {
                'user': UserProfileSerializer(user).data,
                'tokens': get_tokens_for_user(user),
            },
            status=status.HTTP_201_CREATED,
        )


@extend_schema(tags=['Auth'])
class LoginView(APIView):
    """Obtain JWT access + refresh tokens."""
    permission_classes = [permissions.AllowAny]
    serializer_class = UserLoginSerializer

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        return Response({
            'user': UserProfileSerializer(user).data,
            'tokens': get_tokens_for_user(user),
        })


@extend_schema(tags=['Auth'])
class LogoutView(APIView):
    """Blacklist the refresh token (invalidates the session)."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response(
                {'detail': 'refresh token is required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            return Response(
                {'detail': 'Invalid or expired token.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response({'detail': 'Logged out successfully.'}, status=status.HTTP_205_RESET_CONTENT)


@extend_schema(tags=['Auth'])
class MeView(generics.RetrieveUpdateAPIView):
    """Get or update the currently authenticated user's profile."""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user


@extend_schema(tags=['Auth'])
class ChangePasswordView(APIView):
    """Change password for the authenticated user."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save(update_fields=['password', 'updated_at'])
        return Response({'detail': 'Password changed successfully.'})


@extend_schema(tags=['Users'])
class UserListView(generics.ListAPIView):
    """List all users (Super Admin only)."""
    permission_classes = [IsSuperAdmin]
    serializer_class = UserListSerializer
    search_fields = ['email', 'first_name', 'last_name']
    filterset_fields = ['role', 'is_active']

    def get_queryset(self):
        return User.objects.select_related('company').order_by('-created_at')


@extend_schema(tags=['Users'])
class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or deactivate a user. Owner or Super Admin."""
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrSuperAdmin]
    serializer_class = UserProfileSerializer
    queryset = User.objects.select_related('company').all()
    lookup_field = 'id'

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        user.is_active = False
        user.save(update_fields=['is_active', 'updated_at'])
        return Response({'detail': 'User deactivated.'}, status=status.HTTP_200_OK)
