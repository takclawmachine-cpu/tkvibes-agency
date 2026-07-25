import { NextRequest, NextResponse } from 'next/server'
import prisma from '@/lib/prisma'

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url)
  const q = searchParams.get('q') || ''

  if (!q || q.length < 2) {
    return NextResponse.json({ results: [] })
  }

  try {
    const businesses = await prisma.business.findMany({
      where: {
        OR: [
          { name: { contains: q } },
          { phone: { contains: q } },
          { email: { contains: q } },
          { address: { contains: q } },
          { category: { contains: q } },
          { notesText: { contains: q } },
          { industry: { contains: q } },
        ],
      },
      select: {
        id: true,
        name: true,
        logo: true,
        category: true,
        stage: true,
        leadScore: true,
      },
      take: 20,
    })

    const tasks = await prisma.task.findMany({
      where: {
        title: { contains: q },
      },
      select: {
        id: true,
        title: true,
        status: true,
        businessId: true,
        business: { select: { name: true } },
      },
      take: 10,
    })

    return NextResponse.json({
      results: [
        ...businesses.map(b => ({ type: 'business', ...b })),
        ...tasks.map(t => ({ type: 'task', ...t })),
      ],
    })
  } catch (error) {
    return NextResponse.json({ error: 'Search failed' }, { status: 500 })
  }
}