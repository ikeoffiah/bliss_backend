from django.urls import path
from .views import (
    RegisterView,
    LoginAPIView,
    GoogleSocialAuthView,
    RequestPasswordResetEmail,
    VerifyEmailView
)

urlpatterns = [
    path('signup/', RegisterView.as_view(), name="signup"),
    path('verify-email/', VerifyEmailView.as_view(), name="verify-email"),
    path('login/', LoginAPIView.as_view(), name="login"),
    path('google/', GoogleSocialAuthView.as_view(), name="google-login"),
    path('forgot-password/', RequestPasswordResetEmail.as_view(), name="forgot-password"),
]
