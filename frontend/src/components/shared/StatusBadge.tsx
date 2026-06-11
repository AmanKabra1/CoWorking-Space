import { Badge } from '@/components/ui/badge'

const STATUS_VARIANTS: Record<string, 'default' | 'secondary' | 'destructive' | 'success' | 'warning' | 'info' | 'outline'> = {
  // Booking
  pending: 'warning',
  approved: 'info',
  confirmed: 'success',
  rejected: 'destructive',
  cancelled: 'secondary',
  completed: 'info',
  // Invoice
  draft: 'secondary',
  sent: 'info',
  paid: 'success',
  overdue: 'destructive',
  // Maintenance
  open: 'warning',
  in_progress: 'info',
  resolved: 'success',
  closed: 'secondary',
  // Visitor
  expected: 'info',
  checked_in: 'success',
  checked_out: 'secondary',
  // Seat leasing / leases
  active: 'success',
  ended: 'secondary',
  expired: 'destructive',
  terminated: 'secondary',
  // Incubation
  submitted: 'info',
  under_review: 'warning',
  accepted: 'success',
  withdrawn: 'secondary',
}

export function StatusBadge({ status }: { status: string }) {
  const variant = STATUS_VARIANTS[status] ?? 'outline'
  const label = status.replace(/_/g, ' ')
  return <Badge variant={variant}>{label}</Badge>
}
