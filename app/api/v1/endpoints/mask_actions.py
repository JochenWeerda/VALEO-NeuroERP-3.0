"""
UIX-053: Mask Action Stubs — CommandEndpoints für alle verbliebenen native ScreenDefinitions.

Alle Endpunkte folgen dem Schema:
  POST /api/v1/{domain}/{entity_type}/{entity_id}/actions/{action_key}

Payload optional; `_mode` (dryRun/execute), `_auditReason`, `_idempotencyKey` werden
vom ActionRuntime automatisch gesetzt.
"""
from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.tenant import get_tenant_id

router = APIRouter(tags=["mask-actions"])


class MaskActionResult(BaseModel):
    """Einheitliches Ergebnis eines Mask-Action-Stubs (UIX-053)."""

    success: bool
    actionKey: str
    entityId: str
    tenantId: str
    message: str
    proposedChanges: Optional[dict[str, Any]] = None


# ---------------------------------------------------------------------------
# lager/stock-movement → stornieren  (UIX-053)
# ---------------------------------------------------------------------------

@router.post(
    "/lager/stock-movements/{entity_id}/actions/stornieren",
    response_model=MaskActionResult,
    summary="Lagerbewegung stornieren (UIX-053)",
)
async def action_lager_stornieren(
    entity_id: str,
    tenant_id: str = Depends(get_tenant_id),
):
    """Stub: Lagerbewegung stornieren — humanApprovalRequired, dryRun-Phase."""
    return {
        "success": True,
        "actionKey": "stornieren",
        "entityId": entity_id,
        "tenantId": tenant_id,
        "message": "Stornierung wird vorbereitet.",
        "proposedChanges": {"status": "storniert", "bewegung_id": entity_id},
    }


# ---------------------------------------------------------------------------
# einkauf/purchase-order → bestellen  (UIX-053)
# ---------------------------------------------------------------------------

@router.post(
    "/einkauf/bestellungen/{entity_id}/actions/bestellen",
    response_model=MaskActionResult,
    summary="Bestellung erteilen (UIX-053)",
)
async def action_einkauf_bestellen(
    entity_id: str,
    tenant_id: str = Depends(get_tenant_id),
):
    """Stub: Bestellung aus Angebot erzeugen — dryRun zeigt proposedChanges."""
    return {
        "success": True,
        "actionKey": "bestellen",
        "entityId": entity_id,
        "tenantId": tenant_id,
        "message": "Bestellung wird erzeugt.",
        "proposedChanges": {"status": "bestellung_erzeugt", "angebot_id": entity_id},
    }


# ---------------------------------------------------------------------------
# lager/article-stock → wareneingang  (UIX-053)
# ---------------------------------------------------------------------------

@router.post(
    "/lager/artikel/{entity_id}/actions/wareneingang",
    response_model=MaskActionResult,
    summary="Wareneingang buchen (UIX-053)",
)
async def action_lager_wareneingang(
    entity_id: str,
    tenant_id: str = Depends(get_tenant_id),
):
    """Stub: Wareneingang für Artikel buchen — requiresConfirmation."""
    return {
        "success": True,
        "actionKey": "wareneingang",
        "entityId": entity_id,
        "tenantId": tenant_id,
        "message": "Wareneingang wird gebucht.",
        "proposedChanges": {"status": "wareneingang_gebucht", "artikel_id": entity_id},
    }


# ---------------------------------------------------------------------------
# qualitaet/reklamation → abschliessen  (UIX-053)
# ---------------------------------------------------------------------------

@router.post(
    "/reklamationen/{entity_id}/actions/abschliessen",
    response_model=MaskActionResult,
    summary="Reklamation abschliessen (UIX-053)",
)
async def action_reklamation_abschliessen(
    entity_id: str,
    tenant_id: str = Depends(get_tenant_id),
):
    """Stub: Reklamation abschliessen — requiresConfirmation."""
    return {
        "success": True,
        "actionKey": "abschliessen",
        "entityId": entity_id,
        "tenantId": tenant_id,
        "message": "Reklamation wird abgeschlossen.",
        "proposedChanges": {"status": "abgeschlossen", "reklamation_id": entity_id},
    }


# ---------------------------------------------------------------------------
# crm/lead → qualifizieren  (UIX-053)
# ---------------------------------------------------------------------------

@router.post(
    "/crm/leads/{entity_id}/actions/qualifizieren",
    response_model=MaskActionResult,
    summary="Lead als Opportunity qualifizieren (UIX-053)",
)
async def action_crm_qualifizieren(
    entity_id: str,
    tenant_id: str = Depends(get_tenant_id),
):
    """Stub: Lead als Opportunity qualifizieren — Opportunity-Erzeugungsflow folgt."""
    return {
        "success": True,
        "actionKey": "qualifizieren",
        "entityId": entity_id,
        "tenantId": tenant_id,
        "message": "Lead wird als Opportunity qualifiziert.",
        "proposedChanges": {"status": "opportunity", "lead_id": entity_id, "opportunity_id": None},
    }
