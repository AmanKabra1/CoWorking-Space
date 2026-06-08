# Architecture & Code Structure

## Folder Structure (Phase 1 — complete)

```
CoWorking Space/                    ← project root
│
├── docs/                           ← YOU ARE HERE — all documentation
│   ├── 00_overview.md
│   ├── 01_setup.md
│   ├── 02_architecture.md
│   ├── 03_data_models.md
│   ├── 04_auth_and_rbac.md
│   ├── 05_api_reference.md
│   └── 06_phases.md
│
├── docker-compose.yml              ← spins up backend + redis + celery
├── .gitignore
│
└── backend/                        ← Django project root
    │
    ├── manage.py                   ← Django CLI entry point
    ├── Dockerfile                  ← production container
    ├── .env.example                ← copy to .env and fill in
    │
    ├── requirements/
    │   ├── base.txt                ← shared packages (prod + dev)
    │   ├── development.txt         ← base + ipython + django-extensions
    │   └── production.txt          ← base + gunicorn + mysqlclient
    │
    ├── coworkhub/                  ← Django project package
    │   ├── __init__.py             ← imports celery app (required for autodiscover)
    │   ├── celery.py               ← Celery app definition
    │   ├── urls.py                 ← root URL router
    │   ├── wsgi.py                 ← WSGI entry (gunicorn)
    │   ├── asgi.py                 ← ASGI entry (channels / daphne)
    │   └── settings/
    │       ├── base.py             ← all shared settings
    │       ├── development.py      ← SQLite, DEBUG=True, console email
    │       └── production.py       ← TiDB, Redis cache, security headers, Brevo
    │
    └── apps/                       ← all Django apps live here
        ├── core/
        │   └── models.py           ← TimeStampedModel (abstract base with UUID PK)
        │
        ├── accounts/               ← users, auth, RBAC
        │   ├── models.py           ← User (email-based, 3 roles, FK to Company)
        │   ├── managers.py         ← UserManager (create_user / create_superuser)
        │   ├── serializers.py      ← Registration, Login, Profile, ChangePassword
        │   ├── views.py            ← Auth endpoints (Register, Login, Logout, Me…)
        │   ├── urls.py             ← /api/v1/auth/* routes
        │   ├── permissions.py      ← IsSuperAdmin, IsCompanyAdmin, IsOwnerOrSuperAdmin
        │   ├── admin.py            ← Django admin for User
        │   └── management/
        │       └── commands/
        │           └── create_superadmin.py  ← CLI to bootstrap first Super Admin
        │
        └── companies/              ← tenant companies
            ├── models.py           ← Company (extends TimeStampedModel)
            ├── serializers.py      ← CompanySerializer, CompanyListSerializer
            ├── views.py            ← CompanyViewSet (CRUD + employees + invite)
            ├── urls.py             ← /api/v1/companies/* routes
            ├── permissions.py      ← CanViewOwnCompany
            └── admin.py            ← Django admin for Company
```

---

## How a Request Flows Through the Backend

```
HTTP Request
     │
     ▼
coworkhub/urls.py           ← Root router
     │
     ├── /admin/            → Django admin (staff only)
     ├── /api/v1/auth/      → apps/accounts/urls.py
     ├── /api/v1/companies/ → apps/companies/urls.py
     └── /api/schema/       → drf-spectacular (OpenAPI)

                    │
                    ▼
              View / ViewSet
                    │
                    ├── get_permissions()      ← which permission classes apply?
                    │        │
                    │        └── checks request.user.role
                    │
                    ├── get_queryset()         ← what data can this user see?
                    │        │
                    │        └── Super Admin: all  |  others: their own
                    │
                    ├── get_serializer_class() ← list vs detail serializer
                    │
                    └── serializer.is_valid()  ← validate input
                              │
                              └── Model.save() → Database → Response JSON
```

---

## Key Design Decisions

### 1. UUID Primary Keys
All models use `UUIDField` as primary key instead of auto-increment integers.

**Why:** Prevents ID enumeration attacks (attacker can't guess `/companies/1/`,
`/companies/2/`, etc.), better for distributed systems, safe to expose in URLs.

### 2. Email as Username
The `User` model uses `email` as the login field (`USERNAME_FIELD = 'email'`).
No `username` field exists.

**Why:** Coworking tenants identify themselves by company email. Simpler UX.

### 3. Role via a CharField, not Groups
Roles (`super_admin`, `company_admin`, `employee`) are stored as a plain `CharField`
on the User model, not Django's built-in `groups` system.

**Why:** Three fixed roles that never change don't need the flexibility of groups.
Role checks like `user.is_super_admin` are simple Python properties — easier to
read, test, and maintain than `user.groups.filter(name='super_admin').exists()`.

### 4. Split Settings
`base.py` has all shared config. `development.py` and `production.py` only
override what actually differs.

**Why:** A single `settings.py` that switches on `DEBUG` creates hidden prod-only
bugs. Separate files make differences explicit and reviewable.

### 5. Tenant Isolation via Queryset Filtering
Every ViewSet's `get_queryset()` filters data by the requesting user's company.
Super Admin gets everything; others get only their own data.

**Why:** Simpler than row-level security at the DB layer and easier to audit.
Each new app must implement this pattern in its own `get_queryset()`.

### 6. JWT with Custom Claims
The JWT payload includes `role`, `email`, and `full_name` alongside the standard
`user_id` and `exp` claims.

**Why:** The frontend can decode the token and render the correct dashboard without
an extra `/me` API call on every page load.

---

## Adding a New App (Pattern)

Every new feature module follows this pattern:

```bash
# 1. Create app folder
mkdir backend/apps/myfeature
touch backend/apps/myfeature/__init__.py

# 2. Create apps.py
# class MyFeatureConfig(AppConfig):
#     name = 'apps.myfeature'
#     label = 'myfeature'

# 3. Add to INSTALLED_APPS in base.py
# 'apps.myfeature.apps.MyFeatureConfig',

# 4. Create models.py extending TimeStampedModel
# 5. Create serializers.py, views.py, urls.py, permissions.py, admin.py
# 6. Wire urls.py into coworkhub/urls.py
# 7. makemigrations + migrate
```

---

## Celery Task Pattern

```python
# apps/billing/tasks.py
from celery import shared_task

@shared_task
def generate_monthly_invoices():
    # runs as background job, not blocking the HTTP response
    ...
```

Tasks are auto-discovered from every app's `tasks.py` file because of
`app.autodiscover_tasks()` in `coworkhub/celery.py`.
