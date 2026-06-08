'use client'

import { useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { paymentService } from '@/lib/services'
import { toast } from '@/hooks/use-toast'

interface Props {
  orderId: number
  gatewayOrderId: string
  amount: number
  currency: string
  apiKey: string
  invoiceId: number
  onSuccess: () => void
}

declare global {
  interface Window {
    Razorpay: new (options: Record<string, unknown>) => { open: () => void }
  }
}

export function RazorpayButton({ orderId, gatewayOrderId, amount, currency, apiKey, invoiceId, onSuccess }: Props) {
  useEffect(() => {
    if (document.getElementById('razorpay-script')) return
    const script = document.createElement('script')
    script.id = 'razorpay-script'
    script.src = 'https://checkout.razorpay.com/v1/checkout.js'
    script.async = true
    document.body.appendChild(script)
  }, [])

  const handleClick = () => {
    if (!window.Razorpay) {
      toast({ title: 'Razorpay not loaded yet. Please try again.', variant: 'destructive' })
      return
    }

    const rzp = new window.Razorpay({
      key: apiKey,
      amount,
      currency,
      order_id: gatewayOrderId,
      handler: async (response: Record<string, string>) => {
        try {
          await paymentService.verifyPayment(orderId, {
            payment_id: response.razorpay_payment_id,
            signature: response.razorpay_signature,
          })
          toast({ title: 'Payment successful', description: `Invoice #${invoiceId} marked as paid.` })
          onSuccess()
        } catch {
          toast({ title: 'Payment verification failed', variant: 'destructive' })
        }
      },
      modal: {
        ondismiss: () => {
          toast({ title: 'Payment cancelled', variant: 'destructive' })
        },
      },
    })

    rzp.open()
  }

  return (
    <Button size="sm" onClick={handleClick}>
      Pay Now
    </Button>
  )
}
