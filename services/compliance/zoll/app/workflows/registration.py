"""Registrierung der Export-Workflow-Definition."""

from __future__ import annotations

import logging

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


def _build_export_definition() -> dict:
    return {
        "name": "export_clearance",
        "version": "1.0.0",
        "tenant": settings.WORKFLOW_TENANT,
        "description": "Freigabeprozess für Exportaufträge",
        "states": [
            "screening",
            "review",
            "approved",
            "blocked",
            "archived",
        ],
        "initial_state": "screening",
        "transitions": [
            {
                "name": "screening_green",
                "source": "screening",
                "target": "approved",
                "event_type": "export.screening.cleared",
            },
            {
                "name": "screening_yellow",
                "source": "screening",
                "target": "review",
                "event_type": "export.screening.review",
            },
            {
                "name": "screening_red",
                "source": "screening",
                "target": "blocked",
                "event_type": "export.screening.failed",
            },
            {
                "name": "review_approved",
                "source": "review",
                "target": "approved",
                "event_type": "export.review.approved",
            },
            {
                "name": "review_blocked",
                "source": "review",
                "target": "blocked",
                "event_type": "export.review.rejected",
            },
            {
                "name": "archive",
                "source": "approved",
                "target": "archived",
                "event_type": "export.archived",
            },
        ],
        "metadata": {"domain": "compliance", "category": "zoll"},
    }


async def register_export_workflow() -> None:
    definition = _build_export_definition()
    url = f"{settings.WORKFLOW_SERVICE_URL.rstrip('/')}/api/v1/workflows/definitions"

    async with httpx.AsyncClient(timeout=settings.WORKFLOW_REGISTRATION_TIMEOUT) as client:
        try:
            response = await client.post(url, json=definition)
            if response.status_code in (200, 201, 409):
                logger.info("Workflow export_clearance registriert (status %s)", response.status_code)
            else:
                response.raise_for_status()
        except httpx.HTTPError as exc:  # noqa: BLE001
            logger.warning("Workflow-Registrierung fehlgeschlagen: %s", exc)
