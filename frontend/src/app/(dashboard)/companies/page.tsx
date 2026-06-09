'use client'

import { useQuery } from '@tanstack/react-query'
import { PageHeader } from '@/components/shared/PageHeader'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { companyService } from '@/lib/services'
import { formatDate } from '@/lib/utils'
import { useAuthStore } from '@/store/auth'
import { useRouter } from 'next/navigation'
import { useEffect } from 'react'

export default function CompaniesPage() {
  const router = useRouter()
  const { user } = useAuthStore()

  useEffect(() => {
    if (user && user.role !== 'super_admin') {
      router.replace('/dashboard')
    }
  }, [user, router])

  const { data, isLoading } = useQuery({
    queryKey: ['companies'],
    queryFn: () => companyService.list(),
    enabled: user?.role === 'super_admin',
  })

  if (user?.role !== 'super_admin') return null

  return (
    <div className="space-y-4">
      <PageHeader title="Companies" description="All tenant companies in CoWorkHub" />

      {isLoading ? (
        <div className="space-y-3">
          {[...Array(5)].map((_, i) => <div key={i} className="h-14 bg-muted rounded-lg animate-pulse" />)}
        </div>
      ) : (
        <Card>
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b bg-muted/50">
                    <th className="text-left px-4 py-3 font-medium">Company</th>
                    <th className="text-left px-4 py-3 font-medium">Industry</th>
                    <th className="text-left px-4 py-3 font-medium">Employees</th>
                    <th className="text-left px-4 py-3 font-medium">Status</th>
                    <th className="text-left px-4 py-3 font-medium">Joined</th>
                  </tr>
                </thead>
                <tbody>
                  {data?.results?.length === 0 && (
                    <tr>
                      <td colSpan={5} className="text-center py-8 text-muted-foreground">No companies found.</td>
                    </tr>
                  )}
                  {data?.results?.map((company) => (
                    <tr key={company.id} className="border-b last:border-0 hover:bg-muted/30 transition-colors">
                      <td className="px-4 py-3">
                        <div className="font-medium">{company.name}</div>
                        <div className="text-xs text-muted-foreground">{company.email}</div>
                      </td>
                      <td className="px-4 py-3 text-muted-foreground">{company.industry || '—'}</td>
                      <td className="px-4 py-3">{company.employee_count ?? '—'}</td>
                      <td className="px-4 py-3">
                        <Badge variant={company.status === 'active' ? 'success' : 'secondary'}>
                          {company.status.charAt(0).toUpperCase() + company.status.slice(1)}
                        </Badge>
                      </td>
                      <td className="px-4 py-3 text-muted-foreground">{formatDate(company.created_at)}</td>
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
