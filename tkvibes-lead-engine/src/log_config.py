"""Centralised logging configuration for the lead engine with trace ID support.

All modules should import logger from here instead of using print() or
creating their own loggers. Call configure_logging() once at startup
to set the format and level. Additionally, call set_trace_id() at the
start of each pipeline run to propagate trace_id through all log records.

Critical errors are forwarded to the CRM system_logs API for admin visibility.

Usage:
    from .log_config import configure_logging, get_logger, set_trace_id
    
    configure_logging(level="INFO")
    trace_id = set_trace_id()  # or set_trace_id("existing-uuid")
    logger = get_logger(__name__)
    logger.info("Lead engine started", extra={"event": "pipeline_start"})
"""
import json
import logging
import os
import sys
import uuid
from contextvars import ContextVar
from urllib.request import Request, urlopen
from urllib.error import URLError

# ── Trace ID context variable ──────────────────────────────────────────────
# ContextVar automatically propagates trace_id through async/await and
# thread-local contexts without needing to pass it explicitly.
_trace_id: ContextVar[str] = ContextVar('trace_id', default='')


_DEFAULT_FORMAT = "%(asctime)s [%(levelname)s] %(name)s [trace:%(trace_id)s]: %(message)s"
_DEFAULT_DATE = "%Y-%m-%d %H:%M:%S"

_initialised = False
_crm_log_url = ""
_crm_api_key = ""


def set_trace_id(tid: str | None = None) -> str:
    """Set the trace ID for the current execution context.
    
    Args:
        tid: Optional trace ID string. If None, generates a new UUID4.
    
    Returns:
        The trace ID that was set.
    """
    tid = tid or str(uuid.uuid4())
    _trace_id.set(tid)
    return tid


def get_trace_id() -> str:
    """Get the current trace ID from context."""
    return _trace_id.get()


class _TraceIdFilter(logging.Filter):
    """Inject trace_id into every log record."""
    
    def filter(self, record: logging.LogRecord) -> bool:
        # Set trace_id from context variable
        record.trace_id = _trace_id.get() or '-'
        return True


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
        fmt: Optional custom format string (must include %(trace_id)s)
        datefmt: Optional custom date format
        crm_url: CRM base URL for forwarding error logs
        crm_key: CRM API key for log ingestion
    """
    global _initialised, _crm_log_url, _crm_api_key
    if _initialised:
        # Allow reconfiguration of trace_id filter
        root = logging.getLogger()
        for handler in root.handlers:
            for f in handler.filters:
                if isinstance(f, _TraceIdFilter):
                    pass  # Already installed
        return
    _initialised = True

    _crm_log_url = crm_url.rstrip("/") + "/api/logs.php" if crm_url else ""
    _crm_api_key = crm_key

    root = logging.getLogger()
    root.handlers.clear()  # Remove any pre-existing handlers
    root.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(logging.Formatter(fmt or _DEFAULT_FORMAT, datefmt or _DEFAULT_DATE))
    console_handler.addFilter(_TraceIdFilter())
    root.addHandler(console_handler)

    # CRM log forwarding handler
    if crm_url and crm_key:
        crm_handler = _CRMLogHandler(_crm_log_url, crm_key)
        crm_handler.setLevel(logging.ERROR)
        crm_handler.setFormatter(logging.Formatter(_DEFAULT_FORMAT, _DEFAULT_DATE))
        crm_handler.addFilter(_TraceIdFilter())
        root.addHandler(crm_handler)

    # Quiet noisy third-party loggers
    for noisy in ("httpx", "gspread", "google.auth", "urllib3"):
        logging.getLogger(noisy).setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger for the given module name.
    
    All loggers automatically include the current trace_id from context.
    """
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
            trace_id = getattr(record, 'trace_id', '')
            payload = json.dumps({
                "key": self.api_key,
                "level": level,
                "source": f"lead-engine:{record.name}",
                "message": record.getMessage(),
                "context": {
                    "trace_id": trace_id,
                    "module": record.name,
                    "func": record.funcName,
                    "line": record.lineno,
                    "extra": {k: v for k, v in record.__dict__.items() 
                              if k not in ('name', 'msg', 'args', 'levelname', 'levelno',
                                         'pathname', 'filename', 'module', 'exc_info',
                                         'exc_text', 'stack_info', 'lineno', 'funcName',
                                         'created', 'msecs', 'relativeCreated', 'thread',
                                         'threadName', 'processName', 'process', 'message',
                                         'trace_id', 'taskName', 'stack_info', 'filename',
                                         'pathname')},
                },
            }).encode("utf-8")
            req = Request(self.url, data=payload, method="POST")
            req.add_header("Content-Type", "application/json")
            req.add_header("X-Trace-ID", trace_id)
            # Fire-and-forget with short timeout to avoid blocking the main flow
            urlopen(req, timeout=5)
        except Exception:
            pass  # Silently fail — logging should never break the application
