from rest_framework import serializers
from .models import User
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from drf_spectacular.utils import extend_schema_field
from user_profile.models import Profile

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=68, min_length=6, write_only=True
    )

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password']

    def validate(self, attrs):
        email = attrs.get('email', '')
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({'email': ('Email is already in use')})
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255, min_length=3)
    password = serializers.CharField(max_length=68, min_length=6, write_only=True)
    tokens = serializers.SerializerMethodField()

    @extend_schema_field(serializers.DictField)
    def get_tokens(self, obj):
        user = User.objects.get(email=obj['email'])
        return user.tokens()

    class Meta:
        model = User
        fields = ['email', 'password', 'tokens']

    def validate(self, attrs):
        email = attrs.get('email', '')
        password = attrs.get('password', '')

        user = authenticate(email=email, password=password)

        if not user:
            raise AuthenticationFailed('Invalid credentials, try again')
        if not user.is_active:
            raise AuthenticationFailed('Account disabled, contact admin')

        return {
            'email': user.email,
            'tokens': user.tokens
        }

class GoogleAuthSerializer(serializers.Serializer):
    id_token = serializers.CharField()


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField()


class VerifyEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)


class UserWithProfileSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()
    name = serializers.CharField(source='first_name')

    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'profile']

    @extend_schema_field(serializers.DictField)
    def get_profile(self, obj):
        from user_profile.serializers import ProfileSerializer
        profile, _ = Profile.objects.get_or_create(user=obj)
        return ProfileSerializer(profile).data