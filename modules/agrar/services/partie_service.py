"""
Partie/Charge Service.
Handles automatic generation of lot/charge numbers for harvest acceptance.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.infrastructure.models import HarvestAcceptance, HarvestAcceptanceLine
from app.core.uuid7 import uuid7


def generate_lot_number(
    db: Session,
    acceptance_id: str,
    tenant_id: str,
    prefix: str = "LOT",
) -> str:
    """
    Generiert automatisch eine Partie/Charge-Nummer.
    
    Format: {PREFIX}-{YYYYMMDD}-{SEQUENCE}
    Beispiel: LOT-20260217-001
    
    Args:
        db: Database session
        acceptance_id: Harvest Acceptance ID
        tenant_id: Tenant ID
        prefix: Präfix für Partie-Nummer (default: "LOT")
    
    Returns:
        lot_number: Generierte Partie-Nummer
    """
    acceptance = db.query(HarvestAcceptance).filter(
        HarvestAcceptance.id == acceptance_id,
        HarvestAcceptance.tenant_id == tenant_id,
    ).first()
    
    if not acceptance:
        raise ValueError(f"Harvest acceptance {acceptance_id} not found")
    
    # Datum aus delivery_date oder heute
    if acceptance.delivery_date:
        date_str = acceptance.delivery_date.strftime("%Y%m%d")
    else:
        date_str = datetime.now().strftime("%Y%m%d")
    
    # Zähle bestehende Partien für dieses Datum
    count = db.query(func.count(HarvestAcceptanceLine.id)).filter(
        HarvestAcceptanceLine.tenant_id == tenant_id,
        HarvestAcceptanceLine.lot_id.like(f"{prefix}-{date_str}-%"),
    ).scalar() or 0
    
    # Generiere Sequenznummer (3-stellig, 001-999)
    sequence = str(count + 1).zfill(3)
    
    return f"{prefix}-{date_str}-{sequence}"


def create_harvest_acceptance_lines(
    db: Session,
    acceptance_id: str,
    tenant_id: str,
    silo_allocations: list[dict],
) -> list[HarvestAcceptanceLine]:
    """
    Erstellt HarvestAcceptanceLine Einträge für Silo-Verteilungen.
    
    Args:
        db: Database session
        acceptance_id: Harvest Acceptance ID
        tenant_id: Tenant ID
        silo_allocations: Liste von Dicts mit {silo_id, qty_kg_allocated, lot_id (optional)}
    
    Returns:
        lines: Liste der erstellten HarvestAcceptanceLine Objekte
    """
    acceptance = db.query(HarvestAcceptance).filter(
        HarvestAcceptance.id == acceptance_id,
        HarvestAcceptance.tenant_id == tenant_id,
    ).first()
    
    if not acceptance:
        raise ValueError(f"Harvest acceptance {acceptance_id} not found")
    
    lines = []
    line_number = 1
    
    for allocation in silo_allocations:
        # Generiere Partie-Nummer, falls nicht vorhanden
        lot_id = allocation.get("lot_id")
        if not lot_id:
            lot_id = generate_lot_number(db, acceptance_id, tenant_id)
        
        line = HarvestAcceptanceLine(
            id=uuid7(),
            tenant_id=tenant_id,
            harvest_acceptance_id=acceptance_id,
            line_number=line_number,
            silo_id=allocation.get("silo_id"),
            lot_id=lot_id,
            qty_kg_allocated=allocation.get("qty_kg_allocated", 0),
            notes=allocation.get("notes"),
        )
        db.add(line)
        lines.append(line)
        line_number += 1
    
    db.flush()
    return lines


