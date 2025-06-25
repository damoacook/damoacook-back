from rest_framework import generics
from utils.permissions import IsAdminOrReadOnly
from .models import About
from .serializers import AboutSerializer

class AboutDetailView(generics.RetrieveUpdateAPIView):
    """
    GET    /api/about/       → 학원 소개 조회 (Anyone)
    PUT    /api/about/       → 학원 소개 수정 (Admin only)
    PATCH  /api/about/       → 일부 수정 (Admin only)
    """
    queryset           = About.objects.all()
    serializer_class   = AboutSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_object(self):
        # 최초 생성된 About 객체 하나만 사용
        return self.queryset.first()