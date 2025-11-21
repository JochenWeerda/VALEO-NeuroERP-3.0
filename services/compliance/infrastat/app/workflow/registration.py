"""Registrierung der Intrastat-Workflow-Definition beim Workflow-Service."""

from __future__ import annotations

import logging
from typing import Any, Dict, List

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


def _build_intrastat_definition() -> Dict[str, Any]:
    return {
        "name": "intrastat_monthly_cycle",
        "version": "1.0.0",
        "tenant": settings.DEFAULT_TENANT,
        "description": "Automatisierter Monatszyklus für Intrastat-Meldungen",
        "states": [
            "collecting",
            "validating",
            "ready_to_submit",
            "submitting",
            "submitted",
            "archived",
            "error",
        ],
        "initial_state": "collecting",
        "transitions": [
            {
                "name": "schedule_validation",
                "source": "collecting",
                "target": "validating",
                "event_type": "intrastat.batch.ready",
                "description": "Scheduler signalisiert, dass die Sammelphase abgeschlossen ist.",
            },
            {
                "name": "validation_succeeded",
                "source": "validating",
                "target": "ready_to_submit",
                "event_type": "intrastat.validation.completed",
                "description": "Validierung erfolgreich abgeschlossen.",
            },
            {
                "name": "validation_failed",
                "source": "validating",
                "target": "error",
                "event_type": "intrastat.validation.failed",
                "description": "Validierung meldet Fehler.",
            },
            {
                "name": "retry_validation",
                "source": "error",
                "target": "collecting",
                "event_type": "intrastat.retry.requested",
                "description": "Manueller Retry oder automatische Korrektur.",
            },
            {
                "name": "submission_started",
                "source": "ready_to_submit",
                "target": "submitting",
                "event_type": "intrastat.submission.started",
                "description": "Übermittlung an IDEV gestartet.",
            },
            {
                "name": "submission_succeeded",
                "source": "submitting",
                "target": "submitted",
                "event_type": "intrastat.submission.completed",
                "description": "Übermittlung erfolgreich.",
            },
            {
                "name": "submission_failed",
                "source": "submitting",
                "target": "error",
                "event_type": "intrastat.submission.failed",
                "description": "Übermittlung fehlgeschlagen.",
            },
            {
                "name": "archive_submission",
                "source": "submitted",
                "target": "archived",
                "event_type": "intrastat.archived",
                "description": "Archivierung abgeschlossen.",
            },
        ],
        "metadata": {
            "domain": "compliance",
            "category": "intrastat",
            "owner": "compliance-agent",
        },
    }


async def register_intrastat_workflow() -> None:
    definition = _build_intrastat_definition()
    url = f"{settings.WORKFLOW_SERVICE_URL.rstrip('/')}/api/v1/workflows/definitions"

    async with httpx.AsyncClient(timeout=settings.WORKFLOW_REGISTRATION_TIMEOUT) as client:
        try:
            response = await client.post(url, json=definition)
            if response.status_code in (200, 201):
                logger.info("Workflow-Definition intrastat_monthly_cycle registriert")
            elif response.status_code == 409:
                logger.debug("Workflow-Definition intrastat_monthly_cycle existiert bereits")
            else:
                response.raise_for_status()
        except httpx.HTTPError as exc:
            logger.warning("Registrierung der Intrastat-Workflow-Definition fehlgeschlagen: %s", exc)
