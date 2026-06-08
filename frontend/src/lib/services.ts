import api from './api'
import type {
  PaginatedResponse,
  User,
  Company,
  Facility,
  Booking,
  Invoice,
  MaintenanceTicket,
  VisitorPass,
  Notification,
  DashboardData,
  RevenueData,
  ChatRoom,
  ChatMessage,
  Post,
  Event,
  SignatureRequest,
} from '@/types'

// ─── Auth ─────────────────────────────────────────────────
export const authService = {
  login: (email: string, password: string) =>
    api.post<{ user: User; tokens: { access: string; refresh: string } }>('/auth/login/', { email, password }).then(r => r.data),
  logout: (refresh: string) =>
    api.post('/auth/logout/', { refresh }),
  me: () =>
    api.get<User>('/auth/me/').then(r => r.data),
  changePassword: (current: string, newPass: string, confirm: string) =>
    api.post('/auth/change-password/', {
      current_password: current,
      new_password: newPass,
      confirm_password: confirm,
    }),
}

// ─── Companies ────────────────────────────────────────────
export const companyService = {
  list: (params?: Record<string, string>) =>
    api.get<PaginatedResponse<Company>>('/companies/', { params }).then(r => r.data),
  get: (id: string) =>
    api.get<Company>(`/companies/${id}/`).then(r => r.data),
  create: (data: Partial<Company>) =>
    api.post<Company>('/companies/', data).then(r => r.data),
  update: (id: string, data: Partial<Company>) =>
    api.patch<Company>(`/companies/${id}/`, data).then(r => r.data),
  setStatus: (id: string, status: string) =>
    api.patch(`/companies/${id}/status/`, { status }),
}

// ─── Facilities ───────────────────────────────────────────
export const facilityService = {
  list: (params?: Record<string, string>) =>
    api.get<PaginatedResponse<Facility>>('/facilities/', { params }).then(r => r.data),
  get: (id: string) =>
    api.get<Facility>(`/facilities/${id}/`).then(r => r.data),
  availability: (id: string, date: string) =>
    api.get<{ booked_slots: { start: string; end: string }[] }>(
      `/facilities/${id}/availability/`, { params: { date } }
    ).then(r => r.data),
}

// ─── Bookings ─────────────────────────────────────────────
export const bookingService = {
  list: (params?: Record<string, string>) =>
    api.get<PaginatedResponse<Booking>>('/bookings/', { params }).then(r => r.data),
  get: (id: string) =>
    api.get<Booking>(`/bookings/${id}/`).then(r => r.data),
  create: (data: {
    facility: string
    company: string
    booking_date: string
    start_time: string
    end_time: string
    attendees: number
    purpose: string
  }) => api.post<Booking>('/bookings/', data).then(r => r.data),
  approve: (id: string) =>
    api.post<Booking>(`/bookings/${id}/approve/`).then(r => r.data),
  reject: (id: string, reason: string) =>
    api.post<Booking>(`/bookings/${id}/reject/`, { reason }).then(r => r.data),
  cancel: (id: string) =>
    api.post<Booking>(`/bookings/${id}/cancel/`).then(r => r.data),
  pendingQueue: () =>
    api.get<PaginatedResponse<Booking>>('/bookings/pending-queue/').then(r => r.data),
}

// ─── Billing ──────────────────────────────────────────────
export const invoiceService = {
  list: (params?: Record<string, string>) =>
    api.get<PaginatedResponse<Invoice>>('/billing/invoices/', { params }).then(r => r.data),
  get: (id: string) =>
    api.get<Invoice>(`/billing/invoices/${id}/`).then(r => r.data),
  downloadPdf: (id: string) =>
    api.get(`/billing/invoices/${id}/download-pdf/`, { responseType: 'blob' }).then(r => r.data),
  send: (id: string) =>
    api.post<Invoice>(`/billing/invoices/${id}/send/`).then(r => r.data),
  recordPayment: (id: string, data: { amount: string; method: string; reference?: string }) =>
    api.post<Invoice>(`/billing/invoices/${id}/record-payment/`, data).then(r => r.data),
}

// ─── Maintenance ──────────────────────────────────────────
export const maintenanceService = {
  list: (params?: Record<string, string>) =>
    api.get<PaginatedResponse<MaintenanceTicket>>('/maintenance/tickets/', { params }).then(r => r.data),
  create: (data: {
    company: string
    title: string
    description: string
    category: string
    priority: string
    building?: string
  }) => api.post<MaintenanceTicket>('/maintenance/tickets/', data).then(r => r.data),
  assign: (id: string, userId: string) =>
    api.post<MaintenanceTicket>(`/maintenance/tickets/${id}/assign/`, { assigned_to: userId }),
  resolve: (id: string, notes: string) =>
    api.post<MaintenanceTicket>(`/maintenance/tickets/${id}/resolve/`, { resolution_notes: notes }),
}

// ─── Visitors ─────────────────────────────────────────────
export const visitorService = {
  list: (params?: Record<string, string>) =>
    api.get<PaginatedResponse<VisitorPass>>('/visitors/passes/', { params }).then(r => r.data),
  create: (data: Partial<VisitorPass> & { host: string; company: string }) =>
    api.post<VisitorPass>('/visitors/passes/', data).then(r => r.data),
  checkIn: (id: string) =>
    api.post<VisitorPass>(`/visitors/passes/${id}/check-in/`).then(r => r.data),
  checkOut: (id: string) =>
    api.post<VisitorPass>(`/visitors/passes/${id}/check-out/`).then(r => r.data),
  verify: (code: string) =>
    api.get(`/visitors/verify/${code}/`).then(r => r.data),
}

// ─── Notifications ────────────────────────────────────────
export const notificationService = {
  list: () =>
    api.get<PaginatedResponse<Notification>>('/notifications/').then(r => r.data),
  unreadCount: () =>
    api.get<{ unread_count: number }>('/notifications/unread-count/').then(r => r.data),
  markRead: (id: string) =>
    api.post(`/notifications/${id}/mark-read/`),
  markAllRead: () =>
    api.post('/notifications/mark-all-read/'),
}

// ─── Analytics ────────────────────────────────────────────
export const analyticsService = {
  dashboard: () =>
    api.get<DashboardData>('/analytics/dashboard/').then(r => r.data),
  revenue: (params?: { start?: string; end?: string; period?: string }) =>
    api.get<RevenueData>('/analytics/revenue/', { params }).then(r => r.data),
  downloadReport: (type: 'revenue' | 'bookings', format: 'pdf' | 'excel', params?: Record<string, string>) =>
    api.get(`/analytics/reports/${type}/`, { params: { format, ...params }, responseType: 'blob' }).then(r => r.data),
}

// ─── Chat ─────────────────────────────────────────────────
export const chatService = {
  getGeneralRoom: () =>
    api.get<ChatRoom>('/chat/rooms/company-general/').then(r => r.data),
  listRooms: () =>
    api.get<PaginatedResponse<ChatRoom>>('/chat/rooms/').then(r => r.data),
  listMessages: (roomId: string) =>
    api.get<PaginatedResponse<ChatMessage>>('/chat/messages/', { params: { room: roomId } }).then(r => r.data),
}

// ─── Community ────────────────────────────────────────────
export const communityService = {
  listPosts: (params?: Record<string, string>) =>
    api.get<PaginatedResponse<Post>>('/community/posts/', { params }).then(r => r.data),
  listEvents: () =>
    api.get<PaginatedResponse<Event>>('/community/events/').then(r => r.data),
  rsvp: (eventId: string, status: string) =>
    api.post(`/community/events/${eventId}/rsvp/`, { status }).then(r => r.data),
}

// ─── E-Sign ───────────────────────────────────────────────
export const esignService = {
  list: () =>
    api.get<PaginatedResponse<SignatureRequest>>('/esign/requests/').then(r => r.data),
  create: (data: FormData) =>
    api.post<SignatureRequest>('/esign/requests/', data, { headers: { 'Content-Type': 'multipart/form-data' } }).then(r => r.data),
  cancel: (id: string) =>
    api.post(`/esign/requests/${id}/cancel/`).then(r => r.data),
}
