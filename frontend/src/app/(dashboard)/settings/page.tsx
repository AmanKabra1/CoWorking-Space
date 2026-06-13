'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { PageHeader } from '@/components/shared/PageHeader'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { useAuthStore } from '@/store/auth'
import { companySettingsService, companyService } from '@/lib/services'

type Tab = 'profile' | 'appearance'

export default function SettingsPage() {
  const router = useRouter()
  const { user } = useAuthStore()
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState<Tab>('profile')
  const [saved, setSaved] = useState(false)
  const [copied, setCopied] = useState<'code' | 'link' | null>(null)

  useEffect(() => {
    if (user && user.role === 'employee') {
      router.replace('/dashboard')
    }
  }, [user, router])

  const { data: company, isLoading } = useQuery({
    queryKey: ['company-settings'],
    queryFn: () => companySettingsService.get(),
    enabled: user?.role === 'super_admin' || user?.role === 'company_admin',
  })

  const [form, setForm] = useState({
    name: '',
    email: '',
    phone: '',
    address: '',
    city: '',
    state: '',
    pincode: '',
    website: '',
  })

  useEffect(() => {
    if (company) {
      setForm({
        name: company.name ?? '',
        email: company.email ?? '',
        phone: company.phone ?? '',
        address: company.address ?? '',
        city: company.city ?? '',
        state: company.state ?? '',
        pincode: company.pincode ?? '',
        website: company.website ?? '',
      })
    }
  }, [company])

  const mutation = useMutation({
    mutationFn: (data: typeof form) => companySettingsService.update(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['company-settings'] })
      setSaved(true)
      setTimeout(() => setSaved(false), 3000)
    },
  })

  const regenMutation = useMutation({
    mutationFn: () => companyService.regenerateJoinCode(company!.id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['company-settings'] }),
  })

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }))
  }

  const copyToClipboard = async (kind: 'code' | 'link') => {
    if (!company?.join_code) return
    const text =
      kind === 'code'
        ? company.join_code
        : `${window.location.origin}/signup?code=${company.join_code}`
    await navigator.clipboard.writeText(text)
    setCopied(kind)
    setTimeout(() => setCopied(null), 2000)
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    mutation.mutate(form)
  }

  if (user?.role === 'employee') return null

  const tabClass = (tab: Tab) =>
    `px-4 py-2 text-sm font-medium rounded-md transition-colors ${
      activeTab === tab
        ? 'bg-primary text-primary-foreground'
        : 'text-muted-foreground hover:text-foreground hover:bg-muted'
    }`

  return (
    <div className="space-y-6 max-w-3xl">
      <PageHeader title="Settings" description="Manage your company profile and appearance." />

      <div className="flex gap-2">
        <button className={tabClass('profile')} onClick={() => setActiveTab('profile')}>
          Company Profile
        </button>
        <button className={tabClass('appearance')} onClick={() => setActiveTab('appearance')}>
          Appearance
        </button>
      </div>

      {activeTab === 'profile' && (
        <>
        <Card>
          <CardHeader>
            <CardTitle>Company Profile</CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="space-y-3">
                {[...Array(6)].map((_, i) => (
                  <div key={i} className="h-10 bg-muted rounded animate-pulse" />
                ))}
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div className="space-y-1">
                    <label className="text-sm font-medium">Company Name</label>
                    <Input name="name" value={form.name} onChange={handleChange} required />
                  </div>
                  <div className="space-y-1">
                    <label className="text-sm font-medium">Email</label>
                    <Input name="email" type="email" value={form.email} onChange={handleChange} required />
                  </div>
                  <div className="space-y-1">
                    <label className="text-sm font-medium">Phone</label>
                    <Input name="phone" value={form.phone} onChange={handleChange} />
                  </div>
                  <div className="space-y-1">
                    <label className="text-sm font-medium">Website</label>
                    <Input name="website" type="url" value={form.website} onChange={handleChange} placeholder="https://" />
                  </div>
                </div>

                <div className="space-y-1">
                  <label className="text-sm font-medium">Address</label>
                  <Input name="address" value={form.address} onChange={handleChange} />
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  <div className="space-y-1">
                    <label className="text-sm font-medium">City</label>
                    <Input name="city" value={form.city} onChange={handleChange} />
                  </div>
                  <div className="space-y-1">
                    <label className="text-sm font-medium">State</label>
                    <Input name="state" value={form.state} onChange={handleChange} />
                  </div>
                  <div className="space-y-1">
                    <label className="text-sm font-medium">Pincode</label>
                    <Input name="pincode" value={form.pincode} onChange={handleChange} />
                  </div>
                </div>

                <div className="flex items-center gap-3 pt-2">
                  <Button type="submit" disabled={mutation.isPending}>
                    {mutation.isPending ? 'Saving…' : 'Save Changes'}
                  </Button>
                  {saved && (
                    <span className="text-sm text-green-600">Changes saved successfully.</span>
                  )}
                  {mutation.isError && (
                    <span className="text-sm text-destructive">Failed to save. Please try again.</span>
                  )}
                </div>
              </form>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Team Join Code</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-muted-foreground">
              Share this code with your team. Employees create their own accounts at{' '}
              <span className="font-mono">/signup</span> and are added to{' '}
              {company?.name ?? 'your company'} automatically — no manual setup needed.
            </p>
            <div className="flex flex-wrap items-center gap-3">
              <code className="rounded-lg border bg-muted px-4 py-2 text-lg font-mono tracking-[0.3em]">
                {company?.join_code ?? '—'}
              </code>
              <Button type="button" variant="outline" onClick={() => copyToClipboard('code')} disabled={!company?.join_code}>
                {copied === 'code' ? 'Copied!' : 'Copy code'}
              </Button>
              <Button type="button" variant="outline" onClick={() => copyToClipboard('link')} disabled={!company?.join_code}>
                {copied === 'link' ? 'Link copied!' : 'Copy invite link'}
              </Button>
              <Button
                type="button"
                variant="ghost"
                onClick={() => regenMutation.mutate()}
                disabled={regenMutation.isPending || !company}
              >
                {regenMutation.isPending ? 'Regenerating…' : 'Regenerate'}
              </Button>
            </div>
            <p className="text-xs text-muted-foreground">
              Regenerating issues a new code and invalidates the old one — anyone who hasn’t joined yet will need the new code.
            </p>
          </CardContent>
        </Card>
        </>
      )}

      {activeTab === 'appearance' && (
        <Card>
          <CardHeader>
            <CardTitle>Appearance</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-1">
              <label className="text-sm font-medium">Company Slug</label>
              <Input value={company?.slug ?? ''} readOnly className="bg-muted text-muted-foreground" />
              <p className="text-xs text-muted-foreground">
                Used for subdomain access (e.g. <span className="font-mono">{company?.slug ?? 'your-company'}.coworkhub.com</span>).
                The slug is automatically derived from your company name.
              </p>
            </div>
            <div className="rounded-lg border border-dashed p-6 text-center text-muted-foreground">
              <p className="text-sm font-medium">White-label branding coming soon</p>
              <p className="text-xs mt-1">Custom logo, colours, and domain support will be available in a future release.</p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
