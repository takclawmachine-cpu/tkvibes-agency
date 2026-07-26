'use client'

import Image from 'next/image'
import { useEffect, useState } from 'react'
import type { PortfolioProject } from '@/lib/portfolio'

interface HeroProjectStackProps {
  projects: PortfolioProject[]
  intervalMs?: number
}

function clamp(value: number, min: number, max: number) {
  return Math.min(Math.max(value, min), max)
}

export default function HeroProjectStack({
  projects,
  intervalMs = 2000,
}: HeroProjectStackProps) {
  const [activeIndex, setActiveIndex] = useState(0)

  useEffect(() => {
    if (projects.length <= 1) return

    const timer = window.setInterval(() => {
      setActiveIndex((prev) => (prev + 1) % projects.length)
    }, intervalMs)

    return () => window.clearInterval(timer)
  }, [projects.length, intervalMs])

  return (
    <div className="hero-stack-track">
      <div className="hero-stack-sticky">
        <div className="hero-stack-head">
          <span className="hero-stack-pill">Project stack</span>
          <p>Featured launches</p>
        </div>

        <div className="hero-stack-frame">
          {projects.map((project, index) => {
            const delta = index - activeIndex
            const isActive = index === activeIndex
            const isPrev = delta === -1 || (activeIndex === 0 && index === projects.length - 1)

            let translateY: number
            let translateX: number
            let scale: number
            let rotate: number
            let opacity: number

            if (isActive) {
              translateY = 0
              translateX = 0
              scale = 1
              rotate = 0
              opacity = 1
            } else if (isPrev) {
              translateY = -132
              translateX = 42
              scale = 0.89
              rotate = -5.5
              opacity = 0
            } else {
              const futureOffset = index > activeIndex ? index - activeIndex : projects.length - activeIndex + index
              translateY = futureOffset * 28
              translateX = futureOffset * 10
              scale = clamp(1 - futureOffset * 0.045, 0.7, 1)
              rotate = futureOffset * -1.4
              opacity = 1
            }

            return (
              <article
                key={project.id}
                className={`hero-stack-card${isActive ? ' active' : ''}`}
                style={{
                  zIndex: isActive ? projects.length : projects.length - index,
                  transform: `translate3d(${translateX}px, ${translateY}px, 0) scale(${scale}) rotate(${rotate}deg)`,
                  opacity,
                  transition: 'transform 0.7s cubic-bezier(0.22, 1, 0.36, 1), opacity 0.7s cubic-bezier(0.22, 1, 0.36, 1)',
                }}
              >
                <div className="hero-stack-card-bar">
                  <span />
                  <span />
                  <span />
                </div>
                <div className="hero-stack-card-image">
                  {project.previewImage ? (
                    <Image
                      src={project.previewImage}
                      alt={project.title}
                      fill
                      priority={index < 2}
                      sizes="(max-width: 1024px) 100vw, 42vw"
                      className="hero-cover-image"
                    />
                  ) : null}
                </div>
                <div className="hero-stack-card-caption">
                  <div>
                    <strong>{project.title}</strong>
                    <span>{project.industry}</span>
                  </div>
                  <p>{project.result}</p>
                </div>
              </article>
            )
          })}
        </div>

        <div className="hero-stack-dots">
          {projects.map((project, index) => (
            <button
              key={project.id}
              type="button"
              className={`hero-stack-dot${index === activeIndex ? ' active' : ''}`}
              aria-label={`Show ${project.title}`}
              onClick={() => setActiveIndex(index)}
            />
          ))}
        </div>
      </div>
    </div>
  )
}
