import { NextRequest, NextResponse } from 'next/server'
import prisma from '@/lib/prisma'

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url)
  const businessId = searchParams.get('businessId') || ''

  const where: Record<string, any> = {}
  if (businessId) where.businessId = businessId

  try {
    const emails = await prisma.email.findMany({
      where,
      orderBy: { createdAt: 'desc' },
      take: 100,
      include: {
        business: { select: { name: true } },
      },
    })
    return NextResponse.json(emails)
  } catch (error) {
    return NextResponse.json({ error: 'Failed to fetch emails' }, { status: 500 })
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const email = await prisma.email.create({ data: body })

    await prisma.activityLog.create({
      data: {
        type: 'email_sent',
        title: 'Email Sent',
        description: `Email "${body.subject}" sent to ${body.to}`,
      },
    })

    return NextResponse.json(email, { status: 201 })
  } catch (error) {
    return NextResponse.json({ error: 'Failed to create email' }, { status: 500 })
  }
}