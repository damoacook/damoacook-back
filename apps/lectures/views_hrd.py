import os
import requests
import xmltodict
from datetime import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from utils.pagination import CustomPageNumberPagination

HRD_API_KEY = os.getenv("HRD_API_KEY")

class HRDLectureListView(APIView):
    """고용24 연동 강의 목록 조회 (다모아요리학원 전용)"""
    def get(self, request):
        API_URL = "https://www.work24.go.kr/cm/openApi/call/hr/callOpenApiSvcInfo310L01.do"
        today = datetime.today().date()
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
        except Exception as e:
            return Response({"error": f"목록 조회 실패: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        items = data.get("HRDNet", {}).get("srchList", {}).get("scn_list", [])
        if isinstance(items, dict):
            items = [items]

        lectures = []
        for item in items:
            try:
                start = datetime.strptime(item.get("traStartDate"), "%Y-%m-%d").date()
                end = datetime.strptime(item.get("traEndDate"), "%Y-%m-%d").date()
            except:
                continue
            if end < today:
                continue

            capacity = int(item.get("yardMan") or 0)
            applied = int(item.get("regCourseMan") or 0)
            remaining = max(capacity - applied, 0)

            is_full = applied >= capacity
            is_ongoing = start <= today <= end
            status_label = "모집 마감" if is_full else ("진행중" if is_ongoing else "모집중")
            d_day = "진행중" if is_ongoing else (f"D-{(start - today).days}" if start > today else "D-DAY")

            lectures.append({
                "title": item.get("title"),
                "process_id": item.get("trprId"),
                "process_time": item.get("trprDegr"),
                "torg_id": item.get("trainstCstmrId"),
                "crse_tracse_se": item.get("trainTargetCd"),
                "start_date": item.get("traStartDate"),
                "end_date": item.get("traEndDate"),
                "location": item.get("address"),
                "summary": item.get("contents"),
                "tel": item.get("telNo"),
                "satisfaction": item.get("stdgScor"),
                "capacity": capacity,
                "applied": applied,
                "remaining_slots": remaining,
                "status_label": status_label,
                "d_day": d_day,
                "is_closed": is_full or end < today,
            })

        paginator = CustomPageNumberPagination()
        page = paginator.paginate_queryset(lectures, request)
        return paginator.get_paginated_response(page)

class HRDLectureDetailView(APIView):
    """고용24 연동 강의 상세 조회 (310L03)"""
    def get(self, request, trpr_id):
        # 세션 회차와 기관 ID를 반드시 전달
        tracse = request.query_params.get("tracse_tme")
        torg = request.query_params.get("torg_id")
        if not tracse or not torg:
            return Response(
                {"error": "쿼리 파라미터 `tracse_tme`(회차)와 `torg_id`(기관ID)를 모두 전달해주세요."},
                status=status.HTTP_400_BAD_REQUEST
            )

        API_URL = "https://www.work24.go.kr/cm/openApi/call/hr/callOpenApiSvcInfo310L03.do"
        params = {
            "authKey": HRD_API_KEY,
            "returnType": "XML",
            "outType": "2",
            "srchTrprId": trpr_id,
            "srchTrprDegr": tracse,
            "srchTorgId": torg,
        }
        try:
            resp = requests.get(API_URL, params=params)
            resp.raise_for_status()
            data = xmltodict.parse(resp.text)
        except Exception as e:
            return Response({"error": f"상세 조회 실패: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        scn_list = data.get("HRDNet", {}).get("scn_list")
        detail = scn_list[0] if isinstance(scn_list, list) else scn_list

        # 필드 파싱
        start_raw = detail.get("trStaDt")
        end_raw   = detail.get("trEndDt")
        try:
            start = datetime.strptime(start_raw, "%Y-%m-%d").date() if start_raw else None
            end   = datetime.strptime(end_raw, "%Y-%m-%d").date() if end_raw else None
        except:
            start = end = None

        capacity = int(detail.get("totFxnum") or 0)
        applied  = int(detail.get("totTrpCnt") or 0)
        remaining = max(capacity - applied, 0)

        now = datetime.today().date()
        is_full    = applied >= capacity
        is_ongoing = start and end and start <= now <= end
        is_expired = end and end < now

        if is_expired:
            status_label, d_day = "종료", "종료"
        elif is_ongoing:
            status_label, d_day = "진행중", "진행중"
        elif is_full:
            status_label = "모집 마감"
            d_day = f"D-{(start - now).days}" if start else "D-DAY"
        else:
            status_label = "모집중" if start else "정보 없음"
            d_day = f"D-{(start - now).days}" if start else "미정"

        result = {
            "course_id": detail.get("trprId"),
            "course_name": detail.get("trprNm"),
            "start_date": start_raw or "미정",
            "end_date": end_raw or "미정",
            "capacity": capacity,
            "applied": applied,
            "remaining_slots": remaining,
            "graduates": detail.get("finiCnt"),
            "fee": detail.get("totTrco"),
            "empl_rate_6m": detail.get("eiEmplRate6"),
            "non_insured_rate": detail.get("hrdEmplRate6"),
            "status_label": status_label,
            "d_day": d_day,
            "is_closed": is_expired or is_full,
            "registration_url": (
                f"https://www.work24.go.kr/hr/a/a/3100/selectTracseDetl.do"
                f"?tracseId={trpr_id}&tracseTme={tracse}&crseTracseSe={detail.get('trainTargetCd')}&trainstCstmrId={torg}"
            )
        }
        return Response(result, status=status.HTTP_200_OK)
