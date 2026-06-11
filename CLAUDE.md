# CoWorkHub — agent working notes

SaaS for building leasing / coworking / facility booking / startup ecosystem.
Roles: **super_admin** (building owner), **company_admin** (lease/floor tenant),
**employee**, **public visitor** (no login), startup tenant.

## Stack
- Backend: Django 5 + DRF, SimpleJWT, `apps/` per module. Settings split in
  `backend/coworkhub/settings/` (base/development/production).
- DB: SQLite (dev) · **TiDB Cloud via `django_tidb` engine** (prod). TiDB rejects
  ALTER-based FK adds — keep FKs **inline in CreateModel**, never a deferred AddField.
- Frontend: Next.js 16 App Router, TS, Tailwind. Route groups: `(marketing)` public,
  `(auth)`, `(dashboard)`. State: Zustand (`store/auth`) + TanStack Query.
  API layer: `src/lib/services.ts`, types in `src/types/index.ts`.
- Deploy: Render (backend Docker, **free 512MB** — gunicorn honors WEB_CONCURRENCY) ·
  Vercel (frontend). Migrations + optional `createsuperuser` run on container startup
  (see Dockerfile CMD). Render env: `DJANGO_SETTINGS_MODULE=coworkhub.settings.production`,
  `ALLOWED_HOSTS=.onrender.com`, DB_*, `TIDB_SSL_CA=/etc/ssl/certs/ca-certificates.crt`,
  `CORS_ALLOWED_ORIGINS`, `SECRET_KEY`, AI key (below).

## Conventions
- DRF responses are paginated `{count, results}`; frontend services do `.results ?? []`.
- Never use real personal data (no real emails/names) in tests/fixtures — use
  `admin@example.com`, `Acme Corp`, etc.
- **Never `git push` automatically** — user pushes. Commit freely after each phase.
- Verify before commit: backend `flake8 apps/ coworkhub/ --max-line-length=120
  --exclude=migrations,__pycache__ --ignore=E501,W503,E302` + `manage.py check`;
  frontend `npm run type-check`.
- Commit messages via a temp `_commitmsg.txt` + `git commit -F` (avoids PowerShell
  here-string quoting issues). End with the Co-Authored-By line.
- IDE "stale diagnostic" hints after edits are usually resolved by the next edit;
  trust `npm run type-check` / `flake8` over them.

## What's built (modules in apps/ with frontend pages)
accounts, companies, workspace (buildings/floors/rooms/desks), facilities (CRUD by
super+company admin, `is_public`, `owner_company`), bookings (internal/external,
approval RBAC, confirm/paid, **public no-login `/book`**, emails), billing, payments
(Razorpay), inventory (+Excel round-trip import/export), vendors, **subleasing**
(seat sub-lease), **leases** (company↔building/floor↔seats, utilization),
incubation/startup, community, documents, esign, maintenance, visitors, analytics,
notifications (Brevo `send_email`), audit, chat (Channels), **ai_assistant**.

### Booking flow (done)
Public `/book` → super_admin approve → email → "Mark Paid" → CONFIRMED → slot locked.
Employee booking → company_admin (or super_admin) approves → free (internal).
Slots with status pending/approved/confirmed are hidden from new bookings.

### AI assistant (done)
`apps/ai_assistant/services.py` is provider-agnostic via **LangGraph**. Set ONE env
key: `GROQ_API_KEY` (Llama 3.3 70B, preferred) or `GOOGLE_API_KEY`/`GEMINI_API_KEY`
(Gemini 1.5 Flash). Frontend page `/ai-assistant` (all roles, role-aware prompts).

## Remaining / next phases (free-tier-friendly first)
1. Startup **apply→approve** seat-leasing (startup applies → company_admin approves →
   super_admin notified only). Small enhancement to `subleasing`.
2. **QR check-in** for confirmed bookings (qrcode lib already a dep).
3. Online **payment link** for public bookings (replace manual Mark Paid; needs live Razorpay).
4. **UPI QR + monthly invoice automation** (Celery beat — needs an always-on worker, not free).
5. **OnlyOffice** real in-browser Office editor (needs its own always-on Docker server, paid).

## Resuming cheaply after /clear
Read this file + `git log --oneline -15` + the auto-memory. Then continue the next
phase. Don't re-explain the project; it's all here and in git.
