"""Lightweight client for pushing inventory events into the Workflow-Service."""

from __future__ import annotations

import logging

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


async def emit_workflow_event(event_type: str, tenant: str, payload: dict) -> None:
    """Forward domain events to the workflow event endpoint."""

    base_url = str(settings.WORKFLOW_SERVICE_URL).rstrip("/")
    url = f"{base_url}/api/v1/workflows/events"
    body = {
        "eventType": event_type,
        "tenant": tenant,
        "payload": payload,
    }

    async with httpx.AsyncClient(timeout=settings.WORKFLOW_REGISTRATION_TIMEOUT) as client:
        try:
            response = await client.post(url, json=body)
            response.raise_for_status()
        except httpx.HTTPError as exc:  # noqa: BLE001
            logger.debug("Workflow-Event konnte nicht zugestellt werden (%s): %s", event_type, exc)

