"""
VAT Service.
Handles VAT logic for different acceptance modes and advance payments.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Optional, Literal

from sqlalchemy.orm import Session

from app.infrastructure.models import HarvestAcceptance, SelfBillingInvoice
from modules.agrar.services.self_billing_service import (
    create_credit_note,
    CreditNoteCreate,
)
from modules.agrar.repositories.self_billing_repo import SelfBillingRepositoryImpl
from modules.agrar.services.tax_profile_service import get_taxation_type_for_supplier


AcceptanceMode = Literal["STORAGE_ONLY", "PURCHASE_AT_DELIVERY_PTBF", "ADVANCE_ON_STORAGE"]
VatEvent = Literal["NO_INVOICE", "PROVISIONAL_CREDIT_NOTE_CREATED", "FINAL_CREDIT_NOTE_CREATED", "CORRECTION_ISSUED"]


def determine_ownership_type(acceptance_mode: str) -> str:
    """
    Bestimmt ownership_type basierend auf acceptance_mode.
    
    Args:
        acceptance_mode: STORAGE_ONLY / PURCHASE_AT_DELIVERY_PTBF / ADVANCE_ON_STORAGE
    
    Returns:
        ownership_type: THIRD_PARTY_STOCK oder OWN_STOCK
    """
    if acceptance_mode == "STORAGE_ONLY":
        return "THIRD_PARTY_STOCK"
    else:
        return "OWN_STOCK"


def can_create_credit_note_for_vat(acceptance_mode: str, vat_event: str) -> bool:
    """
    Prüft, ob eine Gutschrift für Vorsteuerabzug erstellt werden kann.
    
    Regeln:
    - STORAGE_ONLY: Keine Gutschrift (keine Vorsteuer)
    - PURCHASE_AT_DELIVERY_PTBF: Gutschrift möglich (vorläufig oder final)
    - ADVANCE_ON_STORAGE: Nur Anzahlungsgutschrift nach Zahlung
    
    Args:
        acceptance_mode: Geschäftsmodell
        vat_event: Aktuelles VAT-Ereignis
    
    Returns:
        bool: True, wenn Gutschrift erstellt werden kann
    """
    if acceptance_mode == "STORAGE_ONLY":
        return False
    
    if acceptance_mode == "ADVANCE_ON_STORAGE":
        # Nur wenn Anzahlung bereits gezahlt wurde
        return vat_event == "NO_INVOICE"  # Kann Anzahlungsgutschrift erstellen
    
    if acceptance_mode == "PURCHASE_AT_DELIVERY_PTBF":
        # Kann vorläufige oder finale Gutschrift erstellen
        return vat_event in ("NO_INVOICE", "PROVISIONAL_CREDIT_NOTE_CREATED")
    
    return False


def create_provisional_credit_note(
    db: Session,
    acceptance: HarvestAcceptance,
    tenant_id: str,
    user_id: Optional[str] = None,
) -> Optional[SelfBillingInvoice]:
    """
    Erstellt vorläufige Self-Billing Gutschrift (für PURCHASE_AT_DELIVERY_PTBF).
    
    Voraussetzungen:
    - acceptance_mode = PURCHASE_AT_DELIVERY_PTBF
    - total_gross_amount_eur muss gesetzt sein (kann vorläufig geschätzt sein)
    
    Args:
        db: Database session
        acceptance: HarvestAcceptance
        tenant_id: Tenant ID
        user_id: User ID (optional)
    
    Returns:
        SelfBillingInvoice oder None, wenn nicht möglich
    """
    if not can_create_credit_note_for_vat(acceptance.acceptance_mode or "PURCHASE_AT_DELIVERY_PTBF", acceptance.vat_event or "NO_INVOICE"):
        return None
    
    if not acceptance.total_gross_amount_eur:
        return None
    
    # Hole MWSt-Satz
    vat_rate_percent = Decimal("0")
    if acceptance.vat_rate_percent:
        vat_rate_percent = acceptance.vat_rate_percent
    else:
        # Fallback: Standard-MWSt oder §24-Pauschalierung
        vat_rate_percent = Decimal("19.0")
    
    # Hole Taxation Type
    taxation_type = "regular"
    if acceptance.customer_id:
        taxation_type = get_taxation_type_for_supplier(
            db=db,
            supplier_id=acceptance.customer_id,
            tenant_id=tenant_id,
            effective_date=acceptance.delivery_date,
        )
        
        # §24-Pauschalierung: 7,8% seit 01.01.2025
        if taxation_type == "ustg24_flat_rate":
            vat_rate_percent = Decimal("7.8")
    
    # Erstelle vorläufige Gutschrift
    billing_repo = SelfBillingRepositoryImpl(db)
    credit_note_input = CreditNoteCreate(
        tenant_id=tenant_id,
        harvest_acceptance_id=acceptance.id,
        total_net_amount_eur=acceptance.total_net_amount_eur or Decimal("0"),
        total_vat_amount_eur=acceptance.total_vat_amount_eur or Decimal("0"),
        total_gross_amount_eur=acceptance.total_gross_amount_eur,
        vat_rate_percent=vat_rate_percent,
        created_by=user_id or "system",
    )
    
    invoice = create_credit_note(billing_repo, credit_note_input, taxation_type=taxation_type)
    
    # Aktualisiere VAT-Event
    acceptance.vat_event = "PROVISIONAL_CREDIT_NOTE_CREATED"
    acceptance.invoice_id = invoice.id
    db.commit()
    
    return invoice


def create_advance_payment_credit_note(
    db: Session,
    acceptance: HarvestAcceptance,
    tenant_id: str,
    advance_amount_eur: Decimal,
    advance_date: date,
    user_id: Optional[str] = None,
) -> Optional[SelfBillingInvoice]:
    """
    Erstellt Anzahlungsgutschrift (für ADVANCE_ON_STORAGE).
    
    Voraussetzungen:
    - acceptance_mode = ADVANCE_ON_STORAGE
    - advance_payment_amount_eur muss gesetzt sein
    - advance_payment_date muss gesetzt sein
    
    Wichtig: Vorsteuerabzug nur nach Zahlung möglich!
    
    Args:
        db: Database session
        acceptance: HarvestAcceptance
        tenant_id: Tenant ID
        advance_amount_eur: Anzahlungsbetrag
        advance_date: Anzahlungsdatum
        user_id: User ID (optional)
    
    Returns:
        SelfBillingInvoice oder None, wenn nicht möglich
    """
    if acceptance.acceptance_mode != "ADVANCE_ON_STORAGE":
        return None
    
    # Berechne MWSt (vereinfacht: 19% oder §24-Pauschalierung 7,8%)
    taxation_type = "regular"
    vat_rate_percent = Decimal("19.0")
    
    if acceptance.customer_id:
        taxation_type = get_taxation_type_for_supplier(
            db=db,
            supplier_id=acceptance.customer_id,
            tenant_id=tenant_id,
            effective_date=advance_date,
        )
        
        if taxation_type == "ustg24_flat_rate":
            vat_rate_percent = Decimal("7.8")
    
    # Berechne Netto und MWSt
    net_amount = advance_amount_eur / (Decimal("1") + (vat_rate_percent / Decimal("100")))
    vat_amount = advance_amount_eur - net_amount
    
    # Erstelle Anzahlungsgutschrift
    billing_repo = SelfBillingRepositoryImpl(db)
    credit_note_input = CreditNoteCreate(
        tenant_id=tenant_id,
        harvest_acceptance_id=acceptance.id,
        total_net_amount_eur=net_amount,
        total_vat_amount_eur=vat_amount,
        total_gross_amount_eur=advance_amount_eur,
        vat_rate_percent=vat_rate_percent,
        created_by=user_id or "system",
    )
    
    invoice = create_credit_note(billing_repo, credit_note_input, taxation_type=taxation_type)
    
    # Aktualisiere Acceptance
    acceptance.advance_payment_amount_eur = advance_amount_eur
    acceptance.advance_payment_date = advance_date
    acceptance.advance_invoice_id = invoice.id
    acceptance.vat_event = "PROVISIONAL_CREDIT_NOTE_CREATED"
    db.commit()
    
    return invoice


def create_correction_credit_note(
    db: Session,
    acceptance: HarvestAcceptance,
    tenant_id: str,
    corrected_amount_eur: Decimal,
    user_id: Optional[str] = None,
) -> Optional[SelfBillingInvoice]:
    """
    Erstellt Korrekturgutschrift (für Preisänderungen nach vorläufiger Gutschrift).
    
    Args:
        db: Database session
        acceptance: HarvestAcceptance
        tenant_id: Tenant ID
        corrected_amount_eur: Korrigierter Betrag
        user_id: User ID (optional)
    
    Returns:
        SelfBillingInvoice oder None, wenn nicht möglich
    """
    if acceptance.vat_event not in ("PROVISIONAL_CREDIT_NOTE_CREATED", "FINAL_CREDIT_NOTE_CREATED"):
        return None
    
    # Berechne Differenz
    original_amount = acceptance.total_gross_amount_eur or Decimal("0")
    difference = corrected_amount_eur - original_amount
    
    if difference == 0:
        return None  # Keine Korrektur nötig
    
    # Hole MWSt-Satz
    vat_rate_percent = acceptance.vat_rate_percent or Decimal("19.0")
    
    # Berechne Netto und MWSt für Differenz
    net_difference = difference / (Decimal("1") + (vat_rate_percent / Decimal("100")))
    vat_difference = difference - net_difference
    
    # Erstelle Korrekturgutschrift (Lastschrift bei negativer Differenz)
    billing_repo = SelfBillingRepositoryImpl(db)
    credit_note_input = CreditNoteCreate(
        tenant_id=tenant_id,
        harvest_acceptance_id=acceptance.id,
        total_net_amount_eur=net_difference,
        total_vat_amount_eur=vat_difference,
        total_gross_amount_eur=difference,
        vat_rate_percent=vat_rate_percent,
        created_by=user_id or "system",
    )
    
    taxation_type = "regular"
    if acceptance.customer_id:
        taxation_type = get_taxation_type_for_supplier(
            db=db,
            supplier_id=acceptance.customer_id,
            tenant_id=tenant_id,
            effective_date=acceptance.delivery_date,
        )
    
    invoice = create_credit_note(billing_repo, credit_note_input, taxation_type=taxation_type)
    
    # Aktualisiere VAT-Event
    acceptance.vat_event = "CORRECTION_ISSUED"
    db.commit()
    
    return invoice


