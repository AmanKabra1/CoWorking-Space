'use client'

import { useQuery } from '@tanstack/react-query'
import { Download } from 'lucide-react'
import { PageHeader } from '@/components/shared/PageHeader'
import { StatusBadge } from '@/components/shared/StatusBadge'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { invoiceService } from '@/lib/services'
import { formatCurrency, formatDate } from '@/lib/utils'

export default function InvoicesPage() {
  const { data, isLoading } = useQuery({
    queryKey: ['invoices'],
    queryFn: () => invoiceService.list(),
  })

  return (
    <div className="space-y-4">
      <PageHeader title="Invoices" description="Billing and payment records" />

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
                    <th className="text-left px-4 py-3 font-medium">Invoice #</th>
                    <th className="text-left px-4 py-3 font-medium">Company</th>
                    <th className="text-left px-4 py-3 font-medium">Amount</th>
                    <th className="text-left px-4 py-3 font-medium">Due Date</th>
                    <th className="text-left px-4 py-3 font-medium">Status</th>
                    <th className="text-left px-4 py-3 font-medium">PDF</th>
                  </tr>
                </thead>
                <tbody>
                  {data?.results?.length === 0 && (
                    <tr>
                      <td colSpan={6} className="text-center py-8 text-muted-foreground">No invoices found.</td>
                    </tr>
                  )}
                  {data?.results?.map((inv) => (
                    <tr key={inv.id} className="border-b last:border-0 hover:bg-muted/30 transition-colors">
                      <td className="px-4 py-3 font-mono text-xs">{inv.invoice_number}</td>
                      <td className="px-4 py-3">{inv.company_name}</td>
                      <td className="px-4 py-3 font-medium">{formatCurrency(inv.total_amount)}</td>
                      <td className="px-4 py-3 text-muted-foreground">{formatDate(inv.due_date)}</td>
                      <td className="px-4 py-3"><StatusBadge status={inv.status} /></td>
                      <td className="px-4 py-3">
                        {inv.pdf_url && (
                          <Button variant="ghost" size="icon" asChild>
                            <a href={inv.pdf_url} target="_blank" rel="noreferrer">
                              <Download className="h-4 w-4" />
                            </a>
                          </Button>
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
