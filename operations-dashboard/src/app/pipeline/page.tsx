'use client'

import { useCallback, useEffect, useMemo, useState } from 'react'
import {
  DragDropContext,
  Droppable,
  Draggable,
  DropResult,
} from '@hello-pangea/dnd'
import { Users, Star, Loader2, GripVertical, AlertCircle } from 'lucide-react'
import { cn, PIPELINE_STAGES, getStageColor, getScoreLabel } from '@/lib/utils'

/* ─── Types ─── */

interface Business {
  id: string
  name: string
  stage: string
  leadScore: number
  googleRating: number | null
  reviewCount: number | null
  category: string | null
  website: string | null
  updatedAt: string
  _count?: {
    communications: number
    emails: number
    tasks: number
    generatedAssets: number
  }
}

interface BusinessesByStage {
  [stage: string]: Business[]
}

/* ─── Helpers ─── */

function getStageBgColor(stage: string): string {
  const color = getStageColor(stage)
  // Convert hex to rgba for background
  const r = parseInt(color.slice(1, 3), 16)
  const g = parseInt(color.slice(3, 5), 16)
  const b = parseInt(color.slice(5, 7), 16)
  return `rgba(${r},${g},${b},0.08)`
}

function getStageBorderColor(stage: string): string {
  const color = getStageColor(stage)
  return `rgba(${parseInt(color.slice(1, 3), 16)},${parseInt(color.slice(3, 5), 16)},${parseInt(color.slice(5, 7), 16)},0.2)`
}

/* ─── Business Card ─── */

function BusinessCard({ business, index }: { business: Business; index: number }) {
  const scoreLabel = getScoreLabel(business.leadScore)

  return (
    <Draggable draggableId={business.id} index={index}>
      {(provided, snapshot) => (
        <div
          ref={provided.innerRef}
          {...provided.draggableProps}
          className={cn(
            'rounded-lg border bg-surface p-3 transition-all duration-150',
            snapshot.isDragging
              ? 'shadow-lg shadow-accent/10 border-accent/30 scale-[1.02]'
              : 'border-border hover:border-border-light',
          )}
          style={{
            ...provided.draggableProps.style,
          }}
        >
          {/* Drag handle + name row */}
          <div className="flex items-start gap-2">
            <div
              {...provided.dragHandleProps}
              className="mt-0.5 cursor-grab active:cursor-grabbing text-text-muted hover:text-text-secondary transition-colors flex-shrink-0"
            >
              <GripVertical className="w-3.5 h-3.5" />
            </div>
            <div className="flex-1 min-w-0">
              <h4 className="text-sm font-medium text-text-primary truncate">
                {business.name}
              </h4>
              {business.category && (
                <p className="text-[11px] text-text-muted mt-0.5 truncate">
                  {business.category}
                </p>
              )}
            </div>
          </div>

          {/* Score + Rating row */}
          <div className="flex items-center gap-2 mt-2.5 pl-5">
            {/* Lead Score badge */}
            <span
              className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-semibold"
              style={{
                backgroundColor: `${scoreLabel.color}18`,
                color: scoreLabel.color,
              }}
            >
              <span
                className="w-1.5 h-1.5 rounded-full"
                style={{ backgroundColor: scoreLabel.color }}
              />
              {business.leadScore}
            </span>

            {/* Google Rating */}
            {business.googleRating != null && (
              <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-medium bg-yellow-500/10 text-yellow-400">
                <Star className="w-2.5 h-2.5 fill-current" />
                {business.googleRating.toFixed(1)}
              </span>
            )}

            {/* Activity count */}
            {business._count && (
              <span className="text-[10px] text-text-muted ml-auto">
                {business._count.communications + business._count.emails} activities
              </span>
            )}
          </div>
        </div>
      )}
    </Draggable>
  )
}

/* ─── Stage Column ─── */

function StageColumn({
  stage,
  businesses,
}: {
  stage: string
  businesses: Business[]
}) {
  const stageColor = getStageColor(stage)
  const bgColor = getStageBgColor(stage)
  const borderColor = getStageBorderColor(stage)
  const isTerminal = stage === 'Won' || stage === 'Lost' || stage === 'Archived'

  return (
    <div
      className="flex-shrink-0 w-72 flex flex-col rounded-xl border overflow-hidden"
      style={{ borderColor }}
    >
      {/* Column header */}
      <div
        className="flex items-center justify-between px-3 py-2.5 border-b"
        style={{
          backgroundColor: bgColor,
          borderBottomColor: borderColor,
        }}
      >
        <div className="flex items-center gap-2 min-w-0">
          <span
            className="w-2.5 h-2.5 rounded-full flex-shrink-0"
            style={{ backgroundColor: stageColor }}
          />
          <h3 className="text-sm font-semibold text-text-primary truncate">
            {stage}
          </h3>
        </div>
        <span
          className="flex-shrink-0 text-[10px] font-medium px-1.5 py-0.5 rounded-full"
          style={{
            backgroundColor: bgColor,
            color: stageColor,
          }}
        >
          {businesses.length}
        </span>
      </div>

      {/* Droppable area */}
      <Droppable droppableId={stage}>
        {(provided, snapshot) => (
          <div
            ref={provided.innerRef}
            {...provided.droppableProps}
            className={cn(
              'flex-1 p-2 space-y-2 min-h-[120px] overflow-y-auto transition-colors duration-150',
              snapshot.isDraggingOver ? 'bg-accent/5' : 'bg-surface',
              isTerminal && 'opacity-90',
            )}
          >
            {businesses.length === 0 && !snapshot.isDraggingOver && (
              <div className="flex flex-col items-center justify-center h-24 text-text-muted">
                <Users className="w-6 h-6 mb-1 opacity-30" />
                <p className="text-[11px]">No leads</p>
              </div>
            )}

            {businesses.map((business, idx) => (
              <BusinessCard key={business.id} business={business} index={idx} />
            ))}
            {provided.placeholder}
          </div>
        )}
      </Droppable>
    </div>
  )
}

/* ─── Loading Skeleton ─── */

function LoadingSkeleton() {
  return (
    <div className="flex gap-4 h-full overflow-x-auto pb-4">
      {Array.from({ length: 5 }).map((_, i) => (
        <div key={i} className="flex-shrink-0 w-72 rounded-xl border border-border bg-surface overflow-hidden animate-pulse">
          <div className="h-10 bg-surface-hover border-b border-border" />
          <div className="p-3 space-y-3">
            {Array.from({ length: 3 }).map((_, j) => (
              <div key={j} className="rounded-lg border border-border p-3 space-y-2">
                <div className="h-3 bg-surface-hover rounded w-3/4" />
                <div className="h-2 bg-surface-hover rounded w-1/2" />
                <div className="flex gap-2 mt-2">
                  <div className="h-4 bg-surface-hover rounded w-12" />
                  <div className="h-4 bg-surface-hover rounded w-10" />
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}

/* ─── Error Banner ─── */

function ErrorBanner({ message, onRetry }: { message: string; onRetry: () => void }) {
  return (
    <div className="flex items-center gap-3 px-4 py-3 mb-4 rounded-lg border border-danger/30 bg-danger/5 text-danger">
      <AlertCircle className="w-4 h-4 flex-shrink-0" />
      <p className="text-sm flex-1">{message}</p>
      <button
        onClick={onRetry}
        className="text-xs font-medium px-3 py-1 rounded-md border border-danger/30 hover:bg-danger/10 transition-colors"
      >
        Retry
      </button>
    </div>
  )
}

/* ─── Main Page ─── */

export default function PipelinePage() {
  const [businesses, setBusinesses] = useState<Business[]>([])
  const [loading, setLoading] = useState(true)
  const [updating, setUpdating] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const fetchBusinesses = useCallback(async (): Promise<void> => {
    setLoading(true)
    setError(null)
    try {
      const res = await fetch('/api/businesses?limit=200')
      if (!res.ok) throw new Error(`Failed to fetch (${res.status})`)
      const data = await res.json()
      setBusinesses(data.businesses || [])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load businesses')
    } finally {
      setLoading(false)
    }
  }, [])

  // Initial fetch — states already initialized to loading=true, error=null
  useEffect(() => {
    let cancelled = false
    fetch('/api/businesses?limit=200')
      .then((res) => {
        if (!res.ok) throw new Error(`Failed to fetch (${res.status})`)
        return res.json()
      })
      .then((data) => {
        if (!cancelled) setBusinesses(data.businesses || [])
      })
      .catch((err) => {
        if (!cancelled) setError(err instanceof Error ? err.message : 'Failed to load businesses')
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [])

  // Group businesses by stage
  const grouped = useMemo<BusinessesByStage>(() => {
    const map: BusinessesByStage = {}
    for (const stage of PIPELINE_STAGES) {
      map[stage] = []
    }
    for (const b of businesses) {
      if (map[b.stage]) {
        map[b.stage].push(b)
      } else {
        // Unknown stage — put in Discovered as fallback
        map['Discovered'].push(b)
      }
    }
    return map
  }, [businesses])

  // Handle drag end
  const handleDragEnd = useCallback(
    async (result: DropResult) => {
      const { source, destination, draggableId } = result

      // Dropped outside any droppable
      if (!destination) return

      // Same position — no change
      if (
        source.droppableId === destination.droppableId &&
        source.index === destination.index
      ) {
        return
      }

      // Optimistically update local state
      setBusinesses((prev) =>
        prev.map((b) =>
          b.id === draggableId ? { ...b, stage: destination.droppableId } : b,
        ),
      )

      // Send PATCH to server
      setUpdating(draggableId)
      try {
        const res = await fetch(`/api/businesses/${draggableId}`, {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ stage: destination.droppableId }),
        })
        if (!res.ok) {
          // Revert on failure
          const failedBusiness = businesses.find((b) => b.id === draggableId)
          if (failedBusiness) {
            setBusinesses((prev) =>
              prev.map((b) =>
                b.id === draggableId ? { ...b, stage: source.droppableId } : b,
              ),
            )
          }
          throw new Error(`Failed to update stage (${res.status})`)
        }
      } catch (err) {
        console.error('Failed to update business stage:', err)
        setError(
          err instanceof Error ? err.message : 'Failed to update stage',
        )
      } finally {
        setUpdating(null)
      }
    },
    [businesses],
  )

  return (
    <div className="flex flex-col h-full">
      {/* Page header */}
      <div className="flex items-center justify-between mb-4 flex-shrink-0">
        <div>
          <h1 className="text-xl font-bold text-text-primary">Lead Pipeline</h1>
          <p className="text-sm text-text-muted mt-0.5">
            Drag leads between stages to update their status
          </p>
        </div>
        <div className="flex items-center gap-2">
          {updating && (
            <span className="flex items-center gap-1.5 text-xs text-text-muted">
              <Loader2 className="w-3 h-3 animate-spin" />
              Saving...
            </span>
          )}
          <button
            onClick={fetchBusinesses}
            disabled={loading}
            className="btn-ghost text-xs px-3 py-1.5 rounded-md border border-border hover:bg-surface-hover transition-colors disabled:opacity-50"
          >
            {loading ? 'Loading...' : 'Refresh'}
          </button>
        </div>
      </div>

      {/* Error banner */}
      {error && <ErrorBanner message={error} onRetry={fetchBusinesses} />}

      {/* Kanban board */}
      {loading ? (
        <LoadingSkeleton />
      ) : (
        <DragDropContext onDragEnd={handleDragEnd}>
          <div className="flex gap-4 h-full overflow-x-auto pb-4">
            {PIPELINE_STAGES.map((stage) => (
              <StageColumn
                key={stage}
                stage={stage}
                businesses={grouped[stage] || []}
              />
            ))}
          </div>
        </DragDropContext>
      )}
    </div>
  )
}