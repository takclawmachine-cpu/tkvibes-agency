"""Push leads to the TKVibes CRM webhook after each discovery run."""

import os
import json
import logging
from urllib.request import Request, urlopen
from urllib.error import URLError

logger = logging.getLogger(__name__)


def push_leads(leads: list, api_url: str, api_key: str) -> dict:
    """POST a batch of leads to the CRM sync endpoint.

    Returns the parsed JSON response on success, or raises on failure.
    """
    if not api_url or not api_key:
        logger.info("CRM API URL/KEY not set — skipping push")
        return {"status": "skipped", "reason": "not configured"}

    payload = json.dumps(
        {"key": api_key, "leads": [l.to_dict() for l in leads]},
        default=str,
    ).encode("utf-8")

    url = f"{api_url.rstrip('/')}/api/sync.php"
    req = Request(url, data=payload, method="POST")
    req.add_header("Content-Type", "application/json")

    try:
        with urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode())
        logger.info("CRM push: %s (%d leads)", result.get("status", "ok"), len(leads))
        return result
    except URLError as e:
        logger.warning("CRM push failed: %s", e)
        return {"status": "error", "reason": str(e)}
    except json.JSONDecodeError as e:
        logger.warning("CRM push: bad response: %s", e)
        return {"status": "error", "reason": "unparseable response"}