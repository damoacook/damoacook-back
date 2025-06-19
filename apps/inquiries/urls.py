from django.urls import path
from .views import InquiryCreateView, AdminInquiryListView

urlpatterns = [
    # 사용자: 수강문의 등록
    path('', InquiryCreateView.as_view(), name='inquiry-create'),
    # 관리자: 수강문의 리스트 조회
    path('admin/', AdminInquiryListView.as_view(), name='admin-inquiry-list'),
]