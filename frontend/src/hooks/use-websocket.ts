'use client'

import { useEffect, useRef, useCallback, useState } from 'react'
import { useAuthStore } from '@/store/auth'

interface UseWebSocketOptions {
  onMessage?: (data: unknown) => void
  onOpen?: () => void
  onClose?: () => void
}

export function useWebSocket(path: string, options: UseWebSocketOptions = {}) {
  const { accessToken } = useAuthStore()
  const wsRef = useRef<WebSocket | null>(null)
  const [connected, setConnected] = useState(false)

  const connect = useCallback(() => {
    if (!accessToken || !path) return
    const base = process.env.NEXT_PUBLIC_WS_URL ?? 'ws://localhost:8000'
    const url = `${base}${path}?token=${accessToken}`
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

  return { connected, send }
}
