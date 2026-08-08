import { motion } from 'framer-motion'

const workItems = [
  {
    id: 1,
    title: "Nexus Platform",
    description: "An AI-powered analytics dashboard with real-time 3D data visualization and predictive modeling.",
    tags: ["React", "Three.js", "AI"]
  },
  {
    id: 2,
    title: "Vertex Brand",
    description: "Full brand identity and immersive website with WebGL interactions and cinematic micro-animations.",
    tags: ["Branding", "WebGL", "GSAP"]
  },
  {
    id: 3,
    title: "Pulse CRM",
    description: "Custom CRM with AI lead scoring, automated workflows, and a real-time operations dashboard.",
    tags: ["CRM", "Automation", "AI"]
  }
]

export default function Work() {
  return (
    <section id="work" className="section">
      <motion.div
        className="section-header"
        initial={{ opacity: 0, y: 40 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, amount: 0.3 }}
        transition={{ duration: 0.8 }}
      >
        <div className="label">Selected Projects</div>
        <h2>Work we're <strong>proud of</strong></h2>
        <p>Every project is a collaboration — part craft, part science, and a whole lot of obsession over the details that matter.</p>
      </motion.div>

      <div className="work-grid">
        {workItems.map((item, i) => (
          <motion.div
            key={item.id}
            className="work-card"
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, amount: 0.3 }}
            transition={{ duration: 0.8, delay: i * 0.1 }}
            whileHover={{ y: -4, borderColor: 'var(--accent-dim)' }}
            onHoverStart={(e) => {
              const card = e.currentTarget
              card.style.setProperty('--mx', `${e.nativeEvent.offsetX}px`)
              card.style.setProperty('--my', `${e.nativeEvent.offsetY}px`)
            }}
          >
            <span className="number">0{item.id}</span>
            <h3>{item.title}</h3>
            <p>{item.description}</p>
            <div className="tags">
              {item.tags.map(tag => <span key={tag}>{tag}</span>)}
            </div>
          </motion.div>
        ))}
      </div>
    </section>
  )
}
