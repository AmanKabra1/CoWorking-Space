# API Reference — Phase 1

Base URL: `http://localhost:8000/api/v1/`
Interactive docs: `http://localhost:8000/api/docs/`

Authentication: `Authorization: Bearer <access_token>`

---

## Auth Endpoints

### POST `/auth/login/`
Obtain JWT tokens.

**Request:**
```json
{
  "email": "aman.k@sanchiconnect.com",
  "password": "Admin@123"
}
```

**Response 200:**
```json
{
  "user": {
    "id": "106b7150-966a-4366-b64a-d39f6910c90d",
    "email": "aman.k@sanchiconnect.com",
    "full_name": "Aman K",
    "role": "super_admin",
    "company": null,
    "is_active": true
  },
  "tokens": {
    "access": "eyJ...",
    "refresh": "eyJ..."
  }
}
```

---

### POST `/auth/register/`
Create a new user.

- **No auth:** only allowed for first Super Admin (if none exists)
- **Super Admin auth:** can create any role

**Request:**
```json
{
  "email": "ravi@techstartup.in",
  "first_name": "Ravi",
  "last_name": "Sharma",
  "phone": "9876543210",
  "role": "company_admin",
  "password": "SecurePass@123",
  "password_confirm": "SecurePass@123"
}
```

**Response 201:** same shape as login response

---

### POST `/auth/logout/`
Blacklist a refresh token. Requires auth.

**Request:**
```json
{ "refresh": "eyJ..." }
```

**Response 205:**
```json
{ "detail": "Logged out successfully." }
```

---

### POST `/auth/token/refresh/`
Exchange a refresh token for a new access + refresh pair.

**Request:**
```json
{ "refresh": "eyJ..." }
```

**Response 200:**
```json
{
  "access": "eyJ...",
  "refresh": "eyJ..."
}
```

---

### GET `/auth/me/`
Current user's profile. Requires auth.

**Response 200:**
```json
{
  "id": "...",
  "email": "aman.k@sanchiconnect.com",
  "first_name": "Aman",
  "last_name": "K",
  "full_name": "Aman K",
  "phone": "",
  "role": "super_admin",
  "avatar": null,
  "company": null,
  "company_name": null,
  "is_active": true,
  "created_at": "2026-06-08T10:42:51.157095+05:30"
}
```

### PATCH `/auth/me/`
Update own profile (first_name, last_name, phone, avatar). email and role are read-only.

---

### POST `/auth/change-password/`
Change password. Requires auth.

**Request:**
```json
{
  "current_password": "Admin@123",
  "new_password": "NewPass@456",
  "new_password_confirm": "NewPass@456"
}
```

---

### GET `/auth/users/`
List all users. **Super Admin only.**

Query params: `?role=company_admin`, `?is_active=true`, `?search=ravi`

**Response 200 (paginated):**
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "...",
      "email": "ravi@techstartup.in",
      "full_name": "Ravi Sharma",
      "role": "employee",
      "company_name": "TechStartup Pvt Ltd",
      "is_active": true
    }
  ]
}
```

### GET `/auth/users/{uuid}/`
Get a user. **Owner or Super Admin.**

### PATCH `/auth/users/{uuid}/`
Update a user. **Owner or Super Admin.**

### DELETE `/auth/users/{uuid}/`
Soft-deactivate a user (`is_active = False`). **Super Admin only.**

---

## Company Endpoints

### GET `/companies/`
List companies.
- Super Admin → all companies
- Company Admin / Employee → only their own company

**Response 200 (paginated):**
```json
{
  "count": 1,
  "results": [
    {
      "id": "c0d53ba7-...",
      "name": "TechStartup Pvt Ltd",
      "slug": "techstartup-pvt-ltd",
      "email": "hello@techstartup.in",
      "phone": "9876543210",
      "city": "Bengaluru",
      "state": "Karnataka",
      "status": "active",
      "employee_count": 3,
      "created_at": "2026-06-08T..."
    }
  ]
}
```

---

### POST `/companies/`
Create a company. **Super Admin only.**

**Request:**
```json
{
  "name": "TechStartup Pvt Ltd",
  "email": "hello@techstartup.in",
  "phone": "9876543210",
  "address": "12 MG Road",
  "city": "Bengaluru",
  "state": "Karnataka",
  "pincode": "560001",
  "gst_number": "29ABCDE1234F1Z5",
  "pan_number": "ABCDE1234F",
  "contract_start": "2026-01-01",
  "contract_end": "2026-12-31"
}
```

**Response 201:** full Company object (slug is auto-generated from name)

---

### GET `/companies/{uuid}/`
Company detail. Super Admin sees all; others see only own.

### PUT / PATCH `/companies/{uuid}/`
Update company. Super Admin or Company Admin (own company).

### DELETE `/companies/{uuid}/`
Delete company. **Super Admin only.**

---

### GET `/companies/{uuid}/employees/`
List active employees of a company. Auth required.
Company Admin / Employee can only query their own company's employees.

**Response 200:**
```json
[
  {
    "id": "7a6dd79a-...",
    "email": "ravi@techstartup.in",
    "full_name": "Ravi Sharma",
    "role": "employee",
    "company_name": "TechStartup Pvt Ltd",
    "is_active": true
  }
]
```

---

### POST `/companies/{uuid}/invite-employee/`
Create a new user and link them to this company. **Super Admin only.**

**Request:**
```json
{
  "email": "priya@techstartup.in",
  "first_name": "Priya",
  "last_name": "Mehta",
  "role": "company_admin",
  "password": "TempPass@123",
  "password_confirm": "TempPass@123"
}
```

**Response 201:** User object

---

### PATCH `/companies/{uuid}/status/`
Change company status. **Super Admin only.**

**Request:**
```json
{ "status": "suspended" }
```

Valid values: `active`, `inactive`, `suspended`

---

## Error Responses

All errors follow DRF's standard format:

```json
{ "detail": "Not found." }

{ "email": ["This field is required."] }

{ "password": ["Passwords do not match."] }
```

HTTP status codes:
- `400` Bad Request — validation errors
- `401` Unauthorized — missing or invalid token
- `403` Forbidden — authenticated but wrong role
- `404` Not Found — object not found or queryset filtered out
- `429` Too Many Requests — rate limited (production only)
