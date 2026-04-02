import random
import string
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from user_profile.models import Profile
from .serializers import CodeSerializer, PartnerStatusSerializer

class GenerateCodeView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CodeSerializer
    
    def post(self, request, *args, **kwargs):
        profile, _ = Profile.objects.get_or_create(user=request.user)
        
        # Generate a unique short code
        characters = string.ascii_uppercase + string.digits
        code = ''.join(random.choices(characters, k=6))
        
        # Ensure uniqueness
        while Profile.objects.filter(invite_code=code).exists():
            code = ''.join(random.choices(characters, k=6))
        
        profile.invite_code = code
        profile.save()
        
        return Response({'code': code}, status=status.HTTP_200_OK)

class JoinPartnerView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CodeSerializer
    
    def post(self, request, *args, **kwargs):
        code = request.data.get('code')
        if not code:
            return Response({'error': 'Code is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            partner_profile = Profile.objects.get(invite_code=code)
        except Profile.DoesNotExist:
            return Response({'error': 'Invalid code'}, status=status.HTTP_404_NOT_FOUND)
        
        if partner_profile.user == request.user:
            return Response({'error': 'Cannot join with yourself'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Link both users
        user_profile, _ = Profile.objects.get_or_create(user=request.user)
        user_profile.partner = partner_profile.user
        user_profile.save()
        
        partner_profile.partner = request.user
        partner_profile.save()
        
        return Response({'success': 'Successfully joined with partner'}, status=status.HTTP_200_OK)

class PartnerStatusView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PartnerStatusSerializer
    
    def get(self, request, *args, **kwargs):
        profile, _ = Profile.objects.get_or_create(user=request.user)
        
        status_val = 'NOT_JOINED'
        partner_id = None
        partner_name = None
        
        if profile.partner:
            status_val = 'JOINED'
            partner_id = str(profile.partner.id)
            partner_name = f"{profile.partner.first_name} {profile.partner.last_name}".strip()
            
        return Response({
            'status': status_val,
            'partner_id': partner_id,
            'partner_name': partner_name
        }, status=status.HTTP_200_OK)
