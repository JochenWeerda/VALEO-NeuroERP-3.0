"""
Gap 039: Optionales OpenTelemetry (FastAPI + SQLAlchemy).

Aktivierung:
- OTEL_EXPORTER_OTLP_ENDPOINT gesetzt (z.B. http://localhost:4318/v1/traces), oder
- ENABLE_TRACING=true ohne Endpoint → ConsoleSpanExporter (nur Dev).

Ohne installierte Pakete: Warnung im Log, App läuft unverändert weiter.
"""

from __future__ import annotations

import logging
import os
from typing import Any

logger = logging.getLogger(__name__)


def instrument_app_if_configured(app: Any, engine: Any) -> bool:
    """
    Registriert TracerProvider und instrumentiert FastAPI + SQLAlchemy.
    Returns True wenn Instrumentierung aktiv ist.
    """
    from app.core.config import settings

    endpoint = (
        (getattr(settings, "OTEL_EXPORTER_OTLP_ENDPOINT", None) or "")
        or (os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT") or "")
    ).strip()
    use_console = bool(settings.ENABLE_TRACING) and not endpoint

    if not endpoint and not use_console:
        return False

    try:
        from opentelemetry import trace
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

        resource = Resource.create(
            {
                "service.name": getattr(settings, "OTEL_SERVICE_NAME", "valeo-neuroerp-api"),
                "deployment.environment": settings.APP_ENV,
            }
        )
        provider = TracerProvider(resource=resource)

        if endpoint:
            from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

            exporter = OTLPSpanExporter(endpoint=endpoint)
            provider.add_span_processor(BatchSpanProcessor(exporter))
            logger.info("OpenTelemetry: OTLP HTTP exporter → %s", endpoint)
        else:
            provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
            logger.info("OpenTelemetry: ConsoleSpanExporter (ENABLE_TRACING ohne OTLP-Endpoint)")

        trace.set_tracer_provider(provider)
        FastAPIInstrumentor.instrument_app(app)
        SQLAlchemyInstrumentor().instrument(engine=engine)
        return True
    except ImportError as exc:
        logger.warning(
            "OpenTelemetry-Pakete fehlen (pip install opentelemetry-sdk …): %s — Tracing deaktiviert.",
            exc,
        )
        return False
    except Exception:
        logger.exception("OpenTelemetry-Instrumentierung fehlgeschlagen — Tracing deaktiviert.")
        return False
