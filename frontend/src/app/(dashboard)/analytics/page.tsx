'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useQuery, useMutation } from '@tanstack/react-query'
import { PageHeader } from '@/components/shared/PageHeader'
import { KPICard } from '@/components/shared/KPICard'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { analyticsService } from '@/lib/services'
import { useAuthStore } from '@/store/auth'
import { formatCurrency } from '@/lib/utils'
import { DollarSign, CalendarCheck, BarChart2 } from 'lucide-react'

export default function AnalyticsPage() {
  const router = useRouter()
  const user = useAuthStore(s => s.user)

  useEffect(() => {
    if (user && user.role === 'employee') {
      router.replace('/dashboard')
    }
  }, [user, router])

  const { data: revenueData, isLoading: loadingRevenue } = useQuery({
    queryKey: ['analytics', 'revenue'],
    queryFn: () => analyticsService.revenue(),
    enabled: user?.role !== 'employee',
  })

  const { data: bookingsData, isLoading: loadingBookings } = useQuery({
    queryKey: ['analytics', 'bookings'],
    queryFn: () => analyticsService.bookings(),
    enabled: user?.role !== 'employee',
  })

  const { data: occupancyData, isLoading: loadingOccupancy } = useQuery({
    queryKey: ['analytics', 'occupancy'],
    queryFn: () => analyticsService.occupancy(),
    enabled: user?.role !== 'employee',
  })

  const exportMutation = useMutation({
    mutationFn: () => analyticsService.exportRevenue(),
    onSuccess: (blob) => {
      const url = URL.createObjectURL(blob as Blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'revenue-report.pdf'
      a.click()
      URL.revokeObjectURL(url)
    },
  })

  if (user?.role === 'employee') return null

  const isLoading = loadingRevenue || loadingBookings || loadingOccupancy

  const totalRevenue: number = revenueData?.totals?.paid ?? revenueData?.total_paid ?? 0
  const totalBookings: number = bookingsData?.total ?? 0
  const avgOccupancy: number = occupancyData?.average_rate ?? 0

  const revenueRows: { label: string; amount: number }[] = (() => {
    if (revenueData?.by_company) {
      return (revenueData.by_company as { company_name?: string; name?: string; total?: number; amount?: number }[]).map((r) => ({
        label: r.company_name ?? r.name ?? '—',
        amount: r.total ?? r.amount ?? 0,
      }))
    }
    if (revenueData?.by_period) {
      return (revenueData.by_period as { period: string; paid?: number; invoiced?: number }[]).map((r) => ({
        label: r.period,
        amount: r.paid ?? r.invoiced ?? 0,
      }))
    }
    if (revenueData?.monthly) {
      return (revenueData.monthly as { month?: string; period?: string; amount?: number; paid?: number }[]).map((r) => ({
        label: r.month ?? r.period ?? '—',
        amount: r.amount ?? r.paid ?? 0,
      }))
    }
    return []
  })()

  return (
    <div className="space-y-6">
      <PageHeader
        title="Analytics"
        description="Revenue, bookings, and occupancy overview"
        action={
          <Button onClick={() => exportMutation.mutate()} disabled={exportMutation.isPending}>
            {exportMutation.isPending ? 'Exporting…' : 'Export PDF'}
          </Button>
        }
      />

      {isLoading ? (
        <div className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="h-28 bg-muted rounded-lg animate-pulse" />
            ))}
          </div>
          <div className="h-64 bg-muted rounded-lg animate-pulse" />
        </div>
      ) : (
        <>
          {/* KPI cards */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <KPICard
              title="Total Revenue"
              value={formatCurrency(totalRevenue)}
              icon={DollarSign}
            />
            <KPICard
              title="Total Bookings"
              value={totalBookings}
              icon={CalendarCheck}
            />
            <KPICard
              title="Avg Occupancy"
              value={`${avgOccupancy}%`}
              icon={BarChart2}
            />
          </div>

          {/* Revenue breakdown */}
          {revenueRows.length > 0 && (
            <Card>
              <CardContent className="p-0">
                <div className="px-4 py-3 border-b bg-muted/50">
                  <h2 className="text-sm font-semibold">Revenue Breakdown</h2>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b bg-muted/30">
                        <th className="text-left px-4 py-3 font-medium">Period / Company</th>
                        <th className="text-right px-4 py-3 font-medium">Amount</th>
                      </tr>
                    </thead>
                    <tbody>
                      {revenueRows.map((row, i) => (
                        <tr key={i} className="border-b last:border-0 hover:bg-muted/20 transition-colors">
                          <td className="px-4 py-3 text-muted-foreground">{row.label}</td>
                          <td className="px-4 py-3 text-right font-medium">{formatCurrency(row.amount)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Booking status breakdown */}
          {bookingsData && (
            <Card>
              <CardContent className="p-6">
                <h2 className="text-sm font-semibold mb-4">Booking Status Breakdown</h2>
                <div className="flex flex-wrap gap-4">
                  {bookingsData.approved != null && (
                    <div className="flex items-center gap-2">
                      <Badge variant="success">Approved</Badge>
                      <span className="text-sm font-medium">{bookingsData.approved}</span>
                    </div>
                  )}
                  {bookingsData.pending != null && (
                    <div className="flex items-center gap-2">
                      <Badge variant="warning">Pending</Badge>
                      <span className="text-sm font-medium">{bookingsData.pending}</span>
                    </div>
                  )}
                  {bookingsData.cancelled != null && (
                    <div className="flex items-center gap-2">
                      <Badge variant="secondary">Cancelled</Badge>
                      <span className="text-sm font-medium">{bookingsData.cancelled}</span>
                    </div>
                  )}
                  {bookingsData.completed != null && (
                    <div className="flex items-center gap-2">
                      <Badge variant="info">Completed</Badge>
                      <span className="text-sm font-medium">{bookingsData.completed}</span>
                    </div>
                  )}
                  {bookingsData.rejected != null && (
                    <div className="flex items-center gap-2">
                      <Badge variant="destructive">Rejected</Badge>
                      <span className="text-sm font-medium">{bookingsData.rejected}</span>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          )}
        </>
      )}
    </div>
  )
}
