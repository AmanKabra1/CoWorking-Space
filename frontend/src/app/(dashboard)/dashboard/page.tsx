'use client'

import { useQuery } from '@tanstack/react-query'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { Building2, CalendarDays, FileText, Users } from 'lucide-react'
import { KPICard } from '@/components/shared/KPICard'
import { PageHeader } from '@/components/shared/PageHeader'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { analyticsService } from '@/lib/services'
import { formatCurrency } from '@/lib/utils'

export default function DashboardPage() {
  const { data: dash, isLoading: dashLoading } = useQuery({
    queryKey: ['dashboard'],
    queryFn: analyticsService.dashboard,
  })

  const { data: revenue } = useQuery({
    queryKey: ['revenue-analytics', 'month'],
    queryFn: () => analyticsService.revenue({ period: 'month' }),
  })

  if (dashLoading) {
    return (
      <div className="animate-pulse space-y-4">
        <div className="h-8 bg-muted rounded w-48" />
        <div className="grid grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => <div key={i} className="h-32 bg-muted rounded-lg" />)}
        </div>
      </div>
    )
  }

  const kpis = [
    { title: 'Total Revenue', value: formatCurrency(dash?.revenue.total_paid ?? 0), icon: FileText },
    { title: 'Active Bookings', value: dash?.bookings.approved ?? 0, icon: CalendarDays },
    { title: 'Facilities', value: dash?.platform?.total_facilities ?? 0, icon: Building2 },
    { title: 'Companies', value: dash?.platform?.total_companies ?? 0, icon: Users },
  ]

  const bookingSummary = dash?.bookings
    ? Object.entries(dash.bookings).filter(([k]) => k !== 'total')
    : []

  return (
    <div className="space-y-6">
      <PageHeader title="Dashboard" description="Overview of your coworking space" />

      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        {kpis.map((kpi) => (
          <KPICard key={kpi.title} {...kpi} />
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Monthly Revenue</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={revenue?.by_period ?? []}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                <XAxis dataKey="period" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip formatter={(v: number) => [formatCurrency(v), 'Revenue']} />
                <Bar dataKey="invoiced" fill="hsl(var(--primary))" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Booking Status Breakdown</CardTitle>
          </CardHeader>
          <CardContent className="pt-2">
            {bookingSummary.length > 0 ? (
              <div className="space-y-3">
                {bookingSummary.map(([status, count]) => (
                  <div key={status} className="flex items-center justify-between text-sm">
                    <span className="capitalize text-muted-foreground">{status.replace(/_/g, ' ')}</span>
                    <span className="font-semibold">{count as number}</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">No data available</p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
