import os
from os import getenv
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# 환경변수 로드: 로컬만 .env.* 사용, Render는 대시보드에서 주입해야함
env_local = BASE_DIR / "envs" / ".env.local"
if env_local.exists():
    load_dotenv(env_local)

if os.getenv("DJANGO_ENV") == "production":
    env_prod = BASE_DIR / "envs" / ".env.prod"
    if env_prod.exists():
        load_dotenv(env_prod)

ENV = os.getenv("DJANGO_ENV", "local")
DEBUG = os.getenv("DEBUG", "False") == "True"

# 보안 키 (Render 환경변수로 꼭 주입해줘야함)
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")

# 호스트/오리진 (배포 시 환경변수로 넣어주기)
ALLOWED_HOSTS = [h for h in os.getenv("ALLOWED_HOSTS", "").split(",") if h]
if DEBUG and not ALLOWED_HOSTS:
    # 로컬 편의
    ALLOWED_HOSTS = ["*"]

CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    o for o in os.getenv("CORS_ALLOWED_ORIGINS", "").split(",") if o
]
CSRF_TRUSTED_ORIGINS = [
    o for o in os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",") if o
]

# 로컬 개발 시 자동 허용
if DEBUG:
    if "http://localhost:5173" not in CORS_ALLOWED_ORIGINS:
        CORS_ALLOWED_ORIGINS.append("http://localhost:5173")
    if "http://127.0.0.1:5173" not in CORS_ALLOWED_ORIGINS:
        CORS_ALLOWED_ORIGINS.append("http://127.0.0.1:5173")
    if "http://localhost:8000" not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append("http://localhost:8000")

# ─────────────────────────────────────────────────────────
AUTH_USER_MODEL = "accounts.AdminUser"

# HRD / QNET 키 (필요 시)
HRD_API_KEY = os.getenv("HRD_API_KEY")
PUBLIC_API_KEY = os.getenv("PUBLIC_API_KEY")
QNET_API_KEY = os.getenv("QNET_API_KEY")

# ─────────────────────────────────────────────────────────
# Database (Neon 사용 시 DATABASE_URL 추천하기도..?)
import dj_database_url

_default_url = None
if all(
    os.getenv(k)
    for k in ["DB_ENGINE", "DB_USER", "DB_PASSWORD", "DB_HOST", "DB_PORT", "DB_NAME"]
):
    db_engine_raw = os.getenv("DB_ENGINE", "")
    engine = db_engine_raw.replace("django.db.backends.", "", 1)
    _default_url = (
        f"{engine}://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@"
        f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )

ssl_required = os.getenv("DB_SSL_REQUIRE", "False" if DEBUG else "True") == "True"

DATABASES = {
    "default": dj_database_url.config(
        default=os.getenv("DATABASE_URL", _default_url),
        conn_max_age=600,
        ssl_require=ssl_required,
    )
}

# ─────────────────────────────────────────────────────────
# Email (Naver: 발신주소는 EMAIL_HOST_USER와 일치해야함)
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.naver.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True") == "True"

DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL") or EMAIL_HOST_USER
SERVER_EMAIL = os.getenv("SERVER_EMAIL", DEFAULT_FROM_EMAIL)
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")

# 여러 수신자 지원(수강문의 알림)
INQUIRY_TO_EMAILS = [
    e.strip()
    for e in os.getenv("INQUIRY_TO_EMAILS", os.getenv("ADMIN_EMAIL", "")).split(",")
    if e.strip()
]

# ─────────────────────────────────────────────────────────
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
    "drf_spectacular",
    "drf_spectacular_sidecar",
    "apps.accounts",
    "apps.about",
    "apps.inquiries",
    "apps.lectures",
    "apps.news",
    "apps.certificates",
    "apps.gallery",
    "apps.popup",
    "apps.exam_board",
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.ScopedRateThrottle",
        "rest_framework.throttling.AnonRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "inquiries": "5/min",  # 수강문의: IP 기준 분당 5회
        "anon": "60/min",  # 전체 익명 요청 기본치
    },
    "DEFAULT_PAGINATION_CLASS": "utils.pagination.CustomPageNumberPagination",
    "PAGE_SIZE": 8,
    "DEFAULT_FILTER_BACKENDS": [
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
}

from datetime import timedelta

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=2),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=14),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
}

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

LANGUAGE_CODE = "ko-kr"
TIME_ZONE = "Asia/Seoul"
USE_I18N = True
USE_TZ = True

# --- Static (공통) ---
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
# 압축/해시된 정적파일(WhiteNoise)
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# 보안 (리버스 프록시 HTTPS)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG


def _csv(name):  # 콤마로 입력한 env를 리스트
    return [v.strip() for v in getenv(name, "").split(",") if v.strip()]


CORS_ALLOW_ALL_ORIGINS = False

# 고정 도메인(프로덕션/로컬)
CORS_ALLOWED_ORIGINS = _csv("CORS_ALLOWED_ORIGINS") or [
    "https://damoacook.com",
    "http://damoacook.com",
    "https://www.damoacook.com",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

# 프리뷰(가변) 도메인은 정규식으로 처리
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https://.*\.vercel\.app$",
]

# CSRF는 스킴 포함한 오리진 형식이 필요
CSRF_TRUSTED_ORIGINS = _csv("CSRF_TRUSTED_ORIGINS") or [
    "https://damoacook.com",
    "http://damoacook.com",
    "https://www.damoacook.com",
    "https://*.vercel.app",  # 프리뷰 전부 허용
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

INSTALLED_APPS += ["storages"]

# WhiteNoise는 staticfiles만 담당
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# --- Media / Uploads ---
if ENV == "production":
    INSTALLED_APPS += ["storages"]

    # Naver Object Storage (S3 호환)
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_S3_ENDPOINT_URL = os.getenv(
        "AWS_S3_ENDPOINT_URL"
    )  # https://kr.object.ncloudstorage.com
    AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")
    AWS_S3_REGION_NAME = os.getenv("AWS_S3_REGION_NAME", None)
    AWS_S3_SIGNATURE_VERSION = os.getenv("AWS_S3_SIGNATURE_VERSION", "s3v4")
    AWS_S3_ADDRESSING_STYLE = os.getenv("AWS_S3_ADDRESSING_STYLE", "virtual")
    AWS_DEFAULT_ACL = None  # 권한은 버킷 정책으로 관리 권장
    AWS_QUERYSTRING_AUTH = False  # 공개 URL

    AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.kr.object.ncloudstorage.com"

    STORAGES["default"] = {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
    }
    MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/"

else:
    # 로컬/개발: 파일시스템 사용 (단위테스트/개발 편함)
    STORAGES["default"] = {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    }
    MEDIA_URL = "/media/"
    MEDIA_ROOT = os.path.join(BASE_DIR, "media")


SPECTACULAR_SETTINGS = {
    "TITLE": "Damoa Cook Academy API",
    "DESCRIPTION": "다모아요리학원 공개/관리자 API 문서",
    "VERSION": "1.0.0",
    # Swagger/Redoc 정적 리소스: sidecar 사용
    "SWAGGER_UI_DIST": "SIDECAR",
    "SWAGGER_UI_FAVICON_HREF": "SIDECAR",
    "REDOC_DIST": "SIDECAR",
    # SimpleJWT 토큰 쓰는 경우 보안 스키마
    "COMPONENTS": {
        "securitySchemes": {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
            }
        }
    },
    # 기본적으로 모든 엔드포인트에 BearerAuth 적용 (원치 않으면 제거 가능)
    "SECURITY": [{"BearerAuth": []}],
    # 스키마 자체(JSON)를 /api/docs 화면에 포함하지 않음(링크만)
    "SERVE_INCLUDE_SCHEMA": False,
}

DATA_UPLOAD_MAX_MEMORY_SIZE = 30 * 1024 * 1024  # 30MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 30 * 1024 * 1024
