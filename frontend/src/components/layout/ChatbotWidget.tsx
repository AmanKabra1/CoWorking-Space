'use client'

import { useState, useRef, useEffect } from 'react'
import { useMutation } from '@tanstack/react-query'
import { MessageCircle, X, Send, Sparkles } from 'lucide-react'
import { aiService } from '@/lib/services'
import { cn } from '@/lib/utils'

type Msg = { role: 'user' | 'assistant'; text: string }

export function ChatbotWidget() {
  const [open, setOpen] = useState(false)
  const [messages, setMessages] = useState<Msg[]>([])
  const [input, setInput] = useState('')
  const [sessionId, setSessionId] = useState<string | undefined>()
  const endRef = useRef<HTMLDivElement>(null)

  useEffect(() => { endRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages, open])

  const chat = useMutation({
    mutationFn: (text: string) => aiService.chat(text, sessionId),
    onSuccess: (res) => { setSessionId(res.session_id); setMessages(m => [...m, { role: 'assistant', text: res.reply }]) },
    onError: () => setMessages(m => [...m, { role: 'assistant', text: 'AI is unavailable right now.' }]),
  })

  function send(e: React.FormEvent) {
    e.preventDefault()
    const t = input.trim()
    if (!t || chat.isPending) return
    setMessages(m => [...m, { role: 'user', text: t }])
    setInput('')
    chat.mutate(t)
  }

  return (
    <>
      {/* Launcher */}
      <button
        onClick={() => setOpen(v => !v)}
        className="fixed bottom-5 right-5 z-50 h-14 w-14 rounded-full bg-primary text-primary-foreground shadow-lg flex items-center justify-center hover:bg-primary/90 transition-colors"
        aria-label={open ? 'Close assistant' : 'Open assistant'}
      >
        {open ? <X className="h-6 w-6" /> : <MessageCircle className="h-6 w-6" />}
      </button>

      {/* Panel */}
      <div
        className={cn(
          'fixed bottom-24 right-5 z-50 w-[92vw] max-w-sm h-[28rem] rounded-xl border bg-background shadow-2xl flex flex-col overflow-hidden transition-all',
          open ? 'opacity-100 translate-y-0 pointer-events-auto' : 'opacity-0 translate-y-3 pointer-events-none',
        )}
      >
        <div className="flex items-center gap-2 px-4 py-3 border-b bg-primary text-primary-foreground">
          <Sparkles className="h-4 w-4" />
          <span className="text-sm font-semibold">CoWorkHub Assistant</span>
        </div>

        <div className="flex-1 overflow-y-auto p-3 space-y-2">
          {messages.length === 0 && (
            <p className="text-sm text-muted-foreground text-center mt-8">
              Ask me about bookings, seats, invoices, occupancy…
            </p>
          )}
          {messages.map((m, i) => (
            <div key={i} className={cn('flex', m.role === 'user' ? 'justify-end' : 'justify-start')}>
              <div className={cn('max-w-[85%] rounded-lg px-3 py-2 text-sm whitespace-pre-wrap',
                m.role === 'user' ? 'bg-primary text-primary-foreground' : 'bg-muted')}>
                {m.text}
              </div>
            </div>
          ))}
          {chat.isPending && <div className="text-xs text-muted-foreground">Thinking…</div>}
          <div ref={endRef} />
        </div>

        <form onSubmit={send} className="border-t p-2 flex gap-2">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type a message…"
            disabled={chat.isPending}
            className="flex-1 rounded-md border px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
          />
          <button type="submit" disabled={chat.isPending || !input.trim()}
            className="rounded-md bg-primary text-primary-foreground px-3 disabled:opacity-50">
            <Send className="h-4 w-4" />
          </button>
        </form>
      </div>
    </>
  )
}
