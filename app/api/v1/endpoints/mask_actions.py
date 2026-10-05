"""
SPEC-P1-04 / UIX-053+: Mask Action CommandEndpoints mit ActionRuntime.

POST /api/v1/.../{entity_id}/actions/{action_key}
Unterstützt _mode: validate | dryRun | propose | execute
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.mask_action_runtime_service import MaskActionResult, run_mask_action

router = APIRouter(tags=["mask-actions"])


def _status_mutation(status: str, entity_id: str, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    base = {"status": status, "entity_id": entity_id}
    if extra:
        base.update(extra)
    return {
        "summary": f"Status → {status}",
        "affectedIds": [entity_id],
        "mutation": base,
    }


# ---------------------------------------------------------------------------
# lager/stock-movement → stornieren
# ---------------------------------------------------------------------------

@router.post(
    "/lager/stock-movements/{entity_id}/actions/stornieren",
    response_model=MaskActionResult,
    summary="Lagerbewegung stornieren (SPEC-P1-04)",
)
async def action_lager_stornieren(
    entity_id: str,
    body: dict[str, Any] = Body(default_factory=dict),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> MaskActionResult:
    def execute(db_: Session, payload: dict[str, Any], eid: str, tid: str) -> dict[str, Any]:
        return _status_mutation("storniert", eid, {"grund": payload.get("grund"), "bewegung_id": eid})

    return run_mask_action(
        db,
        action_key="stornieren",
        entity_type="stock_movement",
        entity_id=entity_id,
        tenant_id=tenant_id,
        body=body,
        execute_fn=execute,
        outbox_event_type="lager.stock_movement.storniert",
        require_audit_reason=True,
    )


# ---------------------------------------------------------------------------
# einkauf/purchase-order → bestellen (aus Angebot)
# ---------------------------------------------------------------------------

@router.post(
    "/einkauf/bestellungen/{entity_id}/actions/bestellen",
    response_model=MaskActionResult,
    summary="Bestellung aus Angebot erteilen (SPEC-P1-04)",
)
async def action_einkauf_bestellen(
    entity_id: str,
    body: dict[str, Any] = Body(default_factory=dict),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> MaskActionResult:
    def execute(db_: Session, payload: dict[str, Any], eid: str, tid: str) -> dict[str, Any]:
        return {
            "summary": "Bestellung aus Angebot erzeugt.",
            "affectedIds": [eid],
            "mutation": {"angebot_id": eid, "status": "bestellung_erzeugt", "tenant_id": tid},
        }

    return run_mask_action(
        db,
        action_key="bestellen",
        entity_type="purchase_order",
        entity_id=entity_id,
        tenant_id=tenant_id,
        body=body,
        execute_fn=execute,
        outbox_event_type="einkauf.bestellung.created_from_angebot",
    )


# ---------------------------------------------------------------------------
# lager/article-stock → wareneingang
# ---------------------------------------------------------------------------

@router.post(
    "/lager/artikel/{entity_id}/actions/wareneingang",
    response_model=MaskActionResult,
    summary="Wareneingang buchen (SPEC-P1-04)",
)
async def action_lager_wareneingang(
    entity_id: str,
    body: dict[str, Any] = Body(default_factory=dict),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> MaskActionResult:
    def validate(payload: dict[str, Any]) -> list[dict[str, Any]]:
        errors: list[dict[str, Any]] = []
        qty = payload.get("menge")
        if qty is not None and float(qty) <= 0:
            errors.append({"field": "menge", "message": "Menge muss > 0 sein.", "severity": "blocking"})
        return errors

    def execute(db_: Session, payload: dict[str, Any], eid: str, tid: str) -> dict[str, Any]:
        return {
            "summary": "Wareneingang gebucht.",
            "affectedIds": [eid],
            "mutation": {
                "artikel_id": eid,
                "menge": payload.get("menge"),
                "lager_id": payload.get("lager_id"),
                "status": "wareneingang_gebucht",
            },
        }

    return run_mask_action(
        db,
        action_key="wareneingang",
        entity_type="article_stock",
        entity_id=entity_id,
        tenant_id=tenant_id,
        body=body,
        validate_fn=validate,
        execute_fn=execute,
        outbox_event_type="lager.wareneingang.booked",
    )


# ---------------------------------------------------------------------------
# qualitaet/reklamation → abschliessen
# ---------------------------------------------------------------------------

@router.post(
    "/reklamationen/{entity_id}/actions/abschliessen",
    response_model=MaskActionResult,
    summary="Reklamation abschliessen (SPEC-P1-04)",
)
async def action_reklamation_abschliessen(
    entity_id: str,
    body: dict[str, Any] = Body(default_factory=dict),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> MaskActionResult:
    def execute(db_: Session, payload: dict[str, Any], eid: str, tid: str) -> dict[str, Any]:
        return _status_mutation("abgeschlossen", eid, {"reklamation_id": eid})

    return run_mask_action(
        db,
        action_key="abschliessen",
        entity_type="reklamation",
        entity_id=entity_id,
        tenant_id=tenant_id,
        body=body,
        execute_fn=execute,
        outbox_event_type="qualitaet.reklamation.closed",
    )


# ---------------------------------------------------------------------------
# crm/lead → qualifizieren
# ---------------------------------------------------------------------------

@router.post(
    "/crm/leads/{entity_id}/actions/qualifizieren",
    response_model=MaskActionResult,
    summary="Lead als Opportunity qualifizieren (SPEC-P1-04)",
)
async def action_crm_qualifizieren(
    entity_id: str,
    body: dict[str, Any] = Body(default_factory=dict),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> MaskActionResult:
    def execute(db_: Session, payload: dict[str, Any], eid: str, tid: str) -> dict[str, Any]:
        opportunity_id = payload.get("opportunity_id") or f"opp-{eid[:8]}"
        return {
            "summary": "Lead als Opportunity qualifiziert.",
            "affectedIds": [eid, opportunity_id],
            "mutation": {"lead_id": eid, "opportunity_id": opportunity_id, "status": "qualifiziert"},
        }

    return run_mask_action(
        db,
        action_key="qualifizieren",
        entity_type="lead",
        entity_id=entity_id,
        tenant_id=tenant_id,
        body=body,
        execute_fn=execute,
        outbox_event_type="crm.lead.qualified",
    )


# ---------------------------------------------------------------------------
# crm/opportunity → create_activity
# ---------------------------------------------------------------------------

@router.post(
    "/crm/opportunities/{entity_id}/actions/create_activity",
    response_model=MaskActionResult,
    summary="CRM-Aktivität für Opportunity anlegen (SPEC-P1-04)",
)
async def action_opportunity_create_activity(
    entity_id: str,
    body: dict[str, Any] = Body(default_factory=dict),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> MaskActionResult:
    def validate(payload: dict[str, Any]) -> list[dict[str, Any]]:
        errors: list[dict[str, Any]] = []
        if not str(payload.get("betreff", "")).strip():
            errors.append({"field": "betreff", "message": "Betreff ist Pflicht.", "severity": "blocking"})
        return errors

    def propose(eid: str, payload: dict[str, Any]) -> dict[str, Any]:
        return {
            "betreff": payload.get("betreff") or f"Follow-up Opportunity {eid[:8]}",
            "typ": payload.get("typ") or "Anruf",
            "opportunity_id": eid,
        }

    def execute(db_: Session, payload: dict[str, Any], eid: str, tid: str) -> dict[str, Any]:
        activity_id = payload.get("activity_id") or f"act-{eid[:8]}"
        return {
            "summary": f"Aktivität '{payload.get('betreff')}' angelegt.",
            "affectedIds": [eid, activity_id],
            "mutation": {"opportunity_id": eid, "activity_id": activity_id, **payload},
        }

    return run_mask_action(
        db,
        action_key="create_activity",
        entity_type="opportunity",
        entity_id=entity_id,
        tenant_id=tenant_id,
        body=body,
        validate_fn=validate,
        propose_fn=propose,
        execute_fn=execute,
        outbox_event_type="crm.opportunity.activity_created",
    )


# ---------------------------------------------------------------------------
# sales/delivery-note → drucken
# ---------------------------------------------------------------------------

@router.post(
    "/sales/delivery-notes/{entity_id}/actions/drucken",
    response_model=MaskActionResult,
    summary="Lieferschein drucken (SPEC-P1-04)",
)
async def action_delivery_note_drucken(
    entity_id: str,
    body: dict[str, Any] = Body(default_factory=dict),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> MaskActionResult:
    def execute(db_: Session, payload: dict[str, Any], eid: str, tid: str) -> dict[str, Any]:
        return {
            "summary": "Lieferschein-Druckauftrag erstellt.",
            "affectedIds": [eid],
            "mutation": {"delivery_note_id": eid, "format": payload.get("format", "pdf"), "status": "print_queued"},
        }

    return run_mask_action(
        db,
        action_key="drucken",
        entity_type="delivery_note",
        entity_id=entity_id,
        tenant_id=tenant_id,
        body=body,
        execute_fn=execute,
        outbox_event_type="sales.delivery_note.print_requested",
    )


# ---------------------------------------------------------------------------
# agrar/harvest-settlement → drucken
# ---------------------------------------------------------------------------

@router.post(
    "/agrar/harvest-settlements/{entity_id}/actions/drucken",
    response_model=MaskActionResult,
    summary="Ernte-Abrechnung drucken (SPEC-P1-04)",
)
async def action_harvest_settlement_drucken(
    entity_id: str,
    body: dict[str, Any] = Body(default_factory=dict),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> MaskActionResult:
    def execute(db_: Session, payload: dict[str, Any], eid: str, tid: str) -> dict[str, Any]:
        return {
            "summary": "Abrechnungs-Druckauftrag erstellt.",
            "affectedIds": [eid],
            "mutation": {"settlement_id": eid, "format": payload.get("format", "pdf"), "status": "print_queued"},
        }

    return run_mask_action(
        db,
        action_key="drucken",
        entity_type="harvest_settlement",
        entity_id=entity_id,
        tenant_id=tenant_id,
        body=body,
        execute_fn=execute,
        outbox_event_type="agrar.harvest_settlement.print_requested",
    )


# ---------------------------------------------------------------------------
# finance/payment-run → freigeben
# ---------------------------------------------------------------------------

@router.post(
    "/finance/payment-runs/{entity_id}/actions/freigeben",
    response_model=MaskActionResult,
    summary="Zahlungslauf freigeben (SPEC-P1-04)",
)
async def action_payment_run_freigeben(
    entity_id: str,
    body: dict[str, Any] = Body(default_factory=dict),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> MaskActionResult:
    def execute(db_: Session, payload: dict[str, Any], eid: str, tid: str) -> dict[str, Any]:
        return _status_mutation("freigegeben", eid, {"payment_run_id": eid, "freigegeben_von": payload.get("freigegeben_von")})

    return run_mask_action(
        db,
        action_key="freigeben",
        entity_type="payment_run",
        entity_id=entity_id,
        tenant_id=tenant_id,
        body=body,
        execute_fn=execute,
        outbox_event_type="finance.payment_run.approved",
        require_audit_reason=True,
    )
