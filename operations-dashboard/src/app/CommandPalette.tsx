'use client'

import { useState, useEffect, useRef } from 'react'
import { useRouter } from 'next/navigation'
import { Search, ArrowRight, Users, Building2, LayoutDashboard, MessageSquare, FolderKanban, Globe, FileText, Send, ClipboardList, BarChart3, Activity, Settings } from 'lucide-react'

interface CommandItem {
  label: string
  href: string
  icon: React.ElementType
  keywords: string[]
}

const commands: CommandItem[] = [
  { label: 'Dashboard', href: '/', icon: LayoutDashboard, keywords: ['home', 'overview', 'stats', 'main'] },
  { label: 'Lead Pipeline (Kanban)', href: '/pipeline', icon: Users, keywords: ['leads', 'kanban', 'stages', 'pipeline'] },
  { label: 'Businesses', href: '/businesses', icon: Building2, keywords: ['companies', 'clients', 'leads', 'list'] },
  { label: 'Communications', href: '/communications', icon: MessageSquare, keywords: ['messages', 'email', 'history', 'log'] },
  { label: 'Projects', href: '/projects', icon: FolderKanban, keywords: ['work', 'tasks', 'project management'] },
  { label: 'Websites', href: '/websites', icon: Globe, keywords: ['generated', 'sites', 'web'] },
  { label: 'Pitch Decks', href: '/pitch-decks', icon: FileText, keywords: ['decks', 'presentations', 'proposals'] },
  { label: 'Outreach', href: '/outreach', icon: Send, keywords: ['email', 'campaign', 'send'] },
  { label: 'Tasks', href: '/tasks', icon: ClipboardList, keywords: ['todo', 'follow up', 'reminders'] },
  { label: 'Analytics', href: '/analytics', icon: BarChart3, keywords: ['charts', 'reports', 'metrics', 'data'] },
  { label: 'Agent Monitor', href: '/agents', icon: Activity, keywords: ['agents', 'hermes', 'skills', 'status'] },
  { label: 'Settings', href: '/settings', icon: Settings, keywords: ['config', 'preferences', 'backup', 'export'] },
]

export default function CommandPalette({ onClose }: { onClose: () => void }) {
  const router = useRouter()
  const [query, setQuery] = useState('')
  const [selectedIndex, setSelectedIndex] = useState(0)
  const inputRef = useRef<HTMLInputElement>(null)

  const filtered = query
    ? commands.filter(c =>
        c.label.toLowerCase().includes(query.toLowerCase()) ||
        c.keywords.some(k => k.includes(query.toLowerCase()))
      )
    : commands

  // Reset selection when query changes - do it in the onChange handler
  const handleQueryChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setQuery(e.target.value)
    setSelectedIndex(0)
  }

  useEffect(() => {
    inputRef.current?.focus()
  }, [query])

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'ArrowDown') {
        e.preventDefault()
        setSelectedIndex(i => Math.min(i + 1, filtered.length - 1))
      }
      if (e.key === 'ArrowUp') {
        e.preventDefault()
        setSelectedIndex(i => Math.max(i - 1, 0))
      }
      if (e.key === 'Enter' && filtered[selectedIndex]) {
        router.push(filtered[selectedIndex].href)
        onClose()
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [filtered, selectedIndex, router, onClose])

  return (
    <>
      <div className="command-overlay" onClick={onClose} />
      <div className="fixed inset-0 z-50 flex items-start justify-center pt-[15vh]">
        <div className="w-full max-w-lg animate-scale-in">
          <div className="glass rounded-xl shadow-2xl overflow-hidden">
            {/* Search */}
            <div className="flex items-center gap-3 px-4 py-3 border-b border-border">
              <Search className="w-4 h-4 text-text-muted" />
              <input
                ref={inputRef}
                type="text"
                placeholder="Search pages..."
                value={query}
                onChange={handleQueryChange}
                className="flex-1 bg-transparent text-sm text-text-primary placeholder:text-text-muted outline-none"
              />
              <kbd className="px-1.5 py-0.5 rounded bg-surface text-[10px] font-mono text-text-muted border border-border">
                ESC
              </kbd>
            </div>

            {/* Results */}
            <div className="max-h-72 overflow-y-auto p-2 space-y-0.5">
              {filtered.length === 0 ? (
                <div className="py-8 text-center text-sm text-text-muted">
                  No results found
                </div>
              ) : (
                filtered.map((item, i) => (
                  <button
                    key={item.href}
                    onClick={() => {
                      router.push(item.href)
                      onClose()
                    }}
                    onMouseEnter={() => setSelectedIndex(i)}
                    className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all ${
                      i === selectedIndex
                        ? 'bg-accent-subtle text-accent'
                        : 'text-text-secondary hover:text-text-primary hover:bg-surface-hover'
                    }`}
                  >
                    <item.icon className="w-4 h-4" />
                    <span className="flex-1 text-left">{item.label}</span>
                    <ArrowRight className="w-3.5 h-3.5 opacity-0 group-hover:opacity-100" />
                  </button>
                ))
              )}
            </div>

            {/* Footer */}
            <div className="px-4 py-2 border-t border-border flex items-center gap-4 text-[10px] text-text-muted">
              <span>↑↓ Navigate</span>
              <span>↵ Open</span>
              <span>Esc Close</span>
            </div>
          </div>
        </div>
      </div>
    </>
  )
}