import { NextResponse } from 'next/server'
import prisma from '@/lib/prisma'

export async function GET() {
  try {
    const agents = await prisma.agentStatus.findMany({ orderBy: { name: 'asc' } })
    const skills = await prisma.skillStatus.findMany({ orderBy: { name: 'asc' } })
    return NextResponse.json({ agents, skills })
  } catch (error) {
    return NextResponse.json({ error: 'Failed to fetch agents' }, { status: 500 })
  }
}

export async function POST(request: Request) {
  try {
    const body = await request.json()
    const agent = await prisma.agentStatus.upsert({
      where: { name: body.name },
      update: {
        status: body.status,
        currentTask: body.currentTask,
        lastFinishedTask: body.lastFinishedTask,
        lastError: body.lastError,
        memoryUsage: body.memoryUsage,
        cpuUsage: body.cpuUsage,
        tasksCompleted: body.tasksCompleted,
        averageRuntime: body.averageRuntime,
        queueSize: body.queueSize,
        heartbeatAt: new Date(),
      },
      create: {
        name: body.name,
        status: body.status || 'idle',
        heartbeatAt: new Date(),
      },
    })

    await prisma.activityLog.create({
      data: {
        type: body.status === 'running' ? 'agent_started' : 'agent_stopped',
        title: `Agent ${body.status === 'running' ? 'Started' : 'Stopped'}`,
        description: `${body.name} is now ${body.status}`,
      },
    })

    return NextResponse.json(agent)
  } catch (error) {
    return NextResponse.json({ error: 'Failed to update agent' }, { status: 500 })
  }
}