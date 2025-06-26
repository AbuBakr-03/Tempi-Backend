# TempiProject/settings.py
from pathlib import Path
from datetime import timedelta
import os
from dotenv import load_dotenv
from urllib.parse import urlparse, parse_qsl
from decouple import config

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("DJANGO_SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config("DJANGO_DEBUG", cast=bool, default=False)

RENDER_EXTERNAL_HOSTNAME = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
ALLOWED_HOSTS = ["localhost"]

if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "TempiApp",
    "rest_framework",
    "rest_framework.authtoken",
    "djoser",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "storages",
    "django_filters",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "TempiProject.urls"

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

WSGI_APPLICATION = "TempiProject.wsgi.application"

# Database configuration
tmpPostgres = urlparse(os.getenv("DATABASE_URL"))

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": tmpPostgres.path.replace("/", ""),
        "USER": tmpPostgres.username,
        "PASSWORD": tmpPostgres.password,
        "HOST": tmpPostgres.hostname,
        "PORT": 5432,
        "OPTIONS": dict(parse_qsl(tmpPostgres.query)) if tmpPostgres.query else {},
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static files configuration
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# Cloudflare R2 Configuration
USE_S3 = config("USE_S3", cast=bool, default=False)

if USE_S3:
    # Use Cloudflare R2 for production
    CLOUDFLARE_R2_BUCKET = config("CLOUDFLARE_R2_BUCKET")
    CLOUDFLARE_R2_ACCESS_KEY = config("CLOUDFLARE_R2_ACCESS_KEY")
    CLOUDFLARE_R2_SECRET_KEY = config("CLOUDFLARE_R2_SECRET_KEY")
    CLOUDFLARE_R2_BUCKET_ENDPOINT = config("CLOUDFLARE_R2_BUCKET_ENDPOINT")

    # Validate that all required R2 settings are present
    if not all(
        [
            CLOUDFLARE_R2_BUCKET,
            CLOUDFLARE_R2_ACCESS_KEY,
            CLOUDFLARE_R2_SECRET_KEY,
            CLOUDFLARE_R2_BUCKET_ENDPOINT,
        ]
    ):
        raise ValueError("Missing required Cloudflare R2 configuration variables")

    CLOUDFLARE_R2_CONFIG_OPTIONS = {
        "bucket_name": CLOUDFLARE_R2_BUCKET,
        "access_key": CLOUDFLARE_R2_ACCESS_KEY,
        "secret_key": CLOUDFLARE_R2_SECRET_KEY,
        "endpoint_url": CLOUDFLARE_R2_BUCKET_ENDPOINT,
        "default_acl": "public-read",
        "signature_version": "s3v4",
        "region_name": "auto",  # Add this for Cloudflare R2
    }

    STORAGES = {
        "default": {
            "BACKEND": "helpers.cloudflare.storages.MediaFileStorage",
            "OPTIONS": CLOUDFLARE_R2_CONFIG_OPTIONS,
        },
        "staticfiles": {
            "BACKEND": "helpers.cloudflare.storages.StaticFileStorage",
            "OPTIONS": CLOUDFLARE_R2_CONFIG_OPTIONS,
        },
    }

    MEDIA_URL = f"https://{CLOUDFLARE_R2_BUCKET}.{CLOUDFLARE_R2_BUCKET_ENDPOINT.split('//')[1]}/media/"
else:
    # Use local storage for development
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }
    MEDIA_URL = "/media/"

MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=30),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
}

DJOSER = {
    "LOGIN_FIELD": "username",
    "USER_ID_FIELD": "id",
    "PASSWORD_RESET_CONFIRM_URL": "reset-password/{uid}/{token}",
    "SEND_PASSWORD_RESET_EMAIL": True,
    "TOKEN_MODEL": None,
    "SERIALIZERS": {
        "user_create": "TempiApp.serializers.CustomUserCreateSerializer",
        "user": "TempiApp.serializers.CustomUserSerializer",
    },
}

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ),
}
