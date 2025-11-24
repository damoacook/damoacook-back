<<<<<<< HEAD
=======

# 다모아요리학원 (Damoa Cook Academy)

<p align="center">
  <img src="./assets/로고.jpg" alt="Damoa Cook Academy Logo" width="300" />
</p>

<p align="center">
  <a href="https://damoacook.com">🔗 웹사이트</a> &nbsp;•&nbsp;
  <a href="https://damoacook.com/api/">🧩 API Base</a>
</p>

<p align="center">
  <a href="https://hits.seeyoufarm.com">
    <img src="https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com%2Fdamoacook&count_bg=%2379C83D&title_bg=%23555555&title=org%20visits&edge_flat=false" alt="org visits"/>
  </a>
</p>

---

## 01. 프로젝트 정보

### (1) 프로젝트 제목

**다모아요리학원 홈페이지 / Damoa Cook Academy**

### (2) 프로젝트 개요

- **목적**: 학원 소개, 강의/자격증 정보 제공, 문의 접수, 공지/갤러리 운영
- **개발 기간**: _2025.06 ~ 2025.09_
- **특징**: HRD-Net **공공데이터 연동**, **Naver Object Storage(S3 호환)** 기반 미디어 저장, **무로그인 문의 접수**

### (3) 배포 주소

- **웹사이트**: https://damoacook.com
- **API Base**: https://damoacook.com/api/ _(Vercel → Render/Gunicorn 라우팅)_

### (4) 역할

| 이름   | 역할              | GitHub                    | 비고                      |
| ------ | ----------------- | ------------------------- | ------------------------- |
| 고근우 | 백엔드/풀스택, PM | https://github.com/gkw314 | 인프라/데이터 연동/문서화 |

### (5) 한눈에 보기

- **Frontend**: React(Vite) + Tailwind, React Query, React Router
- **Backend**: Django + DRF, SimpleJWT(관리자 인증), Gunicorn + WhiteNoise
- **Integrations**: HRD-Net 강의, Naver SMTP 메일 전송, Naver Maps
- **Infra**: Vercel(프론트), Render(백엔드), Naver Object Storage(S3)

---

## 02. 시작 가이드

### (1) 요구 사항

- **Node.js** v20+
- **Python** 3.12+ _(3.13도 가능)_
- **PostgreSQL** 14+
- (운영) Vercel / Render / Naver Object Storage(S3)

### (2) 리포 구조

.
├─ frontend/ # React + Vite + Tailwind
└─ backend/ # Django + DRF

### (3) 설치 & 실행

Backend (pip)

```bash

C:\Users\82109\PycharmProjects\damoa-backend
source damoa/bin/activate
# (Windows) .\damoa\Scripts\Activate.ps1
pip install -r requirements.txt

# 로컬 실행 (환경변수는 인프라에서 주입, 값은 README에 공개하지 않음)
# 개발 중 메일은 콘솔 출력으로 대체 가능
# macOS/Linux
export DATABASE_URL="postgresql://USER:PASS@HOST:5432/DBNAME"
export EMAIL_BACKEND="django.core.mail.backends.console.EmailBackend"


python manage.py migrate
python manage.py runserver 0.0.0.0:8000
# Swagger: http://localhost:8000/api/docs/
```

## 03. 기술 스택

# Environment / Infra

- Vercel(Frontend), Render(Backend)
- Naver Object Storage (S3 compatible)
- PostgreSQL

# Backend

- Django, Django REST Framework
- SimpleJWT (관리자 인증)
- django-storages(S3), gunicorn, whitenoise
- drf-spectacular (Swagger/Redoc 자동 문서화)

# Integrations

- HRD-Net (Work24) 강의 데이터
- Naver SMTP (문의 메일)
- Naver MAP (네이버 지도)

4.  운영/배포 아키텍처

```mermaid

flowchart LR
  User -->|HTTPS| Vercel[Frontend]
  Vercel -->|/api rewrite| Render[Backend: Gunicorn]
  Render -->|ORM| PostgreSQL[(DB)]
  Render -->|SMTP| NaverMail[(Naver SMTP)]
  Render -->|Media| NaverObjectStorage[(S3)]
  Render -->|OpenAPI| HRDNet[HRD-Net]
```

- 단일 도메인 + 경로 라우팅: https://damoacook.com/api/*
- 장점: SEO/쿠키/CSRF/추적 스니펫 관리 단순, CORS 이슈 최소화
- 구현: Vercel에서 /api/\* 를 Render 백엔드로 rewrite
- FE/BE 분리 배포: 정적은 Vercel(에지 캐시), 동적은 Render(Gunicorn) → 장애/배포 영향 범위 분리
- S3 호환 스토리지: Render 컨테이너 FS는 휘발성 → 업로드 미디어는 S3로 영속화
- 대안 검토: api.damoacook.com 서브도메인은 CORS/쿠키 정책 고려 필요 → 운영 편의성상 경로 방식 채택

## 05. 화면 구성 / API 주소

# 화면 구성 (예시)

- 홈: 모집중 강의 슬라이드, 공지/갤러리 섹션
- 강의: 내부 강의 목록/상세, HRD-Net 강의 목록/상세
- 공지사항/갤러리: 목록/상세
- 수강문의: 폼 제출(무로그인)
- 오시는 길: Naver Maps JS v3
- 팝업 배너: 오늘 하루 보지 않기(LocalStorage)

# API (요약)

- GET /api/lectures/ 내부 강의 목록
- GET /api/lectures/{id}/ 내부 강의 상세
- GET /api/hrd-lectures/ HRD-Net 강의 목록
- POST /api/inquiries/ 수강문의 접수 (DB 저장 + 메일 발송)
- GET /api/news/, GET /api/news/{id}/
- GET /api/gallery/, GET /api/gallery/{id}/
  (관리자 전용) 생성/수정/삭제 엔드포인트는 JWT 필요
- 문서화: /api/docs(Swagger) · /api/redoc(Redoc)

## 06. 주요 기능

- 강의 관리: 내부 강의 CRUD, 모집 상태 라벨(“모집중”만 홈 노출)
- 수강문의: 폼 제출 → DB 저장 후 Naver SMTP 메일(실패 로깅/재발송 분리 설계)
- 콘텐츠: 공지/갤러리 목록·상세, 이미지 S3 저장
- 지도: Naver Map 연동
- UI/UX: 팝업 배너(오늘 하루 보지 않기), 브레드크럼, 반응형
- 관리자: 관리자 로그인 시 강의/공지/갤러리/팝업 관리

## 07. 트러블슈팅

### 1) 201인데 수강문의 메일이 오지 않음

- **증상**: `POST /api/inquiries/`가 201을 반환해 DB에는 저장되지만 수신 메일이 없음.
- **원인 파악**
  - Naver SMTP 정책상 **발신자(From)와 로그인 계정(EMAIL_HOST_USER)** 미일치 시 차단 가능.
  - `DEFAULT_FROM_EMAIL`에 따옴표 포함 등 **헤더 포맷 오류** 가능.
  - TLS/포트 설정 오류로 실제 발송 단계에서 실패했으나 애플리케이션에서 오류가 숨겨져 확인 곤란.
- **조치**
  - 운영 환경변수 정정: `EMAIL_USE_TLS=True`, `EMAIL_PORT=587`.
  - `DEFAULT_FROM_EMAIL`을 **`다모아요리학원 <whitebhy100@naver.com>`** 형태로 교정(큰따옴표 제거)하고, **발신자 = EMAIL_HOST_USER** 일치 확인.
  - 수신자 구성: `INQUIRY_TO_EMAILS`로 **복수 수신자** 지원(운영/관리자 메일).
  - 개발·검증 단계에서는 **콘솔 메일 백엔드**로 헤더/본문 즉시 확인.
- **검증**
  - 동일 요청 데이터로 실제 SMTP 발송 테스트 → 정상 수신 확인.
  - 201 응답 시 DB 저장 사실과 **메일 수신 이벤트**가 일치하는지 샘플 케이스로 확인.

---

### 2) Vercel 프리뷰에서 CORS/CSRF 프리플라이트 실패

- **증상**: 프리뷰 배포 URL에서 `OPTIONS` 프리플라이트가 403/실패하고 후속 `GET/POST` 요청도 차단.
- **원인 파악**
  - 프리뷰 오리진이 **CORS 허용 목록/정규식**에 포함되지 않음.
  - CSRF Trusted Origins 누락으로 쿠키/세션 플로우 차단.
- **조치**
  - `CORS_ALLOWED_ORIGIN_REGEXES`에 **`^https://.*\.vercel\.app$`** 추가.
  - `CSRF_TRUSTED_ORIGINS`에 운영 도메인 + 프리뷰 와일드카드 추가.
  - 리버스 프록시 HTTPS 인지 설정 확인: `SECURE_PROXY_SSL_HEADER=("HTTP_X_FORWARDED_PROTO","https")`.
- **검증**
  - 프리뷰 URL에서 프리플라이트 응답 헤더(`Access-Control-*`) 정상 여부 확인.
  - 실제 폼 제출/파일 업로드까지 교차 테스트로 정상 동작 확인.

## 08. 디렉토리(요약)

# (1) 파일구조

```bash
=======
>>>>>>> 4770a57 (feat(exam_board): 시험정보 게시판(첨부/검색/순번) + 테스트)
# 다모아요리학원 Backend (Django + DRF)

![Damoa Cook Academy Logo](./assets/다모아로고.jpg)

[![Website](https://img.shields.io/badge/WEBSITE-LIVE-2ea44f?style=for-the-badge&logo=googlechrome&logoColor=white)](https://damoacook.com)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)
![DRF](https://img.shields.io/badge/DRF-E23F3D?style=for-the-badge&logo=django&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![OpenAPI](https://img.shields.io/badge/OpenAPI-6BA539?style=for-the-badge&logo=openapiinitiative&logoColor=white)
![Swagger](https://img.shields.io/badge/Swagger-85EA2D?style=for-the-badge&logo=swagger&logoColor=white)
![Render](https://img.shields.io/badge/Render-46E3B7?style=for-the-badge&logo=render&logoColor=white)
![Gunicorn](https://img.shields.io/badge/Gunicorn-499848?style=for-the-badge&logo=gunicorn&logoColor=white)
![WhiteNoise](https://img.shields.io/badge/WhiteNoise-4B5563?style=for-the-badge)
![SimpleJWT](https://img.shields.io/badge/SimpleJWT-000000?style=for-the-badge)
![Object Storage (S3)](https://img.shields.io/badge/Object%20Storage%20(S3)-03C75A?style=for-the-badge&logo=naver&logoColor=white)

> 다모아요리학원 **백엔드**는 Django + DRF 기반의 REST API입니다.  
> 강의·공지·갤러리·수강문의 도메인과 **HRD-Net(Work24) 연동**, **SMTP 알림**, **S3 미디어 저장**을 제공합니다.

---

## 목차
- [프로젝트 개요](#프로젝트-개요)
- [개발 인원/기간](#개발-인원기간)
- [배포 & 아키텍처](#배포--아키텍처)
- [기술 스택](#기술-스택)
- [설치 & 실행(로컬)](#설치--실행로컬)
- [API 요약](#api-요약)
- [트러블슈팅 & 성능개선](#트러블슈팅--성능개선)
- [운영/보안 체크리스트](#운영보안-체크리스트)
- [라이선스](#라이선스)

---

## 프로젝트 개요
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
- **기간**: 2025.07 ~ 2025.09

---

## 배포 & 아키텍처
![Damoa Architecture](./assets/damoacook(1).png)

- **단일 도메인 + 경로 라우팅**: `https://damoacook.com/api/*` → (Vercel) **rewrite** → (Render) 백엔드  
  - **장점**: SEO/쿠키/CSRF/추적 스니펫 관리 단순, CORS 이슈 최소화
- **FE/BE 분리 배포**: 정적은 Vercel(에지 캐시), 동적은 Render(Gunicorn) → 장애/배포 영향 범위 분리
- **S3 호환 스토리지**: 미디어 영속화
- **외부 연동**: HRD-Net(Work24 OpenAPI), Naver SMTP

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
> 공개 API는 인증 없이 접근, **관리자용 엔드포인트는 JWT 필요**  
> 로컬: http://localhost:8000/api/docs/

---

### 1) 수강문의 (무로그인)
`POST /api/inquiries/`  
요청(모델 기준):
```json
{
  "name": "홍길동",        // 최대 100자
  "phone": "010-1234-5678", // 최대 20자
  "message": "한식 기능사 과정 문의합니다."
}

성공(201):

{
  "id": 5301,
  "name": "홍길동",
  "phone": "010-1234-5678",
  "message": "한식 기능사 과정 문의합니다.",
  "created_at": "2025-09-01T10:11:12+09:00"
}


유효성 오류(예):

{
  "phone": ["이 필드는 최대 20자 이하이어야 합니다."]
}
```

2) 강의 (내부 DB)

GET /api/lectures/?page=1&page_size=12
응답(요약):
```json
{
  "count": 42,
  "next": "https://damoacook.com/api/lectures/?page=2&page_size=12",
  "previous": null,
  "results": [
    {
      "id": 101,
      "type": "academy",           // "academy" | "hrd"
      "title": "한식 기능사 실기",
      "description": "과정 설명...",
      "image": "https://.../media/lectures/xxx.jpg",  // ImageField URL
      "tags": "한식,실기",
      "day_of_week": "월/수/금",
      "time": "14:00~16:00",
      "start_date": "2025-09-15",
      "end_date": "2025-10-30",
      "capacity": 20,
      "applied": 7,
      "created_at": "2025-08-20T12:00:00+09:00"
    }
  ]
}
```

GET /api/lectures/{id}/
응답(예):
```json
{
  "id": 101,
  "type": "academy",
  "title": "한식 기능사 실기",
  "description": "과정 설명...",
  "image": "https://.../media/lectures/xxx.jpg",
  "tags": "한식,실기",
  "day_of_week": "월/수/금",
  "time": "14:00~16:00",
  "start_date": "2025-09-15",
  "end_date": "2025-10-30",
  "capacity": 20,
  "applied": 7,
  "created_at": "2025-08-20T12:00:00+09:00"
}
```


3) HRD-Net 강의(연동)

GET /api/hrd-lectures/?q=한식&region=서울&page=1

HRD-Net 외부 데이터 연동 결과를 페이지네이션하여 제공

응답 필드는 연동 스키마에 맞춰 다를 수 있습니다(예: 과정명, 기관명, 지역, 접수/개강일, 상세링크 등).
```json
{
  "count": 120,
  "next": "...",
  "previous": null,
  "results": [
    {
      "id": "HRD-24-0001",
      "title": "한식 조리기능사 취득과정",
      "provider": "○○직업학교",
      "region": "서울",
      "start_date": "2025-09-10",
      "link": "https://www.hrd.go.kr/..."
    }
  ]
}
```
4) 공지/갤러리

GET /api/news/ / GET /api/news/{id}/

GET /api/gallery/ / GET /api/gallery/{id}/

목록 응답(요약):
```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 301,
      "title": "9월 모집 안내",
      "thumbnail": "https://.../thumb.jpg",
      "created_at": "2025-08-31T20:00:00+09:00"
    }
  ]
}
```

상세 응답(예):
```json
{
  "id": 301,
  "title": "9월 모집 안내",
  "content": "<p>상세 공지 본문...</p>",
  "images": ["https://.../1.jpg", "https://.../2.jpg"],
  "created_at": "2025-08-31T20:00:00+09:00"
}
```

## 트러블슈팅 & 성능개선
### 1) 201인데 수강문의 메일이 오지 않음

- **증상**  
  `POST /api/inquiries/`가 201(저장 성공)을 반환하지만, 실제 수신 메일이 없음.

- **원인 분석**  
  - Naver SMTP 정책상 **From 주소 ≠ 로그인 계정(EMAIL_HOST_USER)** 인 경우 차단 가능.  
  - `DEFAULT_FROM_EMAIL`에 큰따옴표 등 **헤더 포맷 오류**가 섞여 SMTP 단계에서 Drop.  
  - TLS/포트 설정 불일치 + 애플리케이션에서 예외를 묵살(기본 `fail_silently=True` 관성).

- **조치**  
  - 운영 환경변수 교정: `EMAIL_USE_TLS=True`, `EMAIL_PORT=587`, **From = EMAIL_HOST_USER 동일화**.  
  - `DEFAULT_FROM_EMAIL`을 `다모아요리학원 <id@naver.com>` 형태로 규격화(큰따옴표 제거).  
  - 수신자 다중화: `INQUIRY_TO_EMAILS`로 운영/관리자 복수 수신 구성.  
  - 개발·검증 단계는 **콘솔 메일 백엔드**로 교체하여 헤더/본문 즉시 확인.  

- **결과**  
  동일 테스트 데이터로 201 응답 ↔ 실제 수신 이벤트 **일치** 확인.  
  (SMTP 측 Bounce/Drop 재발 없음)

---

### 2) HRD-Net(Work24) 목록 호출 콜드 스타트 지연

- **증상**  
  외부 API 최초 호출 시 네트워크/파싱 지연으로 **2초대 스파이크** 발생.

- **조치**  
  - 목록: **메모리 캐시 + 스냅샷 폴백**(TTL **10분**)  
  - 상세: **메모리 캐시**(TTL **30분**)  
  - 헤더로 계측값 노출: `X-Elapsed-ms`/`X-Cache`(MISS/REFRESH/HIT-FALLBACK)

- **측정 결과(로컬 30회 연속 호출)**

  | 구간         | Avg(ms) | P50(ms) | Max(ms)  |
  |--------------|---------|---------|----------|
  | 최적화 전    | 132.4   | 56.4    | 2184.3   |
  | 최적화 후    | 64.7    | 55.7    | 142.9    |

  - **평균 응답**: 132.4 → 64.7ms (**약 51% 단축**)  
  - **최악 응답(콜드 스타트)**: 2184.3 → 142.9ms (**약 93% 단축**)  
  - 동일 머신/로컬 네트워크 기준. 외부망/시간대에 따라 수치는 변동 가능.

---

### 3) Vercel 프리뷰에서 CORS/CSRF 프리플라이트 실패

- **증상**  
  프리뷰 URL에서 `OPTIONS`(preflight) 403, 후속 `GET/POST`도 차단.

- **원인 분석**  
  - 프리뷰 오리진이 **CORS 허용 목록/정규식**에 포함되지 않음.  
  - `CSRF_TRUSTED_ORIGINS`에 프리뷰 도메인 누락.  
  - 프록시 HTTPS 인지 미설정 시 CSRF 판단이 오작동할 여지.

- **조치**  
  - `CORS_ALLOWED_ORIGIN_REGEXES`에 `^https://.*\.vercel\.app$` 추가.  
  - `CSRF_TRUSTED_ORIGINS`에 운영 도메인 + 프리뷰 와일드카드 반영.  
  - `SECURE_PROXY_SSL_HEADER=("HTTP_X_FORWARDED_PROTO","https")` 설정 확인.

- **결과**  
  프리뷰 배포에서도 **폼 제출/파일 업로드 정상**.

---

### 4) 수강문의 API 남용(스팸/폭주) 예방

> 프러덕션 안정성을 위해 **서버 사이드**에서 1차 방어를 적용했고, 추가 방어는 단계적으로 확대 중입니다.

- **위험 시나리오**  
  자동화된 봇/스크립트가 `POST /api/inquiries/`를 대량 호출 → SMTP 큐 폭주/알림 테러 위험.

- **적용(1차)**  
  - **서버 검증 강제**: `name(max_length=100)`, `phone(max_length=20)`, `message(Text)` 길이 제한 및 필수값 체크.  
  - **Payload 중복 차단**: 동일 `(name, phone, message)` 조합 **60초 내 재요청 차단**(디듀프).  
  - **IP 기반 레이트 리미트**: **5회/10분** 초과 시 **429** 응답(캐시 기반).  
  - **SMTP 경로 분리**: DB 저장과 메일 발송 경로를 분리하여, 발송 실패가 API 응답시간을 지연시키지 않도록 처리.

- **추가 계획(2차)**  
  - **reCAPTCHA/Turnstile** 도입(봇 트래픽 차단)  
  - **전화번호 패턴/통신사 블랙리스트** 기반 정교화  
  - **관리자 재발송 큐**(지연·실패 재시도, 폭주 시 유예 정책)



## 운영/보안 체크리스트

- 비밀값(DB/SMTP/S3/API 키 등)은 환경변수로만 주입(레포 내 노출 금지)
- 업로드 파일은 S3 저장, 정적은 WhiteNoise 해시 서빙
- 관리자 API는 JWT로 보호, 토큰 만료/권한 점검

## 라이선스
- 본 저장소는 UNLICENSED 상태이며, 학원 서비스 운영을 위한 목적으로만 사용합니다.
