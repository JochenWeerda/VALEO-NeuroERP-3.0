"""Structured logging helpers."""

from __future__ import annotations

import logging
import sys
from typing import Any

import structlog


def _shared_processors() -> list[Any]:
    return [
        structlog.contextvars.merge_contextvars,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]


def setup_logging(*, json_format: bool = False, level: str = "INFO") -> None:
    """Initialise stdlib + structlog configuration."""

    resolved_level = getattr(logging, level.upper(), logging.INFO)

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=resolved_level,
    )

    renderer = structlog.processors.JSONRenderer() if json_format else structlog.dev.ConsoleRenderer()

    structlog.configure(
        processors=[*_shared_processors(), renderer],
        wrapper_class=structlog.make_filtering_bound_logger(resolved_level),
        cache_logger_on_first_use=True,
    )

