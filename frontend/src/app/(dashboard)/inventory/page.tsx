'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { PageHeader } from '@/components/shared/PageHeader'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { inventoryService, workspaceService } from '@/lib/services'
import { toast } from '@/hooks/use-toast'
import type { InventoryCategory } from '@/types'

const CATEGORIES: { value: InventoryCategory; label: string }[] = [
  { value: 'pantry', label: 'Pantry' },
  { value: 'canteen', label: 'Canteen' },
  { value: 'water', label: 'Water / Beverages' },
  { value: 'appliance', label: 'Daily Appliance' },
  { value: 'cleaning', label: 'Cleaning Supplies' },
  { value: 'stationery', label: 'Stationery' },
  { value: 'other', label: 'Other' },
]

const selectClass =
  'flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring'

export default function InventoryPage() {
  const queryClient = useQueryClient()
  const [showForm, setShowForm] = useState(false)
  const [adjusting, setAdjusting] = useState<{ id: string; direction: 'in' | 'out' } | null>(null)
  const [adjustQty, setAdjustQty] = useState('')

  const [form, setForm] = useState({
    building: '',
    name: '',
    category: 'pantry' as InventoryCategory,
    unit: 'pcs',
    quantity: '0',
    reorder_level: '0',
    unit_cost: '0',
  })

  const { data: items = [], isLoading } = useQuery({
    queryKey: ['inventory'],
    queryFn: () => inventoryService.list(),
  })

  const { data: buildings = [] } = useQuery({
    queryKey: ['buildings'],
    queryFn: () => workspaceService.buildings(),
  })

  const invalidate = () => queryClient.invalidateQueries({ queryKey: ['inventory'] })

  const createMutation = useMutation({
    mutationFn: () => inventoryService.create(form),
    onSuccess: () => {
      toast({ title: 'Item added' })
      invalidate()
      setShowForm(false)
      setForm({ building: '', name: '', category: 'pantry', unit: 'pcs', quantity: '0', reorder_level: '0', unit_cost: '0' })
    },
    onError: () => toast({ title: 'Could not add item', description: 'Check the fields and try again.', variant: 'destructive' }),
  })

  const adjustMutation = useMutation({
    mutationFn: ({ id, direction, qty }: { id: string; direction: 'in' | 'out'; qty: number }) =>
      direction === 'in' ? inventoryService.restock(id, qty) : inventoryService.consume(id, qty),
    onSuccess: () => {
      toast({ title: 'Stock updated' })
      invalidate()
      setAdjusting(null)
      setAdjustQty('')
    },
    onError: (e: unknown) => {
      const detail = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      toast({ title: 'Could not update stock', description: detail ?? 'Try again.', variant: 'destructive' })
    },
  })

  function submitAdjust() {
    const qty = parseFloat(adjustQty)
    if (!adjusting || isNaN(qty) || qty <= 0) {
      toast({ title: 'Enter a valid quantity', variant: 'destructive' })
      return
    }
    adjustMutation.mutate({ id: adjusting.id, direction: adjusting.direction, qty })
  }

  return (
    <div className="space-y-4">
      <PageHeader
        title="Inventory"
        description="Pantry, canteen, water, appliances & supplies per building"
        action={
          <Button onClick={() => setShowForm(v => !v)}>
            {showForm ? 'Close' : 'Add Item'}
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
                <Label>Building</Label>
                <select
                  className={selectClass}
                  value={form.building}
                  onChange={(e) => setForm({ ...form, building: e.target.value })}
                  required
                >
                  <option value="">Select building…</option>
                  {buildings.map((b) => (
                    <option key={b.id} value={b.id}>{b.name}</option>
                  ))}
                </select>
              </div>
              <div className="space-y-1.5">
                <Label>Item name</Label>
                <Input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
              </div>
              <div className="space-y-1.5">
                <Label>Category</Label>
                <select
                  className={selectClass}
                  value={form.category}
                  onChange={(e) => setForm({ ...form, category: e.target.value as InventoryCategory })}
                >
                  {CATEGORIES.map((c) => <option key={c.value} value={c.value}>{c.label}</option>)}
                </select>
              </div>
              <div className="space-y-1.5">
                <Label>Unit</Label>
                <Input value={form.unit} onChange={(e) => setForm({ ...form, unit: e.target.value })} placeholder="pcs, kg, litre…" />
              </div>
              <div className="space-y-1.5">
                <Label>Opening quantity</Label>
                <Input type="number" step="0.01" value={form.quantity} onChange={(e) => setForm({ ...form, quantity: e.target.value })} />
              </div>
              <div className="space-y-1.5">
                <Label>Reorder level</Label>
                <Input type="number" step="0.01" value={form.reorder_level} onChange={(e) => setForm({ ...form, reorder_level: e.target.value })} />
              </div>
              <div className="space-y-1.5">
                <Label>Unit cost (₹)</Label>
                <Input type="number" step="0.01" value={form.unit_cost} onChange={(e) => setForm({ ...form, unit_cost: e.target.value })} />
              </div>
              <div className="flex items-end">
                <Button type="submit" disabled={createMutation.isPending}>
                  {createMutation.isPending ? 'Saving…' : 'Save Item'}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

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
                    <th className="text-left px-4 py-3 font-medium">Item</th>
                    <th className="text-left px-4 py-3 font-medium">Category</th>
                    <th className="text-left px-4 py-3 font-medium">Building</th>
                    <th className="text-right px-4 py-3 font-medium">In Stock</th>
                    <th className="text-left px-4 py-3 font-medium">Status</th>
                    <th className="text-right px-4 py-3 font-medium">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {items.length === 0 && (
                    <tr>
                      <td colSpan={6} className="text-center py-8 text-muted-foreground">
                        No inventory items yet. Click “Add Item” to start.
                      </td>
                    </tr>
                  )}
                  {items.map((item) => (
                    <tr key={item.id} className="border-b last:border-0 hover:bg-muted/30 transition-colors">
                      <td className="px-4 py-3 font-medium">{item.name}</td>
                      <td className="px-4 py-3 text-muted-foreground">{item.category_display}</td>
                      <td className="px-4 py-3 text-muted-foreground">{item.building_name}</td>
                      <td className="px-4 py-3 text-right">{item.quantity} {item.unit}</td>
                      <td className="px-4 py-3">
                        {item.is_low_stock
                          ? <Badge variant="destructive">Low stock</Badge>
                          : <Badge variant="success">OK</Badge>}
                      </td>
                      <td className="px-4 py-3">
                        {adjusting?.id === item.id ? (
                          <div className="flex justify-end items-center gap-2">
                            <Input
                              type="number"
                              step="0.01"
                              autoFocus
                              value={adjustQty}
                              onChange={(e) => setAdjustQty(e.target.value)}
                              className="h-8 w-24"
                              placeholder={`Qty to ${adjusting.direction === 'in' ? 'add' : 'remove'}`}
                            />
                            <Button size="sm" disabled={adjustMutation.isPending} onClick={submitAdjust}>OK</Button>
                            <Button size="sm" variant="outline" onClick={() => { setAdjusting(null); setAdjustQty('') }}>✕</Button>
                          </div>
                        ) : (
                          <div className="flex justify-end gap-2">
                            <Button size="sm" variant="outline" onClick={() => { setAdjusting({ id: item.id, direction: 'in' }); setAdjustQty('') }}>
                              Restock
                            </Button>
                            <Button size="sm" variant="outline" onClick={() => { setAdjusting({ id: item.id, direction: 'out' }); setAdjustQty('') }}>
                              Consume
                            </Button>
                          </div>
                        )}
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
