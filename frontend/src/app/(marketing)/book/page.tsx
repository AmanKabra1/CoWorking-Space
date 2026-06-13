'use client'

import { useState } from 'react'
import Link from 'next/link'
import { useQuery, useMutation } from '@tanstack/react-query'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { publicService } from '@/lib/services'
import { formatCurrency } from '@/lib/utils'
import { CheckCircle2, Clock } from 'lucide-react'

const selectClass =
  'flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring'

export default function PublicBookingPage() {
  const [form, setForm] = useState({
    facility: '', booking_date: '', start_time: '', end_time: '',
    attendees_count: '1', purpose: '',
    guest_name: '', guest_email: '', guest_phone: '', guest_company: '',
  })

  const { data: facilities = [], isLoading } = useQuery({
    queryKey: ['public-facilities'],
    queryFn: () => publicService.facilities(),
  })

  const { data: availability } = useQuery({
    queryKey: ['public-availability', form.facility, form.booking_date],
    queryFn: () => publicService.availability(form.facility, form.booking_date),
    enabled: Boolean(form.facility && form.booking_date),
  })

  const selected = facilities.find(f => f.id === form.facility)

  const mutation = useMutation({
    mutationFn: () => publicService.createBooking({
      facility: form.facility,
      booking_date: form.booking_date,
      start_time: form.start_time,
      end_time: form.end_time,
      attendees_count: Number(form.attendees_count) || 1,
      purpose: form.purpose,
      guest_name: form.guest_name,
      guest_email: form.guest_email,
      guest_phone: form.guest_phone,
      guest_company: form.guest_company || undefined,
    }),
  })

  if (mutation.isSuccess) {
    return (
      <div className="max-w-xl mx-auto px-4 py-24 text-center">
        <CheckCircle2 className="h-14 w-14 text-green-600 mx-auto mb-4" />
        <h1 className="text-2xl font-bold">Request received</h1>
        <p className="mt-3 text-muted-foreground">
          Your booking request has been submitted and is awaiting approval. We&apos;ll email
          <span className="font-medium text-foreground"> {form.guest_email} </span>
          once it&apos;s reviewed, along with payment details if it&apos;s approved.
        </p>
        <Button className="mt-8" onClick={() => window.location.reload()}>Book another</Button>
      </div>
    )
  }

  return (
    <div className="max-w-3xl mx-auto px-4 py-12">
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight">Book a Space</h1>
        <p className="mt-2 text-muted-foreground">
          Reserve a meeting room or facility — no account needed. We&apos;ll review your request and email you.
        </p>
      </div>

      <div className="mb-6 flex flex-wrap items-center gap-x-2 gap-y-1 rounded-lg border bg-muted/40 px-4 py-3 text-sm text-muted-foreground">
        <span>Part of a member company?</span>
        <Link href="/login" className="font-medium text-primary hover:underline">Sign in</Link>
        <span>or</span>
        <Link href="/signup" className="font-medium text-primary hover:underline">join with your company code</Link>
        <span>for faster internal bookings.</span>
      </div>

      {isLoading ? (
        <div className="h-64 bg-muted rounded-lg animate-pulse" />
      ) : facilities.length === 0 ? (
        <Card><CardContent className="p-8 text-center text-muted-foreground">
          No facilities are open for public booking right now.
        </CardContent></Card>
      ) : (
        <Card>
          <CardContent className="p-6">
            <form
              onSubmit={(e) => { e.preventDefault(); mutation.mutate() }}
              className="space-y-5"
            >
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="space-y-1.5 sm:col-span-2">
                  <Label>Facility</Label>
                  <select
                    className={selectClass}
                    value={form.facility}
                    onChange={(e) => setForm({ ...form, facility: e.target.value })}
                    required
                  >
                    <option value="">Select a facility…</option>
                    {facilities.map((f) => (
                      <option key={f.id} value={f.id}>
                        {f.name}{f.building_name ? ` — ${f.building_name}` : ''} · {formatCurrency(f.price_per_hour)}/hr · cap {f.capacity}
                      </option>
                    ))}
                  </select>
                  {selected?.description && (
                    <p className="text-xs text-muted-foreground">{selected.description}</p>
                  )}
                </div>

                <div className="space-y-1.5">
                  <Label>Date</Label>
                  <Input type="date" value={form.booking_date} onChange={(e) => setForm({ ...form, booking_date: e.target.value })} required />
                </div>
                <div className="space-y-1.5">
                  <Label>Attendees</Label>
                  <Input type="number" min="1" max={selected?.capacity} value={form.attendees_count} onChange={(e) => setForm({ ...form, attendees_count: e.target.value })} />
                </div>
                <div className="space-y-1.5">
                  <Label>Start time</Label>
                  <Input type="time" value={form.start_time} onChange={(e) => setForm({ ...form, start_time: e.target.value })} required />
                </div>
                <div className="space-y-1.5">
                  <Label>End time</Label>
                  <Input type="time" value={form.end_time} onChange={(e) => setForm({ ...form, end_time: e.target.value })} required />
                </div>
              </div>

              {availability && availability.booked_slots.length > 0 && (
                <div className="rounded-md border bg-muted/40 p-3">
                  <div className="flex items-center gap-1.5 text-xs font-medium text-muted-foreground mb-1.5">
                    <Clock className="h-3.5 w-3.5" /> Already booked on this date — pick a free slot:
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {availability.booked_slots.map((s, i) => (
                      <span key={i} className="text-xs rounded bg-destructive/10 text-destructive px-2 py-0.5">
                        {s.start}–{s.end}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              <div className="space-y-1.5">
                <Label>Purpose</Label>
                <Input value={form.purpose} onChange={(e) => setForm({ ...form, purpose: e.target.value })} placeholder="e.g. Client meeting" required />
              </div>

              <div className="border-t pt-5">
                <h2 className="text-sm font-semibold mb-3">Your details</h2>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div className="space-y-1.5">
                    <Label>Full name</Label>
                    <Input value={form.guest_name} onChange={(e) => setForm({ ...form, guest_name: e.target.value })} required />
                  </div>
                  <div className="space-y-1.5">
                    <Label>Email</Label>
                    <Input type="email" value={form.guest_email} onChange={(e) => setForm({ ...form, guest_email: e.target.value })} required />
                  </div>
                  <div className="space-y-1.5">
                    <Label>Phone</Label>
                    <Input value={form.guest_phone} onChange={(e) => setForm({ ...form, guest_phone: e.target.value })} required />
                  </div>
                  <div className="space-y-1.5">
                    <Label>Company (optional)</Label>
                    <Input value={form.guest_company} onChange={(e) => setForm({ ...form, guest_company: e.target.value })} />
                  </div>
                </div>
              </div>

              {mutation.isError && (
                <p className="text-sm text-destructive">
                  Could not submit — that slot may be taken, or please check your details.
                </p>
              )}

              <Button type="submit" className="w-full" disabled={mutation.isPending}>
                {mutation.isPending ? 'Submitting…' : 'Request Booking'}
              </Button>
            </form>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
