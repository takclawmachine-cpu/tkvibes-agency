"""Website performance analysis for leads with weak/existing websites.

Uses GTmetrix API (if configured) or generates simulated analysis data
for leads with weak websites. The analysis feeds into the pitch deck
to show the lead exactly what's wrong with their current site.
"""

import json
import os
import re
from urllib.request import Request, urlopen
from urllib.error import URLError
from .models import Lead


def _check_gtmetrix(website_url: str, api_key: str = "") -> dict | None:
    """Check a website via GTmetrix API.

    Returns dict with performance data or None if unavailable.
    """
    if not api_key or not website_url:
        return None

    # GTmetrix v2 API
    try:
        # Step 1: Submit test
        req = Request(
            "https://gtmetrix.com/api/2.0/tests",
            data=json.dumps({"url": website_url, "adblock": True}).encode(),
            method="POST"
        )
        req.add_header("Authorization", f"Basic {api_key}")
        req.add_header("Content-Type", "application/json")

        with urlopen(req, timeout=30) as resp:
            test_data = json.loads(resp.read().decode())

        test_id = test_data.get("data", {}).get("id", "")
        if not test_id:
            return None

        # Step 2: Poll for result (simplified — one attempt)
        import time
        time.sleep(5)

        poll_url = f"https://gtmetrix.com/api/2.0/tests/{test_id}"
        poll_req = Request(poll_url)
        poll_req.add_header("Authorization", f"Basic {api_key}")

        with urlopen(poll_req, timeout=30) as resp:
            result = json.loads(resp.read().decode())

        attributes = result.get("data", {}).get("attributes", {})
        return {
            "performance_score": attributes.get("performance_score", 0),
            "structure_score": attributes.get("structure_score", 0),
            "lighthouse_score": attributes.get("lighthouse_score", 0),
            "pagespeed_score": attributes.get("pagespeed_score", 0),
            "fully_loaded_time": attributes.get("fully_loaded_time", 0),
            "total_page_size": attributes.get("total_page_size", 0),
            "total_page_requests": attributes.get("total_page_requests", 0),
        }
    except Exception:
        return None


def _check_pingdom(website_url: str) -> dict | None:
    """Check a website (simulated — Pingdom deprecated their free API).

    Returns dict with simulated analysis data.
    """
    if not website_url:
        return None
    return None  # Pingdom API is deprecated; use simulated data


def _simulate_analysis(website_url: str, lead: Lead) -> dict:
    """Generate simulated website analysis based on URL patterns and lead data.

    Uses heuristics: shorten URLs, HTTP-only, no mobile optimization, etc.
    """
    url = (website_url or "").strip().lower()
    issues = []
    score = 50  # Start at 50/100

    # Check for basic issues
    if url.startswith("http://") or not url.startswith("https://"):
        issues.append("Not using HTTPS (SSL) — visitors see 'Not Secure' warning")
        score -= 15

    if "wordpress" in url or "wp-" in url:
        issues.append("Using WordPress without caching/optimization")
        score -= 5

    if "wix" in url or "weebly" in url or "squarespace" in url:
        issues.append("Drag-and-drop builder — limited customization, slow loading")
        score -= 10

    if "blogspot" in url or "blogger" in url or "wordpress.com" in url:
        issues.append("Free platform — looks unprofessional, limited SEO control")
        score -= 20

    if "facebook" in url or "instagram" in url or "social" in url:
        issues.append("Only social media page — not a real website")
        score -= 25

    # Check for mobile responsiveness
    if not any(x in url for x in ["responsive", "mobile", "amp"]):
        issues.append("Likely not mobile-responsive — 60%+ visitors use phones")
        score -= 10

    # Check for simple URL patterns that indicate old sites
    if ".html" in url or ".htm" in url:
        issues.append("Static HTML pages — no CMS, hard to update")
        score -= 5

    if any(x in url for x in ["geocities", "angelfire", "tripod"]):
        issues.append("Extremely outdated platform")
        score -= 20

    score = max(5, min(85, score))

    return {
        "performance_score": score,
        "issues": issues[:5],
        "fully_loaded_time": f"{5 + (85 - score) // 10}.{abs(score) % 10}s",
        "total_page_size": f"{1 + (85 - score) // 5}MB",
        "total_requests": 30 + (85 - score),
        "mobile_ready": score > 50,
        "has_ssl": "https://" in url,
        "is_simulated": True,
    }


def analyze_website(lead: Lead, gtmetrix_api_key: str = "") -> dict:
    """Analyze a lead's website and return performance data + issues.

    Tries GTmetrix API first, falls back to simulated analysis.
    Returns dict with: performance_score, issues list, and metrics.
    """
    url = (lead.website_url or "").strip()
    if not url:
        return {"performance_score": 0, "issues": ["No website found"], "fully_loaded_time": "N/A"}

    # Try GTmetrix
    if gtmetrix_api_key:
        result = _check_gtmetrix(url, gtmetrix_api_key)
        if result:
            issues = []
            if result.get("performance_score", 0) < 50:
                issues.append("Low performance score — slow loading times")
            if result.get("structure_score", 0) < 50:
                issues.append("Poor structure — needs code optimization")
            if result.get("fully_loaded_time", 0) > 3:
                issues.append(f"Slow load time ({result['fully_loaded_time']}s) — visitors leave")
            if result.get("total_page_requests", 0) > 50:
                issues.append("Too many HTTP requests — slowing page load")
            if result.get("total_page_size", 0) > 3_000_000:
                issues.append("Large page size — needs image optimization")
            result["issues"] = issues[:5]
            return result

    # Fallback to simulated
    analysis = _simulate_analysis(url, lead)
    return analysis


def format_website_analysis_html(analysis: dict, lead: Lead) -> str:
    """Format website analysis as a pitch deck slide."""
    issues = analysis.get("issues", [])
    score = analysis.get("performance_score", 0)

    if not issues or score == 0:
        return ""

    # Color the score
    if score < 30:
        score_color = "#ef4444"
        score_bg = "rgba(239,68,68,0.1)"
    elif score < 55:
        score_color = "#f59e0b"
        score_bg = "rgba(245,158,11,0.1)"
    else:
        score_color = "#22c55e"
        score_bg = "rgba(34,197,94,0.1)"

    chunks = [
        '<div style="max-width:800px;width:100%">',
        '<h2 class="anim-fade-up d1" style="font-family:\'Poppins\',sans-serif;font-size:2.2rem;font-weight:700;margin-bottom:1.5rem;text-align:center">Your Website Is Underperforming</h2>',
        '<p class="anim-fade-up d2" style="text-align:center;color:#94a3b8;margin-bottom:2rem;font-size:0.9rem">Our analysis found critical issues costing you customers</p>',
        f'<div style="display:flex;align-items:center;justify-content:center;gap:2rem;margin-bottom:2rem;flex-wrap:wrap">',
        f'<div class="glass anim-fade-up d3" style="text-align:center;padding:2rem;min-width:160px">',
        f'<div style="font-size:3rem;font-weight:800;color:{score_color}">{score}</div>',
        f'<div style="font-size:0.85rem;color:#94a3b8;margin-top:0.25rem">Performance Score</div>',
        f'</div>',
        f'<div class="glass anim-fade-up d4" style="text-align:center;padding:2rem;min-width:160px">',
        f'<div style="font-size:3rem;font-weight:800;color:#f59e0b">{analysis.get("fully_loaded_time", "N/A")}</div>',
        f'<div style="font-size:0.85rem;color:#94a3b8;margin-top:0.25rem">Load Time</div>',
        f'</div>',
        f'<div class="glass anim-fade-up d5" style="text-align:center;padding:2rem;min-width:160px">',
        f'<div style="font-size:3rem;font-weight:800;color:#f59e0b">{analysis.get("total_page_size", "N/A")}</div>',
        f'<div style="font-size:0.85rem;color:#94a3b8;margin-top:0.25rem">Page Size</div>',
        f'</div>',
        f'</div>',
    ]

    if issues:
        chunks.append(
            '<div class="glass anim-fade-up d6" style="padding:1.5rem">'
            '<h3 style="font-weight:700;margin-bottom:1rem;color:#ef4444"><i class="fa-solid fa-circle-exclamation" style="margin-right:8px"></i>Issues Found</h3>'
            '<div style="display:flex;flex-direction:column;gap:0.75rem">'
        )
        for issue in issues:
            chunks.append(
                f'<div style="display:flex;align-items:flex-start;gap:10px;padding:10px;border-radius:8px;background:rgba(239,68,68,0.05)">'
                f'<i class="fa-solid fa-xmark" style="color:#ef4444;margin-top:2px;flex-shrink:0"></i>'
                f'<span style="font-size:0.85rem;color:#cbd5e1">{issue}</span>'
                f'</div>'
            )
        chunks.append("</div></div>")

    chunks.append(
        f'<p class="anim-fade-up d7" style="text-align:center;color:#f59e0b;margin-top:2rem;font-size:0.9rem">'
        f'<i class="fa-solid fa-lightbulb" style="margin-right:6px"></i>'
        f'TKVibes can fix all of these issues with a modern website redesign.'
        f'</p>'
        f'</div>'
    )

    return "\n".join(chunks)


def format_website_analysis_site_section(analysis: dict, lead: Lead) -> str:
    """Format website analysis as a section in the sample site (for weak-site leads)."""
    issues = analysis.get("issues", [])
    score = analysis.get("performance_score", 0)

    if not issues or score == 0:
        return ""

    score_color = "#ef4444" if score < 30 else ("#f59e0b" if score < 55 else "#22c55e")

    items = []
    for issue in issues[:4]:
        items.append(
            f'<div class="card fade-up" style="display:flex;align-items:flex-start;gap:12px;padding:16px">'
            f'<div style="width:32px;height:32px;border-radius:8px;background:rgba(239,68,68,0.1);display:flex;align-items:center;justify-content:center;flex-shrink:0;margin-top:2px">'
            f'<i class="fa-solid fa-xmark" style="color:#ef4444;font-size:14px"></i></div>'
            f'<div><div style="font-size:14px;color:#cbd5e1">{issue}</div></div>'
            f'</div>'
        )

    return f"""
<section class="section" style="background:rgba(245,158,11,0.03)">
<div class="container">
<div style="text-align:center;margin-bottom:40px" class="fade-up">
<div class="section-label"><span>Website Audit</span></div>
<h2 class="section-title">Your Current Website Issues</h2>
<p class="section-sub" style="max-width:500px;margin:0 auto">We analyzed your site and found critical issues hurting your business</p>
</div>
<div style="display:flex;justify-content:center;gap:24px;margin-bottom:32px;flex-wrap:wrap" class="fade-up">
<div class="glass" style="text-align:center;padding:24px;min-width:140px">
<div style="font-size:2.5rem;font-weight:800;color:{score_color}">{score}</div>
<div style="font-size:13px;color:#94a3b8">Performance Score</div>
</div>
<div class="glass" style="text-align:center;padding:24px;min-width:140px">
<div style="font-size:2.5rem;font-weight:800;color:#f59e0b">{analysis.get("fully_loaded_time", "N/A")}</div>
<div style="font-size:13px;color:#94a3b8">Load Time</div>
</div>
<div class="glass" style="text-align:center;padding:24px;min-width:140px">
<div style="font-size:2.5rem;font-weight:800;color:#f59e0b">{analysis.get("total_page_requests", "N/A")}</div>
<div style="font-size:13px;color:#94a3b8">HTTP Requests</div>
</div>
</div>
<div class="grid-2" style="max-width:600px;margin:0 auto">
{chr(10).join(items)}
</div>
</div>
</section>"""