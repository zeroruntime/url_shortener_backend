from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Links(models.Model):
    user_id = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    short_code = models.CharField(max_length=6, db_index=True, unique=True)
    original_url = models.URLField()
    is_active = models.BooleanField()
    expires_at = models.DateTimeField(null=True, blank=True)

class Clicks(models.Model):
    DEVCE_CHOICES = [
        ('mobile', 'Mobile'),
        ('tablet', 'Tablet'),
        ('desktop', 'Desktop'),
        ('bot', 'Bot')
    ]

    link_id = models.ForeignKey(Links, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(db_index=True)
    country = models.CharField(max_length=3)
    device_type = models.CharField(choices=DEVCE_CHOICES)
    referrer = models.TextField()
