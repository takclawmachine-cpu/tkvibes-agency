#!/usr/bin/env python3
"""Bulk-add Unsplash stock images to ALL sections of sample webpages & pitch decks."""
import os, re

BASE = r"C:\Users\takcl\Desktop\tkvibes-agency\Sample Webpages and pitch deck"

# --- MEDICAL/DENTAL IMAGE POOLS (Unsplash direct) ---
HERO = [
    "https://images.unsplash.com/photo-1631217868264-e5b90bb7e133?w=800&q=80",
    "https://images.unsplash.com/photo-1629909613654-28e377c37b09?w=800&q=80",
    "https://images.unsplash.com/photo-1588776814546-1ffcf47267a5?w=800&q=80",
    "https://images.unsplash.com/photo-1606811971618-4486d14f3f99?w=800&q=80",
    "https://images.unsplash.com/photo-1551076805-e1869033e561?w=800&q=80",
]
ABOUT = [
    "https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?w=800&q=80",
    "https://images.unsplash.com/photo-1551601651-2a8555f1a136?w=800&q=80",
    "https://images.unsplash.com/photo-1581595220892-b0739db3ba8c?w=800&q=80",
    "https://images.unsplash.com/photo-1579684385127-1ef15d508118?w=800&q=80",
    "https://images.unsplash.com/photo-1559839734-2b71ea197ec2?w=800&q=80",
]
CTA_BG = [
    "https://images.unsplash.com/photo-1551076805-e1869033e561?w=1200&q=80",
    "https://images.unsplash.com/photo-1588776814546-1ffcf47267a5?w=1200&q=80",
    "https://images.unsplash.com/photo-1631217868264-e5b90bb7e133?w=1200&q=80",
    "https://images.unsplash.com/photo-1629909613654-28e377c37b09?w=1200&q=80",
    "https://images.unsplash.com/photo-1579684385127-1ef15d508118?w=1200&q=80",
]
TESTIMONIAL_FACES = [
    "https://images.unsplash.com/photo-1580489944761-15a19d654956?w=100&q=80",  # woman
    "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&q=80",  # man
    "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=100&q=80",  # woman
    "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=100&q=80",  # man
    "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=100&q=80",  # woman
]
SERVICE_BG = [
    "https://images.unsplash.com/photo-1588776814546-1ffcf47267a5?w=600&q=80",
    "https://images.unsplash.com/photo-1606811971618-4486d14f3f99?w=600&q=80",
    "https://images.unsplash.com/photo-1631217868264-e5b90bb7e133?w=600&q=80",
    "https://images.unsplash.com/photo-1551076805-e1869033e561?w=600&q=80",
    "https://images.unsplash.com/photo-1629909613654-28e377c37b09?w=600&q=80",
]
WHY_US_BG = [
    "https://images.unsplash.com/photo-1579684385127-1ef15d508118?w=600&q=80",
    "https://images.unsplash.com/photo-1559839734-2b71ea197ec2?w=600&q=80",
    "https://images.unsplash.com/photo-1581595220892-b0739db3ba8c?w=600&q=80",
    "https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?w=600&q=80",
    "https://images.unsplash.com/photo-1551076805-e1869033e561?w=600&q=80",
]
COMPETITOR_BG = [
    "https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?w=800&q=80",
    "https://images.unsplash.com/photo-1516549655169-df83a0774514?w=800&q=80",
    "https://images.unsplash.com/photo-1556155092-490a1ba16284?w=800&q=80",
    "https://images.unsplash.com/photo-1579684385127-1ef15d508118?w=800&q=80",
    "https://images.unsplash.com/photo-1551076805-e1869033e561?w=800&q=80",
]

def pick(pool, idx):
    return pool[idx % len(pool)]

def add_sample_images(filepath, idx):
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    changes = []
    original = html

    # 1. Add CTA section background image
    cta_img = pick(CTA_BG, idx)
    # Find CTA glass section and add a subtle background image behind it
    cta_pattern = r'(<section class="section">\s*<div class="container">\s*<div class="glass-strong fade-up" style="padding:40px;text-align:center;)'
    cta_replacement = r'<section class="section" style="background:linear-gradient(rgba(10,15,30,0.6),rgba(10,15,30,0.6)),url(' + cta_img + r') center/cover no-repeat;background-attachment:fixed">\1'
    if re.search(cta_pattern, html):
        html = re.sub(cta_pattern, cta_replacement, html, count=1)
        changes.append("CTA bg")

    # 2. Replace testimonial avatar initials with real face photos
    face1, face2, face3 = pick(TESTIMONIAL_FACES, idx), pick(TESTIMONIAL_FACES, idx+1), pick(TESTIMONIAL_FACES, idx+2)
    # Pattern for testemonial avatars: <div style="width:36px;height:36px;border-radius:50%;background:linear-gradient(...);display:flex...">INITIAL</div>
    # Replace all such avatar divs in testimonials section with <img> tags
    # First avatar
    avatar_pattern = r'(<div style="width:36px;height:36px;border-radius:50%;background:linear-gradient\(135deg,#[a-f0-9]+,#[a-f0-9]+\);display:flex;align-items:center;justify-content:center;font-weight:700;font-size:14px;color:#fff">)([A-Z])(</div>)'
    avatars = list(re.finditer(avatar_pattern, html))
    if avatars:
        # Replace each avatar with a circular image
        for i, match in enumerate(avatars):
            face = face1 if i == 0 else (face2 if i == 1 else face3)
            old = match.group(0)
            new = f'<img src="{face}" alt="Patient" style="width:36px;height:36px;border-radius:50%;object-fit:cover">'
            html = html.replace(old, new, 1)
        changes.append(f"{len(avatars)} testimonial faces")

    # 3. Add background images to service cards - add subtle image above each service card
    # Actually let's add image backgrounds behind the services section
    services_section_pattern = r'(<section id="services" class="section">\s*<div class="container">)'
    services_bg = pick(SERVICE_BG, idx)
    services_replacement = r'<section id="services" class="section" style="background:linear-gradient(rgba(10,15,30,0.85),rgba(10,15,30,0.85)),url(' + services_bg + r') center/cover no-repeat;background-attachment:fixed">\1'
    if re.search(services_section_pattern, html):
        html = re.sub(services_section_pattern, services_replacement, html, count=1)
        changes.append("Services bg")

    # 4. Add background image to Why Us section
    whyus_pattern = r'(<section id="why-us" class="section">\s*<div class="container">)'
    whyus_bg = pick(WHY_US_BG, idx)
    whyus_replacement = r'<section id="why-us" class="section" style="background:linear-gradient(rgba(10,15,30,0.9),rgba(10,15,30,0.9)),url(' + whyus_bg + r') center/cover no-repeat;background-attachment:fixed">\1'
    if re.search(whyus_pattern, html):
        html = re.sub(whyus_pattern, whyus_replacement, html, count=1)
        changes.append("Why Us bg")

    # 5. Add background image to Competitor Gap section (the one with red warning)
    comp_pattern = r'(<section class="section" style="background:rgba\(239,68,68,0\.03\)">\s*<div class="container">)'
    comp_bg = pick(COMPETITOR_BG, idx)
    comp_replacement = r'<section class="section" style="background:linear-gradient(rgba(10,15,30,0.88),rgba(10,15,30,0.88)),url(' + comp_bg + r') center/cover no-repeat;background-attachment:fixed">\1'
    if re.search(comp_pattern, html):
        html = re.sub(comp_pattern, comp_replacement, html, count=1)
        changes.append("Competitor gap bg")

    # 6. Add a background image to the hero section behind everything
    hero_pattern = r'(<section class="hero-section" id="hero" style="padding:100px 0 60px;position:relative">)'
    hero_bg = pick(HERO, idx)
    hero_replacement = r'<section class="hero-section" id="hero" style="padding:100px 0 60px;position:relative;background:linear-gradient(rgba(10,15,30,0.7),rgba(10,15,30,0.8)),url(' + hero_bg + r') center/cover no-repeat">'
    if re.search(hero_pattern, html):
        html = re.sub(hero_pattern, hero_replacement, html, count=1)
        changes.append("Hero section bg")

    if html != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"  => {' | '.join(changes)}")
    else:
        print(f"  => No changes")


# --- PITCH DECK ---
PITCH_HERO = [
    "https://images.unsplash.com/photo-1551076805-e1869033e561?w=1200&q=80",
    "https://images.unsplash.com/photo-1588776814546-1ffcf47267a5?w=1200&q=80",
    "https://images.unsplash.com/photo-1631217868264-e5b90bb7e133?w=1200&q=80",
    "https://images.unsplash.com/photo-1629909613654-28e377c37b09?w=1200&q=80",
    "https://images.unsplash.com/photo-1606811971618-4486d14f3f99?w=1200&q=80",
]
PITCH_SOLUTION = [
    "https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?w=800&q=80",
    "https://images.unsplash.com/photo-1516549655169-df83a0774514?w=800&q=80",
    "https://images.unsplash.com/photo-1556155092-490a1ba16284?w=800&q=80",
    "https://images.unsplash.com/photo-1551076805-e1869033e561?w=800&q=80",
    "https://images.unsplash.com/photo-1579684385127-1ef15d508118?w=800&q=80",
]
PITCH_PROBLEM = [
    "https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?w=800&q=80",
    "https://images.unsplash.com/photo-1516549655169-df83a0774514?w=800&q=80",
    "https://images.unsplash.com/photo-1556155092-490a1ba16284?w=800&q=80",
    "https://images.unsplash.com/photo-1551076805-e1869033e561?w=800&q=80",
    "https://images.unsplash.com/photo-1579684385127-1ef15d508118?w=800&q=80",
]
PITCH_FEATURES = [
    "https://images.unsplash.com/photo-1551076805-e1869033e561?w=800&q=80",
    "https://images.unsplash.com/photo-1631217868264-e5b90bb7e133?w=800&q=80",
    "https://images.unsplash.com/photo-1629909613654-28e377c37b09?w=800&q=80",
    "https://images.unsplash.com/photo-1588776814546-1ffcf47267a5?w=800&q=80",
    "https://images.unsplash.com/photo-1606811971618-4486d14f3f99?w=800&q=80",
]
PITCH_CTA = [
    "https://images.unsplash.com/photo-1551076805-e1869033e561?w=1200&q=80",
    "https://images.unsplash.com/photo-1631217868264-e5b90bb7e133?w=1200&q=80",
    "https://images.unsplash.com/photo-1588776814546-1ffcf47267a5?w=1200&q=80",
    "https://images.unsplash.com/photo-1629909613654-28e377c37b09?w=1200&q=80",
    "https://images.unsplash.com/photo-1579684385127-1ef15d508118?w=1200&q=80",
]
PITCH_ROI = [
    "https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?w=800&q=80",
    "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800&q=80",
    "https://images.unsplash.com/photo-1616077168070-5cb5f5f0b3b2?w=800&q=80",
    "https://images.unsplash.com/photo-1551076805-e1869033e561?w=800&q=80",
    "https://images.unsplash.com/photo-1579684385127-1ef15d508118?w=800&q=80",
]

def add_pitch_images(filepath, idx):
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    changes = []
    original = html

    # 1: Add background to "The Problem" slide (ef4444 - red themed)
    prob_img = pick(PITCH_PROBLEM, idx)
    prob_pattern = r'(<div class="slide" style="background:radial-gradient\(ellipse at 50% 50%,#ef444410 0%,transparent 60%\),#0f172a">\s*<div style="max-width:700px;text-align:center">\s*<h2 class="anim-fade-up d1")'
    if re.search(prob_pattern, html):
        new_style = f'style="background:linear-gradient(rgba(15,23,42,0.8),rgba(15,23,42,0.8)),url({prob_img}) center/cover no-repeat,#0f172a"'
        html = re.sub(prob_pattern, r'<div class="slide" style="' + new_style + r'"><div style="max-width:700px;text-align:center"><h2 class="anim-fade-up d1"', html, count=1)
        changes.append("Problem slide bg")

    # 2: Add background to "The Solution" slide (green themed)
    sol_img = pick(PITCH_SOLUTION, idx)
    sol_pattern = r'(<div class="slide" style="background:radial-gradient\(ellipse at 50% 50%,#22c55e10 0%,transparent 60%\),#0f172a">\s*<div style="max-width:800px;text-align:center">\s*<h2 class="anim-fade-up d1" style="font-family:\'Poppins\',sans-serif;font-size:2.2rem;font-weight:700;margin-bottom:2rem">The Solution)'
    sol_alt_pattern = r'(<div class="slide" style="background:radial-gradient\(ellipse at 50% 50%,#22c55e10 0%,transparent 60%\),#0f172a">\s*<div style="max-width:800px;text-align:center">\s*<h2 class="anim-fade-up d1" style="font-family:\'Poppins\',sans-serif;font-size:2.2rem;font-weight:700;margin-bottom:2rem">The Solution)'
    if re.search(sol_pattern, html) or re.search(sol_alt_pattern, html):
        pattern = sol_pattern if re.search(sol_pattern, html) else sol_alt_pattern
        new_style = f'style="background:linear-gradient(rgba(15,23,42,0.75),rgba(15,23,42,0.75)),url({sol_img}) center/cover no-repeat,#0f172a"'
        html = re.sub(pattern, r'<div class="slide" style="' + new_style + r'"><div style="max-width:800px;text-align:center"><h2 class="anim-fade-up d1" style="font-family:\'Poppins\',sans-serif;font-size:2.2rem;font-weight:700;margin-bottom:2rem">The Solution', html, count=1)
        changes.append("Solution slide bg")

    # 3: Add background to "What TKVibes Delivers" / features slide
    feat_img = pick(PITCH_FEATURES, idx)
    feat_pattern1 = r'(<div class="slide" style="background:radial-gradient\(ellipse at 50% 50%,#0ea5e910 0%,transparent 60%\),#0f172a">\s*<div style="max-width:800px;text-align:center">\s*<h2 class="anim-fade-up d1" style="font-family:\'Poppins\',sans-serif;font-size:2.2rem;font-weight:700;margin-bottom:2rem">What TKVibes Delivers)'
    feat_pattern2 = r'(<div class="slide" style="background:radial-gradient\(ellipse at 50% 50%,#22c55e10 0%,transparent 60%\),#0f172a">\s*<div style="max-width:800px;text-align:center">\s*<h2 class="anim-fade-up d1" style="font-family:\'Poppins\',sans-serif;font-size:2.2rem;font-weight:700;margin-bottom:2rem">What TKVibes Delivers)'
    feat_p = feat_pattern1 if re.search(feat_pattern1, html) else (feat_pattern2 if re.search(feat_pattern2, html) else None)
    if feat_p:
        new_style = f'style="background:linear-gradient(rgba(15,23,42,0.78),rgba(15,23,42,0.78)),url({feat_img}) center/cover no-repeat,#0f172a"'
        html = re.sub(feat_p, r'<div class="slide" style="' + new_style + r'"><div style="max-width:800px;text-align:center"><h2 class="anim-fade-up d1" style="font-family:\'Poppins\',sans-serif;font-size:2.2rem;font-weight:700;margin-bottom:2rem">What TKVibes Delivers', html, count=1)
        changes.append("Features slide bg")

    # 4: Add background to ROI/Expected Impact slide
    roi_img = pick(PITCH_ROI, idx)
    roi_patterns = [
        r'(<div class="slide" style="background:radial-gradient\(ellipse at 50% 50%,#22c55e10 0%,transparent 60%\),#0f172a">\s*<div style="max-width:700px;text-align:center">\s*<h2 class="anim-fade-up d1" style="font-family:\'Poppins\',sans-serif;font-size:2.2rem;font-weight:700;margin-bottom:1rem">Expected Impact)',
        r'(<div class="slide" style="background:radial-gradient\(ellipse at 50% 50%,#22c55e10 0%,transparent 60%\),#0f172a">\s*<div style="max-width:700px;text-align:center">\s*<h2 class="anim-fade-up d1" style="font-family:\'Poppins\',sans-serif;font-size:2.2rem;font-weight:700;margin-bottom:1rem">Expected Impact)',
    ]
    for rp in roi_patterns:
        if re.search(rp, html):
            new_style = f'style="background:linear-gradient(rgba(15,23,42,0.75),rgba(15,23,42,0.75)),url({roi_img}) center/cover no-repeat,#0f172a"'
            html = re.sub(rp, r'<div class="slide" style="' + new_style + r'"><div style="max-width:700px;text-align:center"><h2 class="anim-fade-up d1" style="font-family:\'Poppins\',sans-serif;font-size:2.2rem;font-weight:700;margin-bottom:1rem">Expected Impact', html, count=1)
            changes.append("ROI slide bg")
            break

    # 5: Add background to CTA / "Let's Build" slide
    cta_img = pick(PITCH_CTA, idx)
    cta_patterns = [
        r'(<div class="slide" style="background:radial-gradient\(ellipse at 50% 50%,#0ea5e915 0%,transparent 60%\),#0f172a">\s*<div style="max-width:600px;text-align:center">\s*<div class="anim-fade-up d1" style="width:80px;height:80px;border-radius:24px;background:linear-gradient\(135deg,#0ea5e9,#38bdf8\))',
        r'(<div class="slide" style="background:radial-gradient\(ellipse at 50% 50%,#22c55e15 0%,transparent 60%\),#0f172a">\s*<div style="max-width:600px;text-align:center">\s*<div class="anim-fade-up d1" style="width:80px;height:80px;border-radius:24px;background:linear-gradient\(135deg,#22c55e,#4ade80\))',
    ]
    for cp in cta_patterns:
        if re.search(cp, html):
            new_style = f'style="background:linear-gradient(rgba(15,23,42,0.7),rgba(15,23,42,0.7)),url({cta_img}) center/cover no-repeat,#0f172a"'
            html = re.sub(cp, r'<div class="slide" style="' + new_style + r'"><div style="max-width:600px;text-align:center"><div class="anim-fade-up d1" style="width:80px;height:80px;border-radius:24px;background:linear-gradient(135deg,#0ea5e9,#38bdf8)', html, count=1)
            changes.append("CTA slide bg")
            break

    # 6: Add background to "Your Competitors" slide (problem/gap)
    comp_img = pick(PITCH_PROBLEM, idx+1)
    comp_pattern1 = r'(<div class="slide" style="background:radial-gradient\(ellipse at 70% 30%,#0ea5e910 0%,transparent 60%\),#0f172a">\s*<div style="max-width:800px;width:100%">\s*<h2 class="anim-fade-up d1" style="font-family:\'Poppins\',sans-serif;font-size:2.2rem;font-weight:700;margin-bottom)'
    comp_pattern2 = r'(<div class="slide" style="background:radial-gradient\(ellipse at 70% 30%,#22c55e10 0%,transparent 60%\),#0f172a">\s*<div style="max-width:800px;width:100%">\s*<h2 class="anim-fade-up d1" style="font-family:\'Poppins\',sans-serif;font-size:2.2rem;font-weight:700;margin-bottom)'
    for cp in [comp_pattern1, comp_pattern2]:
        if re.search(cp, html):
            new_style = f'style="background:linear-gradient(rgba(15,23,42,0.82),rgba(15,23,42,0.82)),url({comp_img}) center/cover no-repeat,#0f172a"'
            html = re.sub(cp, r'<div class="slide" style="' + new_style + r'"><div style="max-width:800px;width:100%"><h2 class="anim-fade-up d1" style="font-family:\'Poppins\',sans-serif;font-size:2.2rem;font-weight:700;margin-bottom', html, count=1)
            changes.append("Competitor slide bg")
            break

    # 7: Add background to "What You're Missing" slide 
    missing_img = pick(PITCH_PROBLEM, idx+2)
    missing_pattern = r'(<div class="slide" style="background:radial-gradient\(ellipse at 50% 50%,#ef444410 0%,transparent 60%\),#0f172a">\s*<div style="max-width:700px;text-align:center">\s*<h2 class="anim-fade-up d1" style="font-family:\'Poppins\',sans-serif;font-size:2.2rem;font-weight:700;margin-bottom:2rem">What You)'
    if re.search(missing_pattern, html):
        missing_style = f'style="background:linear-gradient(rgba(15,23,42,0.78),rgba(15,23,42,0.78)),url({missing_img}) center/cover no-repeat,#0f172a"'
        html = re.sub(missing_pattern, r'<div class="slide" style="' + missing_style + r'"><div style="max-width:700px;text-align:center"><h2 class="anim-fade-up d1" style="font-family:\'Poppins\',sans-serif;font-size:2.2rem;font-weight:700;margin-bottom:2rem">What You', html, count=1)
        changes.append("Missing slide bg")

    if html != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"  => {' | '.join(changes)}")
    else:
        print(f"  => No changes")

# Also add images to sample website's second variant files
def main():
    sample_dir = os.path.join(BASE, "sample website")
    pitch_dir = os.path.join(BASE, "pitch deck")

    print("=== SAMPLE WEBSITES ===")
    files = sorted(os.listdir(sample_dir))
    for i, fname in enumerate(files):
        if not fname.endswith('.html'): continue
        fpath = os.path.join(sample_dir, fname)
        print(f"[{i+1}] {fname}")
        add_sample_images(fpath, i)

    print()
    print("=== PITCH DECKS ===")
    files = sorted(os.listdir(pitch_dir))
    for i, fname in enumerate(files):
        if not fname.endswith('.html'): continue
        fpath = os.path.join(pitch_dir, fname)
        print(f"[{i+1}] {fname}")
        add_pitch_images(fpath, i)

    print("\nDone!")

if __name__ == "__main__":
    main()