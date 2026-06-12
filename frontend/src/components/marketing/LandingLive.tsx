'use client'

import { useQuery } from '@tanstack/react-query'
import { publicService } from '@/lib/services'
import { CountUp, Reveal, TiltCard } from '@/components/marketing/fx'

/**
 * Live platform numbers + real customer reviews for the landing page.
 * Everything here comes from the database — no invented stats.
 */
export function LandingStats() {
  const { data } = useQuery({ queryKey: ['public-stats'], queryFn: () => publicService.stats() })

  if (!data) return null
  const items = [
    { value: data.companies, label: 'Companies' },
    { value: data.buildings, label: 'Buildings' },
    { value: data.facilities, label: 'Facilities' },
    { value: data.bookings, label: 'Bookings served' },
  ].filter((i) => i.value > 0)

  if (items.length === 0) return null
  return (
    <section className="relative py-16">
      <div className="max-w-5xl mx-auto px-4">
        <Reveal>
          <div className="fx-glass rounded-2xl px-6 py-10 shadow-xl shadow-primary/10">
            <div className="grid grid-cols-2 gap-8 sm:grid-cols-4">
              {items.map(({ value, label }, i) => (
                <div key={label} className="text-center">
                  <div className="bg-gradient-to-r from-primary via-violet-500 to-primary fx-shimmer-text text-4xl sm:text-5xl font-extrabold tabular-nums">
                    <CountUp value={value} duration={1200 + i * 250} />+
                  </div>
                  <div className="mt-2 text-xs sm:text-sm font-medium uppercase tracking-wider text-muted-foreground">
                    {label}
                  </div>
                </div>
              ))}
            </div>
            <p className="mt-6 text-center text-[11px] text-muted-foreground/70">
              Live numbers, straight from the platform — updated in real time.
            </p>
          </div>
        </Reveal>
      </div>
    </section>
  )
}

export function LandingReviews() {
  const { data: reviews = [] } = useQuery({ queryKey: ['public-reviews'], queryFn: () => publicService.reviews() })

  if (reviews.length === 0) return null
  return (
    <section className="py-20">
      <div className="max-w-6xl mx-auto px-4">
        <Reveal className="text-center mb-12">
          <h2 className="text-3xl sm:text-4xl font-bold tracking-tight text-foreground">What our members say</h2>
          <p className="mt-3 text-muted-foreground">Real reviews from completed bookings — not marketing copy.</p>
        </Reveal>
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {reviews.map((r, i) => (
            <Reveal key={i} delay={i * 90}>
              <TiltCard className="fx-glass h-full rounded-2xl p-6 shadow-lg flex flex-col gap-3">
                <div className="text-amber-400 text-sm tracking-widest" aria-label={`${r.rating} out of 5 stars`}>
                  {'★'.repeat(r.rating)}
                  <span className="text-muted-foreground/30">{'★'.repeat(5 - r.rating)}</span>
                </div>
                <p className="text-sm text-muted-foreground leading-relaxed flex-1">&ldquo;{r.comment}&rdquo;</p>
                <div className="flex items-center gap-3 pt-1">
                  <div className="flex h-9 w-9 items-center justify-center rounded-full bg-gradient-to-br from-primary to-violet-500 text-xs font-bold text-white">
                    {r.reviewer_name.slice(0, 1).toUpperCase()}
                  </div>
                  <div>
                    <div className="font-semibold text-foreground text-sm">{r.reviewer_name}</div>
                    <div className="text-xs text-muted-foreground">
                      {r.company_name ? `${r.company_name} · ` : ''}{r.facility_name}
                    </div>
                  </div>
                </div>
              </TiltCard>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  )
}
