'use client';

import { useState } from 'react';
import Link from 'next/link';
import WebsitePreview from '@/components/WebsitePreview';

export default function PortfolioPage() {
  const [filter, setFilter] = useState('all');

  const projects = [
    {
      url: '/websites/lets-smile-dental.html',
      category: 'website branding',
      gradient: 'linear-gradient(135deg,#1e3a5f,#2d5a87)',
      icon: 'fa-tooth',
      label: 'Website + Branding',
      industry: 'Healthcare',
      title: "Let's Smile Dental",
      desc: 'A complete digital transformation for a modern dental clinic — including a responsive website with appointment booking, doctor profiles, service pages, and full brand identity.',
      services: [
        { text: 'Website Design', bg: '#eef2ff', color: '#4f46e5' },
        { text: 'Logo Design', bg: '#fef3c7', color: '#d97706' },
        { text: 'GMB Setup', bg: '#ecfdf5', color: '#059669' },
        { text: 'SEO', bg: '#f3e8ff', color: '#7c3aed' },
      ],
    },
    {
      url: '/websites/tasty-bites-3d-cafe.html',
      category: 'website branding seo',
      gradient: 'linear-gradient(135deg,#0d4f3c,#1a7a5a)',
      icon: 'fa-mug-hot',
      label: 'Brand Identity',
      industry: 'Food & Beverage',
      title: 'Tasty Bites Cafe',
      desc: 'A warm, inviting website for a local cafe featuring a visually rich menu, location map, online ordering integration, and cohesive brand identity with logo and social media profiles.',
      services: [
        { text: 'Website Design', bg: '#eef2ff', color: '#4f46e5' },
        { text: 'Logo & Branding', bg: '#fef3c7', color: '#d97706' },
        { text: 'Brochure', bg: '#fdf2f8', color: '#db2777' },
        { text: 'Meta Ads', bg: '#eef2ff', color: '#4f46e5' },
      ],
    },
    {
      url: '/websites/deep-water-tank-cleaning-modern.html',
      category: 'website seo design',
      gradient: 'linear-gradient(135deg,#2d1b69,#4f3597)',
      icon: 'fa-water',
      label: 'SEO + Website',
      industry: 'Service Business',
      title: 'Deep Water Tank Cleaning',
      desc: 'A service-oriented website with location-based service areas, customer review integration, contact forms, and comprehensive local SEO strategy to rank in targeted areas.',
      services: [
        { text: 'Website Design', bg: '#eef2ff', color: '#4f46e5' },
        { text: 'SEO Services', bg: '#ecfdf5', color: '#059669' },
        { text: 'Google Ads', bg: '#eff6ff', color: '#2563eb' },
        { text: 'GMB', bg: '#fef3c7', color: '#d97706' },
      ],
    },
    {
      url: '/websites/mita-dental-website.html',
      category: 'website branding design',
      gradient: 'linear-gradient(135deg,#831843,#be185d)',
      icon: 'fa-tooth',
      label: 'Brand Identity',
      industry: 'Healthcare',
      title: 'Mita Dental Clinic',
      desc: 'Modern dental practice website with treatment-specific pages, before/after gallery, patient testimonials, and a complete logo and brand identity design package.',
      services: [
        { text: 'Website Design', bg: '#eef2ff', color: '#4f46e5' },
        { text: 'Logo Design', bg: '#fef3c7', color: '#d97706' },
        { text: 'Logo Animation', bg: '#f3e8ff', color: '#7c3aed' },
        { text: 'Infographics', bg: '#ecfdf5', color: '#059669' },
      ],
    },
    {
      url: '/websites/dental-clinic-3d.html',
      category: 'website seo',
      gradient: 'linear-gradient(135deg,#1e40af,#3b82f6)',
      icon: 'fa-hospital',
      label: 'Multi-Page Website',
      industry: 'Healthcare',
      title: 'Multi-Specialty Dental Clinic',
      desc: 'A comprehensive multi-page dental clinic website featuring service details, team profiles, testimonial carousel, online booking integration, and local SEO optimization.',
      services: [
        { text: 'Website Design', bg: '#eef2ff', color: '#4f46e5' },
        { text: 'SEO', bg: '#ecfdf5', color: '#059669' },
        { text: 'GMB Listing', bg: '#eff6ff', color: '#2563eb' },
        { text: 'Hosting', bg: '#fff7ed', color: '#ea580c' },
      ],
    },
    {
      category: 'branding design',
      gradient: 'linear-gradient(135deg,#4f46e5,#818cf8)',
      icon: 'fa-paint-brush',
      label: 'Brand Identity',
      industry: 'Branding',
      title: 'Complete Brand Identity Packages',
      desc: 'End-to-end brand identity design including logo creation, brand guidelines, business cards, letterheads, social media kit, and brand style guides for multiple businesses.',
      services: [
        { text: 'Logo Design', bg: '#fef3c7', color: '#d97706' },
        { text: 'Logo Animation', bg: '#fdf2f8', color: '#db2777' },
        { text: 'Brochure', bg: '#ecfdf5', color: '#059669' },
        { text: 'Infographics', bg: '#fff7ed', color: '#ea580c' },
      ],
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

  const filtered = filter === 'all' ? projects : projects.filter((p) => p.category.includes(filter));

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
            Our <span>Portfolio</span>
          </h1>
          <p>
            Real projects delivered for real businesses. See how we&apos;ve helped brands transform
            their digital presence.
          </p>
        </div>
      </section>

      <section className="section-padding" style={{ background: '#fff' }}>
        <div className="container-main">
          <div className="filter-bar">
            {['all', 'website', 'branding', 'seo', 'design'].map((f) => (
              <button
                key={f}
                className={filter === f ? 'active' : ''}
                onClick={() => setFilter(f)}
              >
                {f === 'all' ? 'All Projects' : f.charAt(0).toUpperCase() + f.slice(1)}
              </button>
            ))}
          </div>

          <div className="portfolio-grid-page">
            {filtered.map((project, i) => (
              <div className="portfolio-card" key={i}>
                <WebsitePreview src={project.url} title={project.title} />
                <div className="pf-body">
                  <div className="pf-category">{project.industry}</div>
                  <h3>{project.title}</h3>
                  <p>{project.desc}</p>
                  <div className="pf-services">
                    {project.services.map((s, j) => (
                      <span key={j} style={{ background: s.bg, color: s.color }}>
                        {s.text}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* TESTIMONIALS */}
      <section className="section-padding">
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

      <section className="cta-section">
        <div className="container-main">
          <h2>Want Results Like These?</h2>
          <p>
            Let&apos;s create something amazing for your business. Get in touch for a free
            consultation.
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
              <i className="fab fa-whatsapp"></i> WhatsApp Us
            </a>
          </div>
        </div>
      </section>
    </>
  );
}