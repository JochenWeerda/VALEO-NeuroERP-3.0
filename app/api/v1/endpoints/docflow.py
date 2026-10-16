"""Canonical Docflow command endpoints (DOCFLOW-P0-01..03)."""

from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ....core.database import get_db
from app.core.tenant import get_tenant_id
from app.auth.beleg_roles import darf, verlange
from app.auth.deps import get_current_user
from app.core.exceptions import ConflictError, EntityNotFoundError, ValidationFailedError
from app.services.docflow_freigabe import DocflowFreigabe
from app.services.docflow_service import DocflowService, POS_TYPES

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict as _ConfigDict
from app.api.v1.schemas.base import TypedObjectOut


class DocflowOut(BaseSchema):
    model_config = _ConfigDict(extra="allow")


router = APIRouter()

def _docflow_tenant(
    tenant_id: Optional[str] = Query(None),
    verified_tenant: str = Depends(get_tenant_id),
) -> str:
    """The old selector may confirm the identity, never select another tenant."""
    if tenant_id is not None and tenant_id != verified_tenant:
        raise HTTPException(status_code=403, detail="Tenant selector does not match verified identity")
    return verified_tenant


# ── Pydantic schemas ──────────────────────────────────────────────────────────

class DocflowItemOut(BaseModel):
    id: str
    line_number: int
    source_line_id: Optional[str] = None
    article_number: str
    description: Optional[str] = None
    quantity: float
    unit: Optional[str] = None
    unit_price: float
    discount_percent: float
    tax_code: Optional[str] = None
    expense_account: Optional[str] = None
    tax_rate: float
    line_total_net: float
    line_total_tax: float
    line_total_gross: float


class DocflowHeaderOut(BaseModel):
    id: str
    tenant_id: str
    doc_type: str
    doc_number: str
    status: str
    source_system: str
    source_ref: Optional[str] = None
    customer_id: Optional[str] = None
    supplier_id: Optional[str] = None
    currency: str
    total_net: float
    total_tax: float
    total_gross: float
    document_date: datetime
    posting_date: Optional[date] = None
    version: int
    created_at: datetime
    updated_at: datetime
    items: list[DocflowItemOut] = Field(default_factory=list)
    pos_compliance: Optional[dict[str, Any]] = None
    printed_at: Optional[datetime] = None
    printed_by: Optional[str] = None
    print_count: int = 0
    exported_at: Optional[datetime] = None
    exported_by: Optional[str] = None


class DocflowConvertRequest(BaseModel):
    target_doc_type: str = Field(..., min_length=3, max_length=40)
    idempotency_key: str = Field(..., min_length=8, max_length=120)
    quantities_by_source_item_id: dict[str, float] = Field(default_factory=dict)
    expected_version: Optional[int] = Field(default=None, ge=1)
    created_by: Optional[str] = Field(default=None, max_length=100)
    dry_run: bool = False


class DocflowPostRequest(BaseModel):
    idempotency_key: str = Field(..., min_length=8, max_length=120)
    expected_version: Optional[int] = Field(default=None, ge=1)
    posting_date: Optional[date] = None
    posted_by: Optional[str] = Field(default=None, max_length=100)


class DocflowReleaseRequest(BaseModel):
    idempotency_key: str = Field(..., min_length=8, max_length=120)
    expected_version: Optional[int] = Field(default=None, ge=1)
    released_by: Optional[str] = Field(default=None, max_length=100)


class DocflowReverseRequest(BaseModel):
    idempotency_key: str = Field(..., min_length=8, max_length=120)
    reason: str = Field(..., min_length=3, max_length=300)
    expected_version: Optional[int] = Field(default=None, ge=1)
    reversed_by: Optional[str] = Field(default=None, max_length=100)


class DocflowRecordPrintRequest(BaseModel):
    printed_by: Optional[str] = Field(default=None, max_length=100)


class DocflowRecordExportRequest(BaseModel):
    exported_by: Optional[str] = Field(default=None, max_length=100)


class DocflowCommandResult(BaseModel):
    command: str
    idempotent_hit: bool = False
    source_doc_id: Optional[str] = None
    target_doc_id: Optional[str] = None
    posting_id: Optional[str] = None
    status: str
    payload: dict[str, Any] = Field(default_factory=dict)


class DocflowLineInput(BaseModel):
    article_number: str = Field(..., min_length=1, max_length=80)
    description: Optional[str] = None
    quantity: float = Field(default=0, ge=0)
    unit: Optional[str] = Field(default=None, max_length=20)
    unit_price: float = Field(default=0, ge=0)
    discount_percent: float = Field(default=0, ge=0, le=100)
    # Steuerschluessel des Mandanten (tax_keys.code). Mit ihm kommt der Satz vom Server; ein abweichend
    # mitgeschickter Satz wird abgelehnt. Ohne ihn gilt der Satz der Anfrage — gebucht wird so nicht.
    tax_code: Optional[str] = Field(default=None, max_length=2)
    tax_rate: Optional[float] = Field(default=None, ge=0, le=100)
    # Nur Einkaufsbelege: Aufwandskonto der Position; leer = das des Steuerschluessels.
    expense_account: Optional[str] = Field(default=None, max_length=20)
    batch_id: Optional[str] = Field(default=None, max_length=64)
    charge: Optional[str] = Field(default=None, max_length=64)


class PosComplianceInput(BaseModel):
    terminal_id: str = Field(..., min_length=1, max_length=60)
    cash_register_id: Optional[str] = Field(default=None, max_length=60)
    transaction_type: str = Field(default="sale", min_length=4, max_length=20)
    payment_breakdown: Optional[dict[str, Any]] = None
    tse_transaction_id: str = Field(..., min_length=1, max_length=120)
    tse_signature: str = Field(..., min_length=1)
    tse_signature_counter: Optional[int] = None
    transaction_started_at: datetime
    transaction_ended_at: datetime
    receipt_issued_at: datetime
    dsfinvk_export_batch_id: Optional[str] = Field(default=None, max_length=120)
    correction_type: Optional[str] = Field(default=None, max_length=20)
    original_header_id: Optional[str] = Field(default=None, max_length=36)


class DocflowCreateRequest(BaseModel):
    doc_type: str = Field(..., min_length=3, max_length=40)
    doc_number: str = Field(..., min_length=1, max_length=80)
    status: str = Field(default="draft", min_length=3, max_length=20)
    source_system: Optional[str] = Field(default=None, max_length=40)
    source_ref: Optional[str] = Field(default=None, max_length=80)
    customer_id: Optional[str] = None
    supplier_id: Optional[str] = None
    currency: str = Field(default="EUR", min_length=3, max_length=3)
    document_date: Optional[datetime] = None
    posting_date: Optional[date] = None
    created_by: Optional[str] = Field(default=None, max_length=100)
    items: list[DocflowLineInput] = Field(default_factory=list)
    pos_compliance: Optional[PosComplianceInput] = None
    idempotency_key: Optional[str] = Field(default=None, min_length=8, max_length=120)


class DocflowUpdateRequest(BaseModel):
    expected_version: int = Field(..., ge=1, strict=True)
    idempotency_key: str = Field(..., min_length=8, max_length=120)
    status: Optional[str] = Field(default=None, min_length=3, max_length=20)
    source_system: Optional[str] = Field(default=None, max_length=40)
    source_ref: Optional[str] = Field(default=None, max_length=80)
    customer_id: Optional[str] = None
    supplier_id: Optional[str] = None
    currency: Optional[str] = Field(default=None, min_length=3, max_length=3)
    document_date: Optional[datetime] = None
    posting_date: Optional[date] = None
    updated_by: Optional[str] = Field(default=None, max_length=100)
    items: Optional[list[DocflowLineInput]] = None
    pos_compliance: Optional[PosComplianceInput] = None


# ── helpers ───────────────────────────────────────────────────────────────────

def _akteur(nutzer: Any) -> Optional[str]:
    """Die Kennung des angemeldeten Benutzers — aus der geprueften Anmeldung, nie aus der Anfrage."""
    wert = nutzer.get("sub") if isinstance(nutzer, dict) else getattr(nutzer, "sub", None) or getattr(nutzer, "id", None)
    return str(wert).strip() or None if wert else None


def _svc(db: Session, tenant_id: str, akteur: Optional[str] = None) -> DocflowService:
    return DocflowService(db, tenant_id, akteur)


def _recht(svc: DocflowService, doc_id: str, nutzer: Any, recht: str) -> None:
    """403 ohne das Recht an der Belegart dieses Belegs (``app/auth/beleg_roles.py``).

    Steht der Beleg noch nicht in DocFlow, ist er ein Auftrag oder Lieferschein des Verkaufs, der beim ersten
    Zugriff nachgezogen wird — geprueft wird dann das Recht am Auftrag.
    """
    header = svc.fetch_header(doc_id)
    verlange(nutzer, recht, str(header["doc_type"]) if header else "sales_order")


def _validate_pos_compliance_requirements(doc_type: str, pos: Optional[PosComplianceInput]) -> None:
    if doc_type in POS_TYPES and pos is None:
        raise HTTPException(status_code=400, detail="pos_compliance is required for POS documents")
    if pos is None:
        return
    if pos.transaction_ended_at < pos.transaction_started_at:
        raise HTTPException(status_code=400, detail="transaction_ended_at must be >= transaction_started_at")
    if pos.receipt_issued_at < pos.transaction_started_at:
        raise HTTPException(status_code=400, detail="receipt_issued_at must be >= transaction_started_at")
    if pos.correction_type and not pos.original_header_id:
        raise HTTPException(status_code=400, detail="original_header_id required for correction_type")


def _row_to_header_out(svc: DocflowService, header_id: str, snapshot: Optional[dict[str, Any]] = None) -> DocflowHeaderOut:
    header = snapshot["header"] if snapshot is not None else svc.fetch_header(header_id)
    if not header:
        raise HTTPException(status_code=404, detail="Document not found")
    items = snapshot["items"] if snapshot is not None else svc.fetch_items(header_id)
    pos_compliance = snapshot["pos_compliance"] if snapshot is not None else svc.fetch_pos_compliance(header_id)
    return DocflowHeaderOut(
        id=str(header["id"]),
        tenant_id=str(header["tenant_id"]),
        doc_type=str(header["doc_type"]),
        doc_number=str(header["doc_number"]),
        status=str(header["status"]),
        source_system=str(header["source_system"]),
        source_ref=header.get("source_ref"),
        customer_id=header.get("customer_id"),
        supplier_id=header.get("supplier_id"),
        currency=str(header.get("currency") or "EUR"),
        total_net=float(header.get("total_net") or 0),
        total_tax=float(header.get("total_tax") or 0),
        total_gross=float(header.get("total_gross") or 0),
        document_date=header["document_date"],
        posting_date=header.get("posting_date"),
        version=int(header.get("version") or 1),
        created_at=header["created_at"],
        updated_at=header["updated_at"],
        pos_compliance=pos_compliance,
        printed_at=header.get("printed_at"),
        printed_by=header.get("printed_by"),
        print_count=int(header.get("print_count") or 0),
        exported_at=header.get("exported_at"),
        exported_by=header.get("exported_by"),
        items=[
            DocflowItemOut(
                id=str(i["id"]),
                line_number=int(i.get("line_number") or 0),
                source_line_id=i.get("source_line_id"),
                article_number=str(i.get("article_number") or ""),
                description=i.get("description"),
                quantity=float(i.get("quantity") or 0),
                unit=i.get("unit"),
                unit_price=float(i.get("unit_price") or 0),
                discount_percent=float(i.get("discount_percent") or 0),
                tax_code=i.get("tax_code"),
                expense_account=i.get("expense_account"),
                tax_rate=float(i.get("tax_rate") or 0),
                line_total_net=float(i.get("line_total_net") or 0),
                line_total_tax=float(i.get("line_total_tax") or 0),
                line_total_gross=float(i.get("line_total_gross") or 0),
            )
            for i in items
        ],
    )


# ── routes ────────────────────────────────────────────────────────────────────

@router.get("/", response_model=list[DocflowHeaderOut], summary="Documents auflisten")
async def list_documents(
    tenant_id: str = Depends(_docflow_tenant),
    doc_type: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    nutzer: Any = Depends(get_current_user),
):
    effective_tenant = tenant_id
    svc = _svc(db, effective_tenant)
    if doc_type:
        verlange(nutzer, "preise", doc_type)
    doc_ids = svc.list_documents(doc_type, limit)
    belege = [_row_to_header_out(svc, doc_id) for doc_id in doc_ids]
    # Dieser Weg liefert Preise; ohne Preisrecht an der Belegart erscheint der Beleg nicht.
    return [b for b in belege if b.doc_type in POS_TYPES or darf(nutzer, "preise", b.doc_type)]


@router.get("/{doc_id}", response_model=DocflowHeaderOut, summary="Document abrufen")
async def get_document(
    doc_id: str,
    tenant_id: str = Depends(_docflow_tenant),
    db: Session = Depends(get_db),
    nutzer: Any = Depends(get_current_user),
):
    effective_tenant = tenant_id
    svc = _svc(db, effective_tenant)
    _recht(svc, doc_id, nutzer, "preise")
    bootstrapped = svc.bootstrap_doc(doc_id)
    if not bootstrapped:
        raise HTTPException(status_code=404, detail="Document not found")
    db.commit()
    return _row_to_header_out(svc, doc_id)


@router.delete(
    "/{doc_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    response_model=None,
    summary="Ungebuchten Docflow-Entwurf loeschen",
)
async def delete_draft_document(
    doc_id: str,
    tenant_id: str = Depends(_docflow_tenant),
    db: Session = Depends(get_db),
    nutzer: Any = Depends(get_current_user),
) -> Response:
    effective_tenant = tenant_id
    _recht(_svc(db, effective_tenant), doc_id, nutzer, "bearbeiten")
    try:
        _svc(db, effective_tenant, _akteur(nutzer)).delete_draft_document(doc_id)
    except EntityNotFoundError as exc:
        db.rollback()
        raise HTTPException(status_code=404, detail=exc.detail)
    except ValidationFailedError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail=exc.detail)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{doc_id}/status-history", response_model=list[TypedObjectOut],
            summary="Statushistorie und Kommandoprotokoll des Belegs")
async def get_status_history(
    doc_id: str,
    tenant_id: str = Depends(_docflow_tenant),
    db: Session = Depends(get_db),
    nutzer: Any = Depends(get_current_user),
) -> list[dict[str, Any]]:
    """Jeder Statuswechsel des Belegs: von, nach, Kommando, wer, warum, wann. Unveraenderlich."""
    svc = _svc(db, tenant_id)
    _recht(svc, doc_id, nutzer, "lesen")
    if not svc.fetch_header(doc_id):
        raise HTTPException(status_code=404, detail="Document not found")
    return svc.fetch_status_history(doc_id)


@router.get("/{doc_id}/pos-compliance", response_model=DocflowOut, summary="Pos compliance abrufen")
async def get_pos_compliance(
    doc_id: str,
    tenant_id: str = Depends(_docflow_tenant),
    db: Session = Depends(get_db),
):
    effective_tenant = tenant_id
    svc = _svc(db, effective_tenant)
    if not svc.fetch_header(doc_id):
        raise HTTPException(status_code=404, detail="Document not found")
    payload = svc.fetch_pos_compliance(doc_id)
    if not payload:
        raise HTTPException(status_code=404, detail="POS compliance not found")
    return payload


@router.post("/", response_model=DocflowHeaderOut, summary="Document anlegen")
async def create_document(
    payload: DocflowCreateRequest,
    tenant_id: str = Depends(_docflow_tenant),
    db: Session = Depends(get_db),
    nutzer: Any = Depends(get_current_user),
):
    effective_tenant = tenant_id
    verlange(nutzer, "bearbeiten", payload.doc_type)
    _validate_pos_compliance_requirements(payload.doc_type, payload.pos_compliance)
    svc = _svc(db, effective_tenant, _akteur(nutzer))
    try:
        doc_id = svc.create_document(payload)
    except (EntityNotFoundError, ValidationFailedError) as exc:
        db.rollback()
        raise HTTPException(status_code=422, detail=exc.detail)
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"create failed: {exc}") from exc
    return _row_to_header_out(svc, doc_id)


@router.put("/{doc_id}", response_model=DocflowHeaderOut, summary="Document aktualisieren")
async def update_document(
    doc_id: str,
    payload: DocflowUpdateRequest,
    tenant_id: str = Depends(_docflow_tenant),
    db: Session = Depends(get_db),
    nutzer: Any = Depends(get_current_user),
):
    effective_tenant = tenant_id
    svc = _svc(db, effective_tenant, _akteur(nutzer))
    header = svc.fetch_header(doc_id)
    if not header:
        raise HTTPException(status_code=404, detail="Document not found")
    effective_doc_type = str(header.get("doc_type") or "")
    verlange(nutzer, "bearbeiten", effective_doc_type)
    _validate_pos_compliance_requirements(effective_doc_type, payload.pos_compliance)
    try:
        snapshot = svc.update_document(doc_id, payload)
    except EntityNotFoundError as exc:
        db.rollback()
        raise HTTPException(status_code=404, detail=exc.detail)
    except ConflictError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail=exc.detail)
    except ValidationFailedError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail=exc.detail)
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail="Document update failed") from exc
    return _row_to_header_out(svc, doc_id, snapshot)


# ── Freigaben (APPROVAL-001) ──────────────────────────────────────────────────

class DocflowApprovalRequest(BaseModel):
    action: str = Field(..., pattern="^(post|reverse)$")
    reason: Optional[str] = Field(default=None, max_length=300)


class DocflowApprovalDecision(BaseModel):
    granted: bool
    note: Optional[str] = Field(default=None, max_length=300)


@router.get("/{doc_id}/approvals", response_model=list[TypedObjectOut], summary="Freigaben des Belegs")
def list_approvals(
    doc_id: str,
    tenant_id: str = Depends(_docflow_tenant),
    db: Session = Depends(get_db),
    nutzer: Any = Depends(get_current_user),
) -> list[dict[str, Any]]:
    svc = _svc(db, tenant_id)
    if not svc.fetch_header(doc_id):
        raise HTTPException(status_code=404, detail="Document not found")
    _recht(svc, doc_id, nutzer, "lesen")
    return DocflowFreigabe(db, tenant_id).liste(doc_id)


@router.post("/{doc_id}/approvals", response_model=TypedObjectOut, summary="Freigabe durch eine zweite Person anfragen")
def request_approval(
    doc_id: str,
    payload: DocflowApprovalRequest,
    tenant_id: str = Depends(_docflow_tenant),
    db: Session = Depends(get_db),
    nutzer: Any = Depends(get_current_user),
) -> dict[str, Any]:
    """Anfragen darf, wer die Aktion selbst ausfuehren duerfte. Der Antragsteller kommt aus der Anmeldung."""
    svc = _svc(db, tenant_id)
    if not svc.fetch_header(doc_id):
        raise HTTPException(status_code=404, detail="Document not found")
    _recht(svc, doc_id, nutzer, "buchen" if payload.action == "post" else "stornieren")
    try:
        return DocflowFreigabe(db, tenant_id).beantrage(doc_id, payload.action, _akteur(nutzer) or "", payload.reason)
    except EntityNotFoundError as exc:
        db.rollback()
        raise HTTPException(status_code=404, detail=exc.detail)
    except (ConflictError, ValidationFailedError) as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail=exc.detail)


@router.post("/{doc_id}/approvals/{approval_id}/decision", response_model=TypedObjectOut,
             summary="Freigabe erteilen oder ablehnen")
def decide_approval(
    doc_id: str,
    approval_id: str,
    payload: DocflowApprovalDecision,
    tenant_id: str = Depends(_docflow_tenant),
    db: Session = Depends(get_db),
    nutzer: Any = Depends(get_current_user),
) -> dict[str, Any]:
    """Recht, Funktionstrennung, Ablauf und unveraenderter Inhalt prueft die Approval Engine."""
    try:
        return DocflowFreigabe(db, tenant_id).entscheide(doc_id, approval_id, nutzer, payload.granted, payload.note)
    except EntityNotFoundError as exc:
        db.rollback()
        raise HTTPException(status_code=404, detail=exc.detail)
    except ConflictError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail=exc.detail)
    except ValidationFailedError as exc:
        db.rollback()
        raise HTTPException(status_code=403, detail=exc.detail)


@router.post("/{doc_id}/release", response_model=DocflowCommandResult, summary="Document freigeben")
async def release_document(
    doc_id: str,
    payload: DocflowReleaseRequest,
    tenant_id: str = Depends(_docflow_tenant),
    db: Session = Depends(get_db),
    nutzer: Any = Depends(get_current_user),
):
    effective_tenant = tenant_id
    _recht(_svc(db, effective_tenant), doc_id, nutzer, "ausstellen")
    try:
        result = _svc(db, effective_tenant, _akteur(nutzer)).release(doc_id, payload.idempotency_key, payload.expected_version, payload.released_by)
    except EntityNotFoundError as exc:
        db.rollback()
        raise HTTPException(status_code=404, detail=exc.detail)
    except ConflictError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail=exc.detail)
    except ValidationFailedError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail=exc.detail)
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"release failed: {exc}") from exc
    return DocflowCommandResult(**result)


@router.post("/{doc_id}/record-print", response_model=DocflowHeaderOut, summary="Print record")
async def record_print(
    doc_id: str,
    payload: DocflowRecordPrintRequest,
    tenant_id: str = Depends(_docflow_tenant),
    db: Session = Depends(get_db),
    nutzer: Any = Depends(get_current_user),
):
    effective_tenant = tenant_id
    svc = _svc(db, effective_tenant, _akteur(nutzer))
    _recht(svc, doc_id, nutzer, "bearbeiten")
    try:
        svc.record_print(doc_id, payload.printed_by)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.detail)
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"record-print failed: {exc}") from exc
    return _row_to_header_out(svc, doc_id)


@router.post("/{doc_id}/record-export", response_model=DocflowHeaderOut, summary="Export record")
async def record_export(
    doc_id: str,
    payload: DocflowRecordExportRequest,
    tenant_id: str = Depends(_docflow_tenant),
    db: Session = Depends(get_db),
    nutzer: Any = Depends(get_current_user),
):
    effective_tenant = tenant_id
    svc = _svc(db, effective_tenant, _akteur(nutzer))
    _recht(svc, doc_id, nutzer, "bearbeiten")
    try:
        svc.record_export(doc_id, payload.exported_by)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.detail)
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"record-export failed: {exc}") from exc
    return _row_to_header_out(svc, doc_id)


@router.post("/{doc_id}/convert", response_model=DocflowCommandResult, summary="Document umwandeln")
async def convert_document(
    doc_id: str,
    payload: DocflowConvertRequest,
    tenant_id: str = Depends(_docflow_tenant),
    db: Session = Depends(get_db),
    nutzer: Any = Depends(get_current_user),
):
    effective_tenant = tenant_id
    # Ein Folgebeleg braucht das Recht an der Belegart, die entsteht.
    verlange(nutzer, "bearbeiten", payload.target_doc_type)
    try:
        result = _svc(db, effective_tenant, _akteur(nutzer)).convert(doc_id, payload)
    except EntityNotFoundError as exc:
        db.rollback()
        raise HTTPException(status_code=404, detail=exc.detail)
    except ConflictError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail=exc.detail)
    except ValidationFailedError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=exc.detail)
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"convert failed: {exc}") from exc
    return DocflowCommandResult(**result)


@router.post("/{doc_id}/post", response_model=DocflowCommandResult, summary="Document erstellen")
async def post_document(
    doc_id: str,
    payload: DocflowPostRequest,
    tenant_id: str = Depends(_docflow_tenant),
    db: Session = Depends(get_db),
    nutzer: Any = Depends(get_current_user),
):
    effective_tenant = tenant_id
    _recht(_svc(db, effective_tenant), doc_id, nutzer, "buchen")
    try:
        result = _svc(db, effective_tenant, _akteur(nutzer)).post_document(doc_id, payload)
    except EntityNotFoundError as exc:
        db.rollback()
        raise HTTPException(status_code=404, detail=exc.detail)
    except ConflictError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail=exc.detail)
    except ValidationFailedError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=exc.detail)
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"post failed: {exc}") from exc
    return DocflowCommandResult(**result)


@router.post("/{doc_id}/reverse", response_model=DocflowCommandResult, summary="Document reverse")
async def reverse_document(
    doc_id: str,
    payload: DocflowReverseRequest,
    tenant_id: str = Depends(_docflow_tenant),
    db: Session = Depends(get_db),
    nutzer: Any = Depends(get_current_user),
):
    effective_tenant = tenant_id
    _recht(_svc(db, effective_tenant), doc_id, nutzer, "stornieren")
    try:
        result = _svc(db, effective_tenant, _akteur(nutzer)).reverse_document(doc_id, payload)
    except EntityNotFoundError as exc:
        db.rollback()
        raise HTTPException(status_code=404, detail=exc.detail)
    except ConflictError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail=exc.detail)
    except ValidationFailedError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=exc.detail)
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"reverse failed: {exc}") from exc
    return DocflowCommandResult(**result)


# Draft inputs are read-only; tenant identity comes exclusively from request context.
from app.services.docflow_source_proposals import DocflowSourceProposalService, SourceProposalRequest


@router.post("/source-proposals", response_model=DocflowOut, summary="Kontrakt- und Fremdlagerquellen vorschlagen")
def source_proposals(
    body: SourceProposalRequest,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return DocflowSourceProposalService(db, tenant_id).propose(body)
