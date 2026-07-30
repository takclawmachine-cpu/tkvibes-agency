"""Scaffold client project folders for leads, ready for the asset agents.

Mirrors the existing structure under ~/Desktop/clients/<slug>/:

    <slug>/
      AGENTS.md                  # business brief (agent context)
      <slug>-prompt.md           # build instructions for the website agent
      <slug>-website.html        # produced by the website agent
      <slug>-pitch-deck.html     # produced by the deck agent
      spec.json                  # machine-readable site + deck spec

    python -m src.scaffold_clients --tier HOT --limit 5
    python -m src.scaffold_clients --all
"""
import argparse
import json
import os
import re

from .config import load_config
from .models import Lead
from .handoff.sample_site import build_site_spec
from .handoff.pitch_deck import build_deck_spec
from .outreach.phone import clean_name, classify_number

CLIENTS_DIR = os.path.expanduser("~/Desktop/clients")


def slugify(name: str) -> str:
    if not (name or "").strip():
        return "client"
    s = clean_name(name).lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return re.sub(r"-{2,}", "-", s)[:60] or "client"


def _load_leads(path: str) -> list[Lead]:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    out = []
    for d in data:
        l = Lead()
        for k, v in d.items():
            if hasattr(l, k):
                setattr(l, k, v)
        out.append(l)
    return out


def agents_md(lead: Lead, slug: str, wa: str) -> str:
    name = clean_name(lead.business_name)
    site = lead.website_url or "NONE — this would be their first website"
    return f"""# {name} — Lead Project

## Business Details
- **Full listing name:** {lead.business_name}
- **Type:** {lead.category}
- **Location:** {lead.address or lead.city}
- **City:** {lead.city}
- **Phone:** {lead.phone_primary}
- **Email:** {lead.email or "not found — phone/WhatsApp outreach only"}
- **Google Rating:** {lead.rating or "N/A"}★ ({lead.review_count or 0} reviews)
- **Website:** {site}
- **Google Maps:** {lead.source_url}

## Lead Status
- Lead score: **{lead.lead_score}** ({lead.lead_tier})
- Contact channel: **{"WhatsApp" if wa else "phone call"}**
- Outreach: {lead.outreach_status}
{f"- WhatsApp link: {wa}" if wa else ""}

## Generated Assets
- `{slug}-website.html` — concept website (single file, no build step)
- `{slug}-pitch-deck.html` — pitch deck
- `spec.json` — machine-readable spec

## Rules
- This is an **unsolicited concept**. Every asset must carry the footer
  "Concept by TKVibes — not affiliated with {name}".
- Do **not** invent services, prices, credentials, doctor names, or awards.
  Use only the facts above; keep copy generic where data is missing.
- Real rating/review counts only — never fabricate testimonials.
"""


def prompt_md(lead: Lead, slug: str) -> str:
    name = clean_name(lead.business_name)
    return f"""# Build prompt — {name}

Build a **premium, modern, single-file concept website** at `{slug}-website.html`.

## Business
- Name: {name}
- Category: {lead.category}
- City: {lead.city}
- Address: {lead.address or "—"}
- Phone: {lead.phone_primary}
- Rating: {lead.rating or "N/A"}★ ({lead.review_count or 0} Google reviews)
- Hours: {lead.opening_hours or "not listed"}

## Requirements
- Single self-contained `.html` — inline CSS/JS, no build step, no external deps
  except Google Fonts. Must open correctly via `file://`.
- Dark, modern aesthetic; smooth scroll; subtle scroll-reveal animation.
- Fully responsive (360px → 1440px).
- Sections: sticky nav, hero (name + city + rating), services (generic to
  {lead.category}), why-choose-us, hours + map link, contact CTA, footer.
- Click-to-call `tel:` and WhatsApp `wa.me` buttons using the real phone.
- Accessible: semantic landmarks, alt text, visible focus, AA contrast.
- Footer must read: "Concept by TKVibes — not affiliated with {name}".

## Hard constraints
- Invent **nothing** factual — no fake prices, staff, awards, or testimonials.
- Use only the rating/review numbers above.
- Placeholder imagery only (CSS gradients/shapes or inline SVG). No hotlinks.
"""


def deck_prompt_md(lead: Lead, slug: str) -> str:
    name = clean_name(lead.business_name)
    return f"""# Deck prompt — {name}

Build `{slug}-pitch-deck.html`: a self-contained HTML slide deck
(arrow-key + scroll navigation, one slide per viewport).

Slides:
1. **Cover** — "A better online presence for {name}" / TKVibes Digital Agency
2. **The gap** — {lead.rating or "N/A"}★, {lead.review_count or 0} reviews on Google,
   but {"an outdated web presence" if lead.website_url else "no website customers can find"}
3. **Concept** — embed/preview of `{slug}-website.html`
4. **Deliverables** — web design, brand identity, SEO, automation
5. **Proof** — 50+ projects, 98% satisfaction
6. **Offer** — free consultation · services@tkvibes.in · +91 98182 46938

Same dark premium styling as the website. Footer on every slide:
"Concept by TKVibes — not affiliated with {name}".
"""


def scaffold(lead: Lead, force: bool = False) -> tuple[str, bool]:
    slug = slugify(lead.business_name)
    d = os.path.join(CLIENTS_DIR, slug)
    existed = os.path.isdir(d)
    os.makedirs(d, exist_ok=True)

    info = classify_number(lead.phone_primary)
    wa = ""
    if info["valid"] and info["sms_capable"]:
        from .outreach.phone import wa_link, render, _has_real_site
        from .build_outreach import DEFAULT_TEMPLATE, HAS_SITE_TEMPLATE
        tpl = HAS_SITE_TEMPLATE if _has_real_site(lead) else DEFAULT_TEMPLATE
        wa = wa_link(info["e164"], render(tpl, lead))

    files = {
        "AGENTS.md": agents_md(lead, slug, wa),
        f"{slug}-prompt.md": prompt_md(lead, slug),
        f"{slug}-deck-prompt.md": deck_prompt_md(lead, slug),
        "spec.json": json.dumps(
            {"site": build_site_spec(lead), "deck": build_deck_spec(lead),
             "wa_link": wa, "slug": slug},
            indent=2, ensure_ascii=False, default=str),
    }
    for fname, content in files.items():
        p = os.path.join(d, fname)
        if os.path.exists(p) and not force:
            continue
        with open(p, "w", encoding="utf-8") as f:
            f.write(content)
    return d, existed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config.yaml")
    ap.add_argument("--tier", default=None)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    cfg = load_config(args.config)
    leads = _load_leads(cfg["handoff"]["export_json"])
    leads = [l for l in leads if not l.opt_out]
    if args.tier:
        leads = [l for l in leads if l.lead_tier == args.tier.upper()]
    leads.sort(key=lambda l: -l.lead_score)
    if not args.all:
        leads = leads[:args.limit or 5]

    print(f"scaffolding {len(leads)} client folders under {CLIENTS_DIR}")
    for l in leads:
        d, existed = scaffold(l, force=args.force)
        print(f"  {'~' if existed else '+'} {os.path.basename(d)}")
    print("\nNext: run the website/deck agents against each <slug>-prompt.md")


if __name__ == "__main__":
    main()
