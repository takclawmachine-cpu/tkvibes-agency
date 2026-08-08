import { motion } from 'framer-motion'

export default function About() {
  const stats = [
    { number: "5+", label: "Years building" },
    { number: "30+", label: "Projects shipped" },
    { number: "12", label: "Team members" },
    { number: "100%", label: "Client satisfaction" }
  ]

  return (
    <section id="about" className="section">
      <motion.div
        className="section-header"
        initial={{ opacity: 0, y: 40 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, amount: 0.3 }}
        transition={{ duration: 0.8 }}
      >
        <div className="label">About</div>
        <h2>Creativity meets <strong>engineering</strong></h2>
        <p>We're a small, nimble team of designers, developers, and strategists who believe the best digital products are built at the intersection of art and technology.</p>
      </motion.div>

      <div className="about-content">
        <motion.div
          className="about-text"
          initial={{ opacity: 0, x: -40 }}
          whileInView={{ opacity: 1, x: 0 }}
          viewport={{ once: true, amount: 0.3 }}
          transition={{ duration: 0.8 }}
        >
          <h3>Our approach</h3>
          <p>We don't build templates. Every solution is architected from the ground up — tailored to your brand, your audience, and your business goals. From concept to launch, we treat every pixel and every line of code with the same level of care.</p>
          <p>Our toolkit spans modern frontend frameworks, real-time 3D rendering, AI/ML pipelines, and custom backend systems. But technology is just the means — the end is always a memorable experience.</p>
        </motion.div>

        <motion.div
          className="about-stats"
          initial={{ opacity: 0, x: 40 }}
          whileInView={{ opacity: 1, x: 0 }}
          viewport={{ once: true, amount: 0.3 }}
          transition={{ duration: 0.8 }}
        >
          {stats.map((stat, i) => (
            <div key={i} className="stat">
              <div className="number">{stat.number}</div>
              <div className="label">{stat.label}</div>
            </div>
          ))}
        </motion.div>
      </div>
    </section>
  )
}
