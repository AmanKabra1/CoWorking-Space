'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { PageHeader } from '@/components/shared/PageHeader'
import { ExportButtons } from '@/components/shared/ExportButtons'
import { StatusBadge } from '@/components/shared/StatusBadge'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { bookingService, facilityService, companyService } from '@/lib/services'
import { useAuthStore } from '@/store/auth'
import { formatDate, formatTime, formatCurrency } from '@/lib/utils'
import { toast } from '@/hooks/use-toast'
import type { Booking } from '@/types'

const selectClass =
  'flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring'

export default function BookingsPage() {
  const queryClient = useQueryClient()
  const user = useAuthStore(s => s.user)
  const [pendingId, setPendingId] = useState<string | null>(null)
  const [showForm, setShowForm] = useState(false)
  const isSuperAdmin = user?.role === 'super_admin'

  const [form, setForm] = useState({
    facility: '', company: '', booking_date: '',
    start_time: '', end_time: '', attendees_count: '1', purpose: '',
  })

  const { data, isLoading } = useQuery({
    queryKey: ['bookings'],
    queryFn: () => bookingService.list(),
  })

  const { data: facilities } = useQuery({
    queryKey: ['facilities'],
    queryFn: () => facilityService.list(),
  })

  const { data: companies } = useQuery({
    queryKey: ['companies'],
    queryFn: () => companyService.list(),
    enabled: isSuperAdmin,
  })

  const invalidate = () => queryClient.invalidateQueries({ queryKey: ['bookings'] })

  const createMutation = useMutation({
    mutationFn: () => bookingService.create({
      facility: form.facility,
      ...(isSuperAdmin && form.company ? { company: form.company } : {}),
      booking_date: form.booking_date,
      start_time: form.start_time,
      end_time: form.end_time,
      attendees_count: Number(form.attendees_count) || 1,
      purpose: form.purpose,
    }),
    onSuccess: () => {
      toast({ title: 'Booking requested', description: 'Awaiting approval.' })
      invalidate()
      setShowForm(false)
      setForm({ facility: '', company: '', booking_date: '', start_time: '', end_time: '', attendees_count: '1', purpose: '' })
    },
    onError: (e: unknown) => {
      const data = (e as { response?: { data?: Record<string, string[] | string> } })?.response?.data
      const first = data ? Object.values(data)[0] : null
      const msg = Array.isArray(first) ? first[0] : (first ?? 'Check the fields and try again.')
      toast({ title: 'Could not create booking', description: String(msg), variant: 'destructive' })
    },
  })

  const approveMutation = useMutation({
    mutationFn: (id: string) => bookingService.approve(id),
    onMutate: (id) => setPendingId(id),
    onSuccess: () => { toast({ title: 'Booking approved' }); invalidate() },
    onError: () => toast({ title: 'Could not approve', description: 'You may not have permission.', variant: 'destructive' }),
    onSettled: () => setPendingId(null),
  })

  const rejectMutation = useMutation({
    mutationFn: (id: string) => bookingService.reject(id, ''),
    onMutate: (id) => setPendingId(id),
    onSuccess: () => { toast({ title: 'Booking rejected' }); invalidate() },
    onError: () => toast({ title: 'Could not reject', description: 'You may not have permission.', variant: 'destructive' }),
    onSettled: () => setPendingId(null),
  })

  const cancelMutation = useMutation({
    mutationFn: (id: string) => bookingService.cancel(id),
    onMutate: (id) => setPendingId(id),
    onSuccess: () => { toast({ title: 'Booking cancelled' }); invalidate() },
    onError: () => toast({ title: 'Could not cancel', variant: 'destructive' }),
    onSettled: () => setPendingId(null),
  })

  const confirmMutation = useMutation({
    mutationFn: (id: string) => bookingService.confirm(id),
    onMutate: (id) => setPendingId(id),
    onSuccess: () => { toast({ title: 'Marked paid', description: 'Booking confirmed.' }); invalidate() },
    onError: () => toast({ title: 'Could not confirm', variant: 'destructive' }),
    onSettled: () => setPendingId(null),
  })

  const checkInMutation = useMutation({
    mutationFn: (id: string) => bookingService.checkIn(id),
    onMutate: (id) => setPendingId(id),
    onSuccess: () => { toast({ title: 'Checked in' }); invalidate() },
    onError: () => toast({ title: 'Could not check in', variant: 'destructive' }),
    onSettled: () => setPendingId(null),
  })

  async function openQr(id: string) {
    try {
      const blob = await bookingService.qr(id)
      window.open(URL.createObjectURL(blob), '_blank')
    } catch {
      toast({ title: 'Could not load QR', variant: 'destructive' })
    }
  }

  // Mirror backend CanApproveBooking: super_admin handles all;
  // company_admin handles only their own company's internal bookings.
  function canApprove(b: Booking): boolean {
    if (!user) return false
    if (user.role === 'super_admin') return true
    return b.booking_type === 'internal' && user.role === 'company_admin' && b.company === user.company
  }

  function canCancel(b: Booking): boolean {
    if (!user) return false
    if (['cancelled', 'completed', 'rejected'].includes(b.status)) return false
    return user.role === 'super_admin' || user.role === 'company_admin'
  }

  const showActions = user?.role === 'super_admin' || user?.role === 'company_admin'

  return (
    <div className="space-y-4">
      <PageHeader
        title="Bookings"
        description="Manage facility reservations"
        action={
          <div className="flex items-center gap-2">
            <ExportButtons filename="bookings" onExport={(f) => bookingService.export(f)} />
            <Button onClick={() => setShowForm(v => !v)}>
              {showForm ? 'Close' : 'New Booking'}
            </Button>
          </div>
        }
      />

      {showForm && (
        <Card>
          <CardContent className="p-4">
            <form
              onSubmit={(e) => { e.preventDefault(); createMutation.mutate() }}
              className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4"
            >
              <div className="space-y-1.5">
                <Label>Facility</Label>
                <select
                  className={selectClass}
                  value={form.facility}
                  onChange={(e) => setForm({ ...form, facility: e.target.value })}
                  required
                >
                  <option value="">Select facility…</option>
                  {facilities?.results?.filter(f => f.is_active).map((f) => (
                    <option key={f.id} value={f.id}>
                      {f.name}{f.building_name ? ` — ${f.building_name}` : ''} (cap {f.capacity})
                    </option>
                  ))}
                </select>
              </div>

              {isSuperAdmin && (
                <div className="space-y-1.5">
                  <Label>Company</Label>
                  <select
                    className={selectClass}
                    value={form.company}
                    onChange={(e) => setForm({ ...form, company: e.target.value })}
                    required
                  >
                    <option value="">Select company…</option>
                    {companies?.results?.map((c) => (
                      <option key={c.id} value={c.id}>{c.name}</option>
                    ))}
                  </select>
                </div>
              )}

              <div className="space-y-1.5">
                <Label>Date</Label>
                <Input type="date" value={form.booking_date} onChange={(e) => setForm({ ...form, booking_date: e.target.value })} required />
              </div>
              <div className="space-y-1.5">
                <Label>Start time</Label>
                <Input type="time" value={form.start_time} onChange={(e) => setForm({ ...form, start_time: e.target.value })} required />
              </div>
              <div className="space-y-1.5">
                <Label>End time</Label>
                <Input type="time" value={form.end_time} onChange={(e) => setForm({ ...form, end_time: e.target.value })} required />
              </div>
              <div className="space-y-1.5">
                <Label>Attendees</Label>
                <Input type="number" min="1" value={form.attendees_count} onChange={(e) => setForm({ ...form, attendees_count: e.target.value })} />
              </div>
              <div className="space-y-1.5 sm:col-span-2">
                <Label>Purpose</Label>
                <Input value={form.purpose} onChange={(e) => setForm({ ...form, purpose: e.target.value })} placeholder="e.g. Team standup" required />
              </div>
              <div className="flex items-end">
                <Button type="submit" disabled={createMutation.isPending}>
                  {createMutation.isPending ? 'Submitting…' : 'Request Booking'}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      {isLoading ? (
        <div className="space-y-3">
          {[...Array(5)].map((_, i) => <div key={i} className="h-16 bg-muted rounded-lg animate-pulse" />)}
        </div>
      ) : (
        <Card>
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b bg-muted/50">
                    <th className="text-left px-4 py-3 font-medium">Facility</th>
                    <th className="text-left px-4 py-3 font-medium">Date</th>
                    <th className="text-left px-4 py-3 font-medium">Time</th>
                    <th className="text-left px-4 py-3 font-medium">Type</th>
                    <th className="text-left px-4 py-3 font-medium">Amount</th>
                    <th className="text-left px-4 py-3 font-medium">Status</th>
                    {showActions && <th className="text-right px-4 py-3 font-medium">Actions</th>}
                  </tr>
                </thead>
                <tbody>
                  {data?.results?.length === 0 && (
                    <tr>
                      <td colSpan={showActions ? 7 : 6} className="text-center py-8 text-muted-foreground">
                        No bookings found.
                      </td>
                    </tr>
                  )}
                  {data?.results?.map((booking) => {
                    const busy = pendingId === booking.id
                    return (
                      <tr key={booking.id} className="border-b last:border-0 hover:bg-muted/30 transition-colors">
                        <td className="px-4 py-3 font-medium">{booking.facility_name}</td>
                        <td className="px-4 py-3 text-muted-foreground">{formatDate(booking.booking_date)}</td>
                        <td className="px-4 py-3 text-muted-foreground">
                          {formatTime(booking.start_time)} – {formatTime(booking.end_time)}
                        </td>
                        <td className="px-4 py-3">
                          <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${booking.booking_type === 'internal' ? 'bg-blue-100 text-blue-700' : 'bg-amber-100 text-amber-700'}`}>
                            {booking.booking_type === 'internal' ? 'Internal · Free' : 'External · Paid'}
                          </span>
                        </td>
                        <td className="px-4 py-3">
                          {booking.payment_required ? formatCurrency(booking.total_amount) : '—'}
                        </td>
                        <td className="px-4 py-3">
                          <StatusBadge status={booking.status} />
                        </td>
                        {showActions && (
                          <td className="px-4 py-3">
                            <div className="flex justify-end gap-2">
                              {booking.status === 'pending' && canApprove(booking) && (
                                <>
                                  <Button
                                    size="sm"
                                    disabled={busy}
                                    onClick={() => approveMutation.mutate(booking.id)}
                                  >
                                    Approve
                                  </Button>
                                  <Button
                                    size="sm"
                                    variant="destructive"
                                    disabled={busy}
                                    onClick={() => rejectMutation.mutate(booking.id)}
                                  >
                                    Reject
                                  </Button>
                                </>
                              )}
                              {booking.status === 'approved' && booking.payment_required && canApprove(booking) && (
                                <Button
                                  size="sm"
                                  disabled={busy}
                                  onClick={() => confirmMutation.mutate(booking.id)}
                                >
                                  Mark Paid
                                </Button>
                              )}
                              {(booking.status === 'approved' || booking.status === 'confirmed') && (
                                <Button size="sm" variant="outline" disabled={busy} onClick={() => openQr(booking.id)}>
                                  QR
                                </Button>
                              )}
                              {(booking.status === 'approved' || booking.status === 'confirmed') && canApprove(booking) && (
                                booking.checked_in_at ? (
                                  <span className="text-xs text-green-600 self-center">✓ In</span>
                                ) : (
                                  <Button size="sm" variant="outline" disabled={busy} onClick={() => checkInMutation.mutate(booking.id)}>
                                    Check in
                                  </Button>
                                )
                              )}
                              {canCancel(booking) && booking.status !== 'pending' && (
                                <Button
                                  size="sm"
                                  variant="outline"
                                  disabled={busy}
                                  onClick={() => cancelMutation.mutate(booking.id)}
                                >
                                  Cancel
                                </Button>
                              )}
                            </div>
                          </td>
                        )}
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
