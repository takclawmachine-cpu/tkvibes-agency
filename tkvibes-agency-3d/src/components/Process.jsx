import { motion } from 'framer-motion'

const processSteps = [
  {
    number: "01",
    title: "Clarity first",
    description: "We map positioning, offer hierarchy, and customer intent before visuals start."
  },
  {
    number: "02",
    title: "Design with proof",
    description: "Every section is shaped around credibility, conversion, and a premium brand feel."
  },
  {
    number: "03",
    title: "Launch for growth",
    description: "We ship fast, optimize performance, and support search, ads, and automation after launch."
  }
]

export default function Process() {
  return (
    <section className="section" id="process">
      <motion.div
        className="section-header"
        initial={{ opacity: 0, y: 40 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, amount: 0.3 }}
        transition={{ duration: 0.8 }}
      >
        <div className="label">Process</div>
        <h2>A calmer, clearer way to <strong>launch digital work</strong></h2>
        <p>We keep the process direct so you get better output without chasing updates or stitching together multiple vendors.</p>
      </motion.div>

      <div className="process-grid">
        {processSteps.map((step, i) => (
          <motion.div
            key={step.title}
            className="process-card"
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, amount: 0.3 }}
            transition={{ duration: 0.8, delay: i * 0.1 }}
          >
            <div className="process-number">{step.number}</div>
            <div className="process-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                {i === 0 && <><circle cx="12" cy="12" r="8"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="12" x2="16" y2="16"/></>}
                {i === 1 && <><path d="M13 7L8 2L2 8L7 13L13 7Z"/><path d="M11 11l6-6"/><path d="M18 4l2 2"/></>}
                {i === 2 && <><path d="M12 2L2 7v5c0 4 4 9 10 10c6-1 10-6 10-10V7L12 2Z"/><path d="M12 2v10"/><path d="M7 9l5 5 5-5"/></>}
              </svg>
            </div>
            <h3>{step.title}</h3>
            <p>{step.description}</p>
          </motion.div>
        ))}
      </div>
    </section>
  )
}
