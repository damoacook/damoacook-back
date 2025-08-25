from rest_framework import serializers
from .models import Inquiry

class InquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inquiry
        fields = ['id', 'name', 'phone', 'message', 'created_at']
        read_only_fields = ['id', 'created_at']
