import os, requests, xmltodict, time
from datetime import datetime
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from utils.pagination import CustomPageNumberPagination

HRD_API_KEY = os.getenv("HRD_API_KEY")
HRD_TORG_ID = os.getenv("HRD_TORG_ID")


class HRDLectureListView(APIView):
    """고용24 연동 강의 목록 조회 (다모아요리학원 전용)"""

    CACHE_KEY = "hrd:list:2025:damoa"
    CACHE_TTL = 600  # 10분

    def get(self, request):
        API_URL = (
            "https://www.work24.go.kr/cm/openApi/call/hr/callOpenApiSvcInfo310L01.do"
        )
        today = datetime.today().date()
        params = {
            "authKey": HRD_API_KEY,
            "returnType": "XML",
            "outType": "2",
            "pageNum": 1,
            "pageSize": 100,
            "srchTraStDt": "20250101",
            "srchTraEndDt": "20251231",
            "srchTraOrganNm": "다모아요리학원",
            "sort": "DESC",
            "sortCol": 2,
        }

        t0 = time.perf_counter()
        cached = cache.get(self.CACHE_KEY)

        try:
            resp = requests.get(API_URL, params=params, timeout=3)
            resp.raise_for_status()
            data = xmltodict.parse(resp.text)
            items = data.get("HRDNet", {}).get("srchList", {}).get("scn_list", [])
            if isinstance(items, dict):
                items = [items]
        except Exception as e:
            # 네트워크/파싱 실패 → 스냅샷 폴백
            if cached:
                resp = Response(cached, status=status.HTTP_200_OK)
                resp["X-Cache"] = "HIT-FALLBACK"
                resp["X-Elapsed-ms"] = f"{(time.perf_counter()-t0)*1000:.1f}"
                return resp
            return Response(
                {"error": f"목록 조회 실패: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        items = data.get("HRDNet", {}).get("srchList", {}).get("scn_list", [])
        if isinstance(items, dict):
            items = [items]

        lectures = []
        for item in items:
            # 날짜 파싱/필터
            try:
                start_str = item.get("traStartDate")
                end_str = item.get("traEndDate")
                if not start_str or not end_str:
                    continue
                start = datetime.strptime(start_str, "%Y-%m-%d").date()
                end = datetime.strptime(end_str, "%Y-%m-%d").date()
            except Exception:
                continue
            if end < today:
                continue

            # 인원/상태
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

            # torg_id 멀티키 추출(누락 방지)
            torg_id = (
                item.get("trainstCstmrId")
                or item.get("trainstCstmrID")
                or item.get("torgId")
                or item.get("TorgId")
                or item.get("torgID")
                or item.get("insttOrgNo")
                or item.get("trainstId")
                or HRD_TORG_ID
            )

            lectures.append(
                {
                    "title": item.get("title"),
                    "process_id": item.get("trprId"),
                    "process_time": item.get("trprDegr"),
                    "torg_id": torg_id,
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
                }
            )

        paginator = CustomPageNumberPagination()
        page = paginator.paginate_queryset(lectures, request)
        response = paginator.get_paginated_response(page)

        # ▲ 성공 시 스냅샷 저장
        cache.set(self.CACHE_KEY, response.data, self.CACHE_TTL)
        response["X-Cache"] = "MISS" if not cached else "REFRESH"
        response["X-Elapsed-ms"] = f"{(time.perf_counter()-t0)*1000:.1f}"
        return response


class HRDLectureDetailView(APIView):
    """고용24 연동 강의 상세 조회
    - torg_id 없으면 310L01로 '기관ID' 역조회 후 310L03 호출
    """

    CACHE_TTL = 1800

    def _lookup_torg_id(self, trpr_id: str, tracse: str) -> str | None:
        """310L01 목록에서 trprId + trprDegr 로 기관ID(trainstCstmrId) 찾기 (여러 페이지 탐색)"""
        API_URL = (
            "https://www.work24.go.kr/cm/openApi/call/hr/callOpenApiSvcInfo310L01.do"
        )

        # 날짜 필터 없이 trprId만으로 검색: 과거/미래 포함 전부에서 찾게
        for page in range(1, 11):  # 최대 10페이지(필요시 늘리세요)
            params = {
                "authKey": HRD_API_KEY,
                "returnType": "XML",
                "outType": "2",
                "pageNum": page,
                "pageSize": 100,
                "srchTrprId": trpr_id,
            }
            try:
                resp = requests.get(API_URL, params=params, timeout=10)
                resp.raise_for_status()
                data = xmltodict.parse(resp.text)
            except Exception:
                # 네트워크/파싱 에러시 다음 페이지 시도
                continue

            items = data.get("HRDNet", {}).get("srchList", {}).get("scn_list", [])
            if not items:
                # 더 이상 결과 없음
                return None
            if isinstance(items, dict):
                items = [items]

            for it in items:
                if str(it.get("trprDegr")) == str(tracse):
                    # 가능한 모든 키에서 기관ID 시도
                    cand = (
                        it.get("trainstCstmrId")
                        or it.get("trainstCstmrID")
                        or it.get("torgId")
                        or it.get("TorgId")
                        or it.get("torgID")
                        or it.get("insttOrgNo")
                        or it.get("trainstId")
                    )
                    if cand:
                        return str(cand)

        return None

    def get(self, request, trpr_id: str):
        tracse = request.query_params.get("tracse_tme")
        torg = request.query_params.get("torg_id")

        cache_key = f"hrd:detail:{trpr_id}:{tracse}:{torg}"
        t0 = time.perf_counter()
        hit = cache.get(cache_key)
        if hit:
            resp = Response(hit, status=200)
            resp["X-Cache"] = "HIT"
            resp["X-Elapsed-ms"] = f"{(time.perf_counter()-t0)*1000:.1f}"
            return resp

        if not tracse:
            return Response(
                {"error": "`tracse_tme`(회차)가 필요합니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 쿼리에 torg_id가 없으면 고정값으로 대입
        if not torg:
            torg = HRD_TORG_ID

        if not torg:
            # (혹시 폴백도 비어있으면 에러)
            return Response({"error": "기관ID(torg_id)가 필요합니다."}, status=400)

        # === 310L03 상세 호출 ===
        API_URL = (
            "https://www.work24.go.kr/cm/openApi/call/hr/callOpenApiSvcInfo310L03.do"
        )
        params = {
            "authKey": HRD_API_KEY,
            "returnType": "XML",
            "outType": "2",
            "srchTrprId": trpr_id,
            "srchTrprDegr": tracse,
            "srchTorgId": torg,
        }
        try:
            resp = requests.get(API_URL, params=params, timeout=10)
            resp.raise_for_status()
            data = xmltodict.parse(resp.text)
        except Exception as e:
            return Response(
                {"error": f"상세 조회 실패: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        scn_list = data.get("HRDNet", {}).get("scn_list")
        detail = scn_list[0] if isinstance(scn_list, list) else (scn_list or {})

        # 필드 파싱/상태 계산
        start_raw = detail.get("trStaDt")
        end_raw = detail.get("trEndDt")
        try:
            start = (
                datetime.strptime(start_raw, "%Y-%m-%d").date() if start_raw else None
            )
            end = datetime.strptime(end_raw, "%Y-%m-%d").date() if end_raw else None
        except Exception:
            start = end = None

        capacity = int(detail.get("totFxnum") or 0)
        applied = int(detail.get("totTrpCnt") or 0)
        remaining = max(capacity - applied, 0)

        today = datetime.today().date()
        is_full = applied >= capacity
        is_ongoing = bool(start and end and start <= today <= end)
        is_expired = bool(end and end < today)

        if is_expired:
            status_label, d_day = "종료", "종료"
        elif is_ongoing:
            status_label, d_day = "진행중", "진행중"
        elif is_full:
            status_label = "모집 마감"
            d_day = f"D-{(start - today).days}" if start else "D-DAY"
        else:
            status_label = "모집중" if start else "정보 없음"
            d_day = f"D-{(start - today).days}" if start else "미정"

        result = {
            "course_id": trpr_id,
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
                "https://www.work24.go.kr/hr/a/a/3100/selectTracseDetl.do"
                f"?tracseId={trpr_id}&tracseTme={tracse}"
                f"&crseTracseSe={detail.get('trainTargetCd')}"
                f"&trainstCstmrId={torg}"
            ),
        }
        return Response(result, status=status.HTTP_200_OK)
