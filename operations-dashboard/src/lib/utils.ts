import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatCurrency(amount: number | null | undefined): string {
  if (amount == null) return '$0'
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount)
}

export function formatDate(date: Date | string | null | undefined): string {
  if (!date) return '—'
  const d = new Date(date)
  return d.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}

export function formatDateTime(date: Date | string | null | undefined): string {
  if (!date) return '—'
  const d = new Date(date)
  return d.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  })
}

export function formatRelativeTime(date: Date | string | null | undefined): string {
  if (!date) return '—'
  const d = new Date(date)
  const now = new Date()
  const diffMs = now.getTime() - d.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)

  if (diffMins < 1) return 'Just now'
  if (diffMins < 60) return `${diffMins}m ago`
  if (diffHours < 24) return `${diffHours}h ago`
  if (diffDays < 7) return `${diffDays}d ago`
  return formatDate(date)
}

export function getStageColor(stage: string): string {
  const colors: Record<string, string> = {
    Discovered: '#6b7280',
    Qualified: '#3b82f6',
    'Website Generated': '#8b5cf6',
    'Proposal Ready': '#f59e0b',
    'Outreach Sent': '#06b6d4',
    'Waiting For Reply': '#f97316',
    Interested: '#10b981',
    'Meeting Scheduled': '#6366f1',
    'Quotation Sent': '#ec4899',
    Negotiation: '#f43f5e',
    Won: '#22c55e',
    Lost: '#ef4444',
    Archived: '#6b7280',
  }
  return colors[stage] || '#6b7280'
}

export function getScoreLabel(score: number): { label: string; color: string } {
  if (score >= 80) return { label: 'Very Hot', color: '#ef4444' }
  if (score >= 60) return { label: 'Hot', color: '#f97316' }
  if (score >= 40) return { label: 'Warm', color: '#f59e0b' }
  return { label: 'Cold', color: '#3b82f6' }
}

export function getAgentStatusColor(status: string): string {
  switch (status) {
    case 'running': return '#22c55e'
    case 'busy': return '#eab308'
    case 'idle': return '#6b7280'
    case 'paused': return '#f59e0b'
    case 'stopped': return '#ef4444'
    default: return '#6b7280'
  }
}

export function getAgentStatusIcon(status: string): string {
  switch (status) {
    case 'running': return 'bg-green-500'
    case 'busy': return 'bg-yellow-500'
    case 'idle': return 'bg-gray-500'
    case 'paused': return 'bg-yellow-400'
    case 'stopped': return 'bg-red-500'
    default: return 'bg-gray-500'
  }
}

export const PIPELINE_STAGES = [
  'Discovered',
  'Qualified',
  'Website Generated',
  'Proposal Ready',
  'Outreach Sent',
  'Waiting For Reply',
  'Interested',
  'Meeting Scheduled',
  'Quotation Sent',
  'Negotiation',
  'Won',
  'Lost',
  'Archived',
] as const

export const STATS_ITEMS = [
  { key: 'totalBusinesses', label: 'Total Businesses Found', icon: 'Building2', color: '#3b82f6' },
  { key: 'websitesGenerated', label: 'Websites Generated', icon: 'Globe', color: '#8b5cf6' },
  { key: 'pitchDecksGenerated', label: 'Pitch Decks Generated', icon: 'FileText', color: '#ec4899' },
  { key: 'emailsSent', label: 'Emails Sent', icon: 'Send', color: '#06b6d4' },
  { key: 'responsesReceived', label: 'Responses Received', icon: 'MessageSquare', color: '#10b981' },
  { key: 'meetingsScheduled', label: 'Meetings Scheduled', icon: 'Calendar', color: '#6366f1' },
  { key: 'proposalsAccepted', label: 'Proposals Accepted', icon: 'CheckCircle', color: '#22c55e' },
  { key: 'revenueClosed', label: 'Revenue Closed', icon: 'DollarSign', color: '#f59e0b' },
  { key: 'conversionRate', label: 'Conversion Rate', icon: 'TrendingUp', color: '#f43f5e' },
] as const