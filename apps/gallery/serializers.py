from rest_framework import serializers
from .models import GalleryImage

class GalleryImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = GalleryImage
        fields = ('id', 'title', 'image', 'description', 'views', 'uploaded_at')
        read_only_fields = ('views', 'uploaded_at')
        extra_kwargs = {
            'description': {'required': False, 'allow_blank': True},
            'image': {'required': True},
        }