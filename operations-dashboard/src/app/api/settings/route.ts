import { NextRequest, NextResponse } from 'next/server'
import prisma from '@/lib/prisma'
import { existsSync, mkdirSync, writeFileSync, readFileSync, statSync } from 'fs'
import path from 'path'

export async function GET() {
  try {
    const settings = await prisma.setting.findMany()
    const settingsMap: Record<string, string> = {}
    settings.forEach(s => { settingsMap[s.key] = s.value })
    return NextResponse.json(settingsMap)
  } catch (error) {
    return NextResponse.json({ error: 'Failed to fetch settings' }, { status: 500 })
  }
}

export async function PATCH(request: NextRequest) {
  try {
    const body = await request.json()
    for (const [key, value] of Object.entries(body)) {
      await prisma.setting.upsert({
        where: { key },
        update: { value: String(value) },
        create: { key, value: String(value) },
      })
    }
    return NextResponse.json({ success: true })
  } catch (error) {
    return NextResponse.json({ error: 'Failed to save settings' }, { status: 500 })
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const action = body.action

    if (action === 'backup') {
      const backupDir = path.join(process.cwd(), 'backups')
      if (!existsSync(backupDir)) mkdirSync(backupDir, { recursive: true })

      const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
      const dbPath = path.join(process.cwd(), 'prisma', 'dev.db')
      const backupPath = path.join(backupDir, `backup-${timestamp}.db`)

      if (existsSync(dbPath)) {
        const dbContent = readFileSync(dbPath)
        writeFileSync(backupPath, dbContent)
      }

      await prisma.backup.create({
        data: {
          filePath: backupPath,
          size: existsSync(backupPath) ? statSync(backupPath).size : null,
          type: 'manual',
        },
      })

      return NextResponse.json({ success: true, path: backupPath })
    }

    if (action === 'export') {
      const format = body.format || 'json'
      const businesses = await prisma.business.findMany({
        include: { contacts: true, tags: { include: { tag: true } } },
      })

      const exportDir = path.join(process.cwd(), 'exports')
      if (!existsSync(exportDir)) mkdirSync(exportDir, { recursive: true })

      const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
      let exportPath = ''

      if (format === 'json') {
        exportPath = path.join(exportDir, `export-${timestamp}.json`)
        writeFileSync(exportPath, JSON.stringify(businesses, null, 2))
      } else if (format === 'csv') {
        exportPath = path.join(exportDir, `export-${timestamp}.csv`)
        const headers = 'id,name,category,stage,leadScore,email,phone,website,googleRating,industry,expectedRevenue,createdAt\n'
        const rows = businesses.map(b =>
          `${b.id},"${b.name}","${b.category || ''}","${b.stage}",${b.leadScore},"${b.email || ''}","${b.phone || ''}","${b.website || ''}",${b.googleRating || ''},"${b.industry || ''}",${b.expectedRevenue || ''},"${b.createdAt}"`
        ).join('\n')
        writeFileSync(exportPath, headers + rows)
      } else if (format === 'markdown') {
        exportPath = path.join(exportDir, `export-${timestamp}.md`)
        let md = '# Businesses Export\n\n'
        businesses.forEach(b => {
          md += `## ${b.name}\n`
          md += `- **Category:** ${b.category || 'N/A'}\n`
          md += `- **Stage:** ${b.stage}\n`
          md += `- **Lead Score:** ${b.leadScore}\n`
          md += `- **Email:** ${b.email || 'N/A'}\n`
          md += `- **Phone:** ${b.phone || 'N/A'}\n`
          md += `- **Website:** ${b.website || 'N/A'}\n`
          md += `- **Rating:** ${b.googleRating || 'N/A'}\n`
          md += `- **Created:** ${b.createdAt}\n\n`
        })
        writeFileSync(exportPath, md)
      }

      return NextResponse.json({ success: true, path: exportPath })
    }

    return NextResponse.json({ error: 'Unknown action' }, { status: 400 })
  } catch (error) {
    console.error('Settings API error:', error)
    return NextResponse.json({ error: 'Operation failed' }, { status: 500 })
  }
}