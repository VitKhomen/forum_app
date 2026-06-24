from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
import sys
from pathlib import Path
from decouple import config, Csv
from datetime import timedelta
import dj_database_url


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = ['.onrender.com', 'localhost',
                 '127.0.0.1', '.vercel.app', 'forum-app-two-chi.vercel.app']
# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'corsheaders',
    'django_filters',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'taggit',
]

LOCAL_APPS = [
    'apps.main',
    'apps.accounts',
    'apps.comments',
    'apps.feedback',
    'apps.likes',
    'apps.karma',
    'apps.movies',
    'apps.bookmarks',
    'apps.polls',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    "default": dj_database_url.config(
        default=config(
            "DATABASE_URL",
            default='sqlite:///db.sqlite3'
        ),
        conn_max_age=300,
        ssl_require=False
    )
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / config('STATIC_ROOT', default='staticfiles')

# Media files
AWS_ACCESS_KEY_ID = config("R2_ACCESS_KEY")
AWS_SECRET_ACCESS_KEY = config("R2_SECRET_KEY")
AWS_STORAGE_BUCKET_NAME = config("AWS_STORAGE_BUCKET_NAME")

# закрытый API эндпоинт для boto3
AWS_S3_ENDPOINT_URL = config("S3_ENDPOINT_URL")

# публичный домен для ссылок
AWS_S3_CUSTOM_DOMAIN = f"{config('R2_PUBLIC_DOMAIN')}"

STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
        "OPTIONS": {
            "bucket_name": AWS_STORAGE_BUCKET_NAME,
            "endpoint_url": AWS_S3_ENDPOINT_URL,
            "access_key": AWS_ACCESS_KEY_ID,
            "secret_key": AWS_SECRET_ACCESS_KEY,
            "custom_domain": AWS_S3_CUSTOM_DOMAIN,
        },
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/"

AWS_QUERYSTRING_AUTH = False
AWS_S3_FILE_OVERWRITE = False

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'accounts.User'

# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 9,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.MultiPartParser',
        'rest_framework.parsers.FormParser',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        # Глобальні
        'anon': '200/day',
        'user': '1000/day',

        # Коментарі
        'comment_create_minute': '5/min',
        'comment_create_hour':   '30/hour',

        # Лайки
        'like_toggle_minute': '20/min',
        'like_toggle_day':    '200/day',

        # Пости
        'post_create_minute': '3/min',
        'post_create_day':    '20/day',

        # Авторизація
        'login':    '5/min',
        'register': '300/hour',

        # Закладки
        'bookmark': '30/min',
    },
    'EXCEPTION_HANDLER': 'apps.core.exceptions.custom_exception_handler',
}


# CORS Configuration
CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default='http://localhost:5173,http://127.0.0.1:5173,https://forum-app-two-chi.vercel.app',
    cast=Csv()
)
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}

# Security Settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Логирование
LOG_LEVEL = 'DEBUG' if DEBUG else 'INFO'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {name} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {asctime} {name} {message}',
            'style': '{',
        },

    },
    'handlers': {
        'console': {
            'level': LOG_LEVEL,
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,
            'formatter': 'simple',  # или 'verbose', или 'json' если добавишь python-json-logger
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console'],
            'level': LOG_LEVEL,  # 404, 500 и т.д.
            'propagate': False,
        },
        'django.security': {
            'handlers': ['console'],
            'level': LOG_LEVEL,
            'propagate': False,
        },
        # Твои приложения
        'apps': {  # захватит все apps.*
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}


# URL для фронтенда
FRONTEND_URL = config('FRONTEND_URL', default='http://localhost:5173')

CSRF_TRUSTED_ORIGINS = [
    'https://*.vercel.app',
    'https://*.onrender.com',
    'https://forum-app-two-chi.vercel.app',
]


# Настройки для ємейла(повідомлень)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')

# апі для фільмів
TMDB_API_KEY = config('TMDB_API_KEY', default='')
# Кеш — Redis
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": config("REDIS_URL", default="redis://localhost:6379/0"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "SOCKET_CONNECT_TIMEOUT": 5,
            "SOCKET_TIMEOUT": 5,
            "IGNORE_EXCEPTIONS": True,
            "CONNECTION_POOL_KWARGS": {
                "ssl_cert_reqs": None  # потрібно для Upstash TLS
            }
        },
        "KEY_PREFIX": "justforum",
        "TIMEOUT": 3600,
    }
}

# ============================================
# CELERY CONFIGURATION
# ============================================

REDIS_URL = config('REDIS_URL', default='redis://localhost:6379/0')


def get_celery_redis_url(redis_url: str) -> str:
    """Підготовка URL для Celery (Upstash підтримує тільки db=0)"""
    parsed = urlparse(redis_url)

    query_params = parse_qs(parsed.query)

    if parsed.scheme == 'rediss':
        query_params['ssl_cert_reqs'] = ['none']

    new_query = urlencode(query_params, doseq=True)

    # Завжди використовуємо /0 для Upstash
    new_url = urlunparse((
        parsed.scheme,
        parsed.netloc,
        '/0',
        parsed.params,
        new_query,
        parsed.fragment
    ))
    return new_url


CELERY_BROKER_URL = config(
    'CELERY_BROKER_URL',
    default=get_celery_redis_url(REDIS_URL)
)

CELERY_RESULT_BACKEND = CELERY_BROKER_URL

# Додаткові параметри для Upstash
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_BROKER_CONNECTION_RETRY = True
CELERY_BROKER_CONNECTION_MAX_RETRIES = 10

CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

CELERY_RESULT_EXPIRES = 3600
CELERY_TASK_TIME_LIMIT = 60
CELERY_TASK_SOFT_TIME_LIMIT = 45
CELERY_TASK_DEFAULT_RETRY_DELAY = 10
CELERY_TASK_MAX_RETRIES = 3
CELERY_WORKER_MAX_TASKS_PER_CHILD = 200
CELERY_TASK_DEFAULT_QUEUE = 'justforum_default'
