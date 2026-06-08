'use client'

import { useToast } from '@/hooks/use-toast'

export function Toaster() {
  const { toasts } = useToast()

  return (
    <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2 max-w-sm w-full">
      {toasts.map((toast) => (
        <div
          key={toast.id}
          className={`rounded-lg border p-4 shadow-lg text-sm transition-all ${
            toast.variant === 'destructive'
              ? 'bg-destructive text-destructive-foreground border-destructive'
              : 'bg-card text-card-foreground border-border'
          }`}
        >
          {toast.title && <div className="font-semibold mb-0.5">{toast.title}</div>}
          {toast.description && <div className="text-xs opacity-80">{toast.description}</div>}
        </div>
      ))}
    </div>
  )
}
