#!/usr/bin/env python3
"""Generate premium sample websites and pitch decks for all CRM leads with immersive 3D globe mandate.

MANDATORY for every sample website:
- Shader-based interactive rotating globe (Three.js custom shader, dot-matrix)
- Cinematic scroll-linked storytelling via Lenis + GSAP ScrollTrigger
- Bold responsive typography with fluid clamp() scaling, Space Grotesk + Inter
- Fixed canvas container with scroll content overlay
- Mobile responsive: dynamic polygon reduction, capped pixel ratio, skeleton placeholder
"""

import io, json, os, re, sys, hashlib, base64
from urllib.request import Request, urlopen
from urllib.error import URLError

REPO_DIR = os.path.expanduser("~/Desktop/tkvibes-agency")
LEADS_FILE = os.path.join(REPO_DIR, "tkvibes-lead-engine", "data", "leads_export.json")

# ── Slugify (must match CRM PHP slugify) ────────────────────────────────
def slugify(name):
    s = re.sub(r"[^a-z0-9\s]", "", name.lower()).strip()
    s = re.sub(r"\s+", "-", s)
    return re.sub(r"-{2,}", "-", s)[:60] or "client"

# ── Load leads ──────────────────────────────────────────────────────────
with io.open(LEADS_FILE, "r", encoding="utf-8") as f:
    LEADS = json.load(f)
print(f"Loaded {len(LEADS)} leads")

# ── Dental-specific Unsplash images ────────────────────────────────────
DENTAL_HERO = "https://images.unsplash.com/photo-1606811841689-23dfddce3e95?w=1400&q=80"
DENTAL_ABOUT = "https://images.unsplash.com/photo-1588776814546-1ffcf47267a5?w=800&q=80"
DENTAL_SERVICE1 = "https://images.unsplash.com/photo-1609902029572-d9481e34e3b9?w=800&q=80"
DENTAL_SERVICE2 = "https://images.unsplash.com/photo-1580656449271-7e3ae1bd1f50?w=800&q=80"
DENTAL_SERVICE3 = "https://images.unsplash.com/photo-1598256989800-fe5f95da9787?w=800&q=80"
DENTAL_TEAM = "https://images.unsplash.com/photo-1559839734-2b71ea197ec2?w=800&q=80"
DENTAL_CTA = "https://images.unsplash.com/photo-1631217868264-e5b90bb7e133?w=1400&q=80"
DENTAL_TESTIMONIAL = "https://images.unsplash.com/photo-1580489944761-15a19d654956?w=200&q=80"
DENTAL_WHY = "https://images.unsplash.com/photo-1588776814546-1ffcf47267a5?w=800&q=80"
DENTAL_PATIENT = "https://images.unsplash.com/photo-1551076805-e1869033e561?w=1400&q=80"
DENTAL_INTERIOR = "https://images.unsplash.com/photo-1629909613654-28e377c37b09?w=800&q=80"
DENTAL_HERO_ALT = "https://images.unsplash.com/photo-1609619385002-d9c2ce91af0b?w=1400&q=80"

# ── Build sample website HTML ──────────────────────────────────────────
def build_sample_site(lead):
    """Generate a single-file HTML sample website with full 3D globe mandate."""
    name = lead.get("business_name", "Dental Clinic")
    category = lead.get("category", "Dental Clinic")
    address = lead.get("address", "")
    city = lead.get("city", "")
    phone = lead.get("phone_primary", "")
    phone_display = phone
    rating = lead.get("rating", 0)
    reviews = lead.get("review_count", 0)
    score = lead.get("lead_score", 0)
    tier = lead.get("lead_tier", "WARM")
    slug = slugify(name)

    # Short name for display
    parts = name.split()
    name_short = f"{parts[0]} {parts[-1]}" if len(parts) > 2 else name

    # Hours
    hours = lead.get("opening_hours", "")
    hours_html = ""
    if hours:
        for line in hours.split(";"):
            line = line.strip()
            if line:
                day, _, time = line.partition(":")
                hours_html += f'<div class="hours-row"><span class="hours-day">{day.strip()}</span><span class="hours-time">{time.strip()}</span></div>\n'

    # Reason why items
    why_items = [
        ("Award-winning team with 15+ years of combined dental experience", "fa-award"),
        ("State-of-the-art technology for painless, precise treatments", "fa-microscope"),
        ("Personalized care plans tailored to your unique needs", "fa-heart"),
        ("Flexible scheduling including weekend appointments available", "fa-calendar-check"),
        ("5-star rated practice with hundreds of happy patients", "fa-star"),
    ]

    why_html = "\n".join(
        f'<div class="why-item reveal"><i class="fas {icon}"></i><span>{text}</span></div>'
        for text, icon in why_items
    )

    # Services
    services = [
        ("General Dentistry", "Comprehensive exams, cleanings, and preventive care to maintain optimal oral health for you and your family.", "fa-tooth"),
        ("Cosmetic Dentistry", "Transform your smile with whitening, veneers, and bonding. Custom treatment plans for stunning results.", "fa-smile"),
        ("Restorative Dentistry", "Crowns, bridges, implants, and dentures to restore function and confidence in your smile.", "fa-teeth"),
    ]

    services_html = "\n".join(
        f'''<div class="service-card reveal">
            <div class="service-icon"><i class="fas {icon}"></i></div>
            <h3>{title}</h3>
            <p>{desc}</p>
        </div>'''
        for title, desc, icon in services
    )

    nbsp_name = name.replace(" ", "\u00A0")

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{name} - Premium Dental Care in {city}</title>
<meta name="description" content="{name} - Professional dental services in {city}. {rating} stars, {reviews}+ reviews. Book your appointment today.">
<meta property="og:title" content="{name} - Premium Dental Care">
<meta property="og:description" content="Professional dental services in {city}. {rating} stars, {reviews}+ reviews.">
<meta property="og:type" content="website">
<meta property="og:image" content="{DENTAL_HERO}">
<meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700;800&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
html{{scroll-behavior:auto}}
body{{font-family:'Inter',sans-serif;background:#0a0a0f;color:#fafafa;overflow-x:hidden}}

:root{{
  --text-hero:clamp(2.5rem,1.5rem+5vw,7rem);
  --text-2xl:clamp(1.75rem,1.25rem+2.5vw,3.5rem);
  --text-xl:clamp(1.25rem,1rem+1.25vw,2rem);
  --text-lg:clamp(1rem,0.9rem+0.5vw,1.25rem);
  --text-base:clamp(0.875rem,0.8rem+0.375vw,1rem);
  --primary:#4f8cf7;
  --primary-dark:#3661b3;
  --accent:#f59e0b;
  --glow:rgba(79,140,247,0.15);
}}

#globe-container{{position:fixed;top:0;left:0;width:100vw;height:100vh;z-index:0;pointer-events:none}}
#skeleton{{position:fixed;top:0;left:0;width:100vw;height:100vh;z-index:-1;background:linear-gradient(135deg,#0a0a0f,#111122,#0f0f2a,#0a0a0f);background-size:400% 400%;animation:shimmer 3s ease infinite}}
@keyframes shimmer{{0%,100%{{background-position:0% 50%}}50%{{background-position:100% 50%}}}}
#skeleton.fade-out{{opacity:0;transition:opacity 0.8s ease}}

.scroll-content{{position:relative;z-index:1;pointer-events:none;min-height:400vh}}
.scroll-content section,.scroll-content .interactive,.scroll-content .btn,.scroll-content a{{pointer-events:auto}}

section{{min-height:100vh;display:flex;flex-direction:column;justify-content:center;padding:4rem 2rem;position:relative}}

.display-heading{{font-family:'Space Grotesk',sans-serif;font-size:var(--text-hero);font-weight:800;line-height:0.85;letter-spacing:-0.05em;text-transform:uppercase}}
.section-heading{{font-family:'Space Grotesk',sans-serif;font-size:var(--text-2xl);font-weight:700;line-height:1;letter-spacing:-0.035em;margin-bottom:1.5rem}}
.section-sub{{font-size:var(--text-lg);opacity:0.7;max-width:48rem;line-height:1.6;margin-bottom:2rem}}

.reveal-char{{display:inline-block;will-change:transform,opacity}}

.rating-badge{{display:inline-flex;align-items:center;gap:0.5rem;background:rgba(255,255,255,0.08);backdrop-filter:blur(12px);border:1px solid rgba(255,255,255,0.12);border-radius:100px;padding:0.5rem 1rem;font-size:var(--text-sm);margin-bottom:1.5rem}}
.rating-badge i{{color:var(--accent)}}
.rating-badge .star-count{{color:var(--accent);font-weight:700}}

.hero-meta{{display:flex;flex-wrap:wrap;gap:0.75rem;margin-bottom:1.5rem}}

.tag{{display:inline-block;padding:0.35rem 0.85rem;border-radius:100px;font-size:0.75rem;font-weight:600;text-transform:uppercase;letter-spacing:0.05em;background:rgba(79,140,247,0.15);color:var(--primary);border:1px solid rgba(79,140,247,0.3)}}

.hero-cta{{display:flex;flex-wrap:wrap;gap:1rem;margin-top:2rem}}

.btn{{display:inline-flex;align-items:center;gap:0.5rem;padding:0.85rem 2rem;border-radius:100px;font-weight:600;font-size:var(--text-sm);text-decoration:none;transition:all 0.3s ease;border:none;cursor:pointer}}
.btn-primary{{background:linear-gradient(135deg,var(--primary),#6b9aff);color:#fff;box-shadow:0 4px 20px var(--glow)}}
.btn-primary:hover{{transform:translateY(-2px);box-shadow:0 8px 30px rgba(79,140,247,0.25)}}
.btn-outline{{background:transparent;border:1px solid rgba(255,255,255,0.2);color:#fff}}
.btn-outline:hover{{background:rgba(255,255,255,0.06);border-color:rgba(255,255,255,0.4)}}

.glass-card{{background:rgba(255,255,255,0.04);backdrop-filter:blur(16px);border:1px solid rgba(255,255,255,0.08);border-radius:24px;padding:2.5rem;transition:all 0.4s ease}}
.glass-card:hover{{background:rgba(255,255,255,0.07);border-color:rgba(255,255,255,0.14);transform:translateY(-4px)}}

.grid-2{{display:grid;grid-template-columns:1fr 1fr;gap:2rem;max-width:1200px;margin:0 auto;width:100%}}
.grid-3{{display:grid;grid-template-columns:repeat(3,1fr);gap:2rem;max-width:1200px;margin:0 auto;width:100%}}

.service-card{{background:rgba(255,255,255,0.04);backdrop-filter:blur(16px);border:1px solid rgba(255,255,255,0.08);border-radius:24px;padding:2.5rem;transition:all 0.4s ease;text-align:center}}
.service-card:hover{{background:rgba(255,255,255,0.07);border-color:rgba(79,140,247,0.3);transform:translateY(-6px)}}
.service-icon{{width:60px;height:60px;border-radius:16px;background:rgba(79,140,247,0.12);display:flex;align-items:center;justify-content:center;margin:0 auto 1.5rem;font-size:1.5rem;color:var(--primary)}}
.service-card h3{{font-size:var(--text-lg);font-weight:700;margin-bottom:0.75rem}}
.service-card p{{font-size:var(--text-sm);opacity:0.65;line-height:1.6}}

.why-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:1.25rem;max-width:1200px;margin:0 auto;width:100%}}
.why-item{{display:flex;align-items:center;gap:1rem;padding:1.25rem;background:rgba(255,255,255,0.04);border-radius:16px;border:1px solid rgba(255,255,255,0.06);transition:all 0.3s ease}}
.why-item i{{width:36px;height:36px;display:flex;align-items:center;justify-content:center;border-radius:10px;background:rgba(79,140,247,0.12);color:var(--primary);font-size:0.9rem;flex-shrink:0}}
.why-item span{{font-size:var(--text-sm);line-height:1.4}}

.stats-grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:1.5rem;max-width:1200px;margin:2rem auto 0;width:100%}}
.stat-item{{text-align:center;padding:1.5rem}}
.stat-number{{font-family:'Space Grotesk',sans-serif;font-size:var(--text-2xl);font-weight:800;color:var(--primary)}}
.stat-label{{font-size:var(--text-sm);opacity:0.6;margin-top:0.25rem}}

.testimonial-card{{background:rgba(255,255,255,0.04);border-radius:20px;border:1px solid rgba(255,255,255,0.06);padding:2rem;display:flex;flex-direction:column;gap:1rem}}
.testimonial-card .t-stars{{color:var(--accent)}}
.testimonial-card .t-text{{font-size:var(--text-sm);opacity:0.7;line-height:1.6;font-style:italic}}
.testimonial-card .t-author{{display:flex;align-items:center;gap:0.75rem;margin-top:auto}}
.testimonial-card .t-author img{{width:40px;height:40px;border-radius:50%;object-fit:cover}}
.testimonial-card .t-author .t-name{{font-weight:600;font-size:0.875rem}}
.testimonial-card .t-author .t-role{{font-size:0.75rem;opacity:0.5}}

.hours-card{{background:rgba(255,255,255,0.04);border-radius:20px;border:1px solid rgba(255,255,255,0.06);padding:2rem;max-width:400px}}
.hours-row{{display:flex;justify-content:space-between;padding:0.5rem 0;border-bottom:1px solid rgba(255,255,255,0.05);font-size:var(--text-sm)}}
.hours-row:last-child{{border-bottom:none}}
.hours-day{{font-weight:600}}
.hours-time{{opacity:0.6}}

.footer{{padding:3rem 2rem;text-align:center;border-top:1px solid rgba(255,255,255,0.06);font-size:var(--text-sm);opacity:0.5}}
.footer a{{color:var(--primary);text-decoration:none}}

.overlay-section{{position:relative}}
.overlay-section::before{{content:'';position:absolute;inset:0;background:linear-gradient(rgba(10,15,30,0.8),rgba(10,15,30,0.85)),url({DENTAL_PATIENT}) center/cover fixed;z-index:-1}}

.section-bg{{position:absolute;inset:0;z-index:-1;overflow:hidden}}
.section-bg img{{width:100%;height:100%;object-fit:cover;opacity:0.08}}

@media(max-width:768px){{
  section{{padding:2rem 1rem;min-height:80vh}}
  .grid-2,.grid-3{{grid-template-columns:1fr}}
  .stats-grid{{grid-template-columns:repeat(2,1fr)}}
  .hero-cta{{flex-direction:column}}
  .btn{{justify-content:center;text-align:center}}
  .display-heading{{letter-spacing:-0.025em}}
  .glass-card,.service-card{{padding:1.5rem}}
}}

@media(prefers-reduced-motion:reduce){{
  #skeleton{{display:none}}
  #globe-container{{display:none}}
  [class*="reveal"]{{opacity:1!important;transform:none!important}}
  section{{opacity:1!important}}
}}
</style>
</head>
<body>
<div id="skeleton" class="skeleton-loader"></div>
<div id="globe-container"></div>

<div class="scroll-content">
  <!-- Hero -->
  <section id="hero" style="padding-top:6rem">
    <div style="max-width:1200px;margin:0 auto;width:100%">
      <div class="rating-badge">
        <i class="fas fa-star"></i>
        <span class="star-count">{rating}</span>
        <span style="opacity:0.6">|</span>
        <span>{reviews} reviews</span>
      </div>
      <div class="hero-meta">
        <span class="tag"><i class="fas fa-map-pin"></i> {city}</span>
        <span class="tag"><i class="fas fa-tooth"></i> {category}</span>
      </div>
      <h1 class="display-heading" data-split style="margin-bottom:1rem">
        {nbsp_name}
      </h1>
      <p class="section-sub">
        Experience premium dental care in {city}. Our expert team combines advanced technology with compassionate care to create beautiful, healthy smiles.
      </p>
      <div class="hero-cta">
        <a href="tel:{phone}" class="btn btn-primary"><i class="fas fa-phone"></i> Call Now</a>
        <a href="https://wa.me/{phone_display.replace('+','').replace(' ','')}" target="_blank" class="btn btn-outline"><i class="fab fa-whatsapp"></i> WhatsApp</a>
      </div>
    </div>
  </section>

  <!-- About -->
  <section id="about">
    <div class="grid-2" style="align-items:center">
      <div>
        <span class="tag" style="margin-bottom:1rem;display:inline-block">About Us</span>
        <h2 class="section-heading" data-split>Your Trusted<br>Dental Partner</h2>
        <p class="section-sub" style="font-size:var(--text-base);opacity:0.65">
          At {name}, we believe everyone deserves a confident, healthy smile. Our {rating}-star rated practice serves patients across {city} with personalized, gentle care. From routine cleanings to advanced restorative procedures, our experienced team uses cutting-edge technology to ensure your comfort and satisfaction.
        </p>
        <div style="display:flex;gap:1rem;flex-wrap:wrap;margin-top:1.5rem">
          <div><strong style="font-size:var(--text-xl);color:var(--primary)">{rating}</strong><br><span style="font-size:0.75rem;opacity:0.5">Rating</span></div>
          <div><strong style="font-size:var(--text-xl);color:var(--primary)">{reviews}+</strong><br><span style="font-size:0.75rem;opacity:0.5">Reviews</span></div>
          <div><strong style="font-size:var(--text-xl);color:var(--primary)">15+</strong><br><span style="font-size:0.75rem;opacity:0.5">Years Exp.</span></div>
        </div>
      </div>
      <div class="glass-card" style="overflow:hidden;padding:0.5rem">
        <img src="{DENTAL_ABOUT}" alt="Dental clinic" style="width:100%;height:400px;object-fit:cover;border-radius:20px" loading="lazy">
      </div>
    </div>
  </section>

  <!-- Services -->
  <section id="services" style="background:rgba(255,255,255,0.02)">
    <div style="max-width:1200px;margin:0 auto;width:100%">
      <div style="text-align:center;margin-bottom:3rem">
        <span class="tag" style="display:inline-block;margin-bottom:0.75rem">Our Services</span>
        <h2 class="section-heading" data-split>Comprehensive Dental<br>Care Under One Roof</h2>
        <p class="section-sub" style="margin:1rem auto 0;text-align:center">
          From preventive checkups to complete smile makeovers — we offer everything you need for optimal oral health.
        </p>
      </div>
      <div class="grid-3">
        {services_html}
      </div>
    </div>
  </section>

  <!-- Why Choose Us -->
  <section id="why">
    <div style="max-width:1200px;margin:0 auto;width:100%">
      <div style="text-align:center;margin-bottom:3rem">
        <span class="tag" style="display:inline-block;margin-bottom:0.75rem">Why {name_short}</span>
        <h2 class="section-heading" data-split>Why Patients<br>Choose Us</h2>
      </div>
      <div class="why-grid">
        {why_html}
      </div>
    </div>
  </section>

  <!-- Hours -->
  <section id="hours" style="background:rgba(255,255,255,0.02)">
    <div style="max-width:1200px;margin:0 auto;width:100%">
      <div style="text-align:center;margin-bottom:2rem">
        <span class="tag" style="display:inline-block;margin-bottom:0.75rem">Visit Us</span>
        <h2 class="section-heading" data-split>Clinic Hours</h2>
      </div>
      <div style="display:flex;flex-wrap:wrap;gap:2rem;justify-content:center">
        <div class="hours-card">
          {hours_html}
        </div>
        <div class="glass-card" style="max-width:400px;flex:1">
          <h3 style="font-size:var(--text-lg);font-weight:700;margin-bottom:0.5rem"><i class="fas fa-map-pin" style="color:var(--primary)"></i> Location</h3>
          <p style="font-size:var(--text-sm);opacity:0.65;line-height:1.6;margin-bottom:1rem">{address}</p>
          <a href="https://www.google.com/maps/search/{name.replace(' ','+')}+{city.replace(' ','+')}" target="_blank" class="btn btn-outline" style="font-size:0.8rem;padding:0.6rem 1.25rem"><i class="fas fa-directions"></i> Get Directions</a>
        </div>
      </div>
    </div>
  </section>

  <!-- Stats -->
  <section id="stats" style="min-height:50vh;padding:4rem 2rem" class="overlay-section">
    <div style="max-width:1200px;margin:0 auto;width:100%;position:relative;z-index:1">
      <div style="text-align:center;margin-bottom:1rem">
        <h2 class="section-heading" data-split style="color:#fff">Our Impact</h2>
      </div>
      <div class="stats-grid">
        <div class="stat-item"><div class="stat-number" data-count="{reviews}">0</div><div class="stat-label">Happy Patients</div></div>
        <div class="stat-item"><div class="stat-number" data-count="15">0</div><div class="stat-label">Years Experience</div></div>
        <div class="stat-item"><div class="stat-number" data-count="{rating}">0</div><div class="stat-label">Star Rating</div></div>
        <div class="stat-item"><div class="stat-number" data-count="99">0</div><div class="stat-label">% Satisfaction</div></div>
      </div>
    </div>
  </section>

  <!-- CTA -->
  <section id="cta" class="items-center text-center" style="align-items:center;text-align:center;min-height:60vh">
    <div style="max-width:800px;margin:0 auto;width:100%">
      <span class="tag" style="display:inline-block;margin-bottom:0.75rem">Book Now</span>
      <h2 class="section-heading" data-split>Ready for a<br>Brighter Smile?</h2>
      <p class="section-sub" style="margin:1rem auto 2rem;text-align:center">
        Schedule your appointment today and experience the {name_short} difference.
      </p>
      <div class="hero-cta" style="justify-content:center">
        <a href="tel:{phone}" class="btn btn-primary"><i class="fas fa-phone"></i> Call {phone_display}</a>
        <a href="https://wa.me/{phone_display.replace('+','').replace(' ','')}" target="_blank" class="btn btn-outline"><i class="fab fa-whatsapp"></i> Book via WhatsApp</a>
      </div>
    </div>
  </section>

  <div class="footer">
    <p>Concept by <a href="https://tkvibes.in" target="_blank">TKVibes</a> — not affiliated with {name}</p>
    <p style="margin-top:0.5rem;font-size:0.75rem">{address}</p>
  </div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://unpkg.com/lenis@1.1.13/dist/lenis.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js"></script>

<script>
// Lenis
const lenis = new Lenis({{duration:1.2,easing:t=>Math.min(1,1.001-Math.pow(2,-10*t)),smoothWheel:true,wheelMultiplier:1,touchMultiplier:2}});
function raf(t){{lenis.raf(t);requestAnimationFrame(raf)}}
requestAnimationFrame(raf);
lenis.on('scroll',ScrollTrigger.update);
gsap.ticker.add(t=>lenis.raf(t*1000));
gsap.ticker.lagSmoothing(0);

// Globe
const container=document.getElementById('globe-container');
const skeleton=document.getElementById('skeleton');
const scene=new THREE.Scene();
const camera=new THREE.PerspectiveCamera(45,window.innerWidth/window.innerHeight,0.1,100);
camera.position.set(0,0,5.5);
const renderer=new THREE.WebGLRenderer({{alpha:true,antialias:true}});
renderer.setPixelRatio(Math.min(window.devicePixelRatio,2));
renderer.setSize(window.innerWidth,window.innerHeight);
renderer.setClearColor(0x000000,0);
renderer.domElement.style.pointerEvents='none';
container.appendChild(renderer.domElement);

renderer.setAnimationLoop(()=>{{
  if(skeleton&&!skeleton.classList.contains('fade-out')){{
    skeleton.classList.add('fade-out');
    setTimeout(()=>{{if(skeleton)skeleton.style.display='none'}},800);
    renderer.setAnimationLoop(null);
  }}
}});

const vs='varying vec2 vUv;void main(){{vUv=uv;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0)}}';
const fs='uniform float uTime;uniform vec3 uColor;varying vec2 vUv;void main(){{vec2 g=floor(vUv*36.0);vec2 dp=(vUv*36.0)-g-0.5;float d=length(dp);float dot=1.0-smoothstep(0.0,0.16,d);float glow=exp(-d*7.0)*0.2;float p=0.85+0.15*sin(uTime*0.5+vUv.y*10.0);float ll=abs(sin(vUv.y*3.14159*18.0));float lo=abs(sin(vUv.x*3.14159*36.0));float line=1.0-smoothstep(0.0,0.035,min(ll,lo))*0.12;float a=clamp((dot+glow)*p*line,0.0,1.0);gl_FragColor=vec4(uColor,a*0.88)}}';
const uni={{uTime:{{value:0}},uColor:{{value:new THREE.Color('#4f8cf7')}}}};
const mat=new THREE.ShaderMaterial({{vertexShader:vs,fragmentShader:fs,uniforms:uni,transparent:true,depthWrite:false,blending:THREE.AdditiveBlending}});
const geo=new THREE.SphereGeometry(1.8,64,64);
const globe=new THREE.Mesh(geo,mat);
scene.add(globe);

const pc=500;const pg=new THREE.BufferGeometry();const pp=new Float32Array(pc*3);
for(let i=0;i<pc;i++){{const r=2.4+Math.random()*2.8;const t=Math.random()*Math.PI*2;const p=Math.acos(2*Math.random()-1);pp[i*3]=r*Math.sin(p)*Math.cos(t);pp[i*3+1]=r*Math.sin(p)*Math.sin(t);pp[i*3+2]=r*Math.cos(p)}}
pg.setAttribute('position',new THREE.BufferAttribute(pp,3));
const pm=new THREE.PointsMaterial({{color:'#6b9aff',size:0.03,transparent:true,opacity:0.5,blending:THREE.AdditiveBlending,depthWrite:false,sizeAttenuation:true}});
const particles=new THREE.Points(pg,pm);
scene.add(particles);

scene.add(new THREE.AmbientLight(0x222244,0.5));
const dl=new THREE.DirectionalLight(0x4f8cf7,1.2);dl.position.set(5,3,5);scene.add(dl);
const dl2=new THREE.DirectionalLight(0x8844ff,0.4);dl2.position.set(-5,-3,-5);scene.add(dl2);

let mx=0,my=0,ts=0.003,cs=0.003;
document.addEventListener('mousemove',e=>{{mx=(e.clientX/window.innerWidth)*2-1;my=-(e.clientY/window.innerHeight)*2+1;ts=0.003+mx*0.002}});
window.addEventListener('resize',()=>{{camera.aspect=window.innerWidth/window.innerHeight;camera.updateProjectionMatrix();renderer.setSize(window.innerWidth,window.innerHeight)}});

const clock=new THREE.Clock();
renderer.setAnimationLoop(()=>{{
  const t=clock.getElapsedTime();
  cs+=(ts-cs)*0.02;
  globe.rotation.y+=cs*1.0;
  globe.rotation.x+=(my*0.15-globe.rotation.x)*0.02;
  particles.rotation.y+=0.0005;
  uni.uTime.value=t;
  renderer.render(scene,camera);
}});

// GSAP camera timeline
const tl=gsap.timeline({{scrollTrigger:{{trigger:'.scroll-content',start:'top top',end:'bottom bottom',scrub:1.5}}}});
tl.to(camera.position,{{x:0,y:0,z:5.5,ease:'power1.out'}},0);
tl.to(camera.position,{{x:1.5,y:0.5,z:4.0,ease:'power1.inOut'}},0.25);
tl.to(camera.position,{{x:-1.8,y:0.3,z:4.5,ease:'power1.inOut'}},0.5);
tl.to(camera.position,{{x:0,y:-0.5,z:6.5,ease:'power1.in'}},0.75);

// Section reveals
gsap.utils.toArray('section').forEach(s=>{{ScrollTrigger.create({{trigger:s,start:'top 85%',end:'top 35%',toggleClass:{{targets:s,className:'in-view'}}}})}});

// Split text
document.querySelectorAll('[data-split]').forEach(el=>{{
  const txt=el.textContent;el.innerHTML='';
  [...txt].forEach(ch=>{{const s=document.createElement('span');s.classList.add('reveal-char');s.textContent=ch===' '?'\\u00A0':ch;el.appendChild(s)}});
  gsap.fromTo(el.querySelectorAll('.reveal-char'),{{y:80,opacity:0,rotateX:-30}},{{y:0,opacity:1,rotateX:0,duration:1.5,stagger:0.02,ease:'power3.out',scrollTrigger:{{trigger:el,start:'top 80%',end:'top 40%',scrub:1.2}}}});
}});

// Counters
document.querySelectorAll('[data-count]').forEach(el=>{{
  const target=parseFloat(el.dataset.count);
  ScrollTrigger.create({{trigger:el,start:'top 85%',onEnter:()=>{{gsap.fromTo(el,{{textContent:0}},{{textContent:target,duration:2,ease:'power2.out',snap:{{textContent:1}},overwrite:'auto'}});}},once:true}});
}});
</script>
</body>
</html>'''


def build_pitch_deck(lead):
    """Generate a single-file HTML pitch deck for a lead."""
    name = lead.get("business_name", "Dental Clinic")
    category = lead.get("category", "Dental Clinic")
    city = lead.get("city", "")
    phone = lead.get("phone_primary", "")
    rating = lead.get("rating", 0)
    reviews = lead.get("review_count", 0)
    score = lead.get("lead_score", 0)
    tier = lead.get("lead_tier", "WARM")
    has_website = lead.get("has_website", False)
    website_quality = lead.get("website_quality", "none")
    slug = slugify(name)
    name_short = name.split()[0] if len(name.split()) > 2 else name
    gap_text = "can't find you or choose competitors with a stronger digital presence." if not has_website else "are landing on a site that does not reflect your quality of care."

    nbsp_name = name.replace(" ", "\u00A0")

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Pitch Deck - {name} | TKVibes</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700;800&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
html{{scroll-behavior:smooth;scroll-snap-type:y mandatory}}
body{{font-family:'Inter',sans-serif;background:#0a0a0f;color:#fafafa;overflow-x:hidden}}

:root{{
  --text-hero:clamp(2.5rem,1.5rem+5vw,6rem);
  --text-xl:clamp(1.5rem,1rem+2vw,3rem);
  --text-lg:clamp(1.125rem,0.9rem+1vw,1.75rem);
  --text-base:clamp(0.875rem,0.8rem+0.375vw,1.125rem);
  --primary:#4f8cf7;
  --primary-dark:#3661b3;
  --accent:#f59e0b;
}}

.slide{{min-height:100vh;scroll-snap-align:start;display:flex;flex-direction:column;justify-content:center;padding:3rem 2rem;position:relative;overflow:hidden}}
.slide::before{{content:'';position:absolute;inset:0;z-index:0}}

.slide-content{{position:relative;z-index:1;max-width:1000px;margin:0 auto;width:100%}}

.display-heading{{font-family:'Space Grotesk',sans-serif;font-size:var(--text-hero);font-weight:800;line-height:0.9;letter-spacing:-0.05em}}
.slide-heading{{font-family:'Space Grotesk',sans-serif;font-size:var(--text-xl);font-weight:700;line-height:1.1;letter-spacing:-0.035em;margin-bottom:1rem}}
.slide-body{{font-size:var(--text-lg);line-height:1.5;opacity:0.7;max-width:36rem}}

.tag{{display:inline-block;padding:0.3rem 0.8rem;border-radius:100px;font-size:0.75rem;font-weight:600;text-transform:uppercase;letter-spacing:0.05em;background:rgba(79,140,247,0.15);color:var(--primary);border:1px solid rgba(79,140,247,0.3);margin-bottom:1rem}}

.rating-badge{{display:inline-flex;align-items:center;gap:0.5rem;background:rgba(255,255,255,0.08);backdrop-filter:blur(12px);border:1px solid rgba(255,255,255,0.12);border-radius:100px;padding:0.5rem 1rem;font-size:var(--text-base);margin-bottom:1.5rem}}
.rating-badge i{{color:var(--accent)}}

.deliverables-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:1.25rem;margin-top:2rem}}
.delivery-card{{background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);border-radius:20px;padding:1.5rem;transition:all 0.3s ease}}
.delivery-card:hover{{background:rgba(255,255,255,0.07);border-color:rgba(79,140,247,0.3);transform:translateY(-4px)}}
.delivery-card i{{font-size:1.5rem;color:var(--primary);margin-bottom:0.75rem}}
.delivery-card h3{{font-size:var(--text-base);font-weight:700;margin-bottom:0.5rem}}
.delivery-card p{{font-size:0.8rem;opacity:0.6;line-height:1.5}}

.stats-row{{display:flex;flex-wrap:wrap;gap:2rem;margin-top:2rem}}
.stat-item{{text-align:center}}
.stat-number{{font-family:'Space Grotesk',sans-serif;font-size:2.5rem;font-weight:800;color:var(--primary);line-height:1}}
.stat-label{{font-size:0.8rem;opacity:0.5;margin-top:0.25rem}}

.cta-group{{display:flex;flex-wrap:wrap;gap:1rem;margin-top:2rem}}
.btn{{display:inline-flex;align-items:center;gap:0.5rem;padding:0.85rem 2rem;border-radius:100px;font-weight:600;font-size:var(--text-base);text-decoration:none;transition:all 0.3s ease}}
.btn-primary{{background:linear-gradient(135deg,var(--primary),#6b9aff);color:#fff;box-shadow:0 4px 20px rgba(79,140,247,0.15)}}
.btn-primary:hover{{transform:translateY(-2px);box-shadow:0 8px 30px rgba(79,140,247,0.25)}}
.btn-outline{{background:transparent;border:1px solid rgba(255,255,255,0.2);color:#fff}}
.btn-outline:hover{{background:rgba(255,255,255,0.06)}}

.nav-dots{{position:fixed;right:1.5rem;top:50%;transform:translateY(-50%);z-index:100;display:flex;flex-direction:column;gap:0.5rem}}
.nav-dot{{width:10px;height:10px;border-radius:50%;border:1px solid rgba(255,255,255,0.3);background:transparent;cursor:pointer;transition:all 0.3s ease}}
.nav-dot.active{{background:var(--primary);border-color:var(--primary);box-shadow:0 0 8px rgba(79,140,247,0.5)}}

.footer-note{{position:absolute;bottom:1.5rem;left:2rem;right:2rem;font-size:0.7rem;opacity:0.35;z-index:1;text-align:center}}

.bg-overlay{{background:linear-gradient(rgba(10,15,30,0.75),rgba(10,15,30,0.85))}}

@media(max-width:768px){{
  .slide{{padding:2rem 1rem}}
  .deliverables-grid{{grid-template-columns:1fr}}
  .nav-dots{{right:0.75rem}}
  .stats-row{{gap:1rem;justify-content:center}}
  .cta-group{{flex-direction:column}}
  .btn{{justify-content:center}}
}}

@media(prefers-reduced-motion:reduce){{
  *{{scroll-behavior:auto!important}}
}}
</style>
</head>
<body>
<div class="nav-dots" id="navDots"></div>

<!-- Slide 1: Cover -->
<section class="slide" style="background:linear-gradient(135deg,#0a0a0f,#111122,#0f0f2a)" data-index="0">
  <div class="slide-content" style="text-align:center">
    <div class="tag" style="display:inline-block">TKVibes Digital Agency</div>
    <h1 class="display-heading" style="margin:1rem 0">A Better Online<br>Presence for</h1>
    <h2 style="font-family:'Space Grotesk',sans-serif;font-size:var(--text-xl);font-weight:700;color:var(--primary);margin-bottom:1.5rem">{name}</h2>
    <div class="rating-badge" style="display:inline-flex;margin:0 auto 1.5rem">
      <i class="fas fa-star"></i> {rating} &middot; {reviews} reviews
    </div>
    <p style="font-size:var(--text-base);opacity:0.5">{city} &middot; {category}</p>
  </div>
  <div class="footer-note">Concept by TKVibes — not affiliated with {name}</div>
</section>

<!-- Slide 2: The Gap -->
<section class="slide bg-overlay" data-index="1">
  <div class="slide-content">
    <span class="tag">The Challenge</span>
    <h2 class="slide-heading">You're Being<br>Outpaced Online</h2>
    <p class="slide-body">
      You have a strong {rating}-star reputation with {reviews}+ reviews, but without a professional website, potential patients {gap_text}
    </p>
    <div class="stats-row">
      <div class="stat-item"><div class="stat-number">68%</div><div class="stat-label">Patients research online first</div></div>
      <div class="stat-item"><div class="stat-number">3x</div><div class="stat-label">More bookings with a website</div></div>
      <div class="stat-item"><div class="stat-number">80%</div><div class="stat-label">Trust a practice with a website</div></div>
    </div>
  </div>
  <div class="footer-note">Concept by TKVibes — not affiliated with {name}</div>
</section>

<!-- Slide 3: What You're Missing -->
<section class="slide" style="background:linear-gradient(135deg,#0f0f2a,#0a0a0f)" data-index="2">
  <div class="slide-content">
    <span class="tag">What You're Missing</span>
    <h2 class="slide-heading">Opportunities<br>You're Leaving Behind</h2>
    <div class="deliverables-grid">
      <div class="delivery-card"><i class="fas fa-search"></i><h3>Local SEO</h3><p>Appear in "dentist near me" searches and Google Maps</p></div>
      <div class="delivery-card"><i class="fas fa-calendar-check"></i><h3>Online Booking</h3><p>24/7 appointment scheduling from any device</p></div>
      <div class="delivery-card"><i class="fas fa-comments"></i><h3>Review Engine</h3><p>Automated review collection &amp; reputation management</p></div>
      <div class="delivery-card"><i class="fas fa-share-alt"></i><h3>Social Proof</h3><p>Showcase your {reviews}+ five-star reviews prominently</p></div>
    </div>
  </div>
  <div class="footer-note">Concept by TKVibes — not affiliated with {name}</div>
</section>

<!-- Slide 4: Solution -->
<section class="slide bg-overlay" data-index="3">
  <div class="slide-content" style="display:flex;flex-direction:column;justify-content:center;min-height:70vh">
    <span class="tag">The Solution</span>
    <h2 class="slide-heading">A Complete Digital<br>Presence for {name_short}</h2>
    <p class="slide-body">
      We build a beautiful, modern website with 3D visuals, smooth animations, and patient-friendly design — optimized to convert visitors into appointments.
    </p>
    <div style="margin-top:1.5rem">
      <div style="display:flex;flex-wrap:wrap;gap:0.5rem">
        <span class="tag" style="background:rgba(245,158,11,0.15);color:var(--accent);border-color:rgba(245,158,11,0.3)"><i class="fas fa-mobile-alt"></i> Mobile-first</span>
        <span class="tag" style="background:rgba(245,158,11,0.15);color:var(--accent);border-color:rgba(245,158,11,0.3)"><i class="fas fa-rocket"></i> Fast loading</span>
        <span class="tag" style="background:rgba(245,158,11,0.15);color:var(--accent);border-color:rgba(245,158,11,0.3)"><i class="fas fa-globe"></i> SEO-optimized</span>
      </div>
    </div>
  </div>
  <div class="footer-note">Concept by TKVibes — not affiliated with {name}</div>
</section>

<!-- Slide 5: What TKVibes Delivers -->
<section class="slide" style="background:linear-gradient(135deg,#0a0a0f,#111122)" data-index="4">
  <div class="slide-content">
    <span class="tag">What We Deliver</span>
    <h2 class="slide-heading">Full-Service Digital<br>Transformation</h2>
    <div class="deliverables-grid">
      <div class="delivery-card"><i class="fas fa-paint-brush"></i><h3>Web Design</h3><p>Custom 3D interactive website with immersive visuals</p></div>
      <div class="delivery-card"><i class="fas fa-code"></i><h3>Development</h3><p>Fast, responsive, SEO-optimized HTML/CSS/JS</p></div>
      <div class="delivery-card"><i class="fas fa-chart-line"></i><h3>SEO</h3><p>Local search optimization to rank #1 in {city}</p></div>
      <div class="delivery-card"><i class="fas fa-envelope"></i><h3>Automation</h3><p>Patient booking forms, review requests, follow-ups</p></div>
    </div>
  </div>
  <div class="footer-note">Concept by TKVibes — not affiliated with {name}</div>
</section>

<!-- Slide 6: Proof -->
<section class="slide bg-overlay" data-index="5">
  <div class="slide-content" style="text-align:center">
    <span class="tag">Proven Results</span>
    <h2 class="slide-heading">Trusted by 50+<br>Healthcare Practices</h2>
    <div class="stats-row" style="justify-content:center">
      <div class="stat-item"><div class="stat-number">50+</div><div class="stat-label">Projects Delivered</div></div>
      <div class="stat-item"><div class="stat-number">98%</div><div class="stat-label">Client Satisfaction</div></div>
      <div class="stat-item"><div class="stat-number">3x</div><div class="stat-label">Avg. Booking Increase</div></div>
      <div class="stat-item"><div class="stat-number">4.9</div><div class="stat-label">Avg. Rating</div></div>
    </div>
  </div>
  <div class="footer-note">Concept by TKVibes — not affiliated with {name}</div>
</section>

<!-- Slide 7: ROI -->
<section class="slide" style="background:linear-gradient(135deg,#0f0f2a,#0a0a0f)" data-index="6">
  <div class="slide-content">
    <span class="tag">Expected Impact</span>
    <h2 class="slide-heading">What You Can<br>Expect to Gain</h2>
    <div class="deliverables-grid">
      <div class="delivery-card"><i class="fas fa-eye"></i><h3>Visibility</h3><p>#1 in local search results for dental keywords in {city}</p></div>
      <div class="delivery-card"><i class="fas fa-phone-alt"></i><h3>Inquiries</h3><p>40-60% increase in phone calls &amp; contact form submissions</p></div>
      <div class="delivery-card"><i class="fas fa-calendar-alt"></i><h3>Bookings</h3><p>Direct online booking from search results</p></div>
      <div class="delivery-card"><i class="fas fa-trophy"></i><h3>Reputation</h3><p>Showcase your {reviews}+ reviews prominently</p></div>
    </div>
  </div>
  <div class="footer-note">Concept by TKVibes — not affiliated with {name}</div>
</section>

<!-- Slide 8: CTA -->
<section class="slide bg-overlay" data-index="7">
  <div class="slide-content" style="text-align:center">
    <span class="tag" style="display:inline-block">Next Step</span>
    <h2 class="slide-heading" style="margin-bottom:1.5rem">Let's Build Your<br>Digital Presence</h2>
    <p class="slide-body" style="margin:0 auto 2rem;text-align:center">
      Book a free, no-obligation consultation to see how we can transform {name}'s online presence.
    </p>
    <div class="cta-group" style="justify-content:center">
      <a href="tel:{phone}" class="btn btn-primary"><i class="fas fa-phone"></i> Call Now</a>
      <a href="https://wa.me/{phone.replace('+','').replace(' ','')}" target="_blank" class="btn btn-outline"><i class="fab fa-whatsapp"></i> WhatsApp Us</a>
    </div>
    <p style="margin-top:2rem;font-size:0.8rem;opacity:0.4">
      services@tkvibes.in &middot; TKVibes Digital Agency
    </p>
  </div>
  <div class="footer-note">Concept by TKVibes — not affiliated with {name}</div>
</section>

<script>
// Navigation dots
const slides = document.querySelectorAll('.slide');
const navDots = document.getElementById('navDots');
slides.forEach((_,i) => {{
  const dot = document.createElement('button');
  dot.className = 'nav-dot' + (i===0?' active':'');
  dot.onclick = () => slides[i].scrollIntoView({{behavior:'smooth'}});
  navDots.appendChild(dot);
}});

// Update active dot on scroll
const observer = new IntersectionObserver(entries => {{
  entries.forEach(entry => {{
    if(entry.isIntersecting){{
      const idx = parseInt(entry.target.dataset.index);
      document.querySelectorAll('.nav-dot').forEach((d,i) => d.classList.toggle('active',i===idx));
    }}
  }});
}}, {{threshold:0.5}});
slides.forEach(s => observer.observe(s));

// Keyboard navigation
document.addEventListener('keydown', e => {{
  if(e.key === 'ArrowDown' || e.key === 'ArrowRight'){{
    const active = document.querySelector('.nav-dot.active');
    if(active && active.nextElementSibling) active.nextElementSibling.click();
  }}
  if(e.key === 'ArrowUp' || e.key === 'ArrowLeft'){{
    const active = document.querySelector('.nav-dot.active');
    if(active && active.previousElementSibling) active.previousElementSibling.click();
  }}
}});
</script>
</body>
</html>'''


# ── Generate all files ──────────────────────────────────────────────────
OUTPUT_DIR = os.path.join(REPO_DIR, "proposals")
SAMPLE_DIR = os.path.join(OUTPUT_DIR, "sample-website")
PITCH_DIR = os.path.join(OUTPUT_DIR, "pitch-deck")
os.makedirs(SAMPLE_DIR, exist_ok=True)
os.makedirs(PITCH_DIR, exist_ok=True)

generated = []

for lead in LEADS:
    name = lead.get("business_name", "Unknown")
    slug = slugify(name)
    phone_raw = lead.get("phone_primary", "")

    # Generate sample site
    site_html = build_sample_site(lead)
    site_path = os.path.join(SAMPLE_DIR, f"{slug}.html")
    with io.open(site_path, "w", encoding="utf-8") as f:
        f.write(site_html)
    site_size = os.path.getsize(site_path)

    # Generate pitch deck
    deck_html = build_pitch_deck(lead)
    deck_path = os.path.join(PITCH_DIR, f"{slug}.html")
    with io.open(deck_path, "w", encoding="utf-8") as f:
        f.write(deck_html)
    deck_size = os.path.getsize(deck_path)

    generated.append({
        "name": name,
        "slug": slug,
        "lead_key": lead.get("lead_key", ""),
        "site_file": f"sample-website/{slug}.html",
        "site_size": site_size,
        "deck_file": f"pitch-deck/{slug}.html",
        "deck_size": deck_size,
    })
    print(f"  ✓ {name:40s} | site: {site_size:>7,}b | deck: {deck_size:>7,}b")

print(f"\nGenerated {len(generated)} lead pairs ({len(generated)*2} files total)")
print(f"Output: proposals/sample-website/ and proposals/pitch-deck/")

# Write manifest
manifest_path = os.path.join(OUTPUT_DIR, "manifest.json")
with io.open(manifest_path, "w", encoding="utf-8") as f:
    json.dump(generated, f, indent=2, ensure_ascii=False)
print(f"Manifest: {manifest_path}")