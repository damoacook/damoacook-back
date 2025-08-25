import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# ─────────────────────────────────────────────────────────
# 환경변수 로드: 로컬만 .env.* 사용, Render는 대시보드에서 주입
env_local = BASE_DIR / "envs" / ".env.local"
if env_local.exists():
    load_dotenv(env_local)

if os.getenv("DJANGO_ENV") == "production":
    env_prod = BASE_DIR / "envs" / ".env.prod"
    if env_prod.exists():
        load_dotenv(env_prod)

ENV = os.getenv("DJANGO_ENV", "local")
DEBUG = os.getenv("DEBUG", "False") == "True"

# ─────────────────────────────────────────────────────────
# 보안 키 (Render 환경변수로 꼭 주입)
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")

# 호스트/오리진 (배포 시 환경변수로 넣어줘)
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
# Database (Neon 사용 시 DATABASE_URL 추천)
# 예: postgresql://USER:PASS@HOST/DB?sslmode=require
import dj_database_url

_default_url = None
if all(
    os.getenv(k)
    for k in ["DB_ENGINE", "DB_USER", "DB_PASSWORD", "DB_HOST", "DB_PORT", "DB_NAME"]
):
    db_engine_raw = os.getenv("DB_ENGINE", "")  # ← 기본값을 ""로
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
# Email (Naver: 발신주소는 EMAIL_HOST_USER와 일치해야 함)
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
    "apps.accounts",
    "apps.about",
    "apps.inquiries",
    "apps.lectures",
    "apps.news",
    "apps.certificates",
    "apps.gallery",
    "apps.popup",
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
}

from datetime import timedelta

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
}

# ─────────────────────────────────────────────────────────
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    # WhiteNoise: 정적파일 서빙(렌더에서 Nginx 없이)
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

# ─────────────────────────────────────────────────────────
# 국제화
LANGUAGE_CODE = "ko-kr"
TIME_ZONE = "Asia/Seoul"
USE_I18N = True
USE_TZ = True

# ─────────────────────────────────────────────────────────
# Static / Media
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
# 압축/해시된 정적파일(WhiteNoise)
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
# ⚠️ Render는 컨테이너 파일시스템이 휘발성이라 업로드 파일은 S3 같은 외부 스토리지로 옮기는 걸 권장

# ─────────────────────────────────────────────────────────
# 보안 (리버스 프록시 HTTPS 인지)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
