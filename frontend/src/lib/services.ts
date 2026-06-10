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
  IncubationProfile,
  Document,
  Notification,
  DashboardData,
  RevenueData,
  ChatRoom,
  ChatMessage,
  Post,
  Event,
  SignatureRequest,
  PaymentGateway,
  PaymentOrder,
  InventoryItem,
  StockMovement,
  Building,
  Vendor,
  VendorBill,
  VendorBillSummary,
  ExportFormat,
  PublicFacility,
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

// ─── Company Settings ─────────────────────────────────────
export const companySettingsService = {
  get: () =>
    api.get<Company>('/companies/settings/').then(r => r.data),
  update: (data: Partial<Company>) =>
    api.patch<Company>('/companies/settings/', data).then(r => r.data),
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
    company?: string
    booking_date: string
    start_time: string
    end_time: string
    attendees_count: number
    purpose: string
  }) => api.post<Booking>('/bookings/', data).then(r => r.data),
  approve: (id: string) =>
    api.post<Booking>(`/bookings/${id}/approve/`).then(r => r.data),
  reject: (id: string, reason: string) =>
    api.post<Booking>(`/bookings/${id}/reject/`, { reason }).then(r => r.data),
  cancel: (id: string) =>
    api.post<Booking>(`/bookings/${id}/cancel/`).then(r => r.data),
  complete: (id: string) =>
    api.post<Booking>(`/bookings/${id}/complete/`).then(r => r.data),
  pendingQueue: () =>
    api.get<PaginatedResponse<Booking>>('/bookings/pending-queue/').then(r => r.data),
  export: (format: ExportFormat) =>
    api.get('/bookings/export/', { params: { fmt: format }, responseType: 'blob' }).then(r => r.data),
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
    api.get<PaginatedResponse<VisitorPass>>('/visitors/passes/', { params }).then(r => r.data.results ?? []),
  create: (data: Partial<VisitorPass>) =>
    api.post<VisitorPass>('/visitors/passes/', data).then(r => r.data),
  approve: (id: string) =>
    api.post<VisitorPass>(`/visitors/passes/${id}/approve/`).then(r => r.data),
  checkIn: (id: string) =>
    api.post<VisitorPass>(`/visitors/passes/${id}/check_in/`).then(r => r.data),
  checkOut: (id: string) =>
    api.post<VisitorPass>(`/visitors/passes/${id}/check_out/`).then(r => r.data),
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
  bookings: () =>
    api.get('/analytics/bookings/').then(r => r.data),
  occupancy: () =>
    api.get('/analytics/occupancy/').then(r => r.data),
  exportRevenue: () =>
    api.get('/analytics/revenue/export/?format=pdf', { responseType: 'blob' }).then(r => r.data),
  downloadReport: (type: 'revenue' | 'bookings', format: 'pdf' | 'excel', params?: Record<string, string>) =>
    api.get(`/analytics/reports/${type}/`, { params: { format, ...params }, responseType: 'blob' }).then(r => r.data),
}

// ─── Incubation ───────────────────────────────────────────
export const incubationService = {
  list: () =>
    api.get<PaginatedResponse<IncubationProfile>>('/incubation/profiles/').then(r => r.data.results ?? []),
  applications: () =>
    api.get('/incubation/applications/').then(r => r.data),
}

// ─── Documents ────────────────────────────────────────────
export const documentService = {
  list: () =>
    api.get<PaginatedResponse<Document>>('/documents/').then(r => r.data.results ?? []),
  upload: (formData: FormData) =>
    api.post<Document>('/documents/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }).then(r => r.data),
  delete: (id: number) =>
    api.delete(`/documents/${id}/`),
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

// ─── Payments ─────────────────────────────────────────────
export const paymentService = {
  getGateway: () =>
    api.get<PaymentGateway>('/payments/gateways/').then(r => r.data),
  saveGateway: (data: Partial<PaymentGateway> & { api_secret?: string }) =>
    api.post<PaymentGateway>('/payments/gateways/', data).then(r => r.data),
  listOrders: (params?: Record<string, string>) =>
    api.get<PaginatedResponse<PaymentOrder>>('/payments/payment-orders/', { params }).then(r => r.data),
  createOrder: (invoiceId: number) =>
    api.post<{ order_id: number; gateway_order_id: string; amount: number; currency: string; key: string; provider: string; client_secret?: string }>(
      '/payments/payment-orders/create_order/', { invoice_id: invoiceId }
    ).then(r => r.data),
  verifyPayment: (orderId: number, data: Record<string, string>) =>
    api.post(`/payments/payment-orders/${orderId}/verify/`, data).then(r => r.data),
}

// ─── Public (no-login) booking ────────────────────────────
export const publicService = {
  facilities: () =>
    api.get<PublicFacility[]>('/public/facilities/').then(r => r.data),
  availability: (facilityId: string, date: string) =>
    api.get<{ booked_slots: { start: string; end: string }[] }>(
      `/public/facilities/${facilityId}/availability/`, { params: { date } }
    ).then(r => r.data),
  createBooking: (data: {
    facility: string
    booking_date: string
    start_time: string
    end_time: string
    attendees_count: number
    purpose: string
    guest_name: string
    guest_email: string
    guest_phone: string
    guest_company?: string
  }) => api.post<{ id: string; status: string; total_amount: string; detail: string }>(
    '/public/bookings/', data
  ).then(r => r.data),
}

// ─── Workspace ────────────────────────────────────────────
export const workspaceService = {
  buildings: () =>
    api.get<PaginatedResponse<Building>>('/workspace/buildings/').then(r => r.data.results ?? []),
}

// ─── Inventory ────────────────────────────────────────────
export const inventoryService = {
  list: (params?: Record<string, string>) =>
    api.get<PaginatedResponse<InventoryItem>>('/inventory/', { params }).then(r => r.data.results ?? []),
  get: (id: string) =>
    api.get<InventoryItem>(`/inventory/${id}/`).then(r => r.data),
  create: (data: Partial<InventoryItem>) =>
    api.post<InventoryItem>('/inventory/', data).then(r => r.data),
  update: (id: string, data: Partial<InventoryItem>) =>
    api.patch<InventoryItem>(`/inventory/${id}/`, data).then(r => r.data),
  remove: (id: string) =>
    api.delete(`/inventory/${id}/`).then(r => r.data),
  restock: (id: string, quantity: number, reason?: string) =>
    api.post<InventoryItem>(`/inventory/${id}/restock/`, { quantity, reason }).then(r => r.data),
  consume: (id: string, quantity: number, reason?: string) =>
    api.post<InventoryItem>(`/inventory/${id}/consume/`, { quantity, reason }).then(r => r.data),
  lowStock: () =>
    api.get<InventoryItem[]>('/inventory/low-stock/').then(r => r.data),
  movements: (id: string) =>
    api.get<StockMovement[]>(`/inventory/${id}/movements/`).then(r => r.data),
  export: (format: ExportFormat) =>
    api.get('/inventory/export/', { params: { fmt: format }, responseType: 'blob' }).then(r => r.data),
}

// ─── Vendors ──────────────────────────────────────────────
export const vendorService = {
  list: (params?: Record<string, string>) =>
    api.get<PaginatedResponse<Vendor>>('/vendors/', { params }).then(r => r.data.results ?? []),
  create: (data: Partial<Vendor>) =>
    api.post<Vendor>('/vendors/', data).then(r => r.data),
  update: (id: string, data: Partial<Vendor>) =>
    api.patch<Vendor>(`/vendors/${id}/`, data).then(r => r.data),
  remove: (id: string) =>
    api.delete(`/vendors/${id}/`).then(r => r.data),
}

export const vendorBillService = {
  list: (params?: Record<string, string>) =>
    api.get<PaginatedResponse<VendorBill>>('/vendors/bills/', { params }).then(r => r.data.results ?? []),
  create: (data: Partial<VendorBill>) =>
    api.post<VendorBill>('/vendors/bills/', data).then(r => r.data),
  update: (id: string, data: Partial<VendorBill>) =>
    api.patch<VendorBill>(`/vendors/bills/${id}/`, data).then(r => r.data),
  remove: (id: string) =>
    api.delete(`/vendors/bills/${id}/`).then(r => r.data),
  markPaid: (id: string) =>
    api.post<VendorBill>(`/vendors/bills/${id}/mark-paid/`).then(r => r.data),
  summary: () =>
    api.get<VendorBillSummary>('/vendors/bills/summary/').then(r => r.data),
  export: (format: ExportFormat) =>
    api.get('/vendors/bills/export/', { params: { fmt: format }, responseType: 'blob' }).then(r => r.data),
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
