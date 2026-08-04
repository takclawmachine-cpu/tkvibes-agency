#!/usr/bin/env python3
"""Add stock image backgrounds to ALL pitch deck slides that don't already have one."""
import os, re

PITCH_DIR = r"C:\Users\takcl\Desktop\tkvibes-agency\Sample Webpages and pitch deck\pitch deck"

IMAGES = [
    "https://images.unsplash.com/photo-1551076805-e1869033e561?w=1200&q=80",
    "https://images.unsplash.com/photo-1588776814546-1ffcf47267a5?w=1200&q=80",
    "https://images.unsplash.com/photo-1631217868264-e5b90bb7e133?w=1200&q=80",
    "https://images.unsplash.com/photo-1629909613654-28e377c37b09?w=1200&q=80",
    "https://images.unsplash.com/photo-1606811971618-4486d14f3f99?w=1200&q=80",
    "https://images.unsplash.com/photo-1579684385127-1ef15d508118?w=1200&q=80",
    "https://images.unsplash.com/photo-1559839734-2b71ea197ec2?w=1200&q=80",
    "https://images.unsplash.com/photo-1581595220892-b0739db3ba8c?w=1200&q=80",
    "https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?w=1200&q=80",
    "https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?w=1200&q=80",
]

def add_bg_to_all_slides(filepath, idx_start=0):
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    changes = 0
    slide_num = 0

    # Find ALL slides: <div class="slide ..." style="background:...
    # Replace inline background styles that are simple radial-gradient patterns
    # with dark overlay + background image

    def replace_slide_bg(match):
        nonlocal slide_num, changes
        full = match.group(0)
        slide_num += 1
        
        # Skip slides that already have url() in background
        if 'url(' in full:
            return full
            
        # Skip the website preview slide (it's usually styled differently with just #0f172a)
        if 'Your Concept Website' in full or 'slide' not in full:
            # Check for the concept website slide by its minimal background
            pass
            
        img = IMAGES[(idx_start + slide_num) % len(IMAGES)]
        
        # Replace background:radial-gradient(...),#xxxxx with image + dark overlay
        new = re.sub(
            r'background:radial-gradient\([^)]+\)[^,]*,[^;"]+',
            f'background:linear-gradient(rgba(10,15,30,0.75),rgba(10,15,30,0.75)),url({img}) center/cover no-repeat,#0f172a',
            full
        )
        # Also handle background:#0f172a only slides
        new = re.sub(
            r'background:#0f172a',
            f'background:linear-gradient(rgba(10,15,30,0.75),rgba(10,15,30,0.75)),url({img}) center/cover no-repeat,#0f172a',
            new
        )
        if new != full:
            changes += 1
        return new

    # Match all slide opening tags with their style attributes
    html = re.sub(
        r'<div class="slide[^"]*" style="background:[^"]*"',
        replace_slide_bg,
        html
    )
    
    if changes:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"  => {changes} slides updated")
    else:
        print(f"  => No changes")

def main():
    files = sorted(os.listdir(PITCH_DIR))
    for i, fname in enumerate(files):
        if not fname.endswith('.html'): continue
        fpath = os.path.join(PITCH_DIR, fname)
        print(f"[{i+1}] {fname}")
        add_bg_to_all_slides(fpath, i)

if __name__ == "__main__":
    main()
