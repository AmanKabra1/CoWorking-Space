'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { PageHeader } from '@/components/shared/PageHeader'
import { StatusBadge } from '@/components/shared/StatusBadge'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { visitorService } from '@/lib/services'
import { formatDateTime } from '@/lib/utils'
import type { VisitorPass } from '@/types'

interface InviteForm {
  visitor_name: string
  visitor_email: string
  visitor_phone: string
  purpose: string
}

const EMPTY_FORM: InviteForm = {
  visitor_name: '',
  visitor_email: '',
  visitor_phone: '',
  purpose: '',
}

export default function VisitorsPage() {
  const queryClient = useQueryClient()
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState<InviteForm>(EMPTY_FORM)

  const { data: passes, isLoading, isError } = useQuery<VisitorPass[]>({
    queryKey: ['visitors'],
    queryFn: () => visitorService.list(),
  })

  const createMutation = useMutation({
    mutationFn: (data: Partial<VisitorPass>) => visitorService.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['visitors'] })
      setShowForm(false)
      setForm(EMPTY_FORM)
    },
  })

  const approveMutation = useMutation({
    mutationFn: (id: string) => visitorService.approve(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['visitors'] }),
  })

  const checkInMutation = useMutation({
    mutationFn: (id: string) => visitorService.checkIn(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['visitors'] }),
  })

  const checkOutMutation = useMutation({
    mutationFn: (id: string) => visitorService.checkOut(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['visitors'] }),
  })

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    createMutation.mutate(form)
  }

  function handleField(field: keyof InviteForm, value: string) {
    setForm(prev => ({ ...prev, [field]: value }))
  }

  return (
    <div className="space-y-4">
      <PageHeader
        title="Visitor Passes"
        description="Manage visitor access and check-ins"
        action={
          <Button onClick={() => setShowForm(v => !v)}>
            {showForm ? 'Cancel' : 'Invite Visitor'}
          </Button>
        }
      />

      {showForm && (
        <Card>
          <CardContent className="p-6">
            <h2 className="text-base font-semibold mb-4">New Visitor Invitation</h2>
            <form onSubmit={handleSubmit} className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-1">
                <Label htmlFor="visitor_name">Full Name</Label>
                <Input
                  id="visitor_name"
                  value={form.visitor_name}
                  onChange={e => handleField('visitor_name', e.target.value)}
                  required
                />
              </div>
              <div className="space-y-1">
                <Label htmlFor="visitor_email">Email</Label>
                <Input
                  id="visitor_email"
                  type="email"
                  value={form.visitor_email}
                  onChange={e => handleField('visitor_email', e.target.value)}
                  required
                />
              </div>
              <div className="space-y-1">
                <Label htmlFor="visitor_phone">Phone</Label>
                <Input
                  id="visitor_phone"
                  value={form.visitor_phone}
                  onChange={e => handleField('visitor_phone', e.target.value)}
                  required
                />
              </div>
              <div className="space-y-1">
                <Label htmlFor="purpose">Purpose of Visit</Label>
                <Input
                  id="purpose"
                  value={form.purpose}
                  onChange={e => handleField('purpose', e.target.value)}
                  required
                />
              </div>
              <div className="sm:col-span-2 flex justify-end gap-2">
                <Button type="button" variant="outline" onClick={() => { setShowForm(false); setForm(EMPTY_FORM) }}>
                  Cancel
                </Button>
                <Button type="submit" disabled={createMutation.isPending}>
                  {createMutation.isPending ? 'Sending…' : 'Send Invitation'}
                </Button>
              </div>
              {createMutation.isError && (
                <p className="sm:col-span-2 text-sm text-destructive">Failed to create invitation. Please try again.</p>
              )}
            </form>
          </CardContent>
        </Card>
      )}

      {isLoading ? (
        <div className="space-y-3">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="h-16 bg-muted rounded-lg animate-pulse" />
          ))}
        </div>
      ) : isError ? (
        <Card>
          <CardContent className="p-8 text-center text-muted-foreground">
            Failed to load visitor passes.
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b bg-muted/50">
                    <th className="text-left px-4 py-3 font-medium">Visitor</th>
                    <th className="text-left px-4 py-3 font-medium">Email</th>
                    <th className="text-left px-4 py-3 font-medium">Purpose</th>
                    <th className="text-left px-4 py-3 font-medium">Status</th>
                    <th className="text-left px-4 py-3 font-medium">Check-in</th>
                    <th className="text-left px-4 py-3 font-medium">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {passes?.length === 0 && (
                    <tr>
                      <td colSpan={6} className="text-center py-8 text-muted-foreground">
                        No visitor passes found.
                      </td>
                    </tr>
                  )}
                  {passes?.map((pass) => (
                    <tr key={pass.id} className="border-b last:border-0 hover:bg-muted/30 transition-colors">
                      <td className="px-4 py-3 font-medium">{pass.visitor_name}</td>
                      <td className="px-4 py-3 text-muted-foreground">{pass.visitor_email}</td>
                      <td className="px-4 py-3 text-muted-foreground">{pass.purpose}</td>
                      <td className="px-4 py-3">
                        <StatusBadge status={pass.status} />
                      </td>
                      <td className="px-4 py-3 text-muted-foreground">
                        {pass.check_in ? formatDateTime(pass.check_in) : '—'}
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-2">
                          {pass.status === 'pending' && (
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => approveMutation.mutate(String(pass.id))}
                              disabled={approveMutation.isPending}
                            >
                              Approve
                            </Button>
                          )}
                          {pass.status === 'approved' && (
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => checkInMutation.mutate(String(pass.id))}
                              disabled={checkInMutation.isPending}
                            >
                              Check In
                            </Button>
                          )}
                          {pass.status === 'checked_in' && (
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => checkOutMutation.mutate(String(pass.id))}
                              disabled={checkOutMutation.isPending}
                            >
                              Check Out
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
