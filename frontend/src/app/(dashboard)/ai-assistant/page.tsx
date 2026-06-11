'use client'

import { useState, useRef, useEffect } from 'react'
import { useMutation } from '@tanstack/react-query'
import { PageHeader } from '@/components/shared/PageHeader'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { aiService } from '@/lib/services'
import { useAuthStore } from '@/store/auth'
import { Sparkles, Send } from 'lucide-react'

type Msg = { role: 'user' | 'assistant'; text: string }

const SUGGESTIONS: Record<string, string[]> = {
  super_admin: [
    'What is this month\'s revenue?',
    'Which facilities are used most?',
    'What is the building occupancy?',
  ],
  company_admin: [
    'How many seats are free?',
    'Show pending invoices.',
    'List startups using our spare seats.',
  ],
  employee: [
    'Which conference rooms are available tomorrow?',
    'What are my upcoming bookings?',
    'Are there any free seats?',
  ],
}

export default function AIAssistantPage() {
  const role = useAuthStore(s => s.user?.role) ?? 'employee'
  const [messages, setMessages] = useState<Msg[]>([])
  const [input, setInput] = useState('')
  const [sessionId, setSessionId] = useState<string | undefined>(undefined)
  const endRef = useRef<HTMLDivElement>(null)

  useEffect(() => { endRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages])

  const chat = useMutation({
    mutationFn: (text: string) => aiService.chat(text, sessionId),
    onSuccess: (res) => {
      setSessionId(res.session_id)
      setMessages(m => [...m, { role: 'assistant', text: res.reply }])
    },
    onError: () => {
      setMessages(m => [...m, { role: 'assistant', text: 'Sorry — the AI service is unavailable right now. (Is GEMINI_API_KEY set?)' }])
    },
  })

  function send(text: string) {
    const t = text.trim()
    if (!t || chat.isPending) return
    setMessages(m => [...m, { role: 'user', text: t }])
    setInput('')
    chat.mutate(t)
  }

  return (
    <div className="space-y-4">
      <PageHeader title="AI Assistant" description="Ask about bookings, seats, revenue, invoices and more" />

      <Card className="flex flex-col h-[calc(100vh-220px)]">
        <CardContent className="flex-1 overflow-y-auto p-4 space-y-3">
          {messages.length === 0 && (
            <div className="h-full flex flex-col items-center justify-center text-center text-muted-foreground">
              <Sparkles className="h-10 w-10 mb-3 text-primary" />
              <p className="font-medium text-foreground">How can I help?</p>
              <p className="text-sm mt-1">Try one of these:</p>
              <div className="mt-4 flex flex-col gap-2 w-full max-w-md">
                {(SUGGESTIONS[role] ?? SUGGESTIONS.employee).map((s) => (
                  <button
                    key={s}
                    onClick={() => send(s)}
                    className="text-sm rounded-md border px-3 py-2 hover:bg-muted/50 transition-colors text-left"
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>
          )}
          {messages.map((m, i) => (
            <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[80%] rounded-lg px-3 py-2 text-sm whitespace-pre-wrap ${m.role === 'user' ? 'bg-primary text-primary-foreground' : 'bg-muted'}`}>
                {m.text}
              </div>
            </div>
          ))}
          {chat.isPending && (
            <div className="flex justify-start">
              <div className="bg-muted rounded-lg px-3 py-2 text-sm text-muted-foreground">Thinking…</div>
            </div>
          )}
          <div ref={endRef} />
        </CardContent>
        <div className="border-t p-3">
          <form onSubmit={(e) => { e.preventDefault(); send(input) }} className="flex gap-2">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask anything about your workspace…"
              disabled={chat.isPending}
            />
            <Button type="submit" disabled={chat.isPending || !input.trim()}>
              <Send className="h-4 w-4" />
            </Button>
          </form>
        </div>
      </Card>
    </div>
  )
}
