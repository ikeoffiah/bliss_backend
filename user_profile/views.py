from rest_framework import generics, status, permissions
from rest_framework.response import Response
from .models import Profile
from .serializers import ProfileSerializer
from django.core.files.storage import default_storage
from django.conf import settings
import os

class ProfileView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProfileSerializer

    def get_object(self):
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        return profile

    def get(self, request, *args, **kwargs):
        profile = self.get_object()
        serializer = self.get_serializer(profile)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        # Handle POST as GET_OR_CREATE/Update as requested
        profile = self.get_object()
        serializer = self.get_serializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        profile = self.get_object()
        serializer = self.get_serializer(profile, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class ImageUploadView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        file_obj = request.FILES.get('image')
        if not file_obj:
            return Response({'error': 'No image provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        path = default_storage.save(f'profile_images/{request.user.id}_{file_obj.name}', file_obj)
        image_url = request.build_absolute_uri(settings.MEDIA_URL + path)
        
        # Optionally update profile immediately
        profile, _ = Profile.objects.get_or_create(user=request.user)
        profile.image_url = image_url
        profile.save()

        return Response({'url': image_url}, status=status.HTTP_201_CREATED)
