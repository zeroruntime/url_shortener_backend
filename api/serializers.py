from django.utils import timezone
from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User

class LinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Links
        fields = ['id', 'short_code', 'original_url', 'custom_alias', 'user', 'is_active', 'expires_at']
        read_only_fields = ['id', 'short_code', 'user']
    
    def validate_custom_alias(self, value):
        if value and Links.objects.filter(custom_alias=value).exclude(id=self.instance.id if self.instance else None).exists():
            raise serializers.ValidationError("This custom alias is already taken")
        return value

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

class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=False)

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()