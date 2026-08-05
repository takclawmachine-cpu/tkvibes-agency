"""TKVibes Lead Engine — Main Discovery Pipeline Orchestrator.

Runs:
1. Discovery via Google Places API
2. Enrichment (phone normalization, website classification)
3. Scoring (points-based tiering)
4. Deduplication + DNC filtering
5. CRM field application (region, pain points, pitch, employee assignment)
6. Export to JSON for downstream agents
7. Push to CRM database (transactional)

Usage:
    python -m src.run --max-leads 40
    python -m src.run --cities Delhi --categories "dental clinic"
    python -m src.run --dry-run
"""
import os
import json
import uuid
import argparse

from dotenv import load_dotenv

from .log_config import get_logger, configure_logging, set_trace_id, get_trace_id
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


def process_leads(leads: list[Lead], cfg: dict, distribute: bool = True) -> list[Lead]:
    """Enrich, score, finalize, dedupe, DNC-filter a batch of leads.
    
    If distribute=True (default), leads are distributed equally across
    category_groups defined in config.yaml scoring section.
    """
    excluded = set((cfg.get("scoring", {}) or {}).get("excluded_categories", []))
    excluded_lower = {c.lower() for c in excluded}
    
    for l in leads:
        enrich(l)
        score_lead(l, cfg["scoring"]["high_fit_categories"])
        l.finalize_dates(cfg["run"]["cache_stale_days"])
        if not cfg["run"]["collect_personal_data"]:
            l.owner_name = ""

    leads = dedupe(leads)
    
    # Filter out excluded categories (dental, real estate, shopify, etc.)
    if excluded_lower:
        filtered = [l for l in leads 
                    if not any(ex in (l.category or "").lower() for ex in excluded_lower)]
        removed = len(leads) - len(filtered)
        if removed > 0:
            logger.info("Filtered out %d leads from excluded categories", removed)
        leads = filtered
    
    leads = apply_dnc(leads)
    leads.sort(key=lambda x: (TIER_RANK.get(x.lead_tier, 9), -x.lead_score))
    
    # Distribute leads equally across category groups
    groups = (cfg.get("scoring", {}) or {}).get("category_groups", {})
    if distribute and groups:
        leads = _distribute_across_groups(leads, groups)
    
    # Run email finder on the final set of leads
    ef = cfg.get("email_finder", {}) or {}
    if ef.get("enabled"):
        leads = find_emails(leads, ef)
    return leads


def _distribute_across_groups(leads: list[Lead], groups: dict) -> list[Lead]:
    """Distribute leads equally across category groups.
    
    For each group (legal, medical, veterinary, services), takes an equal
    share of the total leads, then interleaves them for diversity.
    """
    # Build reverse lookup: category -> group_name
    cat_to_group = {}
    for gname, cats in groups.items():
        for c in cats:
            cat_to_group[c.lower()] = gname
    
    group_leads: dict[str, list[Lead]] = {g: [] for g in groups}
    ungrouped: list[Lead] = []
    
    for l in leads:
        cat_lower = (l.category or "").lower()
        matched_group = None
        for gname, cats in groups.items():
            for c in cats:
                if c.lower() in cat_lower or cat_lower in c.lower():
                    matched_group = gname
                    break
            if matched_group:
                break
        if matched_group:
            group_leads[matched_group].append(l)
        else:
            ungrouped.append(l)
    
    # Calculate per-group target
    n_groups = len(groups)
    per_group_target = max(1, len(leads) // n_groups) if leads else 0
    
    # Take per_group_target from each group, then add remaining
    result: list[Lead] = []
    remaining: list[Lead] = []
    
    for gname, group_list in group_leads.items():
        group_list.sort(key=lambda x: (TIER_RANK.get(x.lead_tier, 9), -x.lead_score))
        taken = group_list[:per_group_target]
        leftover = group_list[per_group_target:]
        result.extend(taken)
        remaining.extend(leftover)
    
    # Add ungrouped leads and leftovers
    remaining.extend(ungrouped)
    remaining.sort(key=lambda x: (TIER_RANK.get(x.lead_tier, 9), -x.lead_score))
    result.extend(remaining)
    
    # Interleave for diversity (HOT first, then WARM, then COLD)
    result.sort(key=lambda x: (TIER_RANK.get(x.lead_tier, 9), -x.lead_score))
    
    # Log distribution
    for gname, group_list in group_leads.items():
        logger.info("[distribution] %s group: %d leads", gname, len(group_list))
    logger.info("[distribution] ungrouped: %d leads", len(ungrouped))
    logger.info("[distribution] total distributed: %d leads", len(result))
    
    return result


COUNTRY_CODES = {
    "India": "+91",
    "Canada": "+1",
}


def apply_crm_fields(leads: list[Lead], cfg: dict) -> list[Lead]:
    """Resolve region/country, generate pain points, pitch, and assign employees."""
    for l in leads:
        region, country = resolve_region(l.city)
        l.region = region
        l.country = country
        l.pain_points = build_pain_points(l)
        l.recommended_pitch = recommend_pitch(l)

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
    """Write a JSON file that the downstream email/proposal agent reads."""
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
    logger.info("Handoff JSON written: %s (%d leads)", export_path, len(payload))
    return export_path


def _tier_set(min_tier: str) -> set:
    # HOT=0, WARM=1, COLD=2 — "min_tier" means include that tier and BETTER
    order = ["HOT", "WARM", "COLD"]
    idx = order.index(min_tier) if min_tier in order else 0
    return set(order[:idx + 1])


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
    parser.add_argument("--no-distribute", action="store_true",
                        help="Disable equal category distribution (use scoring-only order)")
    args = parser.parse_args()

    load_dotenv()
    cfg = load_config(args.config)

    # Configure structured logging with CRM error forwarding + trace_id
    trace_id = set_trace_id()
    crm_cfg = cfg.get("crm", {}) or {}
    configure_logging(
        level="INFO",
        crm_url=crm_cfg.get("api_url", ""),
        crm_key=crm_cfg.get("api_key", ""),
    )
    logger.info("Lead engine started", extra={
        "event": "pipeline_start",
        "trace_id": trace_id,
        "max_leads": args.max_leads or cfg["run"]["max_leads_per_run"],
        "cities": len(cfg["targets"]["cities"]),
        "categories": len(cfg["targets"]["categories"]),
    })

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
    logger.info("Config: %d cities x %d categories = up to %d Places queries",
                len(cfg["targets"]["cities"]), len(cfg["targets"]["categories"]), nq)

    # ── Phase 1: Discovery ───────────────────────────────────────────────
    # Remove excluded categories from config targets before discovery
    # (dental, real estate, shopify, saas, massage, med spa, home services, etc.)
    scoring_cfg = cfg.get("scoring", {}) or {}
    excluded = scoring_cfg.get("excluded_categories", [])
    if excluded:
        orig_cats = cfg["targets"]["categories"]
        excluded_lower = {c.lower() for c in excluded}
        cfg["targets"]["categories"] = [c for c in orig_cats
                                        if not any(ex in c.lower() for ex in excluded_lower)]
        removed = len(orig_cats) - len(cfg["targets"]["categories"])
        if removed > 0:
            logger.info("Removed %d excluded categories from discovery: %s", removed, excluded)
    raw = discover_all(cfg, per_country_target=per_country)
    logger.info("Discovery complete: %d raw leads (trace_id=%s)", len(raw), trace_id)

    # ── Phase 2: Process ─────────────────────────────────────────────────
    if args.no_distribute:
        leads = process_leads(raw, cfg, distribute=False)
    else:
        leads = process_leads(raw, cfg, distribute=True)
    hot = sum(1 for l in leads if l.lead_tier == "HOT")
    warm = sum(1 for l in leads if l.lead_tier == "WARM")
    cold = sum(1 for l in leads if l.lead_tier == "COLD")
    logger.info("Processing complete: %d unique leads - %d HOT / %d WARM / %d COLD",
                len(leads), hot, warm, cold)

    leads = leads[:max_leads]
    logger.info("Capped to %d leads for this run", len(leads))

    # ── Phase 3: CRM Enrichment ──────────────────────────────────────────
    leads = apply_crm_fields(leads, cfg)
    logger.info("CRM fields applied: region/country, pain points, pitch, employee assignment")

    # ── Phase 4: Export ──────────────────────────────────────────────────
    export_path = export_for_handoff(leads, cfg)

    # ── Phase 5: CRM Push (before sheet write — fail fast) ───────────────
    crm_ok = True
    if not args.no_crm_push and not args.dry_run:
        crm_result = push_leads(leads, crm_cfg.get("api_url", ""), crm_cfg.get("api_key", ""))
        status = crm_result.get("status", "unknown")
        if status == "error":
            logger.error("CRM push returned error: %s", crm_result.get("reason", "unknown"))
            crm_ok = False
        else:
            added = crm_result.get("added", 0)
            updated = crm_result.get("updated", 0)
            logger.info("CRM push: %s (%d added, %d updated) trace_id=%s",
                        status, added, updated, trace_id)

    # ── Phase 6: Sheet Write (only if CRM push succeeded) ────────────────
    if args.dry_run:
        logger.info("Dry-run mode — skipping Google Sheets write")
    else:
        if not crm_ok:
            logger.warning("Skipping sheet write because CRM push failed")
        else:
            sa_path = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON", "")
            sheet_id = os.environ.get("GOOGLE_SHEETS_ID", "")
            if not sa_path or not sheet_id:
                logger.info("GOOGLE_SERVICE_ACCOUNT_JSON or GOOGLE_SHEETS_ID not set — skipping sheet write")
            else:
                writer = SheetWriter(sa_path, sheet_id, cfg["sheets"]["worksheet_name"])
                master_added = writer.upsert(leads)
                logger.info("Master tab: %d new leads upserted", master_added)

                from datetime import datetime as _dt
                job_sheet = _dt.now().strftime("%Y-%m-%d %H-%M-%S")
                added = writer.write_job(leads, job_sheet)
                logger.info("Job tab '%s': wrote %d leads", job_sheet, added)

    logger.info("Pipeline complete | %d leads processed | %d HOT | trace_id=%s",
                len(leads), hot, trace_id)


if __name__ == "__main__":
    main()
