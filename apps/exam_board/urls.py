# apps/exam_board/urls.py
from django.urls import path
from .views import (
    ExamPostListCreateView,
    ExamPostDetailView,
    AttachmentRetrieveDestroyView,
    RichTextImageUploadView,
)

urlpatterns = [
    path("exam-posts/", ExamPostListCreateView.as_view(), name="exam-post-list"),
    path("exam-posts/<int:pk>/", ExamPostDetailView.as_view(), name="exam-post-detail"),
    path(
        "exam-attachments/<int:pk>/",
        AttachmentRetrieveDestroyView.as_view(),
        name="exam-attachment-detail",
    ),
    path(
        "uploads/images/", RichTextImageUploadView.as_view(), name="exam-image-upload"
    ),
]
