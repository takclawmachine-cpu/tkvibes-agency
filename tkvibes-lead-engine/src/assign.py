"""Assign employees to leads based on region.

Strategy:
1. Fetch employee→region mapping from CRM API (if configured).
2. Fall back to config.yaml employees section.
3. For each lead, find employees covering its region. Multi-match → round-robin.
   No match → leave assigned_employee blank (admin assigns manually).
"""

import os
import json
import logging
from collections import defaultdict
from urllib.request import Request, urlopen
from urllib.error import URLError

logger = logging.getLogger(__name__)


def fetch_mapping_from_crm(api_url: str, api_key: str) -> list[dict] | None:
    """Fetch employee→region mapping from the CRM API."""
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

    ``cfg`` may contain a ``crm`` section with:
        crm.api_url, crm.api_key  — CRM API endpoint
        crm.employees             — fallback list of {name, regions} dicts
    """
    crm_cfg = cfg.get("crm", {}) or {}
    api_url = crm_cfg.get("api_url", "")
    api_key = crm_cfg.get("api_key", "")
    fallback_employees = crm_cfg.get("employees", []) or []

    # 1. Try CRM API
    employees = fetch_mapping_from_crm(api_url, api_key)
    if employees is None:
        # 2. Fallback: config.yaml
        employees = fallback_employees
        logger.info("Using config-based employee mapping (%d employees)", len(employees))

    if not employees:
        logger.info("No employee mapping configured — skipping assignment")
        for lead in leads:
            lead.assigned_employee = ""
        return leads

    # Build region → employee index
    region_to_emps: dict[str, list[str]] = defaultdict(list)
    for emp in employees:
        name = emp.get("name", "") or emp.get("email", "").split("@")[0]
        regions = emp.get("regions", []) or []
        if isinstance(regions, str):
            regions = [r.strip() for r in regions.split(",") if r.strip()]
        for r in regions:
            region_to_emps[r.strip().lower()].append(name)

    # Round-robin counters per region
    counters: dict[str, int] = defaultdict(int)

    for lead in leads:
        region_key = (lead.region or "").strip().lower()
        names = region_to_emps.get(region_key, [])
        if not names:
            lead.assigned_employee = ""
            continue
        idx = counters[region_key] % len(names)
        counters[region_key] += 1
        lead.assigned_employee = names[idx]

    return leads