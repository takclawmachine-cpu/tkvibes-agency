# TKVibes Lead Engine

Autonomous B2B lead-generation agent for TKVibes Digital Agency.
Finds local businesses with no website (or a weak one), enriches + scores them,
and writes qualified leads to a Google Sheet — ready for the email outreach agent.

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium                          # only needed for scraping connectors
cp .env.example .env                                 # fill in API keys
python -m src.run                                    # -> leads land in Google Sheet
```

## What it does

1. **Discover** businesses via Google Places API (primary), IndiaMART/JustDial (opt-in scraping)
2. **Enrich** — normalize phones, classify website quality, detect socials
3. **Score** 0–100 based on website need, contactability, reputation, category fit
4. **Dedupe** — by phone, place_id, or fuzzy name+city match
5. **Filter** — DNC (Do-Not-Contact) list suppresses outreach
6. **Store** — upsert into Google Sheet (append-only, no duplicates)
7. **Export** — writes `data/leads_export.json` for the downstream email agent

## CLI options

```bash
python -m src.run                    # normal run
python -m src.run --dry-run          # discover + score, skip sheet write
python -m src.run --max-leads 20     # override config limit
python -m src.run --config other.yaml
```

## Scheduling

```bash
# cron — daily 7 AM IST (01:30 UTC)
30 1 * * * cd /path/to/tkvibes-lead-engine && .venv/bin/python -m src.run >> data/run.log 2>&1
```

## Email coverage

Google Places API **does not return email addresses** — there is no such field.
That is why the `email` column was empty for every lead.

The engine now fills it in two passes:

1. **`src/email_finder.py`** — crawls the lead's own website (homepage +
   `/contact`, `/about`, etc.), reading `mailto:` links, plain text, and
   obfuscated forms (`info [at] clinic dot com`). Ranks results: on-domain
   role addresses (`info@`, `contact@`) beat free-mail; junk/noreply dropped.
2. **`src/email_search.py`** — optional web-search fallback for leads with no
   website (`email_finder.search_fallback: true`).

### Reality check on coverage

The scoring model deliberately favours businesses **without** a website
(`website_quality: none` scores +45) — those are the best prospects. The
consequence: only ~2 of 50 current leads have a site to crawl, so
website-based discovery has a low ceiling here by design.

The search fallback is off by default because DuckDuckGo and Bing actively
block scraping (CAPTCHA / empty result markup) — it was measured returning
nothing. To get real coverage for website-less leads, plug a paid SERP API
(Serper.dev, SerpAPI, ScraperAPI) into `email_search._serp()`.

Every lead now carries a **`contact_channel`** field (`email` / `whatsapp` /
`phone` / `none`) so downstream outreach agents route correctly instead of
silently failing on a blank email. Most leads here are legitimately
**phone/WhatsApp-first** — that is a property of the target segment, not a bug.

### Backfill existing rows

```bash
python -m src.backfill_emails              # sheet + JSON
python -m src.backfill_emails --json-only
python -m src.backfill_emails --sheet-only
```

## Phone / WhatsApp outreach

Email coverage is ~2% (most leads have no website). **Phone coverage is 100%** —
47 of 50 leads are WhatsApp-reachable. Phone is the primary channel for this segment.

```bash
python -m src.build_outreach                 # mobiles only (default)
python -m src.build_outreach --tier HOT
python -m src.build_outreach --limit 20
python -m src.build_outreach --include-landline
python -m src.build_outreach --template-file my_msg.txt
```

Writes `data/outreach_queue.csv` + `.json`, sorted by lead score, each row
carrying a ready `wa.me` click-to-chat link with the message pre-filled.

Safety rules enforced in `src/outreach/phone.py`:
- `opt_out` leads and invalid numbers are dropped
- landlines excluded unless `--include-landline` (you can't SMS a landline)
- leads that already have a real website get a *redesign* angle, never the
  "couldn't find your website" line (checked against the live URL, not the
  possibly-stale `has_website` flag; social-only links don't count as a site)
- every template carries opt-out language

### Compliance — read before sending

**This tool does not auto-send.** It produces a reviewable queue, by design.

- **TRAI TCCCPA (India):** commercial SMS needs a DLT-registered header and a
  pre-approved template through an Indian aggregator (MSG91, Gupshup, Kaleyra).
  Raw-gateway marketing SMS is illegal and gets numbers blacklisted.
- **DND/NCPR:** scrub promotional traffic against the preference register.
- **WhatsApp:** business-initiated marketing requires the WhatsApp Business API
  with a Meta-approved template. Bulk-sending from the consumer app violates
  ToS and gets the number banned quickly.

The `wa.me` links are the compliant manual path: a human opens each chat and
presses send. For volume, wire an approved WABA/DLT provider.

Log opt-outs to `data/do_not_contact.csv` (`business_name,phone,opt_out`);
`apply_dnc()` honours it on every run.

## Sheet: contact_channel + wa_link columns

```bash
python -m src.push_wa_links --dry-run
python -m src.push_wa_links
```

Adds `contact_channel` and `wa_link` to the Leads sheet (creating the columns
if absent) and fills them per row. Opt-outs get `contact_channel=opt_out` and
no link. Leads with a real website get the *redesign* message; the rest get the
*no website* message. Batched at 200 cells per call to stay under API limits.

## Client project scaffolding

```bash
python -m src.scaffold_clients --tier HOT --limit 5
python -m src.scaffold_clients --all
python -m src.scaffold_clients --force      # overwrite existing briefs
```

Creates `~/Desktop/clients/<slug>/` matching the existing client layout:

```
<slug>/
  AGENTS.md                 # business brief + hard rules for the agent
  <slug>-prompt.md          # website build spec
  <slug>-deck-prompt.md     # pitch deck build spec
  spec.json                 # machine-readable site + deck spec + wa_link
  <slug>-website.html       # produced by the website agent
  <slug>-pitch-deck.html    # produced by the deck agent
```

Re-running never clobbers hand-edited files unless `--force` is passed.

Briefs pin the agents to the facts: real rating/review counts only, no invented
prices, staff, awards, or testimonials, and a mandatory
"Concept by TKVibes — not affiliated with <business>" footer on every asset.

## Agency location and targeting (updated)

**TKVibes is Delhi-based.** Outreach templates say "a web studio based in Delhi".
The lead's own city is a separate field - a Hyderabad clinic still gets addressed
about *their* city while we introduce ourselves as Delhi.

Targeting is now **pan-India**: 25 cities (Delhi NCR first, then tier-1 metros,
then tier-2) x 30 categories.

### Cost control - read before a full run

Places API is billed per request. Full scope is **25 x 30 = 750 queries** per run
(previously 210). Scope any run down with:

```bash
python -m src.run --cities "Delhi,Gurgaon,Noida" --categories "dental clinic"
python -m src.run --cities "Delhi"                  # 30 queries
python -m src.run                                   # 750 queries - full sweep
```

`run.py` prints the query count before hitting the API. `max_leads_per_run`
(now 150) caps what is *kept*, not what is *fetched* - it does not limit spend.

## notes column = the outreach message

`push_wa_links` writes the exact message to send into the `notes` column,
prefixed `MSG:`. Landline-only leads get a note too (as a call script) but no
`wa_link`. Re-running rewrites only the `MSG:` block, so hand-written notes in
the same cell survive and the message is never duplicated.
