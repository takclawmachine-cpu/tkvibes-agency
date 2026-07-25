'use client'

import { useState, useEffect, useCallback } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import {
  LayoutDashboard, Users, Building2, MessageSquare, FolderKanban,
  Globe, FileText, Send, ClipboardList, BarChart3, Activity,
  Settings, ChevronLeft, ChevronRight, Search, Bell,
  Menu, LucideIcon,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import CommandPalette from './CommandPalette'

interface NavItem {
  label: string
  href: string
  icon: LucideIcon
  badge?: string
}

const navItems: NavItem[] = [
  { label: 'Dashboard', href: '/', icon: LayoutDashboard },
  { label: 'Lead Pipeline', href: '/pipeline', icon: Users },
  { label: 'Businesses', href: '/businesses', icon: Building2 },
  { label: 'Communications', href: '/communications', icon: MessageSquare },
  { label: 'Projects', href: '/projects', icon: FolderKanban },
  { label: 'Website Generator', href: '/websites', icon: Globe },
  { label: 'Pitch Decks', href: '/pitch-decks', icon: FileText },
  { label: 'Outreach', href: '/outreach', icon: Send },
  { label: 'Tasks', href: '/tasks', icon: ClipboardList },
  { label: 'Analytics', href: '/analytics', icon: BarChart3 },
  { label: 'Agent Monitor', href: '/agents', icon: Activity },
  { label: 'Settings', href: '/settings', icon: Settings },
]

export default function Sidebar({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()
  const [collapsed, setCollapsed] = useState(false)
  const [mobileOpen, setMobileOpen] = useState(false)
  const [commandOpen, setCommandOpen] = useState(false)
  const [notifications, setNotifications] = useState(0)

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault()
        setCommandOpen(true)
      }
      if (e.key === 'Escape') {
        setCommandOpen(false)
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [])

  // Fetch notifications
  const fetchNotifications = useCallback(async () => {
    try {
      const res = await fetch('/api/stats')
      if (res.ok) {
        const data = await res.json()
        return data.overdueFollowUps || 0
      }
    } catch {}
    return 0
  }, [])

  useEffect(() => {
    let mounted = true
    const runFetch = async () => {
      const count = await fetchNotifications()
      if (mounted) setNotifications(count)
    }
    runFetch()
    const interval = setInterval(runFetch, 30000)
    return () => {
      mounted = false
      clearInterval(interval)
    }
  }, [fetchNotifications])

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      {/* Mobile overlay */}
      {mobileOpen && (
        <div
          className="fixed inset-0 bg-black/60 z-40 lg:hidden"
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          'fixed lg:static inset-y-0 left-0 z-50 flex flex-col bg-surface border-r border-border transition-all duration-300',
          collapsed ? 'w-16' : 'w-60',
          mobileOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        )}
      >
        {/* Logo */}
        <div className={cn(
          'flex items-center h-14 px-4 border-b border-border',
          collapsed && 'justify-center px-0'
        )}>
          {collapsed ? (
            <div className="w-8 h-8 rounded-lg bg-accent flex items-center justify-center">
              <span className="text-white font-bold text-sm">H</span>
            </div>
          ) : (
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-accent flex items-center justify-center flex-shrink-0">
                <span className="text-white font-bold text-sm">H</span>
              </div>
              <div>
                <h1 className="text-sm font-semibold text-text-primary">Hermes Ops</h1>
                <p className="text-[10px] text-text-muted">Operations Dashboard</p>
              </div>
            </div>
          )}
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto py-3 px-2 space-y-0.5">
          {navItems.map((item) => {
            const isActive = pathname === item.href
            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={() => setMobileOpen(false)}
                className={cn(
                  'flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-all duration-200 group',
                  isActive
                    ? 'bg-accent-subtle text-accent font-medium'
                    : 'text-text-secondary hover:text-text-primary hover:bg-surface-hover',
                  collapsed && 'justify-center px-2'
                )}
                title={collapsed ? item.label : undefined}
              >
                <item.icon className="w-4 h-4 flex-shrink-0" />
                {!collapsed && (
                  <>
                    <span className="flex-1 truncate">{item.label}</span>
                    {item.badge && (
                      <span className="badge-red text-[10px] px-1.5 py-0.5">{item.badge}</span>
                    )}
                  </>
                )}
              </Link>
            )
          })}
        </nav>

        {/* Bottom */}
        <div className={cn(
          'border-t border-border p-3',
          collapsed && 'flex justify-center'
        )}>
          <button
            onClick={() => setCollapsed(!collapsed)}
            className="btn-ghost btn-icon hidden lg:flex"
          >
            {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
          </button>
        </div>
      </aside>

      {/* Main area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top bar */}
        <header className="h-14 border-b border-border bg-surface/50 backdrop-blur-xl flex items-center justify-between px-4 lg:px-6 flex-shrink-0">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setMobileOpen(true)}
              className="btn-ghost btn-icon lg:hidden"
            >
              <Menu className="w-4 h-4" />
            </button>
            <button
              onClick={() => setCommandOpen(true)}
              className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-surface-active border border-border text-text-muted text-xs hover:border-border-light transition-colors"
            >
              <Search className="w-3.5 h-3.5" />
              <span>Search...</span>
              <kbd className="ml-6 px-1.5 py-0.5 rounded bg-surface text-[10px] font-mono text-text-muted border border-border">
                ⌘K
              </kbd>
            </button>
          </div>

          <div className="flex items-center gap-2">
            <button className="btn-ghost btn-icon relative">
              <Bell className="w-4 h-4" />
              {notifications > 0 && (
                <span className="absolute -top-0.5 -right-0.5 w-4 h-4 bg-danger rounded-full text-[9px] font-bold text-white flex items-center justify-center">
                  {notifications > 9 ? '9+' : notifications}
                </span>
              )}
            </button>
          </div>
        </header>

        {/* Content */}
        <main className="flex-1 overflow-y-auto p-4 lg:p-6">
          {children}
        </main>
      </div>

      {/* Command Palette */}
      {commandOpen && (
        <CommandPalette onClose={() => setCommandOpen(false)} />
      )}
    </div>
  )
}