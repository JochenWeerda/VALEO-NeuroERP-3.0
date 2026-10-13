"""
Accounts Payable (AP) Invoices API
FIBU-AP-02: Eingangsrechnungen
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Body
from sqlalchemy.orm import Session
from typing import List, Optional, Any
from datetime import datetime, timedelta
import logging

from app.core.database import get_db
from app.auth.finance_roles import finance_admin, finance_read, finance_write
from app.services.finance_freigabe import EingangsrechnungFreigabe, verlange_oder_409
from app.core.tenant import get_tenant_id
from app.core.data_quality_enforcement import (
    build_dq_error_detail,
    evaluate_ap_invoice_datensatz,
)
from app.core import endpoint_gateways
from app.core.fibu_audit import log_fibu_audit
from app.core.ap_approval_status import APPROVAL_STATUS_TO_DOCUMENT_STATUS
from app.documents.models import SalesInvoice  # Reusing model structure for now
from app.documents.router_helpers import get_repository, save_to_store, get_from_store, list_from_store, delete_from_store
from app.domains.shared.events import get_event_publisher
from app.domains.shared.process_events import APInvoicePosted
from app.infrastructure.eventbus.outbox import OutboxPublisher
from app.finance.steuerschluessel import Steuerklaerung, vorsteuergruppen
from app.services.finance_eingangsrechnung_buchung import buche_eingangsrechnung, positionen, summen

logger = logging.getLogger(__name__)
from app.api.v1.schemas.base import StatusResponse, TypedObjectOut
from app.api.v1.schemas.ap_invoices_schemas import ApInvoicesOut
from app.api.v1.schemas.mask_entity_contracts import FinanceApInvoiceOut, ap_invoice_mask_aliases
from app.core import finance_periods


router = APIRouter(prefix="/ap/invoices", tags=["finance", "ap", "invoices"])


def _build_ap_invoice_dq_datensatz(invoice: SalesInvoice) -> dict[str, Any]:
    return {
        "rechnungsnummer": invoice.number,
        "lieferant_id": invoice.customerId,
        "faelligkeit": invoice.dueDate,
        "brutto_betrag_eur": invoice.totalGross,
        "waehrung": "EUR",
    }


def _compute_ap_invoice_semantic_status(invoice: dict[str, Any]) -> str:
    document_status = str(invoice.get("status") or "ENTWURF")
    approval_status = invoice.get("approval_status")

    if document_status in {"VERBUCHT", "BEZAHLT", "TEILWEISE_FREIGEGEBEN"}:
        return document_status
    if approval_status == "pending":
        return "ZUR_FREIGABE"
    if approval_status == "partially_approved":
        return "TEILWEISE_FREIGEGEBEN"
    if approval_status == "approved":
        return "FREIGEGEBEN"
    if approval_status == "rejected":
        return "ABGELEHNT"
    return document_status


def _serialize_approval_snapshot(response) -> dict[str, Any]:
    return {
        "approval_status": response.status,
        "approval_required_approvals": response.required_approvals,
        "approval_current_approvals": response.current_approvals,
        "approval_override_resolution": response.override_resolution.model_dump(exclude_none=True),
        "approval_explainability": response.explainability.model_dump(exclude_none=True),
    }


async def _load_invoice_approval_status(invoice: dict[str, Any], db: Session):
    gateway = endpoint_gateways.get_approval_workflow_gateway()
    if gateway is None:
        from app.api.v1.endpoints.ap_approval_workflow import get_approval_status

        return await get_approval_status(
            invoice["number"],
            tenant_id=invoice.get("tenantId", "system"),
            db=db,
        )
    return await gateway.get_status(invoice["number"], invoice.get("tenantId", "system"), db)


async def _enrich_invoice_with_approval(invoice: dict[str, Any], db: Session) -> dict[str, Any]:
    enriched = dict(invoice)
    response = await _load_invoice_approval_status(enriched, db)
    enriched.update(_serialize_approval_snapshot(response))
    enriched["semantic_status"] = _compute_ap_invoice_semantic_status(enriched)
    return ap_invoice_mask_aliases(enriched)


async def _store_ap_invoice_posted_event_in_outbox(
    db,
    *,
    tenant_id: str,
    invoice_id: str,
    posted_by: str,
    journal_entry_id: str | None,
) -> None:
    event = APInvoicePosted(
        aggregate_id=invoice_id,
        timestamp=datetime.utcnow(),
        tenant_id=tenant_id,
        workflow_instance_id=f"wf-ap-{invoice_id}",
        invoice_id=invoice_id,
        posted_by=posted_by,
        journal_entry_id=journal_entry_id,
    )
    outbox = OutboxPublisher(db, get_event_publisher())
    await outbox.store_event(event, tenant_id=tenant_id)


def calculate_invoice_totals(invoice: SalesInvoice, db: Session, tenant_id: str) -> SalesInvoice:
    """Netto, Vorsteuer und Brutto der Eingangsrechnung aus den Steuerschluesseln ihrer Positionen.

    Bis zum 13.10.2026 rechnete der Weg mit dem Satz der Position (``vatRate``), den die Maske frei eingab.
    Laesst sich die Vorsteuer nicht eindeutig bestimmen, bleibt sie offen: Netto aus den Positionen, Steuer 0,
    und der Beleg traegt den Pruefgrund. Gebucht wird so eine Rechnung nicht.
    """
    daten = invoice.model_dump()
    try:
        gruppen = vorsteuergruppen(db, tenant_id, positionen(daten))
    except Steuerklaerung as klaerung:
        netto = sum(line.qty * (line.price or 0) for line in invoice.lines)
        invoice.subtotalNet = round(netto, 2)
        invoice.totalTax = 0.0
        invoice.totalGross = invoice.subtotalNet
        invoice.steuerPruefgrund = str(klaerung)
        return invoice
    netto, steuer, brutto = summen(gruppen)
    saetze = {g.tax_code: g.satz for g in gruppen}
    for line in invoice.lines:
        line.taxCode = str(line.taxCode).strip()
        line.vatRate = float(saetze[line.taxCode])
    invoice.subtotalNet, invoice.totalTax, invoice.totalGross = float(netto), float(steuer), float(brutto)
    invoice.steuerPruefgrund = None
    return invoice


def _rechnung(repo: Any, invoice_id: str, tenant_id: str) -> dict:
    """Die Rechnung dieses Mandanten — fremd oder mandantenlos ist 404.

    Bis 07.10.2026 lasen alle Wege dieses Moduls ohne Mandant; Buchen schrieb
    Journal und offenen Posten mit dem Mandanten aus dem Dokument.
    """
    from app.api.v1.endpoints.ap_approval_workflow import _ensure_invoice_tenant_access

    return _ensure_invoice_tenant_access(get_from_store("ap_invoice", invoice_id, repo), tenant_id)


@router.post("/", summary="Ap invoice anlegen",
    response_model=ApInvoicesOut, status_code=201, dependencies=[Depends(finance_write)]
)
async def create_ap_invoice(
    doc: SalesInvoice,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    nutzer: dict = Depends(finance_write),
) -> dict:
    """Erstellt eine neue Eingangsrechnung (Kreditoren)."""
    logger.info(f"Creating AP invoice: {doc.number}")
    try:
        doc.date = datetime.now().isoformat()[:10]  # Set current date
        doc.dueDate = (datetime.now() + timedelta(days=30)).isoformat()[:10]  # Default 30 days due
        doc.status = "ENTWURF"  # Initial status

        doc = calculate_invoice_totals(doc, db, tenant_id)
        dq_result = evaluate_ap_invoice_datensatz(_build_ap_invoice_dq_datensatz(doc))
        if not dq_result.bestanden:
            raise HTTPException(status_code=422, detail=build_dq_error_detail("APRechnung", dq_result))

        repo = get_repository(db)
        # Der Speicher ist global nach Nummer eindeutig: Anlegen darf eine fremde
        # (oder eigene) Rechnung gleicher Nummer nicht ueberschreiben.
        if get_from_store("ap_invoice", doc.number, repo):
            raise HTTPException(status_code=409, detail=f"Rechnungsnummer {doc.number} ist bereits vergeben")
        daten = doc.model_dump()
        daten["tenantId"] = tenant_id
        # Wer angelegt hat, gibt spaeter nicht frei (Funktionstrennung, APPROVAL-001).
        daten["createdBy"] = str((nutzer or {}).get("sub") or "") if isinstance(nutzer, dict) else ""
        result = save_to_store("ap_invoice", doc.number, daten, repo)
        return {"status": "ok", "message": "AP Invoice created", "data": result}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating AP invoice: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create AP invoice: {str(e)}")


@router.get("/{invoice_id}", summary="Ap invoice abrufen",
    response_model=FinanceApInvoiceOut, dependencies=[Depends(finance_read)]
)
async def get_ap_invoice(
    invoice_id: str, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)
) -> dict:
    """Ruft eine Eingangsrechnung anhand ihrer ID ab."""
    logger.info(f"Fetching AP invoice: {invoice_id}")
    invoice = _rechnung(get_repository(db), invoice_id, tenant_id)
    return await _enrich_invoice_with_approval(invoice, db)


@router.put("/{invoice_id}", summary="Ap invoice aktualisieren",
    response_model=ApInvoicesOut, dependencies=[Depends(finance_write)]
)
async def update_ap_invoice(
    invoice_id: str, doc: SalesInvoice, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)
) -> dict:
    """Aktualisiert eine bestehende Eingangsrechnung."""
    logger.info(f"Updating AP invoice: {invoice_id}")
    repo = get_repository(db)
    _rechnung(repo, invoice_id, tenant_id)

    doc.number = invoice_id  # Ensure number matches ID
    doc = calculate_invoice_totals(doc, db, tenant_id)
    dq_result = evaluate_ap_invoice_datensatz(_build_ap_invoice_dq_datensatz(doc))
    if not dq_result.bestanden:
        raise HTTPException(status_code=422, detail=build_dq_error_detail("APRechnung", dq_result))

    daten = doc.model_dump()
    daten["tenantId"] = tenant_id
    result = save_to_store("ap_invoice", doc.number, daten, repo)
    return {"status": "ok", "message": "AP Invoice updated", "data": result}


@router.get("/", summary="Ap invoices auflisten",
    response_model=list[ApInvoicesOut], dependencies=[Depends(finance_read)]
)
async def list_ap_invoices(
    skip: int = 0,
    limit: int = 100,
    query: Optional[str] = None,
    status: Optional[str] = None,
    supplier_id: Optional[str] = None,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> List[dict]:
    """Listet Eingangsrechnungen auf, optional mit Filterung."""
    logger.info(f"Listing AP invoices with skip={skip}, limit={limit}, query={query}, status={status}, supplier_id={supplier_id}")
    repo = get_repository(db)
    result = list_from_store("ap_invoice", skip, limit, None, repo)
    all_invoices = result.get("data", []) if isinstance(result, dict) else []

    filtered_invoices = []
    for inv in all_invoices:
        if str(inv.get("tenantId") or "") != tenant_id:
            continue
        enriched = await _enrich_invoice_with_approval(inv, db)
        match = True
        if query and not (query.lower() in enriched.get("number", "").lower() or
                         query.lower() in enriched.get("customerId", "").lower() or
                         query.lower() in enriched.get("notes", "").lower()):
            match = False
        if status and enriched.get("semantic_status", enriched.get("status", "")).lower() != status.lower():
            match = False
        if supplier_id and enriched.get("customerId", "").lower() != supplier_id.lower():
            match = False
        if match:
            filtered_invoices.append(enriched)

    return filtered_invoices[skip : skip + limit]


@router.delete("/{invoice_id}", summary="Ap invoice löschen",
    response_model=StatusResponse, dependencies=[Depends(finance_admin)]
)
async def delete_ap_invoice(
    invoice_id: str, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)
) -> dict:
    """Löscht eine Eingangsrechnung."""
    logger.info(f"Deleting AP invoice: {invoice_id}")
    repo = get_repository(db)
    _rechnung(repo, invoice_id, tenant_id)
    success = delete_from_store("ap_invoice", invoice_id, repo)
    if not success:
        raise HTTPException(status_code=404, detail="AP Invoice not found")
    return {"success": True, "message": "AP Invoice deleted"}


@router.post("/{invoice_id}/approve", summary="Ap invoice genehmigen",
    response_model=ApInvoicesOut, dependencies=[Depends(finance_admin)]
)
async def approve_ap_invoice(
    invoice_id: str,
    approved_by: Optional[str] = Query(None, description="Ignoriert — Freigeber ist der angemeldete Nutzer"),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: dict = Depends(finance_admin),
) -> dict:
    """Genehmigt eine Eingangsrechnung (für Freigabeworkflow).

    Freigeber ist der angemeldete Nutzer; ``approved_by`` wird nicht mehr uebernommen.
    """
    approver_id = str(user.get("sub") or "").strip()
    logger.info(f"Approving AP invoice: {invoice_id} by {approver_id}")
    repo = get_repository(db)
    invoice = _rechnung(repo, invoice_id, tenant_id)

    gateway = endpoint_gateways.get_approval_workflow_gateway()
    if gateway is None:
        from app.api.v1.endpoints.ap_approval_workflow import approve_invoice

        response = await approve_invoice(
            type("ApprovalActionCompat", (), {
                "invoice_id": invoice_id,
                "approved_by": approver_id,
                "action": "approve",
                "comment": None,
            })(),
            tenant_id=tenant_id,
            db=db,
            user=user,
        )
    else:
        current_status = await gateway.get_status(invoice_id, tenant_id, db)
        if current_status.status == "not_requested":
            await gateway.request_approval(invoice_id, tenant_id, approver_id, None, db)
        response = await gateway.approve_invoice(invoice_id, tenant_id, approver_id, "approve", None, db)

    invoice["status"] = APPROVAL_STATUS_TO_DOCUMENT_STATUS.get(response.status, invoice.get("status", "ENTWURF"))
    invoice["approvedBy"] = approver_id
    invoice["approvedAt"] = datetime.now().isoformat()
    save_to_store("ap_invoice", invoice_id, invoice, repo)
    return {
        "status": "ok",
        "message": "AP Invoice approved",
        "data": response.model_dump(exclude_none=True),
    }


@router.post("/{invoice_id}/post", summary="Ap invoice erstellen",
    response_model=ApInvoicesOut, dependencies=[Depends(finance_admin)]
)
async def post_ap_invoice(
    invoice_id: str,
    posted_by: str = Query(...),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    nutzer: dict = Depends(finance_admin),
) -> dict:
    """Bucht eine Eingangsrechnung (erzeugt GL-Buchung + OP)."""
    logger.info(f"Posting AP invoice: {invoice_id} by {posted_by}")
    repo = get_repository(db)
    # Ab hier ist invoice["tenantId"] der gepruefte Mandant.
    invoice = _rechnung(repo, invoice_id, tenant_id)

    # Check approval status via workflow API
    try:
        from app.api.v1.endpoints.ap_approval_workflow import get_approval_status
        approval_status = await get_approval_status(invoice_id, tenant_id=invoice.get("tenantId", "system"), db=db)
        
        if not approval_status.can_post:
            raise HTTPException(
                status_code=400,
                detail=f"Invoice must be approved before posting. Current status: {approval_status.status}, Required: {approval_status.required_approvals}, Current: {approval_status.current_approvals}"
            )
    except ImportError:
        # Fallback to simple status check if workflow API not available
        if invoice.get("status") != "FREIGEGEBEN":
            raise HTTPException(
                status_code=400,
                detail="Invoice must be approved before posting"
            )

    # FIBU-GL-05: block posting in closed periods
    invoice_date = invoice.get("date", datetime.now().isoformat()[:10])
    period = str(invoice_date)[:7]
    gesperrt = finance_periods.gesperrter_zustand(
        db, invoice.get("tenantId", "system"), period
    )
    if gesperrt:
        raise HTTPException(
            status_code=403,
            detail=finance_periods.meldung(period, gesperrt),
        )

    # Zentrale Freigabe (APPROVAL-001): Eine Finanzrechnung hat keinen Rechnungsabgleich und braucht deshalb die
    # Freigabe einer zweiten Person — zusaetzlich zum Freigabeablauf dieses Moduls.
    freigabe = EingangsrechnungFreigabe(db, tenant_id)
    akteur = str(nutzer.get("sub") or "") if isinstance(nutzer, dict) else None
    try:
        verlange_oder_409(freigabe, freigabe.vorgang_aus(invoice_id, invoice), "post", akteur)
    except HTTPException:
        db.rollback()
        raise
    # Journal, offener Posten und Beleg in einer Transaktion. Scheitert etwas, bleibt die Rechnung freigegeben.
    try:
        je_id, gruppen = buche_eingangsrechnung(
            db, tenant_id, invoice_id=invoice_id, invoice=invoice, posted_by=posted_by)
    except Steuerklaerung as klaerung:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail=f"Eingangsrechnung {invoice.get('number', invoice_id)} nicht gebucht, bitte prüfen: {klaerung}",
        ) from klaerung
    except Exception:
        db.rollback()
        raise
    netto, steuer, brutto = summen(gruppen)
    invoice["subtotalNet"], invoice["totalTax"], invoice["totalGross"] = float(netto), float(steuer), float(brutto)
    invoice["steuerPruefgrund"] = None
    invoice["status"] = "VERBUCHT"
    invoice["postedBy"] = posted_by
    invoice["postedAt"] = datetime.now().isoformat()
    invoice["journalEntryId"] = je_id
    log_fibu_audit(
        db, tenant_id, "create", "journal_entry", je_id,
        {"source": "ap_invoice", "invoice_id": invoice_id},
        request=None,
    )
    result = repo.save_document("ap_invoice", invoice_id, invoice, commit=False) if repo is not None \
        else save_to_store("ap_invoice", invoice_id, invoice, repo)
    db.commit()
    try:
        await _store_ap_invoice_posted_event_in_outbox(
            db, tenant_id=tenant_id, invoice_id=invoice_id, posted_by=posted_by, journal_entry_id=je_id,
        )
    except Exception as exc:  # noqa: BLE001 — das Ereignis ist Benachrichtigung; die Buchung steht
        db.rollback()
        logger.warning("Could not store AP invoice posted outbox event: %s", exc)
    return {"status": "ok", "message": "AP Invoice posted", "data": result}


@router.post("/{entity_id}/actions/freigeben", response_model=TypedObjectOut, summary="Eingangsrechnung freigeben (SPEC-P1-04)",
             dependencies=[Depends(finance_admin)])
async def action_freigeben(
    entity_id: str,
    body: dict = Body(default_factory=dict),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: dict = Depends(finance_admin),
):
    """Delegiert an den Freigabeweg. Bis zum 07.10.2026 meldete diese Aktion Erfolg,
    ohne die Rechnung anzufassen."""
    from app.services.mask_action_runtime_service import run_delegated_mask_action

    async def pruefen(db_: Session, payload: dict, eid: str, tid: str) -> list[dict]:
        rechnung = get_from_store("ap_invoice", eid, get_repository(db_))
        # Der Freigabeweg liest ohne Mandantenfilter; hier wird er nachgeholt.
        if not rechnung or str(rechnung.get("tenantId") or "") != tid:
            return [{"field": "_entity", "message": "Eingangsrechnung nicht gefunden.", "severity": "blocking"}]
        return []

    async def freigeben(db_: Session, payload: dict, eid: str, tid: str) -> str:
        await approve_ap_invoice(eid, approved_by=None, db=db_, tenant_id=tid, user=user)
        return "Eingangsrechnung freigegeben."

    result = await run_delegated_mask_action(
        db,
        action_key="freigeben",
        entity_type="ap_invoice",
        entity_id=entity_id,
        tenant_id=tenant_id,
        body=body,
        check_fn=pruefen,
        delegate_fn=freigeben,
        outbox_event_type="finance.ap_invoice.approved",
    )
    return result.model_dump()
