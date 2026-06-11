'use client'

import { useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import {
  LayoutDashboard, Building2, CalendarDays, FileText, Wrench, Users, Bell,
  Rocket, FolderOpen, BarChart3, LogOut, MessageSquare, Globe, FileSignature,
  CreditCard, Settings, Package, Receipt, Armchair, Sparkles, FileSpreadsheet,
  ChevronDown, X,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { useAuthStore } from '@/store/auth'
import type { Role } from '@/types'

interface NavItem { href: string; label: string; icon: React.ElementType; roles: Role[] }
interface NavSection { title: string; items: NavItem[] }

const ALL: Role[] = ['super_admin', 'company_admin', 'employee']
const ADMINS: Role[] = ['super_admin', 'company_admin']

const SECTIONS: NavSection[] = [
  {
    title: 'Overview',
    items: [
      { href: '/dashboard', label: 'Dashboard', icon: LayoutDashboard, roles: ALL },
      { href: '/analytics', label: 'Analytics', icon: BarChart3, roles: ADMINS },
    ],
  },
  {
    title: 'Spaces',
    items: [
      { href: '/buildings', label: 'Buildings', icon: Building2, roles: ['super_admin'] },
      { href: '/facilities', label: 'Facilities', icon: Building2, roles: ALL },
      { href: '/leases', label: 'Leases', icon: FileSpreadsheet, roles: ADMINS },
      { href: '/seat-leasing', label: 'Seat Leasing', icon: Armchair, roles: ADMINS },
      { href: '/seat-listings', label: 'Startup Seats', icon: Armchair, roles: ADMINS },
    ],
  },
  {
    title: 'Bookings',
    items: [
      { href: '/bookings', label: 'Bookings', icon: CalendarDays, roles: ALL },
    ],
  },
  {
    title: 'Billing',
    items: [
      { href: '/billing/invoices', label: 'Invoices', icon: FileText, roles: ADMINS },
      { href: '/payments', label: 'Payments', icon: CreditCard, roles: ADMINS },
      { href: '/vendors', label: 'Vendors', icon: Receipt, roles: ADMINS },
    ],
  },
  {
    title: 'Operations',
    items: [
      { href: '/inventory', label: 'Inventory', icon: Package, roles: ADMINS },
      { href: '/maintenance', label: 'Maintenance', icon: Wrench, roles: ALL },
      { href: '/visitors', label: 'Visitors', icon: Users, roles: ADMINS },
    ],
  },
  {
    title: 'People & Community',
    items: [
      { href: '/companies', label: 'Companies', icon: Building2, roles: ['super_admin'] },
      { href: '/incubation', label: 'Incubation', icon: Rocket, roles: ADMINS },
      { href: '/community', label: 'Community', icon: Globe, roles: ALL },
      { href: '/chat', label: 'Chat', icon: MessageSquare, roles: ALL },
      { href: '/documents', label: 'Documents', icon: FolderOpen, roles: ALL },
      { href: '/esign', label: 'E-Sign', icon: FileSignature, roles: ADMINS },
    ],
  },
  {
    title: 'Tools',
    items: [
      { href: '/ai-assistant', label: 'AI Assistant', icon: Sparkles, roles: ALL },
      { href: '/notifications', label: 'Notifications', icon: Bell, roles: ALL },
      { href: '/settings', label: 'Settings', icon: Settings, roles: ADMINS },
    ],
  },
]

export function Sidebar({ open = false, onClose }: { open?: boolean; onClose?: () => void }) {
  const pathname = usePathname()
  const { user, logout } = useAuthStore()
  const [collapsed, setCollapsed] = useState<Record<string, boolean>>({})

  const role = user?.role
  const sections = SECTIONS
    .map((s) => ({ ...s, items: s.items.filter((i) => role && i.roles.includes(role)) }))
    .filter((s) => s.items.length > 0)

  return (
    <>
      {/* Mobile backdrop */}
      {open && <div className="fixed inset-0 z-40 bg-black/50 lg:hidden" onClick={onClose} />}

      <aside
        className={cn(
          'fixed inset-y-0 left-0 z-50 w-[250px] bg-sidebar text-sidebar-foreground flex flex-col',
          'transform transition-transform duration-200 lg:static lg:translate-x-0 lg:shrink-0',
          open ? 'translate-x-0' : '-translate-x-full',
        )}
      >
        <div className="h-16 flex items-center justify-between px-5 border-b border-sidebar-border">
          <span className="text-xl font-bold text-white">CoWorkHub</span>
          <button className="lg:hidden text-white/70 hover:text-white" onClick={onClose} aria-label="Close menu">
            <X className="h-5 w-5" />
          </button>
        </div>

        <nav className="flex-1 py-3 overflow-y-auto">
          {sections.map((section) => {
            const isCollapsed = collapsed[section.title]
            return (
              <div key={section.title} className="mb-1">
                <button
                  onClick={() => setCollapsed((c) => ({ ...c, [section.title]: !c[section.title] }))}
                  className="w-full flex items-center justify-between px-5 py-1.5 text-[11px] font-semibold uppercase tracking-wider text-white/40 hover:text-white/70"
                >
                  {section.title}
                  <ChevronDown className={cn('h-3 w-3 transition-transform', isCollapsed && '-rotate-90')} />
                </button>
                {!isCollapsed && section.items.map(({ href, label, icon: Icon }) => {
                  const active = pathname === href || pathname.startsWith(href + '/')
                  return (
                    <Link
                      key={href}
                      href={href}
                      onClick={onClose}
                      className={cn(
                        'flex items-center gap-3 mx-2 px-3 py-2 rounded-md text-sm font-medium transition-colors',
                        active ? 'bg-white/15 text-white' : 'text-white/70 hover:bg-white/10 hover:text-white',
                      )}
                    >
                      <Icon className="h-4 w-4 shrink-0" />
                      {label}
                    </Link>
                  )
                })}
              </div>
            )
          })}
        </nav>

        <div className="p-4 border-t border-sidebar-border">
          <div className="text-xs text-white/50 mb-2 truncate px-2">{user?.email}</div>
          <button
            onClick={logout}
            className="flex items-center gap-2 w-full px-3 py-2 text-sm text-white/70 hover:text-white hover:bg-white/10 rounded-md transition-colors"
          >
            <LogOut className="h-4 w-4" />
            Sign out
          </button>
        </div>
      </aside>
    </>
  )
}
