import time
import random
import urllib.robotparser as rp
from urllib.parse import urlparse
from tenacity import retry, stop_after_attempt, wait_exponential
from ..log_config import get_logger

logger = get_logger(__name__)


class BaseConnector:
    """Shared rate limiting, robots.txt compliance, and retries."""

    def __init__(self, per_domain_delay=4, max_retries=3):
        self.delay = per_domain_delay
        self.max_retries = max_retries
        self._last_hit = {}
        self._robots = {}

    def _allowed(self, url: str, ua: str = "TKVibesLeadBot") -> bool:
        host = urlparse(url).netloc
        if host not in self._robots:
            r = rp.RobotFileParser()
            r.set_url(f"https://{host}/robots.txt")
            try:
                r.read()
            except Exception as e:
                logger.debug("robots.txt unavailable for %s: %s", host, e)
                r = None
            self._robots[host] = r
        r = self._robots[host]
        return True if r is None else r.can_fetch(ua, url)

    def _throttle(self, url: str):
        host = urlparse(url).netloc
        last = self._last_hit.get(host, 0)
        wait = self.delay - (time.time() - last)
        if wait > 0:
            jitter = random.uniform(0, 1.5)
            time.sleep(wait + jitter)  # jitter
        self._last_hit[host] = time.time()

    def discover(self, city: str, category: str, limit: int) -> list:
        raise NotImplementedError
