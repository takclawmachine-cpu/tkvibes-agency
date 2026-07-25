import { NextRequest, NextResponse } from 'next/server'
import prisma from '@/lib/prisma'

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params
  try {
    const business = await prisma.business.findUnique({
      where: { id },
      include: {
        contacts: true,
        communications: { orderBy: { createdAt: 'desc' } },
        emails: { orderBy: { createdAt: 'desc' } },
        tasks: { orderBy: { createdAt: 'desc' } },
        projects: true,
        generatedAssets: true,
        proposals: { orderBy: { createdAt: 'desc' } },
        meetings: { orderBy: { scheduledAt: 'desc' } },
        notes: { orderBy: { createdAt: 'desc' }, include: { createdBy: { select: { name: true } } } },
        tags: { include: { tag: true } },
        timelineEvents: { orderBy: { createdAt: 'desc' } },
        stageLogs: { orderBy: { createdAt: 'desc' } },
        assignedAgent: { select: { name: true, email: true } },
      },
    })

    if (!business) {
      return NextResponse.json({ error: 'Business not found' }, { status: 404 })
    }

    return NextResponse.json(business)
  } catch (error) {
    console.error('Business detail API error:', error)
    return NextResponse.json({ error: 'Failed to fetch business' }, { status: 500 })
  }
}

export async function PATCH(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params
  try {
    const body = await request.json()
    const existing = await prisma.business.findUnique({ where: { id } })
    if (!existing) {
      return NextResponse.json({ error: 'Business not found' }, { status: 404 })
    }

    // If stage changed, log it
    if (body.stage && body.stage !== existing.stage) {
      await prisma.stageLog.create({
        data: {
          businessId: id,
          fromStage: existing.stage,
          toStage: body.stage,
        },
      })

      await prisma.timelineEvent.create({
        data: {
          businessId: id,
          type: 'status_changed',
          title: 'Status Changed',
          description: `Moved from ${existing.stage} to ${body.stage}`,
        },
      })

      await prisma.activityLog.create({
        data: {
          type: 'status_changed',
          title: 'Lead Updated',
          description: `${existing.name} moved from ${existing.stage} to ${body.stage}`,
        },
      })
    }

    const business = await prisma.business.update({
      where: { id },
      data: body,
      include: {
        contacts: true,
        tags: { include: { tag: true } },
        assignedAgent: { select: { name: true, email: true } },
      },
    })

    return NextResponse.json(business)
  } catch (error) {
    console.error('Update business error:', error)
    return NextResponse.json({ error: 'Failed to update business' }, { status: 500 })
  }
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params
  try {
    await prisma.business.delete({ where: { id } })
    return NextResponse.json({ success: true })
  } catch (error) {
    console.error('Delete business error:', error)
    return NextResponse.json({ error: 'Failed to delete business' }, { status: 500 })
  }
}