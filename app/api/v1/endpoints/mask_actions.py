"""
SPEC-P1-04 / UIX-053+: Mask Action CommandEndpoints mit ActionRuntime.

POST /api/v1/.../{entity_id}/actions/{action_key}
Unterstützt _mode: validate | dryRun | propose | execute

**Nur Aktionen mit Fachweg.** Bis zum 07.10.2026 standen hier neun Handler, die ein
Ergebnis-Dict bauten, Audit und Outbox schrieben und ``success: true`` meldeten —
ohne fachliche Wirkung. Das Ereignis ``finance.payment_run.approved`` speiste die
Projektion ``payment_run_cockpit``: Ein nicht freigegebener Zahlungslauf erschien im
Lesemodell als freigegeben. Jetzt delegiert jeder Handler an den echten Fachweg
(``run_delegated_mask_action``). Die sechs Aktionen ohne Fachweg (Lead qualifizieren,
Opportunity-Aktivitaet, Angebot bestellen, Wareneingang am Artikel, Lagerbewegung
stornieren, Ernteabrechnung drucken) haben keinen Endpunkt mehr; ihre Maske nennt
den ``stubReason``. Siehe ``docs/quality-assurance/mask-aktionen-wirkung-20261007.md``.
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.mask_action_runtime_service import MaskActionResult, run_delegated_mask_action

router = APIRouter(tags=["mask-actions"])


def _fehler(nachricht: str, feld: str = "_entity") -> list[dict[str, Any]]:
    return [{"field": feld, "message": nachricht, "severity": "blocking"}]


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
    async def pruefen(db_: Session, payload: dict[str, Any], eid: str, tid: str) -> list[dict[str, Any]]:
        status = db_.execute(
            text("SELECT status FROM domain_erp.payment_runs WHERE id = :id AND tenant_id = :tid"),
            {"id": eid, "tid": tid},
        ).scalar()
        if status is None:
            return _fehler("Zahlungslauf nicht gefunden.")
        if status != "draft":
            return _fehler(f"Zahlungslauf ist nicht im Entwurf und kann nicht freigegeben werden (Status: {status}).")
        return []

    async def freigeben(db_: Session, payload: dict[str, Any], eid: str, tid: str) -> str:
        from app.api.v1.endpoints.payment_runs import ApprovePaymentRunRequest, approve_payment_run

        # Der Mandant kommt aus dem geprueften Kontext, nicht aus dem Query-Parameter
        # des Fachwegs.
        await approve_payment_run(
            eid,
            ApprovePaymentRunRequest(approved_by=str(payload.get("freigegeben_von") or "Maske")),
            tenant_id=tid,
            db=db_,
        )
        return "Zahlungslauf freigegeben."

    return await run_delegated_mask_action(
        db,
        action_key="freigeben",
        entity_type="payment_run",
        entity_id=entity_id,
        tenant_id=tenant_id,
        body=body,
        check_fn=pruefen,
        delegate_fn=freigeben,
        outbox_event_type="finance.payment_run.approved",
        require_audit_reason=True,
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
    async def pruefen(db_: Session, payload: dict[str, Any], eid: str, tid: str) -> list[dict[str, Any]]:
        status = db_.execute(
            text("SELECT status FROM domain_sales.delivery_notes WHERE id = :id AND tenant_id = :tid"),
            {"id": eid, "tid": tid},
        ).scalar()
        if status is None:
            return _fehler("Lieferschein nicht gefunden.")
        if status in ("posted", "printed", "delivered") and not str(payload.get("attestation") or "").strip():
            return _fehler(
                "Attestation reason required for printing posted delivery notes — "
                "ein Nachdruck braucht eine Begruendung.",
                "attestation",
            )
        return []

    async def drucken(db_: Session, payload: dict[str, Any], eid: str, tid: str) -> str:
        from app.api.v1.endpoints.sales_delivery_notes import print_delivery_note

        await print_delivery_note(
            eid, attestation=str(payload.get("attestation") or "").strip() or None,
            tenant_id=tid, db=db_, request=None,
        )
        return "Lieferschein gedruckt."

    return await run_delegated_mask_action(
        db,
        action_key="drucken",
        entity_type="delivery_note",
        entity_id=entity_id,
        tenant_id=tenant_id,
        body=body,
        check_fn=pruefen,
        delegate_fn=drucken,
        outbox_event_type="sales.delivery_note.print_requested",
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
    async def pruefen(db_: Session, payload: dict[str, Any], eid: str, tid: str) -> list[dict[str, Any]]:
        from app.api.v1.endpoints.reklamation_api import _query_reklamation
        from app.core.reklamation import ReklamationsStatus, ReklamationZustandsmaschine

        try:
            zeile = _query_reklamation(db_, eid, tid)
        except HTTPException:
            return _fehler("Reklamation nicht gefunden.")
        try:
            ReklamationZustandsmaschine.pruefe_statuswechsel(
                ReklamationsStatus(zeile.status), ReklamationsStatus.GESCHLOSSEN
            )
        except ValueError as exc:
            return _fehler(str(exc))
        return []

    async def abschliessen(db_: Session, payload: dict[str, Any], eid: str, tid: str) -> str:
        from app.api.v1.endpoints.reklamation_api import ReklamationTransitionRequest, transition_status
        from app.core.reklamation import ReklamationsStatus

        transition_status(
            eid,
            ReklamationTransitionRequest(
                neuer_status=ReklamationsStatus.GESCHLOSSEN.value,
                aktor_id=str(payload.get("aktor_id") or "Maske"),
                kommentar=payload.get("kommentar"),
            ),
            db=db_,
            tenant_id=tid,
        )
        return "Reklamation abgeschlossen."

    return await run_delegated_mask_action(
        db,
        action_key="abschliessen",
        entity_type="reklamation",
        entity_id=entity_id,
        tenant_id=tenant_id,
        body=body,
        check_fn=pruefen,
        delegate_fn=abschliessen,
        outbox_event_type="qualitaet.reklamation.closed",
    )
