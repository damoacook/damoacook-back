from rest_framework import serializers
from .models import Certificate

class CertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificate
        # exam_schedule 필드를 제거하고, 제목·설명·이미지만 노출
        fields = ('id', 'name', 'description', 'image', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')
        extra_kwargs = {
            'image': {'required': False, 'allow_null': True}
        }