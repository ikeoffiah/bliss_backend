from django.shortcuts import render
from rest_framework import generics, status, views, permissions
from rest_framework.response import Response
from .serializers import (
    RegisterSerializer, 
    LoginSerializer, 
    GoogleAuthSerializer,
    EmailSerializer,
    UserWithProfileSerializer,
    VerifyEmailSerializer
)
from .models import User, OneTimePassword
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from .utils import Util
import firebase_admin
from firebase_admin import auth

class RegisterView(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request):
        user = request.data
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user_data = serializer.data

        # Explicitly set is_active to True for now as requested for completeness
        user_obj = User.objects.get(email=user_data['email'])
        # user_obj.is_active = True # Removed: User must verify email first
        user_obj.save()

        # Send OTP
        Util.send_generated_otp(user_obj)

        response_data = {
            'message': 'Account created successfully. A verification code has been sent to your email.',
            'user': UserWithProfileSerializer(user_obj).data
        }

        return Response(response_data, status=status.HTTP_201_CREATED)


class LoginAPIView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = User.objects.get(email=serializer.validated_data['email'])
        tokens = user.tokens()
        
        response_data = {
            'token': tokens['access'],
            'user': UserWithProfileSerializer(user).data
        }
        return Response(response_data, status=status.HTTP_200_OK)


class GoogleSocialAuthView(generics.GenericAPIView):
    serializer_class = GoogleAuthSerializer

    def post(self, request):
        """
        POST with "id_token"
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        id_token = serializer.validated_data['id_token']

        try:
            decoded_token = auth.verify_id_token(id_token)
            email = decoded_token.get('email')
            name = decoded_token.get('name', 'User')
            
            # Split name into first and last
            name_parts = name.split(' ', 1)
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else ''

            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'user_type': 'google',
                    'is_active': True
                }
            )
            
            return Response(user.tokens(), status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class VerifyEmailView(generics.GenericAPIView):
    serializer_class = VerifyEmailSerializer
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        otp_code = serializer.validated_data['otp']
        
        try:
            user = User.objects.get(email=email)
            otp_obj = OneTimePassword.objects.get(user=user)
            
            if otp_obj.code == otp_code:
                user.is_active = True
                user.save()
                otp_obj.delete() # Remove code after success
                
                return Response({'success': 'Email verified successfully. You can now login.'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid verification code'}, status=status.HTTP_400_BAD_REQUEST)
                
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except OneTimePassword.DoesNotExist:
             return Response({'error': 'Verification code not found or already verified'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class RequestPasswordResetEmail(generics.GenericAPIView):
    serializer_class = EmailSerializer
    
    def post(self, request):
        email = request.data.get('email', '')

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            
            # In a real app, send email here. 
            # For now, return the link as proof of concept if needed or just success
            return Response({'success': 'We have sent you a link to reset your password', 'uidb64': uidb64, 'token': token}, status=status.HTTP_200_OK)
        
        return Response({'error': 'User with this email does not exist'}, status=status.HTTP_404_NOT_FOUND)
