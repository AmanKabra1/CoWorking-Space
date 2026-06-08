'use client'

import { useQuery } from '@tanstack/react-query'
import { PageHeader } from '@/components/shared/PageHeader'
import { StatusBadge } from '@/components/shared/StatusBadge'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { maintenanceService } from '@/lib/services'
import { formatDate } from '@/lib/utils'

const PRIORITY_VARIANT: Record<string, 'destructive' | 'warning' | 'info' | 'secondary'> = {
  critical: 'destructive',
  high: 'warning',
  medium: 'info',
  low: 'secondary',
}

export default function MaintenancePage() {
  const { data, isLoading } = useQuery({
    queryKey: ['maintenance'],
    queryFn: () => maintenanceService.list(),
  })

  return (
    <div className="space-y-4">
      <PageHeader title="Maintenance" description="Track and manage maintenance tickets" />

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
                    <th className="text-left px-4 py-3 font-medium">Ticket #</th>
                    <th className="text-left px-4 py-3 font-medium">Title</th>
                    <th className="text-left px-4 py-3 font-medium">Location</th>
                    <th className="text-left px-4 py-3 font-medium">Priority</th>
                    <th className="text-left px-4 py-3 font-medium">Status</th>
                    <th className="text-left px-4 py-3 font-medium">Created</th>
                  </tr>
                </thead>
                <tbody>
                  {data?.results?.length === 0 && (
                    <tr>
                      <td colSpan={6} className="text-center py-8 text-muted-foreground">No tickets found.</td>
                    </tr>
                  )}
                  {data?.results?.map((ticket) => (
                    <tr key={ticket.id} className="border-b last:border-0 hover:bg-muted/30 transition-colors">
                      <td className="px-4 py-3 font-mono text-xs">{ticket.ticket_number}</td>
                      <td className="px-4 py-3 font-medium">{ticket.title}</td>
                      <td className="px-4 py-3 text-muted-foreground">{ticket.location}</td>
                      <td className="px-4 py-3">
                        <Badge variant={PRIORITY_VARIANT[ticket.priority] ?? 'secondary'}>
                          {ticket.priority}
                        </Badge>
                      </td>
                      <td className="px-4 py-3"><StatusBadge status={ticket.status} /></td>
                      <td className="px-4 py-3 text-muted-foreground">{formatDate(ticket.created_at)}</td>
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
