"""
Tax Profile Service.
Handles supplier tax profile lookup for taxation type determination.
"""

from __future__ import annotations

from datetime import date
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.infrastructure.models import SupplierTaxProfile


def get_taxation_type_for_supplier(
    db: Session,
    supplier_id: str,
    tenant_id: str,
    effective_date: Optional[date] = None,
) -> str:
    """
    Ermittelt taxation_type für einen Lieferanten.
    
    Priorität:
    1. Supplier Tax Profile (gültig zum effective_date)
    2. Fallback: "regular"
    
    Args:
        db: Database session
        supplier_id: Business Partner ID des Lieferanten
        tenant_id: Tenant ID
        effective_date: Datum für Gültigkeitsprüfung (default: heute)
    
    Returns:
        taxation_type: "regular" | "ustg24_flat_rate" | "small_business"
    """
    if not effective_date:
        effective_date = date.today()
    
    # Suche gültiges Tax Profile
    profile = db.query(SupplierTaxProfile).filter(
        and_(
            SupplierTaxProfile.supplier_id == supplier_id,
            SupplierTaxProfile.tenant_id == tenant_id,
            SupplierTaxProfile.valid_from <= effective_date,
            or_(
                SupplierTaxProfile.valid_to.is_(None),
                SupplierTaxProfile.valid_to >= effective_date,
            ),
        )
    ).order_by(SupplierTaxProfile.valid_from.desc()).first()
    
    if profile:
        return profile.taxation_type
    
    # Fallback: Standard-Besteuerung
    return "regular"


