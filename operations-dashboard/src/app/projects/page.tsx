'use client'

import { useState, useEffect, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import { FolderKanban, Loader2, RefreshCw, Building2, Calendar, Clock } from 'lucide-react'
import { cn, formatDate } from '@/lib/utils'

interface ProjectItem {
  id: string
  name: string
  description: string | null
  status: string
  type: string
  startDate: string | null
  endDate: string | null
  createdAt: string
  business: { id: string; name: string } | null
}

export default function ProjectsPage() {
  const [projects, setProjects] = useState<ProjectItem[]>([])
  const [loading, setLoading] = useState(true)
  const router = useRouter()

  const fetchProjects = useCallback(async () => {
    try {
      const res = await fetch('/api/businesses?limit=200')
      if (res.ok) {
        const data = await res.json()
        const allProjects: ProjectItem[] = []
        for (const business of data.businesses) {
          const detailRes = await fetch(`/api/businesses/${business.id}`)
          if (detailRes.ok) {
            const detail = await detailRes.json()
            if (detail.projects) {
              detail.projects.forEach((p: ProjectItem) => {
                allProjects.push({ ...p, business: { id: business.id, name: business.name } })
              })
            }
          }
        }
        setProjects(allProjects)
      }
    } catch (err) {
      console.error('Failed to fetch projects', err)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchProjects()
  }, [fetchProjects])

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-text-primary">Projects</h1>
          <p className="text-sm text-text-muted mt-0.5">Manage business projects</p>
        </div>
        <button onClick={fetchProjects} className="btn-ghost btn-sm">
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="card animate-pulse space-y-3">
              <div className="skeleton h-5 w-40" />
              <div className="skeleton h-3 w-28" />
              <div className="skeleton h-3 w-20" />
            </div>
          ))}
        </div>
      ) : projects.length === 0 ? (
        <div className="card py-16 text-center">
          <FolderKanban className="w-12 h-12 text-text-muted/30 mx-auto mb-3" />
          <p className="text-sm text-text-muted">No projects yet</p>
          <p className="text-xs text-text-muted/60 mt-1">Projects will appear here once created</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {projects.map((project) => (
            <div key={project.id} className="card hover:border-border-light transition-all duration-200 cursor-pointer" onClick={() => router.push(`/businesses/${project.business?.id}`)}>
              <div className="flex items-start justify-between mb-2">
                <h3 className="text-sm font-semibold text-text-primary">{project.name}</h3>
                <span className={cn(
                  'badge text-[10px]',
                  project.status === 'active' ? 'badge-green' :
                  project.status === 'completed' ? 'badge-blue' :
                  project.status === 'on_hold' ? 'badge-yellow' : 'badge-gray'
                )}>
                  {project.status}
                </span>
              </div>
              {project.business && (
                <p className="text-xs text-text-muted flex items-center gap-1 mb-2">
                  <Building2 className="w-3 h-3" />
                  {project.business.name}
                </p>
              )}
              {project.description && (
                <p className="text-xs text-text-secondary mb-3 line-clamp-2">{project.description}</p>
              )}
              <div className="flex items-center gap-3 text-[10px] text-text-muted">
                <span className="flex items-center gap-1">
                  <Calendar className="w-3 h-3" />
                  {project.startDate ? formatDate(project.startDate) : 'TBD'}
                </span>
                {project.endDate && (
                  <span className="flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    Due: {formatDate(project.endDate)}
                  </span>
                )}
                <span className="ml-auto">{project.type}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}