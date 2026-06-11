'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import {
  LayoutDashboard,
  Building2,
  CalendarDays,
  FileText,
  Wrench,
  Users,
  Bell,
  Rocket,
  FolderOpen,
  BarChart3,
  LogOut,
  ChevronRight,
  MessageSquare,
  Globe,
  FileSignature,
  CreditCard,
  Settings,
  Package,
  Receipt,
  Armchair,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { useAuthStore } from '@/store/auth'
import type { Role } from '@/types'

interface NavItem {
  href: string
  label: string
  icon: React.ElementType
  roles: Role[]
}

const NAV_ITEMS: NavItem[] = [
  { href: '/dashboard', label: 'Dashboard', icon: LayoutDashboard, roles: ['super_admin', 'company_admin', 'employee'] },
  { href: '/facilities', label: 'Facilities', icon: Building2, roles: ['super_admin', 'company_admin', 'employee'] },
  { href: '/bookings', label: 'Bookings', icon: CalendarDays, roles: ['super_admin', 'company_admin', 'employee'] },
  { href: '/billing/invoices', label: 'Invoices', icon: FileText, roles: ['super_admin', 'company_admin'] },
  { href: '/maintenance', label: 'Maintenance', icon: Wrench, roles: ['super_admin', 'company_admin', 'employee'] },
  { href: '/visitors', label: 'Visitors', icon: Users, roles: ['super_admin', 'company_admin'] },
  { href: '/incubation', label: 'Incubation', icon: Rocket, roles: ['super_admin', 'company_admin'] },
  { href: '/documents', label: 'Documents', icon: FolderOpen, roles: ['super_admin', 'company_admin', 'employee'] },
  { href: '/inventory', label: 'Inventory', icon: Package, roles: ['super_admin', 'company_admin'] },
  { href: '/vendors', label: 'Vendors', icon: Receipt, roles: ['super_admin', 'company_admin'] },
  { href: '/seat-leasing', label: 'Seat Leasing', icon: Armchair, roles: ['super_admin', 'company_admin'] },
  { href: '/analytics', label: 'Analytics', icon: BarChart3, roles: ['super_admin', 'company_admin'] },
  { href: '/buildings', label: 'Buildings', icon: Building2, roles: ['super_admin'] },
  { href: '/companies', label: 'Companies', icon: Building2, roles: ['super_admin'] },
  { href: '/chat', label: 'Chat', icon: MessageSquare, roles: ['super_admin', 'company_admin', 'employee'] },
  { href: '/community', label: 'Community', icon: Globe, roles: ['super_admin', 'company_admin', 'employee'] },
  { href: '/esign', label: 'E-Sign', icon: FileSignature, roles: ['super_admin', 'company_admin'] },
  { href: '/payments', label: 'Payments', icon: CreditCard, roles: ['super_admin', 'company_admin'] },
  { href: '/notifications', label: 'Notifications', icon: Bell, roles: ['super_admin', 'company_admin', 'employee'] },
  { href: '/settings', label: 'Settings', icon: Settings, roles: ['super_admin', 'company_admin'] },
]

export function Sidebar() {
  const pathname = usePathname()
  const { user, logout } = useAuthStore()

  const visibleItems = NAV_ITEMS.filter((item) => user?.role && item.roles.includes(user.role))

  return (
    <aside className="w-[230px] min-h-screen bg-sidebar text-sidebar-foreground flex flex-col shrink-0">
      <div className="h-16 flex items-center px-6 border-b border-sidebar-border">
        <span className="text-xl font-bold text-white">CoWorkHub</span>
      </div>

      <nav className="flex-1 py-4 overflow-y-auto">
        {visibleItems.map(({ href, label, icon: Icon }) => {
          const active = pathname === href || pathname.startsWith(href + '/')
          return (
            <Link
              key={href}
              href={href}
              className={cn(
                'flex items-center gap-3 mx-2 px-4 py-2.5 rounded-md text-sm font-medium transition-colors',
                active
                  ? 'bg-white/15 text-white'
                  : 'text-white/70 hover:bg-white/10 hover:text-white'
              )}
            >
              <Icon className="h-4 w-4 shrink-0" />
              {label}
              {active && <ChevronRight className="h-3 w-3 ml-auto" />}
            </Link>
          )
        })}
      </nav>

      <div className="p-4 border-t border-sidebar-border">
        <div className="text-xs text-white/50 mb-2 truncate px-2">
          {user?.email}
        </div>
        <button
          onClick={logout}
          className="flex items-center gap-2 w-full px-4 py-2 text-sm text-white/70 hover:text-white hover:bg-white/10 rounded-md transition-colors"
        >
          <LogOut className="h-4 w-4" />
          Sign out
        </button>
      </div>
    </aside>
  )
}
