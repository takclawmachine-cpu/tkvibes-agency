#!/usr/bin/env python
"""
TKVibes Marketing Engine — CLI Entry Point

Usage:
  python marketing/engine.py status          # Show engine status
  python marketing/engine.py plan            # Generate a storyboard
  python marketing/engine.py demo            # Run full demo (plan + render)
  python marketing/engine.py full --voiceover # Full pipeline with voiceover
  python marketing/engine.py list            # List all created reels
  python marketing/engine.py search --query "brand"  # Search reels

Options:
  --template     brand_showcase | service_spotlight | quick_tip | testimonial
  --format       instagram_reel | youtube_shorts | square | landscape
  --service      Name of service to spotlight
  --voiceover    Add AI voiceover narration
  --name         Custom output name for the reel
  --tag          Filter reels by tag
  --query        Search query for finding reels
"""
import sys
import os

# Add parent to path so imports work
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from marketing.engine import main

if __name__ == "__main__":
    sys.argv[0] = "python marketing/engine.py"
    main()