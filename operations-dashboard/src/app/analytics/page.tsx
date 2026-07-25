'use client'

import { useState, useEffect } from 'react'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, PieChart, Pie, Cell, AreaChart, Area,
} from 'recharts'
import { formatCurrency, getStageColor } from '@/lib/utils'
import { TrendingUp, PieChartIcon, BarChart3, DollarSign, Funnel } from 'lucide-react'

// ─── Types ───

interface StageDist {
  stage: string
  count: number
}

interface IndustryDist {
  industry: string
  count: number
}

interface ScoreBucket {
  range: string
  count: number
}

interface StatsData {
  totalBusinesses: number
  websitesGenerated: number
  emailsSent: number
  responsesReceived: number
  meetingsScheduled: number
  proposalsAccepted: number
  revenueClosed: number
  conversionRate: number
  weeklyLabels: string[]
  weeklyLeads: number[]
  weeklyEmails: number[]
  weeklyReplies: number[]
  weeklyConversions: number[]
  weeklyRevenue: number[]
  stageDistribution: StageDist[]
  industryDistribution: IndustryDist[]
  leadScoreDistribution: ScoreBucket[]
}

// ─── Helpers ───

const INDUSTRY_COLORS = [
  '#6366f1', '#f59e0b', '#ef4444', '#22c55e', '#3b82f6',
  '#ec4899', '#14b8a6', '#f97316', '#8b5cf6', '#06b6d4',
  '#84cc16', '#d946ef', '#0ea5e9', '#eab308', '#64748b',
]

const SCORE_COLORS = ['#ef4444', '#f97316', '#f59e0b', '#22c55e', '#6366f1']

const FUNNEL_STAGES = [
  { key: 'Discovered', label: 'Discovered' },
  { key: 'Qualified', label: 'Qualified' },
  { key: 'Website Generated', label: 'Website' },
  { key: 'Proposal Ready', label: 'Proposal' },
  { key: 'Outreach Sent', label: 'Outreach' },
  { key: 'Interested', label: 'Interested' },
  { key: 'Meeting Scheduled', label: 'Meeting' },
  { key: 'Won', label: 'Won' },
]

// ─── Custom Tooltip ───

interface CustomTooltipProps {
  active: boolean
  payload: Array<{ color: string; name: string; value: number | string }>
  label: string
}

const CustomTooltip = ({ active, payload, label }: CustomTooltipProps) => {
  if (!active || !payload?.length) return null
  return (
    <div className="bg-surface border border-border rounded-lg px-3 py-2 shadow-xl text-xs">
      <p className="text-text-muted mb-1">{label}</p>
      {payload.map((entry, i) => (
        <p key={i} style={{ color: entry.color }} className="font-medium">
          {entry.name}: {typeof entry.value === 'number' ? entry.value.toLocaleString() : entry.value}
        </p>
      ))}
    </div>
  )
}

// ─── Conversion Funnel ───

function ConversionFunnel({ stageDistribution }: { stageDistribution: StageDist[] }) {
  const stageMap = new Map(stageDistribution.map(s => [s.stage, s.count]))
  const maxCount = Math.max(...FUNNEL_STAGES.map(s => stageMap.get(s.key) || 0), 1)

  return (
    <div className="space-y-2">
      <h3 className="text-sm font-medium text-text-primary mb-3">Conversion Funnel</h3>
      <div className="space-y-1.5">
        {FUNNEL_STAGES.map((stage, _i) => {
          const count = stageMap.get(stage.key) || 0
          const width = maxCount > 0 ? (count / maxCount) * 100 : 0
          const color = getStageColor(stage.key)
          return (
            <div key={stage.key} className="flex items-center gap-3">
              <span className="text-xs text-text-muted w-20 text-right shrink-0">{stage.label}</span>
              <div className="flex-1 h-7 bg-surface-active rounded relative overflow-hidden">
                <div
                  className="h-full rounded transition-all duration-700 ease-out flex items-center justify-end pr-2"
                  style={{
                    width: `${width}%`,
                    background: `linear-gradient(90deg, ${color}33, ${color})`,
                    minWidth: count > 0 ? '2rem' : '0',
                  }}
                >
                  <span className="text-[11px] font-semibold text-white drop-shadow-sm">
                    {count}
                  </span>
                </div>
              </div>
              <span className="text-xs text-text-muted w-8 shrink-0">
                {maxCount > 0 ? `${Math.round((count / maxCount) * 100)}%` : '0%'}
              </span>
            </div>
          )
        })}
      </div>
    </div>
  )
}

// ─── Skeleton ───

function ChartSkeleton() {
  return (
    <div className="chart-container animate-pulse">
      <div className="h-4 w-32 bg-surface-active rounded mb-4" />
      <div className="h-48 bg-surface-active rounded" />
    </div>
  )
}

// ─── Main Page ───

export default function AnalyticsPage() {
  const [data, setData] = useState<StatsData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetch('/api/stats')
      .then(res => {
        if (!res.ok) throw new Error('Failed to fetch')
        return res.json()
      })
      .then((json: StatsData) => {
        setData(json)
        setLoading(false)
      })
      .catch(err => {
        setError(err.message)
        setLoading(false)
      })
  }, [])

  // Build weekly revenue data for area chart
  const weeklyRevenueData = data?.weeklyLabels.map((label, i) => ({
    day: label,
    revenue: data.weeklyRevenue[i],
    leads: data.weeklyLeads[i],
    emails: data.weeklyEmails[i],
  })) ?? []

  const stageData = data?.stageDistribution ?? []

  const industryData = data?.industryDistribution ?? []

  const scoreData = data?.leadScoreDistribution ?? []

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <p className="text-danger text-lg font-medium mb-2">Failed to load analytics</p>
          <p className="text-text-secondary text-sm">{error}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">Analytics</h1>
          <p className="text-sm text-text-muted mt-0.5">Key metrics and performance charts</p>
        </div>
      </div>

      {/* Summary stat cards */}
      {loading ? (
        <div className="stats-grid">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="card animate-pulse">
              <div className="h-3 w-20 bg-surface-active rounded mb-3" />
              <div className="h-7 w-16 bg-surface-active rounded" />
            </div>
          ))}
        </div>
      ) : (
        <div className="stats-grid">
          {[
            { label: 'Total Businesses', value: data?.totalBusinesses ?? 0, icon: BarChart3, color: 'text-accent' },
            { label: 'Revenue Closed', value: formatCurrency(data?.revenueClosed ?? 0), icon: DollarSign, color: 'text-success' },
            { label: 'Meetings Scheduled', value: data?.meetingsScheduled ?? 0, icon: TrendingUp, color: 'text-info' },
            { label: 'Conversion Rate', value: `${data?.conversionRate ?? 0}%`, icon: TrendingUp, color: 'text-warning' },
          ].map((stat, i) => (
            <div key={i} className="card animate-scale-in" style={{ animationDelay: `${i * 50}ms` }}>
              <div className="flex items-center justify-between mb-2">
                <span className="label">{stat.label}</span>
                <stat.icon className={`w-4 h-4 ${stat.color}`} />
              </div>
              <p className="text-2xl font-bold text-text-primary">{stat.value}</p>
            </div>
          ))}
        </div>
      )}

      {/* Charts grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 1. Businesses per Industry (PieChart) */}
        {loading ? (
          <ChartSkeleton />
        ) : (
          <div className="chart-container animate-scale-in">
            <h3 className="text-sm font-medium text-text-primary mb-4 flex items-center gap-2">
              <PieChartIcon className="w-4 h-4 text-accent" />
              Businesses per Industry
            </h3>
            {industryData.length === 0 ? (
              <p className="text-text-muted text-sm text-center py-12">No industry data available</p>
            ) : (
              <ResponsiveContainer width="100%" height={280}>
                <PieChart>
                  <Pie
                    data={industryData}
                    dataKey="count"
                    nameKey="industry"
                    cx="50%"
                    cy="50%"
                    outerRadius={100}
                    innerRadius={55}
                    paddingAngle={3}
                    animationBegin={100}
                    animationDuration={800}
                    animationEasing="ease-out"
                  >
                    {industryData.map((_, i) => (
                      <Cell key={i} fill={INDUSTRY_COLORS[i % INDUSTRY_COLORS.length]} stroke="transparent" />
                    ))}
                  </Pie>
                  <Tooltip content={<CustomTooltip />} />
                </PieChart>
              </ResponsiveContainer>
            )}
            {/* Legend */}
            <div className="flex flex-wrap gap-3 mt-3">
              {industryData.map((item, i) => (
                <div key={item.industry} className="flex items-center gap-1.5">
                  <span
                    className="w-2.5 h-2.5 rounded-full"
                    style={{ background: INDUSTRY_COLORS[i % INDUSTRY_COLORS.length] }}
                  />
                  <span className="text-xs text-text-secondary">{item.industry}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 2. Lead Score Distribution (BarChart) */}
        {loading ? (
          <ChartSkeleton />
        ) : (
          <div className="chart-container animate-scale-in" style={{ animationDelay: '100ms' }}>
            <h3 className="text-sm font-medium text-text-primary mb-4 flex items-center gap-2">
              <BarChart3 className="w-4 h-4 text-warning" />
              Lead Score Distribution
            </h3>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={scoreData} margin={{ top: 5, right: 10, left: -10, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
                <XAxis dataKey="range" tick={{ fill: '#a1a1aa', fontSize: 11 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: '#a1a1aa', fontSize: 11 }} axisLine={false} tickLine={false} />
                <Tooltip content={<CustomTooltip />} />
                <Bar
                  dataKey="count"
                  name="Leads"
                  radius={[4, 4, 0, 0]}
                  animationBegin={200}
                  animationDuration={800}
                  animationEasing="ease-out"
                >
                  {scoreData.map((_, i) => (
                    <Cell key={i} fill={SCORE_COLORS[i]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* 3. Weekly Revenue (AreaChart) */}
        {loading ? (
          <ChartSkeleton />
        ) : (
          <div className="chart-container animate-scale-in" style={{ animationDelay: '200ms' }}>
            <h3 className="text-sm font-medium text-text-primary mb-4 flex items-center gap-2">
              <DollarSign className="w-4 h-4 text-success" />
              Weekly Revenue
            </h3>
            <ResponsiveContainer width="100%" height={280}>
              <AreaChart data={weeklyRevenueData} margin={{ top: 5, right: 10, left: -10, bottom: 5 }}>
                <defs>
                  <linearGradient id="revenueGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#22c55e" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#22c55e" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
                <XAxis dataKey="day" tick={{ fill: '#a1a1aa', fontSize: 11 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: '#a1a1aa', fontSize: 11 }} axisLine={false} tickLine={false} tickFormatter={(v) => `$${v}`} />
                <Tooltip content={<CustomTooltip />} />
                <Area
                  type="monotone"
                  dataKey="revenue"
                  name="Revenue"
                  stroke="#22c55e"
                  strokeWidth={2}
                  fill="url(#revenueGradient)"
                  animationBegin={300}
                  animationDuration={1000}
                  animationEasing="ease-out"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* 4. Pipeline Stage Distribution (BarChart) */}
        {loading ? (
          <ChartSkeleton />
        ) : (
          <div className="chart-container animate-scale-in" style={{ animationDelay: '300ms' }}>
            <h3 className="text-sm font-medium text-text-primary mb-4 flex items-center gap-2">
              <BarChart3 className="w-4 h-4 text-accent" />
              Pipeline Stage Distribution
            </h3>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={stageData} layout="vertical" margin={{ top: 5, right: 10, left: 10, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#27272a" horizontal={false} />
                <XAxis type="number" tick={{ fill: '#a1a1aa', fontSize: 11 }} axisLine={false} tickLine={false} />
                <YAxis
                  type="category"
                  dataKey="stage"
                  tick={{ fill: '#a1a1aa', fontSize: 10 }}
                  axisLine={false}
                  tickLine={false}
                  width={120}
                />
                <Tooltip content={<CustomTooltip />} />
                <Bar
                  dataKey="count"
                  name="Businesses"
                  radius={[0, 4, 4, 0]}
                  animationBegin={400}
                  animationDuration={800}
                  animationEasing="ease-out"
                >
                  {stageData.map((entry, i) => (
                    <Cell key={i} fill={getStageColor(entry.stage)} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      {/* 5. Conversion Funnel */}
      {loading ? (
        <div className="chart-container animate-pulse">
          <div className="h-4 w-32 bg-surface-active rounded mb-4" />
          <div className="space-y-2">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="flex items-center gap-3">
                <div className="h-3 w-20 bg-surface-active rounded" />
                <div className="flex-1 h-7 bg-surface-active rounded" />
                <div className="h-3 w-8 bg-surface-active rounded" />
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div className="chart-container animate-scale-in" style={{ animationDelay: '400ms' }}>
          <h3 className="text-sm font-medium text-text-primary mb-4 flex items-center gap-2">
            <Funnel className="w-4 h-4 text-purple-400" />
            Conversion Funnel
          </h3>
          <ConversionFunnel stageDistribution={stageData} />
        </div>
      )}
    </div>
  )
}