import Link from 'next/link'
import Logo from '@/components/layout/Logo'

export default function Footer() {
  return (
    <footer className="footer">
      <div className="container-main footer-grid">
        <div className="footer-brand">
          <Logo variant="full" className="footer-brand-logo" />
          <p>
            We design premium websites, brand systems, and growth funnels for businesses that
            want to look sharper and convert better.
          </p>
          <div className="footer-social">
            <a
              href="https://wa.me/919818246938"
              target="_blank"
              rel="noopener noreferrer"
              aria-label="WhatsApp"
            >
              <i className="fab fa-whatsapp" />
            </a>
            <a href="mailto:services@tkvibes.in" aria-label="Email">
              <i className="fas fa-envelope" />
            </a>
          </div>
        </div>

        <div>
          <h4>Company</h4>
          <ul>
            <li><Link href="/about">About</Link></li>
            <li><Link href="/services">Services</Link></li>
            <li><Link href="/packages">Packages</Link></li>
            <li><Link href="/portfolio">Portfolio</Link></li>
          </ul>
        </div>

        <div>
          <h4>Services</h4>
          <ul>
            <li><Link href="/services">Web Design</Link></li>
            <li><Link href="/services">Brand Identity</Link></li>
            <li><Link href="/services">SEO and Ads</Link></li>
            <li><Link href="/services">Automation</Link></li>
          </ul>
        </div>

        <div>
          <h4>Contact</h4>
          <ul>
            <li><a href="mailto:services@tkvibes.in">services@tkvibes.in</a></li>
            <li><a href="tel:+919818246938">+91 98182 46938</a></li>
            <li><a href="https://wa.me/919818246938">WhatsApp</a></li>
            <li><span>India, serving clients worldwide</span></li>
          </ul>
        </div>
      </div>

      <div className="container-main footer-bottom">
        <p>© {new Date().getFullYear()} TKVibes Agency. All rights reserved.</p>
        <p>Built for modern brands that want better digital presence.</p>
      </div>
    </footer>
  )
}
