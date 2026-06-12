'use client'

/**
 * A floating, 3D-tilted "dashboard" built purely from CSS — no images.
 * Animated chart bars, live-pulse dot, and floating glass badges.
 */
import { CalendarCheck, IndianRupee, Sparkles } from 'lucide-react'

const BARS = [42, 68, 38, 80, 56, 92, 64, 74, 48, 88, 60, 96]

export function HeroMockup() {
  return (
    <div className="relative mx-auto mt-16 max-w-4xl px-2" style={{ perspective: '1200px' }}>
      {/* Glow under the panel */}
      <div aria-hidden className="absolute inset-x-8 -bottom-8 h-24 rounded-full bg-primary/30 blur-3xl" />

      <div className="fx-float relative rounded-2xl fx-glass shadow-2xl shadow-primary/20 overflow-hidden">
        {/* Window chrome */}
        <div className="flex items-center gap-1.5 border-b border-border/60 px-4 py-2.5">
          <span className="h-2.5 w-2.5 rounded-full bg-red-400/80" />
          <span className="h-2.5 w-2.5 rounded-full bg-amber-400/80" />
          <span className="h-2.5 w-2.5 rounded-full bg-green-400/80" />
          <span className="ml-3 text-[10px] font-medium text-muted-foreground tracking-wide">
            coworkhub — operator dashboard
          </span>
          <span className="ml-auto flex items-center gap-1.5 text-[10px] font-semibold text-green-500">
            <span className="relative flex h-2 w-2">
              <span className="fx-ping absolute inline-flex h-full w-full rounded-full bg-green-400" />
              <span className="relative inline-flex h-2 w-2 rounded-full bg-green-500" />
            </span>
            LIVE
          </span>
        </div>

        <div className="grid grid-cols-[88px_1fr] sm:grid-cols-[140px_1fr]">
          {/* Mini sidebar */}
          <div className="border-r border-border/60 p-3 space-y-2">
            {['Dashboard', 'Bookings', 'Leases', 'Billing', 'Inventory', 'AI'].map((item, i) => (
              <div
                key={item}
                className={`rounded-md px-2 py-1.5 text-[10px] sm:text-[11px] font-medium ${
                  i === 0 ? 'bg-primary text-primary-foreground' : 'text-muted-foreground'
                }`}
              >
                {item}
              </div>
            ))}
          </div>

          {/* Main panel */}
          <div className="p-3 sm:p-5 space-y-3 sm:space-y-4">
            {/* KPI row */}
            <div className="grid grid-cols-3 gap-2 sm:gap-3">
              {[
                { label: 'Occupancy', value: '94%', accent: 'text-primary' },
                { label: 'Revenue (mo)', value: '₹8.4L', accent: 'text-green-500' },
                { label: 'Bookings', value: '312', accent: 'text-amber-500' },
              ].map((kpi) => (
                <div key={kpi.label} className="rounded-lg border border-border/60 bg-background/60 p-2 sm:p-3">
                  <div className="text-[9px] sm:text-[10px] text-muted-foreground">{kpi.label}</div>
                  <div className={`text-sm sm:text-lg font-bold ${kpi.accent}`}>{kpi.value}</div>
                </div>
              ))}
            </div>

            {/* Animated chart */}
            <div className="rounded-lg border border-border/60 bg-background/60 p-3">
              <div className="mb-2 flex items-center justify-between">
                <span className="text-[10px] font-medium text-muted-foreground">Facility utilisation</span>
                <span className="text-[10px] font-semibold text-primary">▲ 23% this month</span>
              </div>
              <div className="flex h-16 sm:h-24 items-end gap-1 sm:gap-1.5">
                {BARS.map((h, i) => (
                  <div
                    key={i}
                    className="fx-bar flex-1 rounded-sm bg-gradient-to-t from-primary/40 to-primary"
                    style={{ height: `${h}%`, animationDelay: `${i * 70}ms` }}
                  />
                ))}
              </div>
            </div>

            {/* Activity rows */}
            <div className="space-y-1.5 hidden sm:block">
              {[
                'Conference Room A booked — 14:00–16:00',
                'Invoice INV-2026-0612 paid · ₹5,900',
                'Startup “Nimbus Labs” assigned 6 seats',
              ].map((row) => (
                <div key={row} className="flex items-center gap-2 rounded-md border border-border/50 bg-background/50 px-2.5 py-1.5">
                  <span className="h-1.5 w-1.5 rounded-full bg-primary" />
                  <span className="text-[10px] text-muted-foreground">{row}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Floating badges */}
      <div className="fx-glass absolute -left-2 top-10 hidden md:flex items-center gap-2 rounded-xl px-3 py-2 shadow-lg fx-float" style={{ animationDelay: '1.2s' }}>
        <CalendarCheck className="h-4 w-4 text-green-500" />
        <div>
          <div className="text-[10px] font-semibold">Booking confirmed</div>
          <div className="text-[9px] text-muted-foreground">slot locked automatically</div>
        </div>
      </div>
      <div className="fx-glass absolute -right-2 top-24 hidden md:flex items-center gap-2 rounded-xl px-3 py-2 shadow-lg fx-float" style={{ animationDelay: '2.1s' }}>
        <IndianRupee className="h-4 w-4 text-primary" />
        <div>
          <div className="text-[10px] font-semibold">Invoice paid</div>
          <div className="text-[9px] text-muted-foreground">GST PDF emailed</div>
        </div>
      </div>
      <div className="fx-glass absolute -bottom-4 left-1/2 hidden md:flex -translate-x-1/2 items-center gap-2 rounded-xl px-3 py-2 shadow-lg fx-float" style={{ animationDelay: '0.6s' }}>
        <Sparkles className="h-4 w-4 text-amber-500" />
        <div className="text-[10px] font-semibold">AI: “Occupancy will peak Thursday — open 12 hot desks.”</div>
      </div>
    </div>
  )
}
