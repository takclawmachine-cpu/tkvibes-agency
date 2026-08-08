import { motion } from 'framer-motion'

export default function Footer() {
  return (
    <footer>
      <span>&copy; 2026 TKVibes. All rights reserved.</span>
      <div className="socials">
        <motion.a
          href="#"
          target="_blank"
          rel="noopener"
          whileHover={{ color: 'var(--accent)' }}
        >
          Twitter
        </motion.a>
        <motion.a
          href="#"
          target="_blank"
          rel="noopener"
          whileHover={{ color: 'var(--accent)' }}
        >
          GitHub
        </motion.a>
        <motion.a
          href="#"
          target="_blank"
          rel="noopener"
          whileHover={{ color: 'var(--accent)' }}
        >
          Dribbble
        </motion.a>
      </div>
    </footer>
  )
}
