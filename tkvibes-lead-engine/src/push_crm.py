"""Push leads to the TKVibes CRM webhook after each discovery run.

Improvements:
- Batched POST (single request for all leads, not per-lead)
- Idempotency key support (prevents duplicate processing)
- Trace ID propagation for log correlation
- Proper error handling with context
"""
import json
import uuid
import logging
from urllib.request import Request, urlopen
from urllib.error import URLError

from .log_config import get_logger

logger = get_logger(__name__)


def push_leads(leads: list, api_url: str, api_key: str, trace_id: str = "") -> dict:
    """POST a batch of leads to the CRM sync endpoint.

    Args:
        leads: List of Lead objects
        api_url: CRM base URL (e.g., "https://tkvibes.in/crm")
        api_key: CRM API key
        trace_id: Optional trace ID for log correlation (generated if not provided)

    Returns:
        Parsed JSON response from CRM, or error dict.
    """
    if not api_url or not api_key:
        logger.info("CRM API URL/KEY not set — skipping push")
        return {"status": "skipped", "reason": "not configured", "trace_id": trace_id}

    if not trace_id:
        from .log_config import get_trace_id
        trace_id = get_trace_id() or str(uuid.uuid4())

    idempotency_key = f"sync-{trace_id}-{uuid.uuid4().hex[:8]}"

    payload = json.dumps(
        {
            "key": api_key,
            "trace_id": trace_id,
            "idempotency_key": idempotency_key,
            "leads": [l.to_dict() for l in leads],
        },
        default=str,
    ).encode("utf-8")

    url = f"{api_url.rstrip('/')}/api/sync.php"
    req = Request(url, data=payload, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("X-Trace-ID", trace_id)

    logger.info("CRM push: sending %d leads (trace_id=%s, idempotency=%s...)",
                len(leads), trace_id, idempotency_key[:16])

    try:
        with urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode())
        logger.info("CRM push: %s (%d added, %d updated) trace_id=%s",
                     result.get("status", "ok"),
                     result.get("added", 0),
                     result.get("updated", 0),
                     trace_id)
        return result
    except URLError as e:
        logger.error("CRM push failed (trace_id=%s): %s", trace_id, e)
        return {"status": "error", "reason": str(e), "trace_id": trace_id}
    except json.JSONDecodeError as e:
        logger.error("CRM push: bad response (trace_id=%s): %s", trace_id, e)
        return {"status": "error", "reason": "unparseable response", "trace_id": trace_id}
