import { motion } from 'framer-motion'

export default function Contact() {
  return (
    <section id="contact" className="section">
      <motion.div
        className="section-header"
        initial={{ opacity: 0, y: 40 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, amount: 0.3 }}
        transition={{ duration: 0.8 }}
      >
        <div className="label">Contact</div>
        <h2>Let's build something <strong>extraordinary</strong></h2>
        <p>Have a project in mind? We'd love to hear about it. Drop us a message and we'll get back to you within 24 hours.</p>
      </motion.div>

      <motion.form
        className="contact-form"
        initial={{ opacity: 0, y: 40 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, amount: 0.3 }}
        transition={{ duration: 0.8, delay: 0.1 }}
        onSubmit={(e) => {
          e.preventDefault()
          alert("Thanks for reaching out! We'll be in touch shortly.")
        }}
      >
        <input type="text" placeholder="Your name" required />
        <input type="email" placeholder="Your email" required />
        <input type="text" placeholder="Project type" />
        <textarea placeholder="Tell us about your project..." required></textarea>
        <motion.button
          type="submit"
          className="btn btn-primary"
          style={{ alignSelf: 'flex-start' }}
          whileHover={{ scale: 1.05, y: -2 }}
          whileTap={{ scale: 0.98 }}
        >
          Send message
        </motion.button>
      </motion.form>
    </section>
  )
}
