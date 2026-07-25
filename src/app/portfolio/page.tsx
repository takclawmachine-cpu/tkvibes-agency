'use client'

import { useState } from 'react'
import Link from 'next/link'
import Image from 'next/image'
import WebsitePreview from '@/components/WebsitePreview'
import { portfolioProjects } from '@/lib/portfolio'

const filters = ['all', 'website', 'branding', 'seo', 'design']

const testimonials = [
  {
    name: 'Dr. Rajesh Kumar',
    company: "Let's Smile Dental",
    image:
      'https://randomuser.me/api/portraits/men/32.jpg',
    quote:
      "TKVibes helped our clinic feel more premium online, and the website now makes booking much easier for patients.",
  },
  {
    name: 'Priya Kapoor',
    company: 'Tasty Bites Cafe',
    image:
      'https://randomuser.me/api/portraits/women/44.jpg',
    quote:
      'The new branding and website gave our cafe a far stronger identity, and customers noticed the difference immediately.',
  },
  {
    name: 'Arun Mehta',
    company: 'Deep Water Tank Cleaning',
    image:
      'https://randomuser.me/api/portraits/men/51.jpg',
    quote:
      'We needed clearer lead generation and better visibility. The updated website and local SEO work delivered both.',
  },
]

export default function PortfolioPage() {
  const [filter, setFilter] = useState('all')

  const filteredProjects =
    filter === 'all'
      ? portfolioProjects
      : portfolioProjects.filter((project) => project.categories.includes(filter))

  return (
    <>
      <section className="page-header">
        <div className="container-main">
          <div className="breadcrumb">
            <Link href="/">Home</Link>
            <span className="sep">/</span>
            <span className="current">Portfolio</span>
          </div>
          <h1>
            Selected <span>Work</span>
          </h1>
          <p>
            A mix of business websites, local-brand transformations, and conversion-focused design
            systems built for real client growth.
          </p>
        </div>
      </section>

      <section className="section-padding">
        <div className="container-main">
          <div className="filter-bar">
            {filters.map((item) => (
              <button
                key={item}
                type="button"
                className={filter === item ? 'active' : ''}
                onClick={() => setFilter(item)}
              >
                {item === 'all' ? 'All Projects' : item}
              </button>
            ))}
          </div>

          <div className="portfolio-grid-page">
            {filteredProjects.map((project) => (
              <article key={project.id} className="portfolio-card">
                <WebsitePreview imageSrc={project.previewImage} title={project.title} />
                <div className="pf-body">
                  <div className="pf-meta-row">
                    <span className="pf-category">{project.industry}</span>
                    <p>{project.result}</p>
                  </div>
                  <h3>{project.title}</h3>
                  <p>{project.summary}</p>
                  <div className="pf-services">
                    {project.services.map((service) => (
                      <span key={service}>{service}</span>
                    ))}
                  </div>
                </div>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="section-padding">
        <div className="container-main">
          <div className="section-heading centered">
            <span className="eyebrow">Client feedback</span>
            <h2 className="section-title">What clients noticed after the redesign.</h2>
            <p className="section-subtitle">
              Premium presentation matters because trust is often formed before a single call or
              inquiry is made.
            </p>
          </div>

          <div className="testimonial-grid">
            {testimonials.map((testimonial, index) => (
              <article key={testimonial.name} className="testimonial-card">
                <div className="stars">
                  {Array.from({ length: 5 }).map((_, starIndex) => (
                    <i className="fas fa-star" key={`${testimonial.name}-${starIndex}`} />
                  ))}
                </div>
                <blockquote>{testimonial.quote}</blockquote>
                <div className="author">
                  <Image
                    src={testimonial.image}
                    alt={testimonial.name}
                    className="avatar avatar-photo"
                    width={40}
                    height={40}
                    loading="lazy"
                    decoding="async"
                  />
                  <div className="info">
                    <h5>{testimonial.name}</h5>
                    <p>{testimonial.company}</p>
                  </div>
                </div>
                <span className="testimonial-index">{`0${index + 1}`}</span>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="cta-section">
        <div className="container-main cta-panel">
          <span className="eyebrow">Your turn</span>
          <h2>Want your business to look this polished online?</h2>
          <p>
            We can redesign your site, refresh your brand, and build a cleaner digital experience
            that feels more credible from day one.
          </p>
          <div className="cta-buttons">
            <Link href="/contact" className="btn-custom btn-primary-custom">
              <i className="fas fa-paper-plane" />
              Start Your Project
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
