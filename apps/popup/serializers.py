from rest_framework import serializers
from .models import PopupBanner


class PopupBannerSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    MAX_IMAGE_MB = 100

    class Meta:
        model = PopupBanner
        fields = (
            "id",
            "title",
            "image",  # ← 쓰기/읽기 허용(읽기 시 절대 URL로 가공)
            "image_url",  # ← 선택: 보조
            "link_url",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("created_at", "updated_at")
        extra_kwargs = {
            # write_only 제거! 응답에도 image 포함
            "image": {"required": True},
            "link_url": {"required": False, "allow_blank": True, "allow_null": True},
        }

    def validate_image(self, file):
        if not file:
            return file
        ctype = getattr(file, "content_type", "") or ""
        if not ctype.startswith("image/"):
            raise serializers.ValidationError("이미지 파일만 업로드할 수 있습니다.")
        limit = self.MAX_IMAGE_MB * 1024 * 1024
        if file.size > limit:
            raise serializers.ValidationError(
                f"이미지 용량이 {self.MAX_IMAGE_MB}MB를 초과했습니다."
            )
        return file

    def _abs_url(self, url: str):
        req = self.context.get("request")
        if req and url and url.startswith("/"):
            return req.build_absolute_uri(url)
        return url

    def get_image_url(self, obj):
        try:
            return self._abs_url(obj.image.url)
        except Exception:
            return None

    def to_representation(self, instance):
        data = super().to_representation(instance)
        try:
            data["image"] = self._abs_url(instance.image.url)
        except Exception:
            data["image"] = None
        data["image_url"] = data.get("image")
        return data
