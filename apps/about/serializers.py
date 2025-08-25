
from rest_framework import serializers
from .models import About

class AboutSerializer(serializers.ModelSerializer):
    class Meta:
        model = About
        fields = (
            'id', 'greeting', 'vision',
            'address', 'phone', 'opening_hours',
            'latitude', 'longitude',
            'image', 'updated_at'
        )
        read_only_fields = ('updated_at',)
        extra_kwargs = {
            'image': {'required': False, 'allow_null': True},
            'latitude': {'required': False, 'allow_null': True},
            'longitude': {'required': False, 'allow_null': True},
        }