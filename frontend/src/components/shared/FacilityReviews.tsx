'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { facilityService } from '@/lib/services'

function Stars({ rating }: { rating: number }) {
  return (
    <span className="text-amber-400 tracking-tight" aria-label={`${rating} of 5 stars`}>
      {'★'.repeat(rating)}
      <span className="text-muted-foreground/30">{'★'.repeat(5 - rating)}</span>
    </span>
  )
}

export function FacilityReviews({
  facilityId,
  avgRating,
  reviewCount,
}: {
  facilityId: string
  avgRating?: number | null
  reviewCount?: number
}) {
  const [open, setOpen] = useState(false)
  const { data: reviews = [], isLoading } = useQuery({
    queryKey: ['facility-reviews', facilityId],
    queryFn: () => facilityService.reviews(facilityId),
    enabled: open,
  })

  if (!reviewCount) {
    return <div className="pt-1 text-xs text-muted-foreground">No reviews yet</div>
  }

  return (
    <div className="pt-1">
      <button
        onClick={() => setOpen((v) => !v)}
        className="flex items-center gap-1.5 text-xs font-medium text-foreground hover:text-primary transition-colors"
      >
        <span className="text-amber-400">★</span>
        {avgRating?.toFixed(1)}
        <span className="text-muted-foreground">({reviewCount} review{reviewCount > 1 ? 's' : ''})</span>
        <span className="text-muted-foreground">{open ? '▲' : '▼'}</span>
      </button>

      {open && (
        <div className="mt-2 space-y-2 max-h-48 overflow-y-auto pr-1">
          {isLoading && <div className="text-xs text-muted-foreground">Loading…</div>}
          {reviews.map((r, i) => (
            <div key={i} className="rounded-md border bg-background/60 p-2">
              <div className="flex items-center justify-between text-xs">
                <Stars rating={r.rating} />
                <span className="text-muted-foreground">{r.created_at}</span>
              </div>
              {r.comment && <p className="mt-1 text-xs text-muted-foreground leading-relaxed">{r.comment}</p>}
              <div className="mt-1 text-[11px] font-medium text-foreground">
                {r.reviewer_name}{r.company_name ? ` · ${r.company_name}` : ''}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
