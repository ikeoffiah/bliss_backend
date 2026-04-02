from rest_framework import serializers
from .models import Profile
from authentication.models import User

class ProfileSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='user.first_name', required=False)
    relationship_stage = serializers.CharField(required=False)

    class Meta:
        model = Profile
        fields = [
            'name',
            'relationship_start_date',
            'relationship_stage',
            'relationship_goal',
            'image_url',
            'invite_code'
        ]
        read_only_fields = ['invite_code']

    def validate_relationship_stage(self, value):
        valid_stages = [choice[0] for choice in Profile.STAGE_CHOICES]
        upper_val = value.upper()
        if upper_val not in valid_stages:
            # Handle "rekindling" vs "REKINDLED" if needed
            if upper_val == "REKINDLING":
                return "REKINDLED"
            raise serializers.ValidationError(f"Must be one of: {', '.join(valid_stages)}")
        return upper_val

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        first_name = user_data.get('first_name')
        
        if first_name:
            instance.user.first_name = first_name
            instance.user.save()
            
        return super().update(instance, validated_data)

    def create(self, validated_data):
        user_data = validated_data.pop('user', {})
        # Note: In a real app, 'user' is passed from request.user in the view
        # This serializer will be used largely for updates or first-time setups
        return super().create(validated_data)
