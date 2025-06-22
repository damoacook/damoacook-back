from rest_framework import serializers
from .models import News

class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = ('id', 'title', 'content', 'image', 'views', 'created_at', 'updated_at')
        read_only_fields = ('views', 'created_at', 'updated_at')
        extra_kwargs = {
            'image': {'required': False, 'allow_null': True}
        }