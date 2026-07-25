import { NextResponse } from 'next/server'
import prisma from '@/lib/prisma'

export async function POST(request: Request) {
  try {
    const body = await request.json()
    const skill = await prisma.skillStatus.upsert({
      where: { name: body.name },
      update: {
        version: body.version,
        status: body.status,
        executionCount: body.executionCount,
        averageRuntime: body.averageRuntime,
        successRate: body.successRate,
        failureRate: body.failureRate,
        lastUsedAt: body.lastUsedAt ? new Date(body.lastUsedAt) : undefined,
      },
      create: {
        name: body.name,
        version: body.version,
        status: body.status || 'loaded',
      },
    })

    await prisma.activityLog.create({
      data: {
        type: body.status === 'loaded' ? 'skill_loaded' : 'skill_failed',
        title: `Skill ${body.status === 'loaded' ? 'Loaded' : 'Failed'}`,
        description: `${body.name} ${body.status === 'loaded' ? 'loaded successfully' : 'failed to load'}`,
      },
    })

    return NextResponse.json(skill)
  } catch {
    return NextResponse.json({ error: 'Failed to update skill' }, { status: 500 })
  }
}