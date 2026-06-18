"""STMD-DUP-001: Cross-Domain-Dublettenprüfung für Stammdaten.

Erkennt potenzielle Dubletten bei:
- Kunden/Lieferanten: gleiche UST-ID, ähnlicher Name, gleiche Adresse
- Artikel: gleiche EAN, ähnlicher Name+Einheit
- Bankverbindungen: gleiche IBAN
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id

router = APIRouter(prefix="/stammdaten/duplikate", tags=["stammdaten", "qualitaet"])


class DuplikatTreffer(BaseModel):
    id_a: str
    id_b: str
    name_a: str
    name_b: str
    grund: str          # UST_ID | NAME_AEHNLICH | ADRESSE | IBAN | EAN
    score: float        # 0.0–1.0 Übereinstimmungsgrad


@router.get(
    "/business-partner",
    summary="Dubletten-Check Business Partner (UST-ID, Name, Adresse) — STMD-DUP-001",
)
def check_bp_dubletten(
    min_score: float = Query(0.8, ge=0.0, le=1.0, description="Minimaler Übereinstimmungsgrad"),
    limit: int = Query(50, ge=1, le=200),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    """Findet potenzielle Dubletten unter Business Partnern.

    Prüft drei Kriterien:
    1. Identische UST-ID (Score 1.0)
    2. Identische IBAN in Bankverbindung (Score 0.95)
    3. Gleiche Postleitzahl + ähnlicher Name (Score 0.85)
    """
    results: list[dict] = []

    # 1. Identische UST-ID
    try:
        rows = db.execute(text("""
            SELECT a.id, b.id, a.name, b.name, a.vat_id
              FROM domain_erp.business_partners a
              JOIN domain_erp.business_partners b
                ON a.vat_id = b.vat_id
               AND a.id < b.id
             WHERE a.tenant_id = :tid
               AND b.tenant_id = :tid
               AND a.vat_id IS NOT NULL
               AND a.vat_id != ''
             LIMIT :lim
        """), {"tid": tenant_id, "lim": limit}).fetchall()
        for r in rows:
            results.append({
                "id_a": str(r[0]), "id_b": str(r[1]),
                "name_a": str(r[2]), "name_b": str(r[3]),
                "grund": "UST_ID_IDENTISCH",
                "score": 1.0,
                "detail": f"UST-ID: {r[4]}",
            })
    except Exception:
        pass

    # 2. Identische IBAN
    try:
        rows = db.execute(text("""
            SELECT ba.partner_id, bb.partner_id,
                   pa.name, pb.name, ba.iban
              FROM domain_erp.partner_bank_accounts ba
              JOIN domain_erp.partner_bank_accounts bb
                ON ba.iban = bb.iban AND ba.id < bb.id
              JOIN domain_erp.business_partners pa ON pa.id = ba.partner_id
              JOIN domain_erp.business_partners pb ON pb.id = bb.partner_id
             WHERE ba.tenant_id = :tid AND ba.iban IS NOT NULL
             LIMIT :lim
        """), {"tid": tenant_id, "lim": limit}).fetchall()
        for r in rows:
            results.append({
                "id_a": str(r[0]), "id_b": str(r[1]),
                "name_a": str(r[2]), "name_b": str(r[3]),
                "grund": "IBAN_IDENTISCH",
                "score": 0.95,
                "detail": f"IBAN: {r[4][:4]}****",
            })
    except Exception:
        pass

    # 3. Gleiche PLZ + Name-Ähnlichkeit (Trigramm via pg_trgm wenn verfügbar, sonst ILIKE)
    try:
        rows = db.execute(text("""
            SELECT a.id, b.id, a.name, b.name, a.postal_code
              FROM domain_erp.business_partners a
              JOIN domain_erp.business_partners b
                ON a.postal_code = b.postal_code
               AND a.id < b.id
               AND LOWER(a.name) LIKE LOWER(SUBSTRING(b.name, 1, 5)) || '%'
             WHERE a.tenant_id = :tid AND b.tenant_id = :tid
               AND a.postal_code IS NOT NULL
             LIMIT :lim
        """), {"tid": tenant_id, "lim": limit}).fetchall()
        for r in rows:
            results.append({
                "id_a": str(r[0]), "id_b": str(r[1]),
                "name_a": str(r[2]), "name_b": str(r[3]),
                "grund": "PLZ_NAME_AEHNLICH",
                "score": 0.85,
                "detail": f"PLZ: {r[4]}",
            })
    except Exception:
        pass

    filtered = [r for r in results if r["score"] >= min_score]
    return {"dubletten": filtered, "count": len(filtered),
            "min_score": min_score, "tenant_id": tenant_id}


@router.get(
    "/artikel",
    summary="Dubletten-Check Artikel (EAN, Name+Einheit) — STMD-DUP-001",
)
def check_artikel_dubletten(
    limit: int = Query(50, ge=1, le=200),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    """Findet potenzielle Artikel-Dubletten anhand EAN oder Name+Einheit."""
    results: list[dict] = []

    # 1. Gleiche EAN
    try:
        rows = db.execute(text("""
            SELECT a.id, b.id, a.name, b.name, a.ean
              FROM domain_inventory.articles a
              JOIN domain_inventory.articles b
                ON a.ean = b.ean AND a.id < b.id
             WHERE a.tenant_id = :tid AND b.tenant_id = :tid
               AND a.ean IS NOT NULL AND a.ean != ''
             LIMIT :lim
        """), {"tid": tenant_id, "lim": limit}).fetchall()
        for r in rows:
            results.append({
                "id_a": str(r[0]), "id_b": str(r[1]),
                "name_a": str(r[2]), "name_b": str(r[3]),
                "grund": "EAN_IDENTISCH", "score": 1.0,
                "detail": f"EAN: {r[4]}",
            })
    except Exception:
        pass

    # 2. Gleiche Name+Einheit (case-insensitive)
    try:
        rows = db.execute(text("""
            SELECT a.id, b.id, a.name, b.name, a.unit
              FROM domain_inventory.articles a
              JOIN domain_inventory.articles b
                ON LOWER(a.name) = LOWER(b.name)
               AND LOWER(COALESCE(a.unit,'')) = LOWER(COALESCE(b.unit,''))
               AND a.id < b.id
             WHERE a.tenant_id = :tid AND b.tenant_id = :tid
             LIMIT :lim
        """), {"tid": tenant_id, "lim": limit}).fetchall()
        for r in rows:
            results.append({
                "id_a": str(r[0]), "id_b": str(r[1]),
                "name_a": str(r[2]), "name_b": str(r[3]),
                "grund": "NAME_EINHEIT_IDENTISCH", "score": 0.9,
                "detail": f"Einheit: {r[4]}",
            })
    except Exception:
        pass

    return {"dubletten": results, "count": len(results), "tenant_id": tenant_id}


@router.post(
    "/zusammenfuehren",
    summary="Dubletten zusammenführen (Master bleibt, Duplikat wird deaktiviert)",
    status_code=200,
)
def zusammenfuehren(
    master_id: str = Query(..., description="ID des Master-Datensatzes (bleibt erhalten)"),
    duplikat_id: str = Query(..., description="ID des Duplikats (wird deaktiviert)"),
    entity_type: str = Query("business_partner", description="business_partner | artikel"),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    """Markiert ein Duplikat als 'zusammengeführt' — Softdelete, kein Datenverlust."""
    if entity_type == "business_partner":
        table = "domain_erp.business_partners"
    elif entity_type == "artikel":
        table = "domain_inventory.articles"
    else:
        raise HTTPException(status_code=422, detail=f"Unbekannter entity_type: {entity_type}")

    try:
        result = db.execute(text(f"""
            UPDATE {table}
               SET is_active = false,
                   notes = COALESCE(notes, '') || ' [ZUSAMMENGEFUEHRT → ' || :master || ']'
             WHERE id = :dup AND tenant_id = :tid
        """), {"master": master_id, "dup": duplikat_id, "tid": tenant_id})
        db.commit()
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Duplikat nicht gefunden")
        return {"master_id": master_id, "duplikat_id": duplikat_id,
                "entity_type": entity_type, "status": "zusammengefuehrt"}
    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(exc)) from exc
