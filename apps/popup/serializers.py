from rest_framework import serializers
from .models import PopupBanner


class PopupBannerSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    MAX_IMAGE_MB = 100  # 여기서 원하는 MB로 조정

    class Meta:
        model = PopupBanner
        fields = (
            "id",
            "title",
            "image",
            "image_url",
            "link_url",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("created_at", "updated_at")
        extra_kwargs = {"image": {"required": True}}

    def validate_image(self, file):
        limit = self.MAX_IMAGE_MB * 1024 * 1024
        if file and file.size > limit:
            raise serializers.ValidationError(
                f"이미지 용량이 {self.MAX_IMAGE_MB}MB를 초과했습니다."
            )
        return file

    def get_image_url(self, obj):
        try:
            url = obj.image.url
            req = self.context.get("request")
            return (
                req.build_absolute_uri(url)
                if req and url and url.startswith("/")
                else url
            )
        except Exception:
            return None
