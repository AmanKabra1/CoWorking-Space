'use client'

import { useState, useCallback } from 'react'

interface Toast {
  id: string
  title?: string
  description?: string
  variant?: 'default' | 'destructive'
}

let toastListeners: ((toasts: Toast[]) => void)[] = []
let currentToasts: Toast[] = []

function notifyListeners() {
  toastListeners.forEach((fn) => fn([...currentToasts]))
}

export function toast({ title, description, variant = 'default' }: Omit<Toast, 'id'>) {
  const id = Math.random().toString(36).slice(2)
  currentToasts = [...currentToasts, { id, title, description, variant }]
  notifyListeners()
  setTimeout(() => {
    currentToasts = currentToasts.filter((t) => t.id !== id)
    notifyListeners()
  }, 4000)
}

export function useToast() {
  const [toasts, setToasts] = useState<Toast[]>(currentToasts)

  const subscribe = useCallback(() => {
    const listener = (t: Toast[]) => setToasts(t)
    toastListeners.push(listener)
    return () => {
      toastListeners = toastListeners.filter((l) => l !== listener)
    }
  }, [])

  useState(() => {
    const unsub = subscribe()
    return unsub
  })

  return { toasts }
}
