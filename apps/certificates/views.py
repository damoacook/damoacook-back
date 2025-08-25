# certificates/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from datetime import datetime

from .models import Certificate, CertificateExamPlan
from .serializers import CertificateExamPlanSerializer
from utils.qnet import fetch_exam_plans_from_qnet  # 공공데이터 요청 함수

class CertificateExamPlanSyncView(APIView):
    """
    Q-Net 공공데이터 API를 통해 시험일정을 자동 저장하는 API
    GET /api/certificates/<slug>/sync-exam-plans/?year=2025
    """

    def get(self, request, slug):
        try:
            year = int(request.query_params.get('year', datetime.now().year))
        except ValueError:
            return Response({"error": "올바른 연도를 입력해주세요."}, status=status.HTTP_400_BAD_REQUEST)

        certificate = get_object_or_404(Certificate, slug=slug)

        try:
            save_exam_plans(slug, year)
            return Response({"message": f"{year}년도 시험일정이 성공적으로 저장되었습니다."})
        except Exception as e:
            return Response({"error": str(e)}, status=500)

def save_exam_plans(slug, year):
    cert = Certificate.objects.get(slug=slug)
    items = fetch_exam_plans_from_qnet(cert.jmcd, year)

    for item in items:
        CertificateExamPlan.objects.update_or_create(
            certificate=cert,
            impl_yy=int(item['implYy']),
            impl_seq=int(item['implSeq']),
            defaults={
                'qualgb_cd': item['qualgbCd'],
                'qualgb_nm': item['qualgbNm'],
                'description': item.get('description', ''),
                'doc_reg_start_dt': item['docRegStartDt'],
                'doc_reg_end_dt': item['docRegEndDt'],
                'doc_exam_start_dt': item['docExamStartDt'],
                'doc_exam_end_dt': item['docExamEndDt'],
                'doc_pass_dt': item['docPassDt'],
                'prac_reg_start_dt': item['pracRegStartDt'],
                'prac_reg_end_dt': item['pracRegEndDt'],
                'prac_exam_start_dt': item['pracExamStartDt'],
                'prac_exam_end_dt': item['pracExamEndDt'],
                'prac_pass_dt': item['pracPassDt'],
            }
        )
