import { NextRequest, NextResponse } from 'next/server'
import prisma from '@/lib/prisma'

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url)
  const type = searchParams.get('type') || ''
  const businessId = searchParams.get('businessId') || ''

  const where: Record<string, any> = {}
  if (type) where.type = type
  if (businessId) where.businessId = businessId

  try {
    const communications = await prisma.communication.findMany({
      where,
      orderBy: { createdAt: 'desc' },
      take: 100,
      include: {
        business: { select: { name: true, logo: true } },
      },
    })
    return NextResponse.json(communications)
  } catch (error) {
    return NextResponse.json({ error: 'Failed to fetch communications' }, { status: 500 })
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const communication = await prisma.communication.create({
      data: {
        businessId: body.businessId,
        type: body.type,
        subject: body.subject,
        content: body.content,
        direction: body.direction || 'outbound',
        status: body.status || 'completed',
      },
    })

    // Update business lastContact
    if (body.businessId) {
      await prisma.business.update({
        where: { id: body.businessId },
        data: { lastContact: new Date() },
      })
    }

    return NextResponse.json(communication, { status: 201 })
  } catch (error) {
    return NextResponse.json({ error: 'Failed to create communication' }, { status: 500 })
  }
}