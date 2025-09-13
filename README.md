# 다모아요리학원 Backend (Django + DRF)

![Damoa Cook Academy Logo](./assets/다모아아로고.jpg)

[![Website](https://img.shields.io/badge/website-live-2ea44f)](https://damoacook.com)
![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB)
![Django](https://img.shields.io/badge/Django-5.x-092E20)
![DRF](https://img.shields.io/badge/DRF-REST_API-bd2c00)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14%2B-336791)
![Docs](https://img.shields.io/badge/Swagger%2FRedoc-OpenAPI3-009485)
![Deploy](https://img.shields.io/badge/Render-Gunicorn-46E3B7)

> 다모아요리학원 **백엔드**는 Django + DRF 기반의 REST API입니다.  
> 강의·공지·갤러리·수강문의 도메인과 **HRD-Net(Work24) 연동**, **SMTP 알림**, **S3 미디어 저장**을 제공합니다.

---

## 목차
- [프로젝트 개요 & 선정 이유](#프로젝트-개요--선정-이유)
- [개발 인원/기간](#개발-인원기간)
- [배포 & 아키텍처](#배포--아키텍처)
- [기술 스택](#기술-스택)
- [설치 & 실행(로컬)](#설치--실행로컬)
- [API 요약](#api-요약)
- [트러블슈팅](#트러블슈팅)
- [측정 재현 방법](#측정-재현-방법)
- [운영/보안 체크리스트](#운영보안-체크리스트)
- [라이선스](#라이선스)

---

## 프로젝트 개요 & 선정 이유
- **목표**: 학원 소개/강의/자격증/공지·갤러리/수강문의를 **단일 도메인**에서 안정적으로 제공
- **선정 이유(백엔드 관점)**
  - **Django + DRF**: 모델·시리얼라이저·권한/페이지네이션 표준화 → 운영 효율↑, 유지보수 비용↓
  - **경로 라우팅(`/api/*`)**: Vercel → Render **rewrite**로 **CORS/쿠키/CSRF** 단순화
  - **S3(네이버 오브젝트 스토리지)**: Render 컨테이너 FS 휘발성 → 업로드 영속화
  - **SimpleJWT**: 운영자 API 최소 권한·만료 통제에 적합
  - **drf-spectacular**: OpenAPI 3 자동 문서화로 팀/외부 협업 생산성↑

---

## 개발 인원/기간
- **개발**: 1인(백엔드 중심, FE/인프라 포함)  
- **기간**: 2025.06 ~ 2025.09

---

## 배포 & 아키텍처
![Damoa Architecture](./assets/damoacook(1).png)

- **단일 도메인 + 경로 라우팅**: `https://damoacook.com/api/*` → (Vercel) **rewrite** → (Render) 백엔드  
  - **장점**: SEO/쿠키/CSRF/추적 스니펫 관리 단순, CORS 이슈 최소화
- **FE/BE 분리 배포**: 정적은 Vercel(에지 캐시), 동적은 Render(Gunicorn) → 장애/배포 영향 범위 분리
- **S3 호환 스토리지**: 미디어 영속화
- **외부 연동**: HRD-Net(Work24 OpenAPI), Naver SMTP
- **헬스체크**: `GET /healthz` (가벼운 OK 응답)

---

## 기술 스택
- **Backend**: Django, Django REST Framework, SimpleJWT  
- **DB/Infra**: PostgreSQL, Render(Gunicorn), Naver Object Storage(S3), WhiteNoise(정적 해시)  
- **문서화**: drf-spectacular(+ sidecar) → Swagger/Redoc(OpenAPI 3)  

---

## 설치 & 실행(로컬)
> 비밀값은 **환경변수**로 주입합니다(README에 값 공개 X).  
> 개발 중 메일은 콘솔 백엔드로 대체해 흐름만 검증할 수 있습니다.

```bash
git clone <REPO_URL> damoa-backend
cd damoa-backend

# 가상환경 & 의존성
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows PowerShell: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# (로컬) 환경변수 예시
# macOS/Linux
export DATABASE_URL="postgresql://USER:PASS@HOST:5432/DBNAME"
export EMAIL_BACKEND="django.core.mail.backends.console.EmailBackend"
# Windows PowerShell
# $env:DATABASE_URL="postgresql://USER:PASS@HOST:5432/DBNAME"
# $env:EMAIL_BACKEND="django.core.mail.backends.console.EmailBackend"

# 마이그레이션 & 실행
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
# Swagger: http://localhost:8000/api/docs/
# Redoc  : http://localhost:8000/api/redoc/
```

## API 요약

### 공개 API는 인증 없이 접근, 운영자용 엔드포인트는 JWT 필요.

### 1) 강의(내부·학원)

```
GET /api/lectures/?status=active&page=1&page_size=12
응답(요약):

{
  "count": 42,
  "next": "...",
  "previous": null,
  "results": [
    {
      "id": 101,
      "title": "한식 기능사 실기",
      "status": "active",
      "start_date": "2025-09-15",
      "thumbnail": "https://.../thumb.jpg"
    }
  ]
}


GET /api/lectures/{id}/
응답(요약):

{
  "id": 101,
  "title": "한식 기능사 실기",
  "description": "...",
  "curriculum": ["만두소 다듬기", "완자전"],
  "status": "active",
  "images": ["https://.../1.jpg","https://.../2.jpg"]
}
```

### 2) HRD-Net 강의(연동)
```
GET /api/hrd-lectures/?q=한식&region=서울&page=1
외부 데이터(HRD-Net) 연동 결과를 페이지네이션하여 제공

3) 공지/갤러리

GET /api/news/ · GET /api/news/{id}/

GET /api/gallery/ · GET /api/gallery/{id}/
```
### 4) 수강문의(무로그인)
```
POST /api/inquiries/
요청:

{ "name":"홍길동", "phone":"010-1234-5678", "message":"한식 기능사 과정 문의합니다." }

```

## 트러블슈팅
### 1) 201인데 수강문의 메일 미수신
- 증상: POST /api/inquiries/ 201(저장 성공)이나 메일이 오지 않음
- 원인:
Naver SMTP 정책: From ≠ 로그인 계정 시 차단
DEFAULT_FROM_EMAIL 따옴표 포함 등 헤더 포맷 오류
TLS/포트 불일치, 애플리케이션에서 오류가 묵살되던 점
- 조치:
EMAIL_USE_TLS=True, EMAIL_PORT=587, From = EMAIL_HOST_USER 일치
DEFAULT_FROM_EMAIL을 다모아요리학원 <id@naver.com> 형태로 교정
수신자 INQUIRY_TO_EMAILS(복수) 구성, 개발은 콘솔 메일 백엔드로 검증
- 결과: 동일 테스트 데이터로 실제 SMTP 수신 확인(201 응답 ↔ 수신 이벤트 일치)

### 2) Vercel 프리뷰에서 CORS/CSRF 프리플라이트 실패

- 증상: 프리뷰 URL에서 OPTIONS 403 → 후속 GET/POST 차단
- 원인: CORS 허용 목록/정규식, CSRF Trusted Origins에 프리뷰 도메인 누락
- 조치:
CORS_ALLOWED_ORIGIN_REGEXES에 ^https://.*\.vercel\.app$ 추가
CSRF_TRUSTED_ORIGINS에 운영/프리뷰 도메인 와일드카드 반영
SECURE_PROXY_SSL_HEADER=("HTTP_X_FORWARDED_PROTO","https") 확인
- 결과: 프리뷰 배포에서도 폼 제출/업로드 정상

### 3) HRD-Net 목록 호출 콜드 스타트 지연(외부 API)

- 증상: 최초 호출(네트워크/파싱 지연) 2초대 스파이크 발생
- 대응: 메모리 캐시 + 스냅샷 폴백(캐시 TTL: 목록 10분 / 상세 30분)
- 결과: 콜드 스타트 최악값 2.18s → 0.14s, 평균 132ms → 65ms (≈ -51%)

#### 성능 개선(요약)
구간	Avg (ms)	P50 (ms)	Max (ms)
최적화 전	132.4	56.4	2184.3
최적화 후	64.7	55.7	142.9

평균 응답 ≈ 51% 단축 (132.4 → 64.7)

최악 응답(콜드 스타트) ≈ 93% 단축 (2184.3 → 142.9)

동일 머신/로컬 네트워크에서 연속 30회 호출 평균값으로 산출(외부망/시간대에 따라 변동 가능)

## 측정 재현 방법
Windows (PowerShell)
### 30회 반복 측정(총 소요 ms)
1..30 | ForEach-Object {
  $t = Measure-Command { curl.exe -s http://localhost:8000/api/hrd-lectures/ > $null }
  [PSCustomObject]@{ idx = $_; total_ms = [math]::Round($t.TotalMilliseconds,1) }
} | Format-Table -Auto

### 간단 요약 통계
1..30 | %{
  (Measure-Command { curl.exe -s http://localhost:8000/api/hrd-lectures/ > $null }).TotalMilliseconds
} | Measure-Object -Average -Maximum -Minimum

macOS/Linux (bash)
for i in $(seq 1 30); do
  curl -s -o /dev/null -w "total=%{time_total}\n" http://localhost:8000/api/hrd-lectures/
done | awk -F= '{sum+=$2*1000; if($2*1000>max)max=$2*1000} END{printf "avg=%.1fms, max=%.1fms\n",sum/NR,max}'

## 운영/보안 체크리스트

비밀값(DB/SMTP/S3/API 키 등)은 환경변수로만 주입(레포 내 노출 금지)
업로드 파일은 S3 저장, 정적은 WhiteNoise 해시 서빙
관리자 API는 JWT로 보호, 토큰 만료/권한 점검

## 라이선스
### 본 저장소는 UNLICENSED 상태이며, 학원 서비스 운영을 위한 목적으로만 사용합니다.
