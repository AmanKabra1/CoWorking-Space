# Tech Stack, Architecture & Interview Reference — CoWorkHub

This document covers every technology, design decision, and pattern used in CoWorkHub.
Read this before an interview or technical discussion.

---

## 1. What is CoWorkHub?

**CoWorkHub** is a production-ready, multi-tenant SaaS platform for coworking space and facility management.

**Core capabilities:**
- Multi-company workspace management (buildings, floors, desks, parking)
- Facility booking with approval workflow
- GST-compliant invoicing with UPI QR code PDF generation
- Role-based access control (Super Admin / Company Admin / Employee)
- AI assistant powered by Google Gemini (free tier)
- CI/CD pipeline with GitHub Actions → Docker Hub → Render

**Built by:** Sanchi Connect

---

## 2. Full Tech Stack

### Backend
| Technology | Version | Role |
|---|---|---|
| **Python** | 3.12 | Runtime |
| **Django** | 5.1.4 | Web framework |
| **Django REST Framework** | 3.15.2 | REST API layer |
| **djangorestframework-simplejwt** | 5.3.1 | JWT authentication |
| **drf-spectacular** | 0.27.2 | OpenAPI 3 / Swagger docs |
| **django-filter** | 24.3 | Querystring filtering |
| **django-cors-headers** | 4.4.0 | CORS for frontend |
| **Whitenoise** | 6.7.0 | Static file serving (no CDN needed in prod) |

### Database
| Technology | Role |
|---|---|
| **TiDB Cloud** | Production — MySQL-compatible, horizontally scalable, serverless |
| **SQLite** | Development — zero-config local DB |
| **mysqlclient** | Python → MySQL/TiDB driver |

### Background Tasks
| Technology | Version | Role |
|---|---|---|
| **Celery** | 5.4.0 | Distributed task queue |
| **Redis** | 7 (via redis-py 5.2.1) | Message broker + result backend |
| **django-celery-beat** | 2.7.0 | Cron-like periodic tasks via DB scheduler |
| **django-celery-results** | 2.5.1 | Store task results in DB |

### AI
| Technology | Version | Role |
|---|---|---|
| **Google Gemini 1.5 Flash** | via google-generativeai 0.8.3 | AI assistant (free tier) |
| **RAG-lite pattern** | — | Live DB context injected into every prompt — no vector DB needed |

### PDF & QR
| Technology | Version | Role |
|---|---|---|
| **ReportLab** | 4.5.1 | GST-compliant PDF invoice generation |
| **qrcode** | 8.2 | UPI QR code embedded in invoices |
| **Pillow** | 11.0.0 | Image processing (avatars, facility images) |

### Deployment & Infrastructure
| Technology | Role |
|---|---|
| **Docker** | Container runtime |
| **Docker Compose** | Multi-service orchestration (dev + prod) |
| **Gunicorn** | WSGI server (4 workers × 2 gthreads in prod) |
| **Nginx** | Reverse proxy, static file serving, SSL termination |
| **Render** | Cloud PaaS deployment (web + Celery workers + Redis) |
| **GitHub Actions** | CI/CD pipeline |
| **Docker Hub** | Container registry |

### Email
| Technology | Role |
|---|---|
| **Brevo** (formerly Sendinblue) | SMTP email — booking confirmations, invoice delivery |

### Frontend (Phase 9 — planned)
| Technology | Role |
|---|---|
| **Next.js 15** | React framework with App Router |
| **TypeScript** | Type safety |
| **Tailwind CSS** | Utility-first styling |
| **shadcn/ui** | Accessible component library |
| **TanStack Query** | Server state management + caching |

---

## 3. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Client Layer                             │
│  Browser / Mobile / Swagger UI  ← JWT Bearer token             │
└────────────────────────┬────────────────────────────────────────┘
                         │ HTTPS
┌────────────────────────▼────────────────────────────────────────┐
│                     Nginx (reverse proxy)                        │
│  Static files served directly · Proxy /api/* → Gunicorn         │
└────────────────────────┬────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────┐
│              Django 5.1 + DRF 3.15 (Gunicorn)                   │
│                                                                  │
│  apps/core          — TimeStampedModel, health check            │
│  apps/accounts      — Custom User, JWT, RBAC                    │
│  apps/companies     — Tenant (Company) model                    │
│  apps/workspace     — Building, Floor, Room, Desk, Parking      │
│  apps/facilities    — Facility, FacilityImage                   │
│  apps/bookings      — Booking approval workflow                 │
│  apps/billing       — Invoice, Payment, PDF, UPI QR             │
│  apps/ai_assistant  — Gemini chat, suggestions, insights        │
└────────┬───────────────┬──────────────────┬─────────────────────┘
         │               │                  │
┌────────▼──────┐  ┌─────▼──────┐  ┌───────▼──────────┐
│  TiDB Cloud   │  │   Redis    │  │  Google Gemini   │
│  (MySQL prod) │  │  (broker + │  │  1.5 Flash (AI)  │
│  SQLite (dev) │  │   cache)   │  │  Free API        │
└───────────────┘  └─────┬──────┘  └──────────────────┘
                         │
              ┌──────────▼──────────┐
              │   Celery Workers    │
              │  + Celery Beat      │
              │  (background tasks) │
              └─────────────────────┘
```

---

## 4. API Design

- **Versioned:** All endpoints under `/api/v1/`
- **Auth:** JWT Bearer token in `Authorization` header
- **Pagination:** Page-based (`?page=2`), 20 items/page default
- **Filtering:** `?status=pending&booking_date=2026-07-01`
- **Search:** `?search=<text>` via DRF SearchFilter
- **Ordering:** `?ordering=-created_at`
- **Docs:** Swagger UI at `/api/docs/` · ReDoc at `/api/redoc/`
- **OpenAPI schema:** `/api/schema/` (download JSON/YAML)
- **Health check:** `GET /api/health/` — no auth, probes DB + Redis

### All API endpoints

```
/api/health/                         — liveness probe

/api/v1/auth/register/               POST
/api/v1/auth/login/                  POST  → access + refresh tokens
/api/v1/auth/logout/                 POST  → blacklist refresh token
/api/v1/auth/token/refresh/          POST
/api/v1/auth/me/                     GET, PATCH
/api/v1/auth/change-password/        POST
/api/v1/auth/users/                  GET, POST (Super Admin)
/api/v1/auth/users/{id}/             GET, PATCH, DELETE

/api/v1/companies/                   GET, POST
/api/v1/companies/{id}/              GET, PUT, PATCH, DELETE
/api/v1/companies/{id}/employees/    GET
/api/v1/companies/{id}/invite-employee/  POST
/api/v1/companies/{id}/status/       PATCH

/api/v1/workspace/buildings/         GET, POST
/api/v1/workspace/buildings/{id}/    GET, PUT, PATCH, DELETE
/api/v1/workspace/buildings/{id}/floors/    GET
/api/v1/workspace/buildings/{id}/occupancy/ GET
/api/v1/workspace/buildings/{id}/parking/   GET
/api/v1/workspace/floors/            GET, POST
/api/v1/workspace/floors/{id}/       GET, PUT, PATCH, DELETE
/api/v1/workspace/floors/{id}/rooms/ GET
/api/v1/workspace/rooms/             GET, POST
/api/v1/workspace/rooms/{id}/        GET, PUT, PATCH, DELETE
/api/v1/workspace/rooms/{id}/desks/  GET
/api/v1/workspace/desks/             GET, POST
/api/v1/workspace/desks/{id}/        GET, PUT, PATCH, DELETE
/api/v1/workspace/desks/{id}/assign/   POST
/api/v1/workspace/desks/{id}/unassign/ POST
/api/v1/workspace/parking-slots/     GET, POST
/api/v1/workspace/parking-slots/{id}/           GET, PUT, PATCH, DELETE
/api/v1/workspace/parking-slots/{id}/assign/    POST
/api/v1/workspace/parking-slots/{id}/unassign/  POST

/api/v1/facilities/                  GET, POST
/api/v1/facilities/{id}/             GET, PUT, PATCH, DELETE
/api/v1/facilities/{id}/availability/?date=YYYY-MM-DD  GET

/api/v1/bookings/                    GET, POST
/api/v1/bookings/{id}/               GET, PUT, PATCH, DELETE
/api/v1/bookings/{id}/approve/       POST  (Super Admin)
/api/v1/bookings/{id}/reject/        POST  (Super Admin)
/api/v1/bookings/{id}/cancel/        POST  (Company Admin / Super Admin)
/api/v1/bookings/{id}/complete/      POST  (Super Admin)
/api/v1/bookings/pending-queue/      GET   (Super Admin)
/api/v1/bookings/calendar/?start=&end=   GET

/api/v1/billing/invoices/            GET, POST
/api/v1/billing/invoices/{id}/       GET, PUT, PATCH, DELETE
/api/v1/billing/invoices/{id}/send/          POST
/api/v1/billing/invoices/{id}/record-payment/ POST
/api/v1/billing/invoices/{id}/mark-overdue/  POST
/api/v1/billing/invoices/{id}/cancel/        POST
/api/v1/billing/invoices/{id}/download-pdf/  GET  → PDF stream
/api/v1/billing/invoices/generate-monthly/   POST
/api/v1/billing/payments/            GET
/api/v1/billing/payments/{id}/       GET

/api/v1/ai/chat/                     POST  — multi-turn AI assistant
/api/v1/ai/booking-suggestions/      POST  — AI slot recommendations
/api/v1/ai/insights/                 POST  — AI analytics narrative
/api/v1/ai/smart-search/             POST  — NL → filter translation
/api/v1/ai/conversations/            GET   — chat history
```

---

## 5. RBAC — Role-Based Access Control

Three roles stored as `CharField` on the User model:

| Role | What they can do |
|---|---|
| `super_admin` | Full access to everything — manage companies, approve bookings, generate invoices, view all data |
| `company_admin` | Manage their company's bookings, employees, view invoices for their company |
| `employee` | Book facilities, view own bookings and company facilities |

**Implementation:**
- Custom `User.role` CharField with choices
- `is_super_admin`, `is_company_admin`, `is_employee_role` properties on User
- `IsSuperAdmin`, `IsSuperAdminOrCompanyAdmin`, `IsOwnerOrSuperAdmin` DRF permission classes
- **Tenant isolation:** Every ViewSet's `get_queryset()` filters by `request.user.company_id` — company admins and employees can only see their own company's data

---

## 6. Authentication Flow

```
POST /api/v1/auth/login/   {"email": "...", "password": "..."}
   ↓
   Returns: {"access": "JWT...", "refresh": "JWT..."}

Every request: Authorization: Bearer <access_token>

JWT payload includes: user_id, role, email, full_name (custom claims)
Access token TTL: 60 minutes
Refresh token TTL: 7 days (rotated + blacklisted on use)
```

Token blacklisting is enabled — logout invalidates the refresh token in the DB.

---

## 7. AI Assistant — How It Works

**Model:** Google Gemini 1.5 Flash  
**Free tier:** 15 requests/minute · 1M tokens/minute · 1,500 requests/day  
**No billing required** for free tier — just a Google account API key  

**Architecture pattern: RAG-lite (Retrieval-Augmented Generation without vector DB)**

```
User message
    ↓
Build system prompt (role, company, date)
    ↓
Fetch live DB context (recent bookings, invoices, facilities)   ← RAG step
    ↓
Enrich message with context + send to Gemini 1.5 Flash
    ↓
Save [user, model] messages to AIConversation (session history)
    ↓
Return reply + session_id (for multi-turn continuation)
```

**Four AI endpoints:**

| Endpoint | Input | Output |
|---|---|---|
| `POST /ai/chat/` | Free-text message + optional session_id | Contextual reply |
| `POST /ai/booking-suggestions/` | facility_id + date | 3-5 time slots with cost + reasoning |
| `POST /ai/insights/` | insight_type (bookings/invoices/facilities) + date range | Executive summary in plain English |
| `POST /ai/smart-search/` | Natural language query + resource type | Structured API filter params |

**Smart search example:**
```json
POST /api/v1/ai/smart-search/
{"query": "show me rejected bookings from last week", "resource": "bookings"}

Response:
{"filters": {"status": "rejected", "booking_date__gte": "2026-06-01"}, 
 "usage_hint": "Apply these filters to GET /api/v1/bookings/"}
```

---

## 8. Data Model Relationships

```
Company ──< User (employees)
         ──< Booking ──> Facility ──> Building ──> Floor
         ──< Invoice ──< Payment
         ──< AIConversation

Building ──< Floor ──< Room ──< Desk ──> Company (assigned)
          ──< ParkingSlot ──> Company (assigned)
          ──< Facility

User ──> Company (belongs to, nullable for Super Admin)
     ──< Booking (booked_by)
     ──< Booking (approved_by)
     ──< AIConversation
```

**Design decisions:**
- **UUID primary keys** on all models — prevents ID enumeration attacks
- **TimeStampedModel** abstract base — `created_at`, `updated_at` on every model
- **JSONField** for Facility.amenities, Facility.booking_rules, Invoice.line_items — flexible schema, no extra tables
- **PROTECT** on critical FKs (facility, company on bookings) — prevents accidental cascade deletes

---

## 9. CI/CD Pipeline

```
Developer pushes code
        ↓
GitHub Actions: CI (ci.yml) — runs on every push/PR
  ├─ Python 3.12 setup
  ├─ pip install (cached by requirements hash)
  ├─ manage.py check
  ├─ manage.py migrate --check   ← blocks PR if migrations missing
  └─ flake8 lint
        ↓ (if merged to main)
GitHub Actions: CD (deploy.yml)
  ├─ Docker multi-stage build (layer-cached via GHA cache)
  ├─ Push image to Docker Hub
  └─ Trigger Render deploy webhook
        ↓
Render pulls new image → rolling restart → health check at /api/health/
```

**Required GitHub Secrets:**
- `DOCKERHUB_USERNAME` + `DOCKERHUB_TOKEN`
- `RENDER_DEPLOY_HOOK_URL` (from Render service settings)

---

## 10. Deployment Architecture (Render)

Defined in `render.yaml` (Blueprint):

```
Render Services:
  ┌────────────────────────────────┐
  │  coworkhub-backend (Web)       │  ← Django + Gunicorn
  │  healthCheckPath: /api/health/ │
  └────────────────────────────────┘
  ┌────────────────────────────────┐
  │  coworkhub-celery-worker       │  ← Celery worker
  │  (Worker service)              │
  └────────────────────────────────┘
  ┌────────────────────────────────┐
  │  coworkhub-celery-beat         │  ← Celery beat scheduler
  │  (Worker service)              │
  └────────────────────────────────┘
  ┌────────────────────────────────┐
  │  coworkhub-redis (Redis)       │  ← Broker + cache + sessions
  └────────────────────────────────┘

External:
  TiDB Cloud (MySQL) ← Production database (serverless, auto-scaling)
  Google Gemini API  ← AI (free tier)
  Brevo SMTP         ← Transactional email
```

---

## 11. VPS Deployment (Alternative)

```bash
# 1. Clone repo on your VPS
git clone https://github.com/Amank-sc/coworkhub.git
cd coworkhub

# 2. Create production env file
cp backend/.env.example backend/.env.production
# Edit .env.production with real credentials

# 3. Start all services
docker compose -f docker-compose.prod.yml up -d

# 4. Run initial migrations
docker compose -f docker-compose.prod.yml exec backend python manage.py migrate
docker compose -f docker-compose.prod.yml exec backend python manage.py create_superadmin
```

---

## 12. Booking State Machine

```
                    ┌─────────┐
  CREATE ──────────>│ PENDING │
                    └────┬────┘
                         │
              ┌──────────┴──────────┐
              │ Super Admin action  │
              ▼                     ▼
         ┌──────────┐        ┌──────────┐
         │ APPROVED │        │ REJECTED │
         └────┬─────┘        └──────────┘
              │
     ┌────────┴────────┐
     ▼                 ▼
┌───────────┐   ┌───────────┐
│ COMPLETED │   │ CANCELLED │
└───────────┘   └───────────┘
```

---

## 13. Invoice State Machine

```
CREATE ──> DRAFT ──> SENT ──> PAID
                      │
                      └──> OVERDUE ──> (manual collection)
DRAFT/SENT ──> CANCELLED
```

Auto-transition: When `total_paid >= total_amount`, invoice status → PAID automatically.

---

## 14. Key Design Patterns Used

| Pattern | Where used | Why |
|---|---|---|
| **Multi-tenancy** | Every ViewSet `get_queryset()` | Data isolation between companies |
| **State machine** | Booking, Invoice status | Clear lifecycle, prevents invalid transitions |
| **Strategy pattern** | GST calculation (CGST/SGST vs IGST) | Flexible tax computation |
| **RAG-lite** | AI assistant | Ground AI responses in real data without vector DB |
| **Repository pattern** | Serializer's `create()`/`update()` | Business logic out of views |
| **Observer pattern** | Celery tasks | Async side effects (email, PDF generation) |
| **Circuit breaker** | AI service `try/except → 503` | Degrade gracefully when Gemini is unavailable |

---

## 15. Security Measures

| Measure | Implementation |
|---|---|
| JWT + blacklisting | Token invalidated on logout; refresh tokens rotated |
| UUID PKs | Prevents ID enumeration on all models |
| Tenant isolation | QuerySet filtering — no cross-company data leakage |
| HTTPS enforced | `SECURE_SSL_REDIRECT = True` in production |
| HSTS | `SECURE_HSTS_SECONDS = 31536000` |
| CSRF protection | Enabled (cookies `Secure + SameSite`) |
| Rate limiting | 30 req/min (anon), 200 req/min (authenticated) via DRF throttling |
| Non-root Docker | Container runs as `appuser` (uid 1001) |
| PROTECT FK | Critical relations use `on_delete=PROTECT` — no silent cascades |
| `.env` never committed | `.gitignore` excludes all `.env*` files |

---

## 16. Common Interview Questions

**Q: Why Django over FastAPI?**  
A: Django gives us ORM, Admin, migrations, auth, RBAC, and Celery integration out of the box. FastAPI would require building all of that from scratch. DRF gives DRF everything FastAPI has for REST with less boilerplate for CRUD-heavy apps.

**Q: Why TiDB Cloud?**  
A: It's MySQL-compatible (no Django driver changes), horizontally scalable, has a serverless free tier, and handles high-write workloads with HTAP (Hybrid Transactional and Analytical Processing). We use SQLite locally for zero-config dev.

**Q: How does multi-tenancy work?**  
A: Every model has a `company` FK. Every ViewSet overrides `get_queryset()` to filter by `request.user.company_id`. Super Admins bypass this filter. No company ever touches another company's data.

**Q: How is the AI implemented without a vector database?**  
A: RAG-lite — we fetch structured data from the DB (recent bookings, invoices, facilities) and inject it as text into every Gemini prompt. For this data scale it's cheaper and faster than maintaining embeddings. We'd add a vector DB (Pinecone / pgvector) when document search becomes a requirement.

**Q: How do you handle background tasks?**  
A: Celery workers consume tasks from a Redis queue. Celery Beat handles periodic tasks (monthly invoice generation, overdue detection) using `django-celery-beat`'s DB scheduler so schedules can be changed without redeploying.

**Q: What happens if the AI API is down?**  
A: Every AI view wraps the service call in a `try/except` and returns HTTP 503 with a clear error message. The rest of the application continues working normally — AI is additive, not critical path.

**Q: Walk me through a booking creation.**  
A: `POST /api/v1/bookings/` → `CanCreateBooking` permission (must be linked to a company) → `CreateBookingSerializer.validate()` checks: facility active, end > start, not in past, attendees ≤ capacity, no overlapping PENDING/APPROVED booking → `create()` computes duration + amount (price_per_day if ≥ 8h, else hourly × duration) → `Booking` saved with `status=PENDING` → Super Admin sees it in `pending-queue/` → approves → Company Admin can now cancel or it completes.

**Q: How is the PDF generated?**  
A: `ReportLab` builds an A4 `SimpleDocTemplate` with `Platypus` flowables (Table for line items, Paragraph for headers/totals). A UPI QR code is generated via the `qrcode` library and embedded as an image. The PDF is written to a `BytesIO` buffer and returned as a `FileResponse` stream — no disk write needed.

---

## 17. Getting Started (for new developers)

```bash
# 1. Clone
git clone https://github.com/Amank-sc/coworkhub.git
cd "CoWorking Space"

# 2. Install dependencies (no venv — global install)
pip install -r backend/requirements/development.txt

# 3. Create .env file
cp backend/.env.example backend/.env
# Get a free Gemini API key: https://aistudio.google.com/app/apikey
# Add GEMINI_API_KEY to backend/.env

# 4. Run migrations + create super admin
cd backend
python manage.py migrate
python manage.py create_superadmin

# 5. Start dev server
python manage.py runserver

# 6. Open Swagger docs
# http://localhost:8000/api/docs/
```

**Or with Docker:**
```bash
cd "CoWorking Space"
docker compose up -d
```
