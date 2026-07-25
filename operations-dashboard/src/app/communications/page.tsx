'use client'

import { useState, useEffect } from 'react'
import { MessageSquare, Mail, Phone, Calendar, FileText, Send, Inbox, Loader2, Search, Building2 } from 'lucide-react'
import { cn, formatDateTime, formatRelativeTime } from '@/lib/utils'

interface Communication {
  id: string
  type: string
  subject: string | null
  content: string | null
  direction: string
  status: string
  createdAt: string
  business: { name: string; logo: string | null } | null
}

const TYPE_ICONS: Record<string, React.ElementType> = {
  email: Mail,
  call: Phone,
  note: MessageSquare,
  meeting: Calendar,
  quotation: FileText,
  proposal: FileText,
  website: Send,
  discovery: Search,
  won: Send,
  lost: Send,
}

const TYPE_COLORS: Record<string, string> = {
  email: '#3b82f6',
  call: '#10b981',
  note: '#f59e0b',
  meeting: '#6366f1',
  quotation: '#ec4899',
  proposal: '#8b5cf6',
  website: '#06b6d4',
  discovery: '#6b7280',
  won: '#22c55e',
  lost: '#ef4444',
}

export default function CommunicationsPage() {
  const [communications, setCommunications] = useState<Communication[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [typeFilter, setTypeFilter] = useState('')

  const fetchCommunications = useCallback(async () => {
    try {
      const params = new URLSearchParams()
      if (typeFilter) params.set('type', typeFilter)
      const res = await fetch(`/api/communications?${params}`)
      if (res.ok) {
        const data = await res.json()
        setCommunications(data)
      }
    } catch (err) {
      console.error('Failed to fetch communications', err)
    } finally {
      setLoading(false)
    }
  }, [typeFilter])

  useEffect(() => {
    // eslint-disable-next-line react-hooks/exhaustive-deps
    fetchCommunications()
  }, [fetchCommunications])

  const filtered = communications.filter(c => {
    if (search) {
      const q = search.toLowerCase()
      const matches = (c.subject?.toLowerCase().includes(q) || c.content?.toLowerCase().includes(q) || c.business?.name.toLowerCase().includes(q))
      if (!matches) return false
    }
    return true
  })

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div>
        <h1 className="text-xl font-bold text-text-primary">Communications</h1>
        <p className="text-sm text-text-muted mt-0.5">Track all interactions with businesses</p>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-3 flex-wrap">
        <div className="relative flex-1 max-w-xs">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted" />
          <input
            type="text"
            placeholder="Search communications..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="input pl-9"
          />
        </div>
        <select
          value={typeFilter}
          onChange={e => { setTypeFilter(e.target.value) }}
          className="select w-40"
        >
          <option value="">All Types</option>
          <option value="email">Email</option>
          <option value="call">Call</option>
          <option value="note">Note</option>
          <option value="meeting">Meeting</option>
          <option value="quotation">Quotation</option>
          <option value="proposal">Proposal</option>
          <option value="discovery">Discovery</option>
        </select>
        <button onClick={fetchCommunications} className="btn-ghost btn-sm">
          <Loader2 className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      {/* List */}
      <div className="space-y-1">
        {loading ? (
          Array.from({ length: 8 }).map((_, i) => (
            <div key={i} className="card animate-pulse flex items-start gap-4">
              <div className="skeleton h-10 w-10 rounded-lg" />
              <div className="flex-1 space-y-2">
                <div className="skeleton h-4 w-48" />
                <div className="skeleton h-3 w-32" />
              </div>
            </div>
          ))
        ) : filtered.length === 0 ? (
          <div className="card py-12 text-center">
            <MessageSquare className="w-10 h-10 text-text-muted/30 mx-auto mb-3" />
            <p className="text-sm text-text-muted">No communications found</p>
          </div>
        ) : (
          filtered.map((comm) => {
            const Icon = TYPE_ICONS[comm.type] || MessageSquare
            const color = TYPE_COLORS[comm.type] || '#6b7280'
            return (
              <div key={comm.id} className="card hover:border-border-light transition-all duration-200 flex items-start gap-4">
                <div className="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0" style={{ backgroundColor: `${color}15`, color }}>
                  <Icon className="w-4 h-4" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs font-medium uppercase tracking-wider" style={{ color }}>{comm.type}</span>
                    <span className="badge-gray text-[10px]">{comm.direction}</span>
                    {comm.business && (
                      <span className="text-xs text-text-muted flex items-center gap-1">
                        <Building2 className="w-3 h-3" />
                        {comm.business.name}
                      </span>
                    )}
                    <span className="text-[10px] text-text-muted ml-auto">{formatRelativeTime(comm.createdAt)}</span>
                  </div>
                  {comm.subject && (
                    <p className="text-sm font-medium text-text-primary truncate">{comm.subject}</p>
                  )}
                  {comm.content && (
                    <p className="text-xs text-text-secondary mt-1 line-clamp-2">{comm.content}</p>
                  )}
                </div>
              </div>
            )
          })
        )}
      </div>
    </div>
  )
}