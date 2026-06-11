'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { MapPin, Users, DollarSign } from 'lucide-react'
import { PageHeader } from '@/components/shared/PageHeader'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { facilityService, workspaceService } from '@/lib/services'
import { useAuthStore } from '@/store/auth'
import { formatCurrency } from '@/lib/utils'
import { toast } from '@/hooks/use-toast'

const FACILITY_TYPES = [
  { value: 'conference_room', label: 'Conference Room' },
  { value: 'meeting_room', label: 'Meeting Room' },
  { value: 'event_hall', label: 'Event Hall' },
  { value: 'podcast_studio', label: 'Podcast Studio' },
  { value: 'printing_room', label: 'Printing Room' },
  { value: '3d_printer', label: '3D Printer' },
  { value: 'cafeteria', label: 'Cafeteria' },
  { value: 'other', label: 'Other' },
]

const selectClass =
  'flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring'

export default function FacilitiesPage() {
  const queryClient = useQueryClient()
  const isSuperAdmin = useAuthStore(s => s.user?.role === 'super_admin')
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({
    name: '', facility_type: 'meeting_room', building: '', floor: '',
    capacity: '4', price_per_hour: '0', price_per_day: '0',
    description: '', is_public: false,
  })

  const { data, isLoading } = useQuery({
    queryKey: ['facilities'],
    queryFn: () => facilityService.list(),
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
    mutationFn: () => facilityService.create({
      name: form.name,
      facility_type: form.facility_type,
      building: form.building,
      floor: form.floor || null,
      capacity: Number(form.capacity) || 1,
      price_per_hour: form.price_per_hour,
      price_per_day: form.price_per_day,
      description: form.description,
      is_public: form.is_public,
    } as never),
    onSuccess: () => {
      toast({ title: 'Facility created' })
      queryClient.invalidateQueries({ queryKey: ['facilities'] })
      setShowForm(false)
      setForm({ name: '', facility_type: 'meeting_room', building: '', floor: '', capacity: '4', price_per_hour: '0', price_per_day: '0', description: '', is_public: false })
    },
    onError: (e: unknown) => {
      const data = (e as { response?: { data?: Record<string, string[] | string> } })?.response?.data
      const first = data ? Object.values(data)[0] : null
      const msg = Array.isArray(first) ? first[0] : (first ?? 'Check the fields and try again.')
      toast({ title: 'Could not create facility', description: String(msg), variant: 'destructive' })
    },
  })

  return (
    <div className="space-y-4">
      <PageHeader
        title="Facilities"
        description="All spaces available for booking"
        action={isSuperAdmin ? (
          <Button onClick={() => setShowForm(v => !v)}>{showForm ? 'Close' : 'New Facility'}</Button>
        ) : undefined}
      />

      {showForm && isSuperAdmin && (
        <Card>
          <CardContent className="p-4">
            <form
              onSubmit={(e) => { e.preventDefault(); createMutation.mutate() }}
              className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4"
            >
              <div className="space-y-1.5">
                <Label>Name</Label>
                <Input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
              </div>
              <div className="space-y-1.5">
                <Label>Type</Label>
                <select className={selectClass} value={form.facility_type} onChange={(e) => setForm({ ...form, facility_type: e.target.value })}>
                  {FACILITY_TYPES.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
                </select>
              </div>
              <div className="space-y-1.5">
                <Label>Building</Label>
                <select className={selectClass} value={form.building} onChange={(e) => setForm({ ...form, building: e.target.value, floor: '' })} required>
                  <option value="">Select building…</option>
                  {buildings.map(b => <option key={b.id} value={b.id}>{b.name}</option>)}
                </select>
              </div>
              <div className="space-y-1.5">
                <Label>Floor (optional)</Label>
                <select className={selectClass} value={form.floor} onChange={(e) => setForm({ ...form, floor: e.target.value })} disabled={!form.building}>
                  <option value="">—</option>
                  {floors.map(f => <option key={f.id} value={f.id}>{f.name}</option>)}
                </select>
              </div>
              <div className="space-y-1.5">
                <Label>Capacity</Label>
                <Input type="number" min="1" value={form.capacity} onChange={(e) => setForm({ ...form, capacity: e.target.value })} />
              </div>
              <div className="space-y-1.5">
                <Label>Price / hour (₹)</Label>
                <Input type="number" step="0.01" value={form.price_per_hour} onChange={(e) => setForm({ ...form, price_per_hour: e.target.value })} />
              </div>
              <div className="space-y-1.5">
                <Label>Price / day (₹)</Label>
                <Input type="number" step="0.01" value={form.price_per_day} onChange={(e) => setForm({ ...form, price_per_day: e.target.value })} />
              </div>
              <div className="space-y-1.5 sm:col-span-2">
                <Label>Description</Label>
                <Input value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
              </div>
              <label className="flex items-center gap-2 text-sm">
                <input type="checkbox" checked={form.is_public} onChange={(e) => setForm({ ...form, is_public: e.target.checked })} />
                Open for public (no-login) booking
              </label>
              <div className="flex items-end">
                <Button type="submit" disabled={createMutation.isPending}>
                  {createMutation.isPending ? 'Saving…' : 'Create Facility'}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="h-48 bg-muted rounded-lg animate-pulse" />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {data?.results?.map((facility) => (
            <Card key={facility.id} className="overflow-hidden">
              {facility.primary_image && (
                // eslint-disable-next-line @next/next/no-img-element
                <img src={facility.primary_image} alt={facility.name} className="w-full h-36 object-cover" />
              )}
              <CardHeader className="pb-2">
                <div className="flex items-start justify-between gap-2">
                  <CardTitle className="text-base">{facility.name}</CardTitle>
                  <div className="flex flex-col items-end gap-1">
                    <Badge variant={facility.is_available ? 'success' : 'secondary'}>
                      {facility.is_available ? 'Available' : 'Unavailable'}
                    </Badge>
                    {facility.is_public && <Badge variant="info">Public</Badge>}
                  </div>
                </div>
              </CardHeader>
              <CardContent className="pt-0 space-y-1.5 text-sm text-muted-foreground">
                <div className="flex items-center gap-1.5">
                  <MapPin className="h-3.5 w-3.5" />
                  {facility.building_name}{facility.floor_number != null ? `, Floor ${facility.floor_number}` : ''}
                </div>
                <div className="flex items-center gap-1.5">
                  <Users className="h-3.5 w-3.5" />
                  Capacity: {facility.capacity}
                </div>
                <div className="flex items-center gap-1.5">
                  <DollarSign className="h-3.5 w-3.5" />
                  {formatCurrency(facility.price_per_hour)}/hr
                </div>
              </CardContent>
            </Card>
          ))}
          {data?.results?.length === 0 && (
            <p className="col-span-full text-center py-12 text-muted-foreground">No facilities found.</p>
          )}
        </div>
      )}
    </div>
  )
}
