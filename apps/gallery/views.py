from django.db.models import F
from rest_framework import generics, filters
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from utils.permissions import IsAdminOrReadOnly
from utils.pagination import CustomPageNumberPagination
from .models import GalleryImage
from .serializers import GalleryImageSerializer

class GalleryListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/gallery/        → 전체 리스트 (검색/정렬/페이지네이션 지원)
    POST /api/gallery/        → 관리자만 이미지 업로드
    """
    queryset           = GalleryImage.objects.all()
    serializer_class   = GalleryImageSerializer
    permission_classes = [IsAdminOrReadOnly]
    parser_classes     = [MultiPartParser, FormParser]
    pagination_class   = CustomPageNumberPagination
    filter_backends    = [filters.SearchFilter, filters.OrderingFilter]
    search_fields      = ['title', 'description']
    ordering_fields    = ['uploaded_at', 'views']
    ordering           = ['-uploaded_at']


class GalleryRetrieveDestroyView(generics.RetrieveDestroyAPIView):
    """
    GET    /api/gallery/{id}/  → 상세 조회 (조회수 +1)
    DELETE /api/gallery/{id}/  → 관리자만 삭제
    """
    queryset           = GalleryImage.objects.all()
    serializer_class   = GalleryImageSerializer
    lookup_field       = 'id'
    permission_classes = [IsAdminOrReadOnly]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # 조회수 atomic 증가
        GalleryImage.objects.filter(pk=instance.pk).update(views=F('views') + 1)
        instance.refresh_from_db(fields=['views'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
