import os
import json
import argparse
from dotenv import load_dotenv

from .log_config import get_logger
from .config import load_config

logger = get_logger(__name__)
from .connectors.google_places import GooglePlacesConnector
from .enrich import enrich
from .score import score_lead
from .dedupe import dedupe, apply_dnc
from .sheets import SheetWriter
from .models import Lead
from .handoff.sample_site import build_site_spec
from .handoff.pitch_deck import build_deck_spec
from .regions import resolve as resolve_region
from .pain_points import build_pain_points, recommend_pitch
from .assign import assign_employees
from .push_crm import push_leads

TIER_RANK = {"HOT": 0, "WARM": 1, "COLD": 2}


def discover_all(cfg: dict, per_country_target: int = 20) -> list[Lead]:
    """Run all enabled connectors grouped by country and return raw leads.

    Cities are split by country, and each country is discovered independently
    up to ``per_country_target``. This guarantees geographic diversity instead
    of letting one country's cities (e.g. India) drown out another (e.g. Canada).
    """
    from .regions import resolve as resolve_region

    # Group config cities by country
    country_cities: dict[str, list[str]] = {}
    for city in cfg["targets"]["cities"]:
        _, country = resolve_region(city)
        country_cities.setdefault(country, []).append(city)

    all_leads: list[Lead] = []

    def enough(country_leads: list[Lead]) -> bool:
        return per_country_target > 0 and len(country_leads) >= per_country_target

    if cfg["sources"]["google_places"]:
        api_key = os.environ.get("GOOGLE_MAPS_API_KEY", "")
        if not api_key:
            logger.warning("GOOGLE_MAPS_API_KEY not set - skipping Google Places")
        else:
            gp = GooglePlacesConnector(api_key)
            for country in sorted(country_cities):  # deterministic order
                country_pool: list[Lead] = []
                logger.info("── [%s] ──", country)
                for cat in cfg["targets"]["categories"]:
                    if enough(country_pool):
                        break
                    for city in country_cities[country]:
                        if enough(country_pool):
                            break
                        logger.info("[google_places] %s / %s", city, cat)
                        try:
                            country_pool += gp.discover(
                                city, cat, cfg["targets"]["max_results_per_query"]
                            )
                        except Exception as e:
                            logger.error("[google_places] error: %s", e)
                all_leads += country_pool
                logger.info("[%s] %d raw leads", country, len(country_pool))

    if cfg["sources"].get("indiamart"):
        from .connectors.indiamart import IndiaMartConnector
        im = IndiaMartConnector(**cfg["rate_limits"])
        for city in cfg["targets"]["cities"]:
            if enough():
                break
            for cat in cfg["targets"]["categories"]:
                if enough():
                    break
                logger.info("[indiamart] %s / %s", city, cat)
                try:
                    all_leads += im.discover(city, cat)
                except Exception as e:
                    logger.error("[indiamart] error: %s", e)

    if cfg["sources"].get("justdial"):
        from .connectors.justdial import JustDialConnector
        jd = JustDialConnector(**cfg["rate_limits"])
        for city in cfg["targets"]["cities"]:
            if enough():
                break
            for cat in cfg["targets"]["categories"]:
                if enough():
                    break
                logger.info("[justdial] %s / %s", city, cat)
                try:
                    all_leads += jd.discover(city, cat)
                except Exception as e:
                    logger.error("[justdial] error: %s", e)

    return all_leads


def process_leads(leads: list[Lead], cfg: dict) -> list[Lead]:
    """Enrich, score, finalize, dedupe, DNC-filter a batch of leads."""
    for l in leads:
        enrich(l)
        score_lead(l, cfg["scoring"]["high_fit_categories"])
        l.finalize_dates(cfg["run"]["cache_stale_days"])
        if not cfg["run"]["collect_personal_data"]:
            l.owner_name = ""

    leads = dedupe(leads)
    leads = apply_dnc(leads)
    leads.sort(key=lambda x: (TIER_RANK.get(x.lead_tier, 9), -x.lead_score))

    ef = cfg.get("email_finder", {}) or {}
    if ef.get("enabled"):
        leads = find_emails(leads, ef)
    return leads


COUNTRY_CODES = {
    "India": "+91",
    "Canada": "+1",
}


def _filter_phone_country(leads: list[Lead]) -> list[Lead]:
    """Pass through all leads — no phone/country rejection."""
    return leads


def apply_crm_fields(leads: list[Lead], cfg: dict) -> list[Lead]:
    """Resolve region/country, generate pain points, pitch, and assign employees."""
    for l in leads:
        region, country = resolve_region(l.city)
        l.region = region
        l.country = country
        l.pain_points = build_pain_points(l)
        l.recommended_pitch = recommend_pitch(l)

    leads = _filter_phone_country(leads)
    assign_employees(leads, cfg)
    return leads


def find_emails(leads: list[Lead], ef: dict) -> list[Lead]:
    """Crawl lead websites to populate the email field (Places API has none)."""
    from .email_finder import enrich_email

    tier_set = _tier_set(ef.get("min_tier", "WARM"))
    delay = ef.get("per_site_delay_seconds", 0.8)
    targets = [l for l in leads
               if l.lead_tier in tier_set and l.website_url and not l.email]
    logger.info("[email_finder] crawling %d sites for contact emails", len(targets))
    found = 0
    for i, l in enumerate(targets, 1):
        enrich_email(l, delay=delay)
        if l.email:
            found += 1
            logger.info("[%d/%d] %s: %s", i, len(targets), l.business_name, l.email)
    no_site = sum(1 for l in leads if l.lead_tier in tier_set and not l.website_url)
    logger.info("[email_finder] %d/%d emails found (%d leads have no website at all)",
                found, len(targets), no_site)

    if ef.get("search_fallback"):
        from .email_search import enrich_email_via_search
        sd = ef.get("search_delay_seconds", 3.0)
        rest = [l for l in leads if l.lead_tier in tier_set and not l.email]
        logger.info("[email_finder] web-search fallback on %d leads", len(rest))
        for l in rest:
            enrich_email_via_search(l, delay=sd)
            if l.email:
                found += 1
                logger.info("(search) %s: %s", l.business_name, l.email)

    # Tell downstream agents which channel is actually usable
    for l in leads:
        l.contact_channel = ("email" if l.email
                             else "whatsapp" if l.whatsapp
                             else "phone" if l.phone_primary
                             else "none")

    emailable = sum(1 for l in leads if l.email)
    logger.info("[email_finder] %d/%d leads are email-reachable", emailable, len(leads))
    return leads


def export_for_handoff(leads: list[Lead], cfg: dict) -> str:
    """Write a JSON file that the downstream email agent reads."""
    export_path = cfg["handoff"]["export_json"]
    min_tier = cfg["handoff"]["min_tier"]
    tier_set = _tier_set(min_tier)

    payload = []
    for l in leads:
        if l.lead_tier not in tier_set:
            continue
        if l.opt_out:
            continue
        entry = l.to_dict()
        entry["_site_spec"] = build_site_spec(l)
        entry["_deck_spec"] = build_deck_spec(l)
        payload.append(entry)

    os.makedirs(os.path.dirname(export_path), exist_ok=True)
    with open(export_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False, default=str)
    return export_path


def _tier_set(min_tier: str) -> set:
    # HOT=0, WARM=1, COLD=2 — "min_tier" means include that tier and BETTER
    order = ["HOT", "WARM", "COLD"]
    idx = order.index(min_tier) if min_tier in order else 0
    return set(order[:idx+1])


def main():
    parser = argparse.ArgumentParser(description="TKVibes Lead Engine")
    parser.add_argument("--config", default="config.yaml")
    parser.add_argument("--max-leads", type=int, default=None)
    parser.add_argument("--cities", default=None,
                        help="comma-separated subset, e.g. 'Delhi,Gurgaon' "
                             "(limits Places spend)")
    parser.add_argument("--categories", default=None,
                        help="comma-separated subset of categories")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-crm-push", action="store_true",
                        help="Skip pushing leads to CRM after run")
    args = parser.parse_args()

    load_dotenv()
    cfg = load_config(args.config)

    # Configure structured logging with CRM error forwarding
    from .log_config import configure_logging
    crm_cfg = cfg.get("crm", {}) or {}
    configure_logging(
        level="INFO",
        crm_url=crm_cfg.get("api_url", ""),
        crm_key=crm_cfg.get("api_key", ""),
    )

    if args.cities:
        want = [c.strip().lower() for c in args.cities.split(",") if c.strip()]
    cfg["targets"]["cities"] = [c for c in cfg["targets"]["cities"]
                                    if c.lower() in want] or want
    if args.categories:
        want = [c.strip().lower() for c in args.categories.split(",") if c.strip()]
        cfg["targets"]["categories"] = [c for c in cfg["targets"]["categories"]
                                        if c.lower() in want] or want

    max_leads = args.max_leads or cfg["run"]["max_leads_per_run"]

    # Per-country discovery target — collect 3x so all categories get sampled,
    # then cap at max_leads in process_leads
    employees = len(cfg.get("crm", {}).get("country_assignments", {}) or {})
    per_country = max_leads * 3

    nq = len(cfg["targets"]["cities"]) * len(cfg["targets"]["categories"])
    print(f"TKVibes Lead Engine - target: {max_leads} leads this job")
    print(f"   {len(cfg['targets']['cities'])} cities x "
          f"{len(cfg['targets']['categories'])} categories = up to {nq} Places queries")
    raw = discover_all(cfg, per_country_target=per_country)
    print(f"   discovered {len(raw)} raw leads")

    leads = process_leads(raw, cfg)
    hot = sum(1 for l in leads if l.lead_tier == "HOT")
    warm = sum(1 for l in leads if l.lead_tier == "WARM")
    cold = sum(1 for l in leads if l.lead_tier == "COLD")
    print(f"   after dedupe/score: {len(leads)} unique - {hot} HOT / {warm} WARM / {cold} COLD")

    leads = leads[:max_leads]
    print(f"   capped to {len(leads)} leads for this run")

    # ── CRM enrichment ───────────────────────────────────────────────────────
    leads = apply_crm_fields(leads, cfg)
    print(f"   CRM fields applied: region/country, pain points, pitch, employee assignment")

    export_path = export_for_handoff(leads, cfg)
    print(f"   handoff JSON -> {export_path} ({len(leads)} leads)")

    # ── CRM push (before sheet write — fail fast) ────────────────────────────
    crm_ok = True
    if not args.no_crm_push and not args.dry_run:
        crm_cfg = cfg.get("crm", {}) or {}
        crm_result = push_leads(leads, crm_cfg.get("api_url", ""), crm_cfg.get("api_key", ""))
        status = crm_result.get("status", "unknown")
        if status == "error":
            print(f"   ⚠️  CRM push returned error: {crm_result.get('reason', 'unknown')}")
            crm_ok = False
        else:
            added = crm_result.get("added", 0)
            updated = crm_result.get("updated", 0)
            print(f"   CRM push: {status} ({added} added, {updated} updated)")

    # ── Sheet write (only if CRM push succeeded or not configured) ────────────
    if args.dry_run:
        print("   (dry-run - skipping Google Sheets write)")
        master_added = 0
        added = 0
    else:
        if not crm_ok:
            print("   ⚠️  Skipping sheet write because CRM push failed")
            master_added = 0
            added = 0
        else:
            sa_path = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON", "")
            sheet_id = os.environ.get("GOOGLE_SHEETS_ID", "")
            if not sa_path or not sheet_id:
                print("   GOOGLE_SERVICE_ACCOUNT_JSON or GOOGLE_SHEETS_ID not set - skipping sheet write")
                added = 0
            else:
                writer = SheetWriter(sa_path, sheet_id, cfg["sheets"]["worksheet_name"])

                # 1. Upsert to master "Leads" tab (with CRM fields)
                master_added = writer.upsert(leads)
                print(f"   Master tab: {master_added} new leads upserted")

                # 2. One fresh worksheet per job, named by date-time stamp
                from datetime import datetime as _dt
                job_sheet = _dt.now().strftime("%Y-%m-%d %H-%M-%S")
                added = writer.write_job(leads, job_sheet)
                print(f"   Job tab '{job_sheet}': wrote {added} leads")

    print(f"\nDone - {len(leads)} leads processed | {master_added} new sheet rows | {hot} HOT")
    print(f"   Handoff JSON: {export_path}")


if __name__ == "__main__":
    main()