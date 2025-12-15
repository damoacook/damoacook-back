from rest_framework import serializers
from .models import PopupBanner


class PopupBannerSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    MAX_IMAGE_MB = 100  # 원하는 최대 용량(MB)

    class Meta:
        model = PopupBanner
        fields = (
            "id",
            "title",
            "image",  # 업로드용(요청에서만 받기)
            "image_url",  # 응답에서 쓸 절대 URL
            "link_url",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("created_at", "updated_at")
        extra_kwargs = {
            "image": {
                "required": True,
                "write_only": True,
            },  # 응답에 파일필드 노출 안 함
            "link_url": {"required": False, "allow_blank": True, "allow_null": True},
        }

    def validate_image(self, file):
        if not file:
            return file
        # 콘텐츠 타입(이미지인지) 1차 검증
        ctype = getattr(file, "content_type", "") or ""
        if not ctype.startswith("image/"):
            raise serializers.ValidationError("이미지 파일만 업로드할 수 있습니다.")
        # 용량 검증
        limit = self.MAX_IMAGE_MB * 1024 * 1024
        if file.size > limit:
            raise serializers.ValidationError(
                f"이미지 용량이 {self.MAX_IMAGE_MB}MB를 초과했습니다."
            )
        return file

    def get_image_url(self, obj):
        try:
            url = obj.image.url
            req = self.context.get("request")
            return req.build_absolute_uri(url) if req and url.startswith("/") else url
        except Exception:
            return None
