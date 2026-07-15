import type { Metadata } from 'next';
import Link from 'next/link';

export const metadata: Metadata = {
  title: 'Contact Us',
  description:
    'Contact TKVibes for a free consultation. Get a quote for logo design, website development, SEO, Google Ads, Meta ads, automation, and digital marketing services.',
};

export default function ContactPage() {
  return (
    <>
      <section className="page-header">
        <div className="container-main">
          <div className="breadcrumb">
            <Link href="/">Home</Link>
            <span className="sep">/</span>
            <span className="current">Contact</span>
          </div>
          <h1>
            Get in <span>Touch</span>
          </h1>
          <p>
            Ready to start your digital journey? Let&apos;s talk about your project over a free
            consultation.
          </p>
        </div>
      </section>

      <section className="section-padding contact-section">
        <div className="container-main">
          <div className="contact-grid">
            {/* LEFT: Contact Info */}
            <div className="contact-info">
              <h3>
                Let&apos;s Build Your <span>Digital Presence</span>
              </h3>
              <p>
                Have a project in mind? Fill out the form or reach out directly. We&apos;ll get
                back to you within 24 hours with a custom proposal tailored to your needs.
              </p>
              <div className="contact-details">
                <div className="contact-detail">
                  <div
                    className="cd-icon"
                    style={{ background: 'rgba(79,70,229,0.1)', color: '#4f46e5' }}
                  >
                    <i className="fas fa-phone-alt"></i>
                  </div>
                  <div>
                    <h5>Phone</h5>
                    <p>
                      <a href="tel:+919818246938">+91 98182 46938</a>
                    </p>
                    <p style={{ fontSize: '0.82rem', color: '#94a3b8' }}>
                      Mon-Sat, 10:00 AM - 7:00 PM
                    </p>
                  </div>
                </div>
                <div className="contact-detail">
                  <div
                    className="cd-icon"
                    style={{ background: 'rgba(245,158,11,0.1)', color: '#f59e0b' }}
                  >
                    <i className="fas fa-envelope"></i>
                  </div>
                  <div>
                    <h5>Email</h5>
                    <p>
                      <a href="mailto:hello@tkvibes.com">hello@tkvibes.com</a>
                    </p>
                    <p style={{ fontSize: '0.82rem', color: '#94a3b8' }}>
                      We reply within 24 hours
                    </p>
                  </div>
                </div>
                <div className="contact-detail">
                  <div
                    className="cd-icon"
                    style={{ background: 'rgba(16,185,129,0.1)', color: '#059669' }}
                  >
                    <i className="fab fa-whatsapp"></i>
                  </div>
                  <div>
                    <h5>WhatsApp</h5>
                    <p>
                      <a href="https://wa.me/919818246938" target="_blank" rel="noopener noreferrer">
                        +91 98182 46938
                      </a>
                    </p>
                    <p style={{ fontSize: '0.82rem', color: '#94a3b8' }}>
                      Quickest way to reach us
                    </p>
                  </div>
                </div>
                <div className="contact-detail">
                  <div
                    className="cd-icon"
                    style={{ background: 'rgba(239,68,68,0.1)', color: '#dc2626' }}
                  >
                    <i className="fas fa-map-marker-alt"></i>
                  </div>
                  <div>
                    <h5>Location</h5>
                    <p>India</p>
                    <p style={{ fontSize: '0.82rem', color: '#94a3b8' }}>
                      Serving clients worldwide
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* RIGHT: Contact Form */}
            <div className="contact-form-box">
              <h4>Send Us a Message</h4>
              <form
                id="contactForm"
                action="https://formsubmit.co/hello@tkvibes.com"
                method="POST"
              >
                <input type="hidden" name="_subject" value="New Inquiry from TKVibes Website" />
                <input type="hidden" name="_captcha" value="false" />
                <input type="hidden" name="_template" value="table" />

                <div className="form-row">
                  <div className="form-group">
                    <label>
                      Your Name <span className="required">*</span>
                    </label>
                    <input type="text" name="name" required placeholder="John Doe" />
                  </div>
                  <div className="form-group">
                    <label>
                      Phone Number <span className="required">*</span>
                    </label>
                    <input type="tel" name="phone" required placeholder="+91 98765 43210" />
                  </div>
                </div>
                <div className="form-group">
                  <label>
                    Email Address <span className="required">*</span>
                  </label>
                  <input type="email" name="email" required placeholder="john@example.com" />
                </div>
                <div className="form-group">
                  <label>Service Interested In</label>
                  <select name="service">
                    <option value="">Select a service...</option>
                    <option>Logo Designing</option>
                    <option>Logo Animation</option>
                    <option>Website Designing</option>
                    <option>Hosting Management</option>
                    <option>Business Niche Advisory</option>
                    <option>Company Registration</option>
                    <option>Annual Reports</option>
                    <option>Product Brochure Design</option>
                    <option>SEO Services</option>
                    <option>Google My Business Listing</option>
                    <option>Meta Ads</option>
                    <option>Google Ads</option>
                    <option>n8n Automation Agents</option>
                    <option>Infographics</option>
                    <option>Comprehensive Package</option>
                    <option>Other / Custom</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>Budget Range</label>
                  <select name="budget">
                    <option value="">Select a range...</option>
                    <option>Under ₹5,000</option>
                    <option>₹5,000 - ₹15,000</option>
                    <option>₹15,000 - ₹35,000</option>
                    <option>₹35,000 - ₹75,000</option>
                    <option>₹75,000+</option>
                    <option>Not Sure Yet</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>
                    Project Details <span className="required">*</span>
                  </label>
                  <textarea
                    name="message"
                    required
                    placeholder="Tell us about your project, requirements, and any specific goals you have in mind..."
                  ></textarea>
                </div>
                <button
                  type="submit"
                  className="btn-custom btn-primary-custom"
                  style={{ width: '100%', justifyContent: 'center' }}
                >
                  <i className="fas fa-paper-plane"></i> Send Message
                </button>
                <p
                  style={{
                    textAlign: 'center',
                    color: '#94a3b8',
                    fontSize: '0.8rem',
                    marginTop: 12,
                  }}
                >
                  We respect your privacy. Your information is safe with us.
                </p>
              </form>
            </div>
          </div>
        </div>
      </section>

      {/* MAP */}
      <section className="section-padding map-section" style={{ paddingTop: 0 }}>
        <div className="container-main">
          <div className="map-container">
            <iframe
              src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d15282225.79979123!2d73.725024729412!3d20.750367397265!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x30635ff06b92b791%3A0xd78c4fa1854213a6!2sIndia!5e0!3m2!1sen!2sin!4v1"
              loading="lazy"
              referrerPolicy="no-referrer-when-downgrade"
              title="TKVibes Location - India"
            ></iframe>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="cta-section">
        <div className="container-main">
          <h2>Prefer a Quick Chat?</h2>
          <p>
            Reach out to us directly on WhatsApp for instant responses. We&apos;re usually online
            and happy to help.
          </p>
          <div className="cta-buttons">
            <a
              href="https://wa.me/919818246938"
              className="btn-custom btn-primary-custom"
              target="_blank"
              rel="noopener noreferrer"
            >
              <i className="fab fa-whatsapp"></i> WhatsApp Us Now
            </a>
            <a
              href="tel:+919818246938"
              className="btn-custom"
              style={{
                background: 'rgba(255,255,255,0.1)',
                color: '#fff',
                border: '1px solid rgba(255,255,255,0.2)',
              }}
            >
              <i className="fas fa-phone"></i> Call Us
            </a>
          </div>
        </div>
      </section>
    </>
  );
}