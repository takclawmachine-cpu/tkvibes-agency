'use client'

import { useState, useEffect, useCallback } from 'react'
import { Send, Mail, CheckCircle, XCircle, Clock, RefreshCw, Search, AlertTriangle, Eye } from 'lucide-react'
import { cn, formatRelativeTime, formatDate } from '@/lib/utils'

interface Email {
  id: string
  from: string
  to: string
  subject: string
  body: string | null
  status: string
  sentAt: string | null
  openedAt: string | null
  repliedAt: string | null
  createdAt: string
  business: { name: string } | null
}

const STATUS_CONFIG: Record<string, { label: string; color: string; icon: React.ElementType }> = {
  draft: { label: 'Draft', color: '#6b7280', icon: Clock },
  queued: { label: 'Queued', color: '#f59e0b', icon: Clock },
  sent: { label: 'Sent', color: '#3b82f6', icon: Send },
  delivered: { label: 'Delivered', color: '#06b6d4', icon: Send },
  bounced: { label: 'Bounced', color: '#ef4444', icon: XCircle },
  opened: { label: 'Opened', color: '#10b981', icon: Eye },
  clicked: { label: 'Clicked', color: '#22c55e', icon: Mail },
  replied: { label: 'Replied', color: '#6366f1', icon: CheckCircle },
  failed: { label: 'Failed', color: '#ef4444', icon: AlertTriangle },
}

export default function OutreachPage() {
  const [emails, setEmails] = useState<Email[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('')

  const fetchEmails = useCallback(async () => {
    try {
      const params = new URLSearchParams()
      if (statusFilter) params.set('status', statusFilter)
      const res = await fetch(`/api/emails?${params}`)
      if (res.ok) {
        const data = await res.json()
        setEmails(data)
      }
    } catch (err) {
      console.error('Failed to fetch emails', err)
    } finally {
      setLoading(false)
    }
  }, [statusFilter])

  useEffect(() => {
    // eslint-disable-next-line react-hooks/exhaustive-deps
    fetchEmails()
  }, [fetchEmails])

  const filtered = emails.filter(e => {
    if (search) {
      const q = search.toLowerCase()
      return e.subject.toLowerCase().includes(q) || e.to.toLowerCase().includes(q) || e.from.toLowerCase().includes(q)
    }
    return true
  })

  const statusCounts = emails.reduce((acc, e) => {
    acc[e.status] = (acc[e.status] || 0) + 1
    return acc
  }, {} as Record<string, number>)

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-xl font-bold text-text-primary">Outreach</h1>
        <p className="text-sm text-text-muted mt-0.5">Email tracking and outreach management</p>
      </div>

      {/* Status summary */}
      <div className="flex items-center gap-2 flex-wrap">
        {Object.entries(STATUS_CONFIG).map(([key, config]) => {
          const count = statusCounts[key] || 0
          return (
            <button
              key={key}
              onClick={() => setStatusFilter(statusFilter === key ? '' : key)}
              className={cn(
                'inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all border',
                statusFilter === key
                  ? 'border-accent/30 bg-accent-subtle text-accent'
                  : 'border-border text-text-secondary hover:text-text-primary hover:bg-surface-hover'
              )}
            >
              <config.icon className="w-3 h-3" style={{ color: config.color }} />
              {config.label}
              {count > 0 && <span className="text-text-muted">({count})</span>}
            </button>
          )
        })}
      </div>

      {/* Search bar */}
      <div className="flex items-center gap-3">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted" />
          <input
            type="text"
            placeholder="Search emails by subject, to, or from..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="input pl-9"
          />
        </div>
        <button onClick={fetchEmails} className="btn-ghost btn-sm">
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      {/* Email list */}
      <div className="space-y-1">
        {loading ? (
          Array.from({ length: 8 }).map((_, i) => (
            <div key={i} className="card animate-pulse flex items-start gap-4">
              <div className="skeleton h-10 w-10 rounded-lg" />
              <div className="flex-1 space-y-2">
                <div className="skeleton h-4 w-56" />
                <div className="skeleton h-3 w-40" />
              </div>
            </div>
          ))
        ) : filtered.length === 0 ? (
          <div className="card py-12 text-center">
            <Send className="w-10 h-10 text-text-muted/30 mx-auto mb-3" />
            <p className="text-sm text-text-muted">No emails found</p>
          </div>
        ) : (
          filtered.map((email) => {
            const config = STATUS_CONFIG[email.status] || STATUS_CONFIG.draft
            const Icon = config.icon
            return (
              <div key={email.id} className="card hover:border-border-light transition-all duration-200">
                <div className="flex items-start gap-4">
                  <div className="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0" style={{ backgroundColor: `${config.color}15`, color: config.color }}>
                    <Icon className="w-4 h-4" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-0.5">
                      <span className="text-sm font-medium text-text-primary truncate">{email.subject}</span>
                      <span className="badge text-[10px] flex-shrink-0" style={{ backgroundColor: `${config.color}15`, color: config.color }}>
                        {config.label}
                      </span>
                    </div>
                    <div className="flex items-center gap-3 text-xs text-text-muted">
                      <span>To: {email.to}</span>
                      <span>From: {email.from}</span>
                      {email.business && <span>· {email.business.name}</span>}
                    </div>
                    <div className="flex items-center gap-3 text-[10px] text-text-muted mt-1">
                      <span>Created: {formatRelativeTime(email.createdAt)}</span>
                      {email.sentAt && <span>· Sent: {formatDate(email.sentAt)}</span>}
                      {email.openedAt && <span>· Opened: {formatDate(email.openedAt)}</span>}
                      {email.repliedAt && <span>· Replied: {formatDate(email.repliedAt)}</span>}
                    </div>
                  </div>
                </div>
              </div>
            )
          })
        )}
      </div>
    </div>
  )
}