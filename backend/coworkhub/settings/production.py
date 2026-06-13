from .base import *

DEBUG = False

# Require a real SECRET_KEY in production — never fall back to the insecure
# dev default inherited from base settings.
SECRET_KEY = config('SECRET_KEY')

ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    default='',
    cast=lambda v: [s.strip() for s in v.split(',') if s.strip()],
)

# ─── TiDB Cloud ───────────────────────────────────────────
# Use the official django-tidb backend (not plain mysql): it patches Django's
# schema editor for TiDB's DDL limits, so ALTER-based FK migrations (ours and
# third-party, e.g. django_celery_beat) apply correctly.
DATABASES = {
    'default': {
        'ENGINE': 'django_tidb',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT', default='4000'),
        'OPTIONS': {
            # mysqlclient expects SSL nested under "ssl" (not ssl_ca/ssl_verify_*).
            # ssl_mode=VERIFY_IDENTITY enforces TLS; TiDB Cloud certs are publicly
            # signed, so the container's system CA bundle verifies them.
            'ssl_mode': 'VERIFY_IDENTITY',
            'ssl': {'ca': config('TIDB_SSL_CA', default='/etc/ssl/certs/ca-certificates.crt')},
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# ─── Cache + sessions ─────────────────────────────────────
# Use Redis when a broker is provided (e.g. Render). Hosts without managed
# Redis (e.g. Hugging Face Spaces free) leave REDIS_URL unset — fall back to an
# in-process cache and DB-backed sessions so the app runs on a single host with
# no broker. The API is JWT-based, so it never depends on Redis.
REDIS_URL = config('REDIS_URL', default='')

if REDIS_URL:
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': REDIS_URL,
            'OPTIONS': {'CLIENT_CLASS': 'django_redis.client.DefaultClient'},
            'KEY_PREFIX': 'cwh',
        }
    }
    SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
    SESSION_CACHE_ALIAS = 'default'
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'cwh-locmem',
        }
    }
    SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# ─── Security ─────────────────────────────────────────────
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
# Render terminates SSL at the proxy — trust the forwarded header instead of redirecting
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# Default on. Set SECURE_SSL_REDIRECT=False if the host's proxy doesn't forward
# X-Forwarded-Proto (avoids a redirect loop, e.g. on some PaaS proxies).
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=True, cast=bool)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = 'DENY'

# ─── Static files ─────────────────────────────────────────
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ─── File Storage (S3 / MinIO) ────────────────────────────
# Set USE_S3=True in .env to route MEDIA files to S3-compatible storage.
# Requires: pip install django-storages boto3
# Works with AWS S3, MinIO, DigitalOcean Spaces, Cloudflare R2.
if config('USE_S3', default=False, cast=bool):
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    AWS_ACCESS_KEY_ID = config('S3_ACCESS_KEY')
    AWS_SECRET_ACCESS_KEY = config('S3_SECRET_KEY')
    AWS_STORAGE_BUCKET_NAME = config('S3_BUCKET_NAME')
    AWS_S3_ENDPOINT_URL = config('S3_ENDPOINT_URL', default='')  # blank = AWS S3
    AWS_S3_REGION_NAME = config('S3_REGION', default='ap-south-1')
    AWS_DEFAULT_ACL = 'private'
    AWS_S3_FILE_OVERWRITE = False
    AWS_QUERYSTRING_AUTH = True   # signed URLs (private files)
    AWS_QUERYSTRING_EXPIRE = 3600  # 1-hour download link

# ─── Email via Brevo SMTP ─────────────────────────────────
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp-relay.brevo.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('BREVO_EMAIL_USER')
EMAIL_HOST_PASSWORD = config('BREVO_API_KEY')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@coworkhub.com')
