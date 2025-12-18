from rest_framework import serializers
from .models import GalleryImage


class GalleryImageSerializer(serializers.ModelSerializer):
    # 읽기용 보조 필드(선택). 하위 호환 위해 유지
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = GalleryImage
        fields = (
            "id",
            "title",
            "description",
            "views",
            "uploaded_at",
            "image",  # ← 쓰기/읽기 모두 허용(읽기 시 절대 URL로 가공)
            "image_url",  # ← 선택: 프론트에서 쓰면 동일 값
        )
        read_only_fields = ("views", "uploaded_at")
        extra_kwargs = {
            "description": {"required": False, "allow_blank": True},
            # write_only 제거! 응답에 image 포함시키기 위함
            "image": {"required": True},
        }

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
        # image 필드 값을 항상 절대 URL로 보정
        try:
            data["image"] = self._abs_url(instance.image.url)
        except Exception:
            data["image"] = None
        # image_url도 image와 동일하게 맞춰줌(편의)
        data["image_url"] = data.get("image")
        return data
