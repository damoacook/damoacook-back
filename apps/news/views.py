from django.db.models import F
from rest_framework import generics, filters
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from utils.permissions import IsAdminOrReadOnly
from utils.pagination import CustomPageNumberPagination
from .models import News
from .serializers import NewsSerializer


class NewsListCreateView(generics.ListCreateAPIView):
    queryset = News.objects.all()
    serializer_class = NewsSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = CustomPageNumberPagination
    parser_classes = [MultiPartParser, FormParser]

    # 검색·정렬 지원
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "content"]
    ordering_fields = ["created_at", "views"]
    ordering = ["-created_at"]


class NewsRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = News.objects.all()
    serializer_class = NewsSerializer
    lookup_field = "id"
    permission_classes = [IsAdminOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # 조회수 +1 (atomic)
        News.objects.filter(pk=instance.pk).update(views=F("views") + 1)
        instance.refresh_from_db(fields=["views"])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def perform_destroy(self, instance):
        # 레코드 삭제 전에 파일 먼저 제거
        if instance.image:
            instance.image.delete(save=False)
        return super().perform_destroy(instance)
