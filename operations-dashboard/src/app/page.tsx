'use client'

import { useState, useEffect, useCallback, useRef } from 'react'
import {
  Building2, Globe, FileText, Send, MessageSquare,
  Calendar, CheckCircle, DollarSign, TrendingUp, Activity,
  ArrowUp, ArrowDown, AlertCircle, Loader2, RefreshCw,
  Users, Mail, MousePointerClick, Target,
} from 'lucide-react'
import {
  LineChart, Line, BarChart, Bar, AreaChart, Area,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell,
} from 'recharts'
import { cn, formatCurrency, formatRelativeTime, getStageColor } from '@/lib/utils'

// ─── Types ──────────────────────────────────────────────────────────────────

interface StageCount {
  stage: string
  count: number
}

interface ActivityItem {
  id: string
  type: string
  title: string
  description: string | null
  metadata: string | null
  createdAt: string
}

interface DashboardData {
  totalBusinesses: number
  websitesGenerated: number
  pitchDecksGenerated: number
  emailsSent: number
  responsesReceived: number
  meetingsScheduled: number
  proposalsAccepted: number
  revenueClosed: number
  conversionRate: number
  todayActivity: number
  overdueFollowUps: number
  weeklyLabels: string[]
  weeklyLeads: number[]
  weeklyEmails: number[]
  weeklyReplies: number[]
  weeklyConversions: number[]
  weeklyRevenue: number[]
  stageDistribution: StageCount[]
  recentActivity: ActivityItem[]
}

// ─── Stat Card Config ────────────────────────────────────────────────────────

interface StatCardConfig {
  key: keyof DashboardData
  label: string
  icon: React.ElementType
  color: string
  format?: 'number' | 'currency' | 'percent'
}

const STAT_CARDS: StatCardConfig[] = [
  { key: 'totalBusinesses', label: 'Total Businesses', icon: Building2, color: '#3b82f6' },
  { key: 'websitesGenerated', label: 'Websites Generated', icon: Globe, color: '#8b5cf6' },
  { key: 'pitchDecksGenerated', label: 'Pitch Decks', icon: FileText, color: '#ec4899' },
  { key: 'emailsSent', label: 'Emails Sent', icon: Send, color: '#06b6d4' },
  { key: 'responsesReceived', label: 'Responses Received', icon: MessageSquare, color: '#10b981' },
  { key: 'meetingsScheduled', label: 'Meetings Scheduled', icon: Calendar, color: '#6366f1' },
  { key: 'proposalsAccepted', label: 'Proposals Accepted', icon: CheckCircle, color: '#22c55e' },
  { key: 'revenueClosed', label: 'Revenue Closed', icon: DollarSign, color: '#f59e0b', format: 'currency' },
  { key: 'conversionRate', label: 'Conversion Rate', icon: TrendingUp, color: '#f43f5e', format: 'percent' },
]

// ─── Activity Icon Map ──────────────────────────────────────────────────────

function getActivityIcon(type: string) {
  switch (type) {
    case 'lead_found': return Users
    case 'website_generated': return Globe
    case 'email_sent': return Send
    case 'proposal_created': return FileText
    case 'lead_updated': return TrendingUp
    case 'status_changed': return Target
    case 'agent_started': return Activity
    case 'agent_stopped': return Activity
    case 'skill_loaded': return Activity
    case 'skill_failed': return AlertCircle
    default: return Activity
  }
}

function getActivityColor(type: string) {
  switch (type) {
    case 'lead_found': return '#3b82f6'
    case 'website_generated': return '#8b5cf6'
    case 'email_sent': return '#06b6d4'
    case 'proposal_created': return '#ec4899'
    case 'lead_updated': return '#f59e0b'
    case 'status_changed': return '#6366f1'
    case 'agent_started': return '#22c55e'
    case 'agent_stopped': return '#ef4444'
    case 'skill_loaded': return '#10b981'
    case 'skill_failed': return '#ef4444'
    default: return '#71717a'
  }
}

// ─── Custom Tooltip ─────────────────────────────────────────────────────────

const ChartTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null
  return (
    <div className="bg-surface border border-border rounded-lg px-3 py-2 shadow-xl text-xs">
      <p className="text-text-muted mb-1">{label}</p>
      {payload.map((entry: any, i: number) => (
        <p key={i} style={{ color: entry.color }} className="font-medium">
          {entry.name}: {typeof entry.value === 'number' ? entry.value.toLocaleString() : entry.value}
        </p>
      ))}
    </div>
  )
}

// ─── Skeleton ───────────────────────────────────────────────────────────────

function DashboardSkeleton() {
  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header skeleton */}
      <div className="flex items-center justify-between">
        <div>
          <div className="skeleton h-7 w-48 mb-2" />
          <div className="skeleton h-4 w-64" />
        </div>
        <div className="skeleton h-8 w-28 rounded-lg" />
      </div>

      {/* Stats cards skeleton */}
      <div className="stats-grid">
        {Array.from({ length: 9 }).map((_, i) => (
          <div key={i} className="card space-y-3">
            <div className="flex items-center justify-between">
              <div className="skeleton h-9 w-9 rounded-lg" />
              <div className="skeleton h-5 w-16 rounded-md" />
            </div>
            <div className="skeleton h-8 w-24" />
            <div className="skeleton h-3 w-32" />
          </div>
        ))}
      </div>

      {/* Charts skeleton */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="chart-container space-y-4">
          <div className="skeleton h-5 w-36" />
          <div className="skeleton h-[300px] w-full rounded-lg" />
        </div>
        <div className="chart-container space-y-4">
          <div className="skeleton h-5 w-36" />
          <div className="skeleton h-[300px] w-full rounded-lg" />
        </div>
        <div className="chart-container space-y-4">
          <div className="skeleton h-5 w-36" />
          <div className="skeleton h-[300px] w-full rounded-lg" />
        </div>
        <div className="chart-container space-y-4">
          <div className="skeleton h-5 w-36" />
          <div className="space-y-3">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="flex items-start gap-3">
                <div className="skeleton h-8 w-8 rounded-lg flex-shrink-0" />
                <div className="flex-1 space-y-1.5">
                  <div className="skeleton h-3.5 w-48" />
                  <div className="skeleton h-3 w-32" />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

// ─── Stat Card ──────────────────────────────────────────────────────────────

function StatCard({ config, value, loading }: {
  config: StatCardConfig
  value: number
  loading: boolean
}) {
  const Icon = config.icon
  const color = config.color

  let displayValue: string
  if (loading) {
    displayValue = '—'
  } else {
    switch (config.format) {
      case 'currency':
        displayValue = formatCurrency(value)
        break
      case 'percent':
        displayValue = `${value}%`
        break
      default:
        displayValue = value.toLocaleString()
    }
  }

  return (
    <div className="card hover:border-border-light transition-all duration-200 group">
      <div className="flex items-center justify-between mb-3">
        <div
          className="w-9 h-9 rounded-lg flex items-center justify-center transition-transform duration-200 group-hover:scale-110"
          style={{ backgroundColor: `${color}15`, color }}
        >
          <Icon className="w-4 h-4" />
        </div>
        {loading ? (
          <div className="skeleton h-5 w-14 rounded-md" />
        ) : (
          <span
            className="badge text-[10px] font-medium"
            style={{ backgroundColor: `${color}10`, color }}
          >
            {config.format === 'percent' ? 'Rate' : 'Total'}
          </span>
        )}
      </div>
      {loading ? (
        <div className="skeleton h-7 w-20 mb-2" />
      ) : (
        <div className="text-2xl font-bold text-text-primary mb-1 font-mono tracking-tight">
          {displayValue}
        </div>
      )}
      {loading ? (
        <div className="skeleton h-3 w-28" />
      ) : (
        <div className="text-xs text-text-muted">{config.label}</div>
      )}
    </div>
  )
}

// ─── Activity Feed ──────────────────────────────────────────────────────────

function ActivityFeed({ activities, loading }: {
  activities: ActivityItem[]
  loading: boolean
}) {
  if (loading) {
    return (
      <div className="chart-container">
        <h3 className="text-sm font-semibold text-text-primary mb-4">Recent Activity</h3>
        <div className="space-y-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="flex items-start gap-3">
              <div className="skeleton h-8 w-8 rounded-lg" />
              <div className="flex-1 space-y-1.5">
                <div className="skeleton h-3.5 w-48" />
                <div className="skeleton h-3 w-32" />
              </div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="chart-container">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-text-primary">Recent Activity</h3>
        <span className="text-[10px] text-text-muted font-mono">
          Latest {activities.length}
        </span>
      </div>
      <div className="space-y-1">
        {activities.length === 0 ? (
          <div className="py-8 text-center text-sm text-text-muted">
            No recent activity
          </div>
        ) : (
          activities.map((item) => {
            const Icon = getActivityIcon(item.type)
            const color = getActivityColor(item.type)
            return (
              <div
                key={item.id}
                className="flex items-start gap-3 p-2.5 rounded-lg hover:bg-surface-hover transition-colors duration-150"
              >
                <div
                  className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5"
                  style={{ backgroundColor: `${color}12`, color }}
                >
                  <Icon className="w-3.5 h-3.5" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-text-primary truncate">{item.title}</p>
                  {item.description && (
                    <p className="text-xs text-text-muted mt-0.5 line-clamp-2">{item.description}</p>
                  )}
                  <p className="text-[10px] text-text-muted/60 mt-1 font-mono">
                    {formatRelativeTime(item.createdAt)}
                  </p>
                </div>
              </div>
            )
          })
        )}
      </div>
    </div>
  )
}

// ─── Stage Distribution ─────────────────────────────────────────────────────

const STAGE_COLORS = [
  '#6b7280', '#3b82f6', '#8b5cf6', '#f59e0b', '#06b6d4',
  '#f97316', '#10b981', '#6366f1', '#ec4899', '#f43f5e',
  '#22c55e', '#ef4444', '#6b7280',
]

function StageDistributionChart({ stages, loading }: {
  stages: StageCount[]
  loading: boolean
}) {
  if (loading) {
    return (
      <div className="chart-container">
        <div className="skeleton h-5 w-36 mb-4" />
        <div className="skeleton h-[280px] w-full rounded-lg" />
      </div>
    )
  }

  const data = stages
    .filter(s => s.count > 0)
    .sort((a, b) => b.count - a.count)

  return (
    <div className="chart-container">
      <h3 className="text-sm font-semibold text-text-primary mb-4">Pipeline Stage Distribution</h3>
      {data.length === 0 ? (
        <div className="h-[280px] flex items-center justify-center text-sm text-text-muted">
          No data yet
        </div>
      ) : (
        <div className="flex flex-col sm:flex-row items-center gap-6">
          <div className="flex-shrink-0">
            <ResponsiveContainer width={200} height={200}>
              <PieChart>
                <Pie
                  data={data}
                  cx="50%"
                  cy="50%"
                  innerRadius={55}
                  outerRadius={85}
                  paddingAngle={2}
                  dataKey="count"
                  nameKey="stage"
                >
                  {data.map((_, i) => (
                    <Cell key={i} fill={STAGE_COLORS[i % STAGE_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip content={<ChartTooltip />} />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="flex-1 space-y-1.5 w-full">
            {data.map((s, i) => (
              <div key={s.stage} className="flex items-center gap-2 text-xs">
                <div
                  className="w-2 h-2 rounded-full flex-shrink-0"
                  style={{ backgroundColor: STAGE_COLORS[i % STAGE_COLORS.length] }}
                />
                <span className="text-text-secondary flex-1 truncate">{s.stage}</span>
                <span className="text-text-primary font-mono font-medium">{s.count}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

// ─── Weekly Trends Chart ────────────────────────────────────────────────────

function WeeklyTrendsChart({ labels, leads, emails, replies, loading }: {
  labels: string[]
  leads: number[]
  emails: number[]
  replies: number[]
  loading: boolean
}) {
  if (loading) {
    return (
      <div className="chart-container">
        <div className="skeleton h-5 w-36 mb-4" />
        <div className="skeleton h-[300px] w-full rounded-lg" />
      </div>
    )
  }

  const data = labels.map((label, i) => ({
    day: label,
    Leads: leads[i] || 0,
    Emails: emails[i] || 0,
    Replies: replies[i] || 0,
  }))

  return (
    <div className="chart-container">
      <h3 className="text-sm font-semibold text-text-primary mb-4">Weekly Trends</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data} margin={{ top: 5, right: 10, left: -10, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
          <XAxis
            dataKey="day"
            tick={{ fill: '#71717a', fontSize: 11 }}
            axisLine={{ stroke: '#27272a' }}
            tickLine={false}
          />
          <YAxis
            tick={{ fill: '#71717a', fontSize: 11 }}
            axisLine={false}
            tickLine={false}
            allowDecimals={false}
          />
          <Tooltip content={<ChartTooltip />} />
          <Line
            type="monotone"
            dataKey="Leads"
            stroke="#3b82f6"
            strokeWidth={2}
            dot={{ fill: '#3b82f6', r: 3 }}
            activeDot={{ r: 5 }}
          />
          <Line
            type="monotone"
            dataKey="Emails"
            stroke="#06b6d4"
            strokeWidth={2}
            dot={{ fill: '#06b6d4', r: 3 }}
            activeDot={{ r: 5 }}
          />
          <Line
            type="monotone"
            dataKey="Replies"
            stroke="#10b981"
            strokeWidth={2}
            dot={{ fill: '#10b981', r: 3 }}
            activeDot={{ r: 5 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

// ─── Revenue Chart ──────────────────────────────────────────────────────────

function RevenueChart({ labels, revenue, loading }: {
  labels: string[]
  revenue: number[]
  loading: boolean
}) {
  if (loading) {
    return (
      <div className="chart-container">
        <div className="skeleton h-5 w-36 mb-4" />
        <div className="skeleton h-[300px] w-full rounded-lg" />
      </div>
    )
  }

  const data = labels.map((label, i) => ({
    day: label,
    Revenue: revenue[i] || 0,
  }))

  return (
    <div className="chart-container">
      <h3 className="text-sm font-semibold text-text-primary mb-4">Weekly Revenue</h3>
      <ResponsiveContainer width="100%" height={300}>
        <AreaChart data={data} margin={{ top: 5, right: 10, left: -10, bottom: 5 }}>
          <defs>
            <linearGradient id="revenueGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.25} />
              <stop offset="95%" stopColor="#f59e0b" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
          <XAxis
            dataKey="day"
            tick={{ fill: '#71717a', fontSize: 11 }}
            axisLine={{ stroke: '#27272a' }}
            tickLine={false}
          />
          <YAxis
            tick={{ fill: '#71717a', fontSize: 11 }}
            axisLine={false}
            tickLine={false}
            tickFormatter={(v) => `$${v}`}
          />
          <Tooltip content={<ChartTooltip />} />
          <Area
            type="monotone"
            dataKey="Revenue"
            stroke="#f59e0b"
            strokeWidth={2}
            fill="url(#revenueGradient)"
            dot={{ fill: '#f59e0b', r: 3 }}
            activeDot={{ r: 5 }}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}

// ─── Conversion Chart ───────────────────────────────────────────────────────

function ConversionChart({ labels, conversions, loading }: {
  labels: string[]
  conversions: number[]
  loading: boolean
}) {
  if (loading) {
    return (
      <div className="chart-container">
        <div className="skeleton h-5 w-36 mb-4" />
        <div className="skeleton h-[300px] w-full rounded-lg" />
      </div>
    )
  }

  const data = labels.map((label, i) => ({
    day: label,
    Conversions: conversions[i] || 0,
  }))

  return (
    <div className="chart-container">
      <h3 className="text-sm font-semibold text-text-primary mb-4">Weekly Conversions</h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data} margin={{ top: 5, right: 10, left: -10, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
          <XAxis
            dataKey="day"
            tick={{ fill: '#71717a', fontSize: 11 }}
            axisLine={{ stroke: '#27272a' }}
            tickLine={false}
          />
          <YAxis
            tick={{ fill: '#71717a', fontSize: 11 }}
            axisLine={false}
            tickLine={false}
            allowDecimals={false}
          />
          <Tooltip content={<ChartTooltip />} />
          <Bar dataKey="Conversions" fill="#22c55e" radius={[4, 4, 0, 0]} maxBarSize={32} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

// ─── Summary Bar ────────────────────────────────────────────────────────────

function SummaryBar({ data, loading }: {
  data: DashboardData | null
  loading: boolean
}) {
  const items = [
    { label: 'Today Activity', value: data?.todayActivity ?? 0, icon: Activity, color: '#6366f1' },
    { label: 'Overdue Follow-ups', value: data?.overdueFollowUps ?? 0, icon: AlertCircle, color: '#ef4444' },
    { label: 'Weekly Activity', value: data ? (data.weeklyLeads?.reduce((a, b) => a + b, 0) ?? 0) : 0, icon: TrendingUp, color: '#10b981' },
  ]

  return (
    <div className="flex flex-wrap gap-4">
      {items.map((item) => {
        const Icon = item.icon
        const isWarning = item.label === 'Overdue Follow-ups' && item.value > 0
        return (
          <div
            key={item.label}
            className={cn(
              'flex items-center gap-3 px-4 py-2.5 rounded-lg border text-xs',
              isWarning
                ? 'bg-danger/5 border-danger/20 text-danger'
                : 'bg-surface border-border text-text-secondary'
            )}
          >
            <Icon className="w-3.5 h-3.5" />
            {loading ? (
              <div className="skeleton h-3.5 w-16" />
            ) : (
              <>
                <span className="font-medium">{item.value}</span>
                <span className="text-text-muted">{item.label}</span>
              </>
            )}
          </div>
        )
      })}
    </div>
  )
}

// ─── Main Dashboard Page ────────────────────────────────────────────────────

export default function DashboardPage() {
  const [data, setData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [lastRefreshed, setLastRefreshed] = useState<Date | null>(null)
  const intervalRef = useRef<NodeJS.Timeout | null>(null)

  const fetchData = useCallback(async (showLoader = false) => {
    if (showLoader) setLoading(true)
    try {
      const res = await fetch('/api/stats')
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const json = await res.json()
      setData(json)
      setError(null)
      setLastRefreshed(new Date())
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load dashboard data')
    } finally {
      setLoading(false)
    }
  }, [])

  // Initial load
  useEffect(() => {
    // eslint-disable-next-line react-hooks/exhaustive-deps
    fetchData(true)
  }, [fetchData])

  // Auto-refresh every 30 seconds
  useEffect(() => {
    // eslint-disable-next-line react-hooks/exhaustive-deps
    const interval = setInterval(() => fetchData(), 30000)
    return () => clearInterval(interval)
  }, [fetchData])

  // Manual refresh
  const handleRefresh = () => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current)
    }
    setLoading(() => true)
    fetchData()
    intervalRef.current = setInterval(() => fetchData(), 30000)
  }

  // ── Render ──

  if (loading && !data) {
    return <DashboardSkeleton />
  }

  if (error && !data) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4 animate-fade-in">
        <div className="w-16 h-16 rounded-2xl bg-danger/10 flex items-center justify-center">
          <AlertCircle className="w-8 h-8 text-danger" />
        </div>
        <h2 className="text-lg font-semibold text-text-primary">Failed to load dashboard</h2>
        <p className="text-sm text-text-muted max-w-md text-center">{error}</p>
        <button onClick={handleRefresh} className="btn-primary mt-2">
          <RefreshCw className="w-4 h-4" /> Retry
        </button>
      </div>
    )
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* ── Header ── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-text-primary">Dashboard</h1>
          <p className="text-sm text-text-muted mt-0.5">
            Overview of your agency operations and pipeline performance
          </p>
        </div>
        <div className="flex items-center gap-3">
          <SummaryBar data={data} loading={loading} />
          <button
            onClick={handleRefresh}
            disabled={loading}
            className="btn-ghost btn-sm"
            title="Refresh data"
          >
            <RefreshCw className={cn('w-3.5 h-3.5', loading && 'animate-spin')} />
            <span className="hidden sm:inline">
              {lastRefreshed
                ? formatRelativeTime(lastRefreshed)
                : 'Refresh'}
            </span>
          </button>
        </div>
      </div>

      {/* ── Stats Cards ── */}
      <div className="stats-grid">
        {STAT_CARDS.map((card) => (
          <StatCard
            key={card.key}
            config={card}
            value={data ? (data[card.key] as number) : 0}
            loading={loading}
          />
        ))}
      </div>

      {/* ── Charts Row 1 ── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <WeeklyTrendsChart
          labels={data?.weeklyLabels ?? []}
          leads={data?.weeklyLeads ?? []}
          emails={data?.weeklyEmails ?? []}
          replies={data?.weeklyReplies ?? []}
          loading={loading}
        />
        <RevenueChart
          labels={data?.weeklyLabels ?? []}
          revenue={data?.weeklyRevenue ?? []}
          loading={loading}
        />
      </div>

      {/* ── Charts Row 2 ── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ConversionChart
          labels={data?.weeklyLabels ?? []}
          conversions={data?.weeklyConversions ?? []}
          loading={loading}
        />
        <StageDistributionChart
          stages={data?.stageDistribution ?? []}
          loading={loading}
        />
      </div>

      {/* ── Activity Feed ── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ActivityFeed
          activities={data?.recentActivity ?? []}
          loading={loading}
        />
        {/* Quick stats panel */}
        <div className="chart-container">
          <h3 className="text-sm font-semibold text-text-primary mb-4">Quick Overview</h3>
          {loading ? (
            <div className="space-y-3">
              {Array.from({ length: 5 }).map((_, i) => (
                <div key={i} className="flex items-center justify-between p-2.5">
                  <div className="skeleton h-4 w-32" />
                  <div className="skeleton h-4 w-16" />
                </div>
              ))}
            </div>
          ) : (
            <div className="space-y-1">
              {[
                { label: 'Total Businesses', value: data?.totalBusinesses ?? 0, color: '#3b82f6' },
                { label: 'Emails Sent', value: data?.emailsSent ?? 0, color: '#06b6d4' },
                { label: 'Responses Received', value: data?.responsesReceived ?? 0, color: '#10b981' },
                { label: 'Meetings Scheduled', value: data?.meetingsScheduled ?? 0, color: '#6366f1' },
                { label: 'Proposals Accepted', value: data?.proposalsAccepted ?? 0, color: '#22c55e' },
                { label: 'Conversion Rate', value: `${data?.conversionRate ?? 0}%`, color: '#f43f5e' },
                { label: 'Revenue Closed', value: formatCurrency(data?.revenueClosed ?? 0), color: '#f59e0b' },
              ].map((item) => (
                <div
                  key={item.label}
                  className="flex items-center justify-between p-2.5 rounded-lg hover:bg-surface-hover transition-colors"
                >
                  <span className="text-sm text-text-secondary">{item.label}</span>
                  <span
                    className="text-sm font-semibold font-mono"
                    style={{ color: item.color }}
                  >
                    {item.value}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}