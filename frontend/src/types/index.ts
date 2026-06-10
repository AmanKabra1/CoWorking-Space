export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export type Role = 'super_admin' | 'company_admin' | 'employee'

export interface User {
  id: string
  email: string
  full_name: string
  role: Role
  company: string | null
  company_name: string | null
  is_active: boolean
  date_joined: string
}

export interface Company {
  id: string
  name: string
  slug: string
  email: string
  phone: string
  address?: string
  city?: string
  state?: string
  pincode?: string
  website?: string
  gst_number?: string
  pan_number?: string
  industry?: string
  status: 'active' | 'inactive' | 'suspended'
  employee_count: number
  created_at: string
  updated_at?: string
}

export interface Facility {
  id: string
  name: string
  facility_type: string
  description: string
  capacity: number
  price_per_hour: string
  price_per_day: string
  is_active: boolean
  is_available: boolean
  building_name?: string
  floor_number?: number
  primary_image?: string
  amenities: string[]
  images: { id: string; image: string; is_primary: boolean }[]
}

export type BookingStatus = 'pending' | 'approved' | 'rejected' | 'cancelled' | 'completed'

export interface Booking {
  id: string
  facility: string
  facility_name: string
  company: string
  company_name: string
  booked_by: string
  booked_by_name: string
  booking_date: string
  start_time: string
  end_time: string
  duration_hours: number
  attendees: number
  status: BookingStatus
  booking_type: 'internal' | 'external'
  payment_required: boolean
  total_amount: string
  purpose: string
  rejection_reason: string
  created_at: string
}

export type InvoiceStatus = 'draft' | 'sent' | 'paid' | 'overdue' | 'cancelled'

export interface Invoice {
  id: string
  invoice_number: string
  company: string
  company_name: string
  status: InvoiceStatus
  subtotal: string
  cgst_amount: string
  sgst_amount: string
  total_amount: string
  amount_paid: string
  amount_due: string
  due_date: string
  pdf_url?: string
  created_at: string
}

export type TicketStatus = 'open' | 'assigned' | 'in_progress' | 'resolved' | 'closed'
export type TicketPriority = 'low' | 'medium' | 'high' | 'critical'

export interface MaintenanceTicket {
  id: string
  ticket_number: string
  title: string
  description: string
  category: string
  priority: TicketPriority
  status: TicketStatus
  location?: string
  reported_by_name: string
  assigned_to_name: string | null
  building_name: string | null
  resolved_at: string | null
  created_at: string
}

export interface VisitorPass {
  id: string
  visitor_name: string
  visitor_email: string
  visitor_phone: string
  host: { id: number; email: string; first_name: string; last_name: string }
  company: number
  purpose: string
  check_in: string | null
  check_out: string | null
  status: 'pending' | 'approved' | 'checked_in' | 'checked_out' | 'cancelled'
  qr_code: string | null
  created_at: string
  // legacy fields kept for backward compatibility
  host_name?: string
  building_name?: string | null
  pass_code?: string
  scheduled_date?: string
  valid_from?: string
  valid_until?: string
  checked_in_at?: string | null
  checked_out_at?: string | null
}

export interface Notification {
  id: string
  title: string
  message: string
  notification_type: string
  is_read: boolean
  related_id: string | null
  related_type: string
  created_at: string
}

export interface DashboardData {
  as_of: string
  revenue: {
    total_invoiced: number
    total_paid: number
    total_overdue: number
    total_outstanding: number
  }
  bookings: {
    total: number
    pending: number
    approved: number
    completed: number
    rejected: number
    cancelled: number
  }
  occupancy: {
    desks: { total: number; assigned: number; rate_pct: number }
    parking: { total: number; assigned: number; rate_pct: number }
  }
  maintenance: {
    open: number
    in_progress: number
    resolved_this_month: number
  }
  platform?: {
    total_companies: number
    active_companies: number
    total_facilities: number
  }
}

export interface RevenueData {
  start: string
  end: string
  period: string
  by_period: { period: string; invoiced: number; paid?: number; invoice_count: number }[]
  totals: { invoiced: number; paid: number; invoice_count: number }
  by_company?: { company_name?: string; name?: string; total?: number; amount?: number }[]
  monthly?: { month?: string; period?: string; amount?: number; paid?: number }[]
}

// ─── Chat ─────────────────────────────────────────────────
export interface ChatRoom {
  id: string
  name: string
  room_type: 'company_general' | 'direct'
  company: string
  company_name: string
  last_message: { content: string; created_at: string } | null
  updated_at: string
}

export interface ChatMessage {
  id: string
  room: string
  sender: string | null
  sender_name: string
  content: string
  message_type: 'text' | 'system'
  is_deleted: boolean
  created_at: string
}

// ─── Community ────────────────────────────────────────────
export interface Post {
  id: string
  post_type: 'announcement' | 'general'
  title: string
  content: string
  author: string
  author_name: string
  company: string | null
  company_name: string | null
  visibility: 'company' | 'platform'
  is_pinned: boolean
  comment_count: number
  created_at: string
}

export interface Event {
  id: string
  title: string
  description: string
  start_datetime: string
  end_datetime: string
  location: string
  organizer: string
  organizer_name: string
  company: string | null
  company_name: string | null
  max_attendees: number | null
  is_public: boolean
  rsvp_count: number
  my_rsvp: 'attending' | 'maybe' | 'declined' | null
}

// ─── Payments ─────────────────────────────────────────────
export interface PaymentGateway {
  id: number
  provider: 'razorpay' | 'stripe'
  api_key: string
  is_active: boolean
  created_at: string
}

export interface PaymentOrder {
  id: number
  invoice: number
  provider: string
  gateway_order_id: string
  amount: string
  currency: string
  status: 'pending' | 'paid' | 'failed' | 'refunded'
  created_at: string
}

// ─── Incubation ───────────────────────────────────────────
export interface IncubationProfile {
  id: number
  company: { id: number; name: string }
  stage: 'ideation' | 'mvp' | 'growth' | 'scaling'
  sector: string
  description: string
  website: string
  team_size: number
  founded_year: number | null
  mentor: { id: number; email: string; first_name: string; last_name: string } | null
  status: 'active' | 'graduated' | 'inactive'
  created_at: string
}

// ─── Documents ────────────────────────────────────────────
export interface Document {
  id: number
  title: string
  description: string
  file: string
  file_type: string
  file_size: number
  version: number
  uploaded_by: { id: number; email: string; first_name: string; last_name: string }
  company: number
  is_public: boolean
  created_at: string
}

// ─── E-Sign ───────────────────────────────────────────────
export interface SignatureRecord {
  id: string
  request: string
  signer: string | null
  signer_email: string
  signer_name: string
  order: number
  status: 'pending' | 'signed' | 'declined'
  signed_at: string | null
  decline_reason: string
  created_at: string
}

export interface SignatureRequest {
  id: string
  title: string
  document_file: string
  message: string
  created_by: string
  created_by_name: string
  company: string
  company_name: string
  status: 'draft' | 'pending' | 'partially_signed' | 'completed' | 'cancelled' | 'expired'
  expires_at: string | null
  certificate_file: string | null
  records: SignatureRecord[]
  created_at: string
}

// ─── Workspace ────────────────────────────────────────────
export interface Building {
  id: string
  name: string
  city: string
  state: string
  is_active: boolean
}

// ─── Public booking ───────────────────────────────────────
export interface PublicFacility {
  id: string
  name: string
  facility_type: string
  facility_type_display: string
  building_name: string | null
  capacity: number
  price_per_hour: string
  price_per_day: string
  description: string
  amenities: string[]
}

// ─── Exports ──────────────────────────────────────────────
export type ExportFormat = 'excel' | 'word' | 'pdf'

// ─── Vendors ──────────────────────────────────────────────
export type VendorCategory =
  | 'utilities' | 'catering' | 'cleaning' | 'maintenance' | 'supplies' | 'security' | 'internet' | 'other'

export interface Vendor {
  id: string
  name: string
  category: VendorCategory
  category_display: string
  building: string | null
  building_name: string | null
  contact_person: string
  email: string
  phone: string
  gst_number: string
  address: string
  notes: string
  is_active: boolean
  bill_count: number
  created_at: string
  updated_at: string
}

export type VendorBillStatus = 'pending' | 'paid' | 'overdue' | 'cancelled'

export interface VendorBill {
  id: string
  vendor: string
  vendor_name: string
  building: string
  building_name: string
  bill_number: string
  bill_date: string
  due_date: string | null
  amount: string
  tax_amount: string
  total_amount: string
  status: VendorBillStatus
  status_display: string
  paid_at: string | null
  description: string
  attachment: string | null
  notes: string
  created_at: string
  updated_at: string
}

export interface VendorBillSummary {
  total_bills: number
  total_amount: string
  pending_amount: string
  paid_amount: string
  overdue_amount: string
}

// ─── Inventory ────────────────────────────────────────────
export type InventoryCategory =
  | 'pantry' | 'canteen' | 'water' | 'appliance' | 'cleaning' | 'stationery' | 'other'

export interface InventoryItem {
  id: string
  building: string
  building_name: string
  name: string
  category: InventoryCategory
  category_display: string
  unit: string
  quantity: string
  reorder_level: string
  unit_cost: string
  is_low_stock: boolean
  notes: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface StockMovement {
  id: string
  item: string
  item_name: string
  direction: 'in' | 'out'
  direction_display: string
  quantity: string
  reason: string
  performed_by: string | null
  performed_by_name: string | null
  created_at: string
}
