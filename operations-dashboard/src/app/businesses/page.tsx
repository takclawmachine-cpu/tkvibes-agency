'use client'

import { useState, useEffect, useMemo } from 'react'
import { useRouter } from 'next/navigation'
import {
  Search,
  Building2,
  Filter,
  ChevronDown,
  ChevronUp,
  ChevronLeft,
  ChevronRight,
  ChevronsUpDown,
  Star,
  Phone,
  Mail,
  Clock,
  Layers,
  X,
} from 'lucide-react'
import { cn, formatDate, getStageColor, getScoreLabel, PIPELINE_STAGES } from '@/lib/utils'

interface Business {
  id: string
  name: string
  category: string | null
  stage: string
  leadScore: number
  email: string | null
  phone: string | null
  googleRating: number | null
  createdAt: string
}

interface BusinessesResponse {
  businesses: Business[]
  total: number
  page: number
  totalPages: number
}

type SortableColumn = 'name' | 'category' | 'stage' | 'leadScore' | 'email' | 'phone' | 'googleRating' | 'createdAt'

const COLUMNS: { key: SortableColumn; label: string; sortable: boolean; className?: string }[] = [
  { key: 'name', label: 'Business Name', sortable: true },
  { key: 'category', label: 'Category', sortable: true, className: 'hidden md:table-cell' },
  { key: 'stage', label: 'Stage', sortable: true, className: 'hidden lg:table-cell' },
  { key: 'leadScore', label: 'Score', sortable: true, className: 'hidden lg:table-cell' },
  { key: 'email', label: 'Email', sortable: false, className: 'hidden xl:table-cell' },
  { key: 'phone', label: 'Phone', sortable: false, className: 'hidden xl:table-cell' },
  { key: 'googleRating', label: 'Rating', sortable: true, className: 'hidden 2xl:table-cell' },
  { key: 'createdAt', label: 'Created', sortable: true, className: 'hidden 2xl:table-cell' },
]

export default function BusinessesPage() {
  const router = useRouter()

  // Filter state
  const [search, setSearch] = useState('')
  const [searchInput, setSearchInput] = useState('')
  const [stageFilter, setStageFilter] = useState('')
  const [categoryFilter, setCategoryFilter] = useState('')

  // Sort state
  const [sortBy, setSortBy] = useState<SortableColumn>('createdAt')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc')

  // Pagination state
  const [page, setPage] = useState(1)
  const limit = 25

  // Data state
  const [data, setData] = useState<BusinessesResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Derive unique categories from loaded data
  const categories = useMemo(() => {
    if (!data?.businesses) return []
    const cats = new Set<string>()
    data.businesses.forEach((b) => {
      if (b.category) cats.add(b.category)
    })
    return Array.from(cats).sort()
  }, [data])

  // Debounced search
  useEffect(() => {
    const timer = setTimeout(() => {
      setSearch(searchInput)
      setPage(1)
    }, 350)
    return () => clearTimeout(timer)
  }, [searchInput])

  // Fetch businesses
  useEffect(() => {
    const fetchBusinesses = async () => {
      setLoading(true)
      setError(null)
      try {
        const params = new URLSearchParams()
        if (search) params.set('search', search)
        if (stageFilter) params.set('stage', stageFilter)
        if (categoryFilter) params.set('category', categoryFilter)
        params.set('sortBy', sortBy)
        params.set('sortOrder', sortOrder)
        params.set('page', String(page))
        params.set('limit', String(limit))

        const res = await fetch(`/api/businesses?${params.toString()}`)
        if (!res.ok) throw new Error('Failed to fetch businesses')
        const json: BusinessesResponse = await res.json()
        setData(json)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred')
      } finally {
        setLoading(false)
      }
    }

    fetchBusinesses()
  }, [search, stageFilter, categoryFilter, sortBy, sortOrder, page])

  // Handle sort toggle
  const handleSort = (column: SortableColumn) => {
    if (sortBy === column) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')
    } else {
      setSortBy(column)
      setSortOrder('asc')
    }
    setPage(1)
  }

  // Render sort icon
  const SortIcon = ({ column }: { column: SortableColumn }) => {
    if (sortBy !== column) return <ChevronsUpDown className="w-3 h-3 text-text-muted flex-shrink-0" />
    return sortOrder === 'asc' ? (
      <ChevronUp className="w-3 h-3 text-accent flex-shrink-0" />
    ) : (
      <ChevronDown className="w-3 h-3 text-accent flex-shrink-0" />
    )
  }

  // Render star rating
  const StarRating = ({ rating }: { rating: number | null }) => {
    if (rating == null) return <span className="text-text-muted">—</span>
    return (
      <div className="flex items-center gap-1">
        <Star className="w-3 h-3 fill-yellow-500 text-yellow-500" />
        <span>{rating.toFixed(1)}</span>
      </div>
    )
  }

  // Clear all filters
  const hasActiveFilters = search || stageFilter || categoryFilter
  const clearFilters = () => {
    setSearchInput('')
    setSearch('')
    setStageFilter('')
    setCategoryFilter('')
  }

  return (
    <div className="animate-fade-in space-y-5">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">Businesses</h1>
          <p className="text-sm text-text-secondary mt-1">
            {data ? `${data.total} total businesses` : 'Manage your business leads'}
          </p>
        </div>
      </div>

      {/* Filters Bar */}
      <div className="card p-4">
        <div className="flex flex-col sm:flex-row gap-3">
          {/* Search */}
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted" />
            <input
              type="text"
              placeholder="Search businesses..."
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              className="input pl-9 pr-8"
            />
            {searchInput && (
              <button
                onClick={() => { setSearchInput(''); setSearch('') }}
                className="absolute right-2 top-1/2 -translate-y-1/2 p-1 rounded hover:bg-surface-active text-text-muted"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            )}
          </div>

          {/* Stage filter */}
          <div className="relative w-full sm:w-48">
            <Layers className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted pointer-events-none" />
            <select
              value={stageFilter}
              onChange={(e) => { setStageFilter(e.target.value); setPage(1) }}
              className="select pl-9"
            >
              <option value="">All Stages</option>
              {PIPELINE_STAGES.map((stage) => (
                <option key={stage} value={stage}>{stage}</option>
              ))}
            </select>
          </div>

          {/* Category filter */}
          <div className="relative w-full sm:w-48">
            <Filter className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted pointer-events-none" />
            <select
              value={categoryFilter}
              onChange={(e) => { setCategoryFilter(e.target.value); setPage(1) }}
              className="select pl-9"
              disabled={categories.length === 0}
            >
              <option value="">All Categories</option>
              {categories.map((cat) => (
                <option key={cat} value={cat}>{cat}</option>
              ))}
            </select>
          </div>

          {/* Clear filters */}
          {hasActiveFilters && (
            <button onClick={clearFilters} className="btn-ghost btn-sm text-xs whitespace-nowrap">
              <X className="w-3 h-3" />
              Clear
            </button>
          )}
        </div>
      </div>

      {/* Table Card */}
      <div className="card p-0 overflow-hidden">
        {error ? (
          <div className="p-8 text-center">
            <p className="text-danger mb-2">{error}</p>
            <button onClick={() => setPage(1)} className="btn-secondary btn-sm">
              Retry
            </button>
          </div>
        ) : loading ? (
          <LoadingSkeleton />
        ) : data && data.businesses.length === 0 ? (
          <div className="p-8 text-center">
            <Building2 className="w-12 h-12 text-text-muted mx-auto mb-3" />
            <h3 className="text-text-primary font-medium mb-1">No businesses found</h3>
            <p className="text-text-muted text-sm">
              {hasActiveFilters
                ? 'Try adjusting your search or filters'
                : 'No businesses have been added yet'}
            </p>
            {hasActiveFilters && (
              <button onClick={clearFilters} className="btn-secondary btn-sm mt-4">
                Clear Filters
              </button>
            )}
          </div>
        ) : data ? (
          <>
            {/* Table */}
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-border">
                    {COLUMNS.map((col) => (
                      <th
                        key={col.key}
                        className={cn(
                          'table-header px-4 py-3 text-left',
                          col.sortable && 'cursor-pointer hover:text-text-primary transition-colors select-none',
                          col.className
                        )}
                        onClick={() => col.sortable && handleSort(col.key)}
                      >
                        <div className="flex items-center gap-1.5">
                          <span>{col.label}</span>
                          {col.sortable && <SortIcon column={col.key} />}
                        </div>
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {data.businesses.map((business, index) => (
                    <tr
                      key={business.id}
                      onClick={() => router.push(`/businesses/${business.id}`)}
                      className={cn(
                        'border-b border-border transition-colors cursor-pointer',
                        'hover:bg-surface-hover',
                        index % 2 === 0 ? 'bg-surface' : 'bg-surface/50'
                      )}
                    >
                      <td className="table-cell font-medium text-text-primary">
                        <div className="flex items-center gap-2.5">
                          <div className="w-8 h-8 rounded-lg bg-accent-subtle flex items-center justify-center flex-shrink-0">
                            <Building2 className="w-4 h-4 text-accent" />
                          </div>
                          <span className="truncate max-w-[200px]">{business.name}</span>
                        </div>
                      </td>
                      <td className="table-cell text-text-secondary hidden md:table-cell">
                        <span className="badge-gray">{business.category || '—'}</span>
                      </td>
                      <td className="table-cell hidden lg:table-cell">
                        <span
                          className="badge"
                          style={{
                            backgroundColor: `${getStageColor(business.stage)}15`,
                            color: getStageColor(business.stage),
                          }}
                        >
                          {business.stage}
                        </span>
                      </td>
                      <td className="table-cell hidden lg:table-cell">
                        <ScoreBadge score={business.leadScore} />
                      </td>
                      <td className="table-cell text-text-secondary hidden xl:table-cell">
                        {business.email ? (
                          <div className="flex items-center gap-1.5 truncate max-w-[200px]">
                            <Mail className="w-3 h-3 text-text-muted flex-shrink-0" />
                            <span className="truncate">{business.email}</span>
                          </div>
                        ) : (
                          <span className="text-text-muted">—</span>
                        )}
                      </td>
                      <td className="table-cell text-text-secondary hidden xl:table-cell">
                        {business.phone ? (
                          <div className="flex items-center gap-1.5">
                            <Phone className="w-3 h-3 text-text-muted flex-shrink-0" />
                            <span>{business.phone}</span>
                          </div>
                        ) : (
                          <span className="text-text-muted">—</span>
                        )}
                      </td>
                      <td className="table-cell hidden 2xl:table-cell">
                        <StarRating rating={business.googleRating} />
                      </td>
                      <td className="table-cell text-text-secondary hidden 2xl:table-cell">
                        <div className="flex items-center gap-1.5">
                          <Clock className="w-3 h-3 text-text-muted flex-shrink-0" />
                          <span>{formatDate(business.createdAt)}</span>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            {data.totalPages > 1 && (
              <div className="flex items-center justify-between px-4 py-3 border-t border-border">
                <p className="text-xs text-text-muted">
                  Showing {(page - 1) * limit + 1}–{Math.min(page * limit, data.total)} of{' '}
                  {data.total}
                </p>
                <div className="flex items-center gap-1">
                  <button
                    onClick={() => setPage(Math.max(1, page - 1))}
                    disabled={page <= 1}
                    className="btn-ghost btn-icon btn-sm"
                  >
                    <ChevronLeft className="w-4 h-4" />
                  </button>
                  {renderPageNumbers(page, data.totalPages, setPage)}
                  <button
                    onClick={() => setPage(Math.min(data.totalPages, page + 1))}
                    disabled={page >= data.totalPages}
                    className="btn-ghost btn-icon btn-sm"
                  >
                    <ChevronRight className="w-4 h-4" />
                  </button>
                </div>
              </div>
            )}
          </>
        ) : null}
      </div>
    </div>
  )
}

// ─── Sub-components ───

function ScoreBadge({ score }: { score: number }) {
  const { label, color } = getScoreLabel(score)
  return (
    <span className="inline-flex items-center gap-1 tabular-nums">
      <span
        className="w-1.5 h-1.5 rounded-full"
        style={{ backgroundColor: color }}
      />
      <span className="font-medium" style={{ color }}>
        {score}
      </span>
      <span className="text-text-muted text-[10px] uppercase tracking-wider ml-0.5">
        {label}
      </span>
    </span>
  )
}

function LoadingSkeleton() {
  return (
    <div className="p-0">
      <div className="border-b border-border px-4 py-3">
        <div className="flex gap-6">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="skeleton h-3 w-20" />
          ))}
        </div>
      </div>
      {[...Array(8)].map((_, row) => (
        <div
          key={row}
          className={cn(
            'flex items-center gap-4 px-4 py-3.5 border-b border-border',
            row % 2 === 0 ? 'bg-surface' : 'bg-surface/50'
          )}
        >
          <div className="flex items-center gap-2.5 flex-1">
            <div className="skeleton w-8 h-8 rounded-lg" />
            <div className="skeleton h-4 w-40" />
          </div>
          <div className="skeleton h-4 w-24 hidden md:block" />
          <div className="skeleton h-4 w-28 hidden lg:block" />
          <div className="skeleton h-4 w-16 hidden lg:block" />
          <div className="skeleton h-4 w-32 hidden xl:block" />
          <div className="skeleton h-4 w-28 hidden xl:block" />
          <div className="skeleton h-4 w-16 hidden 2xl:block" />
          <div className="skeleton h-4 w-20 hidden 2xl:block" />
        </div>
      ))}
    </div>
  )
}

function renderPageNumbers(
  currentPage: number,
  totalPages: number,
  setPage: (page: number) => void
) {
  const pages: (number | 'ellipsis')[] = []
  const delta = 1

  // Always show first page
  pages.push(1)

  // Calculate range around current page
  const rangeStart = Math.max(2, currentPage - delta)
  const rangeEnd = Math.min(totalPages - 1, currentPage + delta)

  if (rangeStart > 2) pages.push('ellipsis')

  for (let i = rangeStart; i <= rangeEnd; i++) {
    pages.push(i)
  }

  if (rangeEnd < totalPages - 1) pages.push('ellipsis')

  // Always show last page
  if (totalPages > 1) pages.push(totalPages)

  return pages.map((p, i) =>
    p === 'ellipsis' ? (
      <span key={`ellipsis-${i}`} className="px-1.5 text-text-muted text-xs">
        ...
      </span>
    ) : (
      <button
        key={p}
        onClick={() => setPage(p)}
        className={cn(
          'btn-ghost btn-sm min-w-[32px] h-8 px-2 text-xs font-medium',
          p === currentPage && 'bg-accent-subtle text-accent'
        )}
      >
        {p}
      </button>
    )
  )
}