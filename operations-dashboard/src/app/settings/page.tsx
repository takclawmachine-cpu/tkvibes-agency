'use client'

import { useState } from 'react'
import { Settings, Database, Download, Upload, RefreshCw, CheckCircle, AlertCircle, FileJson, FileText, Table, Loader2 } from 'lucide-react'
import { cn } from '@/lib/utils'

export default function SettingsPage() {
  const [backingUp, setBackingUp] = useState(false)
  const [exporting, setExporting] = useState(false)
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null)

  const handleBackup = async () => {
    setBackingUp(true)
    setMessage(null)
    try {
      const res = await fetch('/api/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'backup' }),
      })
      const data = await res.json()
      if (data.success) {
        setMessage({ type: 'success', text: `Backup created: ${data.path}` })
      } else {
        setMessage({ type: 'error', text: 'Backup failed' })
      }
    } catch (err) {
      setMessage({ type: 'error', text: 'Backup failed: ' + (err instanceof Error ? err.message : 'Unknown error') })
    } finally {
      setBackingUp(false)
    }
  }

  const handleExport = async (format: string) => {
    setExporting(true)
    setMessage(null)
    try {
      const res = await fetch('/api/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'export', format }),
      })
      const data = await res.json()
      if (data.success) {
        setMessage({ type: 'success', text: `Export saved: ${data.path}` })
      } else {
        setMessage({ type: 'error', text: 'Export failed' })
      }
    } catch (err) {
      setMessage({ type: 'error', text: 'Export failed: ' + (err instanceof Error ? err.message : 'Unknown error') })
    } finally {
      setExporting(false)
    }
  }

  return (
    <div className="space-y-8 animate-fade-in">
      <div>
        <h1 className="text-xl font-bold text-text-primary">Settings</h1>
        <p className="text-sm text-text-muted mt-0.5">Configure the dashboard, backup data, and export</p>
      </div>

      {/* Message */}
      {message && (
        <div className={cn(
          'flex items-center gap-3 px-4 py-3 rounded-lg border text-sm',
          message.type === 'success'
            ? 'border-green-500/30 bg-green-500/10 text-green-400'
            : 'border-red-500/30 bg-red-500/10 text-red-400'
        )}>
          {message.type === 'success' ? <CheckCircle className="w-4 h-4 flex-shrink-0" /> : <AlertCircle className="w-4 h-4 flex-shrink-0" />}
          <span className="text-xs">{message.text}</span>
        </div>
      )}

      {/* Backup Section */}
      <section className="card">
        <div className="flex items-start gap-4">
          <div className="w-10 h-10 rounded-lg bg-blue-500/10 text-blue-400 flex items-center justify-center flex-shrink-0">
            <Database className="w-4 h-4" />
          </div>
          <div className="flex-1">
            <h2 className="text-sm font-semibold text-text-primary mb-1">Database Backup</h2>
            <p className="text-xs text-text-muted mb-4">Create a manual backup of the SQLite database. Backups are stored in the backups/ folder.</p>
            <button
              onClick={handleBackup}
              disabled={backingUp}
              className="btn-primary btn-sm"
            >
              {backingUp ? (
                <><Loader2 className="w-3.5 h-3.5 animate-spin" /> Backing up...</>
              ) : (
                <><Download className="w-3.5 h-3.5" /> Create Backup</>
              )}
            </button>
          </div>
        </div>
      </section>

      {/* Export Section */}
      <section className="card">
        <div className="flex items-start gap-4">
          <div className="w-10 h-10 rounded-lg bg-purple-500/10 text-purple-400 flex items-center justify-center flex-shrink-0">
            <Upload className="w-4 h-4" />
          </div>
          <div className="flex-1">
            <h2 className="text-sm font-semibold text-text-primary mb-1">Export Data</h2>
            <p className="text-xs text-text-muted mb-4">Export all businesses and related data in various formats. Exports are saved in the exports/ folder.</p>
            <div className="flex items-center gap-2 flex-wrap">
              <button
                onClick={() => handleExport('json')}
                disabled={exporting}
                className="btn-secondary btn-sm"
              >
                <FileJson className="w-3.5 h-3.5" />
                Export JSON
              </button>
              <button
                onClick={() => handleExport('csv')}
                disabled={exporting}
                className="btn-secondary btn-sm"
              >
                <Table className="w-3.5 h-3.5" />
                Export CSV
              </button>
              <button
                onClick={() => handleExport('markdown')}
                disabled={exporting}
                className="btn-secondary btn-sm"
              >
                <FileText className="w-3.5 h-3.5" />
                Export Markdown
              </button>
            </div>
            {exporting && (
              <div className="flex items-center gap-2 text-xs text-text-muted mt-2">
                <Loader2 className="w-3 h-3 animate-spin" />
                Exporting...
              </div>
            )}
          </div>
        </div>
      </section>

      {/* About Section */}
      <section className="card">
        <div className="flex items-start gap-4">
          <div className="w-10 h-10 rounded-lg bg-green-500/10 text-green-400 flex items-center justify-center flex-shrink-0">
            <Settings className="w-4 h-4" />
          </div>
          <div className="flex-1">
            <h2 className="text-sm font-semibold text-text-primary mb-1">About</h2>
            <div className="space-y-1 text-xs text-text-muted">
              <p><span className="text-text-secondary">Dashboard:</span> Hermes Operations Dashboard v1.0.0</p>
              <p><span className="text-text-secondary">Database:</span> SQLite</p>
              <p><span className="text-text-secondary">Framework:</span> Next.js 16 + React 19 + TailwindCSS v4</p>
              <p><span className="text-text-secondary">ORM:</span> Prisma</p>
              <p><span className="text-text-secondary">Project:</span> TKVibes Agency</p>
            </div>
          </div>
        </div>
      </section>

      {/* Auto-backup info */}
      <section className="card">
        <div className="flex items-start gap-4">
          <div className="w-10 h-10 rounded-lg bg-yellow-500/10 text-yellow-400 flex items-center justify-center flex-shrink-0">
            <RefreshCw className="w-4 h-4" />
          </div>
          <div className="flex-1">
            <h2 className="text-sm font-semibold text-text-primary mb-1">Auto-Backup Schedule</h2>
            <p className="text-xs text-text-muted mb-2">The database is automatically backed up daily. You can also create manual backups above.</p>
            <div className="bg-surface-active rounded-lg p-3 text-xs text-text-secondary font-mono">
              <p># Backup location: /backups/</p>
              <p># Export location: /exports/</p>
              <p># Auto-backup runs daily at midnight</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}