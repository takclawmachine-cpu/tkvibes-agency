import Link from 'next/link';
import WebsitePreview from '@/components/WebsitePreview';

export default function Home() {
  const services = [
    {
      icon: 'fa-paint-brush',
      color: '#4f46e5',
      bg: 'rgba(79,70,229,0.1)',
      title: 'Logo Designing',
      desc: 'Custom logo design that captures your brand essence. Professional, memorable, and scalable vector logos with multiple format deliveries.',
      tags: [
        { text: 'Brand Identity', bg: '#eef2ff', color: '#4f46e5' },
        { text: 'Vector Art', bg: '#fef3c7', color: '#d97706' },
      ],
    },
    {
      icon: 'fa-film',
      color: '#f59e0b',
      bg: 'rgba(245,158,11,0.1)',
      title: 'Logo Animation',
      desc: 'Dynamic logo animations that bring your brand to life. Perfect for intros, social media, and video content with smooth motion graphics.',
      tags: [
        { text: 'Motion Graphics', bg: '#fef3c7', color: '#d97706' },
        { text: 'Brand Video', bg: '#eef2ff', color: '#4f46e5' },
      ],
    },
    {
      icon: 'fa-laptop-code',
      color: '#0891b2',
      bg: 'rgba(6,182,212,0.1)',
      title: 'Website Designing',
      desc: 'Professional business websites built with modern tech stacks. Responsive, SEO-optimized, and conversion-focused designs for every industry.',
      tags: [
        { text: 'Responsive', bg: '#ecfdf5', color: '#059669' },
        { text: 'SEO Ready', bg: '#eef2ff', color: '#4f46e5' },
      ],
    },
    {
      icon: 'fa-server',
      color: '#059669',
      bg: 'rgba(16,185,129,0.1)',
      title: 'Hosting Management',
      desc: 'Reliable hosting setup, migration, and ongoing management. Fast CDN, SSL certificates, daily backups, and 24/7 uptime monitoring.',
      tags: [
        { text: 'Managed Hosting', bg: '#ecfdf5', color: '#059669' },
        { text: '24/7 Support', bg: '#eef2ff', color: '#4f46e5' },
      ],
    },
    {
      icon: 'fa-compass',
      color: '#7c3aed',
      bg: 'rgba(139,92,246,0.1)',
      title: 'Business Niche Advisory',
      desc: 'Expert guidance on selecting and positioning your business niche. Market research, competitor analysis, and strategic recommendations on request.',
      tags: [
        { text: 'Consulting', bg: '#f3e8ff', color: '#7c3aed' },
        { text: 'On Request', bg: '#eef2ff', color: '#4f46e5' },
      ],
    },
    {
      icon: 'fa-building',
      color: '#dc2626',
      bg: 'rgba(239,68,68,0.1)',
      title: 'Company Registration',
      desc: 'End-to-end assistance with company registration processes — GST, MSME, trademark filing, and business incorporation as per your requirements.',
      tags: [
        { text: 'Legal', bg: '#fef2f2', color: '#dc2626' },
        { text: 'Registration', bg: '#eef2ff', color: '#4f46e5' },
      ],
    },
    {
      icon: 'fa-file-alt',
      color: '#ea580c',
      bg: 'rgba(249,115,22,0.1)',
      title: 'Annual Reports',
      desc: 'Professionally designed annual reports that communicate your company\'s story, financial highlights, and milestones with visual elegance.',
      tags: [
        { text: 'Corporate', bg: '#fff7ed', color: '#ea580c' },
        { text: 'Reports', bg: '#eef2ff', color: '#4f46e5' },
      ],
    },
    {
      icon: 'fa-book-open',
      color: '#db2777',
      bg: 'rgba(236,72,153,0.1)',
      title: 'Product Brochure Design',
      desc: 'Eye-catching brochure designs for products and services. Print-ready files with compelling layouts that drive engagement and conversions.',
      tags: [
        { text: 'Print Design', bg: '#fdf2f8', color: '#db2777' },
        { text: 'Marketing', bg: '#eef2ff', color: '#4f46e5' },
      ],
    },
    {
      icon: 'fa-search',
      color: '#16a34a',
      bg: 'rgba(34,197,94,0.1)',
      title: 'SEO Services',
      desc: 'Comprehensive search engine optimization to improve your website rankings. On-page, off-page, technical SEO, and content strategy for sustainable growth.',
      tags: [
        { text: 'On-Page SEO', bg: '#ecfdf5', color: '#059669' },
        { text: 'Technical SEO', bg: '#eef2ff', color: '#4f46e5' },
      ],
    },
  ];

  const portfolioItems = [
    {
      url: '/websites/lets-smile-dental.html',
      gradient: 'linear-gradient(135deg,#1e3a5f,#2d5a87)',
      icon: 'fa-tooth',
      title: "Let's Smile Dental",
      desc: 'Complete digital transformation including responsive website, brand identity, and local SEO.',
      tag: 'Website + Branding',
      tagBg: '#eef2ff',
      tagColor: '#4f46e5',
    },
    {
      url: '/websites/tasty-bites-3d-cafe.html',
      gradient: 'linear-gradient(135deg,#0d4f3c,#1a7a5a)',
      icon: 'fa-mug-hot',
      title: 'Tasty Bites Cafe',
      desc: 'Brand identity, menu website, online ordering integration, and social media branding.',
      tag: 'Brand Identity',
      tagBg: '#fef3c7',
      tagColor: '#d97706',
    },
    {
      url: '/websites/deep-water-tank-cleaning-modern.html',
      gradient: 'linear-gradient(135deg,#2d1b69,#4f3597)',
      icon: 'fa-water',
      title: 'Deep Water Tank Cleaning',
      desc: 'Service website with local SEO, Google Ads integration, and customer review system.',
      tag: 'SEO + Website',
      tagBg: '#ecfdf5',
      tagColor: '#059669',
    },
  ];

  const pricingPlans = [
    {
      name: 'Starter',
      price: '₹4,999',
      desc: 'Perfect for startups and new businesses launching their brand identity.',
      features: [
        'Logo Design (2 unique concepts)',
        'Google My Business Profile Setup',
        'Social Media Profile Design (2 platforms)',
        'Professional Business Card Design',
        'Basic SEO Setup',
        '1 Month Post-Delivery Support',
        'High-Resolution File Formats',
      ],
      featured: false,
    },
    {
      name: 'Growth',
      price: '₹14,999',
      desc: 'Ideal for growing businesses ready for a complete digital presence.',
      features: [
        'Logo Design (4 concepts + revisions)',
        'Logo Animation (upto 5 seconds)',
        '5-Page Professional Website',
        'Hosting Setup (1 Year Free)',
        'GMB Complete Optimization',
        'Product Brochure Design (1 Page)',
        'On-Page SEO (10 Keywords)',
        'Free SSL Certificate',
        '3 Months Priority Support',
      ],
      featured: true,
    },
    {
      name: 'Enterprise',
      price: '₹34,999',
      desc: 'Complete digital transformation and marketing suite for established brands.',
      features: [
        'Complete Brand Identity + Stationery',
        'Logo Animation (HD, upto 10 seconds)',
        '10-Page Custom Website + CMS',
        'Hosting Management (1 Year)',
        'Comprehensive SEO (15 Keywords)',
        'Google Ads Campaign Setup',
        'Meta Ads Campaign Setup',
        'n8n Automation (3 workflows)',
        'Annual Report (upto 20 pages)',
        'Infographics Set (5 designs)',
        'Product Brochure (upto 3 pages)',
        '6 Months Dedicated Account Manager',
      ],
      featured: false,
    },
  ];

  const testimonials = [
    {
      initials: 'DR',
      gradient: 'linear-gradient(135deg,#4f46e5,#818cf8)',
      name: 'Dr. Rajesh Kumar',
      biz: "Let's Smile Dental",
      quote:
        'TKVibes completely transformed our dental clinic\'s online presence. The website is beautiful and we\'re getting appointment inquiries every day through the contact form.',
    },
    {
      initials: 'PK',
      gradient: 'linear-gradient(135deg,#f59e0b,#f97316)',
      name: 'Priya Kapoor',
      biz: 'Tasty Bites Cafe',
      quote:
        'The branding and website package gave our cafe a whole new identity. Customers love the new look and our online orders have increased significantly since the launch.',
    },
    {
      initials: 'AM',
      gradient: 'linear-gradient(135deg,#059669,#34d399)',
      name: 'Arun Mehta',
      biz: 'Deep Water Tank Cleaning',
      quote:
        'Their SEO and Google My Business services got us ranking on the first page within weeks. We\'re receiving calls daily from new customers finding us through Google.',
    },
  ];

  return (
    <>
      {/* ===== HERO ===== */}
      <section className="hero" id="home">
        <div className="container-main">
          <div className="hero-grid">
            <div className="hero-content">
              <div className="hero-badge">
                <i className="fas fa-sparkles"></i> Your Brand&apos;s Digital Transformation Partner
              </div>
              <h1>
                Digital Solutions That <span className="highlight">Amplify</span> Your Brand
              </h1>
              <p>
                From logo design and website development to SEO, Google Ads, and automation —
                TKVibes delivers end-to-end digital services that drive real business growth.
              </p>
              <div className="hero-buttons" style={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>
                <Link href="/services" className="btn-custom btn-primary-custom">
                  <i className="fas fa-arrow-right"></i> Explore Services
                </Link>
                <Link href="/portfolio" className="btn-custom btn-glass-custom">
                  <i className="fas fa-eye"></i> View Our Work
                </Link>
              </div>
              <div className="hero-stats">
                <div className="hero-stat">
                  <h3>
                    <span>50+</span>
                  </h3>
                  <p>Projects Delivered</p>
                </div>
                <div className="hero-stat">
                  <h3>
                    <span>5+</span>
                  </h3>
                  <p>Years Experience</p>
                </div>
                <div className="hero-stat">
                  <h3>
                    <span>98%</span>
                  </h3>
                  <p>Client Satisfaction</p>
                </div>
              </div>
            </div>
            <div className="hero-visual">
              <div className="hero-mockup">
                <div className="mockup-items">
                  <div className="floating-card">
                    <div className="icon-circle icon-purple">
                      <i className="fas fa-paint-brush"></i>
                    </div>
                    <div className="card-text">
                      <h4>Logo & Brand Identity</h4>
                      <p>Creative design that stands out</p>
                    </div>
                  </div>
                  <div className="floating-card">
                    <div className="icon-circle icon-gold">
                      <i className="fas fa-code"></i>
                    </div>
                    <div className="card-text">
                      <h4>Web Development</h4>
                      <p>Professional, responsive websites</p>
                    </div>
                  </div>
                  <div className="floating-card">
                    <div className="icon-circle icon-cyan">
                      <i className="fas fa-chart-line"></i>
                    </div>
                    <div className="card-text">
                      <h4>SEO & Digital Marketing</h4>
                      <p>Data-driven growth strategies</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ===== CLIENTS BAR ===== */}
      <section className="clients-bar">
        <div className="container-main">
          <h4>
            <i className="fas fa-handshake"></i> Trusted by Businesses Across Industries
          </h4>
          <div className="client-logos">
            <div className="client-item">
              <i className="fas fa-tooth"></i> Let&apos;s Smile Dental
            </div>
            <div className="client-item">
              <i className="fas fa-mug-hot"></i> Tasty Bites Cafe
            </div>
            <div className="client-item">
              <i className="fas fa-water"></i> Deep Water Tank
            </div>
            <div className="client-item">
              <i className="fas fa-hospital"></i> Dental Clinic
            </div>
          </div>
        </div>
      </section>

      {/* ===== SERVICES ===== */}
      <section className="section-padding" id="services">
        <div className="container-main">
          <h2 className="section-title">
            Our <span className="highlight">Services</span>
          </h2>
          <p className="section-subtitle">
            <i className="fas fa-bolt"></i> Comprehensive digital solutions tailored to elevate your
            brand — from identity creation to growth automation.
          </p>
          <div className="services-grid">
            {services.map((s, i) => (
              <div className="service-card" key={i}>
                <div
                  className="service-icon"
                  style={{ background: s.bg, color: s.color }}
                >
                  <i className={`fas ${s.icon}`}></i>
                </div>
                <h3>{s.title}</h3>
                <p>{s.desc}</p>
                <div className="service-tags">
                  {s.tags.map((t, j) => (
                    <span key={j} style={{ background: t.bg, color: t.color }}>
                      {t.text}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ===== ABOUT PREVIEW ===== */}
      <section className="section-padding about-preview">
        <div className="container-main">
          <div className="about-preview-grid">
            <div className="about-preview-image">
              <div
                style={{
                  width: '100%',
                  height: 400,
                  borderRadius: 'var(--radius)',
                  background: 'var(--gradient-hero)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '4rem',
                  color: 'rgba(255,255,255,0.15)',
                }}
              >
                <i className="fas fa-users"></i>
              </div>
              <div className="stats-badge">
                <h3>5+</h3>
                <p>Years of Excellence</p>
              </div>
            </div>
            <div className="about-preview-content">
              <h2>
                Why Businesses Choose <span style={{ background: 'var(--gradient-accent)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>TKVibes</span>
              </h2>
              <p>
                We&apos;re a passionate team of designers, developers, and digital strategists
                committed to helping businesses build a powerful online presence that drives real results.
              </p>
              <ul>
                <li>
                  <i className="fas fa-check"></i> 50+ successful projects across diverse industries
                </li>
                <li>
                  <i className="fas fa-check"></i> End-to-end digital services under one roof
                </li>
                <li>
                  <i className="fas fa-check"></i> Custom solutions tailored to your business goals
                </li>
                <li>
                  <i className="fas fa-check"></i> Transparent communication and regular updates
                </li>
                <li>
                  <i className="fas fa-check"></i> Affordable pricing with premium quality
                </li>
              </ul>
              <Link href="/about" className="btn-custom btn-primary-custom">
                <i className="fas fa-arrow-right"></i> Learn More About Us
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* ===== PORTFOLIO SHOWCASE ===== */}
      <section className="section-padding portfolio-showcase" id="portfolio">
        <div className="container-main">
          <h2 className="section-title">
            Our Recent <span className="highlight">Work</span>
          </h2>
          <p className="section-subtitle">
            Real projects delivered for real businesses across diverse industries.
          </p>
          <div className="portfolio-grid-main">
            {portfolioItems.map((item, i) => (
              <div className="portfolio-item" key={i}>
                <WebsitePreview src={item.url} title={item.title} />
                <div className="pf-overlay">
                  <h4>{item.title}</h4>
                  <p>{item.desc}</p>
                  <span
                    className="pf-tag"
                    style={{ background: item.tagBg, color: item.tagColor }}
                  >
                    {item.tag}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ===== PACKAGES PREVIEW ===== */}
      <section className="section-padding pricing-dark" id="packages">
        <div className="container-main">
          <h2 className="section-title white">
            Choose Your <span className="highlight">Plan</span>
          </h2>
          <p className="section-subtitle white">
            Pick the package that fits your needs, or let us create a custom solution for you.
          </p>
          <div className="pricing-grid-main">
            {pricingPlans.map((plan, i) => (
              <div className={`pricing-card ${plan.featured ? 'featured' : ''}`} key={i}>
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
                  className={`btn-custom ${plan.featured ? 'btn-primary-custom' : 'btn-glass-custom'}`}
                >
                  <i className="fas fa-arrow-right"></i> Choose {plan.name}
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ===== TESTIMONIALS ===== */}
      <section className="section-padding testimonials-section" id="testimonials">
        <div className="container-main">
          <h2 className="section-title">
            What Our <span className="highlight">Clients Say</span>
          </h2>
          <p className="section-subtitle">
            Feedback from the businesses we&apos;ve had the pleasure of working with.
          </p>
          <div className="testimonial-grid">
            {testimonials.map((t, i) => (
              <div className="testimonial-card" key={i}>
                <div className="stars">
                  {[...Array(5)].map((_, j) => (
                    <i className="fas fa-star" key={j}></i>
                  ))}
                </div>
                <blockquote>&ldquo;{t.quote}&rdquo;</blockquote>
                <div className="author">
                  <div className="avatar" style={{ background: t.gradient }}>
                    {t.initials}
                  </div>
                  <div className="info">
                    <h5>{t.name}</h5>
                    <p>{t.biz}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ===== CTA ===== */}
      <section className="cta-section">
        <div className="container-main">
          <h2>Ready to Transform Your Brand?</h2>
          <p>
            Let&apos;s discuss your project and create a custom digital strategy that drives real
            business growth.
          </p>
          <div className="cta-buttons">
            <Link href="/contact" className="btn-custom btn-primary-custom">
              <i className="fas fa-paper-plane"></i> Start Your Project
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
              <i className="fab fa-whatsapp"></i> Chat on WhatsApp
            </a>
          </div>
        </div>
      </section>
    </>
  );
}