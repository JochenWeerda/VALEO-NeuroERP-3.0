"""
NUTS-2 Service.
Handles NUTS-2 code derivation from postal codes using Eurostat correspondence tables.
"""

from __future__ import annotations

from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.infrastructure.models import Nuts2PostalCode


def derive_nuts2_from_postal_code(
    db: Session,
    postal_code: str,
    country_code: str = "DE",
    nuts_version: str = "NUTS 2024",
) -> Optional[str]:
    """
    Leitet NUTS-2-Code aus PLZ ab (über Eurostat correspondence tables).
    
    Args:
        db: Database session
        postal_code: Postleitzahl (5-stellig für DE)
        country_code: Ländercode (default: "DE")
        nuts_version: NUTS-Version (default: "NUTS 2024")
    
    Returns:
        nuts2_code: NUTS-2-Code (z.B. "DE12") oder None, wenn nicht gefunden
    """
    if not postal_code:
        return None
    
    # Normalisiere PLZ (entferne Leerzeichen)
    postal_code_clean = postal_code.strip().replace(" ", "")
    
    # Suche in NUTS-2 Postal Code Tabelle
    from datetime import date
    today = date.today()
    
    nuts2_entry = db.query(Nuts2PostalCode).filter(
        and_(
            Nuts2PostalCode.postal_code == postal_code_clean,
            Nuts2PostalCode.country_code == country_code,
            Nuts2PostalCode.nuts_version == nuts_version,
            Nuts2PostalCode.valid_from <= today,
            or_(
                Nuts2PostalCode.valid_to.is_(None),
                Nuts2PostalCode.valid_to >= today,
            ),
        )
    ).first()
    
    if nuts2_entry:
        return nuts2_entry.nuts2_code

    return None


def bulk_import_nuts2_postal_codes(
    db: Session,
    entries: list[dict],
) -> int:
    """
    Importiert NUTS-2 Postal Code Zuordnungen in Bulk.
    
    Args:
        db: Database session
        entries: Liste von Dicts mit {postal_code, city, country_code, nuts2_code, nuts_version, valid_from, valid_to}
    
    Returns:
        count: Anzahl der importierten Einträge
    """
    from datetime import date
    
    count = 0
    
    for entry in entries:
        # Prüfe, ob Eintrag bereits existiert
        existing = db.query(Nuts2PostalCode).filter(
            Nuts2PostalCode.postal_code == entry["postal_code"],
            Nuts2PostalCode.country_code == entry["country_code"],
            Nuts2PostalCode.nuts_version == entry.get("nuts_version", "NUTS 2024"),
        ).first()
        
        if existing:
            continue  # Überspringe bereits vorhandene Einträge
        
        nuts2_entry = Nuts2PostalCode(
            postal_code=entry["postal_code"],
            city=entry.get("city"),
            country_code=entry["country_code"],
            nuts2_code=entry["nuts2_code"],
            nuts_version=entry.get("nuts_version", "NUTS 2024"),
            valid_from=entry.get("valid_from", date.today()),
            valid_to=entry.get("valid_to"),
        )
        db.add(nuts2_entry)
        count += 1
    
    db.commit()
    return count

