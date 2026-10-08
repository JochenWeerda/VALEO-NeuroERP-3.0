"""
SPEC-P1-04 / UIX-053+: Mask Action CommandEndpoints mit ActionRuntime.

POST /api/v1/.../{entity_id}/actions/{action_key}
Unterstützt _mode: validate | dryRun | propose | execute

**Nur Aktionen mit Fachweg.** Bis zum 07.10.2026 standen hier neun Handler, die ein
Ergebnis-Dict bauten, Audit und Outbox schrieben und ``success: true`` meldeten —
ohne fachliche Wirkung. Das Ereignis ``finance.payment_run.approved`` speiste die
Projektion ``payment_run_cockpit``: Ein nicht freigegebener Zahlungslauf erschien im
Lesemodell als freigegeben. Jetzt delegiert jeder Handler an den echten Fachweg
(``run_delegated_mask_action``). Lead-Qualifizierung verwendet das kanonische
Leadregister; Ernte-PDFs speichern ihren Inhalt im PostgreSQL-Archiv.
Siehe ``docs/quality-assurance/user-decisions-lead-pdf-20261007.md``.
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.auth.finance_roles import finance_admin
from app.core.tenant import get_tenant_id
from app.services.mask_action_runtime_service import MaskActionResult, run_delegated_mask_action
from app.auth.deps import require_roles

router = APIRouter(tags=["mask-actions"])


@router.post("/agrar/settlements/{entity_id}/actions/drucken", response_model=MaskActionResult,
             summary="Ernte-Abrechnung als PDF in PostgreSQL archivieren")
async def action_settlement_drucken(
    entity_id: str, body: dict[str, Any] = Body(default_factory=dict),
    db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id),
    user: dict = Depends(require_roles("HARVEST_BEARBEITEN", "HARVEST_ADMIN", "AGRAR_BEARBEITEN", "AGRAR_ADMIN", "admin", "manager")),
) -> MaskActionResult:
    from app.services.agrar_settlement_service import AgrarSettlementService
    from app.services.settlement_pdf_service import SettlementPdfService

    async def check(session, payload, settlement_id, tenant):
        AgrarSettlementService(session, tenant).get_settlement(settlement_id)
        return []

    async def execute(session, payload, settlement_id, tenant):
        service = AgrarSettlementService(session, tenant)
        settlement, deductions = service.get_settlement(settlement_id)
        from app.infrastructure.models import BusinessPartner, Article
        supplier = session.query(BusinessPartner).filter(BusinessPartner.partner_id == settlement.supplier_id,
                                                        BusinessPartner.tenant_id == tenant).first()
        article = session.query(Article).filter(Article.id == settlement.article_id,
                                               Article.tenant_id == tenant).first() if settlement.article_id else None
        meta = SettlementPdfService(session, tenant).generate_and_archive(
            settlement, deductions, supplier, article, commit=False,
            created_by=str(user.get("sub") or user.get("id") or user.get("username") or "")[:100] or None)
        return f"PDF archiviert: {meta['download_url']} (SHA-256 {meta['sha256']})."

    return await run_delegated_mask_action(db, action_key="drucken", entity_type="agrar_settlement",
        entity_id=entity_id, tenant_id=tenant_id, body=body, check_fn=check, delegate_fn=execute,
        outbox_event_type="agrar.settlement.pdf_archived")


def _fehler(nachricht: str, feld: str = "_entity") -> list[dict[str, Any]]:
    return [{"field": feld, "message": nachricht, "severity": "blocking"}]


# ---------------------------------------------------------------------------
# finance/payment-run → freigeben
# ---------------------------------------------------------------------------

@router.post(
    "/finance/payment-runs/{entity_id}/actions/freigeben",
    response_model=MaskActionResult,
    summary="Zahlungslauf freigeben (SPEC-P1-04)",
    dependencies=[Depends(finance_admin)],
)
async def action_payment_run_freigeben(
    entity_id: str,
    body: dict[str, Any] = Body(default_factory=dict),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: dict = Depends(finance_admin),
) -> MaskActionResult:
    async def pruefen(db_: Session, payload: dict[str, Any], eid: str, tid: str) -> list[dict[str, Any]]:
        from app.services.payment_run_freigabe import pruefe_freigabe

        pruefe_freigabe(db_, eid, tid, str(user.get("sub") or "").strip())
        return []

    async def freigeben(db_: Session, payload: dict[str, Any], eid: str, tid: str) -> str:
        from app.api.v1.endpoints.payment_runs import ApprovePaymentRunRequest, approve_payment_run

        # Mandant aus dem Kontext, Freigeber = angemeldeter Nutzer; der Fachweg
        # prueft das Vier-Augen-Prinzip.
        await approve_payment_run(eid, ApprovePaymentRunRequest(), tenant_id=tid, db=db_, user=user)
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


# ---------------------------------------------------------------------------
# einkauf/angebot → bestellen
# ---------------------------------------------------------------------------

@router.post(
    "/einkauf/angebote/{entity_id}/actions/bestellen",
    response_model=MaskActionResult,
    summary="Bestellung aus Angebot erstellen (SPEC-P1-04)",
)
async def action_angebot_bestellen(
    entity_id: str,
    body: dict[str, Any] = Body(default_factory=dict),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> MaskActionResult:
    async def pruefen(db_: Session, payload: dict[str, Any], eid: str, tid: str) -> list[dict[str, Any]]:
        from app.services.einkauf_compat_service import _NICHT_BESTELLBAR, EinkaufCompatService

        zeile = EinkaufCompatService(db_, tid)._load_angebot_raw_row(eid)
        if zeile is None:
            return _fehler("Angebot nicht gefunden.")
        status = str(zeile._mapping.get("status") or "").upper()
        if status in _NICHT_BESTELLBAR:
            return _fehler(f"Angebot ist {status} und wird nicht bestellt.")
        positionen = db_.execute(
            text("SELECT COUNT(*) FROM einkauf_angebote_positionen WHERE angebot_id = :id"),
            {"id": zeile._mapping.get("id")},
        ).scalar()
        return [] if positionen else _fehler("Ein Angebot ohne Positionen wird nicht bestellt.")

    async def bestellen(db_: Session, payload: dict[str, Any], eid: str, tid: str) -> str:
        from app.services.einkauf_compat_service import EinkaufCompatService

        ergebnis = await EinkaufCompatService(db_, tid).convert_angebot_to_order(eid)
        return f"Bestellung {ergebnis.get('purchaseOrderNumber')} aus Angebot erstellt."

    return await run_delegated_mask_action(
        db,
        action_key="bestellen",
        entity_type="angebot",
        entity_id=entity_id,
        tenant_id=tenant_id,
        body=body,
        check_fn=pruefen,
        delegate_fn=bestellen,
        outbox_event_type="einkauf.bestellung.created_from_angebot",
    )


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
    """Gegenbuchung ueber den Storno-Dienst; die Begruendung wird zur Bemerkung."""

    async def pruefen(db_: Session, payload: dict[str, Any], eid: str, tid: str) -> list[dict[str, Any]]:
        from app.services.inventory_movement_direction import signed_quantity
        from app.services.inventory_stock_balance import current_stock

        zeile = db_.execute(
            text(
                "SELECT movement_type, quantity, source_document_type, article_id, warehouse_id "
                "FROM domain_inventory.inventory_stock_movements WHERE id = :id AND tenant_id = :tid"
            ),
            {"id": eid, "tid": tid},
        ).mappings().first()
        if zeile is None:
            return _fehler("Lagerbewegung nicht gefunden.")
        if str(zeile["source_document_type"] or "").upper() == "STORNO":
            return _fehler("Ein Storno wird nicht storniert.")
        wirkung = signed_quantity(zeile["movement_type"], float(zeile["quantity"] or 0))
        if wirkung == 0:
            return _fehler("Die Bewegung ist bestandsneutral; es gibt nichts zu stornieren.")
        bestand = current_stock(db_, tenant_id=tid, article_id=str(zeile["article_id"]),
                                warehouse_id=str(zeile["warehouse_id"]))
        if bestand - wirkung < 0:
            return _fehler("Der Storno machte den Bestand negativ; die Ware ist bereits weiter gebucht.")
        return []

    async def stornieren(db_: Session, payload: dict[str, Any], eid: str, tid: str) -> str:
        from app.services.inventory_correction_service import CorrectionError, storno_korrektur

        try:
            ergebnis = storno_korrektur(db_, eid, tid, bemerkung=payload.get("_begruendung"))
        except CorrectionError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        return f"Gegenbuchung {ergebnis['movement_type']} {ergebnis['quantity']:g} gebucht."

    # Die Begruendung des Stornos ist die Bemerkung der Gegenbuchung.
    nutzlast = dict(body)
    nutzlast["_begruendung"] = body.get("_auditReason")
    return await run_delegated_mask_action(
        db,
        action_key="stornieren",
        entity_type="stock_movement",
        entity_id=entity_id,
        tenant_id=tenant_id,
        body=nutzlast,
        check_fn=pruefen,
        delegate_fn=stornieren,
        outbox_event_type="lager.stock_movement.storniert",
        require_audit_reason=True,
    )


# ---------------------------------------------------------------------------
# crm/opportunity → create_activity
# ---------------------------------------------------------------------------

_AKTIVITAETSARTEN = {"CALL", "EMAIL", "MEETING", "NOTE"}


@router.post(
    "/crm/opportunities/{entity_id}/actions/create_activity",
    response_model=MaskActionResult,
    summary="CRM-Aktivitaet fuer Opportunity anlegen (SPEC-P1-04)",
)
async def action_opportunity_create_activity(
    entity_id: str,
    body: dict[str, Any] = Body(default_factory=dict),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> MaskActionResult:
    """Legt die Aktivitaet ueber den mandantengebundenen Fachweg an.

    Betreff und Typ fragt die Maske deklarativ (``inputFields`` der Aktion).
    """

    async def pruefen(db_: Session, payload: dict[str, Any], eid: str, tid: str) -> list[dict[str, Any]]:
        from app.api.v1.endpoints.opportunities import _opportunity_im_mandanten

        fehler: list[dict[str, Any]] = []
        if not str(payload.get("subject") or "").strip():
            fehler += _fehler("Betreff fehlt.", "subject")
        if str(payload.get("activity_type") or "").upper() not in _AKTIVITAETSARTEN:
            fehler += _fehler("Typ muss Anruf, E-Mail, Termin oder Notiz sein.", "activity_type")
        try:
            await _opportunity_im_mandanten(db_, eid, tid)
        except HTTPException:
            fehler += _fehler("Opportunity nicht gefunden.")
        return fehler

    async def anlegen(db_: Session, payload: dict[str, Any], eid: str, tid: str) -> str:
        from app.api.v1.endpoints.opportunities import add_opportunity_activity

        await add_opportunity_activity(
            eid,
            activity_type=str(payload["activity_type"]).upper(),
            subject=str(payload["subject"]).strip(),
            notes=payload.get("notes"),
            assigned_to=None,
            db=db_,
            tenant_id=tid,
        )
        return f"Aktivitaet '{str(payload['subject']).strip()}' angelegt."

    return await run_delegated_mask_action(
        db,
        action_key="create_activity",
        entity_type="opportunity",
        entity_id=entity_id,
        tenant_id=tenant_id,
        body=body,
        check_fn=pruefen,
        delegate_fn=anlegen,
        outbox_event_type="crm.opportunity.activity_created",
    )


# ---------------------------------------------------------------------------
# einkauf/anlieferavis → wareneingang
# ---------------------------------------------------------------------------

@router.post(
    "/einkauf/anlieferavis/{entity_id}/actions/wareneingang",
    response_model=MaskActionResult,
    summary="Wareneingang aus dem Anlieferavis buchen (SPEC-P1-04)",
)
async def action_avis_wareneingang(
    entity_id: str,
    body: dict[str, Any] = Body(default_factory=dict),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> MaskActionResult:
    """Lieferschein-Nr. und Lager fragt die Maske deklarativ (``inputFields``)."""
    from app.services.wareneingang_avis_service import (
        WareneingangAvisError,
        buche_wareneingang_aus_avis,
        pruefe_wareneingang,
    )

    async def pruefen(db_: Session, payload: dict[str, Any], eid: str, tid: str) -> list[dict[str, Any]]:
        try:
            pruefe_wareneingang(db_, eid, tid, str(payload.get("lager_id") or ""), str(payload.get("lieferschein_nr") or ""))
        except WareneingangAvisError as exc:
            return _fehler(str(exc))
        return []

    async def buchen(db_: Session, payload: dict[str, Any], eid: str, tid: str) -> str:
        try:
            ergebnis = buche_wareneingang_aus_avis(
                db_, eid, tid, str(payload["lager_id"]), str(payload["lieferschein_nr"]), payload.get("operator")
            )
        except WareneingangAvisError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        return (f"Wareneingang zu Bestellung {ergebnis['bestellnummer']} gebucht "
                f"({ergebnis['positionen']} Positionen, Lieferschein {ergebnis['lieferschein_nr']}).")

    return await run_delegated_mask_action(
        db,
        action_key="wareneingang",
        entity_type="anlieferavis",
        entity_id=entity_id,
        tenant_id=tenant_id,
        body=body,
        check_fn=pruefen,
        delegate_fn=buchen,
        outbox_event_type="einkauf.wareneingang.gebucht",
    )
