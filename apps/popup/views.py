from rest_framework import generics
from rest_framework.parsers import MultiPartParser, FormParser
from utils.permissions import IsAdminOrReadOnly
from .models import PopupBanner
from .serializers import PopupBannerSerializer

class PopupBannerListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/popup/      → 배너 전체 리스트 조회 (Anyone)
    POST /api/popup/      → 새 배너 생성 (관리자만)
    """
    queryset           = PopupBanner.objects.all()
    serializer_class   = PopupBannerSerializer
    permission_classes = [IsAdminOrReadOnly]
    parser_classes     = [MultiPartParser, FormParser]

class PopupBannerRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/popup/{id}/   → 상세 조회 (Anyone)
    PUT    /api/popup/{id}/   → 수정 (관리자만)
    PATCH  /api/popup/{id}/   → 일부 수정 (관리자만)
    DELETE /api/popup/{id}/   → 삭제 (관리자만)
    """
    queryset           = PopupBanner.objects.all()
    serializer_class   = PopupBannerSerializer
    lookup_field       = 'id'
    permission_classes = [IsAdminOrReadOnly]
    parser_classes     = [MultiPartParser, FormParser]