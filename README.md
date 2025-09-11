
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

cd backend
python -m venv .venv && source .venv/bin/activate
# (Windows) .\.venv\Scripts\Activate.ps1
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
  subgraph Client["사용자 브라우저"]
    U[사용자]
  end

  subgraph FE["Vercel (Frontend: React · Vite)"]
    S["정적 파일<br/>(HTML · CSS · JS)"]
    Rw["Rewrite: /api/* -> Backend"]
  end

  subgraph BE["Render (Django/DRF + Gunicorn)"]
    App[Django App]
    Docs[Swagger / Redoc]
    Health["GET /healthz"]
  end

  DB[(PostgreSQL)]
  S3[(Naver Object Storage)]
  SMTP[(Naver SMTP)]
  HRD[(HRD-Net OpenAPI)]

  U -->|HTTPS| S
  S -->|XHR /api/*| Rw
  Rw --> App

  App -->|ORM| DB
  App -->|django-storages| S3
  App -->|SMTP| SMTP
  App -->|HTTP| HRD
  App -.-> Docs
  App -.-> Health
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




