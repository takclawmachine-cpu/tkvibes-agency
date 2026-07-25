import { NextRequest, NextResponse } from 'next/server'
import prisma from '@/lib/prisma'

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url)
  const search = searchParams.get('search') || ''
  const stage = searchParams.get('stage') || ''
  const category = searchParams.get('category') || ''
  const industry = searchParams.get('industry') || ''
  const minScore = searchParams.get('minScore') ? parseInt(searchParams.get('minScore')!) : undefined
  const maxScore = searchParams.get('maxScore') ? parseInt(searchParams.get('maxScore')!) : undefined
  const hasWebsite = searchParams.get('hasWebsite')
  const sortBy = searchParams.get('sortBy') || 'updatedAt'
  const sortOrder = searchParams.get('sortOrder') || 'desc'
  const page = parseInt(searchParams.get('page') || '1')
  const limit = parseInt(searchParams.get('limit') || '50')

  const where: Record<string, any> = {}

  if (search) {
    where.OR = [
      { name: { contains: search } },
      { phone: { contains: search } },
      { email: { contains: search } },
      { address: { contains: search } },
      { category: { contains: search } },
      { notesText: { contains: search } },
    ]
  }

  if (stage) where.stage = stage
  if (category) where.category = category
  if (industry) where.industry = industry
  if (minScore !== undefined) where.leadScore = { ...where.leadScore, gte: minScore }
  if (maxScore !== undefined) where.leadScore = { ...where.leadScore, lte: maxScore }
  if (hasWebsite === 'yes') where.websiteQuality = { not: 'none' }
  if (hasWebsite === 'no') where.websiteQuality = 'none'

  try {
    const [businesses, total] = await Promise.all([
      prisma.business.findMany({
        where,
        orderBy: { [sortBy]: sortOrder },
        skip: (page - 1) * limit,
        take: limit,
        include: {
          tags: { include: { tag: true } },
          contacts: true,
          _count: { select: { communications: true, emails: true, tasks: true, generatedAssets: true } },
        },
      }),
      prisma.business.count({ where }),
    ])

    return NextResponse.json({ businesses, total, page, totalPages: Math.ceil(total / limit) })
  } catch (error) {
    console.error('Businesses API error:', error)
    return NextResponse.json({ error: 'Failed to fetch businesses' }, { status: 500 })
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const business = await prisma.business.create({
      data: {
        name: body.name,
        logo: body.logo,
        category: body.category,
        address: body.address,
        phone: body.phone,
        email: body.email,
        website: body.website,
        googleMapsLink: body.googleMapsLink,
        googleRating: body.googleRating,
        reviewCount: body.reviewCount,
        websiteQuality: body.websiteQuality || 'none',
        businessSize: body.businessSize,
        industry: body.industry,
        hasPublicEmail: !!body.email,
        hasPhone: !!body.phone,
        socialMediaPresence: body.socialMediaPresence,
        notesText: body.notesText,
        stage: 'Discovered',
        leadScore: 0,
        priority: 'medium',
      },
    })

    // Create timeline event
    await prisma.timelineEvent.create({
      data: {
        businessId: business.id,
        type: 'lead_found',
        title: 'Business Discovered',
        description: `${business.name} was added to the pipeline`,
      },
    })

    await prisma.activityLog.create({
      data: {
        type: 'lead_found',
        title: 'Lead Found',
        description: `${business.name} was discovered`,
      },
    })

    return NextResponse.json(business, { status: 201 })
  } catch (error) {
    console.error('Create business error:', error)
    return NextResponse.json({ error: 'Failed to create business' }, { status: 500 })
  }
}