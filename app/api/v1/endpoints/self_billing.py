"""
Self-Billing API endpoints.
Handles self-billing invoice creation, E-invoice generation, and dispute handling.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.data_quality_enforcement import build_dq_error_detail, evaluate_self_billing_datensatz
from app.core.database import get_db
from app.core.tenant import get_tenant_id

from modules.agrar.services.self_billing_service import (
    create_credit_note,
    issue_invoice,
    generate_einvoice,
    send_einvoice,
    create_dispute,
    CreditNoteCreate,
    DisputeCreate,
)
from modules.agrar.repositories.self_billing_repo import SelfBillingRepositoryImpl

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.self_billing_schemas import SelfBillingOut
from app.core.akteur import akteur_aus_request
from app.auth.bereich_roles import SCHREIBEN  # Schreibrecht je Bereich (WRITE-ROLES)


router = APIRouter()


def _build_self_billing_dq_datensatz(
    *,
    harvest_acceptance_id: str,
    net_amount: float,
    gross_amount: float,
    vat_rate: float,
    taxation_type: str,
) -> dict[str, object]:
    return {
        "ernteannahme_id": harvest_acceptance_id,
        "netto_eur": net_amount,
        "brutto_eur": gross_amount,
        "ust_satz_pct": vat_rate,
        "besteuerung": taxation_type,
    }


# ── Pydantic Models ───────────────────────────────────────────────────────────────

class SelfBillingInvoiceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    """Output-Model für Self-Billing Gutschrift."""
    id: str
    tenant_id: str
    harvest_acceptance_id: Optional[str] = None
    invoice_number: str
    provisional_invoice_number: Optional[str] = None
    status: str
    dispute_status: Optional[str] = None
    dispute_reason: Optional[str] = None
    dispute_date: Optional[datetime] = None
    dispute_user_id: Optional[str] = None
    total_net_amount_eur: float
    total_vat_amount_eur: float
    total_gross_amount_eur: float
    vat_rate_percent: float
    einvoice_sent_at: Optional[datetime] = None
    einvoice_received_at: Optional[datetime] = None
    mandatory_texts: Optional[list[dict]] = None
    created_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[str] = None


class CreditNoteCreateIn(BaseModel):
    """Input-Model für Gutschrift-Erstellung (Beträge Decimal; Client-Werte werden serverseitig geprüft)."""
    harvest_acceptance_id: str
    invoice_number: Optional[str] = None
    provisional_invoice_number: Optional[str] = None
    total_net_amount_eur: Decimal = Field(..., gt=0)
    total_vat_amount_eur: Decimal = Field(..., ge=0)
    total_gross_amount_eur: Decimal = Field(..., gt=0)
    vat_rate_percent: Decimal = Field(..., ge=0, le=100)
    mandatory_texts: Optional[list[dict]] = None
    taxation_type: Optional[str] = None  # nur Entwurfshinweis; endgültig aus Profil


class DisputeCreateIn(BaseModel):
    """Input-Model für Dispute-Erstellung."""
    dispute_type: str = Field(..., pattern="^(amount|quality|quantity|other)$")
    dispute_reason: str = Field(..., min_length=1)
    disputed_amount_eur: Optional[float] = Field(None, ge=0)


class EinvoiceGenerateIn(BaseModel):
    """Input-Model für E-Rechnung-Generierung."""
    supplier_data: dict = Field(..., description="Lieferantendaten (Name, Adresse, USt-ID, etc.)")
    customer_data: dict = Field(..., description="Kundendaten (Name, Adresse, USt-ID, etc.)")
    line_items: list[dict] = Field(..., description="Rechnungspositionen")
    format: str = Field("xrechnung", pattern="^(xrechnung|zugferd)$")


# ── Helper Functions ────────────────────────────────────────────────────────────

def _get_user_id_from_request(request) -> Optional[str]:
    """Urheber aus dem geprueften Token (bis 19.10.2026 zuerst aus dem Client-Header ``X-User-ID``)."""
    return akteur_aus_request(request)


def _to_out(invoice) -> SelfBillingInvoiceOut:
    """Konvertiert Service-Model zu Output-Model."""
    return SelfBillingInvoiceOut(
        id=invoice.id,
        tenant_id=invoice.tenant_id,
        harvest_acceptance_id=invoice.harvest_acceptance_id,
        invoice_number=invoice.invoice_number,
        provisional_invoice_number=invoice.provisional_invoice_number,
        status=invoice.status,
        dispute_status=invoice.dispute_status,
        dispute_reason=invoice.dispute_reason,
        dispute_date=invoice.dispute_date,
        dispute_user_id=invoice.dispute_user_id,
        total_net_amount_eur=float(invoice.total_net_amount_eur),
        total_vat_amount_eur=float(invoice.total_vat_amount_eur),
        total_gross_amount_eur=float(invoice.total_gross_amount_eur),
        vat_rate_percent=float(invoice.vat_rate_percent),
        einvoice_sent_at=invoice.einvoice_sent_at,
        einvoice_received_at=invoice.einvoice_received_at,
        mandatory_texts=invoice.mandatory_texts,
        created_at=invoice.created_at,
        created_by=invoice.created_by,
        updated_at=invoice.updated_at,
        updated_by=invoice.updated_by,
    )


# ── API Endpoints ───────────────────────────────────────────────────────────────

@router.post("/harvest-acceptance/{harvest_acceptance_id}/create-credit-note", response_model=SelfBillingInvoiceOut, status_code=201, summary="Credit note endpoint anlegen", dependencies=SCHREIBEN["AGRAR"])
async def create_credit_note_endpoint(
    harvest_acceptance_id: str,
    payload: CreditNoteCreateIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    request: Request = None,
):
    """Erstellt eine Self-Billing Gutschrift für eine Ernte-Annahme."""
    user_id = _get_user_id_from_request(request)
    taxation_hint = payload.taxation_type or "regular"
    dq_result = evaluate_self_billing_datensatz(
        _build_self_billing_dq_datensatz(
            harvest_acceptance_id=harvest_acceptance_id,
            net_amount=float(payload.total_net_amount_eur),
            gross_amount=float(payload.total_gross_amount_eur),
            vat_rate=float(payload.vat_rate_percent),
            taxation_type=taxation_hint,
        )
    )
    if not dq_result.bestanden:
        raise HTTPException(status_code=422, detail=build_dq_error_detail("SelfBilling", dq_result))

    create_input = CreditNoteCreate(
        tenant_id=tenant_id,
        harvest_acceptance_id=harvest_acceptance_id,
        invoice_number=payload.invoice_number,
        provisional_invoice_number=payload.provisional_invoice_number,
        total_net_amount_eur=Decimal(str(payload.total_net_amount_eur)),
        total_vat_amount_eur=Decimal(str(payload.total_vat_amount_eur)),
        total_gross_amount_eur=Decimal(str(payload.total_gross_amount_eur)),
        vat_rate_percent=Decimal(str(payload.vat_rate_percent)),
        mandatory_texts=payload.mandatory_texts,
        created_by=user_id,
    )

    repo = SelfBillingRepositoryImpl(db, commit_on_success=False)
    invoice = create_credit_note(repo, create_input, taxation_type=taxation_hint)

    # Atomare Rückverknüpfung in derselben Transaktion (kein stilles except:pass)
    updated = db.execute(
        text("""
            UPDATE domain_inventory.harvest_acceptances
            SET invoice_id = :inv_id, updated_at = NOW()
            WHERE id = :ha_id AND tenant_id = :tid AND invoice_id IS NULL
        """),
        {"inv_id": invoice.id, "ha_id": harvest_acceptance_id, "tid": tenant_id},
    )
    if updated.rowcount == 0:
        exists = db.execute(
            text(
                "SELECT invoice_id FROM domain_inventory.harvest_acceptances "
                "WHERE id = :ha_id AND tenant_id = :tid"
            ),
            {"ha_id": harvest_acceptance_id, "tid": tenant_id},
        ).scalar()
        if exists is None:
            raise HTTPException(status_code=404, detail="Ernte-Annahme nicht gefunden")
        if exists != invoice.id:
            raise HTTPException(status_code=409, detail="Ernte-Annahme hat bereits eine Gutschrift")
    db.commit()
    return _to_out(invoice)


@router.get("/{invoice_id}", response_model=SelfBillingInvoiceOut, summary="Invoice abrufen")
async def get_invoice(
    invoice_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Ruft eine Self-Billing Gutschrift ab."""
    repo = SelfBillingRepositoryImpl(db)
    invoice = repo.get_invoice_by_id(invoice_id)
    
    if not invoice:
        raise HTTPException(status_code=404, detail=f"Self-billing invoice {invoice_id} not found")
    
    if invoice.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return _to_out(invoice)


@router.get("/harvest-acceptance/{harvest_acceptance_id}", response_model=Optional[SelfBillingInvoiceOut], summary="Invoice by harvest acceptance abrufen")
async def get_invoice_by_harvest_acceptance(
    harvest_acceptance_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Ruft die Gutschrift für eine Ernte-Annahme ab."""
    repo = SelfBillingRepositoryImpl(db)
    invoice = repo.get_invoice_by_harvest_acceptance(harvest_acceptance_id)
    
    if not invoice:
        return None
    
    if invoice.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return _to_out(invoice)


@router.post("/{invoice_id}/issue", response_model=SelfBillingInvoiceOut, summary="Invoice endpoint issue", dependencies=SCHREIBEN["AGRAR"])
async def issue_invoice_endpoint(
    invoice_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    request: Request = None,
):
    """Gibt eine Gutschrift aus (Status: draft → issued). Vereinbarung + Steuerprofil Pflicht."""
    from app.core.exceptions import DomainError
    from app.infrastructure.models import Customer, HarvestAcceptance
    from modules.agrar.services.tax_profile_service import (
        get_taxation_type_for_supplier,
        require_self_billing_agreement,
    )

    user_id = _get_user_id_from_request(request)

    repo = SelfBillingRepositoryImpl(db)
    invoice = repo.get_invoice_by_id(invoice_id, tenant_id=tenant_id)

    if not invoice:
        raise HTTPException(status_code=404, detail=f"Invoice {invoice_id} not found")

    if invoice.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")

    try:
        supplier_id = None
        delivery = None
        if invoice.harvest_acceptance_id:
            harvest = db.query(HarvestAcceptance).filter(
                HarvestAcceptance.id == invoice.harvest_acceptance_id,
                HarvestAcceptance.tenant_id == tenant_id,
            ).first()
            if harvest and harvest.customer_id:
                customer = db.query(Customer).filter(
                    Customer.id == harvest.customer_id, Customer.tenant_id == tenant_id
                ).first()
                supplier_id = (
                    customer.business_partner_id
                    if customer and customer.business_partner_id
                    else harvest.customer_id
                )
                delivery = harvest.delivery_date
        if not supplier_id:
            raise HTTPException(status_code=422, detail="Lieferant für Ausstellung nicht ermittelbar")
        require_self_billing_agreement(db, tenant_id, supplier_id)
        get_taxation_type_for_supplier(
            db, supplier_id, tenant_id, delivery, require_profile=True
        )
        invoice = issue_invoice(repo, invoice_id, updated_by=user_id)
    except DomainError as err:
        raise HTTPException(status_code=getattr(err, "http_status", 422), detail=str(err)) from err
    return _to_out(invoice)


@router.post("/{invoice_id}/generate-einvoice", response_model=SelfBillingInvoiceOut, summary="Einvoice endpoint generieren", dependencies=SCHREIBEN["AGRAR"])
async def generate_einvoice_endpoint(
    invoice_id: str,
    payload: EinvoiceGenerateIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Generiert E-Rechnung (XRechnung oder ZUGFeRD) für eine Gutschrift."""
    repo = SelfBillingRepositoryImpl(db)
    invoice = repo.get_invoice_by_id(invoice_id)
    
    if not invoice:
        raise HTTPException(status_code=404, detail=f"Invoice {invoice_id} not found")
    
    if invoice.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    invoice = generate_einvoice(
        repo,
        invoice_id=invoice_id,
        supplier_data=payload.supplier_data,
        customer_data=payload.customer_data,
        line_items=payload.line_items,
        format=payload.format,
    )
    
    return _to_out(invoice)


@router.post("/{invoice_id}/send", response_model=SelfBillingInvoiceOut, summary="Einvoice endpoint senden", dependencies=SCHREIBEN["AGRAR"])
async def send_einvoice_endpoint(
    invoice_id: str,
    recipient_email: Optional[str] = None,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Versendet E-Rechnung an den Empfänger."""
    repo = SelfBillingRepositoryImpl(db)
    invoice = repo.get_invoice_by_id(invoice_id)
    
    if not invoice:
        raise HTTPException(status_code=404, detail=f"Invoice {invoice_id} not found")
    
    if invoice.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    invoice = send_einvoice(repo, invoice_id, recipient_email=recipient_email)
    return _to_out(invoice)


@router.post("/{invoice_id}/dispute", response_model=SelfBillingOut, summary="Dispute endpoint anlegen", dependencies=SCHREIBEN["AGRAR"])
async def create_dispute_endpoint(
    invoice_id: str,
    payload: DisputeCreateIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    request: Request = None,
):
    """Erstellt einen Dispute-Record für eine Gutschrift."""
    user_id = _get_user_id_from_request(request)
    
    repo = SelfBillingRepositoryImpl(db)
    invoice = repo.get_invoice_by_id(invoice_id)
    
    if not invoice:
        raise HTTPException(status_code=404, detail=f"Invoice {invoice_id} not found")
    
    if invoice.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    dispute_input = DisputeCreate(
        invoice_id=invoice_id,
        dispute_type=payload.dispute_type,
        dispute_reason=payload.dispute_reason,
        disputed_amount_eur=Decimal(str(payload.disputed_amount_eur)) if payload.disputed_amount_eur else None,
        created_by=user_id,
    )
    
    updated_invoice, dispute_record = create_dispute(repo, dispute_input)
    
    return {
        "invoice": _to_out(updated_invoice),
        "dispute": {
            "id": dispute_record.id,
            "dispute_type": dispute_record.dispute_type,
            "dispute_reason": dispute_record.dispute_reason,
            "disputed_amount_eur": float(dispute_record.disputed_amount_eur) if dispute_record.disputed_amount_eur else None,
            "status": dispute_record.status,
            "created_at": dispute_record.created_at,
        }
    }


class PreviewIn(BaseModel):
    harvest_acceptance_id: str
    total_net_amount_eur: Decimal = Field(Decimal("0"), ge=0)
    total_gross_amount_eur: Decimal = Field(Decimal("0"), ge=0)
    vat_rate_percent: Decimal = Field(Decimal("0"), ge=0, le=100)
    taxation_type: str = "regular"


@router.post("/preview", response_model=SelfBillingOut, summary="Self billing vorschauen", dependencies=SCHREIBEN["AGRAR"])
async def preview_self_billing(
    payload: PreviewIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """
    Preview Self-Billing für Ernte-Annahme (ohne Persistierung; Mandantenfilter Pflicht).
    Entwürfe/Vorschau ohne Steuerprofil erlaubt.
    """
    dq_result = evaluate_self_billing_datensatz(
        _build_self_billing_dq_datensatz(
            harvest_acceptance_id=payload.harvest_acceptance_id,
            net_amount=float(payload.total_net_amount_eur),
            gross_amount=float(payload.total_gross_amount_eur),
            vat_rate=float(payload.vat_rate_percent),
            taxation_type=payload.taxation_type,
        )
    )
    if not dq_result.bestanden:
        raise HTTPException(status_code=422, detail=build_dq_error_detail("SelfBilling", dq_result))

    from sqlalchemy import text as sa_text

    owned = db.execute(
        sa_text(
            "SELECT id FROM domain_inventory.harvest_acceptances "
            "WHERE id = :ha_id AND tenant_id = :tid"
        ),
        {"ha_id": payload.harvest_acceptance_id, "tid": tenant_id},
    ).first()
    if not owned:
        raise HTTPException(status_code=404, detail="Ernte-Annahme nicht gefunden")

    line_items = []
    rows = db.execute(
        sa_text("""
            SELECT hap.position_number, hap.description,
                   COALESCE(hap.quantity_kg, 0) AS menge_kg,
                   COALESCE(hap.unit_price_eur_per_t, 0) AS preis_eur_t,
                   COALESCE(hap.quality_grade, '') AS qualitaet
            FROM domain_inventory.harvest_acceptance_positions hap
            JOIN domain_inventory.harvest_acceptances ha
              ON ha.id = hap.harvest_acceptance_id AND ha.tenant_id = :tid
            WHERE hap.harvest_acceptance_id = :ha_id
            ORDER BY hap.position_number
        """),
        {"ha_id": payload.harvest_acceptance_id, "tid": tenant_id},
    ).fetchall()

    for r in rows:
        menge_t = Decimal(str(r.menge_kg)) / Decimal("1000")
        netto = (menge_t * Decimal(str(r.preis_eur_t))).quantize(Decimal("0.01"))
        line_items.append({
            "position": r.position_number,
            "description": r.description or "",
            "quantity_kg": float(r.menge_kg),
            "quantity_t": float(menge_t.quantize(Decimal("0.001"))),
            "unit_price_eur_t": float(r.preis_eur_t),
            "net_amount_eur": float(netto),
            "quality_grade": r.qualitaet,
        })

    calculated_net = (
        sum((Decimal(str(li["net_amount_eur"])) for li in line_items), Decimal("0"))
        if line_items
        else Decimal(str(payload.total_net_amount_eur))
    )
    vat_amount = (calculated_net * Decimal(str(payload.vat_rate_percent)) / Decimal("100")).quantize(
        Decimal("0.01")
    )

    return {
        "harvest_acceptance_id": payload.harvest_acceptance_id,
        "status": "draft",
        "total_net_amount_eur": float(calculated_net.quantize(Decimal("0.01"))),
        "total_vat_amount_eur": float(vat_amount),
        "total_gross_amount_eur": float((calculated_net + vat_amount).quantize(Decimal("0.01"))),
        "vat_rate_percent": float(payload.vat_rate_percent),
        "line_items": line_items,
    }


@router.post("/{invoice_id}/storno", response_model=SelfBillingOut, summary="Invoice storno", dependencies=SCHREIBEN["AGRAR"])
async def storno_invoice(
    invoice_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    request: Request = None,
):
    """Storno + Neu: Erstellt Storno-Gutschrift und optional neue Gutschrift."""
    user_id = _get_user_id_from_request(request)

    repo = SelfBillingRepositoryImpl(db)
    invoice = repo.get_invoice_by_id(invoice_id)

    if not invoice:
        raise HTTPException(status_code=404, detail=f"Invoice {invoice_id} not found")

    if invoice.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")

    if invoice.status not in ("issued", "paid", "booked"):
        raise HTTPException(status_code=400, detail="Nur issued/paid/booked Gutschriften können storniert werden")

    # Originalkontext — keine Neuberechnung aktueller Steuersätze
    original_taxation = getattr(invoice, "taxation_type", None) or (
        (invoice.tax_context or {}).get("taxation_type") if getattr(invoice, "tax_context", None) else None
    ) or "regular"

    from app.services.self_billing_buchung import storno_self_billing
    from app.core.exceptions import DomainError

    try:
        if getattr(invoice, "journal_entry_id", None):
            storno_self_billing(
                db, tenant_id, invoice=invoice, reason=f"Storno Self-Billing {invoice.invoice_number}"
            )
        storno_number = f"{invoice.invoice_number}-ST"
        storno_input = CreditNoteCreate(
            tenant_id=tenant_id,
            harvest_acceptance_id=invoice.harvest_acceptance_id or "",
            invoice_number=storno_number,
            provisional_invoice_number=invoice.provisional_invoice_number,
            total_net_amount_eur=-Decimal(str(invoice.total_net_amount_eur)),
            total_vat_amount_eur=-Decimal(str(invoice.total_vat_amount_eur)),
            total_gross_amount_eur=-Decimal(str(invoice.total_gross_amount_eur)),
            vat_rate_percent=Decimal(str(invoice.vat_rate_percent)),
            mandatory_texts=invoice.mandatory_texts,
            created_by=user_id,
        )
        storno_invoice_entity = create_credit_note(repo, storno_input, taxation_type=original_taxation)
        db.commit()
    except DomainError as err:
        db.rollback()
        raise HTTPException(status_code=getattr(err, "http_status", 422), detail=str(err)) from err

    return {
        "message": "Storno erstellt",
        "storno_invoice": _to_out(storno_invoice_entity),
        "original_invoice_id": invoice_id,
        "taxation_type": original_taxation,
    }


@router.get("/{invoice_id}/export", summary="Invoice exportieren",
    response_model=SelfBillingOut
)
async def export_invoice(
    invoice_id: str,
    format: str = "xml",  # xml | pdf
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Export Gutschrift als PDF oder XML (ZUGFeRD/XRechnung)."""
    repo = SelfBillingRepositoryImpl(db)
    invoice = repo.get_invoice_by_id(invoice_id)

    if not invoice:
        raise HTTPException(status_code=404, detail=f"Invoice {invoice_id} not found")

    if invoice.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")

    from fastapi.responses import Response

    if format == "xml":
        xml = invoice.einvoice_xml
        if not xml:
            raise HTTPException(status_code=404, detail="E-Rechnung XML noch nicht generiert. POST /{id}/generate-einvoice ausführen.")
        return Response(content=xml, media_type="application/xml")
    elif format == "pdf":
        pdf = invoice.einvoice_pdf
        if not pdf:
            raise HTTPException(status_code=404, detail="PDF noch nicht generiert.")
        return Response(content=pdf, media_type="application/pdf")
    raise HTTPException(status_code=400, detail="format muss xml oder pdf sein")


@router.get("/{invoice_id}/disputes", response_model=list[SelfBillingOut], summary="Disputes abrufen")
async def get_disputes(
    invoice_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Ruft alle Disputes für eine Gutschrift ab."""
    repo = SelfBillingRepositoryImpl(db)
    invoice = repo.get_invoice_by_id(invoice_id)
    
    if not invoice:
        raise HTTPException(status_code=404, detail=f"Invoice {invoice_id} not found")
    
    if invoice.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    disputes = repo.get_disputes_by_invoice(invoice_id)
    
    return [
        {
            "id": d.id,
            "dispute_type": d.dispute_type,
            "dispute_reason": d.dispute_reason,
            "disputed_amount_eur": float(d.disputed_amount_eur) if d.disputed_amount_eur else None,
            "status": d.status,
            "resolution_notes": d.resolution_notes,
            "resolved_by": d.resolved_by,
            "resolved_at": d.resolved_at,
            "created_at": d.created_at,
            "created_by": d.created_by,
        }
        for d in disputes
    ]


# ============================================================================
# BUCHUNGSKREISLAUF INTEGRATION
# ============================================================================

@router.post("/{invoice_id}/buchung", response_model=SelfBillingOut, summary="Gutschrift buche", dependencies=SCHREIBEN["AGRAR"])
async def buche_gutschrift(
    invoice_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    request: Request = None,
):
    """
    Adapter auf den kanonischen Self-Billing-Buchungskern.

    Keine Umgehung der Erntefreigabe: nur nach endgültiger Freigabe / credit_note_created
    und mit Vereinbarung + Steuerprofil. Bereits verbucht → 409.
    """
    from app.core.exceptions import DomainError
    from app.infrastructure.models import Customer, HarvestAcceptance
    from app.services.harvest_acceptance_service import HarvestAcceptanceService
    from modules.agrar.services.tax_profile_service import require_self_billing_agreement

    repo = SelfBillingRepositoryImpl(db, commit_on_success=False)
    invoice = repo.get_invoice_by_id(invoice_id, tenant_id=tenant_id)

    if not invoice:
        raise HTTPException(status_code=404, detail=f"Gutschrift {invoice_id} nicht gefunden")

    if invoice.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")

    if getattr(invoice, "journal_entry_id", None) or invoice.status == "booked":
        raise HTTPException(status_code=409, detail="Self-Billing-Beleg ist bereits verbucht")

    if not invoice.harvest_acceptance_id:
        raise HTTPException(status_code=422, detail="Buchung nur über Ernte-Annahme / Freigabekette")

    harvest = db.query(HarvestAcceptance).filter(
        HarvestAcceptance.id == invoice.harvest_acceptance_id,
        HarvestAcceptance.tenant_id == tenant_id,
    ).first()
    if not harvest:
        raise HTTPException(status_code=404, detail="Ernte-Annahme nicht gefunden")

    if harvest.release_status not in ("final", "credit_note_created", "paid") and harvest.invoice_id != invoice.id:
        raise HTTPException(
            status_code=422,
            detail="API-Buchung ohne endgültige Erntefreigabe ist nicht erlaubt",
        )

    customer = None
    supplier_id = None
    if harvest.customer_id:
        customer = db.query(Customer).filter(
            Customer.id == harvest.customer_id, Customer.tenant_id == tenant_id
        ).first()
        supplier_id = (
            customer.business_partner_id if customer and customer.business_partner_id else harvest.customer_id
        )
    if not supplier_id:
        raise HTTPException(status_code=422, detail="Lieferant an der Annahme fehlt")

    try:
        require_self_billing_agreement(db, tenant_id, supplier_id)
        actor = _get_user_id_from_request(request) if request is not None else None
        HarvestAcceptanceService(db, tenant_id)._book_self_billing_credit_note(
            invoice,
            harvest.delivery_date,
            supplier_id=supplier_id,
            article_id=getattr(harvest, "article_id", None),
            posted_by=actor,
        )
        db.commit()
    except DomainError as err:
        db.rollback()
        raise HTTPException(status_code=getattr(err, "http_status", 422), detail=str(err)) from err

    refreshed = repo.get_invoice_by_id(invoice_id, tenant_id=tenant_id)
    return {
        "message": "Gutschrift gebucht",
        "buchung_id": getattr(refreshed, "journal_entry_id", None),
        "belegnr": f"SB-{invoice.invoice_number}",
        "docflow_header_id": getattr(refreshed, "docflow_header_id", None),
        "betrag": float(invoice.total_gross_amount_eur),
    }


