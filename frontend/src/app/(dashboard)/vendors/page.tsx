'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { PageHeader } from '@/components/shared/PageHeader'
import { ExportButtons } from '@/components/shared/ExportButtons'
import { KPICard } from '@/components/shared/KPICard'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { vendorService, vendorBillService, workspaceService } from '@/lib/services'
import { formatCurrency, formatDate } from '@/lib/utils'
import { toast } from '@/hooks/use-toast'
import { Receipt, IndianRupee, Clock, AlertTriangle } from 'lucide-react'
import type { VendorCategory, VendorBillStatus } from '@/types'

const VENDOR_CATEGORIES: { value: VendorCategory; label: string }[] = [
  { value: 'utilities', label: 'Utilities' },
  { value: 'catering', label: 'Catering / Pantry' },
  { value: 'cleaning', label: 'Cleaning' },
  { value: 'maintenance', label: 'Maintenance' },
  { value: 'supplies', label: 'Supplies' },
  { value: 'security', label: 'Security' },
  { value: 'internet', label: 'Internet / Telecom' },
  { value: 'other', label: 'Other' },
]

const selectClass =
  'flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring'

const STATUS_VARIANT: Record<VendorBillStatus, 'success' | 'warning' | 'destructive' | 'secondary'> = {
  paid: 'success',
  pending: 'warning',
  overdue: 'destructive',
  cancelled: 'secondary',
}

export default function VendorsPage() {
  const queryClient = useQueryClient()
  const [showVendorForm, setShowVendorForm] = useState(false)
  const [showBillForm, setShowBillForm] = useState(false)

  const [vendorForm, setVendorForm] = useState({
    name: '', category: 'utilities' as VendorCategory, building: '',
    contact_person: '', phone: '', email: '', gst_number: '',
  })

  const [billForm, setBillForm] = useState({
    vendor: '', building: '', bill_number: '', bill_date: '',
    due_date: '', amount: '0', tax_amount: '0', description: '',
  })

  const { data: vendors = [] } = useQuery({ queryKey: ['vendors'], queryFn: () => vendorService.list() })
  const { data: buildings = [] } = useQuery({ queryKey: ['buildings'], queryFn: () => workspaceService.buildings() })
  const { data: bills = [], isLoading } = useQuery({ queryKey: ['vendor-bills'], queryFn: () => vendorBillService.list() })
  const { data: summary } = useQuery({ queryKey: ['vendor-bills', 'summary'], queryFn: () => vendorBillService.summary() })

  const invalidateAll = () => {
    queryClient.invalidateQueries({ queryKey: ['vendor-bills'] })
    queryClient.invalidateQueries({ queryKey: ['vendors'] })
  }

  const createVendor = useMutation({
    mutationFn: () => vendorService.create({ ...vendorForm, building: vendorForm.building || null }),
    onSuccess: () => {
      toast({ title: 'Vendor added' })
      queryClient.invalidateQueries({ queryKey: ['vendors'] })
      setShowVendorForm(false)
      setVendorForm({ name: '', category: 'utilities', building: '', contact_person: '', phone: '', email: '', gst_number: '' })
    },
    onError: () => toast({ title: 'Could not add vendor', variant: 'destructive' }),
  })

  const createBill = useMutation({
    mutationFn: () => vendorBillService.create({
      ...billForm,
      due_date: billForm.due_date || null,
    }),
    onSuccess: () => {
      toast({ title: 'Bill recorded' })
      invalidateAll()
      setShowBillForm(false)
      setBillForm({ vendor: '', building: '', bill_number: '', bill_date: '', due_date: '', amount: '0', tax_amount: '0', description: '' })
    },
    onError: () => toast({ title: 'Could not record bill', description: 'Check the fields.', variant: 'destructive' }),
  })

  const markPaid = useMutation({
    mutationFn: (id: string) => vendorBillService.markPaid(id),
    onSuccess: () => { toast({ title: 'Marked paid' }); invalidateAll() },
    onError: () => toast({ title: 'Could not update', variant: 'destructive' }),
  })

  const deleteBill = useMutation({
    mutationFn: (id: string) => vendorBillService.remove(id),
    onSuccess: () => { toast({ title: 'Bill deleted' }); invalidateAll() },
    onError: () => toast({ title: 'Could not delete', variant: 'destructive' }),
  })

  return (
    <div className="space-y-6">
      <PageHeader
        title="Vendors & Bills"
        description="Suppliers and their bills / expenses per building"
        action={
          <div className="flex flex-wrap items-center gap-2">
            <ExportButtons filename="vendor_bills" onExport={(f) => vendorBillService.export(f)} />
            <Button variant="outline" onClick={() => setShowVendorForm(v => !v)}>
              {showVendorForm ? 'Close' : 'Add Vendor'}
            </Button>
            <Button onClick={() => setShowBillForm(v => !v)}>
              {showBillForm ? 'Close' : 'Add Bill'}
            </Button>
          </div>
        }
      />

      {/* Summary */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard title="Total Billed" value={formatCurrency(summary?.total_amount ?? 0)} icon={IndianRupee} />
        <KPICard title="Pending" value={formatCurrency(summary?.pending_amount ?? 0)} icon={Clock} />
        <KPICard title="Paid" value={formatCurrency(summary?.paid_amount ?? 0)} icon={Receipt} />
        <KPICard title="Overdue" value={formatCurrency(summary?.overdue_amount ?? 0)} icon={AlertTriangle} />
      </div>

      {/* Add Vendor form */}
      {showVendorForm && (
        <Card>
          <CardContent className="p-4">
            <form
              onSubmit={(e) => { e.preventDefault(); createVendor.mutate() }}
              className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4"
            >
              <div className="space-y-1.5">
                <Label>Vendor name</Label>
                <Input value={vendorForm.name} onChange={(e) => setVendorForm({ ...vendorForm, name: e.target.value })} required />
              </div>
              <div className="space-y-1.5">
                <Label>Category</Label>
                <select className={selectClass} value={vendorForm.category} onChange={(e) => setVendorForm({ ...vendorForm, category: e.target.value as VendorCategory })}>
                  {VENDOR_CATEGORIES.map((c) => <option key={c.value} value={c.value}>{c.label}</option>)}
                </select>
              </div>
              <div className="space-y-1.5">
                <Label>Building (optional)</Label>
                <select className={selectClass} value={vendorForm.building} onChange={(e) => setVendorForm({ ...vendorForm, building: e.target.value })}>
                  <option value="">Operator-wide</option>
                  {buildings.map((b) => <option key={b.id} value={b.id}>{b.name}</option>)}
                </select>
              </div>
              <div className="space-y-1.5">
                <Label>Contact person</Label>
                <Input value={vendorForm.contact_person} onChange={(e) => setVendorForm({ ...vendorForm, contact_person: e.target.value })} />
              </div>
              <div className="space-y-1.5">
                <Label>Phone</Label>
                <Input value={vendorForm.phone} onChange={(e) => setVendorForm({ ...vendorForm, phone: e.target.value })} />
              </div>
              <div className="space-y-1.5">
                <Label>GST number</Label>
                <Input value={vendorForm.gst_number} onChange={(e) => setVendorForm({ ...vendorForm, gst_number: e.target.value })} />
              </div>
              <div className="flex items-end">
                <Button type="submit" disabled={createVendor.isPending}>
                  {createVendor.isPending ? 'Saving…' : 'Save Vendor'}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      {/* Add Bill form */}
      {showBillForm && (
        <Card>
          <CardContent className="p-4">
            <form
              onSubmit={(e) => { e.preventDefault(); createBill.mutate() }}
              className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4"
            >
              <div className="space-y-1.5">
                <Label>Vendor</Label>
                <select className={selectClass} value={billForm.vendor} onChange={(e) => setBillForm({ ...billForm, vendor: e.target.value })} required>
                  <option value="">Select vendor…</option>
                  {vendors.map((v) => <option key={v.id} value={v.id}>{v.name}</option>)}
                </select>
              </div>
              <div className="space-y-1.5">
                <Label>Building</Label>
                <select className={selectClass} value={billForm.building} onChange={(e) => setBillForm({ ...billForm, building: e.target.value })} required>
                  <option value="">Select building…</option>
                  {buildings.map((b) => <option key={b.id} value={b.id}>{b.name}</option>)}
                </select>
              </div>
              <div className="space-y-1.5">
                <Label>Bill number</Label>
                <Input value={billForm.bill_number} onChange={(e) => setBillForm({ ...billForm, bill_number: e.target.value })} required />
              </div>
              <div className="space-y-1.5">
                <Label>Bill date</Label>
                <Input type="date" value={billForm.bill_date} onChange={(e) => setBillForm({ ...billForm, bill_date: e.target.value })} required />
              </div>
              <div className="space-y-1.5">
                <Label>Due date (optional)</Label>
                <Input type="date" value={billForm.due_date} onChange={(e) => setBillForm({ ...billForm, due_date: e.target.value })} />
              </div>
              <div className="space-y-1.5">
                <Label>Amount (₹)</Label>
                <Input type="number" step="0.01" value={billForm.amount} onChange={(e) => setBillForm({ ...billForm, amount: e.target.value })} />
              </div>
              <div className="space-y-1.5">
                <Label>Tax (₹)</Label>
                <Input type="number" step="0.01" value={billForm.tax_amount} onChange={(e) => setBillForm({ ...billForm, tax_amount: e.target.value })} />
              </div>
              <div className="space-y-1.5 sm:col-span-2">
                <Label>Description</Label>
                <Input value={billForm.description} onChange={(e) => setBillForm({ ...billForm, description: e.target.value })} />
              </div>
              <div className="flex items-end">
                <Button type="submit" disabled={createBill.isPending}>
                  {createBill.isPending ? 'Saving…' : 'Save Bill'}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      {/* Bills table */}
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
                    <th className="text-left px-4 py-3 font-medium">Bill #</th>
                    <th className="text-left px-4 py-3 font-medium">Vendor</th>
                    <th className="text-left px-4 py-3 font-medium">Building</th>
                    <th className="text-left px-4 py-3 font-medium">Date</th>
                    <th className="text-right px-4 py-3 font-medium">Total</th>
                    <th className="text-left px-4 py-3 font-medium">Status</th>
                    <th className="text-right px-4 py-3 font-medium">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {bills.length === 0 && (
                    <tr>
                      <td colSpan={7} className="text-center py-8 text-muted-foreground">
                        No vendor bills yet. Click “Add Bill” to record one.
                      </td>
                    </tr>
                  )}
                  {bills.map((bill) => (
                    <tr key={bill.id} className="border-b last:border-0 hover:bg-muted/30 transition-colors">
                      <td className="px-4 py-3 font-medium">{bill.bill_number}</td>
                      <td className="px-4 py-3 text-muted-foreground">{bill.vendor_name}</td>
                      <td className="px-4 py-3 text-muted-foreground">{bill.building_name}</td>
                      <td className="px-4 py-3 text-muted-foreground">{formatDate(bill.bill_date)}</td>
                      <td className="px-4 py-3 text-right font-medium">{formatCurrency(bill.total_amount)}</td>
                      <td className="px-4 py-3">
                        <Badge variant={STATUS_VARIANT[bill.status]}>{bill.status_display}</Badge>
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex justify-end gap-2">
                          {(bill.status === 'pending' || bill.status === 'overdue') && (
                            <Button size="sm" variant="outline" disabled={markPaid.isPending} onClick={() => markPaid.mutate(bill.id)}>
                              Mark paid
                            </Button>
                          )}
                          <Button size="sm" variant="outline" disabled={deleteBill.isPending}
                            onClick={() => { if (confirm(`Delete bill ${bill.bill_number}?`)) deleteBill.mutate(bill.id) }}>
                            Delete
                          </Button>
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
