import { useEffect } from 'react'
import { motion } from 'framer-motion'
import Services from './Services'
import Process from './Process'
import Footer from './Footer'

export default function ScrollBasedReveal() {
  // Update nav active state based on scroll
  useEffect(() => {
    function onScroll() {
      const sections = document.querySelectorAll('section[id]')
      const navLinks = document.querySelectorAll('nav a')
      let current = ''
      sections.forEach(s => {
        if (window.scrollY >= s.offsetTop - 200) current = s.id
      })
      navLinks.forEach(a => {
        a.classList.toggle('active', a.getAttribute('href') === '#' + current)
      })
    }
    window.addEventListener('scroll', onScroll, { passive: true })
    onScroll()
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  // Audio toggle
  useEffect(() => {
    const audioBtn = document.getElementById('audioBtn')
    if (audioBtn) {
      let audioPlaying = false
      audioBtn.addEventListener('click', () => {
        audioPlaying = !audioPlaying
        audioBtn.style.color = audioPlaying ? 'var(--accent)' : ''
        audioBtn.style.borderColor = audioPlaying ? 'var(--accent-dim)' : ''
      })
    }
  }, [])

  // Work card hover glow
  useEffect(() => {
    const cards = document.querySelectorAll('.work-card')
    cards.forEach(card => {
      card.addEventListener('mousemove', (e) => {
        const rect = card.getBoundingClientRect()
        const x = ((e.clientX - rect.left) / rect.width * 100)
        const y = ((e.clientY - rect.top) / rect.height * 100)
        card.style.setProperty('--mx', x + '%')
        card.style.setProperty('--my', y + '%')
      })
    })
  }, [])

  return (
    <>
      <Services />
      <Process />
      <motion.section
        className="section"
        id="ready"
        initial={{ opacity: 0, y: 40 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, amount: 0.3 }}
        transition={{ duration: 0.8 }}
      >
        <div className="section-header" style={{ maxWidth: '720px' }}>
          <div className="label">Ready when you are</div>
          <h2>Bring your website and brand up to the level your business <strong>deserves</strong>.</h2>
          <p>If the current site feels outdated, inconsistent, or underwhelming, we can redesign it into something cleaner, faster, and more credible.</p>
        </div>
        <motion.div
          className="hero-cta"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.3 }}
          transition={{ duration: 0.8, delay: 0.1 }}
        >
          <motion.a
            href="#contact"
            className="btn btn-primary"
            whileHover={{ scale: 1.05, y: -2 }}
            whileTap={{ scale: 0.98 }}
          >
            Book a Free Consultation
          </motion.a>
          <motion.a
            href="#"
            className="btn btn-outline"
            whileHover={{ scale: 1.05, y: -2 }}
            whileTap={{ scale: 0.98 }}
          >
            See Packages
          </motion.a>
        </motion.div>
      </motion.section>

      <Footer />
    </>
  )
}
