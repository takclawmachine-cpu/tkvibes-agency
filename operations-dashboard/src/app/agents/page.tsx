'use client'

import { useState, useEffect, useCallback } from 'react'
import { Activity, AlertTriangle, RefreshCw, Box } from 'lucide-react'
import { cn, formatRelativeTime, getAgentStatusColor, getAgentStatusIcon } from '@/lib/utils'

interface Agent {
  id: string
  name: string
  status: string
  currentTask: string | null
  lastFinishedTask: string | null
  lastError: string | null
  memoryUsage: number | null
  cpuUsage: number | null
  tasksCompleted: number
  averageRuntime: number | null
  queueSize: number
  heartbeatAt: string
  createdAt: string
}

interface Skill {
  id: string
  name: string
  version: string | null
  status: string
  executionCount: number
  averageRuntime: number | null
  successRate: number | null
  failureRate: number | null
  lastUsedAt: string | null
}

const AGENT_ICONS: Record<string, string> = {
  'Business Discovery': '🔍',
  'Website Generator': '🌐',
  'Proposal Generator': '📄',
  'Pitch Deck Generator': '📊',
  'Outreach Agent': '📧',
  'CRM Sync Agent': '🔄',
}

export default function AgentMonitorPage() {
  const [agents, setAgents] = useState<Agent[]>([])
  const [skills, setSkills] = useState<Skill[]>([])
  const [loading, setLoading] = useState(true)

  const fetchData = useCallback(async () => {
    setLoading(true)
    try {
      const res = await fetch('/api/agents')
      if (res.ok) {
        const data = await res.json()
        setAgents(data.agents || [])
        setSkills(data.skills || [])
      }
    } catch (err) {
      console.error('Failed to fetch agent data', err)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    // fetchData sets loading=true internally, this is a false positive for react-hooks/set-state-in-effect
    // eslint-disable-next-line react-hooks/exhaustive-deps
    fetchData()
    const interval = setInterval(fetchData, 15000)
    return () => clearInterval(interval)
  }, [fetchData])

  const isOffline = useCallback((agent: Agent) => {
    const timeout = 5 * 60 * 1000
    const heartbeat = new Date(agent.heartbeatAt).getTime()
    const now = new Date().getTime()
    return now - heartbeat > timeout
  }, [])

  return (
    <div className="space-y-8 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-text-primary">Agent Monitor</h1>
          <p className="text-sm text-text-muted mt-0.5">Real-time status of Hermes agents and skills</p>
        </div>
        <button onClick={fetchData} className="btn-ghost btn-sm">
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          Auto-refresh (15s)
        </button>
      </div>

      {/* Agents */}
      <section>
        <h2 className="text-sm font-semibold text-text-primary mb-4 flex items-center gap-2">
          <Activity className="w-4 h-4 text-accent" />
          Agents
        </h2>
        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="card animate-pulse space-y-3">
                <div className="flex items-center gap-3">
                  <div className="skeleton h-10 w-10 rounded-lg" />
                  <div className="flex-1">
                    <div className="skeleton h-4 w-32" />
                    <div className="skeleton h-3 w-20 mt-1" />
                  </div>
                </div>
                <div className="skeleton h-3 w-full" />
                <div className="skeleton h-3 w-3/4" />
              </div>
            ))}
          </div>
        ) : agents.length === 0 ? (
          <div className="card py-12 text-center">
            <Activity className="w-10 h-10 text-text-muted/30 mx-auto mb-3" />
            <p className="text-sm text-text-muted">No agents registered</p>
            <p className="text-xs text-text-muted/60 mt-1">Agents will appear here once they start reporting</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {agents.map((agent) => {
              const offline = isOffline(agent)
              const statusColor = offline ? '#ef4444' : getAgentStatusColor(agent.status)
              const statusDot = offline ? 'bg-red-500' : getAgentStatusIcon(agent.status)

              return (
                <div key={agent.id} className={cn(
                  'card hover:border-border-light transition-all duration-200',
                  offline && 'border-danger/30'
                )}>
                  {/* Header */}
                  <div className="flex items-start gap-3 mb-3">
                    <div className="w-10 h-10 rounded-lg flex items-center justify-center text-lg bg-surface-active" style={{ borderColor: statusColor + '30', borderWidth: 1 }}>
                      {AGENT_ICONS[agent.name] || '🤖'}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <h3 className="text-sm font-semibold text-text-primary truncate">{agent.name}</h3>
                        {offline && (
                          <span className="badge-red text-[10px] flex-shrink-0">Offline</span>
                        )}
                      </div>
                      <div className="flex items-center gap-2 mt-0.5">
                        <span className={`w-2 h-2 rounded-full ${statusDot}`} />
                        <span className="text-xs font-medium" style={{ color: statusColor }}>
                          {offline ? 'Offline' : agent.status.charAt(0).toUpperCase() + agent.status.slice(1)}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Stats grid */}
                  <div className="grid grid-cols-2 gap-2 mb-3">
                    <div className="bg-surface-active rounded-lg p-2">
                      <div className="text-[10px] text-text-muted">Tasks Done</div>
                      <div className="text-sm font-semibold text-text-primary font-mono">{agent.tasksCompleted}</div>
                    </div>
                    <div className="bg-surface-active rounded-lg p-2">
                      <div className="text-[10px] text-text-muted">Queue</div>
                      <div className="text-sm font-semibold text-text-primary font-mono">{agent.queueSize}</div>
                    </div>
                    {agent.cpuUsage != null && (
                      <div className="bg-surface-active rounded-lg p-2">
                        <div className="text-[10px] text-text-muted">CPU</div>
                        <div className="text-sm font-semibold text-text-primary font-mono">{agent.cpuUsage.toFixed(1)}%</div>
                      </div>
                    )}
                    {agent.memoryUsage != null && (
                      <div className="bg-surface-active rounded-lg p-2">
                        <div className="text-[10px] text-text-muted">Memory</div>
                        <div className="text-sm font-semibold text-text-primary font-mono">{agent.memoryUsage.toFixed(0)}MB</div>
                      </div>
                    )}
                  </div>

                  {/* Current task */}
                  {agent.currentTask && (
                    <div className="text-xs text-text-secondary mb-1">
                      <span className="text-text-muted">Now: </span>{agent.currentTask}
                    </div>
                  )}
                  {agent.lastError && (
                    <div className="text-xs text-danger flex items-center gap-1 mt-1">
                      <AlertTriangle className="w-3 h-3" />
                      {agent.lastError}
                    </div>
                  )}

                  {/* Heartbeat */}
                  <div className="text-[10px] text-text-muted mt-2">
                    Heartbeat: {formatRelativeTime(agent.heartbeatAt)}
                    {agent.averageRuntime != null && <> · Avg runtime: {agent.averageRuntime.toFixed(1)}s</>}
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </section>

      {/* Skills */}
      <section>
        <h2 className="text-sm font-semibold text-text-primary mb-4 flex items-center gap-2">
          <Box className="w-4 h-4 text-accent" />
          Skills
        </h2>
        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="card animate-pulse space-y-2">
                <div className="skeleton h-4 w-32" />
                <div className="skeleton h-3 w-20" />
              </div>
            ))}
          </div>
        ) : skills.length === 0 ? (
          <div className="card py-12 text-center">
            <Box className="w-10 h-10 text-text-muted/30 mx-auto mb-3" />
            <p className="text-sm text-text-muted">No skills registered</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {skills.map((skill) => (
              <div key={skill.id} className="card hover:border-border-light transition-all duration-200">
                <div className="flex items-start gap-3">
                  <div className={cn(
                    'w-2.5 h-2.5 rounded-full mt-1.5 flex-shrink-0',
                    skill.status === 'loaded' ? 'bg-green-500' :
                    skill.status === 'loading' ? 'bg-yellow-500' : 'bg-red-500'
                  )} />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <h3 className="text-sm font-semibold text-text-primary truncate">{skill.name}</h3>
                      <span className="badge text-[10px] flex-shrink-0"
                        style={{
                          backgroundColor: skill.status === 'loaded' ? 'rgba(34, 197, 94, 0.1)' :
                            skill.status === 'loading' ? 'rgba(234, 179, 8, 0.1)' : 'rgba(239, 68, 68, 0.1)',
                          color: skill.status === 'loaded' ? '#22c55e' :
                            skill.status === 'loading' ? '#eab308' : '#ef4444'
                        }}>
                        {skill.status}
                      </span>
                    </div>
                    {skill.version && (
                      <p className="text-[10px] text-text-muted mt-0.5">v{skill.version}</p>
                    )}

                    <div className="grid grid-cols-2 gap-2 mt-3">
                      <div className="bg-surface-active rounded p-1.5">
                        <div className="text-[10px] text-text-muted">Executions</div>
                        <div className="text-xs font-semibold text-text-primary">{skill.executionCount}</div>
                      </div>
                      {skill.successRate != null && (
                        <div className="bg-surface-active rounded p-1.5">
                          <div className="text-[10px] text-text-muted">Success Rate</div>
                          <div className="text-xs font-semibold text-green-400">{skill.successRate.toFixed(0)}%</div>
                        </div>
                      )}
                      {skill.failureRate != null && (
                        <div className="bg-surface-active rounded p-1.5">
                          <div className="text-[10px] text-text-muted">Failure Rate</div>
                          <div className="text-xs font-semibold text-red-400">{skill.failureRate.toFixed(0)}%</div>
                        </div>
                      )}
                      {skill.averageRuntime != null && (
                        <div className="bg-surface-active rounded p-1.5">
                          <div className="text-[10px] text-text-muted">Avg Runtime</div>
                          <div className="text-xs font-semibold text-text-primary">{skill.averageRuntime.toFixed(1)}s</div>
                        </div>
                      )}
                    </div>

                    {skill.lastUsedAt && (
                      <p className="text-[10px] text-text-muted mt-2">
                        Last used: {formatRelativeTime(skill.lastUsedAt)}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  )
}