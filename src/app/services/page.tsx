import type { Metadata } from 'next'
import Link from 'next/link'

export const metadata: Metadata = {
  title: 'Services',
  description:
    'Explore TKVibes services across website design, branding, SEO, ads, hosting, and automation.',
}

const services = [
  {
    icon: 'fa-palette',
    title: 'Brand identity',
    description:
      'Logos, color systems, and branded assets that make businesses feel cohesive across web, print, and social.',
    features: [
      'Custom logo design',
      'Typography and color systems',
      'Brand guideline support',
      'Collateral and social assets',
    ],
  },
  {
    icon: 'fa-laptop-code',
    title: 'Website design and development',
    description:
      'Responsive, high-performance websites built to feel premium while making next steps obvious for visitors.',
    features: [
      'Custom multi-page websites',
      'Responsive layouts',
      'Conversion-focused sections',
      'Performance and SEO foundations',
    ],
  },
  {
    icon: 'fa-server',
    title: 'Hosting and maintenance',
    description:
      'Setup, hosting guidance, SSL, and technical upkeep so the site stays stable after launch.',
    features: [
      'Hosting setup and support',
      'SSL and domain configuration',
      'Backups and monitoring',
      'Launch assistance',
    ],
  },
  {
    icon: 'fa-magnifying-glass',
    title: 'SEO and local visibility',
    description:
      'Search optimization for businesses that need more discoverability, better rankings, and stronger local trust.',
    features: [
      'On-page SEO',
      'Technical audits',
      'Local SEO and citations',
      'Google Business Profile support',
    ],
  },
  {
    icon: 'fa-bullhorn',
    title: 'Paid acquisition',
    description:
      'Meta and Google ad campaigns structured around clear offers, cleaner creative, and measurable returns.',
    features: [
      'Google Search and Display',
      'Meta ads management',
      'Audience targeting',
      'Reporting and optimization',
    ],
  },
  {
    icon: 'fa-robot',
    title: 'Automation workflows',
    description:
      'n8n-powered workflows that reduce repetitive work and connect lead capture, notifications, and follow-up.',
    features: [
      'Workflow design',
      'App integrations',
      'Lead routing and notifications',
      'AI-assisted process support',
    ],
  },
]

const reasons = [
  {
    icon: 'fa-crosshairs',
    title: 'Strategy before styling',
    copy: 'We start with positioning, offer clarity, and user intent so the design has commercial direction.',
  },
  {
    icon: 'fa-cube',
    title: 'One connected system',
    copy: 'Brand, website, growth, and automation are treated as one experience rather than isolated tasks.',
  },
  {
    icon: 'fa-chart-simple',
    title: 'Built for momentum',
    copy: 'The work is designed to keep supporting the business after launch, not just look nice on day one.',
  },
]

export default function ServicesPage() {
  return (
    <>
      <section className="page-header">
        <div className="container-main">
          <div className="breadcrumb">
            <Link href="/">Home</Link>
            <span className="sep">/</span>
            <span className="current">Services</span>
          </div>
          <h1>
            Services for <span>Modern Growth</span>
          </h1>
          <p>
            We help businesses look sharper, communicate better, and run their digital presence
            with more confidence.
          </p>
        </div>
      </section>

      <section className="section-padding">
        <div className="container-main">
          <div className="section-heading centered">
            <span className="eyebrow">Capabilities</span>
            <h2 className="section-title">Everything we use to strengthen your digital presence.</h2>
          </div>

          <div className="service-detail-grid">
            {services.map((service) => (
              <article key={service.title} className="service-detail-card">
                <div className="sd-header">
                  <div className="sd-icon">
                    <i className={`fas ${service.icon}`} />
                  </div>
                  <div>
                    <h3>{service.title}</h3>
                    <p>{service.description}</p>
                  </div>
                </div>
                <div className="sd-body">
                  <ul>
                    {service.features.map((feature) => (
                      <li key={feature}>
                        <i className="fas fa-check" />
                        {feature}
                      </li>
                    ))}
                  </ul>
                </div>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="section-padding">
        <div className="container-main">
          <div className="section-heading centered">
            <span className="eyebrow">Why TKVibes</span>
            <h2 className="section-title">We build the work around trust and conversion.</h2>
            <p className="section-subtitle">
              The goal is not to add more visual noise. It is to make the business feel clearer,
              more premium, and easier to choose.
            </p>
          </div>

          <div className="why-grid">
            {reasons.map((reason) => (
              <article key={reason.title} className="why-card">
                <div className="icon">
                  <i className={`fas ${reason.icon}`} />
                </div>
                <h4>{reason.title}</h4>
                <p>{reason.copy}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="cta-section">
        <div className="container-main cta-panel">
          <span className="eyebrow">Need the right mix?</span>
          <h2>We can shape a service stack around your actual business goals.</h2>
          <p>
            If you need a website, brand refresh, search growth, or automation support, we can
            package it into one cleaner plan.
          </p>
          <div className="cta-buttons">
            <Link href="/contact" className="btn-custom btn-primary-custom">
              <i className="fas fa-paper-plane" />
              Request a Quote
            </Link>
            <Link href="/packages" className="btn-custom btn-outline-custom">
              <i className="fas fa-tags" />
              View Packages
            </Link>
          </div>
        </div>
      </section>
    </>
  )
}
