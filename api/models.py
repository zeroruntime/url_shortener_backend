from django.db import models
from django.contrib.auth.models import User

class Links(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    short_code = models.CharField(max_length=7, db_index=True, unique=True)
    original_url = models.URLField()
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.short_code} -> {self.original_url[:50]}..."

    class Meta:
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['is_active', 'expires_at']),
        ]


class Clicks(models.Model):
    DEVICE_CHOICES = [
        ('mobile', 'Mobile'),
        ('tablet', 'Tablet'),
        ('desktop', 'Desktop'),
        ('bot', 'Bot'),
        ('other', 'Other')
    ]

    link = models.ForeignKey(Links, on_delete=models.CASCADE, related_name='clicks', null=True, blank=True)
    timestamp = models.DateTimeField(db_index=True, auto_now_add=True)
    country = models.CharField(max_length=3, null=True, blank=True)
    device_type = models.CharField(max_length=20, choices=DEVICE_CHOICES, default='other')
    referrer = models.URLField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    def __str__(self):
        return f"Click on {self.link.short_code if self.link else 'Unknown'} at {self.timestamp}"
