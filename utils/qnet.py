import requests
from django.conf import settings

def fetch_exam_plans_from_qnet(jmcd, year):
    from django.conf import settings

    print(">>> 인증키:", settings.QNET_API_KEY)  # ✅ 출력 필수

    url = "https://apis.data.go.kr/B490007/qualExamSchd/getQualExamSchdList"
    params = {
        "serviceKey": settings.QNET_API_KEY,
        "implYy": year,
        "qualgbCd": "T",
        "jmCd": jmcd,
        "dataFormat": "json",
        "pageNo": 1,
        "numOfRows": 50,
    }

    response = requests.get(url, params=params, timeout=5)
    print(">>> 최종 요청 URL:", response.request.url)
    print(">>> 응답:", response.text)
