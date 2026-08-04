#!/usr/bin/env python3
"""Add Unsplash stock images to all sample websites and pitch decks."""

import os
import re
import time

BASE = r"C:\Users\takcl\Desktop\tkvibes-agency\Sample Webpages and pitch deck"

# Unsplash stock images relevant to medical/dental clinics
# Using direct image URLs (with w=800 for reasonable size)
IMAGES = {
    "hero": [
        "https://images.unsplash.com/photo-1631217868264-e5b90bb7e133?w=800&q=80",  # dental clinic interior
        "https://images.unsplash.com/photo-1629909613654-28e377c37b09?w=800&q=80",  # modern clinic
        "https://images.unsplash.com/photo-1588776814546-1ffcf47267a5?w=800&q=80",  # dentist tools
        "https://images.unsplash.com/photo-1606811971618-4486d14f3f99?w=800&q=80",  # dentist patient
        "https://images.unsplash.com/photo-1551076805-e1869033e561?w=800&q=80",  # doctor patient
    ],
    "about": [
        "https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?w=800&q=80",  # hospital corridor
        "https://images.unsplash.com/photo-1551601651-2a8555f1a136?w=800&q=80",  # dental exam
        "https://images.unsplash.com/photo-1581595220892-b0739db3ba8c?w=800&q=80",  # doctor consultation
        "https://images.unsplash.com/photo-1579684385127-1ef15d508118?w=800&q=80",  # clinic reception
        "https://images.unsplash.com/photo-1559839734-2b71ea197ec2?w=800&q=80",  # surgery room
    ],
    "pitch_hero": [
        "https://images.unsplash.com/photo-1551076805-e1869033e561?w=1200&q=80",
        "https://images.unsplash.com/photo-1588776814546-1ffcf47267a5?w=1200&q=80",
        "https://images.unsplash.com/photo-1631217868264-e5b90bb7e133?w=1200&q=80",
        "https://images.unsplash.com/photo-1629909613654-28e377c37b09?w=1200&q=80",
        "https://images.unsplash.com/photo-1606811971618-4486d14f3f99?w=1200&q=80",
    ],
    "pitch_mockup": [
        "https://images.unsplash.com/photo-1551076805-e1869033e561?w=1000&q=80",
        "https://images.unsplash.com/photo-1588776814546-1ffcf47267a5?w=1000&q=80",
        "https://images.unsplash.com/photo-1631217868264-e5b90bb7e133?w=1000&q=80",
        "https://images.unsplash.com/photo-1629909613654-28e377c37b09?w=1000&q=80",
        "https://images.unsplash.com/photo-1606811971618-4486d14f3f99?w=1000&q=80",
    ],
}

def pick_image(idx, category):
    """Deterministically pick an image based on file index."""
    return IMAGES[category][idx % len(IMAGES[category])]

def add_images_to_sample(filepath, idx):
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    hero_img = pick_image(idx, "hero")
    about_img = pick_image(idx, "about")

    changes = 0

    # 1. Replace the hero 3D-wrap placeholder (the big tooth icon) with a real image
    hero_pattern = r'(<div class="hero-3d-wrap"[^>]*style="[^"]*display:flex;align-items:center;justify-content:center;background:linear-gradient\(135deg,#0ea5e910,#38bdf810\)[^"]*"[^>]*>)<i class="fa-solid fa-tooth"[^>]*></i>(</div>)'
    hero_replacement = r'\1<img src="' + hero_img + r'" alt="Clinic" style="width:100%;height:100%;object-fit:cover;border-radius:20px">\2'
    
    if re.search(hero_pattern, html, re.DOTALL):
        html = re.sub(hero_pattern, hero_replacement, html, count=1, flags=re.DOTALL)
        changes += 1
        print(f"  [OK] Hero image added")
    else:
        # Try alternative patterns - look for any div with hero-3d-wrap or hero section icon
        alt_hero = r'(class="hero-3d-wrap"[^>]*style="[^"]*display:flex[^"]*align-items:center[^"]*justify-content:center[^"]*border-radius:20px"[^>]*>)(<i[^>]*fa-tooth[^>]*></i>)(</div>)'
        if re.search(alt_hero, html, re.DOTALL):
            html = re.sub(alt_hero, r'\1<img src="' + hero_img + r'" alt="Clinic" style="width:100%;height:100%;object-fit:cover;border-radius:20px">\3', html, count=1, flags=re.DOTALL)
            changes += 1
            print(f"  [OK] Hero image added (alt pattern)")
        else:
            print(f"  [SKIP] Hero - pattern not found")

    # 2. Replace the about section placeholder icon (background gradient with fa-hospital icon)
    # The about section has: glass div > inner div with gradient bg + icon
    # Find the about section image placeholder
    about_icon_pattern = r'(<div class="glass"[^>]*style="padding:8px"[^>]*>\s*<div style="width:100%;height:350px;border-radius:12px;background:linear-gradient\(135deg,#0ea5e912,#38bdf812\);display:flex;align-items:center;justify-content:center">\s*)<i class="fa-solid fa-hospital"[^>]*></i>\s*(</div>\s*</div>)'
    
    if re.search(about_icon_pattern, html, re.DOTALL):
        html = re.sub(about_icon_pattern, r'\1<img src="' + about_img + r'" alt="Clinic Interior" style="width:100%;height:100%;object-fit:cover;border-radius:12px">\2', html, count=1, flags=re.DOTALL)
        changes += 1
        print(f"  [OK] About image added")
    else:
        # Broader pattern - look for the about section image
        alt_about = r'(<div class="glass"[^>]*style="padding:8px"[^>]*>\s*<div[^>]*style="[^"]*width:100%[^"]*height:350px[^"]*border-radius:12px[^"]*display:flex[^"]*align-items:center[^"]*justify-content:center[^"]*">\s*)<i[^>]*fa-hospital[^>]*></i>\s*(</div>\s*</div>)'
        if re.search(alt_about, html, re.DOTALL):
            html = re.sub(alt_about, r'\1<img src="' + about_img + r'" alt="Clinic Interior" style="width:100%;height:100%;object-fit:cover;border-radius:12px">\2', html, count=1, flags=re.DOTALL)
            changes += 1
            print(f"  [OK] About image added (alt pattern)")
        else:
            print(f"  [SKIP] About - pattern not found")

    if changes > 0:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"  => {changes} change(s) written")
    else:
        print(f"  => No changes needed")

def add_images_to_pitch(filepath, idx):
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    hero_img = pick_image(idx, "pitch_hero")
    mockup_img = pick_image(idx, "pitch_mockup")
    changes = 0

    # 1. The hero slide has a big icon box - add a background image to the slide itself
    # The first slide (active) has: <div class="slide active" style="background:radial-gradient(...),#0f172a">
    # Replace to add the image as a background element inside the slide
    
    # Add a hero background image behind the first slide's content
    first_slide_pattern = r'(<div class="slide active" style="background:radial-gradient\(ellipse at 30% 50%,#0ea5e915 0%,transparent 60%\),#0f172a">\s*<div class="text-center")'
    first_slide_replacement = r'<div class="slide active" style="background:radial-gradient(ellipse at 30% 50%,rgba(10,15,46,0.85) 0%,rgba(15,23,42,0.92) 100%),url(' + hero_img + r') center/cover no-repeat,#0f172a">\1'
    
    if re.search(first_slide_pattern, html):
        html = re.sub(first_slide_pattern, first_slide_replacement, html, count=1)
        changes += 1
        print(f"  [OK] Hero slide background image added")
    else:
        print(f"  [SKIP] Hero slide - pattern not found")

    # 2. The "concept website" slide has a placeholder div - replace with actual image
    mockup_pattern = r'(<div style="background:#0a0f1e;border-radius:12px;height:400px;display:flex;align-items:center;justify-content:center">\s*<div style="text-align:center"><i class="fa-solid fa-globe"[^>]*></i>)'
    mockup_replacement = r'<div style="background:#0a0f1e;border-radius:12px;height:400px;display:flex;align-items:center;justify-content:center;overflow:hidden;position:relative">\n<img src="' + mockup_img + r'" alt="Website preview" style="width:100%;height:100%;object-fit:cover;opacity:0.3;position:absolute;inset:0"><div style="position:relative;z-index:1;text-align:center">'
    
    if re.search(mockup_pattern, html, re.DOTALL):
        html = re.sub(mockup_pattern, mockup_replacement, html, count=1)
        changes += 1
        print(f"  [OK] Mockup image added")
    else:
        print(f"  [SKIP] Mockup - pattern not found")

    if changes > 0:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"  => {changes} change(s) written")
    else:
        print(f"  => No changes needed")


def main():
    sample_dir = os.path.join(BASE, "sample website")
    pitch_dir = os.path.join(BASE, "pitch deck")

    # Process sample websites
    print("=== SAMPLE WEBSITES ===")
    sample_files = sorted([f for f in os.listdir(sample_dir) if f.endswith('.html')])
    for i, fname in enumerate(sample_files):
        fpath = os.path.join(sample_dir, fname)
        print(f"[{i+1}/{len(sample_files)}] {fname}")
        add_images_to_sample(fpath, i)

    print()
    print("=== PITCH DECKS ===")
    pitch_files = sorted([f for f in os.listdir(pitch_dir) if f.endswith('.html')])
    for i, fname in enumerate(pitch_files):
        fpath = os.path.join(pitch_dir, fname)
        print(f"[{i+1}/{len(pitch_files)}] {fname}")
        add_images_to_pitch(fpath, i)

    print()
    print("Done! All 30 files processed.")

if __name__ == "__main__":
    main()
