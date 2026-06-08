# Build Phases — CoWorkHub

This file is updated at the start and end of every phase.
New developers: read this first to understand where the project is and what's next.

---

## Phase Status Legend

| Symbol | Meaning |
|--------|---------|
| ✅ | Complete — built, migrated, tested |
| 🔄 | In Progress |
| 🔜 | Planned — not started |
| ⏸ | Paused |

---

## Phase 1 — Foundation + Auth + Company ✅ COMPLETE
**Date:** 2026-06-08
**Scope:** Backend only

### What was built
- Django 5.1 + DRF 3.15 project scaffold
- Split settings: `development.py` (SQLite) and `production.py` (TiDB Cloud)
- Docker Compose setup (backend + Redis + Celery worker + Celery beat)
- Dockerfile for production container
- Celery app skeleton (workers ready, no tasks yet)
- `apps/core` — `TimeStampedModel` abstract base (UUID PK, timestamps)
- `apps/accounts` — Custom `User` model, RBAC (3 roles), JWT auth
- `apps/companies` — `Company` tenant model, CRUD API, employee management
- OpenAPI / Swagger docs at `/api/docs/`
- Django admin panel configured for both models
- `create_superadmin` management command

### API endpoints delivered
```
POST   /api/v1/auth/register/
POST   /api/v1/auth/login/
POST   /api/v1/auth/logout/
POST   /api/v1/auth/token/refresh/
GET    /api/v1/auth/me/
PATCH  /api/v1/auth/me/
POST   /api/v1/auth/change-password/
GET    /api/v1/auth/users/
GET    /api/v1/auth/users/{id}/
PATCH  /api/v1/auth/users/{id}/
DELETE /api/v1/auth/users/{id}/

GET    /api/v1/companies/
POST   /api/v1/companies/
GET    /api/v1/companies/{id}/
PUT    /api/v1/companies/{id}/
PATCH  /api/v1/companies/{id}/
DELETE /api/v1/companies/{id}/
GET    /api/v1/companies/{id}/employees/
POST   /api/v1/companies/{id}/invite-employee/
PATCH  /api/v1/companies/{id}/status/
```

### How to test
```bash
cd backend
python manage.py runserver
# Open http://localhost:8000/api/docs/
```

---

## Phase 2 — Workspace Management ✅ COMPLETE
**Date:** 2026-06-08
**Scope:** Backend only

### What was built
- `apps/workspace` Django app — 5 models, full REST API
- `Building` — physical buildings with occupancy stats
- `Floor` — floors within a building (unique floor_number per building)
- `Room` — rooms/cabins on a floor (cabin, open_space, meeting_room, event_hall, storage)
- `Desk` — individual desks (dedicated or hot_desk), assignable to companies
- `ParkingSlot` — car/bike/EV slots per building, assignable to companies
- Permission: Super Admin full CRUD; Company Admin / Employee read-only
- Occupancy report API: building → per-floor breakdown (total/occupied/available/rate %)
- Django admin with inline desks inside rooms

### API endpoints delivered
```
GET/POST   /api/v1/workspace/buildings/
GET/PUT/PATCH/DELETE /api/v1/workspace/buildings/{id}/
GET        /api/v1/workspace/buildings/{id}/floors/
GET        /api/v1/workspace/buildings/{id}/occupancy/
GET        /api/v1/workspace/buildings/{id}/parking/

GET/POST   /api/v1/workspace/floors/
GET/PUT/PATCH/DELETE /api/v1/workspace/floors/{id}/
GET        /api/v1/workspace/floors/{id}/rooms/

GET/POST   /api/v1/workspace/rooms/
GET/PUT/PATCH/DELETE /api/v1/workspace/rooms/{id}/
GET        /api/v1/workspace/rooms/{id}/desks/

GET/POST   /api/v1/workspace/desks/
GET/PUT/PATCH/DELETE /api/v1/workspace/desks/{id}/
POST       /api/v1/workspace/desks/{id}/assign/
POST       /api/v1/workspace/desks/{id}/unassign/

GET/POST   /api/v1/workspace/parking-slots/
GET/PUT/PATCH/DELETE /api/v1/workspace/parking-slots/{id}/
POST       /api/v1/workspace/parking-slots/{id}/assign/
POST       /api/v1/workspace/parking-slots/{id}/unassign/
```

---

## Phase 3 — Facility Booking ✅ COMPLETE
**Date:** 2026-06-08
**Scope:** Backend only

### What was built
- `apps/facilities` — Facility model (conference_room, meeting_room, event_hall, podcast_studio, printing_room, 3d_printer, cafeteria, other)
- `FacilityImage` — multiple images per facility with primary-image flag and ordering
- `apps/bookings` — Booking model with full approval workflow
- Booking states: `pending → approved / rejected → cancelled / completed`
- Automatic duration + amount calculation (price_per_day if ≥ 8 hours, otherwise price_per_hour × duration)
- Overlap / conflict detection on booking creation (validated in serializer)
- Calendar API: bookings for a facility within a date range (excludes cancelled/rejected by default)
- Availability check API: shows booked slots for a facility on a specific date
- Super Admin approval queue API (pending bookings ordered by date/time)
- Permission model: Super Admin approves/rejects/completes; Company Admin cancels own bookings
- Django admin with approve/reject bulk actions
- 2 migrations: `facilities.0001_initial`, `bookings.0001_initial`, `bookings.0002_initial` (FK dependency resolved automatically)

### API endpoints delivered
```
GET/POST                 /api/v1/facilities/
GET/PUT/PATCH/DELETE     /api/v1/facilities/{id}/
GET                      /api/v1/facilities/{id}/availability/?date=YYYY-MM-DD

GET/POST                 /api/v1/bookings/
GET/PUT/PATCH/DELETE     /api/v1/bookings/{id}/
POST                     /api/v1/bookings/{id}/approve/
POST                     /api/v1/bookings/{id}/reject/        body: {"reason": "..."}
POST                     /api/v1/bookings/{id}/cancel/
POST                     /api/v1/bookings/{id}/complete/
GET                      /api/v1/bookings/pending-queue/
GET                      /api/v1/bookings/calendar/?start=YYYY-MM-DD&end=YYYY-MM-DD[&facility=UUID]
```

---

## Phase 4 — Billing & Invoices ✅ COMPLETE
**Date:** 2026-06-08
**Scope:** Backend only

### What was built
- `apps/billing` — `Invoice` and `Payment` models
- Invoice status machine: `draft → sent → paid / overdue / cancelled`
- Sequential invoice numbering: `INV-YYYY-MM-NNNN` (auto-generated)
- GST calculation: CGST + SGST (intra-state) or IGST (inter-state), rates stored per invoice
- `compute_totals()` — recalculates GST amounts + total from subtotal + rates on create/update
- PDF invoice generation with ReportLab — GST-compliant A4 layout, header, line items table, totals
- Dynamic UPI QR code embedded in PDF (using `qrcode` library, pay via UPI ID)
- Payment recording with partial payment support, auto-transition to PAID on full coverage
- `generate_monthly` action — auto-creates draft invoices for all active companies, pulling:
  - Dedicated desks (monthly_rate × qty)
  - Parking slots (monthly_rate × qty)
  - Completed facility bookings (total_amount per booking)
- Skips companies with no billable items, skips duplicate periods
- Payment history with `amount_paid` and `amount_due` computed fields on InvoiceSerializer
- Django admin with inline payments, status badge colouring
- Dependencies added: `reportlab==4.5.1`, `qrcode==8.2`

### API endpoints delivered
```
GET/POST                        /api/v1/billing/invoices/
GET/PUT/PATCH/DELETE            /api/v1/billing/invoices/{id}/
POST                            /api/v1/billing/invoices/{id}/send/
POST                            /api/v1/billing/invoices/{id}/record-payment/
POST                            /api/v1/billing/invoices/{id}/mark-overdue/
POST                            /api/v1/billing/invoices/{id}/cancel/
GET                             /api/v1/billing/invoices/{id}/download-pdf/
POST                            /api/v1/billing/invoices/generate-monthly/   body: {"year":2026,"month":7}

GET                             /api/v1/billing/payments/
GET                             /api/v1/billing/payments/{id}/
```

---

## Phase 5 — Startup Incubation ✅ COMPLETE
**Date:** 2026-06-08
**Scope:** Backend only

### What was built
- `apps/incubation` — 4 models: `StartupProfile`, `IncubationApplication`, `ApplicationNote`, `FundingRound`
- `StartupProfile` — one per company: industry, stage, team size, logo, pitch deck upload, business plan upload
- `IncubationApplication` — apply per cohort (e.g. 2026-Q1); problem statement, solution, market size, traction, funding ask
- Application review workflow: `draft → submitted → under_review → accepted / rejected / withdrawn`
- `ApplicationNote` — internal (Super Admin only) and public notes on any application
- `FundingRound` — track funding rounds (pre-seed, seed, Series A…) per startup, with amount sought vs raised
- RBAC: Company Admin manages own startup; Super Admin reviews all applications
- File uploads: pitch deck + business plan stored in `MEDIA_ROOT/incubation/` (S3/MinIO-ready via django-storages)
- Django admin with bulk accept/reject/review actions, note inline
- 1 migration: `incubation.0001_initial`

### API endpoints delivered
```
GET/POST                       /api/v1/incubation/profiles/
GET/PUT/PATCH/DELETE           /api/v1/incubation/profiles/{id}/

GET/POST                       /api/v1/incubation/applications/
GET/PUT/PATCH/DELETE           /api/v1/incubation/applications/{id}/
POST                           /api/v1/incubation/applications/{id}/submit/
POST                           /api/v1/incubation/applications/{id}/review/      (Super Admin)
POST                           /api/v1/incubation/applications/{id}/accept/      (Super Admin)
POST                           /api/v1/incubation/applications/{id}/reject/      body: {"reason": "..."}
POST                           /api/v1/incubation/applications/{id}/withdraw/
GET                            /api/v1/incubation/applications/{id}/notes/
POST                           /api/v1/incubation/applications/{id}/notes/add/

GET/POST                       /api/v1/incubation/funding/
GET/PUT/PATCH/DELETE           /api/v1/incubation/funding/{id}/
```

### Application state machine
```
CREATE ──> DRAFT ──> SUBMITTED ──> UNDER_REVIEW ──> ACCEPTED
                │                              └──> REJECTED
                └──> WITHDRAWN (from DRAFT or SUBMITTED)
```

---

## Phase 6 — Document Management 🔜
**Scope:** Backend only

### What will be built
- `apps/documents` — `Document`, `DocumentVersion` models
- MinIO integration for file storage (S3-compatible)
- Version control: each upload creates a new version
- Tags, search, per-company isolation
- Document types: contract, lease agreement, invoice, pitch deck, meeting notes

---

## Phase 7 — Maintenance, Visitors, Notifications 🔜
**Scope:** Backend only

### What will be built
- `apps/maintenance` — ticket system (create → assign → in progress → resolved)
- `apps/visitors` — visitor pass, QR entry, check-in/out log
- `apps/notifications` — in-app + email notification system
- Brevo email integration: booking confirmations, reminders, contract expiry alerts
- Celery beat tasks for scheduled reminders

---

## Phase 8 — Analytics, Reports, Audit Logs 🔜
**Scope:** Backend only

### What will be built
- `apps/analytics` — aggregated dashboards (revenue, occupancy, facility usage)
- Report export: PDF (ReportLab) and Excel (openpyxl)
- `apps/audit` — `AuditLog` model tracking every significant action
  (login, booking, approval, payment, document upload)

---

## Phase 9 — Frontend (Next.js) 🔜
**Scope:** Frontend only

### What will be built
- Next.js 15 + TypeScript project in `frontend/`
- Tailwind CSS + shadcn/ui component library
- TanStack Query for server state management
- Three role-based layouts: Super Admin / Company Admin / Employee
- Pages for every backend module built in Phases 1–8
- JWT auth with token refresh logic
- Responsive, mobile-first design

### Pages planned
```
/login
/dashboard (role-based redirect)
/companies            (Super Admin)
/companies/[id]
/workspace/buildings
/workspace/floors/[id]
/facilities
/bookings
/bookings/[id]
/invoices
/invoices/[id]
/incubation
/documents
/maintenance
/visitors
/reports
/settings/profile
/settings/users
```

---

## Phase 10 — Advanced Features 🔜
**Scope:** Full stack

### What will be built
- Real-time notifications via Django Channels + WebSockets
- Internal chat (real-time messaging between users in the same company)
- Community module: events, meetups, startup showcase, discussion board
- AI assistant: document search, invoice lookup, report generation
  (using Claude API or OpenAI API)
- Digital agreement e-signing (PDF signature + OTP verification)

---

## Files modified per phase

| Phase | New apps | New migrations | New API endpoints |
|-------|----------|---------------|-------------------|
| 1 | core, accounts, companies | 2 | 22 |
| 2 | workspace | +1 | ~10 |
| 3 | facilities, bookings | +2 | ~12 |
| 4 | billing | +1 | ~8 |
| 5 | incubation | +1 | ~6 |
| 6 | documents | +1 | ~8 |
| 7 | maintenance, visitors, notifications | +3 | ~14 |
| 8 | analytics, audit | +2 | ~10 |
| 9 | — (frontend only) | 0 | 0 |
| 10 | community, chat | +2 | ~8 |
