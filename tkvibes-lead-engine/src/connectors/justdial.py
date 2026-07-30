# NOTE: JustDial's Terms of Use restrict automated extraction. OFF by default.
# Enable only after reviewing current ToS. Selectors need maintenance.
from .base import BaseConnector
from ..models import Lead


class JustDialConnector(BaseConnector):
    BASE = "https://www.justdial.com"

    def discover(self, city: str, category: str, limit: int = 40) -> list[Lead]:
        from playwright.sync_api import sync_playwright

        url = f"{self.BASE}/{city}/{category.replace(' ', '-')}/nct-1234"
        if not self._allowed(url):
            print(f"[justdial] robots.txt disallows {url} — skipping")
            return []
        leads = []
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            page = browser.new_page(
                user_agent="TKVibesLeadBot (+services@tkvibes.in)"
            )
            self._throttle(url)
            page.goto(url, wait_until="domcontentloaded")
            cards = page.query_selector_all(".store-details, .col-md-6 .jsx-")  # maintain
            for c in cards[:limit]:
                def txt(sel):
                    el = c.query_selector(sel)
                    return el.inner_text().strip() if el else ""

                rating_raw = txt(".star_count, .rating")
                try:
                    rating = float(rating_raw) if rating_raw else None
                except ValueError:
                    rating = None

                leads.append(
                    Lead(
                        business_name=txt(".store-name, .lng_compnm"),
                        phone_primary=txt(".callus, .tel"),
                        address=txt(".address, .lng_add"),
                        city=city,
                        category=category,
                        opening_hours=txt(".hours, .timing"),
                        rating=rating,
                        source="justdial",
                        source_url=url,
                        has_website=False,
                        website_quality="directory_microsite",
                    )
                )
            browser.close()
        return leads
