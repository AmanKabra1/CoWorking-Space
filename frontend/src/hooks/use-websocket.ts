'use client'

import { useEffect, useRef, useCallback, useState } from 'react'
import { useAuthStore } from '@/store/auth'

interface UseWebSocketOptions {
  onMessage?: (data: unknown) => void
  onOpen?: () => void
  onClose?: () => void
}

// WebSocket base resolution:
//  - explicit NEXT_PUBLIC_WS_URL  → use it (any environment)
//  - unset in development         → localhost (dev convenience)
//  - unset in production          → '' = disabled (e.g. Hugging Face Spaces
//    don't support Channels/WS, so don't even attempt — avoids console errors)
const WS_BASE =
  process.env.NEXT_PUBLIC_WS_URL ??
  (process.env.NODE_ENV === 'production' ? '' : 'ws://localhost:8000')
const WS_DISABLED = WS_BASE === ''

export function useWebSocket(path: string, options: UseWebSocketOptions = {}) {
  const { accessToken } = useAuthStore()
  const wsRef = useRef<WebSocket | null>(null)
  const [connected, setConnected] = useState(false)

  const connect = useCallback(() => {
    if (WS_DISABLED || !accessToken || !path) return
    const url = `${WS_BASE}${path}?token=${accessToken}`
    const ws = new WebSocket(url)
    wsRef.current = ws

    ws.onopen = () => {
      setConnected(true)
      options.onOpen?.()
    }
    ws.onmessage = (event) => {
      try {
        options.onMessage?.(JSON.parse(event.data))
      } catch {}
    }
    ws.onclose = () => {
      setConnected(false)
      options.onClose?.()
      wsRef.current = null
    }
    ws.onerror = () => ws.close()
  }, [accessToken, path]) // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    connect()
    return () => {
      wsRef.current?.close()
    }
  }, [connect])

  const send = useCallback((data: unknown) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(data))
    }
  }, [])

  return { connected, send, disabled: WS_DISABLED }
}
