from django.urls import path
from .views import (
    CertificateListCreateView,
    CertificateRetrieveUpdateDestroyView,
    ExamScheduleListView,
)

urlpatterns = [
    # 자격증 소개: 제목·설명·이미지
    path('',          CertificateListCreateView.as_view(),         name='cert-list-create'),
    path('<int:id>/', CertificateRetrieveUpdateDestroyView.as_view(), name='cert-detail-update-delete'),
    # 시험일정: 공공데이터 API 결과만
    path('schedules/', ExamScheduleListView.as_view(),             name='cert-exam-schedules'),
]