# apps/exam_board/views.py
from django.db.models import F
from rest_framework import generics, status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.files.storage import default_storage
from django.utils.crypto import get_random_string
from datetime import datetime
import os

from .models import ExamPost, Attachment
from .serializers import (
    ExamPostReadSerializer,
    ExamPostWriteSerializer,
    AttachmentSerializer,
)
from utils.permissions import IsAdminOrReadOnly
from utils.pagination import CustomPageNumberPagination


class ExamPostListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdminOrReadOnly]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["title", "content"]
    ordering_fields = ["created_at", "view_count", "is_pinned", "published_at"]
    ordering = ["-is_pinned", "-created_at"]
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        qs = ExamPost.objects.select_related("author").prefetch_related("attachments")

        # 핀 고정 필터 (?is_pinned=true/false)
        is_pinned = (self.request.GET.get("is_pinned") or "").lower()
        if is_pinned in ("true", "false"):
            qs = qs.filter(is_pinned=(is_pinned == "true"))

        # 일반/비로그인 → 발행글만
        if not (self.request.user and self.request.user.is_staff):
            return qs.filter(status=ExamPost.Status.PUBLISHED)

        # 관리자 전용 상태 필터 (?status=DRAFT/PUBLISHED)
        status_param = (self.request.GET.get("status") or "").upper()
        if status_param in (ExamPost.Status.DRAFT, ExamPost.Status.PUBLISHED):
            return qs.filter(status=status_param)
        return qs

    def get_serializer_class(self):
        return (
            ExamPostWriteSerializer
            if self.request.method == "POST"
            else ExamPostReadSerializer
        )


class ExamPostDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminOrReadOnly]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        qs = ExamPost.objects.select_related("author").prefetch_related("attachments")
        if not (self.request.user and self.request.user.is_staff):
            return qs.filter(status=ExamPost.Status.PUBLISHED)
        return qs

    def get_serializer_class(self):
        # 조회는 Read, 수정/부분수정/생성계열은 Write
        if self.request.method in ("PUT", "PATCH"):
            return ExamPostWriteSerializer
        return ExamPostReadSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # 발행 글만 조회수 증가
        if instance.status == ExamPost.Status.PUBLISHED:
            ExamPost.objects.filter(pk=instance.pk).update(
                view_count=F("view_count") + 1
            )
            instance.view_count += 1  # 즉시 반영용
        serializer = ExamPostReadSerializer(instance)
        return Response(serializer.data)


class AttachmentRetrieveDestroyView(generics.RetrieveDestroyAPIView):
    """
    첨부 메타 조회(모두 허용), 삭제(관리자)
    """

    queryset = Attachment.objects.select_related("post")
    serializer_class = AttachmentSerializer
    permission_classes = [IsAdminOrReadOnly]


class RichTextImageUploadView(APIView):
    """
    CKEditor SimpleUpload용 인라인 이미지 업로드
    관리자만 허용
    """

    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]
    ALLOWED_EXTS = {"jpg", "jpeg", "png", "gif", "webp", "heic"}
    MAX_SIZE = 20 * 1024 * 1024  # 20MB

    def post(self, request, *args, **kwargs):
        f = (
            request.FILES.get("upload")
            or request.FILES.get("image")
            or request.FILES.get("file")
        )
        if not f:
            return Response(
                {"detail": "파일이 없습니다."}, status=status.HTTP_400_BAD_REQUEST
            )

        ext = os.path.splitext(f.name)[1].lower().lstrip(".")
        if ext not in self.ALLOWED_EXTS:
            return Response(
                {"detail": "이미지 형식만 허용합니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if f.size > self.MAX_SIZE:
            return Response(
                {"detail": "파일 용량이 초과되었습니다(최대 20MB)."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        today = datetime.now().strftime("%Y/%m/%d")
        filename = f"{get_random_string(16)}.{ext}"
        path = f"exam_board/editor_images/{today}/{filename}"
        saved = default_storage.save(path, f)
        url = default_storage.url(saved)

        # CKEditor SimpleUpload 응답 규격
        return Response({"url": url}, status=status.HTTP_201_CREATED)
