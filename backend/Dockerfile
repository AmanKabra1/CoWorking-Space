FROM python:3.12-slim AS base

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# System deps needed by mysqlclient and Pillow
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ── Dependency layer (cached unless requirements change) ──
FROM base AS deps
COPY requirements/ requirements/
RUN pip install -r requirements/production.txt

# ── Final image ───────────────────────────────────────────
FROM base AS final

# Non-root user for security
RUN groupadd --gid 1001 appgroup && \
    useradd --uid 1001 --gid appgroup --no-create-home appuser

COPY --from=deps /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=deps /usr/local/bin /usr/local/bin

COPY --chown=appuser:appgroup . .

# Static files directory owned by app user
RUN mkdir -p staticfiles media && chown -R appuser:appgroup staticfiles media

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/health/ || exit 1

# Run DB migrations (and seed the super admin if DJANGO_SUPERUSER_* env vars are
# set) on every startup, then hand off to gunicorn. Migrate is idempotent;
# collectstatic and createsuperuser are non-fatal so a re-deploy never breaks boot.
CMD python manage.py migrate --noinput && \
    (python manage.py collectstatic --noinput || true) && \
    (python manage.py createsuperuser --noinput || true) && \
    exec gunicorn coworkhub.wsgi:application \
     --bind 0.0.0.0:8000 \
     --workers ${WEB_CONCURRENCY:-2} \
     --worker-class gthread \
     --threads 4 \
     --timeout 120 \
     --max-requests 400 \
     --max-requests-jitter 50 \
     --access-logfile - \
     --error-logfile -
