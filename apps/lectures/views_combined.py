import os
import requests
import xmltodict
from datetime import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Lecture
from .serializers import LectureDisplaySerializer
from utils.pagination import CustomPageNumberPagination

HRD_API_KEY = os.getenv("HRD_API_KEY")


class CombinedLectureListView(APIView):
    """자체 강의 + HRD 강의 전체 목록 조회"""

    def get(self, request):
        today = datetime.today().date()

        # 1. 내부 강의 (DB)
        academy_queryset = Lecture.objects.all().order_by("-created_at")
        academy_serialized = LectureDisplaySerializer(academy_queryset, many=True).data

        # 2. 외부 HRD 강의
        hrd_lectures = []
        API_URL = (
            "https://www.work24.go.kr/cm/openApi/call/hr/callOpenApiSvcInfo310L01.do"
        )
        params = {
            "authKey": HRD_API_KEY,
            "returnType": "XML",
            "outType": "1",
            "pageNum": 1,
            "pageSize": 100,
            "srchTraStDt": "20250101",
            "srchTraEndDt": "20251231",
            "srchTraOrganNm": "다모아요리학원",
            "sort": "DESC",
            "sortCol": 2,
        }

        try:
            resp = requests.get(API_URL, params=params)
            resp.raise_for_status()
            data = xmltodict.parse(resp.text)
            items = data.get("HRDNet", {}).get("srchList", {}).get("scn_list", [])
            if isinstance(items, dict):
                items = [items]

            for item in items:
                start_str = item.get("traStartDate")
                end_str = item.get("traEndDate")
                if not start_str or not end_str:
                    continue

                start = datetime.strptime(start_str, "%Y-%m-%d").date()
                end = datetime.strptime(end_str, "%Y-%m-%d").date()
                if end < today:
                    continue

                capacity = int(item.get("yardMan") or 0)
                applied = int(item.get("regCourseMan") or 0)
                remaining = max(capacity - applied, 0)

                is_full = applied >= capacity
                is_ongoing = start <= today <= end
                status_label = (
                    "모집 마감" if is_full else ("진행중" if is_ongoing else "모집중")
                )
                d_day = (
                    "진행중"
                    if is_ongoing
                    else (f"D-{(start - today).days}" if start > today else "D-DAY")
                )

                hrd_lectures.append(
                    {
                        "title": item.get("title"),
                        "start_date": start_str,
                        "end_date": end_str,
                        "capacity": capacity,
                        "applied": applied,
                        "remain": remaining,
                        "status_label": status_label,
                        "d_day": d_day,
                        "day_of_week": None,  # 자체 강의와 구분 위해 None
                        "id": None,  # 자체 강의만 ID 있음
                    }
                )

        except Exception as e:
            return Response(
                {"error": f"HRD 강의 불러오기 실패: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # 3. 병합 + 정렬 + 페이지네이션
        academy_serialized = list(
            LectureDisplaySerializer(academy_queryset, many=True).data
        )
        merged = academy_serialized + hrd_lectures
        merged_sorted = sorted(
            merged, key=lambda x: x.get("start_date") or "", reverse=True
        )

        paginator = CustomPageNumberPagination()
        page = paginator.paginate_queryset(merged_sorted, request)
        return paginator.get_paginated_response(page)
