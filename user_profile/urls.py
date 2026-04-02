from django.urls import path
from .views import ProfileView, ImageUploadView

urlpatterns = [
    path('profile/', ProfileView.as_view(), name='profile-view'),
    path('profile/upload-image/', ImageUploadView.as_view(), name='image-upload'),
]
