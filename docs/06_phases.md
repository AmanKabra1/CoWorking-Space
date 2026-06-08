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

## Phase 6 — Document Management ✅ COMPLETE
**Date:** 2026-06-08
**Scope:** Backend only

### What was built
- `apps/documents` — 2 models: `Document`, `DocumentVersion`
- `Document` — title, description, doc_type (10 types), tags (JSONField), per-company isolation, archive/restore
- `DocumentVersion` — version-controlled file uploads (v1, v2, v3…); each upload = new version
- Auto version numbering: `max(version_number) + 1` per document
- File metadata stored: original filename, size (bytes + human-readable), MIME type, uploader
- Version upload path: `documents/{company_id}/{document_id}/{filename}`
- Download endpoints: latest version or specific version, served as `FileResponse` (no redirect)
- S3 / MinIO production storage — `USE_S3=True` in `.env` activates `django-storages` S3Boto3 backend
  (works with AWS S3, MinIO, DigitalOcean Spaces, Cloudflare R2; signed 1-hour download URLs)
- Local disk storage for development — no external service required
- RBAC: Super Admin sees all; Company Admin manages own; Employee read-only
- Django admin with version inline, version count column
- 1 migration: `documents.0001_initial`

### API endpoints delivered
```
GET/POST                          /api/v1/documents/
GET/PUT/PATCH/DELETE              /api/v1/documents/{id}/
POST                              /api/v1/documents/{id}/upload-version/   multipart file upload
GET                               /api/v1/documents/{id}/versions/         list all versions
GET                               /api/v1/documents/{id}/download/         download latest version
POST                              /api/v1/documents/{id}/archive/
POST                              /api/v1/documents/{id}/restore/

GET                               /api/v1/documents/versions/              all versions (filterable)
GET                               /api/v1/documents/versions/{id}/
GET                               /api/v1/documents/versions/{id}/download/ download specific version
```

### Document types
`contract` · `lease_agreement` · `invoice` · `pitch_deck` · `meeting_notes` · `nda` · `policy` · `id_proof` · `agreement` · `other`

---

## Phase 7 — Maintenance, Visitors, Notifications ✅ COMPLETE
**Date:** 2026-06-08
**Scope:** Backend only

### What was built

#### apps/maintenance — Ticket System
- `MaintenanceTicket` model with auto-numbered tickets (`TKT-YYYY-NNNN`)
- 9 categories: electrical, plumbing, HVAC, internet, furniture, cleaning, security, elevator, other
- Priority levels: low / medium / high / critical
- State machine: `open → assigned → in_progress → resolved → closed`
- Actions: assign (Super Admin), start, resolve (with resolution notes), close

#### apps/visitors — Visitor Pass & QR Entry
- `VisitorPass` model with auto-generated 8-char unique pass code (e.g. `AB3F9D1E`)
- State machine: `scheduled → checked_in → checked_out / cancelled`
- Valid time window: `valid_from` + `valid_until` fields with validation
- `GET /api/v1/visitors/verify/{pass_code}/` — unauthenticated QR-scan endpoint
- Check-in / check-out with timestamp recording

#### apps/notifications — In-App + Email
- `Notification` model: 10 event types, `is_read`, `related_id/type` for deep links
- `create_for_user()` / `create_for_company()` class methods for bulk creation
- Brevo SMTP email via Django's `send_mail` (configured in `production.py`)
- Endpoints: list, mark-read, mark-all-read, unread-count

#### Celery Tasks (notifications/tasks.py)
| Task | Trigger | Who gets notified |
|---|---|---|
| `notify_booking_status` | booking approved/rejected/cancelled | booker |
| `notify_invoice_sent` | invoice sent | company admins |
| `notify_ticket_assigned` | ticket assigned | assignee |
| `notify_ticket_resolved` | ticket resolved | reporter |
| `notify_visitor_arrival` | visitor check-in | host |
| `check_overdue_invoices` | **daily 9 AM** (Celery Beat) | company admins |

- `django-celery-beat` + `django-celery-results` added to base requirements
- Beat schedule defined in `CELERY_BEAT_SCHEDULE` (settings/base.py)
- All tasks: `max_retries=3`, 60s backoff

### API endpoints delivered
```
GET/POST                          /api/v1/maintenance/tickets/
GET/PUT/PATCH/DELETE              /api/v1/maintenance/tickets/{id}/
POST                              /api/v1/maintenance/tickets/{id}/assign/    body: {"assigned_to": uuid}
POST                              /api/v1/maintenance/tickets/{id}/start/
POST                              /api/v1/maintenance/tickets/{id}/resolve/   body: {"resolution_notes": "..."}
POST                              /api/v1/maintenance/tickets/{id}/close/

GET/POST                          /api/v1/visitors/passes/
GET/PUT/PATCH/DELETE              /api/v1/visitors/passes/{id}/
POST                              /api/v1/visitors/passes/{id}/check-in/
POST                              /api/v1/visitors/passes/{id}/check-out/
POST                              /api/v1/visitors/passes/{id}/cancel/
GET                               /api/v1/visitors/verify/{pass_code}/        ← no auth, QR scan

GET                               /api/v1/notifications/
GET                               /api/v1/notifications/{id}/
POST                              /api/v1/notifications/{id}/mark-read/
POST                              /api/v1/notifications/mark-all-read/
GET                               /api/v1/notifications/unread-count/
```

---

## Phase 8 — Analytics, Reports, Audit Logs ✅ COMPLETE
**Date:** 2026-06-08
**Scope:** Backend only

### What was built

#### apps/analytics — Aggregated Dashboards + Report Export
- No models — purely computed from existing data via Django ORM aggregations
- `DashboardView` — KPI summary: revenue totals, booking counts by status, desk/parking occupancy rates, maintenance open/in-progress counts, platform stats (Super Admin)
- `RevenueAnalyticsView` — revenue grouped by month or day, totals, top 10 companies (Super Admin)
- `BookingAnalyticsView` — by status, top facilities, by day-of-week heatmap, avg duration
- `OccupancyView` — desk (dedicated/hot-desk) and parking (car/bike/EV) occupancy rates
- `RevenueReportView` — download PDF or Excel (`?format=pdf|excel&start=&end=`)
- `BookingReportView` — download PDF or Excel
- PDF: ReportLab styled tables with dark headers (already installed)
- Excel: openpyxl workbooks with bold headers and column widths

#### apps/audit — Immutable Audit Trail
- `AuditLog` model: 25 action types, `resource_type` + `resource_id`, IP address, JSONField extra
- DB indexes on `(action, created_at)` and `(resource_type, resource_id)` for fast lookups
- `log_action(user, action, ...)` helper in `audit/utils.py` — call from any view
- Read-only API: Super Admin sees all; Company Admin sees own company's logs
- Admin: no add/change/delete — tamper-proof
- `openpyxl==3.1.5` added to base requirements

### API endpoints delivered
```
GET   /api/v1/analytics/dashboard/                 ← role-scoped KPI summary
GET   /api/v1/analytics/revenue/?start=&end=&period=monthly|daily
GET   /api/v1/analytics/bookings/?start=&end=
GET   /api/v1/analytics/occupancy/
GET   /api/v1/analytics/reports/revenue/?format=pdf|excel&start=&end=
GET   /api/v1/analytics/reports/bookings/?format=pdf|excel&start=&end=

GET   /api/v1/audit/                               ← read-only, filterable
GET   /api/v1/audit/{id}/
```

### Audit actions tracked (25 types)
`user_login` · `user_logout` · `user_created` · `booking_created` · `booking_approved` · `booking_rejected` · `booking_cancelled` · `invoice_created` · `invoice_sent` · `payment_recorded` · `document_uploaded` · `maintenance_created` · `maintenance_resolved` · `company_created` · `company_status_changed` · `visitor_checked_in` · `application_submitted` · `application_accepted` · _(+7 more)_

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
