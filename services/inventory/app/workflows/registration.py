"""Registriert eine Inventory-Workflow-Definition beim Workflow-Service."""

from __future__ import annotations

import logging
from typing import Any, Dict

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


def _build_inventory_workflow() -> Dict[str, Any]:
    return {
        "name": "inventory_inbound_flow",
        "version": "1.0.0",
        "tenant": settings.DEFAULT_TENANT,
        "description": "Standardfluss für Wareneingang → Einlagerung → Versand",
        "states": [
            "receiving",
            "stored",
            "allocated",
            "shipped",
            "exception",
        ],
        "initial_state": "receiving",
        "transitions": [
            {
                "name": "goods_received",
                "source": "receiving",
                "target": "stored",
                "event_type": "inventory.goods.received",
            },
            {
                "name": "reservation_requested",
                "source": "stored",
                "target": "allocated",
                "event_type": "inventory.stock.reserved",
            },
            {
                "name": "shipment_confirmed",
                "source": "allocated",
                "target": "shipped",
                "event_type": "inventory.stock.issued",
            },
            {
                "name": "receiving_exception",
                "source": "receiving",
                "target": "exception",
                "event_type": "inventory.receiving.mismatch",
            },
            {
                "name": "reset_exception",
                "source": "exception",
                "target": "receiving",
                "event_type": "inventory.workflow.retry",
            },
        ],
        "metadata": {
            "domain": "supply-chain",
            "owner": "inventory-agent",
        },
    }


async def register_inventory_workflow() -> None:
    url = f"{settings.WORKFLOW_SERVICE_URL.rstrip('/')}/api/v1/workflows/definitions"
    definition = _build_inventory_workflow()

    async with httpx.AsyncClient(timeout=settings.WORKFLOW_REGISTRATION_TIMEOUT) as client:
        try:
            response = await client.post(url, json=definition)
            if response.status_code in (200, 201):
                logger.info("Workflow-Definition inventory_inbound_flow registriert")
            elif response.status_code == 409:
                logger.debug("Workflow-Definition inventory_inbound_flow existiert bereits")
            else:
                response.raise_for_status()
        except httpx.HTTPError as exc:  # noqa: BLE001
            logger.warning("Registrierung der Inventory-Workflow-Definition fehlgeschlagen: %s", exc)

