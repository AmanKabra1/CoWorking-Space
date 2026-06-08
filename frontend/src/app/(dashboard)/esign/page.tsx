'use client'

import { useQuery } from '@tanstack/react-query'
import { FileSignature, Download } from 'lucide-react'
import { PageHeader } from '@/components/shared/PageHeader'
import { StatusBadge } from '@/components/shared/StatusBadge'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { esignService } from '@/lib/services'
import { formatDate } from '@/lib/utils'

export default function ESignPage() {
  const { data, isLoading } = useQuery({
    queryKey: ['esign-requests'],
    queryFn: () => esignService.list(),
  })

  return (
    <div className="space-y-4">
      <PageHeader
        title="E-Sign"
        description="Digital signature requests"
        action={
          <Button size="sm" variant="outline">
            <FileSignature className="h-4 w-4 mr-1.5" />
            New Request
          </Button>
        }
      />

      {isLoading ? (
        <div className="space-y-3">
          {[...Array(4)].map((_, i) => <div key={i} className="h-16 bg-muted rounded-lg animate-pulse" />)}
        </div>
      ) : (
        <Card>
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b bg-muted/50">
                    <th className="text-left px-4 py-3 font-medium">Document</th>
                    <th className="text-left px-4 py-3 font-medium">Created by</th>
                    <th className="text-left px-4 py-3 font-medium">Signers</th>
                    <th className="text-left px-4 py-3 font-medium">Status</th>
                    <th className="text-left px-4 py-3 font-medium">Created</th>
                    <th className="text-left px-4 py-3 font-medium">Certificate</th>
                  </tr>
                </thead>
                <tbody>
                  {data?.results?.length === 0 && (
                    <tr>
                      <td colSpan={6} className="text-center py-10 text-muted-foreground">
                        No signature requests yet.
                      </td>
                    </tr>
                  )}
                  {data?.results?.map((req) => {
                    const signed = req.records?.filter((r) => r.status === 'signed').length ?? 0
                    const total = req.records?.length ?? 0
                    return (
                      <tr key={req.id} className="border-b last:border-0 hover:bg-muted/30 transition-colors">
                        <td className="px-4 py-3 font-medium">{req.title}</td>
                        <td className="px-4 py-3 text-muted-foreground">{req.created_by_name}</td>
                        <td className="px-4 py-3">
                          <span className="text-xs bg-muted px-2 py-0.5 rounded">
                            {signed}/{total} signed
                          </span>
                        </td>
                        <td className="px-4 py-3">
                          <StatusBadge status={req.status} />
                        </td>
                        <td className="px-4 py-3 text-muted-foreground">{formatDate(req.created_at)}</td>
                        <td className="px-4 py-3">
                          {req.certificate_file && (
                            <Button variant="ghost" size="icon" asChild>
                              <a href={req.certificate_file} target="_blank" rel="noreferrer">
                                <Download className="h-4 w-4" />
                              </a>
                            </Button>
                          )}
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
