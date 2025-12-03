from rest_framework import serializers
from .models import GalleryImage


class GalleryImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = GalleryImage
        fields = (
            "id",
            "title",
            "image_url",  # 읽기용 절대 URL
            "description",
            "views",
            "uploaded_at",
            "image",  # (선택) 쓰기용 업로드 필드
        )
        # 읽기 전용 필드/기본값
        read_only_fields = ("views", "uploaded_at")
        extra_kwargs = {
            "description": {"required": False, "allow_blank": True},
            "image": {"required": True, "write_only": True},
        }

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
