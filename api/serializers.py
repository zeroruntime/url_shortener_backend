from rest_framework import serializers
from .models import *

class LinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Links
        fields = '__all__'

class ClickSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clicks
        fields = '__all__'
