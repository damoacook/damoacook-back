# apps/exam_board/models.py
from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.utils.translation import gettext_lazy as _
import mimetypes

# (운영 기준) 허용 확장자: 이미지 + 일반 문서 + 한글(HWP/HWPX) + 압축
ALLOWED_EXTS = [
    # 이미지
    "jpg",
    "jpeg",
    "png",
    "gif",
    "webp",
    "heic",
    # 문서/스프레드시트/프레젠테이션/텍스트
    "pdf",
    "doc",
    "docx",
    "xls",
    "xlsx",
    "ppt",
    "pptx",
    "txt",
    # 압축
    "zip",
    # 한글 파일
    "hwp",
    "hwpx",
]

# 최대 업로드 용량(예: 20MB). 필요에 맞게 조정
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB


def exam_upload_to(instance, filename):
    """
    첨부 파일 업로드 경로.
    게시글별로 디렉토리를 구분: exam_board/<post_id>/<filename>
    """
    post_id = instance.post_id or (
        instance.post.pk if instance.post_id is None and instance.post else "tmp"
    )
    return f"exam_board/{post_id}/{filename}"


class ExamPost(models.Model):
    """
    시험정보 게시글.
    - content: CKEditor 등 리치텍스트 에디터의 HTML을 그대로 저장
    """

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "임시저장"
        PUBLISHED = "PUBLISHED", "발행"

    title = models.CharField("제목", max_length=200)
    content = models.TextField("본문(HTML)")  # 리치 텍스트 결과물(HTML) 저장
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="작성자",
        on_delete=models.PROTECT,
        related_name="exam_posts",
    )
    is_pinned = models.BooleanField("상단 고정", default=False)
    view_count = models.PositiveIntegerField("조회수", default=0)

    # ★ 임시저장/발행 관리
    status = models.CharField(
        "상태", max_length=10, choices=Status.choices, default=Status.DRAFT
    )
    published_at = models.DateTimeField("발행일", null=True, blank=True)

    created_at = models.DateTimeField("작성일", auto_now_add=True)
    updated_at = models.DateTimeField("수정일", auto_now=True)

    class Meta:
        verbose_name = "시험정보 게시글"
        verbose_name_plural = "시험정보 게시글"
        ordering = ("-is_pinned", "-created_at")  # 핀 고정 우선 + 최신 순
        indexes = [
            models.Index(fields=["status", "-created_at"]),
            models.Index(fields=["-is_pinned", "-created_at"]),
            models.Index(fields=["-created_at"]),
        ]

    def __str__(self):
        return f"[#{self.pk}] {self.title}"


class Attachment(models.Model):
    """
    첨부 파일(여러 개).
    - 이미지/문서/한글파일 등 모두 허용(화이트리스팅)
    - 저장 시 원본파일명/크기/콘텐츠타입 기록
    - kind: 이미지와 일반파일을 구분(프론트에서 썸네일/아이콘 처리 용이)
    """

    class Kind(models.TextChoices):
        IMAGE = "image", _("Image")
        FILE = "file", _("File")

    post = models.ForeignKey(
        ExamPost,
        verbose_name="게시글",
        on_delete=models.CASCADE,
        related_name="attachments",
    )
    file = models.FileField(
        "파일",
        upload_to=exam_upload_to,
        max_length=255,
        validators=[FileExtensionValidator(allowed_extensions=ALLOWED_EXTS)],
        help_text="이미지, 문서, HWP/HWPX, ZIP 등 허용",
    )
    # 표시/UX 개선용 메타정보
    kind = models.CharField(
        "종류", max_length=10, choices=Kind.choices, default=Kind.FILE
    )
    original_name = models.CharField("원본 파일명", max_length=255, blank=True)
    size = models.PositiveIntegerField("파일 크기(Byte)", default=0)
    content_type = models.CharField("콘텐츠 타입", max_length=100, blank=True)
    caption = models.CharField("설명(옵션)", max_length=255, blank=True)  # 필요 시 사용
    sort_order = models.PositiveIntegerField(
        "정렬순서(옵션)", default=0
    )  # 필요 시 사용
    uploaded_at = models.DateTimeField("업로드 일시", auto_now_add=True)

    class Meta:
        verbose_name = "첨부 파일"
        verbose_name_plural = "첨부 파일"
        ordering = ("sort_order", "id")
        indexes = [models.Index(fields=["post", "sort_order"])]

    def __str__(self):
        return self.original_name or (
            self.file.name if self.file else f"attachment#{self.pk}"
        )

    # ---- 유효성 검사/자동 채움 ----
    def clean(self):
        # 용량 제한
        if self.file and self.file.size > MAX_FILE_SIZE:
            raise ValidationError(
                {
                    "file": f"파일 용량을 초과했습니다(최대 {MAX_FILE_SIZE // (1024*1024)}MB)."
                }
            )

    def save(self, *args, **kwargs):
        """
        저장 시 메타정보 자동 채움 + kind 판별.
        """
        if self.file:
            # 원본 파일명/크기 기록
            if not self.original_name:
                self.original_name = getattr(self.file, "name", "") or ""
            self.size = getattr(self.file, "size", 0)

            # MIME 추정 (mimetypes는 확장자 기반이므로 100% 정확하진 않음)
            if not self.content_type:
                guessed = mimetypes.guess_type(self.original_name)[0]
                self.content_type = guessed or ""

            # 종류 자동 설정
            if self.content_type.startswith("image/"):
                self.kind = self.Kind.IMAGE
            else:
                self.kind = self.Kind.FILE

        # 유효성 검사 실행
        self.full_clean()
        super().save(*args, **kwargs)
