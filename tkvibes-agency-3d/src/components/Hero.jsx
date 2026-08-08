import { Canvas } from '@react-three/fiber'
import { Bloom, EffectComposer, FXAA } from '@react-three/postprocessing'
import * as THREE from 'three'
import Globe3D from './Globe3D'
import { motion } from 'framer-motion'
import { DecryptText } from './ui/decrypt-text'

export default function Hero() {
  return (
    <>
      <div className="site-aurora"></div>
      <div className="site-grid"></div>
      <div id="noise"></div>

      <nav>
        <a href="#work" className="active">Work</a>
        <a href="#about">About</a>
        <a href="#contact">Contact</a>
      </nav>

      <motion.a href="#" className="logo-mark" aria-label="TKVibes"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <svg viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
          <rect x="1" y="1" width="30" height="30" rx="8" stroke="currentColor" strokeWidth="1.5" strokeOpacity="0.2"/>
          <path d="M10 10L22 22M22 10L10 22" stroke="#5eead4" strokeWidth="2.5" strokeLinecap="round"/>
        </svg>
        <span><em>TK</em>Vibes</span>
      </motion.a>

      <motion.div className="audio-toggle"
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 0.3 }}
      >
        <button id="audioBtn" aria-label="Toggle ambient audio">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
            <path d="M9 18V5l12-2v13"/>
            <circle cx="6" cy="18" r="3"/>
            <circle cx="18" cy="16" r="3"/>
          </svg>
        </button>
      </motion.div>

      <section className="hero-section">
        <div className="hero-grid">
          <div className="hero-copy">
            <motion.p className="hero-tag"
              initial={{ opacity: 0, x: -30 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.4, duration: 0.8 }}
            >
              Boutique digital agency for modern service brands
            </motion.p>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5, duration: 0.8 }}
            >
              <DecryptText
                as="h1"
                text="Websites that look premium, feel effortless, and convert clearly."
                trigger="mount"
                variant="display"
                stagger={55}
                speed={45}
                startDelay={400}
                loop={8000}
                retriggerOnHover
                className="hero-title"
              />
            </motion.div>

            <motion.p className="hero-sub"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6, duration: 0.8 }}
            >
              TKVibes builds sharp websites, brand systems, and growth-ready digital experiences for businesses that want to feel more credible online.
            </motion.p>

            <motion.div className="hero-cta"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.7, duration: 0.8 }}
            >
              <motion.a href="#contact" className="btn btn-primary"
                whileHover={{ scale: 1.05, y: -2 }}
                whileTap={{ scale: 0.98 }}
              >
                Start a Project
              </motion.a>
              <motion.a href="#work" className="btn btn-outline"
                whileHover={{ scale: 1.05, y: -2 }}
                whileTap={{ scale: 0.98 }}
              >
                View Selected Work
              </motion.a>
            </motion.div>

            <motion.div className="hero-metrics"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.8, duration: 0.8 }}
            >
              <div className="hero-metric">
                <svg className="metric-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l4.3-4.3a1 1 0 0 1 1.48 1.48l-4.3 4.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 1-1.4 1.4l-6.3-6.3a1 1 0 0 1 0-1.4z"/>
                  <path d="M3 7h18"/><path d="M5 12h14"/><path d="M7 17h10"/>
                </svg>
                <div><strong>50+</strong><span>Projects delivered</span></div>
              </div>
              <div className="hero-metric">
                <svg className="metric-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                  <circle cx="12" cy="7" r="5"/><path d="M7 7c0 3.3 2.7 6 6 6s6-2.7 6-6-2.7-6-6-6S6 3.7 6 7z"/><circle cx="9" r="1"/><circle cx="15" r="1"/>
                </svg>
                <div><strong>98%</strong><span>Client satisfaction</span></div>
              </div>
              <div className="hero-metric">
                <svg className="metric-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M12 22a10 10 0 1 0 0-20 10 10 0 0 0 0 20z"/><path d="M12 16h.01"/><path d="M12 12h.01"/><path d="M12 8h.01"/>
                </svg>
                <div><strong>24/7</strong><span>Support availability</span></div>
              </div>
            </motion.div>
          </div>

          <div className="hero-visual">
            <div className="hero-globe-stage">
              <Canvas
                camera={{ position: [0, 0, 8], fov: 30 }}
                gl={{ antialias: true, alpha: true }}
              >
                <EffectComposer>
                  <Bloom
                    luminanceThreshold={0.1}
                    luminanceSmoothing={0.9}
                    height={30}
                    intensity={1.0}
                  />
                  <FXAA />
                </EffectComposer>
                <Globe3D />
              </Canvas>
              <div className="hero-globe-glow"></div>
            </div>
          </div>
        </div>

        <motion.div className="scroll-indicator"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.5, duration: 0.8 }}
        >
          <span>Scroll</span>
          <div className="scroll-line"></div>
        </motion.div>
      </section>
    </>
  )
}
