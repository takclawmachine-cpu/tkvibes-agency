'use client';

import Link from 'next/link';

export default function Footer() {
  return (
    <footer>
      <div className="container-main">
        <div className="footer-grid">
          <div className="footer-brand">
            <Link href="/" className="nav-logo" style={{ marginBottom: 16 }}>
              <div className="logo-icon">TK</div>
              <span className="brand-text">
                TKVibes<small>DIGITAL AGENCY</small>
              </span>
            </Link>
            <p>
              Your trusted partner for digital growth. We combine creative design, strategic marketing, and
              automation to help businesses thrive online.
            </p>
            <div className="footer-social">
              <a href="#" aria-label="Facebook">
                <i className="fab fa-facebook-f"></i>
              </a>
              <a href="#" aria-label="Instagram">
                <i className="fab fa-instagram"></i>
              </a>
              <a href="#" aria-label="LinkedIn">
                <i className="fab fa-linkedin-in"></i>
              </a>
              <a href="#" aria-label="YouTube">
                <i className="fab fa-youtube"></i>
              </a>
            </div>
          </div>
          <div className="footer-col">
            <h4>Quick Links</h4>
            <ul>
              <li><Link href="/">Home</Link></li>
              <li><Link href="/about">About Us</Link></li>
              <li><Link href="/services">Services</Link></li>
              <li><Link href="/packages">Packages</Link></li>
              <li><Link href="/portfolio">Portfolio</Link></li>
              <li><Link href="/contact">Contact</Link></li>
            </ul>
          </div>
          <div className="footer-col">
            <h4>Services</h4>
            <ul>
              <li><Link href="/services">Logo Design</Link></li>
              <li><Link href="/services">Web Development</Link></li>
              <li><Link href="/services">SEO Services</Link></li>
              <li><Link href="/services">Google Ads</Link></li>
              <li><Link href="/services">Meta Ads</Link></li>
              <li><Link href="/services">n8n Automation</Link></li>
            </ul>
          </div>
          <div className="footer-col">
            <h4>Contact Us</h4>
            <ul>
              <li>
                <a href="tel:+919818246938">
                                  <i className="fas fa-phone"></i> +91 98182 46938
                </a>
              </li>
              <li>
                <a href="mailto:hello@tkvibes.com">
                  <i className="fas fa-envelope"></i> hello@tkvibes.com
                </a>
              </li>
              <li>
                <a href="#">
                  <i className="fas fa-map-marker-alt"></i> India
                </a>
              </li>
              <li>
                <a href="https://wa.me/919818246938" target="_blank" rel="noopener noreferrer">
                  <i className="fab fa-whatsapp"></i> WhatsApp
                </a>
              </li>
            </ul>
          </div>
        </div>
        <div className="footer-bottom">
          <span>&copy; 2025 TKVibes. All rights reserved.</span>
          <span>
            Built with <i className="fas fa-heart" style={{ color: '#ef4444' }}></i> for digital excellence
          </span>
        </div>
      </div>
    </footer>
  );
}