from django.db import models
from django.conf import settings

class Profile(models.Model):
    STAGE_CHOICES = [
        ('EXPLORATION', 'Exploration'),
        ('DATING', 'Dating'),
        ('ENGAGED', 'Engaged'),
        ('MARRIED', 'Married'),
        ('REKINDLED', 'Rekindled'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile'
    )
    image_url = models.URLField(max_length=500, null=True, blank=True)
    relationship_start_date = models.DateTimeField(null=True, blank=True)
    relationship_stage = models.CharField(
        max_length=20,
        choices=STAGE_CHOICES,
        null=True,
        blank=True
    )
    relationship_goal = models.TextField(null=True, blank=True)
    
    # Fields for partner linking
    partner = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='partner_profile'
    )
    invite_code = models.CharField(max_length=10, unique=True, null=True, blank=True)

    def __str__(self):
        return f"Profile of {self.user.email}"
