import React from 'react'
import Hero from './components/Hero'
import Work from './components/Work'
import About from './components/About'
import Contact from './components/Contact'
import { MotionConfig } from 'framer-motion'
import ScrollBasedReveal from './components/ScrollBasedReveal'

function App() {
  return (
    <MotionConfig transition={{ type: "tween", duration: 0.5 }}>
      <div className="app">
        <Hero />
        <Work />
        <About />
        <Contact />
        <ScrollBasedReveal />
        <div className="ambient-text"><span className="dot"></span> system online</div>
      </div>
    </MotionConfig>
  )
}

export default App
