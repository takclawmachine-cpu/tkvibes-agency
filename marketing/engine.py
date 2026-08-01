# TKVibes Marketing Engine
# ========================
# Production-grade video pipeline for Instagram Reels & YouTube Shorts
# Uses ffmpeg gradients + drawtext for fast animation
# edge-tts for voiceover

import os, sys, json, yaml, hashlib, shutil, asyncio, random, re
from pathlib import Path
from datetime import datetime
import subprocess

BASE_DIR = Path(__file__).resolve().parent.parent
MARKETING_DIR = BASE_DIR / "marketing"
STORIES_DIR = MARKETING_DIR / "stories"
ASSETS_DIR = MARKETING_DIR / "assets"
MEMORY_FILE = MARKETING_DIR / "memory_index.json"
CONFIG_FILE = MARKETING_DIR / "config.yaml"

for d in [MARKETING_DIR, STORIES_DIR, ASSETS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ── Config ────────────────────────────────────────────────────────────────
DEFAULT_CONFIG = {
    "brand": {
        "name": "TKVibes", "tagline": "Digital Agency That Delivers",
        "website": "tkvibes.in", "phone": "+91 98182 46938",
        "colors": {
            "primary": "#6C5CE7", "secondary": "#00CEC9",
            "accent": "#FDCB6E", "dark": "#2D3436", "light": "#F8F9FA", "white": "#FFFFFF"
        }
    },
    "video": {
        "instagram_reel": {"w": 1080, "h": 1920, "fps": 30, "crf": 18, "preset": "fast", "codec": "libx264"},
        "youtube_shorts": {"w": 1080, "h": 1920, "fps": 30, "crf": 18, "preset": "fast", "codec": "libx264"},
        "square": {"w": 1080, "h": 1080, "fps": 30, "crf": 18, "preset": "fast", "codec": "libx264"},
        "landscape": {"w": 1920, "h": 1080, "fps": 30, "crf": 18, "preset": "fast", "codec": "libx264"},
    },
    "audio": {"voice": "en-IN-NeerjaNeural", "voice_alt": "en-IN-PrabhatNeural"}
}

def load_config():
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            return _deep_merge(DEFAULT_CONFIG, yaml.safe_load(f))
    with open(CONFIG_FILE, "w") as f:
        yaml.dump(DEFAULT_CONFIG, f, default_flow_style=False)
    return DEFAULT_CONFIG

def _deep_merge(base, over):
    r = dict(base)
    for k, v in over.items():
        if k in r and isinstance(r[k], dict) and isinstance(v, dict):
            r[k] = _deep_merge(r[k], v)
        else:
            r[k] = v
    return r

# ── Memory Bank ───────────────────────────────────────────────────────────
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

def search_reels(q):
    q = q.lower()
    mem = load_memory()
    return [r for r in mem["reels"]
            if q in r.get("title","").lower() or any(q in t.lower() for t in r.get("tags",[]))]

# ── Storyboard Templates ──────────────────────────────────────────────────
TEMPLATES = {
    "brand_showcase": {
        "title": "TKVibes - Your Digital Partner",
        "scenes": [
            ("Hook", 2.5, ["Your Business Deserves", "a Digital Presence That Works"]),
            ("Problem", 3.0, ["Struggling with:", "No website? Low traffic?", "Few leads? No brand?"]),
            ("Solution", 4.0, ["We Build:", "Stunning Websites", "Brand Identity", "SEO & Ads", "Lead Systems"]),
            ("Trust", 3.0, ["Trusted by", "Growing Businesses", "Across India"]),
            ("CTA", 3.5, ["Let's Build Yours", "tkvibes.in", "+91 98182 46938"]),
        ]
    },
    "service_spotlight": {
        "title": "TKVibes - {service}",
        "scenes": [
            ("Hook", 2.5, ["Need {service}?", "We've Got You Covered"]),
            ("Problem", 2.5, ["Don't let {problem} hold you back"]),
            ("What We Do", 3.5, ["What we offer:", "  {detail1}", "  {detail2}", "  {detail3}"]),
            ("Results", 3.0, ["Results that speak:", "{result}"]),
            ("CTA", 3.0, ["Get Started Today", "tkvibes.in", "#DigitalAgency"]),
        ]
    },
    "quick_tip": {
        "title": "Digital Tip by TKVibes",
        "scenes": [
            ("Tip", 5.0, ["{tip}"]),
            ("Why It Matters", 3.0, ["{explanation}"]),
            ("CTA", 3.0, ["Follow for more tips!", "tkvibes.in"]),
        ]
    },
    "testimonial": {
        "title": "What Clients Say - TKVibes",
        "scenes": [
            ("Hook", 2.0, ["Don't take our word for it..."]),
            ("Quote", 4.0, ['"' + "{quote}" + '"', "- {client_name}"]),
            ("Result", 3.0, ["{result}"]),
            ("CTA", 3.0, ["Want similar results?", "tkvibes.in"]),
        ]
    }
}

SERVICES = [
    ("Website Development", "outdated website", "mobile-responsive", "fast loading", "CMS integration", "100% mobile-friendly"),
    ("Brand Identity", "generic branding", "unique logo", "color palette", "brand guidelines", "Memorable brand"),
    ("SEO Optimization", "low rankings", "keyword research", "on-page SEO", "technical SEO", "#1 on Google"),
    ("Social Media Mgmt", "inconsistent posting", "content calendar", "engagement strategy", "analytics", "300%+ engagement"),
    ("Google Ads", "wasted ad spend", "targeted campaigns", "A/B testing", "conversion tracking", "2.5x ROAS"),
    ("Lead Generation", "manual chasing", "automated funnels", "CRM integration", "email sequences", "100+ leads/month"),
    ("E-commerce", "low sales", "product catalog", "payment setup", "shipping config", "3x revenue"),
    ("UI/UX Design", "poor UX", "user research", "wireframing", "prototyping", "40% higher conversion"),
]

TIPS = [
    ("Your website is your 24/7 salesperson. Make it answer questions, not just look pretty.", "Well-designed sites convert 2.5x better."),
    ("Google rewards sites loading under 2.5s. Speed = Sales.", "53% of mobile users leave if a page takes >3s."),
    ("Consistency beats intensity. 3x/week beats 10 posts in one day.", "Algorithms favor regular posting."),
    ("SEO is a marathon. Quality content compounds over 6-12 months.", "Position #1 gets 27.6% of all clicks."),
    ("Your brand is what people say when you are not in the room.", "Consistent branding increases revenue by 23%."),
    ("Best time to start marketing was yesterday. Next best is today.", "Businesses that blog get 67% more leads."),
]

def build_storyboard(template="brand_showcase", **kw):
    tmpl = TEMPLATES.get(template, TEMPLATES["brand_showcase"])
    user_svc = kw.pop("service", None)
    svc_name, *probs = random.choice(SERVICES)
    if user_svc:
        for s in SERVICES:
            if user_svc.lower() in s[0].lower():
                svc_name, *probs = s
                break
        else:
            svc_name = user_svc
    tip = random.choice(TIPS)
    subs = {
        "{service}": svc_name, "{problem}": probs[0],
        "{detail1}": probs[1], "{detail2}": probs[2],
        "{detail3}": probs[3], "{result}": probs[4],
        "{tip}": tip[0], "{explanation}": tip[1],
        "{quote}": kw.get("quote", "They transformed our online presence completely. Highly recommended!"),
        "{client_name}": kw.get("client", "Rahul S., Business Owner"),
    }
    scenes = []
    for i, (title, dur, lines) in enumerate(tmpl["scenes"]):
        resolved = []
        for ln in lines:
            for k, v in subs.items():
                ln = ln.replace(k, v)
            resolved.append(ln)
        scenes.append({"id": "s%d" % (i+1), "title": title, "dur": dur,
                       "lines": resolved, "gradient": i % 2 == 0})
    return {"title": tmpl["title"], "scenes": scenes,
            "total_dur": sum(s["dur"] for s in scenes),
            "format": kw.get("format", "instagram_reel")}

# ── FFmpeg Renderer ───────────────────────────────────────────────────────
def esc_text(t):
    """Escape text for ffmpeg drawtext."""
    return t.replace("'", "\u2019").replace(":", "\\:").replace(",", "\\,")

def render_scene(scene, vid, output):
    """Render one scene: gradient bg + drawbox + drawtext."""
    w, h, fps = vid["w"], vid["h"], vid["fps"]
    dur = scene["dur"]
    colors = load_config()["brand"]["colors"]

    c0 = (colors["primary"] if scene["gradient"] else colors["dark"]).lstrip("#")
    c1 = (colors["secondary"] if scene["gradient"] else colors["primary"]).lstrip("#")
    accent = colors["accent"].lstrip("#")
    white = colors["white"].lstrip("#")
    dark_h = colors["dark"].lstrip("#")
    bfont = "marketing/assets/arialbd.ttf"
    rfont = "marketing/assets/arial.ttf"

    lines = scene["lines"]
    n = len(lines)
    base_y = h // 2 - (n * 80) // 2

    flt = []
    # Input: gradient source
    flt.append(f"gradients=s={w}x{h}:c0={c0}:c1={c1}:r={fps}:d={dur}")
    # Dark overlay
    flt.append(f"drawbox=x=0:y=0:w={w}:h={h}:color=black@0.25:t=fill")
    # Accent box
    if scene["gradient"]:
        flt.append(f"drawbox=x=80:y=200:w=270:h=270:color={accent}@0.2:t=fill")
    # Text lines
    for li, ln in enumerate(lines):
        ty = base_y + li * 80
        fs = 52
        if len(ln) > 18: fs = 44
        if len(ln) > 32: fs = 38
        if li == 0 and n <= 3: fs = 62
        font = bfont if fs >= 50 else rfont
        safe = esc_text(ln)
        flt.append(
            f"drawtext=text='{safe}':fontfile={font}:fontsize={fs}:"
            f"fontcolor={white}:x=(w-text_w)/2:y={ty}"
        )
    # CTA button
    if "CTA" in scene["title"]:
        bh, bw, byy = 70, 420, h - 220
        bx = (w - bw) // 2
        flt.append(f"drawbox=x={bx}:y={byy}:w={bw}:h={bh}:color={accent}:t=fill")
        flt.append(
            f"drawtext=text='VISIT WEBSITE -->':fontfile={bfont}:fontsize=30:"
            f"fontcolor={dark_h}:x={w//2}:y={byy + bh//2}"
        )

    # Build ffmpeg command
    fc = ",".join(flt[1:])
    cmd = ["ffmpeg", "-y", "-f", "lavfi", "-i", flt[0]]
    if fc:
        cmd += ["-filter_complex", fc]
    cmd += ["-c:v", "libx264", "-preset", "fast", "-crf", "20",
            "-pix_fmt", "yuv420p", str(output)]

    try:
        subprocess.run(cmd, check=True, capture_output=True, timeout=300)
    except subprocess.CalledProcessError:
        # Fallback: solid color
        print("    Gradient failed, solid fallback...")
        sf = [f"drawbox=x=0:y=0:w={w}:h={h}:color={c1}@0.15:t=fill"]
        for li, ln in enumerate(lines):
            ty = base_y + li * 80
            safe = esc_text(ln)
            fs = 48 if len(ln) > 20 else 56
            sf.append(
                f"drawtext=text='{safe}':fontfile={rfont}:fontsize={fs}:"
                f"fontcolor={white}:x=(w-text_w)/2:y={ty}"
            )
        cmd2 = ["ffmpeg", "-y", "-f", "lavfi", "-i",
                f"color=c={c0}:s={w}x{h}:r={fps}:d={dur}",
                "-filter_complex", ",".join(sf),
                "-c:v", "libx264", "-preset", "fast", "-crf", "22",
                "-pix_fmt", "yuv420p", str(output)]
        subprocess.run(cmd2, check=True, capture_output=True, timeout=300)

def concat_scenes(videos, output):
    if len(videos) == 1:
        shutil.copy2(videos[0], output)
        return
    lf = output.parent / "_list.txt"
    with open(lf, "w") as f:
        for v in videos:
            f.write("file '%s'\n" % v)
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0",
                    "-i", str(lf), "-c", "copy", str(output)],
                   check=True, capture_output=True, timeout=120)
    lf.unlink(missing_ok=True)

async def gen_voiceover(text, output, voice="en-IN-NeerjaNeural"):
    import edge_tts
    c = edge_tts.Communicate(text, voice)
    await c.save(str(output))

def add_audio(video, audio, output):
    subprocess.run(["ffmpeg", "-y", "-i", str(video), "-i", str(audio),
                    "-c:v", "copy", "-c:a", "aac",
                    "-map", "0:v:0", "-map", "1:a:0", "-shortest", str(output)],
                   check=True, capture_output=True, timeout=120)

def gen_thumbnail(storyboard, output):
    colors = load_config()["brand"]["colors"]
    c0 = colors["primary"].lstrip("#")
    c1 = colors["secondary"].lstrip("#")
    try:
        subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i",
                        "gradients=s=1080x1920:c0=%s:c1=%s:duration=1" % (c0, c1),
                        "-vframes", "1", str(output)],
                       check=True, capture_output=True, timeout=30)
    except Exception:
        pass

# ── Engine ────────────────────────────────────────────────────────────────
class Engine:
    def __init__(self):
        self.cfg = load_config()

    def plan(self, template="brand_showcase", **kw):
        return build_storyboard(template, **kw)

    def render(self, storyboard, name=None):
        fmt = storyboard.get("format", "instagram_reel")
        vid = self.cfg["video"][fmt]
        if not name:
            safe = re.sub(r'[^a-z0-9_]+', '_', storyboard["title"].lower())[:40].strip("_")
            name = "%s_%s" % (datetime.now().strftime("%Y%m%d_%H%M%S"), safe)
        out_dir = STORIES_DIR / name
        out_dir.mkdir(parents=True, exist_ok=True)

        scene_vids = []
        for i, sc in enumerate(storyboard["scenes"]):
            sv = out_dir / ("%s.mp4" % sc["id"])
            print("  Scene %d/%d: %s (%.1fs)..." % (i+1, len(storyboard["scenes"]), sc["title"], sc["dur"]))
            render_scene(sc, vid, sv)
            scene_vids.append(sv)

        raw = out_dir / "_raw.mp4"
        print("  Assembling...")
        concat_scenes(scene_vids, raw)
        thumb = out_dir / "thumbnail.jpg"
        gen_thumbnail(storyboard, thumb)
        final = out_dir / ("%s.mp4" % name)
        shutil.move(str(raw), str(final))

        rid = hashlib.md5(str(out_dir).encode()).hexdigest()[:12]
        result = {"id": rid, "title": storyboard["title"], "format": fmt,
                  "scenes": len(storyboard["scenes"]), "duration": storyboard["total_dur"],
                  "output_path": str(final), "thumbnail": str(thumb),
                  "created_at": datetime.now().isoformat(),
                  "tags": ["tkvibes", "marketing", fmt]}
        index_reel(result)
        return result

    async def render_with_voice(self, storyboard, name=None):
        fmt = storyboard.get("format", "instagram_reel")
        vid = self.cfg["video"][fmt]
        if not name:
            safe = re.sub(r'[^a-z0-9_]+', '_', storyboard["title"].lower())[:40].strip("_")
            name = "%s_%s" % (datetime.now().strftime("%Y%m%d_%H%M%S"), safe)
        out_dir = STORIES_DIR / name
        out_dir.mkdir(parents=True, exist_ok=True)

        voice_text = ". ".join(l for sc in storyboard["scenes"] for l in sc["lines"])
        print("  Voiceover (%d chars)..." % len(voice_text))
        voice_path = out_dir / "voiceover.mp3"
        await gen_voiceover(voice_text, voice_path, self.cfg["audio"]["voice"])

        scene_vids = []
        for i, sc in enumerate(storyboard["scenes"]):
            sv = out_dir / ("%s.mp4" % sc["id"])
            print("  Scene %d: %s (%.1fs)..." % (i+1, sc["title"], sc["dur"]))
            render_scene(sc, vid, sv)
            scene_vids.append(sv)

        no_audio = out_dir / "_noaudio.mp4"
        concat_scenes(scene_vids, no_audio)
        final = out_dir / ("%s.mp4" % name)
        print("  Adding audio...")
        add_audio(no_audio, voice_path, final)
        no_audio.unlink(missing_ok=True)

        thumb = out_dir / "thumbnail.jpg"
        gen_thumbnail(storyboard, thumb)

        rid = hashlib.md5(str(out_dir).encode()).hexdigest()[:12]
        result = {"id": rid, "title": storyboard["title"], "format": fmt,
                  "scenes": len(storyboard["scenes"]), "duration": storyboard["total_dur"],
                  "output_path": str(final), "voiceover": str(voice_path),
                  "thumbnail": str(thumb), "created_at": datetime.now().isoformat(),
                  "tags": ["tkvibes", "marketing", fmt, "voiceover"]}
        index_reel(result)
        return result

    def list_reels(self, tag=None):
        mem = load_memory()
        r = mem.get("reels", [])
        if tag:
            return [x for x in r if tag in x.get("tags", [])]
        return r

    def search(self, q):
        return search_reels(q)

    def stats(self):
        mem = load_memory()
        return {"total": len(mem.get("reels", [])),
                "last": mem.get("stats", {}).get("last")}

# ── CLI ───────────────────────────────────────────────────────────────────
def main():
    import argparse
    ap = argparse.ArgumentParser(description="TKVibes Marketing Engine")
    ap.add_argument("action", nargs="?", default="status",
                    choices=["plan", "render", "full", "list", "search", "stats", "demo"])
    ap.add_argument("--template", default="brand_showcase")
    ap.add_argument("--format", default="instagram_reel")
    ap.add_argument("--service")
    ap.add_argument("--voiceover", action="store_true")
    ap.add_argument("--query")
    ap.add_argument("--tag")
    ap.add_argument("--name")
    args = ap.parse_args()
    eng = Engine()

    if args.action in ("status", "stats"):
        s = eng.stats()
        print("\n[STATS] TKVibes Marketing Engine")
        print("=" * 40)
        print("  Reels:     %d" % s["total"])
        print("  Last:      %s" % (s["last"] or "Never"))
        print("  Store:     %s" % STORIES_DIR)
        print("  Memory:    %s" % MEMORY_FILE)

    elif args.action == "plan":
        sb = eng.plan(args.template, format=args.format, service=args.service)
        print("\n[STORYBOARD] %s (%.1fs)" % (sb["title"], sb["total_dur"]))
        print("=" * 40)
        for s in sb["scenes"]:
            print("  [%s] %s (%.1fs)" % (s["id"], s["title"], s["dur"]))
            for ln in s["lines"]:
                print("       %s" % ln)

    elif args.action == "demo":
        sb = eng.plan(args.template, format=args.format, service=args.service)
        print("\n[DEMO] %s (%.1fs)" % (sb["title"], sb["total_dur"]))
        r = eng.render(sb, args.name)
        print("  [OK] %s" % r["output_path"])

    elif args.action == "render":
        sb = eng.plan(args.template, format=args.format, service=args.service)
        print("Rendering %s..." % sb["title"])
        if args.voiceover:
            r = asyncio.run(eng.render_with_voice(sb, args.name))
        else:
            r = eng.render(sb, args.name)
        print("  [OK] %s" % r["output_path"])

    elif args.action == "full":
        sb = eng.plan(args.template, format=args.format, service=args.service)
        print("[PIPELINE] %s (%.1fs, %d scenes)" % (sb["title"], sb["total_dur"], len(sb["scenes"])))
        if args.voiceover:
            r = asyncio.run(eng.render_with_voice(sb, args.name))
        else:
            r = eng.render(sb, args.name)
        print("  [OK] Output: %s" % r["output_path"])
        print("  [THUMB] %s" % r.get("thumbnail", "N/A"))
        print("  [ID]    %s" % r["id"])

    elif args.action == "list":
        for r in eng.list_reels(args.tag):
            print("  [%s] %s (%.1fs)" % (r["id"], r["title"], r["duration"]))
            print("       %s" % r["output_path"])

    elif args.action == "search":
        for r in eng.search(args.query or ""):
            print("  [%s] %s" % (r["id"], r["title"]))
            print("       %s" % r.get("tags", []))

if __name__ == "__main__":
    main()