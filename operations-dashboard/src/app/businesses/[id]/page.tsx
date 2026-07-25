'use client'

import { useState, useEffect, useReducer } from 'react'
import { useParams, useRouter } from 'next/navigation'
import Link from 'next/link'
import {
  Building2, MapPin, Phone, Mail, Globe, Star, ChevronLeft,
  AlertCircle, Clock, Calendar, MessageSquare, CheckCircle2,
  FileText, Image as ImageIcon, ListTodo, ScrollText, Tag, ExternalLink,
  Pencil, Target, Users, DollarSign,
  Send, PhoneCall, StickyNote, Loader2,
  History, Hash, Eye, Download,
} from 'lucide-react'
import { cn, formatDate, formatDateTime, formatCurrency, getScoreLabel, getStageColor } from '@/lib/utils'

// ─── Types ───────────────────────────────────────────────────────────────────

interface TagItem {
  id: string
  name: string
  color: string | null
}

interface BusinessTag {
  tag: TagItem
}

interface Contact {
  id: string
  name: string
  role: string | null
  phone: string | null
  email: string | null
  isPrimary: boolean
}

interface TimelineEvent {
  id: string
  type: string
  title: string
  description: string | null
  createdAt: string
  createdBy?: { name: string } | null
}

interface Communication {
  id: string
  type: string
  subject: string | null
  content: string | null
  direction: string
  status: string
  createdAt: string
  createdBy?: { name: string } | null
}

interface Task {
  id: string
  title: string
  description: string | null
  status: string
  priority: string
  dueDate: string | null
  category: string | null
  createdAt: string
}

interface GeneratedAsset {
  id: string
  type: string
  name: string
  description: string | null
  filePath: string | null
  url: string | null
  status: string
  createdAt: string
}

interface Proposal {
  id: string
  title: string
  content: string | null
  filePath: string | null
  status: string
  amount: number | null
  sentAt: string | null
  createdAt: string
}

interface Meeting {
  id: string
  title: string
  description: string | null
  scheduledAt: string
  duration: number | null
  status: string
  location: string | null
  notes: string | null
  outcome: string | null
}

interface Note {
  id: string
  content: string
  type: string
  createdAt: string
  createdBy?: { name: string } | null
}

interface Business {
  id: string
  name: string
  logo: string | null
  category: string | null
  address: string | null
  phone: string | null
  email: string | null
  website: string | null
  googleMapsLink: string | null
  googleRating: number | null
  reviewCount: number | null
  websiteQuality: string | null
  businessSize: string | null
  industry: string | null
  stage: string
  leadScore: number
  expectedRevenue: number | null
  priority: string
  createdAt: string
  updatedAt: string
  contacts: Contact[]
  tags: BusinessTag[]
  timelineEvents: TimelineEvent[]
  communications: Communication[]
  tasks: Task[]
  generatedAssets: GeneratedAsset[]
  proposals: Proposal[]
  meetings: Meeting[]
  notes: Note[]
  assignedAgent?: { name: string; email: string } | null
}

// ─── Helpers ─────────────────────────────────────────────────────────────────

function getTimelineIcon(type: string) {
  switch (type) {
    case 'lead_found': return Target
    case 'website_generated': return Globe
    case 'email_sent': return Send
    case 'proposal_created': return FileText
    case 'status_changed': return History
    case 'meeting_scheduled': return Calendar
    case 'task_completed': return CheckCircle2
    default: return Clock
  }
}

function getTimelineColor(type: string): string {
  switch (type) {
    case 'lead_found': return '#3b82f6'
    case 'website_generated': return '#8b5cf6'
    case 'email_sent': return '#06b6d4'
    case 'proposal_created': return '#ec4899'
    case 'status_changed': return '#f59e0b'
    case 'meeting_scheduled': return '#6366f1'
    case 'task_completed': return '#22c55e'
    default: return '#6b7280'
  }
}

function getCommIcon(type: string) {
  switch (type) {
    case 'email': return Send
    case 'call': return PhoneCall
    case 'meeting': return Calendar
    case 'note': return StickyNote
    case 'quotation': return DollarSign
    case 'proposal': return FileText
    case 'website': return Globe
    case 'discovery': return SearchIcon
    case 'won': return CheckCircle2
    case 'lost': return AlertCircle
    default: return MessageSquare
  }
}

function SearchIcon({ className }: { className?: string }) {
  return <svg className={className} width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
}

function getCommColor(type: string): string {
  switch (type) {
    case 'email': return '#06b6d4'
    case 'call': return '#22c55e'
    case 'meeting': return '#6366f1'
    case 'note': return '#f59e0b'
    case 'quotation': return '#ec4899'
    case 'proposal': return '#8b5cf6'
    case 'won': return '#22c55e'
    case 'lost': return '#ef4444'
    default: return '#6b7280'
  }
}

function getTaskPriorityColor(priority: string): string {
  switch (priority) {
    case 'critical': return '#ef4444'
    case 'high': return '#f97316'
    case 'medium': return '#f59e0b'
    case 'low': return '#3b82f6'
    default: return '#6b7280'
  }
}

function getAssetIcon(type: string) {
  switch (type) {
    case 'website': return Globe
    case 'pitch_deck': return FileText
    case 'proposal': return ScrollText
    case 'document': return FileText
    default: return ImageIcon
  }
}

function getProposalStatusColor(status: string): string {
  switch (status) {
    case 'draft': return '#6b7280'
    case 'sent': return '#3b82f6'
    case 'accepted': return '#22c55e'
    case 'rejected': return '#ef4444'
    case 'revised': return '#f59e0b'
    default: return '#6b7280'
  }
}

function getSizeLabel(size: string | null): string {
  switch (size) {
    case 'small': return 'Small (1-10)'
    case 'medium': return 'Medium (11-50)'
    case 'large': return 'Large (50+)'
    default: return '—'
  }
}

function getWebsiteQualityLabel(wq: string | null): string {
  switch (wq) {
    case 'none': return 'No Website'
    case 'outdated': return 'Outdated'
    case 'good': return 'Good'
    case 'excellent': return 'Excellent'
    default: return '—'
  }
}

// ─── Skeleton ────────────────────────────────────────────────────────────────

function Skeleton() {
  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header skeleton */}
      <div className="card">
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 rounded-xl skeleton" />
          <div className="flex-1 space-y-2">
            <div className="h-6 w-48 skeleton rounded" />
            <div className="h-4 w-32 skeleton rounded" />
          </div>
        </div>
      </div>
      {/* Grid skeleton */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {[1, 2, 3].map((i) => (
          <div key={i} className="card space-y-3">
            <div className="h-5 w-24 skeleton rounded" />
            <div className="h-4 w-full skeleton rounded" />
            <div className="h-4 w-3/4 skeleton rounded" />
            <div className="h-4 w-1/2 skeleton rounded" />
          </div>
        ))}
      </div>
      {/* Timeline skeleton */}
      <div className="card space-y-3">
        <div className="h-5 w-32 skeleton rounded" />
        {[1, 2, 3].map((i) => (
          <div key={i} className="flex gap-3">
            <div className="w-8 h-8 rounded-full skeleton flex-shrink-0" />
            <div className="flex-1 space-y-1">
              <div className="h-4 w-40 skeleton rounded" />
              <div className="h-3 w-24 skeleton rounded" />
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

// ─── Sections ────────────────────────────────────────────────────────────────

function HeaderSection({
  business,
  onEdit,
}: {
  business: Business
  onEdit: () => void
}) {
  const score = getScoreLabel(business.leadScore)
  const stageColor = getStageColor(business.stage)

  return (
    <div className="card animate-fade-in">
      <div className="flex items-start justify-between gap-4 flex-wrap">
        <div className="flex items-center gap-4 min-w-0">
          {/* Logo */}
          <div className="w-16 h-16 rounded-xl bg-accent-subtle flex items-center justify-center flex-shrink-0 overflow-hidden">
            {business.logo ? (
              <img
                src={business.logo}
                alt={`${business.name} logo`}
                className="w-full h-full object-cover"
              />
            ) : (
              <Building2 className="w-7 h-7 text-accent" />
            )}
          </div>

          <div className="min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              <h1 className="text-xl font-bold text-text-primary truncate">
                {business.name}
              </h1>
              {business.category && (
                <span className="badge-purple text-xs">{business.category}</span>
              )}
            </div>
            <div className="flex items-center gap-2 mt-1.5 flex-wrap">
              {/* Stage badge */}
              <span
                className="badge text-xs"
                style={{
                  background: `${stageColor}18`,
                  color: stageColor,
                  border: `1px solid ${stageColor}30`,
                }}
              >
                {business.stage}
              </span>
              {/* Score badge */}
              <span
                className="badge text-xs"
                style={{
                  background: `${score.color}18`,
                  color: score.color,
                  border: `1px solid ${score.color}30`,
                }}
              >
                {business.leadScore} — {score.label}
              </span>
              {/* Priority */}
              {business.priority && (
                <span className="badge-gray text-xs capitalize">
                  {business.priority} priority
                </span>
              )}
              {/* Assigned agent */}
              {business.assignedAgent && (
                <span className="badge-gray text-xs">
                  <Users className="w-3 h-3 mr-1" />
                  {business.assignedAgent.name}
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2 flex-shrink-0">
          <button onClick={onEdit} className="btn-primary btn-sm">
            <Pencil className="w-3.5 h-3.5" />
            Edit
          </button>
        </div>
      </div>
    </div>
  )
}

function DetailsSection({ business }: { business: Business }) {
  const details = [
    { label: 'Address', value: business.address, icon: MapPin },
    { label: 'Phone', value: business.phone, icon: Phone, href: business.phone ? `tel:${business.phone}` : null },
    { label: 'Email', value: business.email, icon: Mail, href: business.email ? `mailto:${business.email}` : null },
    { label: 'Website', value: business.website, icon: Globe, href: business.website ? business.website.startsWith('http') ? business.website : `https://${business.website}` : null },
    { label: 'Google Maps', value: business.googleMapsLink ? 'View on Maps' : null, icon: MapPin, href: business.googleMapsLink || null },
    { label: 'Rating', value: business.googleRating != null ? `${business.googleRating} ⭐ (${business.reviewCount || 0} reviews)` : '—', icon: Star },
    { label: 'Website Quality', value: getWebsiteQualityLabel(business.websiteQuality), icon: Globe },
    { label: 'Industry', value: business.industry || '—', icon: Target },
    { label: 'Business Size', value: getSizeLabel(business.businessSize), icon: Users },
    { label: 'Expected Revenue', value: business.expectedRevenue ? formatCurrency(business.expectedRevenue) : '—', icon: DollarSign },
    { label: 'Created', value: formatDate(business.createdAt), icon: Calendar },
    { label: 'Last Updated', value: formatDate(business.updatedAt), icon: Clock },
  ]

  return (
    <div className="card animate-fade-in">
      <h2 className="text-sm font-semibold text-text-primary mb-4 flex items-center gap-2">
        <Building2 className="w-4 h-4 text-accent" />
        Details
      </h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-3">
        {details.map((d) => (
          <div key={d.label} className="flex items-start gap-2.5">
            <d.icon className="w-4 h-4 text-text-muted mt-0.5 flex-shrink-0" />
            <div className="min-w-0">
              <span className="label">{d.label}</span>
              {d.href ? (
                <a
                  href={d.href}
                  target={d.href.startsWith('http') ? '_blank' : undefined}
                  rel="noopener noreferrer"
                  className="value text-accent hover:text-accent-hover truncate block transition-colors"
                >
                  {d.value}
                  <ExternalLink className="w-3 h-3 inline ml-1 opacity-60" />
                </a>
              ) : (
                <span className="value truncate block">{d.value || '—'}</span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

function TagsSection({ tags }: { tags: BusinessTag[] }) {
  if (!tags.length) return null

  return (
    <div className="card animate-fade-in">
      <h2 className="text-sm font-semibold text-text-primary mb-3 flex items-center gap-2">
        <Tag className="w-4 h-4 text-accent" />
        Tags
      </h2>
      <div className="flex flex-wrap gap-2">
        {tags.map((bt) => (
          <span
            key={bt.tag.id}
            className="badge text-xs"
            style={{
              background: `${bt.tag.color || '#6366f1'}18`,
              color: bt.tag.color || '#6366f1',
              border: `1px solid ${bt.tag.color || '#6366f1'}30`,
            }}
          >
            {bt.tag.name}
          </span>
        ))}
      </div>
    </div>
  )
}

function TimelineSection({ events }: { events: TimelineEvent[] }) {
  if (!events.length) {
    return (
      <div className="card animate-fade-in">
        <h2 className="text-sm font-semibold text-text-primary mb-3 flex items-center gap-2">
          <History className="w-4 h-4 text-accent" />
          Timeline
        </h2>
        <p className="text-sm text-text-muted">No timeline events yet.</p>
      </div>
    )
  }

  // Display chronologically (oldest first)
  const sorted = [...events].sort(
    (a, b) => new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime()
  )

  return (
    <div className="card animate-fade-in">
      <h2 className="text-sm font-semibold text-text-primary mb-4 flex items-center gap-2">
        <History className="w-4 h-4 text-accent" />
        Timeline
      </h2>
      <div className="relative">
        {/* Vertical line */}
        <div className="absolute left-3.5 top-2 bottom-2 w-px bg-border" />
        <div className="space-y-4">
          {sorted.map((event, idx) => {
            const Icon = getTimelineIcon(event.type)
            const color = getTimelineColor(event.type)
            return (
              <div
                key={event.id}
                className="relative pl-10 animate-fade-in"
                style={{ animationDelay: `${idx * 50}ms` }}
              >
                {/* Icon circle */}
                <div
                  className="absolute left-0 top-0 w-7 h-7 rounded-full flex items-center justify-center"
                  style={{ background: `${color}18`, color }}
                >
                  <Icon className="w-3.5 h-3.5" />
                </div>
                <div>
                  <p className="text-sm font-medium text-text-primary">
                    {event.title}
                  </p>
                  {event.description && (
                    <p className="text-xs text-text-muted mt-0.5">
                      {event.description}
                    </p>
                  )}
                  <p className="text-[11px] text-text-muted/60 mt-0.5">
                    {formatDateTime(event.createdAt)}
                    {event.createdBy?.name && ` · by ${event.createdBy.name}`}
                  </p>
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}

function CommunicationsSection({ communications }: { communications: Communication[] }) {
  if (!communications.length) {
    return (
      <div className="card animate-fade-in">
        <h2 className="text-sm font-semibold text-text-primary mb-3 flex items-center gap-2">
          <MessageSquare className="w-4 h-4 text-accent" />
          Communication History
        </h2>
        <p className="text-sm text-text-muted">No communications recorded yet.</p>
      </div>
    )
  }

  return (
    <div className="card animate-fade-in">
      <h2 className="text-sm font-semibold text-text-primary mb-4 flex items-center gap-2">
        <MessageSquare className="w-4 h-4 text-accent" />
        Communication History
        <span className="badge-gray text-[10px] ml-auto">{communications.length}</span>
      </h2>
      <div className="space-y-3">
        {communications.map((comm, idx) => {
          const Icon = getCommIcon(comm.type)
          const color = getCommColor(comm.type)
          return (
            <div
              key={comm.id}
              className="flex items-start gap-3 p-3 rounded-lg bg-surface-hover/50 animate-fade-in"
              style={{ animationDelay: `${idx * 50}ms` }}
            >
              <div
                className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0"
                style={{ background: `${color}15`, color }}
              >
                <Icon className="w-4 h-4" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="text-xs font-medium text-text-primary capitalize">
                    {comm.type}
                  </span>
                  <span
                    className={cn(
                      'badge text-[10px]',
                      comm.direction === 'inbound' ? 'badge-green' : 'badge-blue'
                    )}
                  >
                    {comm.direction}
                  </span>
                  {comm.status !== 'completed' && (
                    <span className="badge-yellow text-[10px]">{comm.status}</span>
                  )}
                  <span className="text-[11px] text-text-muted/60 ml-auto whitespace-nowrap">
                    {formatDateTime(comm.createdAt)}
                  </span>
                </div>
                {comm.subject && (
                  <p className="text-sm text-text-primary mt-0.5 font-medium truncate">
                    {comm.subject}
                  </p>
                )}
                {comm.content && (
                  <p className="text-xs text-text-muted mt-0.5 line-clamp-2">
                    {comm.content}
                  </p>
                )}
                {comm.createdBy?.name && (
                  <p className="text-[11px] text-text-muted/50 mt-0.5">
                    by {comm.createdBy.name}
                  </p>
                )}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

function TasksSection({ tasks }: { tasks: Task[] }) {
  if (!tasks.length) {
    return (
      <div className="card animate-fade-in">
        <h2 className="text-sm font-semibold text-text-primary mb-3 flex items-center gap-2">
          <ListTodo className="w-4 h-4 text-accent" />
          Tasks
        </h2>
        <p className="text-sm text-text-muted">No tasks yet.</p>
      </div>
    )
  }

  const statusColors: Record<string, string> = {
    pending: '#f59e0b',
    in_progress: '#3b82f6',
    completed: '#22c55e',
    cancelled: '#6b7280',
  }

  return (
    <div className="card animate-fade-in">
      <h2 className="text-sm font-semibold text-text-primary mb-4 flex items-center gap-2">
        <ListTodo className="w-4 h-4 text-accent" />
        Tasks
        <span className="badge-gray text-[10px] ml-auto">{tasks.length}</span>
      </h2>
      <div className="space-y-2">
        {tasks.map((task, idx) => (
          <div
            key={task.id}
            className="flex items-start gap-3 p-3 rounded-lg bg-surface-hover/50 animate-fade-in"
            style={{ animationDelay: `${idx * 50}ms` }}
          >
            <div
              className="w-2 h-2 rounded-full mt-1.5 flex-shrink-0"
              style={{ background: statusColors[task.status] || '#6b7280' }}
            />
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 flex-wrap">
                <span
                  className={cn(
                    'text-sm font-medium',
                    task.status === 'completed'
                      ? 'text-text-muted line-through'
                      : 'text-text-primary'
                  )}
                >
                  {task.title}
                </span>
                <span
                  className="badge text-[10px]"
                  style={{
                    background: `${getTaskPriorityColor(task.priority)}18`,
                    color: getTaskPriorityColor(task.priority),
                  }}
                >
                  {task.priority}
                </span>
                <span className="badge-gray text-[10px] capitalize">
                  {task.status.replace('_', ' ')}
                </span>
              </div>
              {task.description && (
                <p className="text-xs text-text-muted mt-0.5 line-clamp-1">
                  {task.description}
                </p>
              )}
              <div className="flex items-center gap-3 mt-1">
                {task.dueDate && (
                  <span className="text-[11px] text-text-muted/60 flex items-center gap-1">
                    <Calendar className="w-3 h-3" />
                    {formatDate(task.dueDate)}
                  </span>
                )}
                {task.category && (
                  <span className="text-[11px] text-text-muted/60">
                    {task.category}
                  </span>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

function AssetsSection({ assets }: { assets: GeneratedAsset[] }) {
  if (!assets.length) {
    return (
      <div className="card animate-fade-in">
        <h2 className="text-sm font-semibold text-text-primary mb-3 flex items-center gap-2">
          <ImageIcon className="w-4 h-4 text-accent" />
          Generated Assets
        </h2>
        <p className="text-sm text-text-muted">No assets generated yet.</p>
      </div>
    )
  }

  return (
    <div className="card animate-fade-in">
      <h2 className="text-sm font-semibold text-text-primary mb-4 flex items-center gap-2">
        <ImageIcon className="w-4 h-4 text-accent" />
        Generated Assets
        <span className="badge-gray text-[10px] ml-auto">{assets.length}</span>
      </h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {assets.map((asset, idx) => {
          const Icon = getAssetIcon(asset.type)
          const statusColors: Record<string, string> = {
            generated: '#8b5cf6',
            approved: '#22c55e',
            archived: '#6b7280',
            regenerating: '#f59e0b',
          }
          return (
            <div
              key={asset.id}
              className="p-3 rounded-lg bg-surface-hover/50 border border-border/50 hover:border-border-light transition-all duration-200 animate-fade-in"
              style={{ animationDelay: `${idx * 50}ms` }}
            >
              <div className="flex items-start gap-3">
                <div
                  className="w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0"
                  style={{ background: '#8b5cf615', color: '#8b5cf6' }}
                >
                  <Icon className="w-4.5 h-4.5" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="text-sm font-medium text-text-primary truncate">
                      {asset.name}
                    </span>
                    <span
                      className="badge text-[10px]"
                      style={{
                        background: `${statusColors[asset.status] || '#6b7280'}18`,
                        color: statusColors[asset.status] || '#6b7280',
                      }}
                    >
                      {asset.status}
                    </span>
                  </div>
                  {asset.description && (
                    <p className="text-xs text-text-muted mt-0.5 line-clamp-1">
                      {asset.description}
                    </p>
                  )}
                  <div className="flex items-center gap-2 mt-1.5">
                    <span className="text-[11px] text-text-muted/60 capitalize">
                      {asset.type.replace('_', ' ')}
                    </span>
                    <span className="text-[11px] text-text-muted/40">·</span>
                    <span className="text-[11px] text-text-muted/60">
                      {formatDate(asset.createdAt)}
                    </span>
                  </div>
                  {/* Actions */}
                  <div className="flex items-center gap-1.5 mt-2">
                    {asset.url && (
                      <a
                        href={asset.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="btn-ghost btn-sm !px-2 !py-1 text-[11px]"
                      >
                        <Eye className="w-3 h-3" />
                        Preview
                      </a>
                    )}
                    {asset.filePath && (
                      <a
                        href={asset.filePath}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="btn-ghost btn-sm !px-2 !py-1 text-[11px]"
                      >
                        <Download className="w-3 h-3" />
                        Download
                      </a>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

function ProposalsSection({ proposals }: { proposals: Proposal[] }) {
  if (!proposals.length) {
    return (
      <div className="card animate-fade-in">
        <h2 className="text-sm font-semibold text-text-primary mb-3 flex items-center gap-2">
          <ScrollText className="w-4 h-4 text-accent" />
          Proposals
        </h2>
        <p className="text-sm text-text-muted">No proposals yet.</p>
      </div>
    )
  }

  return (
    <div className="card animate-fade-in">
      <h2 className="text-sm font-semibold text-text-primary mb-4 flex items-center gap-2">
        <ScrollText className="w-4 h-4 text-accent" />
        Proposals
        <span className="badge-gray text-[10px] ml-auto">{proposals.length}</span>
      </h2>
      <div className="space-y-3">
        {proposals.map((proposal, idx) => (
          <div
            key={proposal.id}
            className="flex items-start gap-3 p-3 rounded-lg bg-surface-hover/50 animate-fade-in"
            style={{ animationDelay: `${idx * 50}ms` }}
          >
            <div
              className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0"
              style={{ background: '#8b5cf615', color: '#8b5cf6' }}
            >
              <ScrollText className="w-4 h-4" />
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-sm font-medium text-text-primary">
                  {proposal.title}
                </span>
                <span
                  className="badge text-[10px]"
                  style={{
                    background: `${getProposalStatusColor(proposal.status)}18`,
                    color: getProposalStatusColor(proposal.status),
                  }}
                >
                  {proposal.status}
                </span>
              </div>
              <div className="flex items-center gap-3 mt-1 flex-wrap">
                {proposal.amount != null && (
                  <span className="text-xs font-medium text-text-primary">
                    {formatCurrency(proposal.amount)}
                  </span>
                )}
                <span className="text-[11px] text-text-muted/60">
                  Created {formatDate(proposal.createdAt)}
                </span>
                {proposal.sentAt && (
                  <span className="text-[11px] text-text-muted/60">
                    Sent {formatDate(proposal.sentAt)}
                  </span>
                )}
              </div>
              {proposal.content && (
                <p className="text-xs text-text-muted mt-1 line-clamp-2">
                  {proposal.content}
                </p>
              )}
              {proposal.filePath && (
                <a
                  href={proposal.filePath}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1 text-[11px] text-accent hover:text-accent-hover mt-1.5 transition-colors"
                >
                  <Eye className="w-3 h-3" />
                  View Document
                </a>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

function NotesSection({ notes }: { notes: Note[] }) {
  if (!notes.length) {
    return (
      <div className="card animate-fade-in">
        <h2 className="text-sm font-semibold text-text-primary mb-3 flex items-center gap-2">
          <StickyNote className="w-4 h-4 text-accent" />
          Notes
        </h2>
        <p className="text-sm text-text-muted">No notes yet.</p>
      </div>
    )
  }

  return (
    <div className="card animate-fade-in">
      <h2 className="text-sm font-semibold text-text-primary mb-4 flex items-center gap-2">
        <StickyNote className="w-4 h-4 text-accent" />
        Notes
        <span className="badge-gray text-[10px] ml-auto">{notes.length}</span>
      </h2>
      <div className="space-y-3">
        {notes.map((note, idx) => (
          <div
            key={note.id}
            className="p-3 rounded-lg bg-surface-hover/50 border border-border/50 animate-fade-in"
            style={{ animationDelay: `${idx * 50}ms` }}
          >
            <div className="flex items-start gap-2">
              <div className="w-6 h-6 rounded flex items-center justify-center bg-accent-subtle flex-shrink-0 mt-0.5">
                <StickyNote className="w-3.5 h-3.5 text-accent" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm text-text-primary whitespace-pre-wrap">
                  {note.content}
                </p>
                <div className="flex items-center gap-2 mt-1.5">
                  <span className="badge-gray text-[10px] capitalize">
                    {note.type.replace('_', ' ')}
                  </span>
                  <span className="text-[11px] text-text-muted/60">
                    {formatDateTime(note.createdAt)}
                  </span>
                  {note.createdBy?.name && (
                    <span className="text-[11px] text-text-muted/60">
                      · {note.createdBy.name}
                    </span>
                  )}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

// ─── Main Page ───────────────────────────────────────────────────────────────

export default function BusinessProfilePage() {
  const params = useParams()
  const router = useRouter()
  const id = params.id as string

  const [retryCount, setRetryCount] = useState(0)

  type FetchState = { loading: boolean; error: string | null; business: Business | null }
  type FetchAction =
    | { type: 'loading' }
    | { type: 'success'; business: Business }
    | { type: 'error'; error: string }

  function fetchReducer(state: FetchState, action: FetchAction): FetchState {
    switch (action.type) {
      case 'loading': return { loading: true, error: null, business: state.business }
      case 'success': return { loading: false, error: null, business: action.business }
      case 'error': return { loading: false, error: action.error, business: null }
    }
  }

  const [{ loading, error, business }, dispatch] = useReducer(fetchReducer, {
    loading: true,
    error: null,
    business: null,
  })

  useEffect(() => {
    if (!id) return
    dispatch({ type: 'loading' })

    fetch(`/api/businesses/${id}`)
      .then((res) => {
        if (!res.ok) {
          if (res.status === 404) throw new Error('Business not found')
          throw new Error('Failed to load business')
        }
        return res.json()
      })
      .then((data) => dispatch({ type: 'success', business: data }))
      .catch((err) => dispatch({ type: 'error', error: err.message }))
  }, [id, retryCount])

  // ── Loading state ──
  if (loading) {
    return (
      <div className="max-w-5xl mx-auto">
        <div className="mb-6">
          <button
            onClick={() => router.back()}
            className="btn-ghost btn-sm"
          >
            <ChevronLeft className="w-4 h-4" />
            Back
          </button>
        </div>
        <Skeleton />
      </div>
    )
  }

  // ── Error state ──
  if (error) {
    return (
      <div className="max-w-5xl mx-auto">
        <div className="mb-6">
          <button
            onClick={() => router.back()}
            className="btn-ghost btn-sm"
          >
            <ChevronLeft className="w-4 h-4" />
            Back
          </button>
        </div>
        <div className="card text-center py-12 animate-fade-in">
          <AlertCircle className="w-12 h-12 text-danger mx-auto mb-4" />
          <h2 className="text-lg font-semibold text-text-primary mb-2">
            {error}
          </h2>
          <p className="text-sm text-text-muted mb-6">
            The business could not be loaded. It may have been removed or you may not have access.
          </p>
          <div className="flex items-center justify-center gap-3">
            <button onClick={() => setRetryCount((c) => c + 1)} className="btn-primary">
              <Loader2 className="w-4 h-4" />
              Retry
            </button>
            <Link href="/businesses" className="btn-secondary">
              All Businesses
            </Link>
          </div>
        </div>
      </div>
    )
  }

  // ── Empty state (no data) ──
  if (!business) {
    return (
      <div className="max-w-5xl mx-auto">
        <div className="mb-6">
          <button
            onClick={() => router.back()}
            className="btn-ghost btn-sm"
          >
            <ChevronLeft className="w-4 h-4" />
            Back
          </button>
        </div>
        <div className="card text-center py-12 animate-fade-in">
          <Building2 className="w-12 h-12 text-text-muted mx-auto mb-4" />
          <h2 className="text-lg font-semibold text-text-primary mb-2">
            Business Not Found
          </h2>
          <p className="text-sm text-text-muted mb-6">
            This business doesn&apos;t exist or has been deleted.
          </p>
          <Link href="/businesses" className="btn-primary">
            All Businesses
          </Link>
        </div>
      </div>
    )
  }

  // ── Main content ──
  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Back button */}
      <div className="flex items-center justify-between animate-fade-in">
        <button
          onClick={() => router.back()}
          className="btn-ghost btn-sm"
        >
          <ChevronLeft className="w-4 h-4" />
          Back
        </button>
        <span className="text-xs text-text-muted">
          ID: {business.id.slice(0, 8)}...
        </span>
      </div>

      {/* Header */}
      <HeaderSection
        business={business}
        onEdit={() => {
          // Edit functionality placeholder — could open a modal or navigate
          router.push(`/businesses/${id}/edit`)
        }}
      />

      {/* Details + Tags Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <DetailsSection business={business} />
        </div>
        <div className="space-y-6">
          <TagsSection tags={business.tags} />
          {/* Quick stats mini-card */}
          <div className="card animate-fade-in">
            <h2 className="text-sm font-semibold text-text-primary mb-3 flex items-center gap-2">
              <Hash className="w-4 h-4 text-accent" />
              Quick Stats
            </h2>
            <div className="space-y-2.5">
              <div className="flex items-center justify-between text-sm">
                <span className="text-text-muted">Contacts</span>
                <span className="font-medium text-text-primary">{business.contacts?.length || 0}</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-text-muted">Communications</span>
                <span className="font-medium text-text-primary">{business.communications?.length || 0}</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-text-muted">Tasks</span>
                <span className="font-medium text-text-primary">{business.tasks?.length || 0}</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-text-muted">Assets</span>
                <span className="font-medium text-text-primary">{business.generatedAssets?.length || 0}</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-text-muted">Proposals</span>
                <span className="font-medium text-text-primary">{business.proposals?.length || 0}</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-text-muted">Notes</span>
                <span className="font-medium text-text-primary">{business.notes?.length || 0}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Timeline */}
      <TimelineSection events={business.timelineEvents} />

      {/* Communications */}
      <CommunicationsSection communications={business.communications} />

      {/* Tasks */}
      <TasksSection tasks={business.tasks} />

      {/* Generated Assets */}
      <AssetsSection assets={business.generatedAssets} />

      {/* Proposals */}
      <ProposalsSection proposals={business.proposals} />

      {/* Notes */}
      <NotesSection notes={business.notes} />
    </div>
  )
}