import requests
from django.conf import settings
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from utils.permissions import IsAdminOrReadOnly
from utils.pagination import CustomPageNumberPagination
from .models import Certificate
from .serializers import CertificateSerializer

class CertificateListCreateView(generics.ListCreateAPIView):
    queryset = Certificate.objects.all()
    serializer_class = CertificateSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = CustomPageNumberPagination

class CertificateRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Certificate.objects.all()
    serializer_class = CertificateSerializer
    lookup_field = 'id'
    permission_classes = [IsAdminOrReadOnly]

class ExamScheduleListView(APIView):
    """
    GET /api/certificates/schedules/?implYy=2025&jmCd=7910&qualgbCd=T
    """
    def get(self, request):
        implYy   = request.query_params.get('implYy')
        jmCd     = request.query_params.get('jmCd')
        qualgbCd = request.query_params.get('qualgbCd', 'T')

        if not implYy or not jmCd:
            return Response(
                {"error": "implYy(시행년도)와 jmCd(종목코드)를 모두 전달해주세요."},
                status=status.HTTP_400_BAD_REQUEST
            )

        params = {
            "serviceKey": settings.PUBLIC_API_KEY,
            "numOfRows": 100,
            "pageNo": 1,
            "dataFormat": "json",
            "implYy": implYy,
            "qualgbCd": qualgbCd,
            "jmCd": jmCd,
        }
        resp = requests.get(
            "http://apis.data.go.kr/B490007/qualExamSchd/getQualExamSchdList",
            params=params
        )
        if resp.status_code != 200:
            return Response({"error": "외부 API 호출 실패"}, status=status.HTTP_502_BAD_GATEWAY)

        body = resp.json().get('response', {}).get('body', {})
        items = body.get('items', {}).get('item', [])
        return Response(items, status=status.HTTP_200_OK)