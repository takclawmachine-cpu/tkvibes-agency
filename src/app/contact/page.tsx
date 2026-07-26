import type { Metadata } from 'next'
import Link from 'next/link'
import MultiSelectServices from '@/components/MultiSelectServices'

export const metadata: Metadata = {
  title: 'Contact',
  description:
    'Contact TKVibes for website design, branding, SEO, ads, and automation support.',
}

const contactDetails = [
  {
    iconClass: 'fas fa-phone',
    title: 'Phone',
    value: '+91 98182 46938',
    href: 'tel:+919****6938',
    note: 'Mon to Sat, 10:00 AM to 7:00 PM',
  },
  {
    iconClass: 'fas fa-envelope',
    title: 'Email',
    value: 'services@tkvibes.in',
    href: 'mailto:services@tkvibes.in',
    note: 'Replies usually within 24 hours',
  },
  {
    iconClass: 'fab fa-whatsapp',
    title: 'WhatsApp',
    value: '+91 98182 46938',
    href: 'https://wa.me/919818246938',
    note: 'Best for the fastest response',
  },
  {
    iconClass: 'fas fa-location-dot',
    title: 'Location',
    value: 'India',
    note: 'Serving clients worldwide',
  },
]

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
            Start the <span>Conversation</span>
          </h1>
          <p>
            If you need a sharper website, a better brand presence, or a more conversion-focused
            digital experience, we would love to hear about it.
          </p>
        </div>
      </section>

      <section className="section-padding">
        <div className="container-main">
          <div className="contact-grid">
            <div className="contact-info">
              <span className="eyebrow">Reach out</span>
              <h3>
                Let&apos;s build a digital presence that feels more premium and more effective.
              </h3>
              <p>
                Share your current challenge, what you want the business to look like online, and
                what needs fixing first. We will help you map the next step.
              </p>

              <div className="contact-details">
                {contactDetails.map((item) => (
                  <div key={item.title} className="contact-detail">
                    <div className="cd-icon">
                      <i className={item.iconClass} />
                    </div>
                    <div>
                      <h5>{item.title}</h5>
                      <p>
                        {item.href ? (
                          <a href={item.href} target={item.href.startsWith('http') ? '_blank' : undefined} rel={item.href.startsWith('http') ? 'noopener noreferrer' : undefined}>
                            {item.value}
                          </a>
                        ) : (
                          item.value
                        )}
                      </p>
                      <p className="contact-note">{item.note}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="contact-form-box">
              <p className="contact-form-headline">
                <span className="contact-form-headline-text">
                  Select Your Services,
                  <br />
                  Set Your Price
                </span>
              </p>
              <h4>Send us a message</h4>
              <form action="https://formsubmit.co/services@tkvibes.in" method="POST">
                <input type="hidden" name="_subject" value="New inquiry from TKVibes website" />
                <input type="hidden" name="_captcha" value="false" />
                <input type="hidden" name="_template" value="table" />

                <div className="form-row">
                  <div className="form-group">
                    <label htmlFor="name">
                      Your name <span className="required">*</span>
                    </label>
                    <input id="name" type="text" name="name" required placeholder="John Doe" />
                  </div>
                  <div className="form-group">
                    <label htmlFor="phone">
                      Phone number <span className="required">*</span>
                    </label>
                    <input
                      id="phone"
                      type="tel"
                      name="phone"
                      required
                      placeholder="+91 98765 43210"
                    />
                  </div>
                </div>

                <div className="form-group">
                  <label htmlFor="email">
                    Email address <span className="required">*</span>
                  </label>
                  <input
                    id="email"
                    type="email"
                    name="email"
                    required
                    placeholder="john@example.com"
                  />
                </div>

                <div className="form-group">
                  <label>Services interested in</label>
                  <MultiSelectServices />
                </div>

                <div className="form-group">
                  <label htmlFor="budget">Budget range</label>
                  <select id="budget" name="budget" defaultValue="">
                    <option value="" disabled>
                      Select a range
                    </option>
                    <option>Under Rs 5,000</option>
                    <option>Rs 5,000 to Rs 15,000</option>
                    <option>Rs 15,000 to Rs 35,000</option>
                    <option>Rs 35,000 to Rs 75,000</option>
                    <option>Rs 75,000+</option>
                    <option>Not sure yet</option>
                  </select>
                </div>

                <div className="form-group">
                  <label htmlFor="message">
                    Project details <span className="required">*</span>
                  </label>
                  <textarea
                    id="message"
                    name="message"
                    required
                    placeholder="Tell us what needs improving, what stage the business is at, and what kind of outcome you want."
                  />
                </div>

                <button type="submit" className="btn-custom btn-primary-custom full-width">
                  <i className="fas fa-paper-plane" />
                  Send Message
                </button>
                <p className="contact-privacy">
                  Your information stays private and is only used to respond to your inquiry.
                </p>
              </form>
            </div>
          </div>
        </div>
      </section>

      <section className="section-padding">
        <div className="container-main">
          <div className="map-container">
            <iframe
              src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d15282225.79979123!2d73.725024729412!3d20.750367397265!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x30635ff06b92b791%3A0xd78c4fa1854213a6!2sIndia!5e0!3m2!1sen!2sin!4v1"
              loading="lazy"
              referrerPolicy="no-referrer-when-downgrade"
              title="TKVibes location"
            />
          </div>
        </div>
      </section>

      <section className="cta-section">
        <div className="container-main cta-panel">
          <span className="eyebrow">Need a quick answer?</span>
          <h2>WhatsApp is the fastest way to reach us.</h2>
          <p>
            If you already know what needs fixing, send us a message and we can talk through scope,
            timing, and the best first move.
          </p>
          <div className="cta-buttons">
            <a
              href="https://wa.me/919818246938"
              className="btn-custom btn-primary-custom"
              target="_blank"
              rel="noopener noreferrer"
            >
              <i className="fab fa-whatsapp" />
              WhatsApp Us
            </a>
            <a href="tel:+919****6938" className="btn-custom btn-outline-custom">
              <i className="fas fa-phone" />
              Call Us
            </a>
          </div>
        </div>
      </section>
    </>
  )
}
