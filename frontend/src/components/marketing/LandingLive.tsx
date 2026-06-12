'use client'

import { useQuery } from '@tanstack/react-query'
import { publicService } from '@/lib/services'

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
    <section className="py-14 bg-primary">
      <div className="max-w-6xl mx-auto px-4">
        <div className="grid grid-cols-2 gap-8 sm:grid-cols-4">
          {items.map(({ value, label }) => (
            <div key={label} className="text-center">
              <div className="text-4xl font-extrabold text-white">{value.toLocaleString()}+</div>
              <div className="mt-1 text-sm font-medium text-primary-foreground/70">{label}</div>
            </div>
          ))}
        </div>
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
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold tracking-tight text-foreground">What our members say</h2>
          <p className="mt-3 text-muted-foreground">Real reviews from completed bookings.</p>
        </div>
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {reviews.map((r, i) => (
            <div key={i} className="rounded-xl border bg-card p-6 shadow-sm flex flex-col gap-3">
              <div className="text-amber-400 text-sm tracking-wide" aria-label={`${r.rating} out of 5 stars`}>
                {'★'.repeat(r.rating)}
                <span className="text-muted-foreground/30">{'★'.repeat(5 - r.rating)}</span>
              </div>
              <p className="text-sm text-muted-foreground leading-relaxed flex-1">&ldquo;{r.comment}&rdquo;</p>
              <div>
                <div className="font-semibold text-foreground text-sm">{r.reviewer_name}</div>
                <div className="text-xs text-muted-foreground">
                  {r.company_name ? `${r.company_name} · ` : ''}{r.facility_name}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
