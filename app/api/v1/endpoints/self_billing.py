"""
Self-Billing API endpoints.
Handles self-billing invoice creation, E-invoice generation, and dispute handling.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.domains.inventory.api.inventory_auth import require_inventory_admin

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

router = APIRouter()


# ── Pydantic Models ───────────────────────────────────────────────────────────────

class SelfBillingInvoiceOut(BaseModel):
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

    class Config:
        from_attributes = True


class CreditNoteCreateIn(BaseModel):
    """Input-Model für Gutschrift-Erstellung."""
    harvest_acceptance_id: str
    invoice_number: Optional[str] = None
    provisional_invoice_number: Optional[str] = None
    total_net_amount_eur: float = Field(..., gt=0)
    total_vat_amount_eur: float = Field(..., ge=0)
    total_gross_amount_eur: float = Field(..., gt=0)
    vat_rate_percent: float = Field(..., ge=0, le=100)
    mandatory_texts: Optional[list[dict]] = None
    taxation_type: str = "regular"  # regular / ustg24_flat_rate / small_business


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
    """Holt User-ID aus Request-Header oder Bearer-Token."""
    if request is None:
        return None
    user_id = request.headers.get("X-User-ID")
    if user_id:
        return user_id
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        try:
            import base64, json as _json
            payload_b64 = auth[7:].split(".")[1]
            payload_b64 += "=" * (4 - len(payload_b64) % 4)
            return _json.loads(base64.urlsafe_b64decode(payload_b64)).get("sub")
        except Exception:
            pass
    return None


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

@router.post("/harvest-acceptance/{harvest_acceptance_id}/create-credit-note", response_model=SelfBillingInvoiceOut, status_code=201)
async def create_credit_note_endpoint(
    harvest_acceptance_id: str,
    payload: CreditNoteCreateIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    request: Request = None,
):
    """Erstellt eine Self-Billing Gutschrift für eine Ernte-Annahme."""
    user_id = _get_user_id_from_request(request)
    
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
    
    repo = SelfBillingRepositoryImpl(db)
    invoice = create_credit_note(repo, create_input, taxation_type=payload.taxation_type)
    
    return _to_out(invoice)


@router.get("/{invoice_id}", response_model=SelfBillingInvoiceOut)
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


@router.get("/harvest-acceptance/{harvest_acceptance_id}", response_model=Optional[SelfBillingInvoiceOut])
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


@router.post("/{invoice_id}/issue", response_model=SelfBillingInvoiceOut)
async def issue_invoice_endpoint(
    invoice_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    request: Request = None,
):
    """Gibt eine Gutschrift aus (Status: draft → issued)."""
    user_id = _get_user_id_from_request(request)
    
    repo = SelfBillingRepositoryImpl(db)
    invoice = repo.get_invoice_by_id(invoice_id)
    
    if not invoice:
        raise HTTPException(status_code=404, detail=f"Invoice {invoice_id} not found")
    
    if invoice.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    invoice = issue_invoice(repo, invoice_id, updated_by=user_id)
    return _to_out(invoice)


@router.post("/{invoice_id}/generate-einvoice", response_model=SelfBillingInvoiceOut)
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


@router.post("/{invoice_id}/send", response_model=SelfBillingInvoiceOut)
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


@router.post("/{invoice_id}/dispute", response_model=dict)
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


@router.post("/preview", response_model=dict)
async def preview_self_billing(
    payload: PreviewIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """
    Preview Self-Billing für Ernte-Annahme.
    Liefert Draft mit Beträgen, MwSt, Positionen ohne Persistierung.
    """
    from modules.agrar.services.self_billing_service import create_credit_note, CreditNoteCreate
    # Placeholder: Berechne aus harvest_acceptance (Positionen, Preise, Qualität)
    # Hier: Minimal-Draft basierend auf Annahme-Summen
    return {
        "harvest_acceptance_id": payload.harvest_acceptance_id,
        "status": "draft",
        "total_net_amount_eur": 0,
        "total_vat_amount_eur": 0,
        "total_gross_amount_eur": 0,
        "vat_rate_percent": 0,
        "line_items": [],
        "note": "Preview: Beträge aus Ernte-Annahme-Positionen berechnen (TODO: Vollimplementierung)",
    }


@router.post("/{invoice_id}/storno", response_model=dict)
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

    if invoice.status not in ("issued", "paid"):
        raise HTTPException(status_code=400, detail="Nur issued/paid Gutschriften können storniert werden")

    # Storno: Negative Gutschrift mit gleicher Nummer + Storno-Suffix
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
    storno_invoice_entity = create_credit_note(repo, storno_input, taxation_type="regular")

    return {
        "message": "Storno erstellt",
        "storno_invoice": _to_out(storno_invoice_entity),
        "original_invoice_id": invoice_id,
    }


@router.get("/{invoice_id}/export")
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


@router.get("/{invoice_id}/disputes", response_model=list[dict])
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

@router.post("/{invoice_id}/buchung", response_model=dict)
async def buche_gutschrift(
    invoice_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """
    Buche Gutschrift in Buchhaltung (Fibu).
    
    Erstellt Buchungssatz:
    - Soll: Lieferantenkonto (Kreditor)
    - Haben: Erlöskonto / Umsatzsteuer
    """
    from app.infrastructure.models import Buchung, BusinessPartner
    from modules.agrar.repositories.self_billing_repo import SelfBillingRepositoryImpl
    
    repo = SelfBillingRepositoryImpl(db)
    invoice = repo.get_invoice_by_id(invoice_id)
    
    if not invoice:
        raise HTTPException(status_code=404, detail=f"Gutschrift {invoice_id} nicht gefunden")
    
    if invoice.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if invoice.status != "issued":
        raise HTTPException(status_code=400, detail="Gutschrift muss erst issued sein")
    
    # Hole Harvest Acceptance für Lieferanten-Info
    from app.infrastructure.models import HarvestAcceptance
    harvest = db.query(HarvestAcceptance).filter(
        HarvestAcceptance.id == invoice.harvest_acceptance_id
    ).first()
    
    if not harvest:
        raise HTTPException(status_code=400, detail="Ernte-Annahme nicht gefunden")
    
    # Hole Lieferant
    supplier = db.query(BusinessPartner).filter(
        BusinessPartner.id == harvest.supplier_id,
        BusinessPartner.tenant_id == tenant_id
    ).first()
    
    # Generiere Buchungssatz
    from app.core.uuid7 import uuid7
    from datetime import date
    from decimal import Decimal

    buchung = Buchung(
        id=uuid7(),
        tenant_id=tenant_id,
        belegnr=f"SB-{invoice.invoice_number}",
        datum=date.today(),
        soll_konto="1600",  # Kreditoren
        haben_konto="4200",  # Erlöse Landwirtschaft
        betrag=Decimal(str(invoice.total_net_amount_eur)),
        text=f"Gutschrift {invoice.invoice_number} - {supplier.name if supplier else 'Lieferant'}",
        belart="SB",  # Self-Billing
        created_at=datetime.now(),
    )
    db.add(buchung)
    
    # Erstelle auch Umsatzsteuer-Buchung
    if invoice.total_vat_amount_eur > 0:
        buchung_st = Buchung(
            id=uuid7(),
            tenant_id=tenant_id,
            belegnr=f"SB-{invoice.invoice_number}",
            datum=date.today(),
            soll_konto="1600",  # Kreditoren
            haben_konto="1400",  # Umsatzsteuer
            betrag=Decimal(str(invoice.total_vat_amount_eur)),
            text=f"UST Gutschrift {invoice.invoice_number}",
            belart="SB",
            created_at=datetime.now(),
        )
        db.add(buchung_st)
    
    # Markiere Gutschrift als gebucht
    invoice.status = "booked"
    invoice.updated_at = datetime.now()
    
    db.commit()
    
    return {
        "message": "Gutschrift gebucht",
        "buchung_id": buchung.id,
        "belegnr": buchung.belegnr,
        "betrag": float(buchung.betrag),
    }


