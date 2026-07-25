'use client'

import Link from 'next/link'

const plans = [
  {
    name: 'Starter',
    price: 'Rs 4,999',
    description: 'A lean package for new businesses that need a cleaner first impression.',
    features: [
      'Logo design concepts',
      'Google Business Profile setup',
      'Business card design',
      'Basic SEO setup',
      'One month support',
    ],
    featured: false,
  },
  {
    name: 'Growth',
    price: 'Rs 14,999',
    description: 'Best for businesses ready to pair branding with a serious website launch.',
    features: [
      'Expanded logo and brand work',
      'Five-page business website',
      'Hosting setup assistance',
      'Google Business optimization',
      'On-page SEO setup',
      'Three months priority support',
    ],
    featured: true,
  },
  {
    name: 'Enterprise',
    price: 'Rs 34,999',
    description: 'A broader digital package for established businesses that need more scale.',
    features: [
      'Full brand identity package',
      'Larger custom website build',
      'Managed hosting guidance',
      'SEO plus technical audit',
      'Ads setup and launch support',
      'Automation workflow planning',
    ],
    featured: false,
  },
]

const addons = [
  {
    icon: 'fa-chart-line',
    title: 'Technical SEO audit',
    description: 'A detailed review of structure, indexing, speed, and conversion blockers.',
    price: 'Rs 2,999',
  },
  {
    icon: 'fa-bullhorn',
    title: 'Monthly ad management',
    description: 'Ongoing optimization for Google or Meta campaigns with reporting.',
    price: 'Rs 3,999 per month',
  },
  {
    icon: 'fa-sitemap',
    title: 'n8n workflow setup',
    description: 'A custom automation workflow for lead routing, notifications, or follow-up.',
    price: 'Rs 2,499',
  },
  {
    icon: 'fa-file-lines',
    title: 'Brochure or deck design',
    description: 'Sales-ready presentation or brochure assets aligned to your new web presence.',
    price: 'Rs 1,999 and up',
  },
]

const faqs = [
  {
    question: 'How long does delivery usually take?',
    answer:
      'Starter work can often be delivered in a few business days. Larger website and branding packages take longer depending on scope and feedback cycles.',
  },
  {
    question: 'Can we customize a package?',
    answer:
      'Yes. These packages are starting points. We can combine branding, website, SEO, ads, and automation into a custom plan.',
  },
  {
    question: 'Do revisions come with the packages?',
    answer:
      'Yes. Every package includes revision rounds. The exact number depends on the package size and scope agreed at kickoff.',
  },
  {
    question: 'Do you provide support after launch?',
    answer:
      'Yes. Each package includes post-delivery support, and longer ongoing support can be added when needed.',
  },
]

export default function PackagesPage() {
  return (
    <>
      <section className="page-header">
        <div className="container-main">
          <div className="breadcrumb">
            <Link href="/">Home</Link>
            <span className="sep">/</span>
            <span className="current">Packages</span>
          </div>
          <h1>
            Simple <span>Packages</span>
          </h1>
          <p>
            Clear starting points for businesses that want to upgrade their website, branding, or
            both without overcomplicating the process.
          </p>
        </div>
      </section>

      <section className="section-padding">
        <div className="container-main">
          <div className="section-heading centered">
            <span className="eyebrow">Pricing</span>
            <h2 className="section-title">Choose the package that matches your stage.</h2>
            <p className="section-subtitle">
              If none of these fit exactly, we can shape a custom combination around your current
              priorities.
            </p>
          </div>

          <div className="pricing-grid">
            {plans.map((plan) => (
              <article
                key={plan.name}
                className={`pricing-card-light${plan.featured ? ' featured' : ''}`}
              >
                {plan.featured ? <div className="popular-badge">Most Popular</div> : null}
                <div className="plan-name">{plan.name}</div>
                <div className="plan-price">
                  {plan.price} <small>per project</small>
                </div>
                <div className="plan-desc">{plan.description}</div>
                <ul className="plan-features">
                  {plan.features.map((feature) => (
                    <li key={feature}>
                      <i className="fas fa-check" />
                      {feature}
                    </li>
                  ))}
                </ul>
                <Link href="/contact" className="btn-custom btn-primary-custom">
                  <i className="fas fa-arrow-right" />
                  Choose {plan.name}
                </Link>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="section-padding">
        <div className="container-main">
          <div className="section-heading centered">
            <span className="eyebrow">Add-ons</span>
            <h2 className="section-title">Expand the package only where you need it.</h2>
          </div>

          <div className="addon-grid">
            {addons.map((addon) => (
              <article key={addon.title} className="addon-card">
                <div className="icon">
                  <i className={`fas ${addon.icon}`} />
                </div>
                <h4>{addon.title}</h4>
                <p>{addon.description}</p>
                <div className="price">{addon.price}</div>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="section-padding">
        <div className="container-main">
          <div className="custom-plan-card">
            <span className="eyebrow">Custom scope</span>
            <h3>Need a plan tailored to your business?</h3>
            <p>
              Tell us what you already have, what is missing, and where growth is getting stuck.
              We will shape a practical package around that.
            </p>
            <Link href="/contact" className="btn-custom btn-primary-custom">
              <i className="fas fa-wand-magic-sparkles" />
              Request Custom Quote
            </Link>
          </div>
        </div>
      </section>

      <section className="section-padding">
        <div className="container-main">
          <div className="section-heading centered">
            <span className="eyebrow">FAQ</span>
            <h2 className="section-title">A few common package questions.</h2>
          </div>

          <div className="faq-grid">
            {faqs.map((faq) => (
              <details key={faq.question} className="faq-item">
                <summary>{faq.question}</summary>
                <div className="faq-answer">{faq.answer}</div>
              </details>
            ))}
          </div>
        </div>
      </section>

      <section className="cta-section">
        <div className="container-main cta-panel">
          <span className="eyebrow">Still deciding?</span>
          <h2>We can help you choose the right starting point.</h2>
          <p>
            If you are unsure whether to prioritize branding, website work, or growth systems, we
            can recommend the cleanest next move.
          </p>
          <div className="cta-buttons">
            <Link href="/contact" className="btn-custom btn-primary-custom">
              <i className="fas fa-paper-plane" />
              Contact Us
            </Link>
            <a
              href="https://wa.me/919818246938"
              className="btn-custom btn-outline-custom"
              target="_blank"
              rel="noopener noreferrer"
            >
              <i className="fab fa-whatsapp" />
              WhatsApp Us
            </a>
          </div>
        </div>
      </section>
    </>
  )
}
