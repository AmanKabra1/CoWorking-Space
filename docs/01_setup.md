# Setup Guide — Running CoWorkHub Locally

## Prerequisites

| Tool | Version | Check |
|------|---------|-------|
| Python | 3.12+ | `python --version` |
| pip | latest | `pip --version` |
| Docker | 28+ | `docker --version` (optional for Redis) |
| Node.js | 20+ | `node --version` (Phase 9 frontend only) |

---

## 1. Clone and install

```bash
# All packages install globally — no venv needed
cd "CoWorking Space/backend"
pip install -r requirements/development.txt
```

---

## 2. Environment variables

```bash
# Copy the example file
cp .env.example .env
```

For **local development** the defaults in `.env.example` already work:
- SQLite is used automatically (no DB setup needed)
- Email is printed to the terminal console
- Redis is optional (Celery tasks are synchronous without it)

The only thing you may want to change:
```env
SECRET_KEY=any-long-random-string-here
```

---

## 3. Run migrations

```bash
python manage.py migrate
```

---

## 4. Create your Super Admin

```bash
python manage.py create_superadmin \
  --email="you@example.com" \
  --password="YourPassword123" \
  --first-name="Your" \
  --last-name="Name"
```

---

## 5. Start the server

```bash
python manage.py runserver
```

| URL | Purpose |
|-----|---------|
| `http://localhost:8000/api/docs/` | Swagger UI (interactive API explorer) |
| `http://localhost:8000/api/redoc/` | ReDoc API docs |
| `http://localhost:8000/admin/` | Django admin panel |
| `http://localhost:8000/api/schema/` | Raw OpenAPI JSON/YAML |

---

## 6. Optional: Redis + Celery (for background tasks)

If you want Celery tasks to run (email reminders, invoice generation):

**Option A — Docker (recommended):**
```bash
# From the project root
docker compose up redis -d
```

**Option B — Windows:**
Download and run Redis from https://github.com/tporadowski/redis/releases

Then start the Celery worker:
```bash
cd backend
celery -A coworkhub worker --loglevel=info
```

---

## 7. Production deployment (TiDB Cloud)

1. Set `DJANGO_SETTINGS_MODULE=coworkhub.settings.production` in your host environment
2. Fill in all DB_ and TIDB_ vars in `.env`
3. Download TiDB CA certificate and set `TIDB_SSL_CA=/path/to/isrgrootx1.pem`
4. Run `python manage.py migrate --settings=coworkhub.settings.production`
5. Run `python manage.py collectstatic --noinput`

```bash
# Production start (gunicorn)
gunicorn coworkhub.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 4 \
  --timeout 120
```

---

## Common commands

```bash
# Generate migrations after changing models
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Open Django shell
python manage.py shell

# Run with production settings locally (needs .env filled)
python manage.py runserver --settings=coworkhub.settings.production

# Check for code issues
python manage.py check
```

---

## Settings files explained

| File | When used | Database |
|------|-----------|----------|
| `coworkhub/settings/development.py` | Local dev (default) | SQLite |
| `coworkhub/settings/production.py` | Deployed (Railway/Render) | TiDB Cloud |

`base.py` contains everything shared. `development.py` and `production.py` only
override what differs (DB, caching, email, security headers).
