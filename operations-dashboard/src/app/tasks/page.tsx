'use client'

import { useState, useEffect, useCallback } from 'react'
import {
  ClipboardList,
  CheckCircle2,
  Circle,
  AlertCircle,
  Loader2,
  Calendar,
  Building2,
  ArrowUp,
  Flame,
  Plus,
  RefreshCw,
} from 'lucide-react'
import { cn, formatDate, formatRelativeTime } from '@/lib/utils'

// ─── Types ───

interface TaskBusiness {
  id: string
  name: string
}

interface Task {
  id: string
  title: string
  description: string | null
  status: 'pending' | 'in_progress' | 'completed' | 'cancelled'
  priority: 'low' | 'medium' | 'high' | 'critical'
  dueDate: string | null
  completedAt: string | null
  category: string | null
  createdAt: string
  updatedAt: string
  businessId: string | null
  business: TaskBusiness | null
  assignedTo: { name: string } | null
}

interface Tab {
  key: string
  label: string
  filter: { status?: string; overdue?: boolean }
}

// ─── Constants ───

const TABS: Tab[] = [
  { key: 'all', label: 'All', filter: {} },
  { key: 'pending', label: 'Pending', filter: { status: 'pending' } },
  { key: 'in_progress', label: 'In Progress', filter: { status: 'in_progress' } },
  { key: 'completed', label: 'Completed', filter: { status: 'completed' } },
  { key: 'overdue', label: 'Overdue', filter: { status: 'pending', overdue: true } },
]

const PRIORITY_COLORS: Record<string, { label: string; className: string }> = {
  critical: { label: 'Critical', className: 'badge-red' },
  high: { label: 'High', className: 'badge-yellow' },
  medium: { label: 'Medium', className: 'badge-blue' },
  low: { label: 'Low', className: 'badge-gray' },
}

const STATUS_CONFIG: Record<string, { label: string; className: string; icon: typeof Circle }> = {
  pending: { label: 'Pending', className: 'badge-yellow', icon: Circle },
  in_progress: { label: 'In Progress', className: 'badge-blue', icon: Loader2 },
  completed: { label: 'Completed', className: 'badge-green', icon: CheckCircle2 },
  cancelled: { label: 'Cancelled', className: 'badge-gray', icon: AlertCircle },
}

const CATEGORY_COLORS: Record<string, string> = {
  'follow-up': 'badge-blue',
  call: 'badge-purple',
  quotation: 'badge-yellow',
  proposal: 'badge-green',
  meeting: 'badge-red',
  general: 'badge-gray',
}

function getCategoryLabel(category: string | null): string {
  if (!category) return 'General'
  return category
    .split('-')
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(' ')
}

function getCategoryClass(category: string | null): string {
  if (!category) return 'badge-gray'
  return CATEGORY_COLORS[category] || 'badge-gray'
}

function getDueDateColor(dueDate: string | null): string {
  if (!dueDate) return 'text-text-muted'
  const now = new Date()
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  const due = new Date(dueDate)
  const dueDay = new Date(due.getFullYear(), due.getMonth(), due.getDate())

  if (dueDay < today) return 'text-danger'
  if (dueDay.getTime() === today.getTime()) return 'text-warning'
  return 'text-text-muted'
}

function isOverdue(dueDate: string | null): boolean {
  if (!dueDate) return false
  const now = new Date()
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  const due = new Date(dueDate)
  const dueDay = new Date(due.getFullYear(), due.getMonth(), due.getDate())
  return dueDay < today
}

function isToday(dueDate: string | null): boolean {
  if (!dueDate) return false
  const now = new Date()
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  const due = new Date(dueDate)
  const dueDay = new Date(due.getFullYear(), due.getMonth(), due.getDate())
  return dueDay.getTime() === today.getTime()
}

// ─── Skeleton ───

function TaskSkeleton() {
  return (
    <div className="animate-fade-in space-y-2">
      {Array.from({ length: 6 }).map((_, i) => (
        <div key={i} className="card flex items-center gap-4 p-4">
          <div className="skeleton h-5 w-5 rounded-full flex-shrink-0" />
          <div className="flex-1 space-y-2 min-w-0">
            <div className="skeleton h-4 w-3/5" />
            <div className="skeleton h-3 w-2/5" />
          </div>
          <div className="skeleton h-5 w-16 rounded-full flex-shrink-0" />
          <div className="skeleton h-5 w-20 rounded-full flex-shrink-0" />
          <div className="skeleton h-5 w-24 rounded-full flex-shrink-0" />
          <div className="skeleton h-8 w-20 rounded-lg flex-shrink-0" />
        </div>
      ))}
    </div>
  )
}

// ─── Empty State ───

function EmptyState({ activeTab }: { activeTab: string }) {
  const messages: Record<string, { title: string; desc: string }> = {
    all: {
      title: 'No tasks yet',
      desc: 'Tasks will appear here once they are created by the system or your team.',
    },
    pending: {
      title: 'No pending tasks',
      desc: 'All caught up! No pending tasks to show.',
    },
    in_progress: {
      title: 'No active tasks',
      desc: 'No tasks are currently in progress.',
    },
    completed: {
      title: 'No completed tasks',
      desc: 'Completed tasks will appear here once you mark them done.',
    },
    overdue: {
      title: 'No overdue tasks',
      desc: 'Great job! No tasks are past their due date.',
    },
  }

  const msg = messages[activeTab] || messages.all

  return (
    <div className="flex flex-col items-center justify-center py-20 text-center">
      <div className="w-16 h-16 rounded-2xl bg-surface-active flex items-center justify-center mb-4">
        <ClipboardList className="w-8 h-8 text-text-muted" />
      </div>
      <h3 className="text-lg font-semibold text-text-primary mb-1">{msg.title}</h3>
      <p className="text-sm text-text-muted max-w-sm">{msg.desc}</p>
    </div>
  )
}

// ─── Main Page ───

export default function TasksPage() {
  const [tasks, setTasks] = useState<Task[]>([])
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('all')
  const [completingIds, setCompletingIds] = useState<Set<string>>(new Set())
  const [counts, setCounts] = useState<Record<string, number>>({})
  const [error, setError] = useState<string | null>(null)

  // ── Fetch tasks ──

  const fetchTasks = useCallback(async () => {
    try {
      setError(null)
      const tab = TABS.find((t) => t.key === activeTab) || TABS[0]
      const params = new URLSearchParams()
      if (tab.filter.status) params.set('status', tab.filter.status)
      if (tab.filter.overdue) params.set('overdue', 'true')

      const res = await fetch(`/api/tasks?${params.toString()}`)
      if (!res.ok) throw new Error('Failed to fetch tasks')
      const data = await res.json()
      setTasks(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load tasks')
    } finally {
      setLoading(false)
    }
  }, [activeTab])

  // ── Fetch counts for all tabs ──

  const fetchCounts = useCallback(async () => {
    try {
      const results = await Promise.all(
        TABS.map(async (tab) => {
          const params = new URLSearchParams()
          if (tab.filter.status) params.set('status', tab.filter.status)
          if (tab.filter.overdue) params.set('overdue', 'true')
          const res = await fetch(`/api/tasks?${params.toString()}`)
          if (!res.ok) return { key: tab.key, count: 0 }
          const data = await res.json()
          return { key: tab.key, count: data.length }
        })
      )
      const countMap: Record<string, number> = {}
      results.forEach((r) => {
        countMap[r.key] = r.count
      })
      setCounts(countMap)
    } catch {
      // Silently fail — counts are non-critical
    }
  }, [])

  useEffect(() => {
    // eslint-disable-next-line react-hooks/exhaustive-deps
    fetchTasks()
    fetchCounts()
  }, [fetchTasks, fetchCounts])

  // ── Mark complete ──

  const markComplete = useCallback(async (taskId: string) => {
    setCompletingIds((prev) => new Set(prev).add(taskId))
    try {
      const res = await fetch('/api/tasks', {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: taskId, status: 'completed' }),
      })
      if (!res.ok) throw new Error('Failed to update task')

      // Optimistically update local state
      setTasks((prev) =>
        prev.map((t) =>
          t.id === taskId
            ? { ...t, status: 'completed', completedAt: new Date().toISOString() }
            : t
        )
      )
      // Refresh counts
      fetchCounts()
    } catch (err) {
      console.error('Failed to mark task complete:', err)
    } finally {
      setCompletingIds((prev) => {
        const next = new Set(prev)
        next.delete(taskId)
        return next
      })
    }
  }, [fetchCounts])

  // ── Render ──

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">Tasks</h1>
          <p className="text-sm text-text-muted mt-1">
            Manage and track your tasks across all businesses
          </p>
        </div>
        <button
          onClick={() => {
            setLoading(true)
            setActiveTab('all')
          }}
          className="btn-ghost btn-sm"
          title="Refresh"
        >
          <RefreshCw className="w-4 h-4" />
          Refresh
        </button>
      </div>

      {/* Filter tabs */}
      <div className="flex items-center gap-1 overflow-x-auto pb-1">
        {TABS.map((tab) => {
          const count = counts[tab.key]
          const isActive = activeTab === tab.key
          return (
            <button
              key={tab.key}
              onClick={() => {
                setActiveTab(tab.key)
                setLoading(true)
              }}
              className={cn(
                'flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 whitespace-nowrap',
                isActive
                  ? 'bg-accent text-white shadow-sm'
                  : 'text-text-secondary hover:text-text-primary hover:bg-surface-hover'
              )}
            >
              {tab.label}
              {count !== undefined && (
                <span
                  className={cn(
                    'inline-flex items-center justify-center min-w-[20px] h-5 px-1.5 rounded-full text-[11px] font-semibold',
                    isActive
                      ? 'bg-white/20 text-white'
                      : 'bg-surface-active text-text-muted'
                  )}
                >
                  {count}
                </span>
              )}
            </button>
          )
        })}
      </div>

      {/* Error state */}
      {error && (
        <div className="card border-danger/30 bg-danger/5 flex items-center gap-3 p-4">
          <AlertCircle className="w-5 h-5 text-danger flex-shrink-0" />
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-danger">{error}</p>
            <p className="text-xs text-text-muted mt-0.5">
              Try refreshing the page or check your connection.
            </p>
          </div>
          <button onClick={fetchTasks} className="btn-ghost btn-sm">
            <RefreshCw className="w-3.5 h-3.5" />
            Retry
          </button>
        </div>
      )}

      {/* Loading skeleton */}
      {loading && !error && <TaskSkeleton />}

      {/* Task list */}
      {!loading && !error && tasks.length === 0 && <EmptyState activeTab={activeTab} />}

      {!loading && !error && tasks.length > 0 && (
        <div className="space-y-2">
          {/* Table header (hidden on mobile) */}
          <div className="hidden md:flex items-center gap-4 px-4 py-2 text-xs font-medium text-text-muted uppercase tracking-wider">
            <div className="w-5 flex-shrink-0" />
            <div className="flex-1 min-w-0">Task</div>
            <div className="w-28 flex-shrink-0">Business</div>
            <div className="w-20 flex-shrink-0 text-center">Priority</div>
            <div className="w-28 flex-shrink-0 text-center">Due Date</div>
            <div className="w-24 flex-shrink-0 text-center">Status</div>
            <div className="w-24 flex-shrink-0 text-center">Category</div>
            <div className="w-24 flex-shrink-0 text-right">Action</div>
          </div>

          {tasks.map((task) => {
            const StatusIcon = STATUS_CONFIG[task.status]?.icon || Circle
            const isCompleting = completingIds.has(task.id)
            const canComplete = task.status === 'pending' || task.status === 'in_progress'
            const dueColor = getDueDateColor(task.dueDate)
            const taskOverdue = isOverdue(task.dueDate)
            const taskToday = isToday(task.dueDate)

            return (
              <div
                key={task.id}
                className={cn(
                  'card flex flex-col md:flex-row md:items-center gap-3 md:gap-4 p-4 animate-scale-in',
                  task.status === 'completed' && 'opacity-60'
                )}
              >
                {/* Status icon + title */}
                <div className="flex items-start gap-3 flex-1 min-w-0">
                  <button
                    onClick={() => canComplete && !isCompleting && markComplete(task.id)}
                    disabled={!canComplete || isCompleting}
                    className={cn(
                      'mt-0.5 flex-shrink-0 transition-all duration-200',
                      canComplete && !isCompleting
                        ? 'text-text-muted hover:text-success cursor-pointer'
                        : 'text-text-muted cursor-default',
                      task.status === 'completed' && 'text-success',
                      isCompleting && 'animate-pulse'
                    )}
                    title={canComplete ? 'Mark as complete' : task.status}
                  >
                    {isCompleting ? (
                      <Loader2 className="w-5 h-5 animate-spin" />
                    ) : task.status === 'completed' ? (
                      <CheckCircle2 className="w-5 h-5" />
                    ) : (
                      <Circle className="w-5 h-5" />
                    )}
                  </button>

                  <div className="min-w-0">
                    <h3
                      className={cn(
                        'text-sm font-medium text-text-primary truncate',
                        task.status === 'completed' && 'line-through'
                      )}
                    >
                      {task.title}
                    </h3>
                    {task.description && (
                      <p className="text-xs text-text-muted mt-0.5 line-clamp-1">
                        {task.description}
                      </p>
                    )}
                  </div>
                </div>

                {/* Business */}
                <div className="flex items-center gap-1.5 md:w-28 flex-shrink-0">
                  <Building2 className="w-3.5 h-3.5 text-text-muted md:hidden" />
                  <span className="text-xs text-text-secondary truncate">
                    {task.business?.name || '—'}
                  </span>
                </div>

                {/* Priority */}
                <div className="md:w-20 flex-shrink-0 md:text-center">
                  {task.priority && PRIORITY_COLORS[task.priority] ? (
                    <span className={cn(PRIORITY_COLORS[task.priority].className, 'text-[11px]')}>
                      {task.priority === 'critical' && <Flame className="w-3 h-3 inline mr-0.5" />}
                      {task.priority === 'high' && <ArrowUp className="w-3 h-3 inline mr-0.5" />}
                      {PRIORITY_COLORS[task.priority].label}
                    </span>
                  ) : (
                    <span className="badge-gray text-[11px]">—</span>
                  )}
                </div>

                {/* Due Date */}
                <div className="flex items-center gap-1.5 md:w-28 flex-shrink-0 md:justify-center">
                  <Calendar className={cn('w-3.5 h-3.5 md:hidden', dueColor)} />
                  <span className={cn('text-xs font-medium', dueColor)}>
                    {task.dueDate ? (
                      <>
                        {formatDate(task.dueDate)}
                        {taskOverdue && (
                          <span className="ml-1 text-[10px] text-danger">(Overdue)</span>
                        )}
                        {taskToday && (
                          <span className="ml-1 text-[10px] text-warning">(Today)</span>
                        )}
                      </>
                    ) : (
                      'No due date'
                    )}
                  </span>
                </div>

                {/* Status */}
                <div className="md:w-24 flex-shrink-0 md:text-center">
                  {STATUS_CONFIG[task.status] ? (
                    <span className={cn(STATUS_CONFIG[task.status].className, 'text-[11px]')}>
                      <StatusIcon className="w-3 h-3 inline mr-0.5" />
                      {STATUS_CONFIG[task.status].label}
                    </span>
                  ) : (
                    <span className="badge-gray text-[11px]">{task.status}</span>
                  )}
                </div>

                {/* Category */}
                <div className="md:w-24 flex-shrink-0 md:text-center">
                  <span className={cn(getCategoryClass(task.category), 'text-[11px]')}>
                    {getCategoryLabel(task.category)}
                  </span>
                </div>

                {/* Action */}
                <div className="md:w-24 flex-shrink-0 md:text-right">
                  {canComplete ? (
                    <button
                      onClick={() => markComplete(task.id)}
                      disabled={isCompleting}
                      className="btn-ghost btn-sm text-success hover:text-success hover:bg-success/10 w-full md:w-auto"
                    >
                      {isCompleting ? (
                        <Loader2 className="w-3.5 h-3.5 animate-spin" />
                      ) : (
                        <CheckCircle2 className="w-3.5 h-3.5" />
                      )}
                      <span className="hidden sm:inline">Complete</span>
                    </button>
                  ) : (
                    <span className="text-xs text-text-muted block text-center md:text-right">
                      {task.status === 'completed'
                        ? `Done ${task.completedAt ? formatRelativeTime(task.completedAt) : ''}`
                        : task.status}
                    </span>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      )}

      {/* Summary footer */}
      {!loading && !error && tasks.length > 0 && (
        <div className="flex items-center justify-between text-xs text-text-muted px-1">
          <span>
            Showing {tasks.length} task{tasks.length !== 1 ? 's' : ''}
            {activeTab !== 'all' && ` (${activeTab} filter)`}
          </span>
          <span className="hidden sm:inline">
            Last updated {formatRelativeTime(new Date().toISOString())}
          </span>
        </div>
      )}
    </div>
  )
}