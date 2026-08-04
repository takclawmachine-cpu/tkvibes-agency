"""Centralised logging configuration for the lead engine.

All modules should import logger from here instead of using print() or
creating their own loggers. Call configure_logging() once at startup
to set the format and level.

Critical errors are forwarded to the CRM system_logs API for admin visibility.

Usage:
    from .log_config import configure_logging, get_logger

    configure_logging(level="INFO")
    logger = get_logger(__name__)
    logger.info("Lead engine started")
"""
import json
import logging
import os
import sys
from urllib.request import Request, urlopen
from urllib.error import URLError

_DEFAULT_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
_CRITICAL_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
_DEFAULT_DATE = "%H:%M:%S"

_initialised = False
_crm_log_url = ""
_crm_api_key = ""


def configure_logging(
    level: str = "INFO",
    fmt: str | None = None,
    datefmt: str | None = None,
    crm_url: str = "",
    crm_key: str = "",
):
    """Set up root-logger formatting once.

    Args:
        level: Log level string (INFO, DEBUG, WARNING, ERROR)
        fmt: Optional custom format string
        datefmt: Optional custom date format
        crm_url: CRM base URL for forwarding error logs (e.g. https://tkvibes.in/crm)
        crm_key: CRM API key for log ingestion
    """
    global _initialised, _crm_log_url, _crm_api_key
    if _initialised:
        return
    _initialised = True

    _crm_log_url = crm_url.rstrip("/") + "/api/logs.php" if crm_url else ""
    _crm_api_key = crm_key

    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format=fmt or _DEFAULT_FORMAT,
        datefmt=datefmt or _DEFAULT_DATE,
        stream=sys.stdout,
    )
    # Quiet noisy third-party loggers
    for noisy in ("httpx", "gspread", "google.auth", "urllib3"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    # Install handler for forwarding critical errors to CRM
    root = logging.getLogger()
    root.addHandler(_CRMLogHandler(_crm_log_url, _crm_api_key))


def get_logger(name: str) -> logging.Logger:
    """Get a logger for the given module name."""
    return logging.getLogger(name)


class _CRMLogHandler(logging.Handler):
    """Forward ERROR and CRITICAL log records to the CRM system_logs API."""

    def __init__(self, url: str, api_key: str):
        super().__init__(logging.ERROR)
        self.url = url
        self.api_key = api_key

    def emit(self, record: logging.LogRecord):
        if not self.url or not self.api_key:
            return
        try:
            level = record.levelname.lower()
            payload = json.dumps({
                "key": self.api_key,
                "level": level,
                "source": f"lead-engine:{record.name}",
                "message": self.format(record),
                "context": {
                    "module": record.name,
                    "func": record.funcName,
                    "line": record.lineno,
                },
            }).encode("utf-8")
            req = Request(self.url, data=payload, method="POST")
            req.add_header("Content-Type", "application/json")
            # Fire-and-forget with short timeout to avoid blocking the main flow
            urlopen(req, timeout=3)
        except Exception:
            pass  # Silently fail — logging should never break the application