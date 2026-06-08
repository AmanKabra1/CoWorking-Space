'use client'

import { useQuery } from '@tanstack/react-query'
import { PageHeader } from '@/components/shared/PageHeader'
import { StatusBadge } from '@/components/shared/StatusBadge'
import { Card, CardContent } from '@/components/ui/card'
import { bookingService } from '@/lib/services'
import { formatDate, formatTime, formatCurrency } from '@/lib/utils'

export default function BookingsPage() {
  const { data, isLoading } = useQuery({
    queryKey: ['bookings'],
    queryFn: () => bookingService.list(),
  })

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
                    <th className="text-left px-4 py-3 font-medium">Amount</th>
                    <th className="text-left px-4 py-3 font-medium">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {data?.results?.length === 0 && (
                    <tr>
                      <td colSpan={5} className="text-center py-8 text-muted-foreground">
                        No bookings found.
                      </td>
                    </tr>
                  )}
                  {data?.results?.map((booking) => (
                    <tr key={booking.id} className="border-b last:border-0 hover:bg-muted/30 transition-colors">
                      <td className="px-4 py-3 font-medium">{booking.facility_name}</td>
                      <td className="px-4 py-3 text-muted-foreground">{formatDate(booking.start_time)}</td>
                      <td className="px-4 py-3 text-muted-foreground">
                        {formatTime(booking.start_time)} – {formatTime(booking.end_time)}
                      </td>
                      <td className="px-4 py-3">{formatCurrency(booking.total_amount)}</td>
                      <td className="px-4 py-3">
                        <StatusBadge status={booking.status} />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
