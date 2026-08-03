"""Assign employees to leads based on region and/or country.

Strategy:
1. Apply country_assignments from config.yaml (if configured) — e.g. India->Jashmit, Canada->Tishya.
2. Fetch employee mapping from CRM API (if configured).
3. Fall back to config.yaml employees section.
4. For each lead: try country match first, then region match. Multi-match -> round-robin.
   No match -> leave assigned_employee blank (admin assigns manually).
"""

import os
import json
import logging
from collections import defaultdict
from urllib.request import Request, urlopen
from urllib.error import URLError

logger = logging.getLogger(__name__)


def fetch_mapping_from_crm(api_url: str, api_key: str) -> list[dict] | None:
    """Fetch employee mapping from the CRM API (includes regions + countries)."""
    if not api_url or not api_key:
        return None
    url = f"{api_url.rstrip('/')}/api/employees.php?key={api_key}"
    try:
        req = Request(url, headers={"Accept": "application/json"})
        with urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
        if isinstance(data, list):
            logger.info("Fetched employee mapping from CRM (%d employees)", len(data))
            return data
        return None
    except (URLError, json.JSONDecodeError, OSError) as e:
        logger.warning("CRM API unreachable (%s); falling back to config", e)
        return None


def assign_employees(leads: list, cfg: dict) -> list:
    """Assign employees to leads in-place, return the list for chaining.

    Priority:
      1. ``crm.country_assignments`` dict in config.yaml (e.g. {"India": "Jashmit Bhalla"}).
      2. Employee mapping from CRM API or config fallback (country match, then region match).
      3. Unassigned if no match at any level.

    ``cfg`` may contain a ``crm`` section with:
        crm.country_assignments   -- dict {country: employee_name}
        crm.api_url, crm.api_key  -- CRM API endpoint
        crm.employees             -- fallback list of {name, regions} dicts
    """
    crm_cfg = cfg.get("crm", {}) or {}
    country_assignments = crm_cfg.get("country_assignments", {}) or {}
    api_url = crm_cfg.get("api_url", "")
    api_key = crm_cfg.get("api_key", "")
    fallback_employees = crm_cfg.get("employees", []) or []

    # 1. Apply country_assignments from config (simple, always works)
    if country_assignments:
        assigned = 0
        for lead in leads:
            c = (lead.country or "").strip()
            if c in country_assignments:
                lead.assigned_employee = country_assignments[c]
                assigned += 1
        logger.info("Country assignments applied: %d leads assigned", assigned)

    # 2. For remaining unassigned leads, try CRM/fallback mapping
    unassigned = [l for l in leads if not l.assigned_employee]
    if not unassigned:
        return leads

    employees = fetch_mapping_from_crm(api_url, api_key)
    if employees is None:
        employees = fallback_employees
        if fallback_employees:
            logger.info("Using config-based employee mapping (%d employees)", len(employees))

    if not employees:
        return leads

    # Build country -> employee index
    country_to_emps: dict[str, list[str]] = defaultdict(list)
    for emp in employees:
        name = emp.get("name", "") or emp.get("email", "").split("@")[0]
        countries = emp.get("countries", []) or []
        if isinstance(countries, str):
            countries = [c.strip() for c in countries.split(",") if c.strip()]
        for c in countries:
            country_to_emps[c.strip().lower()].append(name)

    # Build region -> employee index
    region_to_emps: dict[str, list[str]] = defaultdict(list)
    for emp in employees:
        name = emp.get("name", "") or emp.get("email", "").split("@")[0]
        regions = emp.get("regions", []) or []
        if isinstance(regions, str):
            regions = [r.strip() for r in regions.split(",") if r.strip()]
        for r in regions:
            region_to_emps[r.strip().lower()].append(name)

    # Round-robin counters
    country_counters: dict[str, int] = defaultdict(int)
    region_counters: dict[str, int] = defaultdict(int)

    for lead in unassigned:
        country_key = (lead.country or "").strip().lower()
        region_key = (lead.region or "").strip().lower()

        # Try country match first
        names = country_to_emps.get(country_key, [])
        if names:
            idx = country_counters[country_key] % len(names)
            country_counters[country_key] += 1
            lead.assigned_employee = names[idx]
            continue

        # Try region match
        names = region_to_emps.get(region_key, [])
        if names:
            idx = region_counters[region_key] % len(names)
            region_counters[region_key] += 1
            lead.assigned_employee = names[idx]
            continue

        lead.assigned_employee = ""

    return leads