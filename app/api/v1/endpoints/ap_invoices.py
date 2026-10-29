"""
Accounts Payable (AP) Invoices API
FIBU-AP-02: Eingangsrechnungen
"""

from fastapi import APIRouter, HTTPException, Depends, Body
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from typing import List, Optional, Any
from datetime import datetime, timedelta
import logging

from app.core.database import get_db
from app.auth.finance_roles import finance_admin, finance_read, finance_write
from app.core.tenant import get_tenant_id
from app.core.data_quality_enforcement import (
    build_dq_error_detail,
    evaluate_ap_invoice_datensatz,
)
from app.core import endpoint_gateways
from app.core.ap_approval_status import APPROVAL_STATUS_TO_DOCUMENT_STATUS
from app.documents.models import SalesInvoice  # Reusing model structure for now
from app.documents.router_helpers import get_repository, save_to_store, get_from_store, list_from_store, delete_from_store
from app.documents.repository import DocumentAlreadyExists, DocumentOwnershipError
from app.finance.steuerschluessel import Steuerklaerung, vorsteuergruppen
from app.services.finance_eingangsrechnung_buchung import positionen, summen

logger = logging.getLogger(__name__)
from app.api.v1.schemas.base import StatusResponse, TypedObjectOut
from app.api.v1.schemas.ap_invoices_schemas import ApInvoicesOut
from app.api.v1.schemas.mask_entity_contracts import FinanceApInvoiceOut, ap_invoice_mask_aliases
from app.core.akteur import gepruefter_akteur
from app.api.v1.schemas.ap_approval_workflow_schemas import ApprovalAction, ApprovalDecisionReference
from app.services.ap_invoice_approval_service import APApprovalWorkflowService


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
        "approval_request_id": getattr(response, "approval_request_id", None),
        "approval_can_decide": getattr(response, "can_decide", False),
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
    actor = gepruefter_akteur(nutzer)
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
        daten["createdBy"] = actor
        if repo is None:
            raise HTTPException(503, "Eingangsrechnung benoetigt den Dokumentspeicher")
        result = repo.save_document("ap_invoice", doc.number, daten, create_only=True)
        return {"status": "ok", "message": "AP Invoice created", "data": result}
    except HTTPException:
        raise
    except (DocumentAlreadyExists, DocumentOwnershipError):
        db.rollback()
        raise HTTPException(409, "Rechnungsnummer ist bereits vergeben") from None
    except IntegrityError as error:
        db.rollback()
        if getattr(error.orig, "pgcode", None) == "23505":
            raise HTTPException(409, "Rechnungsnummer ist bereits vergeben") from None
        raise HTTPException(503, "Eingangsrechnung konnte nicht gespeichert werden") from None
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(503, "Eingangsrechnung konnte nicht gespeichert werden") from None


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
    invoice_id: str, doc: SalesInvoice, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id),
    user: dict = Depends(finance_write),
) -> dict:
    """Aktualisiert eine bestehende Eingangsrechnung."""
    logger.info(f"Updating AP invoice: {invoice_id}")
    repo = get_repository(db)
    original = APApprovalWorkflowService(db, tenant_id).editable_invoice(invoice_id, user)

    doc.number = invoice_id  # Ensure number matches ID
    doc = calculate_invoice_totals(doc, db, tenant_id)
    dq_result = evaluate_ap_invoice_datensatz(_build_ap_invoice_dq_datensatz(doc))
    if not dq_result.bestanden:
        raise HTTPException(status_code=422, detail=build_dq_error_detail("APRechnung", dq_result))

    daten = doc.model_dump()
    daten["tenantId"] = tenant_id
    daten["createdBy"] = original.get("createdBy")
    daten["updatedBy"] = gepruefter_akteur(user)
    daten["status"] = "ENTWURF"
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
    invoice_id: str, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id),
    user: dict = Depends(finance_admin),
) -> dict:
    """Löscht eine Eingangsrechnung."""
    logger.info(f"Deleting AP invoice: {invoice_id}")
    repo = get_repository(db)
    APApprovalWorkflowService(db, tenant_id).editable_invoice(invoice_id, user, deleting=True)
    success = delete_from_store("ap_invoice", invoice_id, repo)
    if not success:
        raise HTTPException(status_code=404, detail="AP Invoice not found")
    return {"success": True, "message": "AP Invoice deleted"}


@router.post("/{invoice_id}/approve", summary="Ap invoice genehmigen",
    response_model=ApInvoicesOut, dependencies=[Depends(finance_admin)]
)
async def approve_ap_invoice(
    invoice_id: str,
    reference: ApprovalDecisionReference,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: dict = Depends(finance_admin),
) -> dict:
    """Same content-bound decision as the workflow endpoint; no implicit self-request."""
    action = ApprovalAction(invoice_id=invoice_id, approval_request_id=reference.approval_request_id,
                            action="approve", comment=reference.comment)
    response = APApprovalWorkflowService(db, tenant_id).decide(action, user)
    return {"status": "ok", "message": "AP review decision recorded", "data": response.model_dump(exclude_none=True)}


@router.post("/{invoice_id}/post", summary="Ap invoice erstellen",
    response_model=ApInvoicesOut, dependencies=[Depends(finance_admin)]
)
async def post_ap_invoice(
    invoice_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    nutzer: dict = Depends(finance_admin),
) -> dict:
    """Bucht eine Eingangsrechnung (erzeugt GL-Buchung + OP)."""
    return APApprovalWorkflowService(db, tenant_id).post_invoice(invoice_id, nutzer)


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
    from app.services.mask_action_runtime_service import run_delegated_mask_action, parse_action_body, MaskActionResult

    def action_for(payload: dict, eid: str) -> ApprovalAction:
        return ApprovalAction(invoice_id=eid, action="approve",
            approval_request_id=payload.get("approval_request_id"), comment=payload.get("comment"))

    async def pruefen(db_: Session, payload: dict, eid: str, tid: str) -> list[dict]:
        from pydantic import ValidationError
        try:
            APApprovalWorkflowService(db_, tid).validate_decision(action_for(payload, eid), user)
        except ValidationError:
            return [{"field": "approval_request_id", "message": "Aktuelle Freigabeanfrage erforderlich.", "severity": "blocking"}]
        except HTTPException as exc:
            return [{"field": "_approval", "message": str(exc.detail), "severity": "blocking"}]
        return []

    async def freigeben(db_: Session, payload: dict, eid: str, tid: str) -> str:
        response = APApprovalWorkflowService(db_, tid).decide(action_for(payload, eid), user)
        return f"Freigabeentscheidung gespeichert ({response.status})."

    # A cached outcome must not bypass today's person, policy or request checks.
    try:
        mode, _, key, payload = parse_action_body(body)
    except ValueError:
        return MaskActionResult(actionKey="freigeben", mode="invalid", success=False,
                                error="Ungueltiger Aktionsmodus").model_dump()
    errors = await pruefen(db, payload, entity_id, tenant_id)
    db.rollback()
    if errors:
        return MaskActionResult(actionKey="freigeben", mode=mode, success=False,
                                validationErrors=errors, error="Freigabepruefung fehlgeschlagen").model_dump()
    if key:
        import hashlib
        from app.core.akteur import gepruefter_akteur
        scoped = f"{tenant_id}:{gepruefter_akteur(user)}:{payload['approval_request_id']}:{key}"
        body = {**body, "_idempotencyKey": hashlib.sha256(scoped.encode()).hexdigest()}

    result = await run_delegated_mask_action(
        db,
        action_key="freigeben",
        entity_type="ap_invoice",
        entity_id=entity_id,
        tenant_id=tenant_id,
        body=body,
        check_fn=lambda *_: [],  # Same payload was checked before even considering a cached result.
        delegate_fn=freigeben,
        outbox_event_type="finance.ap_invoice.approval_decided",
    )
    return result.model_dump()
