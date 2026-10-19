"""Auftrag stornieren als Kommando-Weg (Studio-Katalog ``stornieren``, MASK-COMMANDS-ROLLOUT-20261019).

Aus ``sales_orders.py`` herausgeloest, damit das Godfile nicht waechst. Pfad ``/sales/orders/{id}/actions/stornieren``.
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.auth.deps import require_roles
from app.core.akteur import gepruefter_akteur
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.mask_action_runtime_service import MaskActionResult as MaskActionResultOut
from app.services.mask_commands import statusaktion

router = APIRouter()

#: Storno eines Auftrags ist Verkaufsarbeit: Sachbearbeitung oder Leitung des Verkaufs.
_sales_write = require_roles("SALES_BEARBEITEN", "SALES_ADMIN", "admin")


@router.post(
    "/{entity_id}/actions/stornieren",
    response_model=MaskActionResultOut,
    summary="Auftrag stornieren (Maskenaktion: Begruendung, Trockenlauf, Wiederholungsschutz)",
)
async def stornieren_action(
    entity_id: str,
    body: dict[str, Any] = Body(default_factory=dict),
    user: dict = Depends(_sales_write),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Derselbe Zustandswechsel wie ``/cancel`` (offen/bestaetigt -> storniert), fuer Maske, Studio, CLI und MCP.

    Die Begruendung ist Pflicht und steht mit dem Bearbeiter aus dem Token im Audit der Laufzeit.
    Agenten sperrt die Maske (``forbiddenForAgents`` im Studio-Katalog).
    """
    gepruefter_akteur(user)

    def ausfuehren(db_: Session, _payload: dict[str, Any]) -> str:
        db_.execute(
            text("UPDATE domain_crm.sales_orders SET status = 'cancelled', updated_at = NOW() "
                 "WHERE id = :id AND tenant_id = :tid AND status NOT IN ('cancelled', 'completed')"),
            {"id": entity_id, "tid": tenant_id},
        )
        return "Auftrag storniert."

    result = await statusaktion(
        db, action_key="stornieren", entity_type="sales_order", entity_id=entity_id, tenant_id=tenant_id,
        body=body, erlaubt={"draft", "open", "confirmed", "in_delivery"}, ausfuehren=ausfuehren,
        status_sql="SELECT status FROM domain_crm.sales_orders WHERE id::text = :id AND tenant_id = :tid",
        event_type="sales.order.cancelled",
    )
    return result.model_dump()
