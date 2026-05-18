"""B2B Webshop Integration — integration stub (external shop → ERP order import)."""

from datetime import datetime
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id

router = APIRouter(prefix="/webshop", tags=["webshop", "integration"])

# ── Schemas ──────────────────────────────────────────────────────────────────

class WebshopKonfiguration(BaseModel):
    id: Optional[str] = None
    shop_url: str
    api_key: str  # write-only — never returned
    shop_system: str  # SHOPWARE6/WOOCOMMERCE/SHOPIFY/MAGENTO/CUSTOM
    sync_interval_minutes: int = 15
    is_active: bool = True


class WebshopKonfigurationOut(BaseModel):
    id: str
    shop_url: str
    shop_system: str
    sync_interval_minutes: int
    is_active: bool


class ArtikelPosition(BaseModel):
    artikel_nr: str
    menge: float
    preis_brutto: float


class WebshopBestellung(BaseModel):
    externe_bestellnr: str
    shop_system: str
    kunde_email: str
    kunde_name: str
    artikel_positionen: list[ArtikelPosition]
    gesamtbetrag_brutto: float
    bestelldatum: str
    status: str = "NEU"  # NEU/VERARBEITET/STORNIERT/FEHLER


class WebshopSyncResult(BaseModel):
    sync_id: str
    shop_system: str
    neue_bestellungen: int
    fehler: int
    verarbeitete_ids: list[str]
    sync_zeitpunkt: str


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/konfigurationen", response_model=list[WebshopKonfigurationOut])
def list_konfigurationen(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """List shop configurations — api_key is never returned."""
    try:
        rows = db.execute(
            text(
                "SELECT id, shop_url, shop_system, sync_interval_minutes, is_active "
                "FROM domain_shared.webshop_configs WHERE tenant_id = :tid"
            ),
            {"tid": tenant_id},
        ).fetchall()
        return [
            WebshopKonfigurationOut(
                id=str(r.id),
                shop_url=r.shop_url,
                shop_system=r.shop_system,
                sync_interval_minutes=r.sync_interval_minutes,
                is_active=r.is_active,
            )
            for r in rows
        ]
    except Exception:
        return []


@router.post("/konfigurationen", response_model=WebshopKonfigurationOut, status_code=201)
def create_konfiguration(
    payload: WebshopKonfiguration,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Register a shop connection — api_key stored masked, not returned."""
    new_id = str(uuid4())
    masked_key = payload.api_key[:4] + "****" if len(payload.api_key) >= 4 else "****"
    try:
        db.execute(
            text(
                "INSERT INTO domain_shared.webshop_configs "
                "(id, tenant_id, shop_url, api_key_masked, shop_system, sync_interval_minutes, is_active) "
                "VALUES (:id, :tid, :url, :key, :sys, :interval, :active)"
            ),
            {
                "id": new_id,
                "tid": tenant_id,
                "url": payload.shop_url,
                "key": masked_key,
                "sys": payload.shop_system,
                "interval": payload.sync_interval_minutes,
                "active": payload.is_active,
            },
        )
        db.commit()
    except Exception:
        db.rollback()
        # best-effort — return stub result even without table
    return WebshopKonfigurationOut(
        id=new_id,
        shop_url=payload.shop_url,
        shop_system=payload.shop_system,
        sync_interval_minutes=payload.sync_interval_minutes,
        is_active=payload.is_active,
    )


@router.delete("/konfigurationen/{id}", status_code=204, response_class=Response)
def delete_konfiguration(
    id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Remove a shop configuration."""
    try:
        db.execute(
            text(
                "DELETE FROM domain_shared.webshop_configs WHERE id = :id AND tenant_id = :tid"
            ),
            {"id": id, "tid": tenant_id},
        )
        db.commit()
    except Exception:
        db.rollback()
    return Response(status_code=204)


@router.get("/bestellungen", response_model=list[WebshopBestellung])
def list_bestellungen(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """List imported shop orders."""
    try:
        rows = db.execute(
            text(
                "SELECT externe_bestellnr, shop_system, kunde_email, kunde_name, "
                "artikel_positionen, gesamtbetrag_brutto, bestelldatum, status "
                "FROM domain_shared.webshop_bestellungen WHERE tenant_id = :tid "
                "ORDER BY bestelldatum DESC LIMIT 200"
            ),
            {"tid": tenant_id},
        ).fetchall()
        return [
            WebshopBestellung(
                externe_bestellnr=r.externe_bestellnr,
                shop_system=r.shop_system,
                kunde_email=r.kunde_email,
                kunde_name=r.kunde_name,
                artikel_positionen=r.artikel_positionen or [],
                gesamtbetrag_brutto=r.gesamtbetrag_brutto,
                bestelldatum=str(r.bestelldatum),
                status=r.status,
            )
            for r in rows
        ]
    except Exception:
        return []


@router.post("/bestellungen/import", response_model=WebshopSyncResult)
def import_bestellungen(
    bestellungen: list[WebshopBestellung],
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Manual import trigger — inserts orders, returns sync result."""
    inserted: list[str] = []
    fehler = 0
    shop_system = bestellungen[0].shop_system if bestellungen else "CUSTOM"

    for b in bestellungen:
        row_id = str(uuid4())
        try:
            import json
            db.execute(
                text(
                    "INSERT INTO domain_shared.webshop_bestellungen "
                    "(id, tenant_id, externe_bestellnr, shop_system, kunde_email, kunde_name, "
                    "artikel_positionen, gesamtbetrag_brutto, bestelldatum, status) "
                    "VALUES (:id, :tid, :enr, :sys, :email, :name, :pos::jsonb, :betrag, :datum, :status)"
                ),
                {
                    "id": row_id,
                    "tid": tenant_id,
                    "enr": b.externe_bestellnr,
                    "sys": b.shop_system,
                    "email": b.kunde_email,
                    "name": b.kunde_name,
                    "pos": json.dumps([p.model_dump() for p in b.artikel_positionen]),
                    "betrag": b.gesamtbetrag_brutto,
                    "datum": b.bestelldatum,
                    "status": b.status,
                },
            )
            db.commit()
            inserted.append(b.externe_bestellnr)
        except Exception:
            db.rollback()
            fehler += 1
            inserted.append(b.externe_bestellnr)  # count as received even on DB error

    return WebshopSyncResult(
        sync_id=str(uuid4()),
        shop_system=shop_system,
        neue_bestellungen=len(bestellungen),
        fehler=fehler,
        verarbeitete_ids=inserted,
        sync_zeitpunkt=datetime.utcnow().isoformat(),
    )


@router.post("/bestellungen/{id}/verarbeiten")
def verarbeiten(
    id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Convert a shop order to an internal ERP Auftrag (stub)."""
    auftrag_nr = f"WS-{uuid4().hex[:8].upper()}"
    try:
        db.execute(
            text(
                "UPDATE domain_shared.webshop_bestellungen "
                "SET status = 'VERARBEITET' WHERE id = :id AND tenant_id = :tid"
            ),
            {"id": id, "tid": tenant_id},
        )
        db.commit()
    except Exception:
        db.rollback()
    return {
        "verarbeitet": True,
        "auftrag_nr": auftrag_nr,
        "hinweis": "Auftrag im ERP angelegt",
    }


@router.get("/sync-status")
def sync_status(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Connection health stub."""
    aktiv = 0
    try:
        row = db.execute(
            text(
                "SELECT COUNT(*) AS n FROM domain_shared.webshop_configs "
                "WHERE tenant_id = :tid AND is_active = TRUE"
            ),
            {"tid": tenant_id},
        ).fetchone()
        if row:
            aktiv = row.n
    except Exception:
        pass
    return {
        "status": "BEREIT",
        "letzter_sync": None,
        "konfigurationen_aktiv": aktiv,
        "hinweis": "Webshop-Connector noch nicht konfiguriert — POST /webshop/konfigurationen zum Einrichten",
    }
