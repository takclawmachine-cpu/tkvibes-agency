# TKVibes Animated Marketing Engine v2
# =====================================
# Renders rich animated HTML+CSS+SVG scenes to video using Playwright + ffmpeg
# Each scene is a self-contained HTML file with CSS keyframe animations
# Playwright captures frames as the animation plays, ffmpeg stitches to video

import os, sys, json, yaml, hashlib, shutil, asyncio, random, re
from pathlib import Path
from datetime import datetime
from typing import Optional
import subprocess

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # tkvibes-agency/
MARKETING_DIR = BASE_DIR / "marketing"
ANIMATED_DIR = MARKETING_DIR / "animated"
SCENES_DIR = ANIMATED_DIR / "scenes"
STORIES_DIR = MARKETING_DIR / "stories"
MEMORY_FILE = MARKETING_DIR / "memory_index.json"

for d in [ANIMATED_DIR, SCENES_DIR, STORIES_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ── Scene definitions ─────────────────────────────────────────────────────
# Each scene: (name, html_file, duration_seconds, description, voiceover_script)
INTRO_REEL = [
    ("Shock",       "shock.html",            3.0,  "Pain point",
     "Did you know fifty three percent of users leave a website if it takes more than three seconds to load. Your slow website is literally costing you customers every single day."),
    ("Pain Points", "pain_points.html",      2.5,  "Familiar struggles",
     "Sound familiar. Sales dropping, nobody can find you on Google, wasting money on ads that don't convert, not mobile friendly, and zero brand identity. These problems are costing your business growth."),
    ("Websites",    "website_building.html",  3.5, "Website building",
     "At TKVibes we build stunning, mobile responsive websites that load in under two seconds. From concept to launch, we handle everything. Clean code, fast performance, and designs that convert visitors into customers."),
    ("SEO",         "seo.html",              3.5, "SEO rankings",
     "Our SEO strategy puts you on page one of Google where your customers are searching. We take you from page five to the number one spot with proven techniques that drive real traffic to your business."),
    ("Ads",         "ads.html",              3.0, "Ad dashboard",
     "Stop wasting money on ads that don't work. Our targeted ad campaigns deliver an average of two point five times return on ad spend. Every rupee works harder with smart targeting and continuous optimization."),
    ("Results",     "results.html",          2.5, "Stats and testimonials",
     "The proof is in the results. Over fifty websites delivered, number one Google rankings, and ninety eight percent client satisfaction. Our clients don't just get a website, they get a complete digital transformation."),
    ("CTA",         "cta.html",              3.5, "Call to action with USP",
     "Ready to transform your business. Get your free sample website, a custom pitch deck, and flexible plans designed around your budget. Visit tkvibes dot in or call us at nine eight one eight two four six nine three eight. Let's build something amazing together."),
]

# ── Memory ────────────────────────────────────────────────────────────────
def load_memory():
    if MEMORY_FILE.exists():
        with open(MEMORY_FILE) as f:
            return json.load(f)
    return {"reels": [], "stats": {"total": 0, "last": None}}

def save_memory(m):
    with open(MEMORY_FILE, "w") as f:
        json.dump(m, f, indent=2)

def index_reel(data):
    mem = load_memory()
    mem["reels"].insert(0, data)
    mem["stats"]["total"] = len(mem["reels"])
    mem["stats"]["last"] = datetime.now().isoformat()
    save_memory(mem)

# ── Playwright Frame Capturer ─────────────────────────────────────────────

async def render_scene(scene_html: Path, output_video: Path, duration: float, fps: int = 30):
    """Open an HTML scene in headless Chromium and record frames to video."""
    from playwright.async_api import async_playwright
    
    total_frames = int(duration * fps)
    frame_dir = output_video.parent / f"frames_{output_video.stem}"
    frame_dir.mkdir(parents=True, exist_ok=True)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(
            viewport={"width": 1080, "height": 1920},
            device_scale_factor=1
        )
        
        # Open the HTML file
        html_path = scene_html.resolve()
        await page.goto(f"file:///{html_path.as_posix()}", wait_until="networkidle")
        
        # Wait a tiny bit for initial animations to start
        await asyncio.sleep(0.05)
        
        print(f"    Capturing {total_frames} frames @ {fps}fps ({duration}s)...")
        
        for f_idx in range(total_frames):
            timestamp = f_idx / fps
            frame_path = frame_dir / f"frame_{f_idx:05d}.png"
            
            # Take screenshot
            await page.screenshot(path=str(frame_path))
            
            # Small progress indicator
            if (f_idx + 1) % 30 == 0 or f_idx == 0:
                print(f"      frame {f_idx+1}/{total_frames}", end="\r")
        
        await browser.close()
    
    print(f"\n    Stitching frames to video...")
    
    # Stitch frames to video with ffmpeg
    # Use concat demuxer for speed
    flist = frame_dir / "frames.txt"
    with open(flist, "w") as f:
        for fi in sorted(frame_dir.iterdir()):
            if fi.suffix == ".png":
                f.write(f"file '{fi}'\n")
                f.write(f"duration {1/fps:.6f}\n")
    
    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(flist),
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-r", str(fps),
        str(output_video)
    ]
    subprocess.run(cmd, check=True, capture_output=True, timeout=600)
    
    # Clean up frames
    shutil.rmtree(frame_dir, ignore_errors=True)
    flist.unlink(missing_ok=True)


def concat_videos(video_paths: list[Path], output_path: Path):
    """Concatenate multiple scene videos."""
    if len(video_paths) == 1:
        shutil.copy2(video_paths[0], output_path)
        return
    
    list_file = output_path.parent / "_concat.txt"
    with open(list_file, "w") as f:
        for vp in video_paths:
            f.write(f"file '{vp}'\n")
    
    subprocess.run([
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(list_file),
        "-c", "copy",
        str(output_path)
    ], check=True, capture_output=True, timeout=120)
    
    list_file.unlink(missing_ok=True)


async def add_voiceover(video_path: Path, text: str, output_path: Path, voice: str = "en-IN-NeerjaNeural"):
    """Add voiceover to video."""
    import edge_tts
    
    voice_path = output_path.parent / "_voiceover.mp3"
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(str(voice_path))
    
    subprocess.run([
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-i", str(voice_path),
        "-c:v", "copy",
        "-c:a", "aac",
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-shortest",
        str(output_path)
    ], check=True, capture_output=True, timeout=120)
    
    voice_path.unlink(missing_ok=True)


async def generate_intro(name: str = None, with_voiceover: bool = False):
    """Generate the intro reel from all animated scenes."""
    scenes = INTRO_REEL
    total_dur = sum(s[2] for s in scenes)
    
    if not name:
        name = f"animated_intro_{datetime.now():%Y%m%d_%H%M%S}"
    
    out_dir = STORIES_DIR / name
    out_dir.mkdir(parents=True, exist_ok=True)
    
    scene_videos = []
    
    print(f"\n[TKVibes Animated Engine v2]")
    print(f"  Scenes: {len(scenes)}, Total duration: {total_dur:.1f}s")
    print(f"  Output: {out_dir}\n")
    
    for i, (scene_name, html_file, dur, desc, script) in enumerate(scenes):
        html_path = SCENES_DIR / html_file
        if not html_path.exists():
            print(f"  WARNING: {html_path} not found, skipping")
            continue
        
        video_path = out_dir / f"scene_{i+1:02d}_{scene_name.lower().replace(' ','_')}.mp4"
        print(f"  [{i+1}/{len(scenes)}] {scene_name} ({dur}s) - {desc}")
        
        await render_scene(html_path, video_path, dur, fps=30)
        scene_videos.append(video_path)
        print(f"    -> {video_path.name}")
    
    # Concatenate all scenes
    print(f"\n  Assembling {len(scene_videos)} scenes...")
    raw_video = out_dir / "_raw.mp4"
    concat_videos(scene_videos, raw_video)
    
    final_video = out_dir / f"{name}.mp4"
    
    if with_voiceover:
        print("  Adding voiceover...")
        voice_text = " ".join(s[4] for s in scenes)
        await add_voiceover(raw_video, voice_text, final_video)
        raw_video.unlink(missing_ok=True)
    else:
        shutil.move(str(raw_video), str(final_video))
    
    # Generate thumbnail using first frame
    thumb = out_dir / "thumbnail.jpg"
    subprocess.run([
        "ffmpeg", "-y", "-i", str(scene_videos[0]),
        "-vframes", "1", str(thumb)
    ], check=True, capture_output=True, timeout=30)
    
    # Index in memory
    rid = hashlib.md5(str(out_dir).encode()).hexdigest()[:12]
    result = {
        "id": rid,
        "title": "TKVibes Intro Reel (Animated)",
        "format": "instagram_reel",
        "scenes": len(scene_videos),
        "duration": total_dur,
        "output_path": str(final_video),
        "thumbnail": str(thumb),
        "created_at": datetime.now().isoformat(),
        "tags": ["tkvibes", "marketing", "instagram_reel", "animated", "v2"],
        "description": "Animated intro reel with shock element, pain points, website demo, SEO, ads, results, CTA"
    }
    index_reel(result)
    
    print(f"\n  [DONE] {final_video}")
    print(f"  [ID]   {rid}")
    return result


# ── CLI ───────────────────────────────────────────────────────────────────
def main():
    import argparse
    ap = argparse.ArgumentParser(description="TKVibes Animated Marketing Engine v2")
    ap.add_argument("action", nargs="?", default="render",
                    choices=["render", "list", "stats"])
    ap.add_argument("--voiceover", action="store_true", help="Add AI voiceover")
    ap.add_argument("--name", help="Custom output name")
    args = ap.parse_args()
    
    if args.action in ("stats", "list"):
        mem = load_memory()
        v2_reels = [r for r in mem.get("reels", []) if "v2" in r.get("tags", [])]
        print(f"[STATS] V2 Animated Reels: {len(v2_reels)}")
        for r in v2_reels:
            print(f"  [{r['id']}] {r['title']} ({r['duration']}s)")
            print(f"       {r['output_path']}")
    else:
        asyncio.run(generate_intro(args.name, args.voiceover))

if __name__ == "__main__":
    main()