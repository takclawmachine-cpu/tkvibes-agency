import Image from 'next/image'
import Link from 'next/link'
import HeroProjectStack from '@/components/ui/HeroProjectStack'
import { portfolioProjects } from '@/lib/portfolio'

const heroStackProjects = portfolioProjects.filter((project) => project.previewImage).slice(0, 5)
const featuredProjects = heroStackProjects.slice(0, 3)

const serviceHighlights = [
  {
    title: 'Premium website design',
    copy: 'Fast, polished marketing sites and service websites built to feel trustworthy from the first scroll.',
    icon: 'fa-laptop-code',
  },
  {
    title: 'Brand identity systems',
    copy: 'Logos, color systems, and collateral that help businesses feel established across every touchpoint.',
    icon: 'fa-layer-group',
  },
  {
    title: 'Growth and automation',
    copy: 'SEO, paid acquisition, and automations that keep leads moving without adding more manual work.',
    icon: 'fa-chart-line',
  },
]

const processSteps = [
  {
    number: '01',
    title: 'Clarity first',
    copy: 'We map positioning, offer hierarchy, and customer intent before visuals start.',
  },
  {
    number: '02',
    title: 'Design with proof',
    copy: 'Every section is shaped around credibility, conversion, and a premium brand feel.',
  },
  {
    number: '03',
    title: 'Launch for growth',
    copy: 'We ship fast, optimize performance, and support search, ads, and automation after launch.',
  },
]

export default function HomePage() {
  return (
    <>
      <section className="hero-section">
        <div className="container-main hero-grid">
          <div className="hero-copy">
            <div className="eyebrow">
              <span className="eyebrow-dot" />
              Boutique digital agency for modern service brands
            </div>
            <h1>
              Websites that look premium,
              <span> feel effortless, and convert clearly.</span>
            </h1>
            <p>
              TKVibes builds sharp websites, brand systems, and growth-ready digital experiences
              for businesses that want to feel more credible online.
            </p>
            <div className="hero-actions">
              <Link href="/contact" className="btn-custom btn-primary-custom">
                <i className="fas fa-paper-plane" />
                Start a Project
              </Link>
              <Link href="/portfolio" className="btn-custom btn-outline-custom">
                View Selected Work
              </Link>
            </div>
            <div className="hero-metrics">
              <div>
                <strong>50+</strong>
                <span>Projects delivered</span>
              </div>
              <div>
                <strong>98%</strong>
                <span>Client satisfaction</span>
              </div>
              <div>
                <strong>24/7</strong>
                <span>Support availability</span>
              </div>
            </div>
          </div>

          <div className="hero-visual">
            <HeroProjectStack projects={heroStackProjects} />
          </div>
        </div>
      </section>

      <section className="section-padding">
        <div className="container-main">
          <div className="proof-strip">
            <p>Designed for trust, speed, and stronger first impressions.</p>
            <div>
              <span>Web Design</span>
              <span>Brand Identity</span>
              <span>SEO</span>
              <span>Ads</span>
              <span>Automation</span>
            </div>
          </div>
        </div>
      </section>

      <section className="section-padding">
        <div className="container-main">
          <div className="section-heading">
            <div>
              <span className="eyebrow">What we do</span>
              <h2 className="section-title left">Built to make your business look established.</h2>
            </div>
            <p className="section-subtitle left">
              We combine clean design, strong messaging, and practical growth systems so your site
              does more than just exist online.
            </p>
          </div>

          <div className="feature-grid">
            {serviceHighlights.map((item) => (
              <article key={item.title} className="feature-card">
                <div className="feature-icon">
                  <i className={`fas ${item.icon}`} />
                </div>
                <h3>{item.title}</h3>
                <p>{item.copy}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="section-padding">
        <div className="container-main">
          <div className="section-heading">
            <div>
              <span className="eyebrow">Selected work</span>
              <h2 className="section-title left">Recent websites and brand-led launches.</h2>
            </div>
            <Link href="/portfolio" className="btn-custom btn-outline-custom">
              Explore Portfolio
            </Link>
          </div>

          <div className="showcase-grid">
            {featuredProjects.map((project) => (
              <article key={project.id} className="showcase-card">
                <div className="showcase-image">
                  <Image
                    src={project.previewImage!}
                    alt={project.title}
                    fill
                    sizes="(max-width: 768px) 100vw, 33vw"
                    className="hero-cover-image"
                  />
                </div>
                <div className="showcase-body">
                  <div className="showcase-meta">
                    <span>{project.industry}</span>
                    <p>{project.result}</p>
                  </div>
                  <h3>{project.title}</h3>
                  <p>{project.summary}</p>
                </div>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="section-padding">
        <div className="container-main">
          <div className="section-heading centered">
            <span className="eyebrow">Process</span>
            <h2 className="section-title">A calmer, clearer way to launch digital work.</h2>
            <p className="section-subtitle">
              We keep the process direct so you get better output without chasing updates or
              stitching together multiple vendors.
            </p>
          </div>

          <div className="process-grid">
            {processSteps.map((step) => (
              <article key={step.number} className="process-card">
                <span className="process-number">{step.number}</span>
                <h3>{step.title}</h3>
                <p>{step.copy}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="cta-section">
        <div className="container-main cta-panel">
          <span className="eyebrow">Ready when you are</span>
          <h2>Bring your website and brand up to the level your business deserves.</h2>
          <p>
            If the current site feels outdated, inconsistent, or underwhelming, we can redesign it
            into something cleaner, faster, and more credible.
          </p>
          <div className="cta-buttons">
            <Link href="/contact" className="btn-custom btn-primary-custom">
              <i className="fas fa-calendar-check" />
              Book a Free Consultation
            </Link>
            <Link href="/packages" className="btn-custom btn-outline-custom">
              See Packages
            </Link>
          </div>
        </div>
      </section>
    </>
  )
}
