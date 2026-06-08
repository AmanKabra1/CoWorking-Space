import Link from 'next/link'
import { CheckCircle, ArrowRight } from 'lucide-react'

const plans = [
  {
    name: 'Starter',
    price: '₹2,999',
    period: '/mo',
    description: 'Perfect for small coworking spaces just getting started.',
    features: [
      'Up to 50 members',
      'Facility bookings with approval workflow',
      'Basic invoicing and payment collection',
      'Community posts and announcements',
      'Email support',
    ],
    cta: 'Get Started',
    highlighted: false,
  },
  {
    name: 'Growth',
    price: '₹7,999',
    period: '/mo',
    description: 'For growing spaces that need more power and automation.',
    features: [
      'Up to 300 members',
      'Advanced booking rules and capacity management',
      'Automated billing with Razorpay & Stripe',
      'Real-time member chat and events',
      'Analytics dashboard',
      'Priority support',
    ],
    cta: 'Start Free Trial',
    highlighted: true,
  },
  {
    name: 'Enterprise',
    price: 'Custom',
    period: '',
    description: 'For large operators with multiple locations and complex needs.',
    features: [
      'Unlimited members and locations',
      'Custom integrations and API access',
      'Dedicated onboarding and training',
      'SLA-backed uptime guarantee',
      'Dedicated account manager',
    ],
    cta: 'Contact Sales',
    highlighted: false,
  },
]

export default function PricingPage() {
  return (
    <div className="py-20">
      <div className="max-w-6xl mx-auto px-4">
        {/* Header */}
        <div className="text-center mb-16">
          <h1 className="text-4xl font-extrabold tracking-tight text-foreground sm:text-5xl">
            Simple, transparent pricing
          </h1>
          <p className="mt-4 text-lg text-muted-foreground max-w-xl mx-auto">
            Choose the plan that fits your space. Upgrade or downgrade at any time.
          </p>
        </div>

        {/* Plans */}
        <div className="grid gap-8 sm:grid-cols-3 items-start">
          {plans.map((plan) => (
            <div
              key={plan.name}
              className={
                plan.highlighted
                  ? 'rounded-xl border-2 border-primary bg-card p-8 shadow-lg ring-2 ring-primary/20'
                  : 'rounded-xl border bg-card p-8 shadow-sm'
              }
            >
              {plan.highlighted && (
                <div className="inline-block rounded-full bg-primary px-3 py-0.5 text-xs font-semibold text-primary-foreground mb-4">
                  Most Popular
                </div>
              )}
              <h2 className="text-xl font-bold text-foreground">{plan.name}</h2>
              <div className="mt-4 flex items-end gap-1">
                <span className="text-4xl font-extrabold text-foreground">{plan.price}</span>
                {plan.period && (
                  <span className="text-sm text-muted-foreground mb-1">{plan.period}</span>
                )}
              </div>
              <p className="mt-3 text-sm text-muted-foreground">{plan.description}</p>

              <ul className="mt-6 space-y-3">
                {plan.features.map((feature) => (
                  <li key={feature} className="flex items-start gap-2 text-sm text-foreground">
                    <CheckCircle className="h-4 w-4 text-primary shrink-0 mt-0.5" />
                    {feature}
                  </li>
                ))}
              </ul>

              <Link
                href="/login"
                className={
                  'mt-8 flex items-center justify-center gap-2 rounded-md px-6 py-2.5 text-sm font-semibold transition-colors ' +
                  (plan.highlighted
                    ? 'bg-primary text-primary-foreground hover:bg-primary/90'
                    : 'border border-input bg-background text-foreground hover:bg-accent')
                }
              >
                {plan.cta}
                <ArrowRight className="h-4 w-4" />
              </Link>
            </div>
          ))}
        </div>

        {/* Footer note */}
        <p className="mt-12 text-center text-sm text-muted-foreground">
          All plans include a 14-day free trial. No credit card required to start.
        </p>
      </div>
    </div>
  )
}
