"""Email discovery for leads.

Google Places API never returns email addresses, so leads arrive with email="".
This module finds a contact email by crawling the lead's own website
(homepage + common contact pages), reading mailto: links, visible text,
and simple obfuscations ("name [at] domain dot com").

Strategy (in order, first hit wins):
  1. mailto: links on homepage
  2. mailto: links / text on /contact, /contact-us, /about, /reach-us ...
  3. plain-text regex on page bodies
  4. de-obfuscation pass ([at] (at) {at} " at ")
Results are ranked: role emails on the site's own domain beat free-mail,
generic noreply/example/sentry addresses are discarded.
"""

from __future__ import annotations

import re
import time
from urllib.parse import urljoin, urlparse

import httpx

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")

CONTACT_PATHS = [
    "", "/contact", "/contact-us", "/contactus", "/contact.html",
    "/contact.php", "/about", "/about-us", "/reach-us", "/get-in-touch",
    "/enquiry", "/appointment", "/book-appointment",
]

EMAIL_RE = re.compile(
    r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}"
)

# "info [at] clinic dot com" / "info(at)clinic.com"
OBFUSCATED_RE = re.compile(
    r"([A-Za-z0-9._%+\-]+)\s*(?:\[at\]|\(at\)|\{at\}|\s+at\s+|&#64;)\s*"
    r"([A-Za-z0-9.\-]+)\s*(?:\[dot\]|\(dot\)|\s+dot\s+|\.)\s*([A-Za-z]{2,})",
    re.IGNORECASE,
)

JUNK_SUBSTRINGS = (
    "noreply", "no-reply", "donotreply", "example.com", "sentry.io",
    "wixpress.com", "godaddy.com", "yourdomain", "domain.com", "email.com",
    "@sentry", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".css",
    "@2x", "u003e", "wordpress.com", "@schema.org", "core-js",
)

ROLE_PREFIXES = (
    "info", "contact", "hello", "enquiry", "enquiries", "inquiry",
    "admin", "office", "reception", "appointments", "appointment",
    "care", "support", "clinic", "mail", "help", "frontdesk", "desk",
)

FREE_MAIL = ("gmail.com", "yahoo.com", "yahoo.co.in", "hotmail.com",
             "outlook.com", "rediffmail.com", "live.com", "icloud.com",
             "protonmail.com", "aol.com")


def _clean(addr: str) -> str:
    return addr.strip().strip(".,;:()<>\"'").lower()


def _is_junk(addr: str) -> bool:
    a = addr.lower()
    if any(j in a for j in JUNK_SUBSTRINGS):
        return True
    if len(a) > 80 or a.count("@") != 1:
        return True
    local, _, dom = a.partition("@")
    if not local or "." not in dom:
        return True
    # image/hash-like locals e.g. 3f2a9b8c7d@2x
    if re.fullmatch(r"[0-9a-f]{16,}", local):
        return True
    return False


def _site_domain(url: str) -> str:
    try:
        host = urlparse(url).netloc.lower()
        return host[4:] if host.startswith("www.") else host
    except Exception:
        return ""


def _score(addr: str, site_domain: str) -> int:
    """Higher = better contact email."""
    local, _, dom = addr.partition("@")
    s = 0
    if site_domain and (dom == site_domain or dom.endswith("." + site_domain)
                        or site_domain.endswith("." + dom)):
        s += 50
    if any(local.startswith(p) for p in ROLE_PREFIXES):
        s += 25
    if dom in FREE_MAIL:
        s += 5           # still usable for small businesses, just lower rank
    if len(local) <= 3:
        s -= 5
    return s


def _extract(html: str) -> set[str]:
    found: set[str] = set()

    for m in re.finditer(r'mailto:([^"\'>\s?]+)', html, re.IGNORECASE):
        found.add(_clean(m.group(1)))

    for m in EMAIL_RE.finditer(html):
        found.add(_clean(m.group(0)))

    for m in OBFUSCATED_RE.finditer(html):
        found.add(_clean(f"{m.group(1)}@{m.group(2)}.{m.group(3)}"))

    return {a for a in found if a and not _is_junk(a)}


def find_emails_for_site(
    website_url: str,
    timeout: float = 12.0,
    delay: float = 0.8,
    max_pages: int = 6,
) -> list[str]:
    """Crawl a business website and return candidate emails, best first."""
    if not website_url:
        return []
    if not website_url.startswith(("http://", "https://")):
        website_url = "https://" + website_url

    domain = _site_domain(website_url)
    candidates: set[str] = set()
    pages_fetched = 0

    headers = {"User-Agent": UA, "Accept": "text/html,*/*"}
    with httpx.Client(timeout=timeout, follow_redirects=True,
                      headers=headers) as client:
        for path in CONTACT_PATHS:
            if pages_fetched >= max_pages:
                break
            url = urljoin(website_url, path) if path else website_url
            try:
                r = client.get(url)
                if r.status_code != 200 or "html" not in \
                        r.headers.get("content-type", "").lower():
                    continue
                pages_fetched += 1
                candidates |= _extract(r.text)
                time.sleep(delay)
            except Exception:
                continue
            # Homepage hit with a solid on-domain email? stop early.
            if path == "" and any(
                _score(a, domain) >= 75 for a in candidates
            ):
                break

    return sorted(candidates, key=lambda a: -_score(a, domain))


def enrich_email(lead, delay: float = 0.8) -> "object":
    """Populate lead.email (and notes) from the lead's website."""
    if lead.email:
        return lead
    if not lead.website_url:
        lead.notes = (lead.notes + " | no-website:email-unavailable").strip(" |")
        return lead

    emails = find_emails_for_site(lead.website_url, delay=delay)
    if emails:
        lead.email = emails[0]
        if len(emails) > 1:
            extra = ", ".join(emails[1:4])
            lead.notes = (lead.notes + f" | alt_emails: {extra}").strip(" |")
    else:
        lead.notes = (lead.notes + " | email-not-found-on-site").strip(" |")
    return lead
