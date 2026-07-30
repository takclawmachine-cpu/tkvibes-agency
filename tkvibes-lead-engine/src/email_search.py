"""Search-engine fallback for finding lead emails.

Most leads from Google Places have NO website (that's why they're leads),
so website crawling alone finds nothing for them. This module searches the
open web for "<business> <city> email" and:

  1. reads emails straight out of the SERP snippets
  2. follows the top organic results that are fetchable (many business
     directories return 403 to bots — those are skipped, not faked)
  3. extracts emails from those pages

Coverage is genuinely partial. Businesses without a web presence often have
no discoverable email; those are reported as not-found so downstream agents
fall back to phone/WhatsApp outreach.
"""

from __future__ import annotations

import re
import time
import urllib.parse

import httpx

from .email_finder import _clean, _is_junk, _score, EMAIL_RE, OBFUSCATED_RE, UA

DDG_HTML = "https://html.duckduckgo.com/html/"

# Directories that reliably block bots — don't waste requests
BLOCKED_HOSTS = (
    "justdial.com", "sulekha.com", "indiamart.com", "healthdial.com",
    "searchlistinghub.com", "practo.com", "facebook.com", "instagram.com",
    "linkedin.com", "yelp.com", "tripadvisor.com",
)


def _serp(query: str, timeout: float = 20.0) -> tuple[str, list[str]]:
    """Return (raw_html, organic_links) from DuckDuckGo HTML endpoint."""
    headers = {"User-Agent": UA}
    r = httpx.post(DDG_HTML, data={"q": query}, headers=headers,
                   timeout=timeout, follow_redirects=True)
    r.raise_for_status()
    html = r.text
    links = []
    for raw in re.findall(r'class="result__a"[^>]*href="([^"]+)"', html):
        if "uddg=" in raw:
            raw = urllib.parse.unquote(raw.split("uddg=")[1].split("&")[0])
        if raw.startswith("http") and not any(b in raw for b in BLOCKED_HOSTS):
            if raw not in links:
                links.append(raw)
    return html, links


# The search engines' own addresses / infra noise must never become a lead email
ENGINE_DOMAINS = (
    "duckduckgo.com", "google.com", "bing.com", "yahoo.com/help",
    "mozilla.org", "w3.org", "gstatic.com", "googleapis.com",
)


def _emails_from_text(text: str) -> set[str]:
    found = {_clean(m.group(0)) for m in EMAIL_RE.finditer(text)}
    for m in OBFUSCATED_RE.finditer(text):
        found.add(_clean(f"{m.group(1)}@{m.group(2)}.{m.group(3)}"))
    return {
        a for a in found
        if a and not _is_junk(a)
        and not any(d in a for d in ENGINE_DOMAINS)
    }


def _is_error_page(html: str) -> bool:
    """Detect DDG rate-limit / error responses so we back off instead of
    treating the error page as a result."""
    low = html[:4000].lower()
    return ("error-lite@duckduckgo" in low
            or "anomaly" in low and "traffic" in low
            or len(html) < 1200)


def search_email(
    business_name: str,
    city: str = "",
    delay: float = 1.5,
    max_pages: int = 3,
    timeout: float = 15.0,
) -> list[str]:
    """Find candidate emails for a business via web search. Best first."""
    if not business_name:
        return []

    candidates: set[str] = set()
    queries = [
        f'"{business_name}" {city} email',
        f'"{business_name}" {city} contact email address',
    ]

    headers = {"User-Agent": UA, "Accept": "text/html,*/*"}
    visited: set[str] = set()

    with httpx.Client(timeout=timeout, follow_redirects=True,
                      headers=headers) as client:
        for q in queries:
            try:
                html, links = _serp(q, timeout=timeout)
            except Exception:
                continue

            if _is_error_page(html):
                # rate-limited: back off hard, retry this query once
                time.sleep(delay * 6)
                try:
                    html, links = _serp(q, timeout=timeout)
                except Exception:
                    continue
                if _is_error_page(html):
                    continue

            # 1. emails visible right in the SERP snippets
            candidates |= _emails_from_text(html)
            if candidates:
                break

            # 2. follow fetchable organic results
            for url in links[:max_pages]:
                if url in visited:
                    continue
                visited.add(url)
                try:
                    r = client.get(url)
                    if r.status_code != 200:
                        continue
                    if "html" not in r.headers.get("content-type", "").lower():
                        continue
                    candidates |= _emails_from_text(r.text)
                except Exception:
                    continue
                time.sleep(delay)
            if candidates:
                break
            time.sleep(delay)

    return sorted(candidates, key=lambda a: -_score(a, ""))


def enrich_email_via_search(lead, delay: float = 1.5):
    """Second-pass enrichment: only for leads still missing an email."""
    if lead.email:
        return lead
    emails = search_email(lead.business_name, lead.city, delay=delay)
    if emails:
        lead.email = emails[0]
        lead.notes = (lead.notes + " | email_source: web_search").strip(" |")
        if len(emails) > 1:
            lead.notes += f" | alt_emails: {', '.join(emails[1:3])}"
    else:
        lead.notes = (lead.notes +
                      " | no-email-found:use-phone-outreach").strip(" |")
    return lead
