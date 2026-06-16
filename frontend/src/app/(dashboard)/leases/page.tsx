'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { PageHeader } from '@/components/shared/PageHeader'
import { StatusBadge } from '@/components/shared/StatusBadge'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { leaseService, companyService, workspaceService } from '@/lib/services'
import { useAuthStore } from '@/store/auth'
import { formatCurrency, formatDate } from '@/lib/utils'
import { Spinner } from '@/components/shared/Spinner'
import { toast } from '@/hooks/use-toast'

const selectClass =
  'flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring'

export default function LeasesPage() {
  const queryClient = useQueryClient()
  const isSuperAdmin = useAuthStore(s => s.user?.role === 'super_admin')
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({
    company: '', building: '', floor: '', seats_leased: '',
    start_date: '', end_date: '', monthly_rate: '', notes: '',
  })

  const { data: leases = [], isLoading } = useQuery({
    queryKey: ['leases'],
    queryFn: () => leaseService.list(),
  })

  const { data: companies = [] } = useQuery({
    queryKey: ['companies'],
    queryFn: () => companyService.list().then(r => r.results ?? []),
    enabled: isSuperAdmin,
  })

  const { data: buildings = [] } = useQuery({
    queryKey: ['buildings'],
    queryFn: () => workspaceService.buildings(),
    enabled: isSuperAdmin,
  })

  const { data: floors = [] } = useQuery({
    queryKey: ['floors', form.building],
    queryFn: () => workspaceService.floors(form.building),
    enabled: isSuperAdmin && Boolean(form.building),
  })

  const createMutation = useMutation({
    mutationFn: () => leaseService.create({
      company: form.company,
      building: form.building,
      floor: form.floor || null,
      seats_leased: Number(form.seats_leased) || 0,
      start_date: form.start_date,
      end_date: form.end_date || null,
      monthly_rate: form.monthly_rate || '0',
      notes: form.notes || undefined,
    }),
    onSuccess: () => {
      toast({ title: 'Lease created' })
      queryClient.invalidateQueries({ queryKey: ['leases'] })
      setShowForm(false)
      setForm({ company: '', building: '', floor: '', seats_leased: '', start_date: '', end_date: '', monthly_rate: '', notes: '' })
    },
    onError: (e: unknown) => {
      const data = (e as { response?: { data?: Record<string, string[] | string> } })?.response?.data
      const first = data ? Object.values(data)[0] : null
      const msg = Array.isArray(first) ? first[0] : (first ?? 'Check the fields.')
      toast({ title: 'Could not create lease', description: String(msg), variant: 'destructive' })
    },
  })

  return (
    <div className="space-y-4">
      <PageHeader
        title="Leases"
        description={isSuperAdmin ? 'Lease agreements — which company leases which floor/seats' : 'Your lease agreements'}
        action={isSuperAdmin ? (
          <Button onClick={() => setShowForm(v => !v)}>{showForm ? 'Close' : 'New Lease'}</Button>
        ) : undefined}
      />

      {showForm && isSuperAdmin && (
        <Card>
          <CardContent className="p-4">
            <form onSubmit={(e) => { e.preventDefault(); createMutation.mutate() }} className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              <fieldset disabled={createMutation.isPending} className="contents">
              <div className="space-y-1.5">
                <Label>Company (tenant)</Label>
                <select className={selectClass} value={form.company} onChange={(e) => setForm({ ...form, company: e.target.value })} required>
                  <option value="">Select company…</option>
                  {companies.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
                </select>
              </div>
              <div className="space-y-1.5">
                <Label>Building</Label>
                <select className={selectClass} value={form.building} onChange={(e) => setForm({ ...form, building: e.target.value, floor: '' })} required>
                  <option value="">Select building…</option>
                  {buildings.map((b) => <option key={b.id} value={b.id}>{b.name}</option>)}
                </select>
              </div>
              <div className="space-y-1.5">
                <Label>Floor (optional)</Label>
                <select className={selectClass} value={form.floor} onChange={(e) => setForm({ ...form, floor: e.target.value })} disabled={!form.building}>
                  <option value="">—</option>
                  {floors.map((f) => <option key={f.id} value={f.id}>{f.name}</option>)}
                </select>
              </div>
              <div className="space-y-1.5">
                <Label>Seats leased</Label>
                <Input type="number" min="0" placeholder="0" value={form.seats_leased} onChange={(e) => setForm({ ...form, seats_leased: e.target.value })} />
              </div>
              <div className="space-y-1.5">
                <Label>Monthly rate (₹)</Label>
                <Input type="number" step="0.01" min="0" placeholder="0" value={form.monthly_rate} onChange={(e) => setForm({ ...form, monthly_rate: e.target.value })} />
              </div>
              <div className="space-y-1.5">
                <Label>Start date</Label>
                <Input type="date" value={form.start_date} onChange={(e) => setForm({ ...form, start_date: e.target.value })} required />
              </div>
              <div className="space-y-1.5">
                <Label>End date (optional)</Label>
                <Input type="date" value={form.end_date} onChange={(e) => setForm({ ...form, end_date: e.target.value })} />
              </div>
              <div className="space-y-1.5 sm:col-span-2">
                <Label>Notes</Label>
                <Input value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} />
              </div>
              </fieldset>
              <div className="flex items-end">
                <Button type="submit" disabled={createMutation.isPending}>
                  {createMutation.isPending && <Spinner className="mr-2" />}
                  {createMutation.isPending ? 'Saving…' : 'Create Lease'}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      {isLoading ? (
        <div className="space-y-3">{[...Array(4)].map((_, i) => <div key={i} className="h-16 bg-muted rounded-lg animate-pulse" />)}</div>
      ) : (
        <Card>
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b bg-muted/50">
                    <th className="text-left px-4 py-3 font-medium">Company</th>
                    <th className="text-left px-4 py-3 font-medium">Location</th>
                    <th className="text-left px-4 py-3 font-medium">Seats (used / leased)</th>
                    <th className="text-left px-4 py-3 font-medium">Period</th>
                    <th className="text-right px-4 py-3 font-medium">Rate/mo</th>
                    <th className="text-left px-4 py-3 font-medium">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {leases.length === 0 && (
                    <tr>
                      <td colSpan={6} className="text-center py-8 text-muted-foreground">
                        {isSuperAdmin ? 'No leases yet. Click “New Lease”.' : 'No lease agreements found.'}
                      </td>
                    </tr>
                  )}
                  {leases.map((l) => (
                    <tr key={l.id} className="border-b last:border-0 hover:bg-muted/30 transition-colors">
                      <td className="px-4 py-3 font-medium">{l.company_name}</td>
                      <td className="px-4 py-3 text-muted-foreground">
                        {l.building_name}{l.floor_name ? ` · ${l.floor_name}` : ''}
                      </td>
                      <td className="px-4 py-3">
                        <span className="font-medium">{l.seats_used}</span>
                        <span className="text-muted-foreground"> / {l.seats_leased}</span>
                        {l.seats_available > 0 && <span className="ml-2 text-xs text-green-600">{l.seats_available} free</span>}
                      </td>
                      <td className="px-4 py-3 text-muted-foreground">
                        {formatDate(l.start_date)}{l.end_date ? ` – ${formatDate(l.end_date)}` : ' →'}
                      </td>
                      <td className="px-4 py-3 text-right font-medium">{formatCurrency(l.monthly_rate)}</td>
                      <td className="px-4 py-3"><StatusBadge status={l.status} /></td>
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
