from rest_framework import generics, status
from rest_framework.response import Response
from .models import Lecture
from .serializers import LectureDisplaySerializer, LectureCreateUpdateSerializer
from utils.pagination import CustomPageNumberPagination
from utils.permissions import IsAdminOrReadOnly
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser


# ✅ 강의 목록 조회 (페이지네이션 포함)
class AcademyLectureListView(generics.ListAPIView):
    queryset = Lecture.objects.all().order_by("-created_at")
    serializer_class = LectureDisplaySerializer
    pagination_class = CustomPageNumberPagination


# ✅ 강의 상세 조회 / 수정 / 삭제
class AcademyLectureDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lecture.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = "id"

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return LectureCreateUpdateSerializer
        return LectureDisplaySerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"message": "강의가 성공적으로 삭제되었습니다."}, status=status.HTTP_200_OK
        )


# ✅ 강의 생성
class AcademyLectureCreateView(generics.CreateAPIView):
    queryset = Lecture.objects.all()
    serializer_class = LectureCreateUpdateSerializer
    permission_classes = [IsAdminOrReadOnly]
    parser_classes = [MultiPartParser, FormParser, JSONParser]  # ✅ 추가


# ✅ 강의 수정
class AcademyLectureUpdateView(generics.UpdateAPIView):
    queryset = Lecture.objects.all()
    serializer_class = LectureCreateUpdateSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = "id"
    parser_classes = [MultiPartParser, FormParser, JSONParser]  # ✅ 추가
