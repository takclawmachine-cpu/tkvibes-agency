'use client'

import type { ReactNode } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { IBM_Plex_Mono, Manrope } from 'next/font/google'
import { useEffect, useEffectEvent, useState } from 'react'
import './globals.css'

const manrope = Manrope({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-sans',
})

const ibmPlexMono = IBM_Plex_Mono({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-mono',
  weight: ['400', '500'],
})

const navLinks = [
  { href: '/', label: 'Home' },
  { href: '/about', label: 'About' },
  { href: '/services', label: 'Services' },
  { href: '/packages', label: 'Packages' },
  { href: '/portfolio', label: 'Portfolio' },
  { href: '/contact', label: 'Contact' },
]

export default function RootLayout({
  children,
}: Readonly<{
  children: ReactNode
}>) {
  const pathname = usePathname()
  const [scrolled, setScrolled] = useState(false)
  const [mobileOpen, setMobileOpen] = useState(false)
  const isHome = pathname === '/'

  const updateAuroraMotion = useEffectEvent(() => {
    const root = document.documentElement

    if (!isHome) {
      root.style.setProperty('--aurora-scroll', '0')
      root.style.setProperty('--aurora-tilt', '0deg')
      root.style.setProperty('--aurora-depth', '1')
      root.style.setProperty('--aurora-opacity', '0.72')
      root.style.setProperty('--aurora-grid-shift', '0px')
      return
    }

    const maxScroll = Math.max(window.innerHeight * 1.6, 1)
    const progress = Math.min(window.scrollY / maxScroll, 1)
    const tilt = `${(progress * 14 - 5).toFixed(2)}deg`
    const depth = (1 + progress * 0.18).toFixed(3)
    const opacity = (0.78 - progress * 0.2).toFixed(3)
    const gridShift = `${Math.round(progress * 32)}px`

    root.style.setProperty('--aurora-scroll', progress.toFixed(3))
    root.style.setProperty('--aurora-tilt', tilt)
    root.style.setProperty('--aurora-depth', depth)
    root.style.setProperty('--aurora-opacity', opacity)
    root.style.setProperty('--aurora-grid-shift', gridShift)
  })

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20)
    onScroll()
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  useEffect(() => {
    const t = setTimeout(() => setMobileOpen(false), 0)
    return () => clearTimeout(t)
  }, [pathname])

  useEffect(() => {
    let frame = 0

    const onScroll = () => {
      cancelAnimationFrame(frame)
      frame = window.requestAnimationFrame(updateAuroraMotion)
    }

    updateAuroraMotion()
    window.addEventListener('scroll', onScroll, { passive: true })
    window.addEventListener('resize', onScroll)

    return () => {
      cancelAnimationFrame(frame)
      window.removeEventListener('scroll', onScroll)
      window.removeEventListener('resize', onScroll)
    }
  }, [pathname])

  return (
    <html lang="en" className="dark" data-scroll-behavior="smooth">
      <head>
        <link
          rel="stylesheet"
          href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css"
          crossOrigin="anonymous"
          referrerPolicy="no-referrer"
        />
      </head>
      <body className={`${manrope.variable} ${ibmPlexMono.variable} ${isHome ? 'home-route' : ''}`}>
        <div className="site-aurora" />
        <div className="site-grid" />
        <div className="site-noise" />
        <nav className={`navbar${scrolled ? ' scrolled' : ''}`}>
          <div className="container-main">
            <div className="nav-panel">
              <Link href="/" className="logo" aria-label="TKVibes home">
                <span className="logo-icon">TV</span>
                <span className="logo-copy">
                  TKVibes
                  <small>Digital Agency</small>
                </span>
              </Link>

              <ul className={`nav-links${mobileOpen ? ' open' : ''}`}>
                {navLinks.map((link) => {
                  const isActive =
                    link.href === '/' ? pathname === '/' : pathname.startsWith(link.href)

                  return (
                    <li key={link.href}>
                      <Link
                        href={link.href}
                        className={isActive ? 'active' : ''}
                      >
                        {link.label}
                      </Link>
                    </li>
                  )
                })}
              </ul>

              <div className="nav-cta">
                <Link href="/contact" className="btn-custom btn-primary-custom nav-button">
                  <i className="fas fa-paper-plane" />
                  Start a Project
                </Link>
                <button
                  type="button"
                  className="mobile-toggle"
                  onClick={() => setMobileOpen((value) => !value)}
                  aria-label="Toggle menu"
                  aria-expanded={mobileOpen}
                >
                  <i className={`fas ${mobileOpen ? 'fa-times' : 'fa-bars'}`} />
                </button>
              </div>
            </div>
          </div>
        </nav>

        <main className="site-main">{children}</main>

        <footer className="footer">
          <div className="container-main footer-grid">
            <div className="footer-brand">
              <Link href="/" className="logo footer-logo">
                <span className="logo-icon">TV</span>
                <span className="logo-copy">
                  TKVibes
                  <small>Digital Agency</small>
                </span>
              </Link>
              <p>
                We design premium websites, brand systems, and growth funnels for businesses that
                want to look sharper and convert better.
              </p>
              <div className="footer-social">
                <a
                  href="https://wa.me/919818246938"
                  target="_blank"
                  rel="noopener noreferrer"
                  aria-label="WhatsApp"
                >
                  <i className="fab fa-whatsapp" />
                </a>
                <a href="mailto:services@tkvibes.in" aria-label="Email">
                  <i className="fas fa-envelope" />
                </a>
              </div>
            </div>

            <div>
              <h4>Company</h4>
              <ul>
                <li><Link href="/about">About</Link></li>
                <li><Link href="/services">Services</Link></li>
                <li><Link href="/packages">Packages</Link></li>
                <li><Link href="/portfolio">Portfolio</Link></li>
              </ul>
            </div>

            <div>
              <h4>Services</h4>
              <ul>
                <li><Link href="/services">Web Design</Link></li>
                <li><Link href="/services">Brand Identity</Link></li>
                <li><Link href="/services">SEO and Ads</Link></li>
                <li><Link href="/services">Automation</Link></li>
              </ul>
            </div>

            <div>
              <h4>Contact</h4>
              <ul>
                <li><a href="mailto:services@tkvibes.in">services@tkvibes.in</a></li>
                <li><a href="tel:+919818246938">+91 98182 46938</a></li>
                <li><a href="https://wa.me/919818246938">WhatsApp</a></li>
                <li><span>India, serving clients worldwide</span></li>
              </ul>
            </div>
          </div>

          <div className="container-main footer-bottom">
            <p>© {new Date().getFullYear()} TKVibes Agency. All rights reserved.</p>
            <p>Built for modern brands that want better digital presence.</p>
          </div>
        </footer>
      </body>
    </html>
  )
}
