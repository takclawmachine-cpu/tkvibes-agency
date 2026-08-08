import { motion } from 'framer-motion'

const features = [
  {
    title: "Premium website design",
    description: "Fast, polished marketing sites and service websites built to feel trustworthy from the first scroll.",
    icon: "💻"
  },
  {
    title: "Brand identity systems",
    description: "Logos, color systems, and collateral that help businesses feel established across every touchpoint.",
    icon: "🎨"
  },
  {
    title: "Growth and automation",
    description: "SEO, paid acquisition, and automations that keep leads moving without adding more manual work.",
    icon: "📈"
  }
]

export default function Services() {
  return (
    <section className="section" id="services">
      <motion.div
        className="section-header"
        initial={{ opacity: 0, y: 40 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, amount: 0.3 }}
        transition={{ duration: 0.8 }}
      >
        <div className="label">What we do</div>
        <h2>Built to make your business look <strong>established</strong></h2>
        <p>Premium website design, brand identity systems, and growth automation — engineered for modern service brands.</p>
      </motion.div>

      <div className="feature-grid">
        {features.map((feature, i) => (
          <motion.div
            key={feature.title}
            className="feature-card"
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, amount: 0.3 }}
            transition={{ duration: 0.8, delay: i * 0.1 }}
            whileHover={{ y: -4, borderColor: 'var(--accent-dim)' }}
          >
            <div className="feature-icon">{feature.icon}</div>
            <h3>{feature.title}</h3>
            <p>{feature.description}</p>
          </motion.div>
        ))}
      </div>
    </section>
  )
}
