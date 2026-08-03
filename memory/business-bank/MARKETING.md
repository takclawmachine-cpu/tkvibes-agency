# Marketing Engine — Deep Reference

## Architecture
`marketing/` — Python, generates video reels for Instagram/YouTube

```
marketing/
├── engine.py          # TKVibesMarketingEngine class
├── config.yaml        # Brand colors, audio, video codecs
├── memory_index.json  # Indexed bank of all created reels
├── templates/         # Storyboard templates (brand_showcase, service_spotlight, quick_tip, testimonial)
├── assets/            # Brand assets, fonts, music
├── stories/           # Generated reels (YYYYMMDD_HHMMSS_title/)
│   └── scene_*.mp4 → title_final.mp4
├── animated/          # Animated sequences
└── __init__.py
```

## Commands
```bash
python marketing/engine.py status
python marketing/engine.py plan --template brand_showcase
python marketing/engine.py full --voiceover --template service_spotlight --service "Website Development"
python marketing/engine.py list
python marketing/engine.py search --query "website"
```

## Templates
| Template | Purpose |
|----------|---------|
| `brand_showcase` | General agency promotion |
| `service_spotlight` | Deep dive on one service |
| `quick_tip` | Digital marketing tip |
| `testimonial` | Client social proof |

## Output Formats
| Format | Resolution | Platform |
|--------|-----------|----------|
| `instagram_reel` | 1080×1920 | Instagram Reels |
| `youtube_shorts` | 1080×1920 | YouTube Shorts |
| `square` | 1080×1080 | Feed / LinkedIn |
| `landscape` | 1920×1080 | YouTube / Website |

## Brand Colors
- Primary: `#6C5CE7` (purple) · Secondary: `#00CEC9` (teal) · Accent: `#FDCB6E` (amber)
- Voice: `en-IN-NeerjaNeural` / `en-IN-PrabhatNeural` (edge-tts)