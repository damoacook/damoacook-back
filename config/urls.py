from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)
from django.views.static import serve as static_serve
import os


def healthz(_):
    return JsonResponse({"ok": True})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/admin/", include("apps.accounts.urls")),
    path("api/about/", include("apps.about.urls")),
    path("api/inquiries/", include("apps.inquiries.urls")),
    path("api/lectures/", include("apps.lectures.urls")),
    path("api/news/", include("apps.news.urls")),
    path("api/certificates/", include("apps.certificates.urls")),
    path("api/gallery/", include("apps.gallery.urls")),
    path("api/popup/", include("apps.popup.urls")),
    path("api/exam-board/", include("apps.exam_board.urls")),
    # OpenAPI 스키마 & 문서 ---
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("healthz", healthz),
]

# 개발 환경에서 media 파일 서빙
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# 운영에서도 임시로 media 서빙(환경변수로 on/off)
# if not settings.DEBUG and os.getenv("SERVE_MEDIA", "1") == "1":
#     urlpatterns += [
#         re_path(
#             r"^media/(?P<path>.*)$",
#             static_serve,
#             {"document_root": settings.MEDIA_ROOT, "show_indexes": False},
#         ),
#     ]
