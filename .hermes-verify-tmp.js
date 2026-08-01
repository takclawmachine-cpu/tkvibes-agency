#!/usr/bin/env node
'use strict'
const fs = require('fs'), path = require('path')
const tmp = require('os').tmpdir()

const scriptPath = path.join(tmp, 'hermes-verify-mobile.css')
fs.writeFileSync(scriptPath, `
const BASE = 'C:\\\\Users\\\\takcl\\\\Desktop\\\\tkvibes-agency'
let fail = false

function check(what, ok) {
  const s = ok ? 'PASS' : 'FAIL'
  if (!ok) fail = true
  console.log('  ' + s + ' \\u2014 ' + what)
}

console.log('=== TKVibes Mobile Responsiveness ===\\n')

const css = require('fs').readFileSync(BASE + '/assets/css/styles.css', 'utf8')
console.log('[styles.css]')
check('Braces balanced', (css.match(/{/g)||[]).length === (css.match(/}/g)||[]).length)

const bps = css.match(/@media \\(max-width: [0-9]+px\\)/g) || []
check('Has 820px breakpoint', bps.some(b => b.includes('820')))
check('Has 480px breakpoint', bps.some(b => b.includes('480')))
check('Has 1080px breakpoint', bps.some(b => b.includes('1080')))
check('Has tabFadeIn keyframes', css.includes('tabFadeIn'))
check('Has aurora keyframes', css.includes('aurora-drift-one'))

// Check mobile-specific classes exist
const mob = css.split('@media (max-width: 480px)')[1] || ''
const mobChecks = [
  ['nav-panel mobile sizing', '.nav-panel'],
  ['section-padding mobile', '.section-padding'],
  ['hero-copy mobile', '.hero-copy h1'],
  ['pricing-grid mobile', '.pricing-grid'],
  ['btn-custom mobile', '.btn-custom'],
  ['service-menu-grid mobile 1-col', '.service-menu-grid'],
  ['feature-grid mobile 1-col', '.feature-grid'],
  ['contact-grid mobile 1-col', '.contact-grid'],
  ['footer-grid mobile 1-col', '.footer-grid'],
  ['plan-modal mobile', '.plan-modal'],
  ['faq-item mobile', '.faq-item summary'],
  ['filter-bar mobile', '.filter-bar'],
  ['stats-row 2-col mobile', '.stats-row'],
  ['enterprise-form mobile', '.enterprise-form'],
  ['proof-strip mobile', '.proof-strip'],
]
mobChecks.forEach(([name, cls]) => check(name, mob.includes(cls)))

// Check all HTML pages load and have consistent CSS version
console.log('\\n[HTML pages]')
const pages = ['404.html','about.html','contact.html','index.html','packages.html','portfolio.html','services.html']
const cssHash = 'styles.css?v=20260801b'
pages.forEach(p => {
  const h = fs.readFileSync(BASE + '/' + p, 'utf8')
  check(p + ' - CSS version ' + cssHash, h.includes(cssHash))
  check(p + ' - viewport meta', h.includes('width=device-width, initial-scale=1'))
  check(p + ' - has theme script', h.includes('localStorage.getItem'))
  check(p + ' - font preconnect', h.includes('fonts.googleapis.com'))
})

console.log('\\n' + (fail ? 'FAILED' : 'ALL PASSED'))
process.exit(fail ? 1 : 0)
`)

console.log('Script written to', scriptPath)