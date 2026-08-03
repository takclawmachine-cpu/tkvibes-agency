# Lead Engine — Deep Reference

## Architecture
`tkvibes-lead-engine/` — Python 3.11, venv at `.venv/`

```
src/
├── run.py              # Main entry: discover → enrich → score → dedupe → sheet → CRM
├── config.py           # Loads config.yaml
├── models.py           # Lead dataclass
├── connectors/         # Google Places (primary), IndiaMart, JustDial (opt-in)
├── enrich.py           # Normalize phones, classify website quality, detect socials
├── score.py            # Multi-factor score 0-100
├── dedupe.py           # By phone, place_id, fuzzy name+city
├── sheets.py           # Google Sheets writer (upsert)
├── email_finder.py     # Crawl website for mailto: links
├── email_search.py     # Web search fallback (disabled — DuckDuckGo blocks)
├── pain_points.py      # Build pitch per category + website quality
├── assign.py           # Employee→region round-robin
├── push_crm.py         # Webhook POST to CRM
├── push_proposals.py   # Upload proposal files to CRM
├── push_wa_links.py    # Push wa.me links + MSG templates to sheet
├── build_outreach.py   # Build outreach queue CSV/JSON
├── scaffold_clients.py # Generate client briefs in ~/Desktop/clients/
├── regions.py          # Resolve city→region mapping
├── handoff/            # Site spec + deck spec builders
│   ├── sample_site.py
│   └── pitch_deck.py
└── outreach/           # Phone/WhatsApp outreach logic
```

## Key Config (`config.yaml`)

| Section | Key Settings |
|---------|-------------|
| `run` | `collect_personal_data: false`, `max_leads_per_run: 20` |
| `sources` | `google_places: true`, others false |
| `targets.cities` | 25 India + 25 Canada (see `regions.py`) |
| `targets.categories` | 30 categories (medical, legal, service) |
| `scoring` | `hot_threshold: 70`, `warm_threshold: 45` |
| `crm` | `api_url: https://tkvibes.in/crm`, `api_key: ***` |
| `email_finder` | `enabled: true`, `search_fallback: false` |

## Deployment
- NOT deployed to Hostinger — runs locally from `~/Desktop/tkvibes-agency/tkvibes-lead-engine/`
- Sheet: `1cZ7w4HlN5aGaSAY-m-9EPexqEaCVC52kRELPk1OGiXc`
- Webhook: `POST /crm/api/sync.php?key=***` pushes leads to CRM

## Scoring Logic
- No website: +45, Bad website: +25, Basic: +10, Good: 0
- High-fit category: +20
- Rating > 4.0: +10, > 4.5: +15
- Reviews > 10: +5, > 50: +10
- Phone present: +10, Email found: +15

## Business Rules
- **Email coverage is ~2%** (most leads have no website; Google Places doesn't return email)
- **Phone coverage is 100%** — WhatsApp is primary channel
- **DNC list** at `data/do_not_contact.csv` — applied on every run
- **Landlines excluded** from outreach (no SMS) unless `--include-landline`