import requests
from xml.etree import ElementTree as ET

url = "http://openapi.q-net.or.kr/api/service/rest/InquiryTestDatesNationalProfessionalQualificationSVC/getList"
params = {
    "serviceKey": "iN/MiNSfdhs9q9tT5JcJw/TJ3pLmRX8w6ncWhPgd96ju9eBWuKA/dm+LVOYzwIcXBv8SJ5Vkwe452qnKmOZiQA==",
    "seriesCd": "DA"
}

try:
    response = requests.get(url, params=params, timeout=10)
    print("✅ 응답 상태코드:", response.status_code)
    root = ET.fromstring(response.content)

    items = root.findall(".//item")
    if not items:
        print("🔍 조리기능장 일정 없음")
    else:
        print(f"🔍 {len(items)}개 일정 발견")
        for item in items:
            print("회차:", item.findtext("description"))
            print("원서접수:", item.findtext("examregstartdt"), "~", item.findtext("examregenddt"))
            print("시험:", item.findtext("examstartdt"), "~", item.findtext("examenddt"))
            print("발표:", item.findtext("passstartdt"), "~", item.findtext("passenddt"))
            print("---")

except Exception as e:
    print("❌ 예외 발생:", e)
