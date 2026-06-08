'use client'

import { Bell, User } from 'lucide-react'
import { useAuthStore } from '@/store/auth'
import { Button } from '@/components/ui/button'

export function Navbar() {
  const { user } = useAuthStore()

  const roleBadgeColor: Record<string, string> = {
    super_admin: 'bg-purple-100 text-purple-800',
    company_admin: 'bg-blue-100 text-blue-800',
    employee: 'bg-green-100 text-green-800',
  }

  return (
    <header className="h-16 border-b bg-background flex items-center px-6 gap-4">
      <div className="flex-1" />

      <Button variant="ghost" size="icon" asChild>
        <a href="/notifications">
          <Bell className="h-4 w-4" />
        </a>
      </Button>

      <div className="flex items-center gap-2">
        <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center">
          <User className="h-4 w-4 text-primary" />
        </div>
        <div className="text-sm">
          <div className="font-medium leading-none">{user?.full_name || user?.email}</div>
          {user?.role && (
            <span className={`text-xs px-1.5 py-0.5 rounded font-medium mt-0.5 inline-block ${roleBadgeColor[user.role] ?? ''}`}>
              {user.role.replace(/_/g, ' ')}
            </span>
          )}
        </div>
      </div>
    </header>
  )
}
