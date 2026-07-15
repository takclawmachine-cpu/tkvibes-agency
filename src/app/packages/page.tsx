'use client';

import Link from 'next/link';

export default function PackagesPage() {
  const plans = [
    {
      name: 'Starter',
      price: '₹4,999',
      desc: 'Perfect for startups and new businesses launching their brand identity.',
      features: [
        'Logo Design (2 unique concepts)',
        'Google My Business Profile Setup & Verification',
        'Social Media Profile Design (2 platforms)',
        'Professional Business Card Design',
        'Basic SEO Setup (Title, Description, Keywords)',
        '1 Month Post-Delivery Support',
        'All Files in High-Resolution Formats',
      ],
      featured: false,
    },
    {
      name: 'Growth',
      price: '₹14,999',
      desc: 'Ideal for growing businesses ready for a complete digital presence.',
      features: [
        'Logo Design (4 unique concepts + revisions)',
        'Logo Animation (upto 5 seconds)',
        '5-Page Professional Business Website',
        'Hosting Setup & Configuration (1 Year Free)',
        'Google My Business Complete Optimization',
        'Product / Service Brochure Design (1 Page)',
        'On-Page SEO (10 Keywords with Tracking)',
        'Free SSL Certificate Installation',
        '3 Months Priority Support',
      ],
      featured: true,
    },
    {
      name: 'Enterprise',
      price: '₹34,999',
      desc: 'Complete digital transformation and marketing suite for established brands.',
      features: [
        'Complete Brand Identity (Logo + Guidelines + Stationery)',
        'Logo Animation (HD, upto 10 seconds)',
        '10-Page Custom Website (+ CMS Integration)',
        'Hosting Management (1 Year Fully Managed)',
        'Comprehensive SEO (15 Keywords + Technical Audit)',
        'Google Ads Campaign Setup & 30 Days Management',
        'Meta Ads (Facebook & Instagram) Campaign Setup',
        'n8n Automation Workflow (upto 3 workflows)',
        'Annual Report Design (upto 20 pages)',
        'Infographics Set (5 designs)',
        'Product Brochure (upto 3 pages)',
        '6 Months Dedicated Account Manager',
      ],
      featured: false,
    },
  ];

  const addons = [
    { icon: '🔍', title: 'Technical SEO Audit', desc: 'In-depth audit of site speed, core web vitals, mobile optimization & crawl errors.', price: '₹2,999' },
    { icon: '📈', title: 'Google Ads Month-on-Month', desc: 'Ongoing ad management with A/B testing, optimization & performance reports.', price: '₹3,999/mo' },
    { icon: '📱', title: 'Meta Ads (Per Campaign)', desc: 'Complete Facebook & Instagram ad setup with creative design & targeting.', price: '₹3,499' },
    { icon: '🤖', title: 'n8n Workflow (Per Workflow)', desc: 'Custom automation connecting your tools. Includes testing & deployment.', price: '₹2,499' },
    { icon: '📄', title: 'Company Registration', desc: 'End-to-end assistance for GST, MSME, trademark filing & business incorporation.', price: '₹1,999+' },
    { icon: '📊', title: 'Infographics (Per Design)', desc: 'Custom data visualization and illustrated infographics for any purpose.', price: '₹999' },
  ];

  const faqs = [
    {
      q: 'How long does it take to deliver a project?',
      a: 'Timelines depend on the package. Starter projects typically take 3-5 business days. Growth packages take 7-14 business days. Enterprise packages may take 15-30 business days depending on scope. We provide a clear timeline before starting any project.',
    },
    {
      q: 'Can I customize the packages?',
      a: 'Absolutely! All packages are customizable. You can mix and match services from different packages or add add-on services. Contact us for a custom quote tailored to your specific needs.',
    },
    {
      q: 'Do you provide revisions?',
      a: 'Yes, all packages include revisions. Starter includes 2 rounds, Growth includes 3 rounds, and Enterprise includes unlimited revisions during the project timeline. Additional revisions beyond the scope can be purchased separately.',
    },
    {
      q: 'What payment methods do you accept?',
      a: 'We accept bank transfers, UPI, PayPal, and credit/debit cards. A 50% advance is required to start the project, with the remaining 50% due upon delivery or as per agreed milestone schedule.',
    },
    {
      q: 'Do you provide ongoing support after delivery?',
      a: 'Yes, each package includes post-delivery support. Starter includes 1 month, Growth includes 3 months, and Enterprise includes 6 months of priority support. Extended support and maintenance packages are available separately.',
    },
  ];

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
            Our <span>Packages</span>
          </h1>
          <p>
            Transparent pricing with flexible plans for every business size and budget.
          </p>
        </div>
      </section>

      <section className="section-padding pricing-section">
        <div className="container-main">
          <h2 className="section-title">
            Choose Your <span className="highlight">Plan</span>
          </h2>
          <p className="section-subtitle">
            Pick the package that fits your needs, or let us create a custom solution for you.
          </p>

          <div className="pricing-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: 28, marginBottom: 60 }}>
            {plans.map((plan, i) => (
              <div className={`pricing-card-light ${plan.featured ? 'featured' : ''}`} key={i}>
                {plan.featured && <div className="popular-badge">Most Popular</div>}
                <div className="plan-name">{plan.name}</div>
                <div className="plan-price">
                  {plan.price} <small>/ project</small>
                </div>
                <div className="plan-desc">{plan.desc}</div>
                <ul className="plan-features">
                  {plan.features.map((f, j) => (
                    <li key={j}>
                      <i className="fas fa-check"></i> {f}
                    </li>
                  ))}
                </ul>
                <Link
                  href="/contact"
                  className={`btn-custom ${plan.featured ? 'btn-primary-custom' : 'btn-custom'}`}
                  style={plan.featured ? {} : { background: 'var(--primary)', color: '#fff' }}
                >
                  <i className="fas fa-arrow-right"></i> Choose {plan.name}
                </Link>
              </div>
            ))}
          </div>

          {/* ADD-ON SERVICES */}
          <h2 className="section-title">
            Add-On <span className="highlight">Services</span>
          </h2>
          <p className="section-subtitle">
            Enhance your package with these additional services.
          </p>
          <div className="addon-grid">
            {addons.map((a, i) => (
              <div className="addon-card" key={i}>
                <div className="icon">{a.icon}</div>
                <h4>{a.title}</h4>
                <p>{a.desc}</p>
                <div className="price">{a.price}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CUSTOM PLAN */}
      <section className="section-padding" style={{ background: '#f8faff', paddingTop: 0 }}>
        <div className="container-main">
          <div className="custom-plan-card">
            <h3>Need a Custom Plan?</h3>
            <p>
              Every business is unique. Tell us about your specific requirements and we&apos;ll
              create a tailored package that fits your exact needs and budget.
            </p>
            <Link href="/contact" className="btn-custom btn-primary-custom">
              <i className="fas fa-magic"></i> Request Custom Quote
            </Link>
          </div>
        </div>
      </section>

      {/* FAQ */}
      <section className="section-padding" style={{ background: '#fff' }}>
        <div className="container-main">
          <h2 className="section-title">
            Frequently Asked <span className="highlight">Questions</span>
          </h2>
          <p className="section-subtitle">
            Everything you need to know about our packages and process.
          </p>
          <div className="faq-grid">
            {faqs.map((faq, i) => (
              <details className="faq-item" key={i}>
                <summary>{faq.q}</summary>
                <div className="faq-answer">{faq.a}</div>
              </details>
            ))}
          </div>
        </div>
      </section>

      <section className="cta-section">
        <div className="container-main">
          <h2>Still Have Questions?</h2>
          <p>
            We&apos;re here to help you find the perfect package. Reach out for a free consultation.
          </p>
          <div className="cta-buttons">
            <Link href="/contact" className="btn-custom btn-primary-custom">
              <i className="fas fa-paper-plane"></i> Contact Us
            </Link>
            <a
              href="https://wa.me/919818246938"
              className="btn-custom"
              style={{
                background: 'rgba(255,255,255,0.1)',
                color: '#fff',
                border: '1px solid rgba(255,255,255,0.2)',
              }}
              target="_blank"
              rel="noopener noreferrer"
            >
              <i className="fab fa-whatsapp"></i> WhatsApp Us
            </a>
          </div>
        </div>
      </section>
    </>
  );
}