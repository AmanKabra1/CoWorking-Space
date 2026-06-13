---
title: CoWorkHub Backend
emoji: 🏢
colorFrom: indigo
colorTo: blue
sdk: docker
app_port: 8000
pinned: false
---

# CoWorkHub Backend

Django 5 + DRF API for CoWorkHub, deployed as a Hugging Face **Docker Space**.
The container builds from `./Dockerfile`, runs migrations on startup, and serves
gunicorn on port `8000` (declared via `app_port` above).

State lives in external SaaS, so the Space's ephemeral filesystem is fine:

- **Database:** TiDB Cloud (`DB_*` secrets)
- **Email:** Brevo SMTP (`BREVO_*` secrets)
- **AI:** Groq or Gemini (`GROQ_API_KEY` / `GOOGLE_API_KEY`)

## Required Space secrets

Set these under **Settings → Variables and secrets**:

| Key | Notes |
|-----|-------|
| `DJANGO_SETTINGS_MODULE` | `coworkhub.settings.production` |
| `SECRET_KEY` | any long random string |
| `ALLOWED_HOSTS` | `.hf.space` |
| `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST` | TiDB Cloud |
| `DB_PORT` | `4000` |
| `TIDB_SSL_CA` | `/etc/ssl/certs/ca-certificates.crt` |
| `CORS_ALLOWED_ORIGINS` | your Vercel frontend URL |
| `BREVO_EMAIL_USER`, `BREVO_API_KEY` | email |
| `GROQ_API_KEY` *(or `GOOGLE_API_KEY`)* | AI assistant |
| `DJANGO_SUPERUSER_USERNAME` / `_EMAIL` / `_PASSWORD` | optional first admin |

`REDIS_URL` is intentionally **unset** here — without it the app uses an
in-process cache and DB sessions (no Redis needed). `SECURE_SSL_REDIRECT`
defaults on; set it to `False` only if you hit a redirect loop.
