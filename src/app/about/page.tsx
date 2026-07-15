import type { Metadata } from 'next';
import Link from 'next/link';

export const metadata: Metadata = {
  title: 'About',
  description:
    'Learn about TKVibes — a full-service digital agency specializing in logo design, web development, SEO, digital marketing, and automation.',
};

export default function AboutPage() {
  return (
    <>
      {/* ===== PAGE HEADER ===== */}
      <section className="page-header">
        <div className="container-main">
          <div className="breadcrumb">
            <Link href="/">Home</Link>
            <span className="sep">/</span>
            <span className="current">About Us</span>
          </div>
          <h1>
            About <span>TKVibes</span>
          </h1>
          <p>
            We&apos;re a passionate team of designers, developers, and digital strategists committed
            to helping businesses build a powerful online presence.
          </p>
        </div>
      </section>

      {/* ===== MISSION & VISION ===== */}
      <section className="section-padding">
        <div className="container-main">
          <div className="mission-grid">
            <div className="mission-card">
              <div
                className="icon"
                style={{ background: 'rgba(79,70,229,0.1)', color: 'var(--primary)' }}
              >
                <i className="fas fa-bullseye"></i>
              </div>
              <h3>Our Mission</h3>
              <p>
                To empower businesses with creative digital solutions that drive measurable growth.
                We believe every brand deserves a compelling online presence, and we deliver it
                through thoughtful design, strategic marketing, and intelligent automation.
              </p>
            </div>
            <div className="mission-card">
              <div
                className="icon"
                style={{ background: 'rgba(245,158,11,0.1)', color: 'var(--accent)' }}
              >
                <i className="fas fa-eye"></i>
              </div>
              <h3>Our Vision</h3>
              <p>
                To become India&apos;s most trusted digital agency — known for delivering
                exceptional value, innovative solutions, and lasting partnerships with every client
                we serve.
              </p>
            </div>
          </div>

          <h2 className="section-title">
            Our Core <span className="highlight">Values</span>
          </h2>
          <p className="section-subtitle">The principles that guide everything we create.</p>
          <div className="values-grid">
            <div className="value-card">
              <div className="icon">🎯</div>
              <h4>Results-Driven</h4>
              <p>
                Every project is measured by the tangible business outcomes it delivers — more
                traffic, better rankings, higher conversions.
              </p>
            </div>
            <div className="value-card">
              <div className="icon">🎨</div>
              <h4>Creative Excellence</h4>
              <p>
                We push creative boundaries while keeping designs functional and user-friendly.
                Beauty meets purpose in every project.
              </p>
            </div>
            <div className="value-card">
              <div className="icon">🤝</div>
              <h4>Client Partnership</h4>
              <p>
                We work as an extension of your team — transparent communication, regular updates,
                and a shared commitment to your success.
              </p>
            </div>
            <div className="value-card">
              <div className="icon">⚡</div>
              <h4>Innovation First</h4>
              <p>
                From AI automation to modern web technologies, we leverage the latest tools to give
                your brand a competitive edge.
              </p>
            </div>
          </div>

          {/* ===== STATS ===== */}
          <div className="stats-row">
            <div className="stat">
              <h3>
                <span>50+</span>
              </h3>
              <p>Projects Delivered</p>
            </div>
            <div className="stat">
              <h3>
                <span>5+</span>
              </h3>
              <p>Years Experience</p>
            </div>
            <div className="stat">
              <h3>
                <span>30+</span>
              </h3>
              <p>Happy Clients</p>
            </div>
            <div className="stat">
              <h3>
                <span>14</span>
              </h3>
              <p>Services Offered</p>
            </div>
          </div>
        </div>
      </section>

      {/* ===== TEAM ===== */}
      <section className="section-padding" style={{ background: '#fff' }}>
        <div className="container-main">
          <h2 className="section-title">
            Meet Our <span className="highlight">Team</span>
          </h2>
          <p className="section-subtitle">
            Passionate creators and strategists dedicated to your brand&apos;s success.
          </p>
          <div className="team-grid">
            <div className="team-card">
              <div
                className="avatar-lg"
                style={{ background: 'linear-gradient(135deg,#4f46e5,#818cf8)' }}
              >
                TK
              </div>
              <h4>Tarun Kumar</h4>
              <div className="role">Founder &amp; Lead Strategist</div>
              <p>
                Visionary digital strategist with expertise in brand identity, web development, and
                marketing automation.
              </p>
            </div>
            <div className="team-card">
              <div
                className="avatar-lg"
                style={{ background: 'linear-gradient(135deg,#f59e0b,#f97316)' }}
              >
                AD
              </div>
              <h4>Ananya Dev</h4>
              <div className="role">Creative Director</div>
              <p>
                Talented designer specializing in logo design, brand identity, brochure design, and
                visual storytelling.
              </p>
            </div>
            <div className="team-card">
              <div
                className="avatar-lg"
                style={{ background: 'linear-gradient(135deg,#059669,#34d399)' }}
              >
                RS
              </div>
              <h4>Rohan Sharma</h4>
              <div className="role">Lead Developer</div>
              <p>
                Full-stack web developer building responsive, high-performance websites with modern
                technologies.
              </p>
            </div>
            <div className="team-card">
              <div
                className="avatar-lg"
                style={{ background: 'linear-gradient(135deg,#dc2626,#f87171)' }}
              >
                PM
              </div>
              <h4>Priya Mehta</h4>
              <div className="role">Digital Marketing Head</div>
              <p>
                SEO and paid ads specialist driving measurable growth through Google Ads, Meta Ads,
                and content strategy.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ===== CTA ===== */}
      <section className="cta-section">
        <div className="container-main">
          <h2>Let&apos;s Build Something Great Together</h2>
          <p>
            Have a project in mind? We&apos;d love to hear about it. Reach out and let&apos;s
            discuss how TKVibes can help your brand grow.
          </p>
          <div className="cta-buttons">
            <Link href="/contact" className="btn-custom btn-primary-custom">
              <i className="fas fa-paper-plane"></i> Start a Project
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