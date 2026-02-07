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

class ClickSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clicks
        fields = '__all__'
