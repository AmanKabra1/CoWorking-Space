# CoWorkHub — Platform Overview

> Smart Coworking Space & Facility Management Platform  
> Built for **Sanchi Connect** — production SaaS, multi-tenant, India-ready

---

## What is CoWorkHub?

CoWorkHub is a full-stack SaaS platform that manages every moving part of a coworking
space: tenant companies, workspace seats, facility bookings, monthly billing, startup
incubation, maintenance, visitor management, and more.

It is built for real coworking businesses (starting with Sanchi Connect) and is designed
from day one to be multi-tenant — meaning multiple companies can be onboarded as tenants,
each isolated from the other.

---

## The Three Users

```
Super Admin  ──────────────────────────────────────────────────────────────
  (Building   Full control. Manages companies, workspaces, facilities,
   Owner)     billing, reports, all settings. One or more per platform.

Company Admin ─────────────────────────────────────────────────────────────
  (Tenant     Rep from a startup / company that rents space. Manages
   Rep)       their own employees, books facilities, pays invoices,
              uploads startup documents, submits maintenance requests.

Employee ──────────────────────────────────────────────────────────────────
  (Staff)     Individual users under a company. Can book approved
              facilities, access documents, receive notifications,
              submit requests.
```

---

## Full Module Map

| # | Module | Description | Phase |
|---|--------|-------------|-------|
| 1 | Auth & RBAC | JWT login, 3 roles, user management | ✅ Phase 1 |
| 2 | Company / Tenant | Onboarding, GST, contract, employee mgmt | ✅ Phase 1 |
| 3 | Workspace | Buildings, floors, rooms, desks, cabins, parking | 🔜 Phase 2 |
| 4 | Facility Management | Conference rooms, studios, 3D printers, cafeteria | 🔜 Phase 3 |
| 5 | Facility Booking | Request → Approve → Pay → Confirm workflow | 🔜 Phase 3 |
| 6 | Calendar | Day/week/month view for bookings and maintenance | 🔜 Phase 3 |
| 7 | Billing & Invoices | Monthly automated billing, GST, PDF invoices | 🔜 Phase 4 |
| 8 | Payments | UPI QR (PhonePe/GPay/Paytm), transaction tracking | 🔜 Phase 4 |
| 9 | Startup Incubation | Pitch deck, funding requests, mentor/investor notes | 🔜 Phase 5 |
| 10 | Document Management | Version-controlled file storage (MinIO), contracts | 🔜 Phase 6 |
| 11 | Maintenance / Helpdesk | Tickets, assignment, resolution workflow | 🔜 Phase 7 |
| 12 | Visitor Management | Visitor pass, QR entry, check-in/out logs | 🔜 Phase 7 |
| 13 | Email Automation | Brevo-powered transactional emails, reminders | 🔜 Phase 7 |
| 14 | Notifications | In-app + email + SMS (optional) | 🔜 Phase 7 |
| 15 | Dashboard Analytics | Revenue, occupancy, usage charts | 🔜 Phase 8 |
| 16 | Reports | PDF/Excel export — revenue, occupancy, maintenance | 🔜 Phase 8 |
| 17 | Audit Logs | Every action tracked with user + timestamp | 🔜 Phase 8 |
| 18 | Frontend (Next.js) | Role-based dashboards, all modules, mobile-first | 🔜 Phase 9 |
| 19 | Community | Events, startup showcase, discussion board | 🔜 Phase 10 |
| 20 | Internal Chat | Real-time messaging via Django Channels | 🔜 Phase 10 |
| 21 | AI Assistant | Document search, report generation, query bot | 🔜 Phase 10 |

---

## Tech Stack

```
Backend
  Python 3.12 + Django 5.1 + Django REST Framework 3.15
  JWT Auth: djangorestframework-simplejwt
  API Docs: drf-spectacular (OpenAPI 3 / Swagger)
  Task Queue: Celery 5 + Redis 7
  Realtime: Django Channels + WebSockets (Phase 10)
  Email: Brevo SMTP API
  PDF: ReportLab
  QR Codes: qrcode
  File Storage: MinIO (S3-compatible, self-hosted)

Database
  Development: SQLite (zero config, local)
  Production: TiDB Cloud (MySQL-compatible, serverless, scalable)

Frontend (Phase 9)
  Next.js 15 + TypeScript
  Tailwind CSS + shadcn/ui
  TanStack Query (server state)

Deployment
  Backend: Railway or Render
  Frontend: Vercel
  Database: TiDB Cloud
  Storage: MinIO (self-hosted or MinIO Cloud)
  Cache/Queue: Upstash Redis (or self-hosted)
```

---

## India-specific Features

- **GST-compliant invoices** with CGST/SGST/IGST breakdown
- **UPI QR codes** on invoices (PhonePe, Google Pay, Paytm, BHIM)
- **PAN + GST number** stored per company
- **IST timezone** (`Asia/Kolkata`) throughout
- **Brevo** for transactional email (excellent India deliverability)
