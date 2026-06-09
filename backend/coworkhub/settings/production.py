import dj_database_url

from .base import *

DEBUG = False
ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    default='',
    cast=lambda v: [s.strip() for s in v.split(',') if s.strip()],
)

# ─── PostgreSQL (Render managed) ──────────────────────────
# Set DATABASE_URL to Render's Postgres connection string. The Internal
# Database URL works without SSL; set DB_SSL_REQUIRE=True for an external URL.
DATABASES = {
    'default': dj_database_url.config(
        env='DATABASE_URL',
        conn_max_age=600,
        ssl_require=config('DB_SSL_REQUIRE', default=False, cast=bool),
    )
}

# ─── Redis Cache ──────────────────────────────────────────
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': config('REDIS_URL', default='redis://localhost:6379/0'),
        'OPTIONS': {'CLIENT_CLASS': 'django_redis.client.DefaultClient'},
        'KEY_PREFIX': 'cwh',
    }
}

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# ─── Security ─────────────────────────────────────────────
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
# Render terminates SSL at the proxy — trust the forwarded header instead of redirecting
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
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
