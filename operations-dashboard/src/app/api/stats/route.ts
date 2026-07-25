import { NextResponse } from 'next/server'
import prisma from '@/lib/prisma'

export async function GET() {
  try {
    const [
      totalBusinesses,
      websites,
      pitchDecks,
      emails,
      replies,
      meetings,
      proposals,
      won,
      overdueTasks,
      todayTasks,
      weeklyActivity,
      monthlyActivity,
      stageCounts,
      recentActivity,
      agents,
      skills,
    ] = await Promise.all([
      prisma.business.count(),
      prisma.generatedAsset.count({ where: { type: 'website' } }),
      prisma.generatedAsset.count({ where: { type: 'pitch_deck' } }),
      prisma.email.count({ where: { status: { in: ['sent', 'delivered', 'opened', 'clicked', 'replied'] } } }),
      prisma.email.count({ where: { status: 'replied' } }),
      prisma.meeting.count({ where: { status: { not: 'cancelled' } } }),
      prisma.proposal.count({ where: { status: 'accepted' } }),
      prisma.business.count({ where: { stage: 'Won' } }),
      prisma.task.count({ where: { status: 'pending', dueDate: { lt: new Date() } } }),
      prisma.task.count({ where: { status: 'pending', dueDate: { gte: new Date(new Date().setHours(0, 0, 0, 0)), lt: new Date(new Date().setHours(23, 59, 59, 999)) } } }),
      prisma.activityLog.count({ where: { createdAt: { gte: new Date(Date.now() - 7 * 86400000) } } }),
      prisma.activityLog.count({ where: { createdAt: { gte: new Date(Date.now() - 30 * 86400000) } } }),
      prisma.business.groupBy({ by: ['stage'], _count: true }),
      prisma.activityLog.findMany({ orderBy: { createdAt: 'desc' }, take: 10 }),
      prisma.agentStatus.findMany({ orderBy: { name: 'asc' } }),
      prisma.skillStatus.findMany({ orderBy: { name: 'asc' } }),
    ])

    // Calculate conversion rate
    const totalWithOutreach = await prisma.email.count({
      where: { status: { in: ['sent', 'delivered', 'opened', 'clicked', 'replied'] } },
    })
    const conversionRate = totalBusinesses > 0
      ? Math.round((won / totalBusinesses) * 100)
      : 0

    // Revenue from won businesses
    const revenueBusinesses = await prisma.business.findMany({
      where: { stage: 'Won', expectedRevenue: { not: null } },
      select: { expectedRevenue: true },
    })
    const revenueClosed = revenueBusinesses.reduce((sum, b) => sum + (b.expectedRevenue || 0), 0)

    // Weekly data points for charts
    const weeklyLabels: string[] = []
    const weeklyLeads: number[] = []
    const weeklyEmails: number[] = []
    const weeklyReplies: number[] = []
    const weeklyConversions: number[] = []
    const weeklyRevenue: number[] = []

    for (let i = 6; i >= 0; i--) {
      const day = new Date(Date.now() - i * 86400000)
      const dayStart = new Date(day.setHours(0, 0, 0, 0))
      const dayEnd = new Date(new Date(day).setHours(23, 59, 59, 999))

      const dayLabel = dayStart.toLocaleDateString('en-US', { weekday: 'short' })
      weeklyLabels.push(dayLabel)

      const [leads, emailsDay, repliesDay, conversionsDay, revenueDay] = await Promise.all([
        prisma.business.count({ where: { createdAt: { gte: dayStart, lte: dayEnd } } }),
        prisma.email.count({ where: { createdAt: { gte: dayStart, lte: dayEnd }, status: { in: ['sent', 'delivered', 'opened', 'clicked', 'replied'] } } }),
        prisma.email.count({ where: { createdAt: { gte: dayStart, lte: dayEnd }, status: 'replied' } }),
        prisma.business.count({ where: { updatedAt: { gte: dayStart, lte: dayEnd }, stage: 'Won' } }),
        prisma.business.aggregate({ where: { updatedAt: { gte: dayStart, lte: dayEnd }, stage: 'Won' }, _sum: { expectedRevenue: true } }),
      ])

      weeklyLeads.push(leads)
      weeklyEmails.push(emailsDay)
      weeklyReplies.push(repliesDay)
      weeklyConversions.push(conversionsDay)
      weeklyRevenue.push(revenueDay._sum.expectedRevenue || 0)
    }

    // Stage distribution
    const stageDistribution = stageCounts.map(s => ({
      stage: s.stage,
      count: s._count,
    }))

    // Industry distribution
    const industryCounts = await prisma.business.groupBy({ by: ['industry'], _count: true })
    const industryDistribution = industryCounts
      .filter(i => i.industry != null)
      .map(i => ({ industry: i.industry!, count: i._count }))

    // Lead score buckets
    const allScores = await prisma.business.findMany({ select: { leadScore: true } })
    const leadScoreDistribution = [
      { range: '0-20', count: 0 },
      { range: '21-40', count: 0 },
      { range: '41-60', count: 0 },
      { range: '61-80', count: 0 },
      { range: '81-100', count: 0 },
    ]
    for (const b of allScores) {
      if (b.leadScore <= 20) leadScoreDistribution[0].count++
      else if (b.leadScore <= 40) leadScoreDistribution[1].count++
      else if (b.leadScore <= 60) leadScoreDistribution[2].count++
      else if (b.leadScore <= 80) leadScoreDistribution[3].count++
      else leadScoreDistribution[4].count++
    }

    // Today's activity
    const todayStart = new Date(new Date().setHours(0, 0, 0, 0))
    const todayActivity = await prisma.activityLog.count({
      where: { createdAt: { gte: todayStart } },
    })

    // Overdue follow-ups count
    const overdueFollowUps = await prisma.task.count({
      where: { status: 'pending', dueDate: { lt: new Date() } },
    })

    return NextResponse.json({
      totalBusinesses,
      websitesGenerated: websites,
      pitchDecksGenerated: pitchDecks,
      emailsSent: emails,
      responsesReceived: replies,
      meetingsScheduled: meetings,
      proposalsAccepted: proposals,
      revenueClosed: revenueClosed,
      conversionRate,
      todayActivity,
      weeklyActivity,
      monthlyActivity,
      overdueFollowUps,
      weeklyLabels,
      weeklyLeads,
      weeklyEmails,
      weeklyReplies,
      weeklyConversions,
      weeklyRevenue,
      stageDistribution,
      industryDistribution,
      leadScoreDistribution,
      recentActivity,
      agents,
      skills,
    })
  } catch (error) {
    console.error('Stats API error:', error)
    return NextResponse.json({ error: 'Failed to fetch stats' }, { status: 500 })
  }
}