# TKVibes Marketing Engine

Production-ready video creation pipeline for Instagram Reels, YouTube Shorts, and social media promotions.

## What it does

Generates animated promotional videos for TKVibes Digital Agency:
1. **Storyboard** — Plans scene-by-scene narrative based on templates
2. **Frame Renderer** — Renders frames with gradients, text animation, shapes, stats counters
3. **Video Composer** — Stitches scenes with ffmpeg transitions + audio
4. **Voiceover** — AI voice narration via edge-tts
5. **Memory Bank** — Indexed database of every reel created

## Usage

```bash
# Show engine status
python marketing/engine.py status

# Plan a storyboard
python marketing/engine.py plan --template brand_showcase

# Render a full video (no voiceover)
python marketing/engine.py full

# Render with voiceover
python marketing/engine.py full --voiceover

# Service spotlight
python marketing/engine.py full --template service_spotlight --service "Website Development"

# List all reels
python marketing/engine.py list

# Search reels
python marketing/engine.py search --query "website"
```

## Templates

| Template | Description |
|----------|-------------|
| `brand_showcase` | General agency promotion, services overview |
| `service_spotlight` | Deep dive on one specific service |
| `quick_tip` | Digital marketing tip with value content |
| `testimonial` | Client testimonial / social proof |

## Output formats

| Format | Resolution | Use |
|--------|-----------|-----|
| `instagram_reel` | 1080×1920 | Instagram Reels |
| `youtube_shorts` | 1080×1920 | YouTube Shorts |
| `square` | 1080×1080 | Instagram Feed / LinkedIn |
| `landscape` | 1920×1080 | YouTube / Website |

## Storage

```
marketing/
├── engine.py          # Main engine
├── config.yaml        # Brand & video config
├── memory_index.json  # Indexed memory bank of all reels
├── templates/         # Saved templates
├── assets/            # Brand assets, fonts, music
└── stories/           # Generated reels (organized by date)
    └── YYYYMMDD_HHMMSS_title/
        ├── scene_01.mp4
        ├── scene_02.mp4
        └── title_final.mp4
```

## Programmatic usage

```python
from marketing.engine import TKVibesMarketingEngine

engine = TKVibesMarketingEngine()

# Plan
sb = engine.plan("brand_showcase")

# Render
result = engine.render(sb)

# Check it
print(f"Created: {result['output_path']}")