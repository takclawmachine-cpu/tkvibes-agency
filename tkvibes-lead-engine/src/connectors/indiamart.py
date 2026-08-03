# NOTE: IndiaMART's Terms of Use restrict automated extraction. This connector
# is OFF by default. Enable only after reviewing current ToS; it honours
# robots.txt and rate limits via BaseConnector. Selectors need maintenance.
from .base import BaseConnector
from ..models import Lead
from ..log_config import get_logger

logger = get_logger(__name__)


class IndiaMartConnector(BaseConnector):
    BASE = "https://dir.indiamart.com"

    def discover(self, city: str, category: str, limit: int = 40) -> list[Lead]:
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            logger.warning("playwright not installed — skipping IndiaMart")
            return []

        url = f"{self.BASE}/search.mp?ss={category.replace(' ', '+')}&cq={city}"
        if not self._allowed(url):
            logger.info("robots.txt disallows %s — skipping", url)
            return []
        leads = []
        try:
            with sync_playwright() as pw:
                browser = pw.chromium.launch(headless=True)
                page = browser.new_page(
                    user_agent="TKVibesLeadBot (+services@tkvibes.in)"
                )
                self._throttle(url)
                page.goto(url, wait_until="domcontentloaded", timeout=30000)
                cards = page.query_selector_all(".lst .card, .prc-card")  # maintain
                for c in cards[:limit]:
                    def txt(sel):
                        el = c.query_selector(sel)
                        return el.inner_text().strip() if el else ""

                    leads.append(
                        Lead(
                            business_name=txt(".companyname, .cmpny"),
                            owner_name=txt(".cntct-nm, .owner"),
                            phone_primary=txt(".contact-no, .pns_h"),
                            address=txt(".newLocationUi, .clg"),
                            city=city,
                            category=category,
                            years_in_business=txt(".exp, .membYr"),
                            source="indiamart",
                            source_url=url,
                            has_website=False,
                            website_quality="directory_microsite",
                        )
                    )
                browser.close()
        except Exception as e:
            logger.error("IndiaMart scraping failed for %s/%s: %s", city, category, e)
        return leads
