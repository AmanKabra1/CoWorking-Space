import { Building2, Users, BarChart3, CheckCircle } from 'lucide-react'

const values = [
  {
    icon: Building2,
    title: 'Built for operators',
    description:
      'Every feature is designed around the day-to-day reality of running a coworking space — not generic project management.',
  },
  {
    icon: Users,
    title: 'Member-first experience',
    description:
      'We obsess over the member experience so your community stays engaged, books easily, and pays on time.',
  },
  {
    icon: BarChart3,
    title: 'Data you can act on',
    description:
      'Real-time occupancy, revenue, and engagement analytics so you can make confident decisions about your space.',
  },
]

const highlights = [
  'Launched in 2023, serving spaces across India and Southeast Asia',
  'Processing thousands of bookings and invoices every month',
  'SOC 2 Type II audit in progress; data hosted on AWS Mumbai',
  'Dedicated customer success team with onboarding support',
  'Open roadmap — customers vote on features',
]

export default function AboutPage() {
  return (
    <div className="py-20">
      <div className="max-w-4xl mx-auto px-4">
        {/* Mission */}
        <div className="text-center mb-16">
          <h1 className="text-4xl font-extrabold tracking-tight text-foreground sm:text-5xl">
            Our mission
          </h1>
          <p className="mt-6 text-lg text-muted-foreground leading-relaxed max-w-2xl mx-auto">
            Coworking spaces are where ideas are born and companies are built. CoWorkHub exists to
            remove the operational friction so operators can focus entirely on their communities —
            not on spreadsheets, chasing payments, or juggling disconnected tools.
          </p>
        </div>

        {/* Built for coworking operators */}
        <section className="mb-20">
          <h2 className="text-2xl font-bold text-foreground mb-8 text-center">
            Built for coworking operators
          </h2>
          <div className="grid gap-8 sm:grid-cols-3">
            {values.map(({ icon: Icon, title, description }) => (
              <div
                key={title}
                className="rounded-xl border bg-card p-7 shadow-sm text-center"
              >
                <div className="inline-flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10 mb-4">
                  <Icon className="h-6 w-6 text-primary" />
                </div>
                <h3 className="font-semibold text-foreground mb-2">{title}</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">{description}</p>
              </div>
            ))}
          </div>
        </section>

        {/* Highlights */}
        <section className="rounded-xl border bg-muted/40 p-8">
          <h2 className="text-xl font-bold text-foreground mb-6">CoWorkHub at a glance</h2>
          <ul className="space-y-3">
            {highlights.map((item) => (
              <li key={item} className="flex items-start gap-3 text-sm text-foreground">
                <CheckCircle className="h-4 w-4 text-primary shrink-0 mt-0.5" />
                {item}
              </li>
            ))}
          </ul>
        </section>

        {/* Closing */}
        <div className="mt-16 text-center">
          <p className="text-muted-foreground leading-relaxed max-w-2xl mx-auto">
            We are a small, focused team with deep roots in the coworking industry. Every line of
            CoWorkHub was written with a real operator's workflow in mind. If you have feedback,
            ideas, or just want to talk shop, we would love to hear from you.
          </p>
        </div>
      </div>
    </div>
  )
}
