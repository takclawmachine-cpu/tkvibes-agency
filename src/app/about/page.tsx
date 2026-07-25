import type { Metadata } from 'next'
import Link from 'next/link'

export const metadata: Metadata = {
  title: 'About',
  description:
    'Learn about TKVibes, a digital agency focused on premium website design, brand identity, SEO, and automation.',
}

const values = [
  {
    icon: 'fa-bullseye',
    title: 'Results-led thinking',
    copy: 'We care about business outcomes, not just attractive mockups. The work should improve trust, leads, and clarity.',
  },
  {
    icon: 'fa-gem',
    title: 'Premium execution',
    copy: 'Every interaction, layout, and visual detail should feel intentional and polished.',
  },
  {
    icon: 'fa-handshake',
    title: 'True partnership',
    copy: 'We work closely with clients so the output reflects the business, not a generic agency template.',
  },
  {
    icon: 'fa-bolt',
    title: 'Modern systems',
    copy: 'From websites to automation, we use current tools to make digital operations simpler and sharper.',
  },
]

const team = [
  {
    initials: 'TK',
    name: 'Tarun Kumar',
    role: 'Founder and Lead Strategist',
    copy: 'Leads positioning, project direction, and the overall digital strategy behind each client build.',
  },
  {
    initials: 'AD',
    name: 'Ananya Dev',
    role: 'Creative Director',
    copy: 'Shapes the visual systems, brand assets, and the premium design language behind launches.',
  },
  {
    initials: 'RS',
    name: 'Rohan Sharma',
    role: 'Lead Developer',
    copy: 'Builds fast, reliable websites with a focus on performance, responsiveness, and maintainability.',
  },
  {
    initials: 'PM',
    name: 'Priya Mehta',
    role: 'Growth Marketing Lead',
    copy: 'Connects websites to SEO, paid acquisition, and ongoing optimization after launch.',
  },
]

export default function AboutPage() {
  return (
    <>
      <section className="page-header">
        <div className="container-main">
          <div className="breadcrumb">
            <Link href="/">Home</Link>
            <span className="sep">/</span>
            <span className="current">About</span>
          </div>
          <h1>
            About <span>TKVibes</span>
          </h1>
          <p>
            We help businesses present themselves with more clarity, more confidence, and a more
            premium digital presence.
          </p>
        </div>
      </section>

      <section className="section-padding">
        <div className="container-main">
          <div className="mission-grid">
            <article className="mission-card">
              <div className="icon">
                <i className="fas fa-compass" />
              </div>
              <h3>Our mission</h3>
              <p>
                To design websites and brand systems that make growing businesses feel more
                established, more trusted, and easier to choose.
              </p>
            </article>
            <article className="mission-card">
              <div className="icon accent">
                <i className="fas fa-eye" />
              </div>
              <h3>Our vision</h3>
              <p>
                To become the agency businesses call when they need digital work that feels modern,
                elegant, and commercially smart.
              </p>
            </article>
          </div>

          <div className="section-heading centered">
            <span className="eyebrow">Core values</span>
            <h2 className="section-title">The standards we bring into every project.</h2>
          </div>

          <div className="values-grid">
            {values.map((value) => (
              <article key={value.title} className="value-card">
                <div className="icon">
                  <i className={`fas ${value.icon}`} />
                </div>
                <h4>{value.title}</h4>
                <p>{value.copy}</p>
              </article>
            ))}
          </div>

          <div className="stats-row">
            <div className="stat">
              <h3>50+</h3>
              <p>Projects delivered</p>
            </div>
            <div className="stat">
              <h3>5+</h3>
              <p>Years of experience</p>
            </div>
            <div className="stat">
              <h3>30+</h3>
              <p>Businesses supported</p>
            </div>
            <div className="stat">
              <h3>14</h3>
              <p>Services offered</p>
            </div>
          </div>
        </div>
      </section>

      <section className="section-padding">
        <div className="container-main">
          <div className="section-heading centered">
            <span className="eyebrow">Team</span>
            <h2 className="section-title">The people behind the work.</h2>
            <p className="section-subtitle">
              Strategy, design, development, and growth work together here instead of being passed
              between disconnected vendors.
            </p>
          </div>

          <div className="team-grid">
            {team.map((member) => (
              <article key={member.name} className="team-card">
                <div className="avatar-lg">{member.initials}</div>
                <h4>{member.name}</h4>
                <div className="role">{member.role}</div>
                <p>{member.copy}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="cta-section">
        <div className="container-main cta-panel">
          <span className="eyebrow">Let us build with you</span>
          <h2>Need a sharper website, stronger brand, or both?</h2>
          <p>
            We can help turn an average digital presence into something more cohesive, more
            credible, and more effective.
          </p>
          <div className="cta-buttons">
            <Link href="/contact" className="btn-custom btn-primary-custom">
              <i className="fas fa-paper-plane" />
              Start a Project
            </Link>
            <a
              href="https://wa.me/919818246938"
              className="btn-custom btn-outline-custom"
              target="_blank"
              rel="noopener noreferrer"
            >
              <i className="fab fa-whatsapp" />
              Chat on WhatsApp
            </a>
          </div>
        </div>
      </section>
    </>
  )
}
