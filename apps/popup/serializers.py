from rest_framework import serializers
from .models import PopupBanner

class PopupBannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = PopupBanner
        fields = (
            'id', 'title', 'image', 'link_url',
            'is_active', 'created_at', 'updated_at'
        )
        read_only_fields = ('created_at', 'updated_at')
        extra_kwargs = {
            'image': {'required': True},
            'link_url': {'required': False, 'allow_null': True},
        }