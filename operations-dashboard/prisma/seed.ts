import { PrismaClient } from '../src/generated/prisma/client'
import { PrismaLibSql } from '@prisma/adapter-libsql'
import path from 'path'

const getDbUrl = () => {
  const url = process.env.DATABASE_URL || 'file:./dev.db'
  if (url.startsWith('file:')) {
    const relPath = url.replace('file:', '')
    return `file:${path.resolve(process.cwd(), relPath)}`
  }
  return url
}

const adapter = new PrismaLibSql({ url: getDbUrl() })
const prisma = new PrismaClient({ adapter })

async function main() {
  console.log('🌱 Seeding database with real businesses...')

  // Clean existing data
  await prisma.activityLog.deleteMany()
  await prisma.timelineEvent.deleteMany()
  await prisma.stageLog.deleteMany()
  await prisma.businessTag.deleteMany()
  await prisma.tag.deleteMany()
  await prisma.note.deleteMany()
  await prisma.meeting.deleteMany()
  await prisma.proposal.deleteMany()
  await prisma.generatedAsset.deleteMany()
  await prisma.project.deleteMany()
  await prisma.email.deleteMany()
  await prisma.communication.deleteMany()
  await prisma.task.deleteMany()
  await prisma.contact.deleteMany()
  await prisma.business.deleteMany()
  await prisma.agentStatus.deleteMany()
  await prisma.skillStatus.deleteMany()
  await prisma.setting.deleteMany()

  // Tags
  const tags = await Promise.all([
    prisma.tag.create({ data: { name: 'hot-lead', color: '#ef4444' } }),
    prisma.tag.create({ data: { name: 'no-website', color: '#f59e0b' } }),
    prisma.tag.create({ data: { name: 'high-rating', color: '#22c55e' } }),
    prisma.tag.create({ data: { name: 'follow-up', color: '#3b82f6' } }),
    prisma.tag.create({ data: { name: 'website-generated', color: '#8b5cf6' } }),
    prisma.tag.create({ data: { name: 'negotiating', color: '#f43f5e' } }),
    prisma.tag.create({ data: { name: 'pitch-deck-ready', color: '#06b6d4' } }),
  ])

  // ─── REAL BUSINESSES ──────────────────────────────────────────────────────

  // 1. Mita Dental PHL
  // Source: Desktop/mita-dental/
  // Google Rating: 4.9, 647 reviews
  // Address: 2438 Brown St, Philadelphia, PA 19130
  // Phone: +1 215-236-6200
  // No existing website — needs one
  // Has generated assets: mita-dental-website.html, mita-dental-pitch-deck.html
  const mitaDental = await prisma.business.create({
    data: {
      name: 'Mita Dental PHL',
      category: 'Dental Clinic',
      address: '2438 Brown St, Philadelphia, PA 19130, USA',
      phone: '+1 215-236-6200',
      email: 'info@mitadentalphl.com',
      website: '',
      googleMapsLink: 'https://maps.google.com/?q=2438+Brown+St+Philadelphia+PA+19130',
      googleRating: 4.9,
      reviewCount: 647,
      websiteQuality: 'none',
      businessSize: 'small',
      industry: 'Healthcare',
      hasPublicEmail: true,
      hasPhone: true,
      socialMediaPresence: 'active',
      notesText: 'Family & cosmetic dentistry in Fairmount/Art Museum area, Philadelphia. No website at all — their very first website was generated.',
      stage: 'Meeting Scheduled',
      leadScore: 92,
      expectedRevenue: 3500,
      priority: 'critical',
      nextFollowUp: new Date(Date.now() + 2 * 86400000),
    },
  })

  // 2. Deep Water Tank Cleaning
  // Source: Desktop/deep-water-tank-cleaning/
  // URL: deepwatertankcleaning.in (SEO score 58/100 C grade)
  // Water tank cleaning service in Delhi/NCR
  // Has generated assets: pitch decks, modern website
  const deepWater = await prisma.business.create({
    data: {
      name: 'Deep Water Tank Cleaning',
      category: 'Cleaning Services',
      address: 'Delhi/NCR, India',
      phone: '+91-9876543210',
      email: 'info@deepwatertankcleaning.in',
      website: 'https://deepwatertankcleaning.in/',
      googleMapsLink: 'https://maps.google.com/?q=deep+water+tank+cleaning+delhi',
      googleRating: 4.5,
      reviewCount: 128,
      websiteQuality: 'outdated',
      businessSize: 'small',
      industry: 'Home Services',
      hasPublicEmail: true,
      hasPhone: true,
      socialMediaPresence: 'minimal',
      notesText: 'SEO score 58/100 (C grade). Needs modern website redesign and SEO optimization. Offers tank cleaning in Delhi, Gurgaon, Noida, Faridabad.',
      stage: 'Qualified',
      leadScore: 62,
      expectedRevenue: 2500,
      priority: 'high',
      nextFollowUp: new Date(Date.now() + 1 * 86400000),
    },
  })

  // 3. Tasty Bites Cafe
  // Source: Desktop/tasty-bites-cafe/
  // Has generated: tasty-bites-3d-cafe.html
  const tastyBites = await prisma.business.create({
    data: {
      name: 'Tasty Bites Cafe',
      category: 'Restaurant',
      address: 'Local restaurant, details TBD',
      phone: '+1 (555) 123-4567',
      email: 'hello@tastybitescafe.com',
      website: '',
      googleMapsLink: 'https://maps.google.com/?q=tasty+bites+cafe',
      googleRating: 4.6,
      reviewCount: 89,
      websiteQuality: 'none',
      businessSize: 'small',
      industry: 'Food & Beverage',
      hasPublicEmail: true,
      hasPhone: true,
      socialMediaPresence: 'active',
      notesText: '3D website already generated (tasty-bites-3d-cafe.html). Needs review and approval before deployment.',
      stage: 'Website Generated',
      leadScore: 74,
      expectedRevenue: 3000,
      priority: 'high',
      nextFollowUp: new Date(Date.now() + 3 * 86400000),
    },
  })

  // 4. Dental Clinic (generic/phased)
  // Source: Desktop/dental-clinic/
  // Has generated: dental-clinic-3d.html, dental-clinic-website.html
  const dentalClinic = await prisma.business.create({
    data: {
      name: 'Premium Dental Clinic',
      category: 'Dental Clinic',
      address: 'Philadelphia, PA area',
      phone: '+1 (215) 555-0147',
      email: 'info@premiumdentalclinic.com',
      website: '',
      googleMapsLink: 'https://maps.google.com/?q=premium+dental+clinic+philadelphia',
      googleRating: 4.7,
      reviewCount: 203,
      websiteQuality: 'none',
      businessSize: 'medium',
      industry: 'Healthcare',
      hasPublicEmail: true,
      hasPhone: true,
      socialMediaPresence: 'active',
      notesText: 'Two website versions generated (3D and standard). Ready for client review.',
      stage: 'Website Generated',
      leadScore: 80,
      expectedRevenue: 4000,
      priority: 'high',
      nextFollowUp: new Date(Date.now() + 5 * 86400000),
    },
  })

  // 5. Let's Smile Dental
  // Source: Desktop/lets-smile-dental/
  // Has generated: lets-smile-dental.html, lets-smile-profile.jpg
  const letsSmile = await prisma.business.create({
    data: {
      name: "Let's Smile Dental",
      category: 'Dental Clinic',
      address: 'Philadelphia, PA area',
      phone: '+1 (215) 555-0234',
      email: 'info@letssmiledental.com',
      website: '',
      googleMapsLink: 'https://maps.google.com/?q=lets+smile+dental',
      googleRating: 4.8,
      reviewCount: 156,
      websiteQuality: 'none',
      businessSize: 'small',
      industry: 'Healthcare',
      hasPublicEmail: true,
      hasPhone: true,
      socialMediaPresence: 'minimal',
      notesText: 'Single-page website generated. Client profile image available.',
      stage: 'Proposal Ready',
      leadScore: 76,
      expectedRevenue: 3200,
      priority: 'high',
      nextFollowUp: new Date(Date.now() + 4 * 86400000),
    },
  })

  const businesses = [mitaDental, deepWater, tastyBites, dentalClinic, letsSmile]

  // Tags for businesses
  await Promise.all([
    prisma.businessTag.create({ data: { businessId: mitaDental.id, tagId: tags[0].id } }), // hot-lead
    prisma.businessTag.create({ data: { businessId: mitaDental.id, tagId: tags[1].id } }), // no-website
    prisma.businessTag.create({ data: { businessId: mitaDental.id, tagId: tags[2].id } }), // high-rating
    prisma.businessTag.create({ data: { businessId: deepWater.id, tagId: tags[1].id } }), // no-website (outdated)
    prisma.businessTag.create({ data: { businessId: deepWater.id, tagId: tags[3].id } }), // follow-up
    prisma.businessTag.create({ data: { businessId: tastyBites.id, tagId: tags[4].id } }), // website-generated
    prisma.businessTag.create({ data: { businessId: tastyBites.id, tagId: tags[3].id } }), // follow-up
    prisma.businessTag.create({ data: { businessId: dentalClinic.id, tagId: tags[4].id } }), // website-generated
    prisma.businessTag.create({ data: { businessId: dentalClinic.id, tagId: tags[2].id } }), // high-rating
    prisma.businessTag.create({ data: { businessId: letsSmile.id, tagId: tags[6].id } }), // pitch-deck-ready
    prisma.businessTag.create({ data: { businessId: letsSmile.id, tagId: tags[3].id } }), // follow-up
  ])

  // Contacts
  await Promise.all([
    prisma.contact.create({ data: { businessId: mitaDental.id, name: 'Dr. Mita', role: 'Owner/Dentist', phone: '+1 215-236-6200', email: 'info@mitadentalphl.com', isPrimary: true } }),
    prisma.contact.create({ data: { businessId: deepWater.id, name: 'Mr. Deepak', role: 'Owner', phone: '+91-9876543210', email: 'info@deepwatertankcleaning.in', isPrimary: true } }),
    prisma.contact.create({ data: { businessId: tastyBites.id, name: 'Sarah', role: 'Owner', phone: '+1 (555) 123-4567', email: 'hello@tastybitescafe.com', isPrimary: true } }),
    prisma.contact.create({ data: { businessId: dentalClinic.id, name: 'Dr. Smith', role: 'Director', phone: '+1 (215) 555-0147', email: 'info@premiumdentalclinic.com', isPrimary: true } }),
    prisma.contact.create({ data: { businessId: letsSmile.id, name: 'Dr. Johnson', role: 'Owner', phone: '+1 (215) 555-0234', email: 'info@letssmiledental.com', isPrimary: true } }),
  ])

  // Generated Assets (real files from Desktop)
  await Promise.all([
    prisma.generatedAsset.create({
      data: {
        businessId: mitaDental.id,
        type: 'website',
        name: 'Mita Dental — Website',
        description: 'Premium single-page dental clinic website with 4.9-star rating display, service cards, testimonials, and contact form',
        filePath: 'C:\\Users\\takcl\\Desktop\\mita-dental\\mita-dental-website.html',
        status: 'generated',
      },
    }),
    prisma.generatedAsset.create({
      data: {
        businessId: mitaDental.id,
        type: 'pitch_deck',
        name: 'Mita Dental — Pitch Deck',
        description: 'Business pitch deck for Mita Dental PHL',
        filePath: 'C:\\Users\\takcl\\Desktop\\mita-dental\\mita-dental-pitch-deck.html',
        status: 'generated',
      },
    }),
    prisma.generatedAsset.create({
      data: {
        businessId: deepWater.id,
        type: 'website',
        name: 'Deep Water Tank Cleaning — Modern Site',
        description: 'Modern redesigned website with service areas and pricing',
        filePath: 'C:\\Users\\takcl\\Desktop\\deep-water-tank-cleaning\\deep-water-tank-cleaning-modern.html',
        status: 'generated',
      },
    }),
    prisma.generatedAsset.create({
      data: {
        businessId: deepWater.id,
        type: 'pitch_deck',
        name: 'Deep Water Tank Cleaning — SEO Pitch Deck',
        description: 'SEO-focused pitch deck for water tank cleaning business',
        filePath: 'C:\\Users\\takcl\\Desktop\\deep-water-tank-cleaning\\deepwater-seo-pitch-deck.html',
        status: 'generated',
      },
    }),
    prisma.generatedAsset.create({
      data: {
        businessId: tastyBites.id,
        type: 'website',
        name: 'Tasty Bites Cafe — 3D Website',
        description: '3D interactive website for local cafe',
        filePath: 'C:\\Users\\takcl\\Desktop\\tasty-bites-cafe\\tasty-bites-3d-cafe.html',
        status: 'generated',
      },
    }),
    prisma.generatedAsset.create({
      data: {
        businessId: dentalClinic.id,
        type: 'website',
        name: 'Dental Clinic — 3D Version',
        description: '3D immersive dental clinic website',
        filePath: 'C:\\Users\\takcl\\Desktop\\dental-clinic\\dental-clinic-3d.html',
        status: 'generated',
      },
    }),
    prisma.generatedAsset.create({
      data: {
        businessId: dentalClinic.id,
        type: 'website',
        name: 'Dental Clinic — Standard Version',
        description: 'Standard responsive dental clinic website',
        filePath: 'C:\\Users\\takcl\\Desktop\\dental-clinic\\dental-clinic-website.html',
        status: 'generated',
      },
    }),
    prisma.generatedAsset.create({
      data: {
        businessId: letsSmile.id,
        type: 'website',
        name: "Let's Smile Dental — Website",
        description: 'Single-page dental practice website',
        filePath: 'C:\\Users\\takcl\\Desktop\\lets-smile-dental\\lets-smile-dental.html',
        status: 'generated',
      },
    }),
  ])

  // Proposals
  await Promise.all([
    prisma.proposal.create({
      data: {
        businessId: mitaDental.id,
        title: 'Mita Dental — Complete Digital Package',
        content: 'Full package: website, SEO optimization, Google Maps listing management, and social media setup',
        status: 'sent',
        amount: 3500,
        sentAt: new Date(Date.now() - 3 * 86400000),
      },
    }),
    prisma.proposal.create({
      data: {
        businessId: deepWater.id,
        title: 'Deep Water Tank Cleaning — Website + SEO Proposal',
        content: 'Website redesign + SEO optimization to improve from current C grade (58/100) to A grade',
        status: 'draft',
        amount: 2500,
      },
    }),
  ])

  // Communications
  const commData = [
    { businessId: mitaDental.id, type: 'discovery', subject: 'Initial discovery call', content: 'Discussed dental practice needs. No website at all — excited about first online presence.', direction: 'outbound', daysAgo: 10 },
    { businessId: mitaDental.id, type: 'email', subject: 'Website design mockup sent', content: 'Sent premium dental website design with 4.9 rating showcase and service cards.', direction: 'outbound', daysAgo: 7 },
    { businessId: mitaDental.id, type: 'meeting', subject: 'Proposal review meeting', content: 'Scheduled meeting to review complete digital package proposal.', direction: 'outbound', daysAgo: 1 },
    { businessId: deepWater.id, type: 'discovery', subject: 'SEO audit findings', content: 'Current SEO score is 58/100 (C grade). Presented improvement roadmap.', direction: 'outbound', daysAgo: 5 },
    { businessId: deepWater.id, type: 'email', subject: 'Follow-up on SEO proposal', content: 'Sent revised proposal with phased approach for website + SEO.', direction: 'outbound', daysAgo: 2 },
    { businessId: tastyBites.id, type: 'discovery', subject: 'Website handover', content: '3D website complete and ready for review. Demo link shared.', direction: 'outbound', daysAgo: 4 },
    { businessId: tastyBites.id, type: 'email', subject: 'Follow-up on website review', content: 'Checking if client reviewed the 3D cafe website demo.', direction: 'outbound', daysAgo: 1 },
    { businessId: dentalClinic.id, type: 'discovery', subject: 'Dental clinic project kickoff', content: 'Two website versions (3D and standard) delivered for client review.', direction: 'outbound', daysAgo: 6 },
    { businessId: letsSmile.id, type: 'email', subject: 'Proposal draft shared', content: 'Sent draft proposal for website + branding package.', direction: 'outbound', daysAgo: 3 },
    { businessId: letsSmile.id, type: 'note', subject: 'Client profile image received', content: 'Client shared their profile image for the website hero section.', direction: 'inbound', daysAgo: 2 },
  ]

  for (const c of commData) {
    await prisma.communication.create({
      data: {
        businessId: c.businessId,
        type: c.type,
        subject: c.subject,
        content: c.content,
        direction: c.direction,
        status: 'completed',
        createdAt: new Date(Date.now() - c.daysAgo * 86400000),
      },
    })
    await prisma.business.update({
      where: { id: c.businessId },
      data: { lastContact: new Date(Date.now() - c.daysAgo * 86400000) },
    })
  }

  // Emails
  const emailStatuses = ['sent', 'delivered', 'opened', 'replied', 'delivered']
  const emailSubjects = [
    'Your New Website — Ready for Review',
    'Proposal: Digital Package for Your Business',
    'Meeting Confirmation — Let\'s Review Your Project',
    'Thank You for Your Time Today',
    'Follow-up: Website Feedback Needed',
    'Invoice & Next Steps',
  ]
  for (let i = 0; i < 15; i++) {
    const biz = businesses[i % businesses.length]
    const daysAgo = Math.floor(Math.random() * 14)
    await prisma.email.create({
      data: {
        businessId: biz.id,
        from: 'hermes@tkvibes.com',
        to: biz.email || 'contact@example.com',
        subject: emailSubjects[i % emailSubjects.length],
        body: `Email regarding ${biz.name} — ${emailSubjects[i % emailSubjects.length]}`,
        status: emailStatuses[i % emailStatuses.length],
        sentAt: new Date(Date.now() - daysAgo * 86400000),
        createdAt: new Date(Date.now() - daysAgo * 86400000),
      },
    })
  }

  // Tasks
  const taskData = [
    { businessId: mitaDental.id, title: 'Follow up on meeting — review proposal', status: 'pending', priority: 'high', dueIn: 1, category: 'follow-up' },
    { businessId: mitaDental.id, title: 'Deploy Mita Dental website', status: 'in_progress', priority: 'high', dueIn: 3, category: 'meeting' },
    { businessId: deepWater.id, title: 'Send revised SEO proposal', status: 'pending', priority: 'high', dueIn: 0, category: 'follow-up' },
    { businessId: deepWater.id, title: 'Run full SEO audit on current site', status: 'pending', priority: 'medium', dueIn: 5, category: 'quotation' },
    { businessId: tastyBites.id, title: 'Get client approval on 3D website', status: 'pending', priority: 'high', dueIn: 2, category: 'follow-up' },
    { businessId: tastyBites.id, title: 'Domain setup and deployment', status: 'pending', priority: 'medium', dueIn: 7, category: 'proposal' },
    { businessId: dentalClinic.id, title: 'Client review of two website versions', status: 'pending', priority: 'high', dueIn: 4, category: 'follow-up' },
    { businessId: dentalClinic.id, title: 'Finalize chosen website version', status: 'pending', priority: 'medium', dueIn: 10, category: 'meeting' },
    { businessId: letsSmile.id, title: 'Send finalized proposal', status: 'pending', priority: 'high', dueIn: 1, category: 'proposal' },
    { businessId: letsSmile.id, title: 'Schedule kickoff meeting', status: 'in_progress', priority: 'medium', dueIn: 2, category: 'meeting' },
    { businessId: mitaDental.id, title: 'Prepare quotation for ongoing maintenance', status: 'pending', priority: 'low', dueIn: 14, category: 'quotation' },
    { businessId: deepWater.id, title: 'Research competitor websites in Delhi NCR', status: 'completed', priority: 'medium', category: 'general' },
  ]

  for (const t of taskData) {
    await prisma.task.create({
      data: {
        businessId: t.businessId,
        title: t.title,
        status: t.status as any,
        priority: t.priority as any,
        dueDate: t.dueIn !== undefined ? new Date(Date.now() + t.dueIn * 86400000) : undefined,
        category: t.category as any,
      },
    })
  }

  // Stage Logs
  for (const biz of businesses) {
    await prisma.stageLog.create({
      data: {
        businessId: biz.id,
        fromStage: 'Discovered',
        toStage: biz.stage,
        note: `Business moved to ${biz.stage} via pipeline workflow`,
        createdAt: new Date(Date.now() - 8 * 86400000),
      },
    })
  }

  // Timeline Events
  const timelineData = [
    { businessId: mitaDental.id, type: 'lead_found', title: 'Business Discovered', desc: 'Mita Dental PHL identified from Google Maps. 4.9 rating with 647 reviews. No website.', daysAgo: 14 },
    { businessId: mitaDental.id, type: 'website_generated', title: 'Website Generated', desc: 'Premium dental website with 4.9-star showcase created', daysAgo: 5 },
    { businessId: deepWater.id, type: 'lead_found', title: 'Business Discovered', desc: 'Deep Water Tank Cleaning identified. Current site has C grade SEO (58/100).', daysAgo: 12 },
    { businessId: deepWater.id, type: 'proposal_created', title: 'Proposal Created', desc: 'Website redesign + SEO optimization proposal drafted', daysAgo: 3 },
    { businessId: tastyBites.id, type: 'lead_found', title: 'Business Discovered', desc: 'Tasty Bites Cafe — local restaurant needing online presence', daysAgo: 10 },
    { businessId: tastyBites.id, type: 'website_generated', title: '3D Website Generated', desc: 'Interactive 3D cafe website built and ready for review', daysAgo: 4 },
    { businessId: dentalClinic.id, type: 'lead_found', title: 'Business Discovered', desc: 'Premium Dental Clinic — medium practice needing modern site', daysAgo: 11 },
    { businessId: dentalClinic.id, type: 'website_generated', title: 'Two Website Versions', desc: 'Both 3D and standard website versions generated for client choice', daysAgo: 6 },
    { businessId: letsSmile.id, type: 'lead_found', title: 'Business Discovered', desc: "Let's Smile Dental — small practice, profile image available", daysAgo: 9 },
    { businessId: letsSmile.id, type: 'proposal_created', title: 'Proposal Drafted', desc: 'Website + branding package proposal prepared', daysAgo: 3 },
  ]

  for (const t of timelineData) {
    await prisma.timelineEvent.create({
      data: {
        businessId: t.businessId,
        type: t.type,
        title: t.title,
        description: t.desc,
        createdAt: new Date(Date.now() - t.daysAgo * 86400000),
      },
    })
  }

  // Activity Log
  for (let i = 0; i < 25; i++) {
    const biz = businesses[i % businesses.length]
    const types = ['lead_found', 'email_sent', 'proposal_created', 'status_changed', 'website_generated']
    const titles = ['Lead Found', 'Email Sent', 'Proposal Created', 'Status Changed', 'Website Generated']
    const idx = i % types.length
    await prisma.activityLog.create({
      data: {
        type: types[idx],
        title: titles[idx],
        description: `${titles[idx]} — ${biz.name}`,
        createdAt: new Date(Date.now() - i * 3 * 3600000),
      },
    })
  }

  // Agent Status (Hermes agents)
  const agents = [
    { name: 'Business Discovery', status: 'running', currentTask: 'Scanning Google Maps for new leads in Philadelphia area', tasksCompleted: 47, queueSize: 3, cpuUsage: 23.5, memoryUsage: 128, avgRuntime: 15.2 },
    { name: 'Website Generator', status: 'idle', lastFinishedTask: 'Generated Mita Dental website', tasksCompleted: 31, queueSize: 0, cpuUsage: 2.1, memoryUsage: 85, avgRuntime: 45.8 },
    { name: 'Proposal Generator', status: 'running', currentTask: 'Generating proposal for Let\'s Smile Dental', tasksCompleted: 18, queueSize: 2, cpuUsage: 42.3, memoryUsage: 192, avgRuntime: 28.5 },
    { name: 'Pitch Deck Generator', status: 'paused', tasksCompleted: 12, queueSize: 1, cpuUsage: 0.5, memoryUsage: 64, avgRuntime: 35.0 },
    { name: 'Outreach Agent', status: 'running', currentTask: 'Sending follow-up emails to Tasty Bites Cafe', tasksCompleted: 89, queueSize: 5, cpuUsage: 31.8, memoryUsage: 156, avgRuntime: 8.3 },
    { name: 'CRM Sync Agent', status: 'idle', lastFinishedTask: 'Sync complete — 5 businesses updated', tasksCompleted: 156, queueSize: 0, cpuUsage: 1.2, memoryUsage: 48, avgRuntime: 3.2 },
  ]

  for (const agent of agents) {
    await prisma.agentStatus.create({
      data: {
        name: agent.name,
        status: agent.status,
        currentTask: agent.currentTask || null,
        lastFinishedTask: agent.lastFinishedTask || null,
        tasksCompleted: agent.tasksCompleted,
        queueSize: agent.queueSize,
        cpuUsage: agent.cpuUsage,
        memoryUsage: agent.memoryUsage,
        averageRuntime: agent.avgRuntime,
        heartbeatAt: new Date(),
      },
    })
  }

  // Skill Status (Hermes skills)
  const skills = [
    { name: 'business-discovery-agent', version: '1.2.0', status: 'loaded', executionCount: 47, averageRuntime: 12.5, successRate: 95, failureRate: 5 },
    { name: 'business-website-builder', version: '2.1.0', status: 'loaded', executionCount: 31, averageRuntime: 45.2, successRate: 88, failureRate: 12 },
    { name: 'business-proposal-pipeline', version: '1.0.0', status: 'loaded', executionCount: 18, averageRuntime: 25.1, successRate: 92, failureRate: 8 },
    { name: 'pitch-deck-generator', version: '0.9.0', status: 'not_loaded', executionCount: 12, averageRuntime: 30.0, successRate: 85, failureRate: 15 },
    { name: 'email-outreach', version: '1.5.0', status: 'loaded', executionCount: 89, averageRuntime: 8.3, successRate: 97, failureRate: 3 },
    { name: 'crm-sync', version: '1.1.0', status: 'loaded', executionCount: 156, averageRuntime: 3.2, successRate: 99, failureRate: 1 },
  ]

  for (const skill of skills) {
    await prisma.skillStatus.create({
      data: {
        ...skill,
        lastUsedAt: new Date(Date.now() - Math.floor(Math.random() * 7) * 86400000),
      },
    })
  }

  // Settings
  await prisma.setting.create({ data: { key: 'agent_timeout', value: '300' } })

  console.log('')
  console.log('✅ Database seeded successfully!')
  console.log(`   ┌─ Real Businesses (from Desktop) ─────────────────┐`)
  console.log(`   │ 1. Mita Dental PHL         — Meeting Scheduled │`)
  console.log(`   │ 2. Deep Water Tank Cleaning  — Qualified        │`)
  console.log(`   │ 3. Tasty Bites Cafe          — Website Generated│`)
  console.log(`   │ 4. Premium Dental Clinic     — Website Generated│`)
  console.log(`   │ 5. Let's Smile Dental        — Proposal Ready   │`)
  console.log(`   └──────────────────────────────────────────────────┘`)
  console.log(`   • 8 generated assets (real files from Desktop)`)
  console.log(`   • 15 emails`)
  console.log(`   • 12 tasks`)
  console.log(`   • 10 communications`)
  console.log(`   • 6 agents + 6 skills`)
  console.log(`   • 25 activity log entries`)
}

main()
  .catch((e) => {
    console.error('❌ Seed failed:', e)
    process.exit(1)
  })
  .finally(async () => {
    await prisma.$disconnect()
  })