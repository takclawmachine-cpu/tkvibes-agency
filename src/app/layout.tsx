'use client'

import type { ReactNode } from 'react'
import { IBM_Plex_Mono, Manrope } from 'next/font/google'
import { usePathname } from 'next/navigation'
import { useEffect, useEffectEvent } from 'react'
import Footer from '@/components/layout/Footer'
import Navbar from '@/components/layout/Navbar'
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

export default function RootLayout({
  children,
}: Readonly<{
  children: ReactNode
}>) {
  const pathname = usePathname()
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
        <Navbar />
        <main className="site-main">{children}</main>
        <Footer />
      </body>
    </html>
  )
}
