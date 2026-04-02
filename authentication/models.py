from django.db import models
import uuid
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
    PermissionsMixin,
)
from rest_framework_simplejwt.tokens import RefreshToken


class CustomUserManager(BaseUserManager):
    """Authentication for User"""

    def create_user(self, email, first_name, last_name, password, **extra_fields):

        if email:
            email = self.normalize_email(email)

        user = self.model(
            email=email, first_name=first_name, last_name=last_name, **extra_fields
        )
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, first_name, last_name, password, **extra_fields):
        """Authentication for superuser"""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser is_staff must be True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))

        return self.create_user(
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password,
            **extra_fields,
        )


class User(AbstractBaseUser, PermissionsMixin):
    """User model authentication for all type of user authentications"""

    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    user_type = models.CharField(
        max_length=20,
        choices=[("regular", "Regular"), ("google", "Google")],
        default="regular",
    )
    unique_pass = models.TextField(unique=True, null=True, blank=True)

    # user status
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    # date
    last_login = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def tokens(self):
        refresh_token = RefreshToken.for_user(self)
        return {
            "refresh": str(refresh_token),
            "access": str(refresh_token.access_token),
        }


class OneTimePassword(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6, unique=True)

    def __str__(self):
        return f"{self.user.first_name}-otp code"