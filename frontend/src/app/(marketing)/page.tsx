import Link from 'next/link'
import {
  ArrowRight,
  Building2,
  CalendarDays,
  CreditCard,
  Sparkles,
  Armchair,
  Package,
  QrCode,
  FileSpreadsheet,
  Rocket,
  Globe2,
  ShieldCheck,
} from 'lucide-react'
import { LandingStats, LandingReviews } from '@/components/marketing/LandingLive'
import { HeroMockup } from '@/components/marketing/HeroMockup'
import { Reveal, TiltCard, Spotlight } from '@/components/marketing/fx'

const MARQUEE = [
  'Facility Booking', 'Smart Approvals', 'GST Invoicing', 'Seat Leasing',
  'Startup Ecosystem', 'AI Assistant', 'QR Check-in', 'Inventory + Excel',
  'Vendor Bills', 'Visitor Passes', 'Real-time Chat', 'Analytics',
]

const BENTO = [
  {
    icon: CalendarDays,
    title: 'Bookings that run themselves',
    description:
      'Public visitors book without an account. Employees book in two clicks. Approvals route to exactly the right admin, slots lock on payment, and everyone gets emailed — automatically.',
    span: 'lg:col-span-2',
    accent: 'from-primary/20',
  },
  {
    icon: Sparkles,
    title: 'An AI that knows your building',
    description:
      '“How many seats are free?” “Monthly revenue?” Ask in plain language — the assistant reads your live data and answers per role.',
    span: '',
    accent: 'from-violet-500/20',
  },
  {
    icon: Armchair,
    title: 'Lease the seats you don’t use',
    description:
      'Tenant companies post spare desks, startups apply, admins approve. The building owner just watches the occupancy climb.',
    span: '',
    accent: 'from-amber-500/20',
  },
  {
    icon: CreditCard,
    title: 'Billing on autopilot',
    description:
      'GST invoices, Razorpay payments, vendor bills, and expense tracking — exportable to Excel, Word, or PDF in one click.',
    span: '',
    accent: 'from-green-500/20',
  },
  {
    icon: QrCode,
    title: 'QR check-in at the door',
    description:
      'Every confirmed booking carries a QR code. Scan, check in, done — attendance tracked without a front desk.',
    span: '',
    accent: 'from-sky-500/20',
  },
  {
    icon: Package,
    title: 'Inventory you can edit in Excel',
    description:
      'Pantry, water, appliances — export the sheet, edit it in real Microsoft Excel, upload it back. The database updates itself.',
    span: 'lg:col-span-2',
    accent: 'from-rose-500/20',
  },
]

const STEPS = [
  {
    n: '01',
    icon: Building2,
    title: 'Model your building',
    text: 'Buildings → floors → facilities → desks, with pricing and public visibility per facility.',
  },
  {
    n: '02',
    icon: FileSpreadsheet,
    title: 'Lease to companies',
    text: 'Assign floors and seat counts to tenant companies. Their admins run their own teams.',
  },
  {
    n: '03',
    icon: Rocket,
    title: 'Open to the world',
    text: 'Public booking, startup seat listings, community events — your space starts selling itself.',
  },
]

export default function MarketingHomePage() {
  return (
    <>
      {/* ── HERO ─────────────────────────────────────────── */}
      <section className="relative overflow-hidden">
        {/* Aurora blobs */}
        <div aria-hidden className="pointer-events-none absolute inset-0 -z-20 overflow-hidden">
          <div className="fx-aurora-1 absolute -top-40 -left-32 h-[34rem] w-[34rem] rounded-full bg-primary/25 blur-3xl" />
          <div className="fx-aurora-2 absolute -top-24 right-0 h-[28rem] w-[28rem] rounded-full bg-violet-500/20 blur-3xl" />
          <div className="fx-aurora-3 absolute top-64 left-1/3 h-[24rem] w-[24rem] rounded-full bg-sky-400/15 blur-3xl" />
        </div>
        {/* Dotted grid + cursor spotlight */}
        <div aria-hidden className="fx-grid pointer-events-none absolute inset-0 -z-10" />
        <Spotlight />

        <div className="max-w-6xl mx-auto px-4 pt-20 sm:pt-28 pb-10 text-center">
          <Reveal>
            <div className="inline-flex items-center gap-2 rounded-full border border-primary/30 bg-primary/5 px-4 py-1.5 text-xs font-semibold text-primary mb-8">
              <span className="relative flex h-2 w-2">
                <span className="fx-ping absolute inline-flex h-full w-full rounded-full bg-primary" />
                <span className="relative inline-flex h-2 w-2 rounded-full bg-primary" />
              </span>
              Building OS · Bookings · Billing · AI — in one platform
            </div>
          </Reveal>

          <Reveal delay={120}>
            <h1 className="text-5xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight leading-[1.05]">
              Your building,
              <br />
              <span className="bg-gradient-to-r from-primary via-violet-500 to-sky-400 fx-shimmer-text">
                running on autopilot.
              </span>
            </h1>
          </Reveal>

          <Reveal delay={240}>
            <p className="mt-7 max-w-2xl mx-auto text-lg sm:text-xl text-muted-foreground">
              CoWorkHub turns a building into a self-service business — bookings, leases,
              invoices, startups, and an AI that answers before you ask.
            </p>
          </Reveal>

          <Reveal delay={360}>
            <div className="mt-10 flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                href="/book"
                className="group inline-flex items-center justify-center gap-2 rounded-xl px-8 py-3.5 text-sm font-bold bg-primary text-primary-foreground hover:bg-primary/90 transition-all shadow-xl shadow-primary/30 hover:shadow-primary/50 hover:-translate-y-0.5"
              >
                Book a Space — no account needed
                <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
              </Link>
              <Link
                href="/login"
                className="inline-flex items-center justify-center gap-2 rounded-xl border border-border px-8 py-3.5 text-sm font-bold text-foreground hover:bg-accent transition-colors fx-glass"
              >
                Operator Sign In
              </Link>
            </div>
          </Reveal>

          {/* The floating dashboard */}
          <Reveal delay={480}>
            <HeroMockup />
          </Reveal>
        </div>
      </section>

      {/* ── MODULE MARQUEE ──────────────────────────────── */}
      <section className="relative border-y border-border/60 bg-muted/30 py-5 overflow-hidden">
        <div aria-hidden className="pointer-events-none absolute inset-y-0 left-0 w-24 z-10 bg-gradient-to-r from-background to-transparent" />
        <div aria-hidden className="pointer-events-none absolute inset-y-0 right-0 w-24 z-10 bg-gradient-to-l from-background to-transparent" />
        <div className="fx-marquee flex w-max gap-10">
          {[...MARQUEE, ...MARQUEE].map((m, i) => (
            <span key={i} className="flex items-center gap-2 text-sm font-semibold text-muted-foreground whitespace-nowrap">
              <span className="h-1.5 w-1.5 rounded-full bg-primary" />
              {m}
            </span>
          ))}
        </div>
      </section>

      {/* ── LIVE STATS ──────────────────────────────────── */}
      <LandingStats />

      {/* ── BENTO FEATURES ──────────────────────────────── */}
      <section className="py-20">
        <div className="max-w-6xl mx-auto px-4">
          <Reveal className="text-center mb-14">
            <h2 className="text-3xl sm:text-4xl font-bold tracking-tight">
              Everything a space needs.{' '}
              <span className="bg-gradient-to-r from-primary to-violet-500 bg-clip-text text-transparent">
                Nothing it doesn’t.
              </span>
            </h2>
            <p className="mt-3 text-muted-foreground max-w-xl mx-auto">
              Twenty-two modules, one login. Replace the spreadsheets, the WhatsApp groups, and the register at the door.
            </p>
          </Reveal>

          <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
            {BENTO.map(({ icon: Icon, title, description, span, accent }, i) => (
              <Reveal key={title} delay={i * 80} className={span}>
                <TiltCard className={`group relative h-full overflow-hidden rounded-2xl border bg-card p-6 shadow-sm hover:shadow-xl hover:shadow-primary/10 transition-shadow`}>
                  <div aria-hidden className={`absolute -top-16 -right-16 h-40 w-40 rounded-full bg-gradient-to-br ${accent} to-transparent blur-2xl transition-opacity opacity-60 group-hover:opacity-100`} />
                  <div className="relative">
                    <div className="mb-4 inline-flex h-11 w-11 items-center justify-center rounded-xl bg-primary/10 text-primary ring-1 ring-primary/20">
                      <Icon className="h-5 w-5" />
                    </div>
                    <h3 className="text-base font-bold">{title}</h3>
                    <p className="mt-2 text-sm text-muted-foreground leading-relaxed">{description}</p>
                  </div>
                </TiltCard>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* ── HOW IT WORKS ────────────────────────────────── */}
      <section className="relative py-20 bg-muted/30 border-y border-border/60 overflow-hidden">
        <div aria-hidden className="fx-grid pointer-events-none absolute inset-0 opacity-50" />
        <div className="max-w-5xl mx-auto px-4 relative">
          <Reveal className="text-center mb-14">
            <h2 className="text-3xl sm:text-4xl font-bold tracking-tight">Live in an afternoon</h2>
            <p className="mt-3 text-muted-foreground">Three steps from empty floors to a running business.</p>
          </Reveal>
          <div className="grid gap-10 sm:grid-cols-3 relative">
            <div aria-hidden className="hidden sm:block absolute top-7 left-[16%] right-[16%] h-px bg-gradient-to-r from-transparent via-primary/50 to-transparent" />
            {STEPS.map(({ n, icon: Icon, title, text }, i) => (
              <Reveal key={n} delay={i * 140} className="relative text-center">
                <div className="relative z-10 mx-auto mb-5 flex h-14 w-14 items-center justify-center rounded-2xl bg-background shadow-lg ring-1 ring-primary/30">
                  <Icon className="h-6 w-6 text-primary" />
                  <span className="absolute -top-2 -right-2 rounded-full bg-primary px-1.5 py-0.5 text-[9px] font-black text-primary-foreground">{n}</span>
                </div>
                <h3 className="font-bold">{title}</h3>
                <p className="mt-2 text-sm text-muted-foreground leading-relaxed max-w-xs mx-auto">{text}</p>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* ── REAL REVIEWS ────────────────────────────────── */}
      <LandingReviews />

      {/* ── FINAL CTA ───────────────────────────────────── */}
      <section className="py-24 px-4">
        <Reveal>
          <div className="relative max-w-4xl mx-auto overflow-hidden rounded-3xl bg-gradient-to-br from-primary via-violet-600 to-primary p-[1px] shadow-2xl shadow-primary/30">
            <div className="relative rounded-3xl bg-background/95 px-6 py-16 text-center overflow-hidden">
              <div aria-hidden className="fx-orbit pointer-events-none absolute -top-1/2 left-1/2 h-[120%] w-[120%] -translate-x-1/2 rounded-full border border-primary/20" />
              <div aria-hidden className="fx-orbit pointer-events-none absolute -top-1/4 left-1/2 h-[80%] w-[80%] -translate-x-1/2 rounded-full border border-violet-500/20" style={{ animationDirection: 'reverse' }} />
              <ShieldCheck className="mx-auto mb-5 h-10 w-10 text-primary" />
              <h2 className="text-3xl sm:text-5xl font-extrabold tracking-tight">
                Ready to put your building
                <br />
                <span className="bg-gradient-to-r from-primary to-violet-500 bg-clip-text text-transparent">on autopilot?</span>
              </h2>
              <p className="mt-5 text-muted-foreground max-w-md mx-auto">
                Set up your space, share the booking link, and watch the dashboard light up.
              </p>
              <div className="mt-9 flex flex-col sm:flex-row gap-4 justify-center">
                <Link
                  href="/book"
                  className="inline-flex items-center justify-center gap-2 rounded-xl px-8 py-3.5 text-sm font-bold bg-primary text-primary-foreground hover:bg-primary/90 transition-all shadow-lg shadow-primary/30 hover:-translate-y-0.5"
                >
                  <Globe2 className="h-4 w-4" />
                  Book a Space
                </Link>
                <Link
                  href="/login"
                  className="inline-flex items-center justify-center gap-2 rounded-xl border px-8 py-3.5 text-sm font-bold hover:bg-accent transition-colors"
                >
                  Operator Sign In
                  <ArrowRight className="h-4 w-4" />
                </Link>
              </div>
            </div>
          </div>
        </Reveal>
      </section>
    </>
  )
}
