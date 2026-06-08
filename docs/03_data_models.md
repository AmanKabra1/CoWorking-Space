# Data Models

All models (except `User`) extend `TimeStampedModel` which provides:
- `id` — UUID primary key (auto-generated, never exposed to enumeration)
- `created_at` — auto set on create
- `updated_at` — auto set on every save

---

## Phase 1 Models (built)

### User (`accounts_user`)

The central user record. Email is the login identifier.

```
User
├── id            UUID        PK, auto-generated
├── email         EmailField  unique — used as login username
├── first_name    CharField
├── last_name     CharField
├── phone         CharField   optional
├── role          CharField   choices: super_admin | company_admin | employee
├── company       FK → Company  null for Super Admin
├── avatar        ImageField  optional profile photo
├── is_active     Boolean     False = soft-deleted / deactivated
├── is_staff      Boolean     True = can access Django admin
├── is_superuser  Boolean     True for Super Admin (Django permissions)
├── created_at    DateTime    auto
└── updated_at    DateTime    auto
```

**Relationships:**
- `user.company` — the tenant company this user belongs to (null for Super Admin)
- `company.employees` — reverse: all users in a company

---

### Company (`companies_company`)

A tenant — a startup or business renting space.

```
Company
├── id             UUID        PK
├── name           CharField   "TechStartup Pvt Ltd"
├── slug           SlugField   unique, auto-derived from name ("techstartup-pvt-ltd")
├── email          EmailField  company contact email
├── phone          CharField
├── gst_number     CharField   optional (15 chars, e.g. "29ABCDE1234F1Z5")
├── pan_number     CharField   optional (10 chars)
├── address        TextField   full address
├── city           CharField
├── state          CharField
├── pincode        CharField
├── logo           ImageField  optional
├── website        URLField    optional
├── status         CharField   choices: active | inactive | suspended
├── contract_start DateField   optional lease start
├── contract_end   DateField   optional lease end
├── notes          TextField   internal notes (Super Admin only)
├── created_at     DateTime    auto
└── updated_at     DateTime    auto
```

**Computed property:**
- `company.employee_count` — count of active users linked to this company

---

## Phase 2 Models (built — Workspace)

```
Building                              workspace_building
├── id            UUID   PK
├── name          CharField
├── address       TextField
├── city, state, pincode
├── description   TextField  optional
└── is_active     Boolean

Floor                                 workspace_floor
├── id            UUID   PK
├── building      FK → Building
├── floor_number  Integer    unique per building (0=Ground, 1=1st...)
├── name          CharField  "Ground Floor", "1st Floor"
├── floor_plan    ImageField optional
└── is_active     Boolean

Room                                  workspace_room
├── id            UUID   PK
├── floor         FK → Floor
├── room_number   CharField  unique per floor ("101", "A-205")
├── name          CharField  optional display name
├── room_type     CharField  cabin|open_space|meeting_room|event_hall|storage|other
├── capacity      Integer    max occupants
├── area_sqft     Decimal    optional
└── is_active     Boolean

Desk                                  workspace_desk
├── id            UUID   PK
├── room          FK → Room
├── desk_code     CharField  unique per room ("D-101-A", "HOT-01")
├── desk_type     CharField  dedicated | hot_desk
├── company       FK → Company  nullable — set when dedicated desk is assigned
├── monthly_rate  Decimal
├── is_available  Boolean    False = under maintenance or permanently occupied
└── notes         TextField  optional

ParkingSlot                           workspace_parkingslot
├── id            UUID   PK
├── building      FK → Building
├── slot_number   CharField  unique per building ("P-01", "B-15", "EV-03")
├── slot_type     CharField  car | bike | ev
├── company       FK → Company  nullable — assigned company
├── monthly_rate  Decimal
├── is_available  Boolean
└── notes         TextField
```

---

## Phase 3 Models (built — Facility Booking)

```
Facility                               facilities_facility
├── id             UUID    PK
├── name           CharField
├── facility_type  CharField  conference_room | meeting_room | event_hall |
│                             podcast_studio | printing_room | 3d_printer |
│                             cafeteria | other
├── building       FK → Building  CASCADE
├── floor          FK → Floor     SET_NULL, nullable
├── capacity       Integer    max attendees
├── price_per_hour Decimal
├── price_per_day  Decimal
├── description    TextField  optional
├── amenities      JSONField  ["WiFi", "Projector", "AC", ...]
├── booking_rules  JSONField  {"min_hours": 1, "max_hours": 8, ...}
├── is_active      Boolean
├── created_at     DateTime   auto
└── updated_at     DateTime   auto

FacilityImage                          facilities_facilityimage
├── id          UUID    PK
├── facility    FK → Facility  CASCADE
├── image       ImageField
├── caption     CharField  optional
├── is_primary  Boolean
├── order       Integer    display order
├── created_at  DateTime   auto
└── updated_at  DateTime   auto

Booking                                bookings_booking
├── id               UUID    PK
├── facility         FK → Facility  PROTECT
├── company          FK → Company   PROTECT
├── booked_by        FK → User      PROTECT  (who created the booking)
├── booking_date     DateField
├── start_time       TimeField
├── end_time         TimeField
├── duration_hours   Decimal    auto-calculated on creation
├── status           CharField  pending | approved | rejected | cancelled | completed
├── purpose          TextField  reason for booking
├── attendees_count  Integer
├── total_amount     Decimal    auto-calculated (price_per_day if ≥8h else price_per_hour × hours)
├── approved_by      FK → User  nullable — set when status → approved
├── approved_at      DateTimeField  nullable
├── rejection_reason TextField  optional — set when status → rejected
├── notes            TextField  internal admin notes
├── created_at       DateTime   auto
└── updated_at       DateTime   auto
```

**Booking state machine:**
```
created → PENDING
PENDING → APPROVED  (Super Admin action)
PENDING → REJECTED  (Super Admin action, optional reason)
PENDING/APPROVED → CANCELLED  (Company Admin or Super Admin)
APPROVED → COMPLETED  (Super Admin action, after event ends)
```

**Conflict detection:** Any new booking that overlaps in date + time with an existing PENDING or APPROVED booking for the same facility is rejected at validation time.

---

## Phase 4 Models (built — Billing)

```
Invoice                                billing_invoice
├── id              UUID    PK
├── invoice_number  CharField  unique, auto: INV-YYYY-MM-NNNN
├── company         FK → Company  PROTECT
├── billing_period_start  DateField
├── billing_period_end    DateField
├── line_items      JSONField  [{description, qty, rate, amount}, ...]
├── subtotal        Decimal
├── cgst_rate       Decimal    default 9.00 %
├── sgst_rate       Decimal    default 9.00 %
├── igst_rate       Decimal    default 0.00 %  (use for inter-state)
├── cgst_amount     Decimal    auto-calculated
├── sgst_amount     Decimal    auto-calculated
├── igst_amount     Decimal    auto-calculated
├── total_amount    Decimal    auto-calculated = subtotal + all GST
├── status          CharField  draft | sent | paid | overdue | cancelled
├── due_date        DateField  optional
├── sent_at         DateTimeField  set when status → sent
├── paid_at         DateTimeField  set when status → paid
├── pdf_file        FileField  optional cached PDF
├── notes           TextField
├── created_at      DateTime   auto
└── updated_at      DateTime   auto

Payment                                billing_payment
├── id              UUID    PK
├── invoice         FK → Invoice  PROTECT
├── company         FK → Company  PROTECT
├── amount          Decimal
├── payment_method  CharField  upi | bank_transfer | cash | cheque | neft
├── transaction_id  CharField  bank/UPI reference
├── upi_ref         CharField  UPI VPA used
├── status          CharField  pending | completed | failed | refunded
├── paid_at         DateTimeField
├── notes           TextField
├── recorded_by     FK → User  SET_NULL, nullable
├── created_at      DateTime   auto
└── updated_at      DateTime   auto
```

**Invoice state machine:**
```
draft → SENT (send action)
SENT  → PAID (record-payment auto-transitions when total_paid ≥ total_amount)
SENT  → OVERDUE (mark-overdue action)
DRAFT/SENT → CANCELLED (cancel action)
```

**Auto-generation logic:** `generate_monthly` scans all active companies and creates a draft invoice with line items from: dedicated desks, parking slots, and completed facility bookings within the period.

---

## Phase 5 Models (coming — Startup Incubation)

```
StartupProfile
├── id, company FK (one-to-one)
├── stage (idea | mvp | growth | scaling), sector, founding_year
├── team_size, monthly_revenue, funding_raised
├── pitch_deck FK → Document
└── created/updated

IncubationApplication
├── id, startup FK
├── status (applied | under_review | accepted | rejected)
├── reviewer FK → User, review_notes, reviewed_at
└── created/updated
```

---

## Entity Relationship (text diagram)

```
Building ──< Floor ──< Room ──< Desk
                              └──< ParkingSlot

Company ──< User (employees)
         ──< Booking ──> Facility
         ──< Invoice ──< Payment
         ──< StartupProfile
         ──< MaintenanceTicket
         └──< Document

User ──> Company (belongs to)
     ──< Booking (booked_by)
```
