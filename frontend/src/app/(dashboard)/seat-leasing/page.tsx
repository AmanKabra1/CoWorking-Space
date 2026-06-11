'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { PageHeader } from '@/components/shared/PageHeader'
import { StatusBadge } from '@/components/shared/StatusBadge'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { seatLeaseService } from '@/lib/services'
import { useAuthStore } from '@/store/auth'
import { formatCurrency, formatDate } from '@/lib/utils'
import { toast } from '@/hooks/use-toast'

const selectClass =
  'flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring'

export default function SeatLeasingPage() {
  const queryClient = useQueryClient()
  const isCompanyAdmin = useAuthStore(s => s.user?.role === 'company_admin')
  const [showForm, setShowForm] = useState(false)
  const [pendingId, setPendingId] = useState<string | null>(null)
  const [form, setForm] = useState({
    desk: '', lessee_name: '', lessee_email: '', lessee_phone: '', lessee_company: '',
    start_date: '', end_date: '', monthly_rate: '0', notes: '',
  })

  const { data: leases = [], isLoading } = useQuery({
    queryKey: ['seat-leases'],
    queryFn: () => seatLeaseService.list(),
  })

  const { data: desks = [] } = useQuery({
    queryKey: ['available-desks'],
    queryFn: () => seatLeaseService.availableDesks(),
  })

  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ['seat-leases'] })
    queryClient.invalidateQueries({ queryKey: ['available-desks'] })
  }

  const createMutation = useMutation({
    mutationFn: () => seatLeaseService.create({
      desk: form.desk,
      lessee_name: form.lessee_name,
      lessee_email: form.lessee_email || undefined,
      lessee_phone: form.lessee_phone || undefined,
      lessee_company: form.lessee_company || undefined,
      start_date: form.start_date,
      end_date: form.end_date || null,
      monthly_rate: form.monthly_rate,
      notes: form.notes || undefined,
    }),
    onSuccess: () => {
      toast({ title: 'Seat sub-leased' })
      invalidate()
      setShowForm(false)
      setForm({ desk: '', lessee_name: '', lessee_email: '', lessee_phone: '', lessee_company: '', start_date: '', end_date: '', monthly_rate: '0', notes: '' })
    },
    onError: (e: unknown) => {
      const data = (e as { response?: { data?: Record<string, string[] | string> } })?.response?.data
      const first = data ? Object.values(data)[0] : null
      const msg = Array.isArray(first) ? first[0] : (first ?? 'Check the fields and try again.')
      toast({ title: 'Could not create sub-lease', description: String(msg), variant: 'destructive' })
    },
  })

  const endMutation = useMutation({
    mutationFn: (id: string) => seatLeaseService.end(id),
    onMutate: (id) => setPendingId(id),
    onSuccess: () => { toast({ title: 'Sub-lease ended' }); invalidate() },
    onError: () => toast({ title: 'Could not end sub-lease', variant: 'destructive' }),
    onSettled: () => setPendingId(null),
  })

  return (
    <div className="space-y-4">
      <PageHeader
        title="Seat Leasing"
        description="Sub-lease your company's spare desks to other tenants"
        action={!isCompanyAdmin ? undefined :
          <Button onClick={() => setShowForm(v => !v)} disabled={desks.length === 0 && !showForm}>
            {showForm ? 'Close' : 'Sub-lease a Seat'}
          </Button>
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
                <Label>Desk</Label>
                <select className={selectClass} value={form.desk} onChange={(e) => setForm({ ...form, desk: e.target.value })} required>
                  <option value="">Select a desk…</option>
                  {desks.map((d) => (
                    <option key={d.id} value={d.id}>{d.desk_code} — {d.location}</option>
                  ))}
                </select>
              </div>
              <div className="space-y-1.5">
                <Label>Sub-tenant name</Label>
                <Input value={form.lessee_name} onChange={(e) => setForm({ ...form, lessee_name: e.target.value })} required />
              </div>
              <div className="space-y-1.5">
                <Label>Sub-tenant company</Label>
                <Input value={form.lessee_company} onChange={(e) => setForm({ ...form, lessee_company: e.target.value })} />
              </div>
              <div className="space-y-1.5">
                <Label>Email</Label>
                <Input type="email" value={form.lessee_email} onChange={(e) => setForm({ ...form, lessee_email: e.target.value })} />
              </div>
              <div className="space-y-1.5">
                <Label>Phone</Label>
                <Input value={form.lessee_phone} onChange={(e) => setForm({ ...form, lessee_phone: e.target.value })} />
              </div>
              <div className="space-y-1.5">
                <Label>Monthly rate (₹)</Label>
                <Input type="number" step="0.01" value={form.monthly_rate} onChange={(e) => setForm({ ...form, monthly_rate: e.target.value })} />
              </div>
              <div className="space-y-1.5">
                <Label>Start date</Label>
                <Input type="date" value={form.start_date} onChange={(e) => setForm({ ...form, start_date: e.target.value })} required />
              </div>
              <div className="space-y-1.5">
                <Label>End date (optional)</Label>
                <Input type="date" value={form.end_date} onChange={(e) => setForm({ ...form, end_date: e.target.value })} />
              </div>
              <div className="flex items-end">
                <Button type="submit" disabled={createMutation.isPending}>
                  {createMutation.isPending ? 'Saving…' : 'Create Sub-lease'}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      {isLoading ? (
        <div className="space-y-3">
          {[...Array(4)].map((_, i) => <div key={i} className="h-16 bg-muted rounded-lg animate-pulse" />)}
        </div>
      ) : (
        <Card>
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b bg-muted/50">
                    <th className="text-left px-4 py-3 font-medium">Desk</th>
                    <th className="text-left px-4 py-3 font-medium">Sub-tenant</th>
                    <th className="text-left px-4 py-3 font-medium">Period</th>
                    <th className="text-right px-4 py-3 font-medium">Rate/mo</th>
                    <th className="text-left px-4 py-3 font-medium">Status</th>
                    <th className="text-right px-4 py-3 font-medium">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {leases.length === 0 && (
                    <tr>
                      <td colSpan={6} className="text-center py-8 text-muted-foreground">
                        No sub-leases yet. Click “Sub-lease a Seat” to start.
                      </td>
                    </tr>
                  )}
                  {leases.map((lease) => (
                    <tr key={lease.id} className="border-b last:border-0 hover:bg-muted/30 transition-colors">
                      <td className="px-4 py-3">
                        <div className="font-medium">{lease.desk_code}</div>
                        <div className="text-xs text-muted-foreground">{lease.desk_location}</div>
                      </td>
                      <td className="px-4 py-3">
                        <div>{lease.lessee_name}</div>
                        <div className="text-xs text-muted-foreground">{lease.lessee_company || '—'}</div>
                      </td>
                      <td className="px-4 py-3 text-muted-foreground">
                        {formatDate(lease.start_date)}{lease.end_date ? ` – ${formatDate(lease.end_date)}` : ' →'}
                      </td>
                      <td className="px-4 py-3 text-right font-medium">{formatCurrency(lease.monthly_rate)}</td>
                      <td className="px-4 py-3"><StatusBadge status={lease.status} /></td>
                      <td className="px-4 py-3">
                        <div className="flex justify-end">
                          {lease.status === 'active' && isCompanyAdmin && (
                            <Button size="sm" variant="outline" disabled={pendingId === lease.id} onClick={() => endMutation.mutate(lease.id)}>
                              End
                            </Button>
                          )}
                        </div>
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
