from datetime import timezone
from rest_framework import serializers
from .models import *

class LinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Links
        fields = ['id', 'short_code', 'original_url', 'user', 'is_active', 'expires_at']
        read_only_fields = ['id', 'short_code', 'user']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

    def validate_original_url(self, value):
        if not value.startswith(('http://', 'https://')):
            raise serializers.ValidationError("URL must start with http:// or https://")
        return value

    def validate_expires_at(self, value):
        if value and value < timezone.now():
            raise serializers.ValidationError("Expiration date must be in the future")
        return value

class ClickSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clicks
        fields = ['link_id', 'timestamp', 'country', 'device_type', 'referrer']
        read_only_fields = ['link_id', 'timestamp', 'country', 'device_type', 'referrer']
