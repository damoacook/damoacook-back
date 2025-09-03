# 다모아요리학원 Backend (Django + DRF)

<p align="center">
  <a href="https://damoacook.com"><img alt="Website" src="https://img.shields.io/badge/website-live-2ea44f"></a>
  <img alt="Python" src="https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white">
  <img alt="Django" src="https://img.shields.io/badge/Django-5.x-092E20?logo=django&logoColor=white">
  <img alt="DRF" src="https://img.shields.io/badge/DRF-REST_API-red">
  <img alt="PostgreSQL" src="https://img.shields.io/badge/PostgreSQL-14%2B-4169E1?logo=postgresql&logoColor=white">
  <img alt="Render" src="https://img.shields.io/badge/Backend-Render-46E3B7?logo=render&logoColor=white">
  <img alt="License" src="https://img.shields.io/badge/license-UNLICENSED-lightgrey">
</p>

<p align="center">
  <!-- repo 방문 카운터: url 파라미터를 현재 백엔드 리포 페이지 주소로 맞추세요 -->
  <a href="https://hits.seeyoufarm.com">
    <img src="https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=<--여기에_백엔드_리포_URL을_URL인코딩하여_넣으세요-->&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=repo%20visits&edge_flat=false" alt="hits"/>
  </a>
</p>

> 다모아요리학원 백엔드는 Django + DRF 기반 REST API 서비스를 제공합니다.

- [요구 사항](#요구-사항)
- [설치](#설치)
- [실행](#실행)
- [API](#api)
- [보안](#보안)
- [아키텍처](#아키텍처)
- [디렉토리](#디렉토리)
- [기여](#기여)
- [라이선스](#라이선스)

---

## 요구 사항
- Python 3.12+ (3.13도 가능)
- PostgreSQL 14+
- (배포) Render, Vercel(프론트), S3 호환 스토리지

## 설치
```bash
git clone <REPO_URL> damoa-backend
cd damoa-backend

# Poetry
poetry install

# 또는 pip
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
⚠️ 프로젝트는 운영·개발 설정을 환경변수에서 읽습니다. 값 자체는 이 README에 포함하지 않습니다.
운영 환경에서 제공 받은 변수(이메일, 스토리지, DB, 외부 API 키 등)를 인프라 콘솔(Render 등)에 등록해 주세요.

실행
```

# DB 마이그레이션 & 개발 서버
poetry run python manage.py migrate
poetry run python manage.py runserver 0.0.0.0:8000
# 또는 pip 환경에서
python manage.py migrate && python manage.py runserver 0.0.0.0:8000
SMTP 점검(선택):
# python manage.py shell
from django.core.mail import send_mail
send_mail('[테스트] 다모아요리학원', '본문', '다모아요리학원 <발신자메일@도메인>', ['수신자메일@도메인'], fail_silently=False)
API
GET /api/lectures/ 내부 강의 목록

GET /api/lectures/{id}/ 내부 강의 상세

GET /api/hrd-lectures/ HRD-Net 강의 목록

GET /api/hrd-lectures/{id}/ HRD-Net 강의 상세

POST /api/inquiries/ 수강문의 접수 (DB 저장 + 메일 발송)

GET /api/news/, GET /api/news/{id}/

GET /api/gallery/, GET /api/gallery/{id}/

문서화: /docs(Swagger/Redoc) 또는 docs/api.md

## 보안
비밀값(메일, 스토리지, DB, 외부 API 키 등)은 환경변수로만 주입합니다(값 공개 금지).

CSRF/CORS는 운영 도메인 및 프리뷰 도메인만 허용하도록 설정합니다.

컨테이너 파일시스템은 휘발성일 수 있으므로 업로드는 외부 스토리지를 사용합니다.

메일 전송 시 실패 원인 파악을 위해 개발 단계에 한해 fail_silently=False 권장.

## 아키텍처
mermaid
코드 복사
flowchart LR
  User -->|HTTPS| Frontend[Vercel]
  Frontend -->|/api| Backend[Render: Gunicorn]
  Backend -->|ORM| PostgreSQL[(DB)]
  Backend -->|SMTP| Mail[(SMTP)]
  Backend -->|Media| ObjectStorage[(S3)]
  Backend -->|OpenAPI| HRDNet[HRD-Net]
## 디렉토리
backend/
  ├─ apps/
  │  ├─ lectures/
  │  ├─ certificates/
  │  ├─ inquiries/
  │  ├─ news/
  │  ├─ gallery/
  │  └─ popup/
  ├─ config/ (settings, urls, wsgi)
  ├─ utils/  (pagination, responses ...)
  └─ envs/   (.env.local, .env.prod)   # 파일은 예시이며 실제 값은 인프라 환경변수로 관리
