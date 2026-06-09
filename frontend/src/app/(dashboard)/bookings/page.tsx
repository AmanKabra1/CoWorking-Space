'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { PageHeader } from '@/components/shared/PageHeader'
import { StatusBadge } from '@/components/shared/StatusBadge'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { bookingService } from '@/lib/services'
import { useAuthStore } from '@/store/auth'
import { formatDate, formatTime, formatCurrency } from '@/lib/utils'
import { toast } from '@/hooks/use-toast'
import type { Booking } from '@/types'

export default function BookingsPage() {
  const queryClient = useQueryClient()
  const user = useAuthStore(s => s.user)
  const [pendingId, setPendingId] = useState<string | null>(null)

  const { data, isLoading } = useQuery({
    queryKey: ['bookings'],
    queryFn: () => bookingService.list(),
  })

  const invalidate = () => queryClient.invalidateQueries({ queryKey: ['bookings'] })

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
      <PageHeader title="Bookings" description="Manage facility reservations" />

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
