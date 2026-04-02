from django.urls import path
from .views import (
    RegisterView,
    LoginAPIView,
    GoogleSocialAuthView,
    RequestPasswordResetEmail
)

urlpatterns = [
    path('signup/', RegisterView.as_view(), name="signup"),
    path('login/', LoginAPIView.as_view(), name="login"),
    path('google/', GoogleSocialAuthView.as_view(), name="google-login"),
    path('forgot-password/', RequestPasswordResetEmail.as_view(), name="forgot-password"),
]
