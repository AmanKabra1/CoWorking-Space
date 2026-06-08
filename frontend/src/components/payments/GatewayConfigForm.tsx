'use client'

import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { paymentService } from '@/lib/services'
import type { PaymentGateway } from '@/types'

interface FormValues {
  provider: 'razorpay' | 'stripe'
  api_key: string
  api_secret: string
}

interface Props {
  existing?: PaymentGateway
  onSaved?: () => void
}

export function GatewayConfigForm({ existing, onSaved }: Props) {
  const queryClient = useQueryClient()
  const [saved, setSaved] = useState(false)

  const { register, handleSubmit, formState: { errors } } = useForm<FormValues>({
    defaultValues: {
      provider: existing?.provider ?? 'razorpay',
      api_key: existing?.api_key ?? '',
      api_secret: '',
    },
  })

  const mutation = useMutation({
    mutationFn: (data: FormValues) => paymentService.saveGateway(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['payment-gateway'] })
      setSaved(true)
      onSaved?.()
    },
  })

  return (
    <Card>
      <CardHeader>
        <CardTitle>Payment Gateway Configuration</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit((d) => mutation.mutate(d))} className="space-y-4 max-w-md">
          <div className="space-y-1">
            <Label htmlFor="provider">Provider</Label>
            <select
              id="provider"
              {...register('provider', { required: true })}
              className="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
            >
              <option value="razorpay">Razorpay</option>
              <option value="stripe">Stripe</option>
            </select>
          </div>

          <div className="space-y-1">
            <Label htmlFor="api_key">API Key (Public)</Label>
            <Input
              id="api_key"
              {...register('api_key', { required: 'API key is required' })}
              placeholder="rzp_live_xxxx or pk_live_xxxx"
            />
            {errors.api_key && <p className="text-xs text-destructive">{errors.api_key.message}</p>}
          </div>

          <div className="space-y-1">
            <Label htmlFor="api_secret">
              API Secret{existing && <span className="text-muted-foreground ml-1">(leave blank to keep existing)</span>}
            </Label>
            <Input
              id="api_secret"
              type="password"
              {...register('api_secret', { required: !existing ? 'API secret is required' : false })}
              placeholder={existing ? '●●●●●●●●' : 'Enter secret key'}
            />
            {errors.api_secret && <p className="text-xs text-destructive">{errors.api_secret.message}</p>}
          </div>

          {mutation.isError && (
            <p className="text-sm text-destructive">Failed to save gateway configuration.</p>
          )}
          {saved && (
            <p className="text-sm text-green-600">Gateway configuration saved.</p>
          )}

          <Button type="submit" disabled={mutation.isPending}>
            {mutation.isPending ? 'Saving…' : 'Save Configuration'}
          </Button>
        </form>
      </CardContent>
    </Card>
  )
}
