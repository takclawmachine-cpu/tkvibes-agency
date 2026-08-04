"""Build a phone/WhatsApp outreach queue from the lead export.

    python -m src.build_outreach                    # mobiles only
    python -m src.build_outreach --include-landline
    python -m src.build_outreach --tier HOT
    python -m src.build_outreach --limit 20

Outputs data/outreach_queue.csv + .json — review before sending.
"""
import argparse
import json
import os

from .config import load_config
from .log_config import get_logger
from .models import Lead
from .outreach.phone import build_queue, export_queue

logger = get_logger(__name__)

# Personal, human tone — written as Taarush (owner) manually messaging each lead.
# Hook + short story, references the sample website + pitch deck he'll share.
# Keep it short, specific, and non-spammy. First line must earn the read.
DEFAULT_TEMPLATE = (
    "Hi! This is Taarush, I run TK Vibes, a small web studio. "
    "I was actually looking up {category}s in {city} last week and {business_name} "
    "kept coming up with great reviews — but I couldn't find a website, which "
    "honestly surprised me. So I went ahead and built a sample one for you. "
    "It's real, it's ready, and it's genuinely just a click away from going live. "
    "I'll send over the sample site and a short deck showing what it could do for "
    "you — no charge to look, no pressure. Would you like to see it?"
)

# Used when the lead ALREADY has a website — different, honest angle.
HAS_SITE_TEMPLATE = (
    "Hi! This is Taarush, I run TK Vibes, a small web studio. "
    "I came across {business_name} while looking at {category}s in {city} — "
    "your reviews are great, but your current site isn't doing them justice. "
    "So I redesigned it. Not a mockup, an actual working version that's a click "
    "away from going live. I'll share the redesign and a short deck on what it "
    "could do for you — free to look, zero pressure. Want me to send it over?"
)


def _load_leads(path: str) -> list[Lead]:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    leads = []
    for d in data:
        l = Lead()
        for k, v in d.items():
            if hasattr(l, k):
                setattr(l, k, v)
        leads.append(l)
    return leads


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config.yaml")
    ap.add_argument("--tier", default=None, help="HOT / WARM / COLD filter")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--include-landline", action="store_true")
    ap.add_argument("--template-file", default=None)
    args = ap.parse_args()

    cfg = load_config(args.config)
    leads = _load_leads(cfg["handoff"]["export_json"])

    if args.tier:
        leads = [l for l in leads if l.lead_tier == args.tier.upper()]

    template = DEFAULT_TEMPLATE
    if args.template_file:
        with open(args.template_file, encoding="utf-8") as f:
            template = f.read()

    queue = build_queue(leads, template, include_landline=args.include_landline,
                        template_has_site=HAS_SITE_TEMPLATE)
    if args.limit:
        queue = queue[:args.limit]

    out_dir = os.path.dirname(cfg["handoff"]["export_json"]) or "data"
    csv_path = os.path.join(out_dir, "outreach_queue.csv")
    json_path = os.path.join(out_dir, "outreach_queue.json")
    export_queue(queue, csv_path, json_path)

    by_ch = {}
    for r in queue:
        by_ch[r["channel"]] = by_ch.get(r["channel"], 0) + 1

    print(f"{len(queue)} leads queued from {len(leads)} total")
    for ch, n in sorted(by_ch.items()):
        print(f"  {ch}: {n}")
    print(f"\n  {csv_path}\n  {json_path}")
    print("\nReview the queue before sending. Indian numbers need DLT-registered "
          "SMS templates or an approved WhatsApp Business template.")


if __name__ == "__main__":
    main()