'use client'

import { Suspense, useState } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import Link from 'next/link'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Building2, Eye, EyeOff, KeyRound } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { useAuthStore } from '@/store/auth'
import { authService } from '@/lib/services'
import { toast } from '@/hooks/use-toast'

const schema = z
  .object({
    join_code: z.string().min(1, 'Enter the code your company gave you'),
    first_name: z.string().min(1, 'First name is required'),
    last_name: z.string().min(1, 'Last name is required'),
    email: z.string().email('Enter a valid email'),
    phone: z.string().optional(),
    department: z.string().optional(),
    employee_number: z.string().optional(),
    password: z.string().min(8, 'At least 8 characters'),
    password_confirm: z.string().min(1, 'Confirm your password'),
  })
  .refine((d) => d.password === d.password_confirm, {
    message: 'Passwords do not match',
    path: ['password_confirm'],
  })

type FormData = z.infer<typeof schema>

/** Pull the first human-readable error out of a DRF error response. */
function firstApiError(err: unknown): string | null {
  const data = (err as { response?: { data?: unknown } })?.response?.data
  if (!data || typeof data !== 'object') return null
  for (const v of Object.values(data as Record<string, unknown>)) {
    if (typeof v === 'string') return v
    if (Array.isArray(v) && typeof v[0] === 'string') return v[0]
  }
  return null
}

function SignupForm() {
  const router = useRouter()
  const codeFromUrl = useSearchParams().get('code') ?? ''
  const { setTokens, setUser } = useAuthStore()
  const [loading, setLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)

  const { register, handleSubmit, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { join_code: codeFromUrl },
  })

  async function onSubmit(data: FormData) {
    setLoading(true)
    try {
      const res = await authService.join({
        join_code: data.join_code.trim(),
        email: data.email,
        first_name: data.first_name,
        last_name: data.last_name,
        phone: data.phone || undefined,
        department: data.department || undefined,
        employee_number: data.employee_number || undefined,
        password: data.password,
        password_confirm: data.password_confirm,
      })
      setTokens(res.tokens.access, res.tokens.refresh)
      setUser(res.user)
      toast({ title: 'Welcome aboard!', description: `Joined ${res.user.company_name ?? 'your company'}.` })
      router.push('/dashboard')
    } catch (err) {
      toast({
        title: 'Could not sign up',
        description: firstApiError(err) ?? 'Please check your details and try again.',
        variant: 'destructive',
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-sidebar to-sidebar/80 flex items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center pb-2">
          <div className="flex justify-center mb-3">
            <div className="h-12 w-12 rounded-xl bg-primary flex items-center justify-center">
              <Building2 className="h-6 w-6 text-white" />
            </div>
          </div>
          <CardTitle className="text-2xl">Join your company</CardTitle>
          <CardDescription>Enter the code your company admin shared to create your account</CardDescription>
        </CardHeader>
        <CardContent className="pt-4">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div className="space-y-1.5">
              <Label htmlFor="join_code">Company join code</Label>
              <div className="relative">
                <KeyRound className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  id="join_code"
                  placeholder="e.g. N97LXS2Y"
                  autoCapitalize="characters"
                  className="pl-9 tracking-widest font-mono uppercase"
                  disabled={loading}
                  {...register('join_code')}
                />
              </div>
              {errors.join_code && <p className="text-xs text-destructive">{errors.join_code.message}</p>}
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1.5">
                <Label htmlFor="first_name">First name</Label>
                <Input id="first_name" disabled={loading} {...register('first_name')} />
                {errors.first_name && <p className="text-xs text-destructive">{errors.first_name.message}</p>}
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="last_name">Last name</Label>
                <Input id="last_name" disabled={loading} {...register('last_name')} />
                {errors.last_name && <p className="text-xs text-destructive">{errors.last_name.message}</p>}
              </div>
            </div>

            <div className="space-y-1.5">
              <Label htmlFor="email">Email</Label>
              <Input id="email" type="email" placeholder="you@company.com" autoComplete="email" disabled={loading} {...register('email')} />
              {errors.email && <p className="text-xs text-destructive">{errors.email.message}</p>}
            </div>

            <div className="space-y-1.5">
              <Label htmlFor="phone">Phone <span className="text-muted-foreground font-normal">(optional)</span></Label>
              <Input id="phone" type="tel" autoComplete="tel" disabled={loading} {...register('phone')} />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1.5">
                <Label htmlFor="department">Department <span className="text-muted-foreground font-normal">(optional)</span></Label>
                <Input id="department" disabled={loading} {...register('department')} />
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="employee_number">Employee no. <span className="text-muted-foreground font-normal">(optional)</span></Label>
                <Input id="employee_number" disabled={loading} {...register('employee_number')} />
              </div>
            </div>

            <div className="space-y-1.5">
              <Label htmlFor="password">Password</Label>
              <div className="relative">
                <Input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  autoComplete="new-password"
                  className="pr-10"
                  disabled={loading}
                  {...register('password')}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(v => !v)}
                  className="absolute inset-y-0 right-0 flex items-center px-3 text-muted-foreground hover:text-foreground transition-colors"
                  tabIndex={-1}
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                >
                  {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
              {errors.password && <p className="text-xs text-destructive">{errors.password.message}</p>}
            </div>

            <div className="space-y-1.5">
              <Label htmlFor="password_confirm">Confirm password</Label>
              <Input
                id="password_confirm"
                type={showPassword ? 'text' : 'password'}
                autoComplete="new-password"
                disabled={loading}
                {...register('password_confirm')}
              />
              {errors.password_confirm && <p className="text-xs text-destructive">{errors.password_confirm.message}</p>}
            </div>

            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? 'Creating account...' : 'Create account'}
            </Button>

            <p className="text-center text-sm text-muted-foreground">
              Already have an account?{' '}
              <Link href="/login" className="font-medium text-primary hover:underline">Sign in</Link>
            </p>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}

export default function SignupPage() {
  // useSearchParams() (read in SignupForm) must sit under a Suspense boundary,
  // otherwise `next build` fails to prerender this page.
  return (
    <Suspense fallback={<div className="min-h-screen bg-gradient-to-br from-sidebar to-sidebar/80" />}>
      <SignupForm />
    </Suspense>
  )
}
