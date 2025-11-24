# apps/exam_board/tests/test_exam_board_api.py
import shutil
import tempfile
from datetime import timedelta
from typing import cast

from django.contrib.auth import get_user_model
from django.test import override_settings
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile

from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.response import Response as DRFResponse

from apps.exam_board.models import ExamPost, Attachment

User = get_user_model()


def uf(
    name: str, content: bytes = b"x", content_type: str = "application/octet-stream"
):
    """테스트용 업로드 파일 헬퍼"""
    return SimpleUploadedFile(name=name, content=content, content_type=content_type)


class BaseExamBoardTest(APITestCase):
    """
    외부 스토리지(NCP S3) 대신 테스트에서는 로컬 FileSystemStorage 사용.
    임시 MEDIA_ROOT로 격리.
    """

    client: APIClient  # IDE에게 DRF 클라이언트라고 명시

    def setUp(self):
        super().setUp()
        self.client = APIClient()

        # 임시 미디어 디렉터리
        self.tmp_media = tempfile.mkdtemp(prefix="test_media_")
        self._override = override_settings(
            DEFAULT_FILE_STORAGE="django.core.files.storage.FileSystemStorage",
            MEDIA_ROOT=self.tmp_media,
        )
        self._override.enable()

        # 관리자
        self.admin = User.objects.create_user(
            email="admin@example.com", password="pass1234", is_staff=True, name="관리자"
        )

        # URL
        self.base = "/api/exam-board"
        self.list_url = f"{self.base}/exam-posts/"
        self.upload_url = f"{self.base}/uploads/images/"

    def tearDown(self):
        self._override.disable()
        shutil.rmtree(self.tmp_media, ignore_errors=True)
        super().tearDown()

    # ---- 타입이 보장된 요청 헬퍼 (IDE 경고 제거) ----
    def req_get(self, url: str, **kwargs) -> DRFResponse:
        return cast(DRFResponse, self.client.get(url, **kwargs))

    def req_post(self, url: str, **kwargs) -> DRFResponse:
        return cast(DRFResponse, self.client.post(url, **kwargs))

    def req_patch(self, url: str, **kwargs) -> DRFResponse:
        return cast(DRFResponse, self.client.patch(url, **kwargs))

    def req_delete(self, url: str, **kwargs) -> DRFResponse:
        return cast(DRFResponse, self.client.delete(url, **kwargs))

    # ---- 공용 유틸 ----
    def j(self, res: DRFResponse):
        """DRF Response면 .data, 아니면 .json()으로 파싱"""
        return getattr(res, "data", None) or res.json()

    def as_admin(self):
        self.client.force_authenticate(user=self.admin)

    def as_anon(self):
        self.client.force_authenticate(user=None)

    # ---- Optional 방지용 헬퍼 ----
    def latest_post(self) -> ExamPost:
        obj = ExamPost.objects.order_by("-id").first()
        if obj is None:
            self.fail("latest_post(): ExamPost가 생성되지 않았습니다.")
        return cast(ExamPost, obj)

    def first_attachment(self, post_id: int) -> Attachment:
        obj = Attachment.objects.filter(post_id=post_id).first()
        if obj is None:
            self.fail("first_attachment(): Attachment가 생성되지 않았습니다.")
        return cast(Attachment, obj)


class ExamBoardAPITests(BaseExamBoardTest):

    # ───────── 목록/권한/상태 ─────────

    def test_list_anonymous_shows_published_only(self):
        ExamPost.objects.create(
            title="draft",
            content="<p>draft</p>",
            author=self.admin,
            status=ExamPost.Status.DRAFT,
        )
        ExamPost.objects.create(
            title="pub",
            content="<p>pub</p>",
            author=self.admin,
            status=ExamPost.Status.PUBLISHED,
            published_at=timezone.now(),
        )
        res = self.req_get(self.list_url)
        self.assertEqual(res.status_code, 200)
        data = self.j(res)
        self.assertEqual(data["total_count"], 1)
        self.assertEqual(data["results"][0]["title"], "pub")

    def test_list_admin_can_filter_status(self):
        ExamPost.objects.create(
            title="d1", content="x", author=self.admin, status=ExamPost.Status.DRAFT
        )
        ExamPost.objects.create(
            title="p1",
            content="x",
            author=self.admin,
            status=ExamPost.Status.PUBLISHED,
            published_at=timezone.now(),
        )

        self.as_admin()
        r_all = self.req_get(self.list_url)
        self.assertEqual(r_all.status_code, 200)
        self.assertEqual(self.j(r_all)["total_count"], 2)

        r_draft = self.req_get(self.list_url + "?status=DRAFT")
        self.assertEqual(self.j(r_draft)["total_count"], 1)
        self.assertEqual(self.j(r_draft)["results"][0]["status"], "DRAFT")

    # ───────── 생성/수정/발행/첨부 ─────────

    def test_create_post_admin_with_attachments(self):
        self.as_admin()
        res = self.req_post(
            self.list_url,
            data={
                "title": "시험 공지",
                "content": "<p>내용</p>",
                "status": "DRAFT",
                "attachments": [
                    uf("poster.jpg", b"img", "image/jpeg"),
                    uf("안내문.hwp", b"hwp", "application/octet-stream"),
                ],
            },
            format="multipart",
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED, self.j(res))
        post = self.latest_post()
        self.assertEqual(Attachment.objects.filter(post_id=post.pk).count(), 2)

    def test_create_post_anonymous_forbidden(self):
        self.as_anon()
        res = self.req_post(
            self.list_url, data={"title": "x", "content": "y"}, format="multipart"
        )
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_publish_sets_published_at(self):
        self.as_admin()
        r = self.req_post(
            self.list_url, data={"title": "d", "content": "<p>d</p>", "status": "DRAFT"}
        )
        self.assertEqual(r.status_code, 201)

        post = self.latest_post()
        post_id = int(post.pk)

        r2 = self.req_patch(
            f"{self.list_url}{post_id}/",
            data={"status": "PUBLISHED"},
            format="multipart",
        )
        self.assertEqual(r2.status_code, 200)
        post.refresh_from_db()
        self.assertEqual(post.status, ExamPost.Status.PUBLISHED)
        self.assertIsNotNone(post.published_at)

    def test_update_add_attachment(self):
        self.as_admin()
        r = self.req_post(
            self.list_url, data={"title": "t", "content": "c", "status": "DRAFT"}
        )
        self.assertEqual(r.status_code, 201)

        post = self.latest_post()
        post_id = int(post.pk)

        r2 = self.req_patch(
            f"{self.list_url}{post_id}/",
            data={"attachments": [uf("a.pdf", b"1", "application/pdf")]},
            format="multipart",
        )
        self.assertEqual(r2.status_code, 200)
        self.assertEqual(Attachment.objects.filter(post_id=post_id).count(), 1)

    # ───────── 상세/조회수 ─────────

    def test_retrieve_increments_view_count_only_for_published(self):
        pub = ExamPost.objects.create(
            title="p",
            content="c",
            author=self.admin,
            status=ExamPost.Status.PUBLISHED,
            published_at=timezone.now(),
        )
        draft = ExamPost.objects.create(
            title="d", content="c", author=self.admin, status=ExamPost.Status.DRAFT
        )

        r1 = self.req_get(f"{self.list_url}{pub.pk}/")
        self.assertEqual(r1.status_code, 200)
        pub.refresh_from_db()
        self.assertEqual(pub.view_count, 1)
        self.req_get(f"{self.list_url}{pub.pk}/")
        pub.refresh_from_db()
        self.assertEqual(pub.view_count, 2)

        r2 = self.req_get(f"{self.list_url}{draft.pk}/")
        self.assertEqual(r2.status_code, 404)

        self.as_admin()
        r3 = self.req_get(f"{self.list_url}{draft.pk}/")
        self.assertEqual(r3.status_code, 200)
        draft.refresh_from_db()
        self.assertEqual(draft.view_count, 0)

    # ───────── 검색/정렬/핀 ─────────

    def test_search_and_pinned_ordering(self):
        ExamPost.objects.create(
            title="가",
            content="aaa",
            author=self.admin,
            status=ExamPost.Status.PUBLISHED,
            published_at=timezone.now(),
        )
        p2 = ExamPost.objects.create(
            title="나 pinned",
            content="bbb",
            author=self.admin,
            status=ExamPost.Status.PUBLISHED,
            is_pinned=True,
            published_at=timezone.now(),
        )
        ExamPost.objects.create(
            title="다 latest",
            content="ccc",
            author=self.admin,
            status=ExamPost.Status.PUBLISHED,
            published_at=timezone.now(),
        )

        res = self.req_get(self.list_url)
        self.assertEqual(res.status_code, 200)
        ids = [row["id"] for row in self.j(res)["results"]]
        self.assertEqual(ids[0], p2.pk)

        res2 = self.req_get(self.list_url + "?search=latest")
        titles = [row["title"] for row in self.j(res2)["results"]]
        self.assertIn("다 latest", titles)

    # ───────── 페이지네이션 ─────────

    def test_pagination_structure_and_page_size(self):
        for i in range(3):
            ExamPost.objects.create(
                title=f"p{i}",
                content="c",
                author=self.admin,
                status=ExamPost.Status.PUBLISHED,
                published_at=timezone.now() - timedelta(minutes=i),
            )

        res = self.req_get(self.list_url + "?page=1&page_size=2")
        self.assertEqual(res.status_code, 200)
        data = self.j(res)
        self.assertIn("total_count", data)
        self.assertIn("total_pages", data)
        self.assertIn("current_page", data)
        self.assertIn("results", data)
        self.assertEqual(len(data["results"]), 2)
        self.assertEqual(data["total_count"], 3)

    # ───────── 첨부 조회/삭제 권한 ─────────

    def test_attachment_get_allowed_delete_admin_only(self):
        self.as_admin()
        r = self.req_post(
            self.list_url,
            data={"title": "t", "content": "c", "status": "PUBLISHED"},
            format="multipart",
        )
        self.assertEqual(r.status_code, 201)

        post = self.latest_post()
        post_id = int(post.pk)

        r2 = self.req_patch(
            f"{self.list_url}{post_id}/",
            data={"attachments": [uf("x.jpg", b"img", "image/jpeg")]},
            format="multipart",
        )
        self.assertEqual(r2.status_code, 200)
        att = self.first_attachment(post_id)
        att_id = int(att.pk)
        att_url = f"{self.base}/exam-attachments/{att_id}/"

        # 익명 GET 허용
        self.as_anon()
        g = self.req_get(att_url)
        self.assertEqual(g.status_code, 200)

        # 익명 삭제 금지 (일반 유저 시나리오 제거)
        d_forbid = self.req_delete(att_url)
        self.assertEqual(d_forbid.status_code, status.HTTP_401_UNAUTHORIZED)

        # 관리자 삭제 가능
        self.as_admin()
        d_ok = self.req_delete(att_url)
        self.assertEqual(d_ok.status_code, 204)
        self.assertFalse(Attachment.objects.filter(pk=att_id).exists())

    # ───────── 본문 정화 ─────────

    def test_content_html_sanitized(self):
        self.as_admin()
        dirty = (
            '<p>ok</p><script>alert(1)</script><a href="https://example.com">link</a>'
        )
        r = self.req_post(
            self.list_url,
            data={"title": "t", "content": dirty, "status": "PUBLISHED"},
            format="multipart",
        )
        self.assertEqual(r.status_code, 201)

        post = self.latest_post()
        detail = self.req_get(f"{self.list_url}{int(post.pk)}/")
        self.assertEqual(detail.status_code, 200)
        html = self.j(detail)["content_html"]
        self.assertIn("link", html)
        self.assertNotIn("<script>", html)

    # ───────── CKEditor 인라인 이미지 업로드 ─────────

    def test_richtext_image_upload_admin_only(self):
        self.as_anon()
        r_forbid = self.req_post(
            self.upload_url,
            data={"upload": uf("x.jpg", b"img", "image/jpeg")},
            format="multipart",
        )
        self.assertEqual(
            r_forbid.status_code, status.HTTP_401_UNAUTHORIZED
        )  # 403 → 401

        self.as_admin()
        r_ok = self.req_post(
            self.upload_url,
            data={"upload": uf("y.jpg", b"img", "image/jpeg")},
            format="multipart",
        )
        self.assertEqual(r_ok.status_code, 201, self.j(r_ok))
        self.assertIn("url", self.j(r_ok))
