from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User


def get_tokens_for_user(user):
    """Generate JWT pair with role + email embedded in payload."""
    refresh = RefreshToken.for_user(user)
    refresh['role'] = user.role
    refresh['email'] = user.email
    refresh['full_name'] = user.get_full_name()
    return {
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    }


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, validators=[validate_password], style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True, style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = [
            'email', 'first_name', 'last_name', 'phone',
            'role', 'password', 'password_confirm',
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('password_confirm'):
            raise serializers.ValidationError({'password': 'Passwords do not match.'})
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    def validate(self, attrs):
        user = authenticate(email=attrs['email'], password=attrs['password'])
        if not user:
            raise serializers.ValidationError('Invalid email or password.')
        if not user.is_active:
            raise serializers.ValidationError('This account has been deactivated.')
        attrs['user'] = user
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    company_name = serializers.CharField(source='company.name', read_only=True, default=None)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'phone', 'role', 'avatar', 'company', 'company_name',
            'is_active', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'email', 'role', 'created_at', 'updated_at']

    def get_full_name(self, obj):
        return obj.get_full_name()


class UserListSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    company_name = serializers.CharField(source='company.name', read_only=True, default=None)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'full_name', 'first_name', 'last_name',
            'role', 'phone', 'company', 'company_name', 'is_active', 'created_at',
        ]

    def get_full_name(self, obj):
        return obj.get_full_name()


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(
        write_only=True, style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
        style={'input_type': 'password'},
    )
    new_password_confirm = serializers.CharField(
        write_only=True, style={'input_type': 'password'}
    )

    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Current password is incorrect.')
        return value

    def validate(self, attrs):
        if attrs['new_password'] != attrs.pop('new_password_confirm'):
            raise serializers.ValidationError({'new_password': 'Passwords do not match.'})
        return attrs
