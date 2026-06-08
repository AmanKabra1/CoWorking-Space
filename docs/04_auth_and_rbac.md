# Authentication & Role-Based Access Control

## How Authentication Works

CoWorkHub uses **JWT (JSON Web Tokens)** — stateless, no session cookies.

```
1. User POSTs email + password to /api/v1/auth/login/
         │
         ▼
2. Django authenticates against DB (email = USERNAME_FIELD)
         │
         ▼
3. Two tokens returned:
   ┌─────────────────────────────────────────────────────┐
   │  access token   — short-lived (60 min)              │
   │  refresh token  — long-lived (7 days)               │
   └─────────────────────────────────────────────────────┘
         │
         ▼
4. Client stores tokens (localStorage or httpOnly cookie)
         │
         ▼
5. Every API request sends:
   Authorization: Bearer <access_token>
         │
         ▼
6. When access token expires, POST to /api/v1/auth/token/refresh/
   with the refresh token → new access token returned
         │
         ▼
7. Logout: POST to /api/v1/auth/logout/ with refresh token
   → refresh token is BLACKLISTED (can never be used again)
```

---

## JWT Payload

Every access token contains these claims (decode at jwt.io to inspect):

```json
{
  "token_type": "access",
  "exp": 1780899190,
  "iat": 1780895590,
  "jti": "f8380b32ac434cc7a912533c520bd18d",
  "user_id": "106b7150-966a-4366-b64a-d39f6910c90d",
  "role": "super_admin",
  "email": "aman.k@sanchiconnect.com",
  "full_name": "Aman K"
}
```

**Why include role/email in the token?**
The frontend can decode the JWT client-side and immediately know which dashboard
to render — no extra API call to `/me` on every page load.

---

## The Three Roles

### `super_admin` — Building Owner / Platform Admin
```
✅ Create / manage companies (tenants)
✅ Manage all workspaces and facilities
✅ Approve / reject bookings
✅ View all invoices and payments
✅ Access Django admin panel (is_staff=True, is_superuser=True)
✅ View all audit logs and reports
✅ Create users of any role
✅ Suspend or deactivate companies
```

### `company_admin` — Tenant Representative
```
✅ Manage their company's profile (read + limited update)
✅ Manage employees in their company
✅ Request facility bookings
✅ View and pay invoices for their company
✅ Submit maintenance requests
✅ Upload startup documents
✅ View their company's bookings and payments
❌ Cannot see other companies' data
❌ Cannot access Django admin
❌ Cannot approve bookings (only request)
```

### `employee` — Individual Team Member
```
✅ View their company's approved facilities
✅ Request bookings (within allowed rules)
✅ Access company documents
✅ Submit maintenance / support requests
✅ View their own profile
❌ Cannot manage employees
❌ Cannot view invoices
❌ Cannot see other companies' data
```

---

## Permission Classes (backend code)

Defined in `apps/accounts/permissions.py`:

```python
IsSuperAdmin               # user.role == 'super_admin'
IsCompanyAdmin             # user.role == 'company_admin'
IsSuperAdminOrCompanyAdmin # either of the above
IsOwnerOrSuperAdmin        # obj == request.user OR is super_admin
```

Defined in `apps/companies/permissions.py`:
```python
CanViewOwnCompany          # Super Admin: all  |  others: own company (read-only)
```

### How permissions compose in a ViewSet

```python
class CompanyViewSet(ModelViewSet):

    def get_permissions(self):
        if self.action in ['create', 'destroy']:
            return [IsSuperAdmin()]           # only super admin creates/deletes
        if self.action in ['update', 'partial_update']:
            return [IsSuperAdminOrCompanyAdmin()]  # admin can update own company
        return [IsAuthenticated(), CanViewOwnCompany()]  # read: anyone authenticated
```

### How queryset filtering enforces tenant isolation

```python
def get_queryset(self):
    user = self.request.user
    if user.is_super_admin:
        return Company.objects.all()     # sees everything
    if user.company_id:
        return Company.objects.filter(id=user.company_id)  # sees only own company
    return Company.objects.none()        # no company assigned → empty
```

Permissions block the *action type*. Queryset filtering blocks *which records*.
Both layers are needed.

---

## Token Lifecycle

```
Login ─────────────────────────────────► access (60min) + refresh (7 days)
                                              │
Access expires ───────────────────────────── │ ──► POST /token/refresh/
                                              │         │
                                              │    new access (60min)
                                              │    new refresh (7 days)  [rotated]
                                              │    old refresh BLACKLISTED
                                              │
Logout ────────────────────────────────────── │ ──► POST /logout/ {refresh}
                                                        │
                                                   refresh BLACKLISTED
                                                   (access still valid until exp)
```

**Note:** Access tokens cannot be revoked early (stateless). If you need instant
revocation (e.g., admin deactivates a user), the account `is_active` check on each
request handles that — the token is valid but the user is denied.

---

## First-Time Setup Flow

```
1. Deploy backend
2. Run: python manage.py create_superadmin --email=... --password=...
3. Super Admin logs in → gets JWT
4. Super Admin creates companies via POST /api/v1/companies/
5. Super Admin invites company admins via POST /api/v1/companies/{id}/invite-employee/
   (with role=company_admin)
6. Company Admin logs in, sees their company dashboard
7. Company Admin invites employees via the same endpoint (role=employee)
```
