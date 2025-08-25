from django.urls import path
from .views import CertificateExamPlanSyncView

urlpatterns = [
    path('certificates/<slug:slug>/sync-exam-plans/', CertificateExamPlanSyncView.as_view()),
]