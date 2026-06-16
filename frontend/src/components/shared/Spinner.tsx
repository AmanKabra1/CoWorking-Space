import { Loader2 } from 'lucide-react'
import { cn } from '@/lib/utils'

/** Small inline spinner — use inside buttons or beside short loading text. */
export function Spinner({ className }: { className?: string }) {
  return <Loader2 className={cn('h-4 w-4 animate-spin', className)} />
}

/** Centred page/section loader with an optional label. */
export function PageLoader({ label = 'Loading…' }: { label?: string }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-16 text-muted-foreground">
      <Loader2 className="h-7 w-7 animate-spin" />
      <span className="text-sm">{label}</span>
    </div>
  )
}
