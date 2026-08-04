#!/usr/bin/env python3
"""Fix remaining pitch decks and sample websites that didn't get images."""

import os
import re

BASE = r"C:\Users\takcl\Desktop\tkvibes-agency\Sample Webpages and pitch deck"

# Fix the 6 remaining pitch decks that didn't get hero images
PITCH_HERO_IMG = "https://images.unsplash.com/photo-1551076805-e1869033e561?w=1200&q=80"
PITCH_MOCKUP_IMG = "https://images.unsplash.com/photo-1551076805-e1869033e561?w=1000&q=80"
SAMPLE_HERO_IMG = "https://images.unsplash.com/photo-1631217868264-e5b90bb7e133?w=800&q=80"

def fix_pitch_hero(filepath):
    """Add background image to first slide of pitch deck regardless of color."""
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()
    
    # Check if hero already has background image
    if 'url(' in html[:500]:
        # Check first slide - if it has a url() in its inline style, already done
        first_slide = html.split('class="slide active"', 1)
        if len(first_slide) > 1 and 'url(' in first_slide[1][:500]:
            return False  # Already has image
    
    # Find the first slide's background style - works with any color hex
    # Pattern: <div class="slide active" style="background:radial-gradient(...),#xxxxxx">
    pattern = r'(<div class="slide active" style="background:radial-gradient\(ellipse at [^)]+\)[^,]*,[^"]*">)'
    
    def add_bg(match):
        orig = match.group(1)
        # Add the image background with dark overlay
        new_bg = orig.replace(
            'style="background:radial-gradient(',
            'style="background:radial-gradient('
        )
        # Replace the style to include the image with overlay
        new_style = re.sub(
            r'style="background:radial-gradient\(([^)]+)\)([^,]*),([^"]*)"',
            r'style="background:linear-gradient(rgba(10,15,30,0.7),rgba(10,15,30,0.7)),url(' + PITCH_HERO_IMG + r') center/cover no-repeat,radial-gradient(\1)\2,\3"',
            orig
        )
        return new_style
    
    new_html = re.sub(pattern, add_bg, html)
    
    if new_html != html:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_html)
        return True
    return False

def fix_pitch_mockup(filepath):
    """Add image to the website preview slide (slide 5 typically)."""
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()
    
    # Already has an image?
    if 'Webpage and pitch deck/pitch deck' in filepath:
        pass  # check anyway
    
    # Find the website preview slide - look for the globe icon in mockup
    # Pattern: <i class="fa-solid fa-globe" ...> inside the mockup container
    pattern = r'(<div style="background:#0a0f1e;border-radius:12px;height:400px;display:flex;align-items:center;justify-content:center[^>]*>)\s*<div style="text-align:center">\s*<i class="fa-solid fa-globe"'
    
    def add_img(match):
        opening = match.group(1)
        # Add position:relative and overflow:hidden if not present
        if 'position:relative' not in opening:
            opening = opening.replace('">', ';overflow:hidden;position:relative">')
        replacement = opening + (
            '\n<img src="' + PITCH_MOCKUP_IMG + 
            '" alt="Website preview" style="width:100%;height:100%;object-fit:cover;opacity:0.25;position:absolute;inset:0">\n'
            '<div style="position:relative;z-index:1;text-align:center">\n<i class="fa-solid fa-globe"'
        )
        return replacement
    
    new_html = re.sub(pattern, add_img, html)
    
    if new_html != html:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_html)
        return True
    return False

def fix_sample_hero_canvas(filepath):
    """For sample websites with canvas hero, replace canvas with img."""
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()
    
    # Check if this file uses a canvas in the hero
    if '<canvas id="hero-canvas">' not in html:
        return False
    
    # If already has an img inside hero-3d-wrap, skip
    if '<img' in html.split('<canvas id="hero-canvas">')[0][-200:]:
        return False  # already has an image nearby
    
    # Replace the canvas + shimmer with an image
    # Pattern: <canvas id="hero-canvas"></canvas>\n</div> (closing hero-3d-wrap)
    pattern = r'<div class="hero-3d-wrap">\s*<div id="shimmer-overlay" class="shimmer"></div>\s*<canvas id="hero-canvas"></canvas>\s*</div>'
    
    replacement = (
        '<div class="hero-3d-wrap" style="display:flex;align-items:center;justify-content:center;overflow:hidden">\n'
        '<img src="' + SAMPLE_HERO_IMG + '" alt="Dental Clinic" '
        'style="width:100%;height:100%;object-fit:cover;border-radius:20px">\n</div>'
    )
    
    new_html = re.sub(pattern, replacement, html)
    
    if new_html != html:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_html)
        return True
    return False


def main():
    pitch_dir = os.path.join(BASE, "pitch deck")
    sample_dir = os.path.join(BASE, "sample website")
    
    print("=== PITCH DECKS (fixing remaining) ===")
    pitch_files = sorted([f for f in os.listdir(pitch_dir) if f.endswith('.html')])
    for i, fname in enumerate(pitch_files):
        fpath = os.path.join(pitch_dir, fname)
        print(f"[{i+1}/{len(pitch_files)}] {fname}")
        h = fix_pitch_hero(fpath)
        m = fix_pitch_mockup(fpath)
        if h or m:
            print(f"  Hero: {'✓' if h else '—'} | Mockup: {'✓' if m else '—'}")
        else:
            print(f"  No changes needed")
    
    print()
    print("=== SAMPLE WEBSITES (fixing canvas hero) ===")
    sample_files = sorted([f for f in os.listdir(sample_dir) if f.endswith('.html')])
    for i, fname in enumerate(sample_files):
        fpath = os.path.join(sample_dir, fname)
        result = fix_sample_hero_canvas(fpath)
        if result:
            print(f"[{i+1}] {fname}: Canvas replaced with image ✓")
    
    print()
    print("Done!")

if __name__ == "__main__":
    main()
