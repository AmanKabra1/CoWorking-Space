'use client'

import { useState, useEffect, useRef, useCallback } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Send } from 'lucide-react'
import { PageHeader } from '@/components/shared/PageHeader'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { useWebSocket } from '@/hooks/use-websocket'
import { useAuthStore } from '@/store/auth'
import { chatService } from '@/lib/services'
import { formatTime } from '@/lib/utils'
import { cn } from '@/lib/utils'

interface Message {
  id: string
  content: string
  sender_id: string | null
  sender_name: string
  created_at: string
}

export default function ChatPage() {
  const { user } = useAuthStore()
  const [roomId, setRoomId] = useState<string | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const bottomRef = useRef<HTMLDivElement>(null)

  const { data: room } = useQuery({
    queryKey: ['chat-room'],
    queryFn: chatService.getGeneralRoom,
    staleTime: Infinity,
  })

  useEffect(() => {
    if (room?.id) setRoomId(room.id)
  }, [room])

  const handleMessage = useCallback((data: unknown) => {
    const payload = data as { type: string; messages?: Message[]; message?: Message }
    if (payload.type === 'history' && payload.messages) {
      setMessages(payload.messages)
    } else if (payload.type === 'message' && payload.message) {
      setMessages((prev) => [...prev, payload.message!])
    }
  }, [])

  const { connected, send } = useWebSocket(
    roomId ? `/ws/chat/${roomId}/` : '',
    { onMessage: handleMessage }
  )

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  function handleSend() {
    const content = input.trim()
    if (!content || !connected) return
    send({ content })
    setInput('')
  }

  return (
    <div className="space-y-4 h-full flex flex-col">
      <PageHeader
        title="Company Chat"
        description={connected ? '● Live' : '○ Connecting...'}
      />

      <Card className="flex-1 flex flex-col min-h-0">
        <CardHeader className="pb-2 border-b">
          <CardTitle className="text-sm font-medium text-muted-foreground">
            {room?.name ?? 'General'}
          </CardTitle>
        </CardHeader>

        <CardContent className="flex-1 overflow-y-auto p-4 space-y-3 min-h-0">
          {messages.length === 0 && (
            <p className="text-sm text-center text-muted-foreground py-8">
              No messages yet. Say hello!
            </p>
          )}
          {messages.map((msg) => {
            const isMe = msg.sender_id === user?.id
            return (
              <div key={msg.id} className={cn('flex gap-2', isMe && 'flex-row-reverse')}>
                <div
                  className={cn(
                    'max-w-xs lg:max-w-md rounded-2xl px-3 py-2 text-sm',
                    isMe
                      ? 'bg-primary text-primary-foreground rounded-tr-sm'
                      : 'bg-muted rounded-tl-sm'
                  )}
                >
                  {!isMe && (
                    <p className="text-xs font-medium opacity-70 mb-0.5">{msg.sender_name}</p>
                  )}
                  <p>{msg.content}</p>
                  <p className={cn('text-xs mt-0.5 opacity-60', isMe ? 'text-right' : '')}>
                    {formatTime(msg.created_at)}
                  </p>
                </div>
              </div>
            )
          })}
          <div ref={bottomRef} />
        </CardContent>

        <div className="p-4 border-t flex gap-2">
          <Input
            placeholder="Type a message…"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            disabled={!connected}
          />
          <Button onClick={handleSend} disabled={!connected || !input.trim()} size="icon">
            <Send className="h-4 w-4" />
          </Button>
        </div>
      </Card>
    </div>
  )
}
