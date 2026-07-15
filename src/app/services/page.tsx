import type { Metadata } from 'next';
import Link from 'next/link';

export const metadata: Metadata = {
  title: 'Our Services',
  description:
    'Explore TKVibes full range of digital services: logo design, logo animation, website development, hosting, SEO, Google My Business, Meta Ads, Google Ads, n8n automation, and more.',
};

export default function ServicesPage() {
  const services = [
    {
      icon: 'fa-paint-brush',
      bg: 'rgba(79,70,229,0.1)',
      color: '#4f46e5',
      title: 'Logo Designing',
      desc: 'Custom logo design services that capture your brand\'s unique identity. We create memorable, scalable vector logos that make lasting impressions.',
      features: [
        'Custom logo concepts tailored to your brand',
        'Vector formats (AI, EPS, SVG, PDF)',
        'Color palette & typography recommendations',
        'Brand guideline document included',
      ],
      tags: [
        { text: 'Brand Identity', bg: '#eef2ff', color: '#4f46e5' },
        { text: 'Vector Art', bg: '#fef3c7', color: '#d97706' },
        { text: 'Minimalist', bg: '#ecfdf5', color: '#059669' },
        { text: 'Mascot Logo', bg: '#f3e8ff', color: '#7c3aed' },
      ],
    },
    {
      icon: 'fa-film',
      bg: 'rgba(245,158,11,0.1)',
      color: '#f59e0b',
      title: 'Logo Animation',
      desc: 'Dynamic logo animations that bring your brand identity to life. Perfect for video intros, social media, presentations, and digital advertising.',
      features: [
        '2D & 3D logo animation options',
        'Custom motion graphics & transitions',
        'Multiple format exports (MP4, GIF, Lottie)',
        'Optimized for web, social & broadcast',
      ],
      tags: [
        { text: 'Motion Graphics', bg: '#fef3c7', color: '#d97706' },
        { text: 'Brand Video', bg: '#eef2ff', color: '#4f46e5' },
        { text: 'Social Media', bg: '#fdf2f8', color: '#db2777' },
      ],
    },
    {
      icon: 'fa-laptop-code',
      bg: 'rgba(6,182,212,0.1)',
      color: '#0891b2',
      title: 'Website Designing',
      desc: 'Professional, responsive business websites built with modern technology. Custom designs optimized for performance, SEO, and conversions.',
      features: [
        'Custom multi-page business websites',
        'Mobile-first responsive design',
        'SEO-optimized structure & code',
        'Contact forms, maps & social integration',
      ],
      tags: [
        { text: 'Responsive', bg: '#ecfdf5', color: '#059669' },
        { text: 'SEO Ready', bg: '#eef2ff', color: '#4f46e5' },
        { text: 'E-Commerce', bg: '#fff7ed', color: '#ea580c' },
      ],
    },
    {
      icon: 'fa-server',
      bg: 'rgba(16,185,129,0.1)',
      color: '#059669',
      title: 'Hosting Management',
      desc: 'Reliable hosting setup, migration, and management services. We handle everything from domain configuration to performance optimization.',
      features: [
        'Managed hosting setup & configuration',
        'SSL certificate installation & renewal',
        'Daily backups & security monitoring',
        '24/7 uptime monitoring & support',
      ],
      tags: [
        { text: 'Managed Hosting', bg: '#ecfdf5', color: '#059669' },
        { text: '24/7 Support', bg: '#eef2ff', color: '#4f46e5' },
        { text: 'Cloud', bg: '#eff6ff', color: '#2563eb' },
      ],
    },
    {
      icon: 'fa-compass',
      bg: 'rgba(139,92,246,0.1)',
      color: '#7c3aed',
      title: 'Business Niche Advisory',
      desc: 'Strategic guidance on identifying and positioning your business niche. Expert market research and competitor analysis available on request.',
      features: [
        'Market research & niche identification',
        'Competitor analysis & gap assessment',
        'Brand positioning strategy',
        'Custom recommendations on request',
      ],
      tags: [
        { text: 'Consulting', bg: '#f3e8ff', color: '#7c3aed' },
        { text: 'On Request', bg: '#eef2ff', color: '#4f46e5' },
        { text: 'Strategy', bg: '#fef3c7', color: '#d97706' },
      ],
    },
    {
      icon: 'fa-building',
      bg: 'rgba(239,68,68,0.1)',
      color: '#dc2626',
      title: 'Company Registration',
      desc: 'Assistance with company registration processes including GST registration, MSME registration, trademark filing, and business incorporation.',
      features: [
        'GST registration assistance',
        'MSME / Udyam registration',
        'Trademark & copyright filing',
        'Business incorporation guidance',
      ],
      tags: [
        { text: 'Legal', bg: '#fef2f2', color: '#dc2626' },
        { text: 'Registration', bg: '#eef2ff', color: '#4f46e5' },
        { text: 'MSME', bg: '#ecfdf5', color: '#059669' },
      ],
    },
    {
      icon: 'fa-file-alt',
      bg: 'rgba(249,115,22,0.1)',
      color: '#ea580c',
      title: 'Annual Reports',
      desc: 'Professionally designed annual reports that articulate your company\'s story, achievements, financial performance, and future vision with elegance.',
      features: [
        'Custom layout & infographic design',
        'Financial data visualization',
        'Print-ready PDF & digital versions',
        'Consistent brand alignment',
      ],
      tags: [
        { text: 'Corporate', bg: '#fff7ed', color: '#ea580c' },
        { text: 'Reports', bg: '#eef2ff', color: '#4f46e5' },
        { text: 'Financial', bg: '#fdf2f8', color: '#db2777' },
      ],
    },
    {
      icon: 'fa-book-open',
      bg: 'rgba(236,72,153,0.1)',
      color: '#db2777',
      title: 'Product Brochure Design',
      desc: 'Eye-catching brochure designs for products and services. Print-ready digital files with compelling layouts that drive engagement and conversions.',
      features: [
        'Multi-fold & single-page brochure layouts',
        'Product catalog & service menu design',
        'Print-ready high-resolution files',
        'Digital flipbook versions available',
      ],
      tags: [
        { text: 'Print Design', bg: '#fdf2f8', color: '#db2777' },
        { text: 'Marketing', bg: '#eef2ff', color: '#4f46e5' },
        { text: 'Catalog', bg: '#ecfdf5', color: '#059669' },
      ],
    },
    {
      icon: 'fa-search',
      bg: 'rgba(34,197,94,0.1)',
      color: '#16a34a',
      title: 'SEO Services',
      desc: 'Comprehensive search engine optimization to improve your website rankings. On-page, off-page, technical SEO, and content strategy for sustainable growth.',
      features: [
        'On-page SEO & keyword optimization',
        'Technical SEO audit & fixes',
        'Off-page SEO & link building',
        'Local SEO & citation building',
      ],
      tags: [
        { text: 'On-Page SEO', bg: '#ecfdf5', color: '#059669' },
        { text: 'Technical SEO', bg: '#eef2ff', color: '#4f46e5' },
        { text: 'Local SEO', bg: '#fef3c7', color: '#d97706' },
      ],
    },
    {
      icon: 'fa-store',
      bg: 'rgba(59,130,246,0.1)',
      color: '#2563eb',
      title: 'Google My Business',
      desc: 'Complete Google Business Profile setup, optimization, and management. Boost local search visibility and attract more customers in your area.',
      features: [
        'GMB profile creation & verification',
        'Photo & post management',
        'Review monitoring & responses',
        'Insights tracking & monthly reports',
      ],
      tags: [
        { text: 'Local SEO', bg: '#eff6ff', color: '#2563eb' },
        { text: 'Visibility', bg: '#ecfdf5', color: '#059669' },
        { text: 'Maps', bg: '#eef2ff', color: '#4f46e5' },
      ],
    },
    {
      icon: 'fa-ad',
      bg: 'rgba(37,99,235,0.1)',
      color: '#2563eb',
      title: 'Meta & Google Ads',
      desc: 'Strategic paid advertising campaigns on Meta (Facebook & Instagram) and Google. Data-driven targeting, creative optimization, and ROI-focused management.',
      features: [
        'Google Search & Display campaigns',
        'Facebook & Instagram ad management',
        'Audience targeting & retargeting',
        'Performance tracking & weekly reports',
      ],
      tags: [
        { text: 'PPC', bg: '#eff6ff', color: '#2563eb' },
        { text: 'Social Ads', bg: '#fef3c7', color: '#d97706' },
        { text: 'ROI', bg: '#ecfdf5', color: '#059669' },
      ],
    },
    {
      icon: 'fa-robot',
      bg: 'rgba(168,85,247,0.1)',
      color: '#9333ea',
      title: 'n8n Automation Agents',
      desc: 'Custom n8n workflow automation for business processes. Connect 300+ apps, automate repetitive tasks, and build intelligent agents that save time.',
      features: [
        'Custom workflow design & development',
        'CRM, email & social media integrations',
        'Data sync & notification automation',
        'AI agent integration & deployment',
      ],
      tags: [
        { text: 'Automation', bg: '#f3e8ff', color: '#7c3aed' },
        { text: 'Workflow', bg: '#eef2ff', color: '#4f46e5' },
        { text: 'AI Agents', bg: '#ecfdf5', color: '#059669' },
      ],
    },
    {
      icon: 'fa-chart-pie',
      bg: 'rgba(251,191,36,0.1)',
      color: '#d97706',
      title: 'Infographics',
      desc: 'Visually compelling infographics for data storytelling, presentations, social media, and marketing collateral. Custom illustrations and data visualization.',
      features: [
        'Data visualization & chart design',
        'Custom illustrations & icons',
        'Social media infographic sets',
        'Print & digital format exports',
      ],
      tags: [
        { text: 'Visual Design', bg: '#fef3c7', color: '#d97706' },
        { text: 'Data Viz', bg: '#eef2ff', color: '#4f46e5' },
        { text: 'Social', bg: '#fdf2f8', color: '#db2777' },
      ],
    },
    {
      icon: 'fa-rocket',
      bg: 'linear-gradient(135deg,#4f46e5,#818cf8)',
      color: '#fff',
      title: 'Comprehensive Digital Strategy',
      desc: 'End-to-end digital strategy combining multiple services for maximum impact. From brand creation to market domination — we handle it all.',
      features: [
        'Full brand identity & digital presence audit',
        'Multi-channel marketing strategy',
        'Custom tech stack recommendations',
        'Ongoing optimization & monthly reviews',
      ],
      tags: [
        { text: 'Strategy', bg: '#f3e8ff', color: '#7c3aed' },
        { text: 'Full-Service', bg: '#eef2ff', color: '#4f46e5' },
        { text: 'Growth', bg: '#fef3c7', color: '#d97706' },
      ],
    },
  ];

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
            Our <span>Services</span>
          </h1>
          <p>14+ comprehensive digital services to take your brand from concept to market dominance.</p>
        </div>
      </section>

      <section className="section-padding services-all">
        <div className="container-main">
          <h2 className="section-title">
            Everything Your Brand <span className="highlight">Needs</span>
          </h2>
          <p className="section-subtitle">
            From brand identity creation to digital marketing automation — we cover your entire
            digital journey.
          </p>
          <div className="service-detail-grid">
            {services.map((s, i) => (
              <div className="service-detail-card" key={i}>
                <div className="sd-header">
                  <div
                    className="sd-icon"
                    style={{ background: s.bg, color: s.color }}
                  >
                    <i className={`fas ${s.icon}`}></i>
                  </div>
                  <div>
                    <h3>{s.title}</h3>
                    <p>{s.desc}</p>
                  </div>
                </div>
                <div className="sd-body">
                  <ul>
                    {s.features.map((f, j) => (
                      <li key={j}>
                        <i className="fas fa-check"></i> {f}
                      </li>
                    ))}
                  </ul>
                  <div className="sd-tags">
                    {s.tags.map((t, j) => (
                      <span key={j} style={{ background: t.bg, color: t.color }}>
                        {t.text}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* WHY CHOOSE US */}
      <section className="why-banner">
        <div className="container-main">
          <h2 className="section-title" style={{ color: '#fff' }}>
            Why <span className="highlight">Choose TKVibes</span>
          </h2>
          <p className="section-subtitle" style={{ color: 'rgba(255,255,255,0.6)' }}>
            What sets us apart from other digital agencies.
          </p>
          <div className="why-grid">
            <div className="why-card">
              <div className="icon">🎯</div>
              <h4>Results-Focused</h4>
              <p>
                Every strategy is designed to deliver measurable outcomes — higher rankings, more
                leads, increased sales.
              </p>
            </div>
            <div className="why-card">
              <div className="icon">💡</div>
              <h4>Custom Solutions</h4>
              <p>
                No cookie-cutter approaches. Every service is tailored to your unique business goals
                and target audience.
              </p>
            </div>
            <div className="why-card">
              <div className="icon">🤝</div>
              <h4>End-to-End Service</h4>
              <p>
                From logo design to ad campaigns to automation — we manage your complete digital
                ecosystem under one roof.
              </p>
            </div>
            <div className="why-card">
              <div className="icon">📊</div>
              <h4>Transparent Reporting</h4>
              <p>
                Regular performance updates, clear communication, and complete transparency in
                everything we do.
              </p>
            </div>
          </div>
        </div>
      </section>

      <section className="cta-section">
        <div className="container-main">
          <h2>Ready to Get Started?</h2>
          <p>
            Let&apos;s discuss which services are right for your business. Get a free consultation
            and custom quote today.
          </p>
          <div className="cta-buttons">
            <Link href="/contact" className="btn-custom btn-primary-custom">
              <i className="fas fa-paper-plane"></i> Request a Quote
            </Link>
            <Link
              href="/packages"
              className="btn-custom"
              style={{
                background: 'rgba(255,255,255,0.1)',
                color: '#fff',
                border: '1px solid rgba(255,255,255,0.2)',
              }}
            >
              <i className="fas fa-tags"></i> View Packages
            </Link>
          </div>
        </div>
      </section>
    </>
  );
}