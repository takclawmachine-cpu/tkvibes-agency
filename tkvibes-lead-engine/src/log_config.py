"""Centralised logging configuration for the lead engine.

All modules should import logger from here instead of using print() or
creating their own loggers. Call configure_logging() once at startup
to set the format and level.

Usage:
    from .log_config import configure_logging, get_logger

    configure_logging(level="INFO")
    logger = get_logger(__name__)
    logger.info("Lead engine started")
"""

import logging
import sys

_DEFAULT_FORMAT = (
    "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    if sys.stderr.isatty()
    else "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
_DEFAULT_DATE = "%H:%M:%S"

_initialised = False


def configure_logging(
    level: str = "INFO",
    fmt: str | None = None,
    datefmt: str | None = None,
):
    """Set up root-logger formatting once.

    Call this from main() before any module is imported.
    """
    global _initialised
    if _initialised:
        return
    _initialised = True

    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format=fmt or _DEFAULT_FORMAT,
        datefmt=datefmt or _DEFAULT_DATE,
        stream=sys.stdout,
    )
    # Quiet noisy third-party loggers
    for noisy in ("httpx", "gspread", "google.auth", "urllib3"):
        logging.getLogger(noisy).setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger for the given module name."""
    return logging.getLogger(name)