import { NextRequest, NextResponse } from 'next/server'
import prisma from '@/lib/prisma'

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url)
  const status = searchParams.get('status') || ''
  const category = searchParams.get('category') || ''
  const overdue = searchParams.get('overdue') === 'true'

  const where: Record<string, any> = {}
  if (status) where.status = status
  if (category) where.category = category
  if (overdue) where.dueDate = { lt: new Date() }

  try {
    const tasks = await prisma.task.findMany({
      where,
      orderBy: [{ dueDate: 'asc' }, { createdAt: 'desc' }],
      take: 100,
      include: {
        business: { select: { name: true, id: true } },
        assignedTo: { select: { name: true } },
      },
    })
    return NextResponse.json(tasks)
  } catch (error) {
    return NextResponse.json({ error: 'Failed to fetch tasks' }, { status: 500 })
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const task = await prisma.task.create({ data: body })
    return NextResponse.json(task, { status: 201 })
  } catch (error) {
    return NextResponse.json({ error: 'Failed to create task' }, { status: 500 })
  }
}

export async function PATCH(request: NextRequest) {
  try {
    const body = await request.json()
    const { id, ...data } = body
    if (data.status === 'completed') {
      data.completedAt = new Date()
    }
    const task = await prisma.task.update({ where: { id }, data })
    return NextResponse.json(task)
  } catch (error) {
    return NextResponse.json({ error: 'Failed to update task' }, { status: 500 })
  }
}