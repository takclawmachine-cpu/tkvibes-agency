'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useEffect, useState } from 'react'
import Logo from '@/components/layout/Logo'
import { navLinks } from '@/lib/nav-links'

export default function Navbar() {
  const pathname = usePathname()
  const [scrolled, setScrolled] = useState(false)
  const [mobileOpen, setMobileOpen] = useState(false)

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

  return (
    <nav className={`navbar${scrolled ? ' scrolled' : ''}`}>
      <div className="container-main">
        <div className="nav-panel">
          <Logo variant="mark" />

          <ul className={`nav-links${mobileOpen ? ' open' : ''}`}>
            {navLinks.map((link) => {
              const isActive =
                link.href === '/' ? pathname === '/' : pathname.startsWith(link.href)

              return (
                <li key={link.href}>
                  <Link href={link.href} className={isActive ? 'active' : ''}>
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
  )
}
