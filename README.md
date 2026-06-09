# CoWorkHub

The modern operating system for coworking spaces — manage buildings, facilities, bookings, billing, members, inventory, vendors, and community from one platform.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 5.1 + Django REST Framework, SimpleJWT auth |
| Frontend | Next.js 16 (App Router), React 19, TypeScript |
| State | Zustand (auth) + TanStack Query (server state) |
| Styling | Tailwind CSS + Radix UI |
| Database | SQLite (dev) · TiDB Cloud / MySQL (prod) |
| Cache / Queue | Redis + Celery |
| Realtime | Django Channels + Daphne (WebSocket chat) |
| Payments | Razorpay + Stripe |
| Exports | openpyxl (Excel), python-docx (Word), reportlab (PDF) |
| Deploy | Render (backend, Docker) · Vercel (frontend) |

## Features

- **Workspace** — buildings → floors → rooms → desks → parking, with occupancy tracking
- **Facilities & Bookings** — bookable rooms with an approval workflow. Internal bookings (companies that lease the building) are free and approved by the company admin; external bookings are paid and approved by the super admin
- **Billing & Payments** — GST invoices, Razorpay/Stripe checkout, webhooks
- **Inventory** — pantry, canteen, water, appliances & supplies per building, with restock/consume and low-stock alerts
- **Vendors & Bills** — suppliers and their bills/expenses per building, with a paid/pending/overdue summary
- **Exports** — download any list as Excel, Word, or PDF
- **Community & Chat** — posts, events, real-time messaging
- **Visitors, Incubation, Documents, E-Sign, Maintenance, Analytics, Notifications, AI assistant**

## Roles

| Role | Scope |
|------|-------|
| `super_admin` | Everything — all companies, buildings, platform analytics |
| `company_admin` | Their own company's data + the buildings they occupy |
| `employee` | Their own bookings and profile |

## Local Development

### Backend

```powershell
cd backend
python -m venv venv
venv\Scripts\Activate.ps1            # PowerShell; may need: Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
pip install -r requirements/development.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Celery worker (Windows uses the solo pool):

```powershell
celery -A coworkhub worker -l info --pool=solo
```

API runs at `http://localhost:8000` · Swagger docs at `/api/schema/swagger-ui/` · Django admin at `/admin/`.

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

App runs at `http://localhost:3000`. Set `frontend/.env.local`:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Quality checks

```powershell
# backend
flake8 apps/ coworkhub/ --max-line-length=120 --exclude=migrations,__pycache__ --ignore=E501,W503,E302
python manage.py check

# frontend
npm run type-check
npm run lint
npm run build
```

## Environment Variables (production)

Backend (Render):

| Key | Notes |
|-----|-------|
| `DJANGO_SETTINGS_MODULE` | `coworkhub.settings.production` |
| `SECRET_KEY` | long random string |
| `ALLOWED_HOSTS` | your `*.onrender.com` host |
| `DB_NAME` `DB_USER` `DB_PASSWORD` `DB_HOST` `DB_PORT` | TiDB Cloud |
| `REDIS_URL` `CELERY_BROKER_URL` `CELERY_RESULT_BACKEND` | Upstash Redis (`rediss://…`) |
| `BREVO_EMAIL_USER` `BREVO_API_KEY` | email (Brevo SMTP) |
| `CORS_ALLOWED_ORIGINS` | your Vercel URL |

Frontend (Vercel): `NEXT_PUBLIC_API_URL` → your Render URL.

## Deployment

1. **TiDB** — create the `coworkhub` database, then run migrations against it (`manage.py migrate --settings=coworkhub.settings.production`) so all tables exist
2. **Render** — Web Service (Docker), root directory empty, Dockerfile path `backend/Dockerfile`, build context `backend`; set the env vars above
3. **Vercel** — import the repo, root directory `frontend`, set `NEXT_PUBLIC_API_URL`
4. CI (`.github/workflows/deploy.yml`) builds the backend image and pushes to Docker Hub, then optionally triggers a Render deploy hook

## Project Structure

```
backend/
  apps/            # accounts, companies, workspace, facilities, bookings,
                   # billing, payments, inventory, vendors, chat, community,
                   # documents, esign, visitors, incubation, maintenance,
                   # analytics, notifications, ai_assistant, audit, core
  coworkhub/       # settings/, urls.py, asgi.py, wsgi.py
frontend/
  src/app/         # (marketing) (auth) (dashboard) route groups
  src/components/  # ui/ shared/ layout/
  src/lib/         # api client + services
  src/store/       # zustand auth store
  src/types/       # shared TypeScript types
```
