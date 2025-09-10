from rest_framework import serializers
from .models import Inquiry


class InquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inquiry
        fields = ["id", "name", "phone", "message", "created_at"]
        read_only_fields = ["id", "created_at"]

    def validate(self, attrs):
        # 봇이 숨김 필드에 값 넣으면 차단
        if attrs.get("honeypot"):
            raise serializers.ValidationError("Invalid submission.")
        # 간단 포맷/길이 검증(선택)
        if len(attrs.get("message", "").strip()) < 5:
            raise serializers.ValidationError("문의 내용은 5자 이상 입력해주세요.")
        return attrs
