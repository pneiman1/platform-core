"""Structured logging for platform-core.

Uses structlog to emit JSON log lines that include timestamp, log level,
module name, event name, and arbitrary key-value context. This format
is what Datadog, CloudWatch, and any modern log aggregator expects.

Usage:
    from platform_core.utils.logging import configure_logging, get_logger

    configure_logging()  # call once at process startup
    log = get_logger(__name__)
    log.info("seed_started", tenant_id="del_mar_derm", n_patients=3500)

Produces a single JSON line:
    {"event": "seed_started", "tenant_id": "del_mar_derm", "n_patients": 3500,
     "logger": "scripts.seed_data", "level": "info",
     "timestamp": "2026-06-07T15:42:18.123456Z"}
"""
from __future__ import annotations

import logging
import sys

import structlog

from platform_core.config import get_settings


def configure_logging() -> None:
    """Configure structlog. Call once at process startup."""
    settings = get_settings()

    # Bridge stdlib logging into structlog so third-party libraries
    # (boto3, snowflake-connector, sqlalchemy) also emit JSON.
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=settings.log_level,
    )

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.getLevelName(settings.log_level)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """Return a logger bound to the given module name.

    Convention: pass ``__name__`` so log lines include the source module.

        from platform_core.utils.logging import get_logger
        log = get_logger(__name__)
    """
    return structlog.get_logger(name)
    