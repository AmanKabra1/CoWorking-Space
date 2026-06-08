import Link from 'next/link'
import {
  Calendar,
  CreditCard,
  Users,
  MessageSquare,
  CheckCircle,
  ArrowRight,
  BarChart3,
  Building2,
} from 'lucide-react'

const features = [
  {
    icon: Calendar,
    title: 'Smart Bookings',
    description:
      'Calendar-based facility reservation with an integrated approval workflow. Members book desks, meeting rooms, and event spaces in seconds.',
  },
  {
    icon: CreditCard,
    title: 'Automated Billing',
    description:
      'Auto-generate invoices on any schedule and accept payments via Razorpay and Stripe. Reconciliation is handled automatically.',
  },
  {
    icon: MessageSquare,
    title: 'Member Community',
    description:
      'Posts, events, and real-time chat keep your members engaged and connected — all built into the same platform.',
  },
]

const stats = [
  { value: '500+', label: 'Spaces' },
  { value: '10,000+', label: 'Members' },
  { value: '99.9%', label: 'Uptime' },
  { value: '24/7', label: 'Support' },
]

const testimonials = [
  {
    quote:
      'Reduced our admin work by 60%. Invoicing used to take our team a full day every month — now it runs automatically overnight.',
    name: 'Sarah M.',
    title: 'Operations Manager',
    company: 'Acme Corp',
  },
  {
    quote:
      'Our members love the booking experience. The approval workflow is exactly what we needed to keep everything organised without constant back-and-forth.',
    name: 'Raj K.',
    title: 'Founder',
    company: 'TechHub',
  },
  {
    quote:
      'The community features are outstanding. Member engagement has doubled since we switched and the chat keeps everyone in the loop.',
    name: 'Priya L.',
    title: 'Community Manager',
    company: 'StartSpace',
  },
]

export default function MarketingHomePage() {
  return (
    <>
      {/* Hero */}
      <section className="relative overflow-hidden">
        <div
          aria-hidden="true"
          className="pointer-events-none absolute inset-0 -z-10 bg-gradient-to-br from-primary/10 via-background to-background"
        />
        <div className="max-w-6xl mx-auto px-4 py-24 text-center">
          <div className="inline-flex items-center gap-2 rounded-full border px-3 py-1 text-xs font-medium text-muted-foreground mb-6">
            <Building2 className="h-3.5 w-3.5" />
            The Modern OS for Coworking Spaces
          </div>
          <h1 className="text-5xl font-extrabold tracking-tight text-foreground sm:text-6xl lg:text-7xl">
            The Modern OS for
            <br />
            <span className="text-primary">Coworking Spaces</span>
          </h1>
          <p className="mt-6 max-w-2xl mx-auto text-lg text-muted-foreground">
            Manage bookings, billing, members, and community — all in one platform. Built for
            operators who want to focus on people, not paperwork.
          </p>
          <div className="mt-10 flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/login"
              className="inline-flex items-center justify-center gap-2 rounded-md px-8 py-3 text-sm font-semibold bg-primary text-primary-foreground hover:bg-primary/90 transition-colors"
            >
              Get Started
              <ArrowRight className="h-4 w-4" />
            </Link>
            <Link
              href="/login"
              className="inline-flex items-center justify-center gap-2 rounded-md border px-8 py-3 text-sm font-semibold text-foreground hover:bg-accent transition-colors"
            >
              View Demo
            </Link>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-20 bg-muted/40">
        <div className="max-w-6xl mx-auto px-4">
          <div className="text-center mb-14">
            <h2 className="text-3xl font-bold tracking-tight text-foreground">
              Everything your space needs
            </h2>
            <p className="mt-3 text-muted-foreground">
              One platform to replace the spreadsheets, emails, and disconnected tools.
            </p>
          </div>
          <div className="grid gap-8 sm:grid-cols-3">
            {features.map(({ icon: Icon, title, description }) => (
              <div
                key={title}
                className="rounded-xl border bg-card p-8 shadow-sm hover:shadow-md transition-shadow"
              >
                <div className="inline-flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10 mb-5">
                  <Icon className="h-6 w-6 text-primary" />
                </div>
                <h3 className="text-lg font-semibold text-foreground mb-2">{title}</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">{description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="py-16 bg-primary">
        <div className="max-w-6xl mx-auto px-4">
          <div className="grid grid-cols-2 gap-8 sm:grid-cols-4">
            {stats.map(({ value, label }) => (
              <div key={label} className="text-center">
                <div className="text-4xl font-extrabold text-white">{value}</div>
                <div className="mt-1 text-sm font-medium text-primary-foreground/70">{label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="py-20">
        <div className="max-w-6xl mx-auto px-4">
          <div className="text-center mb-14">
            <h2 className="text-3xl font-bold tracking-tight text-foreground">
              Trusted by operators worldwide
            </h2>
            <p className="mt-3 text-muted-foreground">
              See what space operators are saying about CoWorkHub.
            </p>
          </div>
          <div className="grid gap-8 sm:grid-cols-3">
            {testimonials.map(({ quote, name, title, company }) => (
              <div
                key={name}
                className="rounded-xl border bg-card p-8 shadow-sm flex flex-col gap-4"
              >
                <div className="flex gap-0.5">
                  {Array.from({ length: 5 }).map((_, i) => (
                    <svg
                      key={i}
                      className="h-4 w-4 fill-amber-400 text-amber-400"
                      viewBox="0 0 20 20"
                      aria-hidden="true"
                    >
                      <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                    </svg>
                  ))}
                </div>
                <p className="text-sm text-muted-foreground leading-relaxed flex-1">
                  &ldquo;{quote}&rdquo;
                </p>
                <div>
                  <div className="font-semibold text-foreground text-sm">{name}</div>
                  <div className="text-xs text-muted-foreground">
                    {title}, {company}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Banner */}
      <section className="py-20 bg-muted/40">
        <div className="max-w-3xl mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
            Ready to modernize your space?
          </h2>
          <p className="mt-4 text-muted-foreground">
            Join hundreds of coworking operators who have already switched. No credit card required
            to start.
          </p>
          <Link
            href="/login"
            className="mt-8 inline-flex items-center justify-center gap-2 rounded-md px-8 py-3 text-sm font-semibold bg-primary text-primary-foreground hover:bg-primary/90 transition-colors"
          >
            Start Free Trial
            <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
      </section>
    </>
  )
}
