from rest_framework import serializers
from .models import News


class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = (
            "id",
            "title",
            "content",
            "image",
            "views",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("views", "created_at", "updated_at")
        extra_kwargs = {"image": {"required": False, "allow_null": True}}

    def update(self, instance, validated_data):
        request = self.context.get("request")

        # ✅ 삭제 플래그 우선 처리
        if request:
            flag = request.data.get("remove_image")
            remove_flag = str(flag).lower() in ("1", "true", "on", "yes")

            # 새 파일 업로드 여부(교체)
            has_new_file = "image" in validated_data and bool(
                validated_data.get("image")
            )

            if remove_flag and not has_new_file:
                # 기존 파일 삭제 + 필드 비우기
                if instance.image:
                    instance.image.delete(save=False)
                instance.image = None
                # validated_data에 image가 있으면 제거
                validated_data.pop("image", None)

            elif has_new_file:
                # 새 파일로 교체할 때 기존 파일 삭제
                if instance.image:
                    instance.image.delete(save=False)
                # 이후 super().update에서 새 파일 저장

            # (remove_flag 가 true여도 새 파일이 있으면 교체가 우선)

        return super().update(instance, validated_data)
