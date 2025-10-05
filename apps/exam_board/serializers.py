# apps/exam_board/serializers.py
from rest_framework import serializers
from django.utils import timezone
from .models import ExamPost, Attachment

import bleach
from bleach.sanitizer import Cleaner
from bleach.css_sanitizer import CSSSanitizer

# CKEditor 등 리치텍스트에서 사용하는 대표 태그/속성 화이트리스트
ALLOWED_TAGS = [
    "p",
    "br",
    "div",
    "span",
    "strong",
    "em",
    "u",
    "s",
    "code",
    "pre",
    "blockquote",
    "hr",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "ul",
    "ol",
    "li",
    "table",
    "thead",
    "tbody",
    "tr",
    "th",
    "td",
    "a",
    "img",
    "figure",
    "figcaption",
]
ALLOWED_ATTRS = {
    "*": ["class", "style"],
    "a": ["href", "title", "target", "rel"],
    "img": ["src", "alt", "title", "width", "height"],
    "table": ["border", "cellpadding", "cellspacing"],
    "th": ["colspan", "rowspan"],
    "td": ["colspan", "rowspan"],
}
css_sanitizer = CSSSanitizer(
    allowed_css_properties=[
        "color",
        "background-color",
        "font-size",
        "font-weight",
        "font-style",
        "text-decoration",
        "text-align",
        "font-family",
        "line-height",
        "letter-spacing",
        "margin",
        "padding",
        "border",
        "border-color",
        "border-width",
        "border-style",
        "width",
        "height",
        "max-width",
    ]
)
cleaner = Cleaner(
    tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS, css_sanitizer=css_sanitizer, strip=True
)


def _link_target_blank(attrs, new=False):
    if not new:
        return attrs
    attrs["target"] = "_blank"
    attrs["rel"] = "noopener noreferrer nofollow"
    return attrs


class AttachmentSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = Attachment
        fields = (
            "id",
            "url",
            "original_name",
            "size",
            "content_type",
            "kind",
            "caption",
            "sort_order",
            "uploaded_at",
        )

    def get_url(self, obj):
        try:
            return obj.file.url
        except Exception:
            return None


class ExamPostReadSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.username", read_only=True)
    attachments = AttachmentSerializer(many=True, read_only=True)
    content_html = serializers.SerializerMethodField()

    class Meta:
        model = ExamPost
        fields = (
            "id",
            "title",
            "content",
            "content_html",
            "author_name",
            "is_pinned",
            "status",
            "view_count",
            "published_at",
            "created_at",
            "updated_at",
            "attachments",
        )

    def get_content_html(self, obj):
        raw_html = obj.content or ""
        safe = cleaner.clean(raw_html)
        safe = bleach.linkify(safe, callbacks=[_link_target_blank])
        return safe


class ExamPostWriteSerializer(serializers.ModelSerializer):
    """
    - 관리자만 사용 (권한은 View에서 제어)
    - attachments: 여러 파일 업로드 가능
    - status: DRAFT/PUBLISHED (발행시 published_at 자동 세팅)
    """

    attachments = serializers.ListField(
        child=serializers.FileField(), write_only=True, required=False, allow_empty=True
    )

    class Meta:
        model = ExamPost
        fields = ("title", "content", "is_pinned", "status", "attachments")

    def create(self, validated_data):
        files = validated_data.pop("attachments", [])
        user = self.context["request"].user
        # 발행일 처리
        status_val = validated_data.get("status", ExamPost.Status.DRAFT)
        if status_val == ExamPost.Status.PUBLISHED:
            validated_data["published_at"] = timezone.now()

        post = ExamPost.objects.create(author=user, **validated_data)
        for f in files:
            Attachment.objects.create(post=post, file=f)
        return post

    def update(self, instance, validated_data):
        files = validated_data.pop("attachments", None)
        new_status = validated_data.get("status", instance.status)

        # 필드 갱신
        for k, v in validated_data.items():
            setattr(instance, k, v)

        # 발행 전환 시 발행일 세팅
        if new_status == ExamPost.Status.PUBLISHED and instance.published_at is None:
            instance.published_at = timezone.now()

        instance.save()

        # 첨부 추가(기존 유지)
        if files:
            for f in files:
                Attachment.objects.create(post=instance, file=f)

        return instance
