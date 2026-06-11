'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { PageHeader } from '@/components/shared/PageHeader'
import { StatusBadge } from '@/components/shared/StatusBadge'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { seatListingService, workspaceService } from '@/lib/services'
import { useAuthStore } from '@/store/auth'
import { formatCurrency } from '@/lib/utils'
import { toast } from '@/hooks/use-toast'

const selectClass =
  'flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring'

export default function SeatListingsPage() {
  const queryClient = useQueryClient()
  const isCompanyAdmin = useAuthStore(s => s.user?.role === 'company_admin')
  const [showForm, setShowForm] = useState(false)
  const [openListing, setOpenListing] = useState<string | null>(null)
  const [form, setForm] = useState({ building: '', title: '', seats_available: '1', monthly_rate: '0', description: '' })

  const { data: listings = [], isLoading } = useQuery({
    queryKey: ['seat-listings'],
    queryFn: () => seatListingService.list(),
  })
  const { data: buildings = [] } = useQuery({
    queryKey: ['buildings'],
    queryFn: () => workspaceService.buildings(),
    enabled: isCompanyAdmin,
  })
  const { data: applications = [] } = useQuery({
    queryKey: ['seat-applications', openListing],
    queryFn: () => seatListingService.applications(openListing ?? undefined),
    enabled: Boolean(openListing),
  })

  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ['seat-listings'] })
    queryClient.invalidateQueries({ queryKey: ['seat-applications'] })
  }

  const createListing = useMutation({
    mutationFn: () => seatListingService.create({
      building: form.building, title: form.title,
      seats_available: Number(form.seats_available) || 1,
      monthly_rate: form.monthly_rate, description: form.description || undefined,
    }),
    onSuccess: () => {
      toast({ title: 'Listing posted' }); invalidate(); setShowForm(false)
      setForm({ building: '', title: '', seats_available: '1', monthly_rate: '0', description: '' })
    },
    onError: () => toast({ title: 'Could not post listing', variant: 'destructive' }),
  })

  const review = useMutation({
    mutationFn: ({ id, action }: { id: string; action: 'approve' | 'reject' }) =>
      action === 'approve' ? seatListingService.approve(id) : seatListingService.reject(id),
    onSuccess: () => { toast({ title: 'Application updated' }); invalidate() },
    onError: () => toast({ title: 'Could not update', variant: 'destructive' }),
  })

  return (
    <div className="space-y-4">
      <PageHeader
        title="Startup Seats"
        description="Open spare seats to startups — they apply, you approve (super admin is just notified)"
        action={isCompanyAdmin ? (
          <Button onClick={() => setShowForm(v => !v)}>{showForm ? 'Close' : 'Post Listing'}</Button>
        ) : undefined}
      />

      {showForm && isCompanyAdmin && (
        <Card><CardContent className="p-4">
          <form onSubmit={(e) => { e.preventDefault(); createListing.mutate() }} className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            <div className="space-y-1.5"><Label>Title</Label><Input value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} placeholder="e.g. 10 hot desks, 5th floor" required /></div>
            <div className="space-y-1.5">
              <Label>Building</Label>
              <select className={selectClass} value={form.building} onChange={(e) => setForm({ ...form, building: e.target.value })} required>
                <option value="">Select building…</option>
                {buildings.map(b => <option key={b.id} value={b.id}>{b.name}</option>)}
              </select>
            </div>
            <div className="space-y-1.5"><Label>Seats available</Label><Input type="number" min="1" value={form.seats_available} onChange={(e) => setForm({ ...form, seats_available: e.target.value })} /></div>
            <div className="space-y-1.5"><Label>Monthly rate (₹)</Label><Input type="number" step="0.01" value={form.monthly_rate} onChange={(e) => setForm({ ...form, monthly_rate: e.target.value })} /></div>
            <div className="space-y-1.5 sm:col-span-2"><Label>Description</Label><Input value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} /></div>
            <div className="flex items-end"><Button type="submit" disabled={createListing.isPending}>{createListing.isPending ? 'Posting…' : 'Post Listing'}</Button></div>
          </form>
        </CardContent></Card>
      )}

      {isLoading ? (
        <div className="space-y-3">{[...Array(3)].map((_, i) => <div key={i} className="h-20 bg-muted rounded-lg animate-pulse" />)}</div>
      ) : listings.length === 0 ? (
        <Card><CardContent className="p-8 text-center text-muted-foreground">No seat listings yet.</CardContent></Card>
      ) : (
        <div className="space-y-3">
          {listings.map((l) => (
            <Card key={l.id}>
              <CardContent className="p-4">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <div className="font-medium">{l.title}</div>
                    <div className="text-xs text-muted-foreground">
                      {l.lessor_company_name} · {l.building_name} · {l.seats_available} seats · {formatCurrency(l.monthly_rate)}/mo
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {l.pending_count > 0 && <Badge variant="warning">{l.pending_count} pending</Badge>}
                    <Badge variant={l.is_open ? 'success' : 'secondary'}>{l.is_open ? 'Open' : 'Closed'}</Badge>
                    <Button size="sm" variant="outline" onClick={() => setOpenListing(openListing === l.id ? null : l.id)}>
                      {openListing === l.id ? 'Hide' : `Applications (${l.application_count})`}
                    </Button>
                  </div>
                </div>

                {openListing === l.id && (
                  <div className="mt-4 border-t pt-3 space-y-2">
                    {applications.length === 0 && <p className="text-sm text-muted-foreground">No applications yet.</p>}
                    {applications.map((a) => (
                      <div key={a.id} className="flex items-center justify-between rounded border px-3 py-2 text-sm">
                        <div>
                          <span className="font-medium">{a.startup_name}</span>
                          <span className="text-muted-foreground"> · {a.seats_requested} seats · {a.contact_email}</span>
                          {a.message && <div className="text-xs text-muted-foreground mt-0.5">{a.message}</div>}
                        </div>
                        <div className="flex items-center gap-2">
                          <StatusBadge status={a.status} />
                          {a.status === 'pending' && (
                            <>
                              <Button size="sm" disabled={review.isPending} onClick={() => review.mutate({ id: a.id, action: 'approve' })}>Approve</Button>
                              <Button size="sm" variant="destructive" disabled={review.isPending} onClick={() => review.mutate({ id: a.id, action: 'reject' })}>Reject</Button>
                            </>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
