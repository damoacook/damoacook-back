from rest_framework import generics, filters
from rest_framework.parsers import MultiPartParser, FormParser
from utils.permissions import IsAdminOrReadOnly
from utils.pagination import CustomPageNumberPagination
from .models import PopupBanner
from .serializers import PopupBannerSerializer


class PopupBannerListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/popup/      → 배너 리스트 (Anyone)
    POST /api/popup/      → 생성 (관리자)
    """

    queryset = PopupBanner.objects.all()
    serializer_class = PopupBannerSerializer
    permission_classes = [IsAdminOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]

    # 페이지네이션이 필요 없으면 주석 해제 (배열로 응답)
    # pagination_class   = None

    # ✅ 반드시 넣어줍니다(500 방지)
    ordering = ("-created_at",)

    def get_queryset(self):
        qs = super().get_queryset()
        active_only = self.request.query_params.get("active_only")
        if active_only in ("1", "true", "True", "yes"):
            qs = qs.filter(is_active=True)
        # ✅ 안전하게 고정 필드로 정렬
        return qs.order_by(*self.ordering)


class PopupBannerRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/popup/{id}/
    PUT    /api/popup/{id}/
    PATCH  /api/popup/{id}/
    DELETE /api/popup/{id}/
    """

    queryset = PopupBanner.objects.all()
    serializer_class = PopupBannerSerializer
    lookup_field = "id"
    permission_classes = [IsAdminOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]
