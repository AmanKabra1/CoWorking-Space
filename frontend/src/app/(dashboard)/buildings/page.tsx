'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { PageHeader } from '@/components/shared/PageHeader'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { workspaceService } from '@/lib/services'
import { useAuthStore } from '@/store/auth'
import { toast } from '@/hooks/use-toast'
import { Building2, ChevronRight } from 'lucide-react'

export default function BuildingsPage() {
  const router = useRouter()
  const queryClient = useQueryClient()
  const user = useAuthStore(s => s.user)
  const [showBuilding, setShowBuilding] = useState(false)
  const [selected, setSelected] = useState<string | null>(null)

  const [bForm, setBForm] = useState({ name: '', address: '', city: '', state: '', pincode: '', description: '' })
  const [fForm, setFForm] = useState({ floor_number: '', name: '' })

  useEffect(() => {
    if (user && user.role !== 'super_admin') router.replace('/dashboard')
  }, [user, router])

  const { data: buildings = [], isLoading } = useQuery({
    queryKey: ['buildings'],
    queryFn: () => workspaceService.buildings(),
    enabled: user?.role === 'super_admin',
  })

  const { data: floors = [] } = useQuery({
    queryKey: ['floors', selected],
    queryFn: () => workspaceService.floors(selected ?? undefined),
    enabled: Boolean(selected),
  })

  const createBuilding = useMutation({
    mutationFn: () => workspaceService.createBuilding(bForm),
    onSuccess: () => {
      toast({ title: 'Building created' })
      queryClient.invalidateQueries({ queryKey: ['buildings'] })
      setShowBuilding(false)
      setBForm({ name: '', address: '', city: '', state: '', pincode: '', description: '' })
    },
    onError: () => toast({ title: 'Could not create building', description: 'Check the fields.', variant: 'destructive' }),
  })

  const createFloor = useMutation({
    mutationFn: () => workspaceService.createFloor({
      building: selected!,
      floor_number: Number(fForm.floor_number),
      name: fForm.name,
    }),
    onSuccess: () => {
      toast({ title: 'Floor added' })
      queryClient.invalidateQueries({ queryKey: ['floors', selected] })
      queryClient.invalidateQueries({ queryKey: ['buildings'] })
      setFForm({ floor_number: '', name: '' })
    },
    onError: (e: unknown) => {
      const data = (e as { response?: { data?: Record<string, string[] | string> } })?.response?.data
      const first = data ? Object.values(data)[0] : null
      const msg = Array.isArray(first) ? first[0] : (first ?? 'Check the fields.')
      toast({ title: 'Could not add floor', description: String(msg), variant: 'destructive' })
    },
  })

  if (user?.role !== 'super_admin') return null

  return (
    <div className="space-y-4">
      <PageHeader
        title="Buildings & Floors"
        description="Set up your buildings and their floors"
        action={<Button onClick={() => setShowBuilding(v => !v)}>{showBuilding ? 'Close' : 'New Building'}</Button>}
      />

      {showBuilding && (
        <Card>
          <CardContent className="p-4">
            <form onSubmit={(e) => { e.preventDefault(); createBuilding.mutate() }} className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              <div className="space-y-1.5"><Label>Name</Label><Input value={bForm.name} onChange={(e) => setBForm({ ...bForm, name: e.target.value })} required /></div>
              <div className="space-y-1.5"><Label>City</Label><Input value={bForm.city} onChange={(e) => setBForm({ ...bForm, city: e.target.value })} required /></div>
              <div className="space-y-1.5"><Label>State</Label><Input value={bForm.state} onChange={(e) => setBForm({ ...bForm, state: e.target.value })} required /></div>
              <div className="space-y-1.5"><Label>Pincode</Label><Input value={bForm.pincode} onChange={(e) => setBForm({ ...bForm, pincode: e.target.value })} required /></div>
              <div className="space-y-1.5 sm:col-span-2"><Label>Address</Label><Input value={bForm.address} onChange={(e) => setBForm({ ...bForm, address: e.target.value })} required /></div>
              <div className="space-y-1.5 sm:col-span-2"><Label>Description</Label><Input value={bForm.description} onChange={(e) => setBForm({ ...bForm, description: e.target.value })} /></div>
              <div className="flex items-end"><Button type="submit" disabled={createBuilding.isPending}>{createBuilding.isPending ? 'Saving…' : 'Create Building'}</Button></div>
            </form>
          </CardContent>
        </Card>
      )}

      {isLoading ? (
        <div className="space-y-3">{[...Array(3)].map((_, i) => <div key={i} className="h-16 bg-muted rounded-lg animate-pulse" />)}</div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {/* Buildings list */}
          <Card>
            <CardContent className="p-0">
              {buildings.length === 0 && <p className="text-center py-8 text-muted-foreground">No buildings yet. Click “New Building”.</p>}
              {buildings.map((b) => (
                <button
                  key={b.id}
                  onClick={() => setSelected(b.id)}
                  className={`w-full text-left flex items-center gap-3 px-4 py-3 border-b last:border-0 hover:bg-muted/40 transition-colors ${selected === b.id ? 'bg-muted/60' : ''}`}
                >
                  <Building2 className="h-4 w-4 text-muted-foreground shrink-0" />
                  <div className="flex-1">
                    <div className="font-medium">{b.name}</div>
                    <div className="text-xs text-muted-foreground">{b.city}, {b.state} · {b.total_floors ?? 0} floors · {b.occupancy_rate ?? 0}% occupied</div>
                  </div>
                  <ChevronRight className="h-4 w-4 text-muted-foreground" />
                </button>
              ))}
            </CardContent>
          </Card>

          {/* Floors of selected building */}
          <Card>
            <CardContent className="p-4">
              {!selected ? (
                <p className="text-center py-8 text-muted-foreground">Select a building to manage its floors.</p>
              ) : (
                <div className="space-y-4">
                  <h2 className="text-sm font-semibold">Floors</h2>
                  <div className="space-y-1.5">
                    {floors.length === 0 && <p className="text-sm text-muted-foreground">No floors yet.</p>}
                    {floors.map((f) => (
                      <div key={f.id} className="flex items-center justify-between rounded border px-3 py-2 text-sm">
                        <span>{f.name} (Floor {f.floor_number})</span>
                        <Badge variant={f.is_active ? 'success' : 'secondary'}>{f.is_active ? 'Active' : 'Inactive'}</Badge>
                      </div>
                    ))}
                  </div>
                  <form onSubmit={(e) => { e.preventDefault(); createFloor.mutate() }} className="grid grid-cols-1 sm:grid-cols-3 gap-3 border-t pt-4">
                    <div className="space-y-1.5"><Label>Floor #</Label><Input type="number" value={fForm.floor_number} onChange={(e) => setFForm({ ...fForm, floor_number: e.target.value })} placeholder="0 = Ground" required /></div>
                    <div className="space-y-1.5"><Label>Name</Label><Input value={fForm.name} onChange={(e) => setFForm({ ...fForm, name: e.target.value })} placeholder="Ground Floor" required /></div>
                    <div className="flex items-end"><Button type="submit" disabled={createFloor.isPending}>{createFloor.isPending ? 'Adding…' : 'Add Floor'}</Button></div>
                  </form>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}
