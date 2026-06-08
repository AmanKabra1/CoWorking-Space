'use client'

import { useEffect, useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useRouter } from 'next/navigation'
import { PageHeader } from '@/components/shared/PageHeader'
import { StatusBadge } from '@/components/shared/StatusBadge'
import { Card, CardContent } from '@/components/ui/card'
import { GatewayConfigForm } from '@/components/payments/GatewayConfigForm'
import { RazorpayButton } from '@/components/payments/RazorpayButton'
import { paymentService } from '@/lib/services'
import { useAuthStore } from '@/store/auth'
import { formatCurrency, formatDate } from '@/lib/utils'
import { toast } from '@/hooks/use-toast'

export default function PaymentsPage() {
  const router = useRouter()
  const { user } = useAuthStore()
  const queryClient = useQueryClient()

  const [activeOrder, setActiveOrder] = useState<{
    orderId: number
    gatewayOrderId: string
    amount: number
    currency: string
    key: string
    provider: string
    invoiceId: number
  } | null>(null)

  useEffect(() => {
    if (user && user.role === 'employee') {
      router.replace('/dashboard')
    }
  }, [user, router])

  const { data: gatewayData, isLoading: gatewayLoading } = useQuery({
    queryKey: ['payment-gateway'],
    queryFn: () => paymentService.getGateway(),
    retry: false,
  })

  const { data: ordersData, isLoading: ordersLoading } = useQuery({
    queryKey: ['payment-orders'],
    queryFn: () => paymentService.listOrders(),
  })

  const createOrderMutation = useMutation({
    mutationFn: (invoiceId: number) => paymentService.createOrder(invoiceId),
    onSuccess: (data) => {
      if (data.provider === 'razorpay') {
        setActiveOrder({
          orderId: data.order_id,
          gatewayOrderId: data.gateway_order_id,
          amount: data.amount,
          currency: data.currency,
          key: data.key,
          provider: data.provider,
          invoiceId: data.order_id,
        })
      } else {
        toast({ title: 'Stripe checkout not supported in this UI yet.', variant: 'destructive' })
      }
    },
    onError: () => {
      toast({ title: 'Failed to create payment order.', variant: 'destructive' })
    },
  })

  if (user?.role === 'employee') return null

  return (
    <div className="space-y-6">
      <PageHeader title="Payments" description="Configure payment gateway and manage payment orders" />

      <div className="space-y-4">
        {gatewayLoading ? (
          <div className="h-48 bg-muted rounded-lg animate-pulse" />
        ) : (
          <GatewayConfigForm
            existing={gatewayData}
            onSaved={() => queryClient.invalidateQueries({ queryKey: ['payment-gateway'] })}
          />
        )}
      </div>

      <div className="space-y-2">
        <h2 className="text-lg font-semibold">Recent Payment Orders</h2>

        {ordersLoading ? (
          <div className="space-y-3">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-12 bg-muted rounded-lg animate-pulse" />
            ))}
          </div>
        ) : (
          <Card>
            <CardContent className="p-0">
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b bg-muted/50">
                      <th className="text-left px-4 py-3 font-medium">Order ID</th>
                      <th className="text-left px-4 py-3 font-medium">Invoice #</th>
                      <th className="text-left px-4 py-3 font-medium">Provider</th>
                      <th className="text-left px-4 py-3 font-medium">Amount</th>
                      <th className="text-left px-4 py-3 font-medium">Status</th>
                      <th className="text-left px-4 py-3 font-medium">Date</th>
                      <th className="text-left px-4 py-3 font-medium">Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {!ordersData?.results?.length && (
                      <tr>
                        <td colSpan={7} className="text-center py-8 text-muted-foreground">
                          No payment orders found.
                        </td>
                      </tr>
                    )}
                    {ordersData?.results?.map((order) => (
                      <tr key={order.id} className="border-b last:border-0 hover:bg-muted/30 transition-colors">
                        <td className="px-4 py-3 font-mono text-xs">{order.gateway_order_id}</td>
                        <td className="px-4 py-3">{order.invoice}</td>
                        <td className="px-4 py-3 capitalize">{order.provider}</td>
                        <td className="px-4 py-3 font-medium">{formatCurrency(order.amount)}</td>
                        <td className="px-4 py-3">
                          <StatusBadge status={order.status} />
                        </td>
                        <td className="px-4 py-3 text-muted-foreground">{formatDate(order.created_at)}</td>
                        <td className="px-4 py-3">
                          {order.status === 'pending' && order.provider === 'razorpay' && (
                            activeOrder?.gatewayOrderId === order.gateway_order_id ? (
                              <RazorpayButton
                                orderId={activeOrder.orderId}
                                gatewayOrderId={activeOrder.gatewayOrderId}
                                amount={activeOrder.amount}
                                currency={activeOrder.currency}
                                apiKey={activeOrder.key}
                                invoiceId={Number(order.invoice)}
                                onSuccess={() => {
                                  setActiveOrder(null)
                                  queryClient.invalidateQueries({ queryKey: ['payment-orders'] })
                                }}
                              />
                            ) : (
                              <button
                                className="text-sm text-primary underline underline-offset-2"
                                onClick={() => createOrderMutation.mutate(Number(order.invoice))}
                                disabled={createOrderMutation.isPending}
                              >
                                Pay Now
                              </button>
                            )
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
    </div>
  )
}
