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
  email: string
  phone: string
  industry?: string
  status: 'pending' | 'active' | 'suspended'
  is_active: boolean
  employee_count: number
  created_at: string
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
  purpose: string
  host_name: string
  building_name: string | null
  pass_code: string
  status: 'expected' | 'checked_in' | 'checked_out' | 'cancelled'
  scheduled_date: string
  valid_from: string
  valid_until: string
  checked_in_at: string | null
  checked_out_at: string | null
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
  by_period: { period: string; invoiced: number; invoice_count: number }[]
  totals: { invoiced: number; paid: number; invoice_count: number }
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
