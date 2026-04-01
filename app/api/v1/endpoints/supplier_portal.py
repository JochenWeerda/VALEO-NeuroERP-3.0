from __future__ import annotations

from fastapi import APIRouter, Query, Depends
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import text

from ....core.database import get_db
from ....core.tenant import get_tenant_id

router = APIRouter(prefix="/supplier-portal", tags=["supplier-portal"])

# --- Schemas ---

class SupplierLieferungView(BaseModel):
    lieferung_id: str
    datum: str
    sorte: str
    menge_t: float
    qualitaet: str
    status: str
    abgerechnet: bool
    schema_version: int = 1

class SupplierKontraktView(BaseModel):
    lieferant_id: str
    kontrakt_id: str
    sorte: str
    menge_soll_t: float
    menge_geliefert_t: float
    offene_menge_t: float
    preis_eur_t: float
    status: str
    schema_version: int = 1

class SupplierPreisauskunft(BaseModel):
    sorte: str
    qualitaet: str
    stichtag: str
    preis_eur_t: Optional[float]
    verfuegbar: bool
    schema_version: int = 1

# --- Endpoints ---

@router.get("/lieferanten/{lieferant_id}/lieferungen", response_model=list[SupplierLieferungView])
def get_lieferant_lieferungen(
    lieferant_id: str,
    von: Optional[str] = Query(None),
    bis: Optional[str] = Query(None),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Lieferungen eines Lieferanten aus harvest_acceptances."""
    try:
        params: dict = {"lieferant_id": lieferant_id, "tenant_id": tenant_id}
        where_clauses = [
            "ha.customer_id = :lieferant_id",
            "ha.tenant_id = :tenant_id",
        ]
        if von:
            where_clauses.append("ha.acceptance_date >= :von")
            params["von"] = von
        if bis:
            where_clauses.append("ha.acceptance_date <= :bis")
            params["bis"] = bis

        rows = db.execute(text("""
            SELECT ha.id, ha.acceptance_date, ha.article_name,
                   COALESCE(ha.net_weight_kg, 0) / 1000.0 AS menge_t,
                   COALESCE(ha.quality_grade, '') AS qualitaet,
                   ha.release_status, ha.invoice_id
            FROM domain_inventory.harvest_acceptances ha
            WHERE {where_clause}
            ORDER BY ha.acceptance_date DESC
            LIMIT 100
        """.format(where_clause=" AND ".join(where_clauses))), params).fetchall()

        return [
            SupplierLieferungView(
                lieferung_id=r.id,
                datum=str(r.acceptance_date) if r.acceptance_date else "",
                sorte=r.article_name or "",
                menge_t=float(r.menge_t),
                qualitaet=r.qualitaet,
                status=r.release_status or "offen",
                abgerechnet=bool(r.invoice_id),
            )
            for r in rows
        ]
    except Exception:
        return []


@router.get("/lieferanten/{lieferant_id}/kontrakte", response_model=list[SupplierKontraktView])
def get_lieferant_kontrakte(
    lieferant_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Kontrakte eines Lieferanten mit Erfuellungsstand."""
    try:
        rows = db.execute(text("""
            SELECT ac.id, ac.article_name,
                   COALESCE(ac.quantity_contracted, 0) AS menge_soll,
                   COALESCE(ac.quantity_delivered, 0) AS menge_geliefert,
                   COALESCE(ac.fixed_price, 0) AS preis,
                   ac.status
            FROM domain_inventory.agrar_contracts ac
            WHERE ac.partner_id = :lieferant_id
              AND ac.tenant_id = :tenant_id
            ORDER BY ac.created_at DESC
            LIMIT 100
        """), {"lieferant_id": lieferant_id, "tenant_id": tenant_id}).fetchall()

        return [
            SupplierKontraktView(
                lieferant_id=lieferant_id,
                kontrakt_id=r.id,
                sorte=r.article_name or "",
                menge_soll_t=float(r.menge_soll),
                menge_geliefert_t=float(r.menge_geliefert),
                offene_menge_t=max(float(r.menge_soll) - float(r.menge_geliefert), 0),
                preis_eur_t=float(r.preis),
                status=r.status or "aktiv",
            )
            for r in rows
        ]
    except Exception:
        return []


@router.get("/preisauskunft", response_model=SupplierPreisauskunft)
def get_preisauskunft(
    sorte: str = Query(...),
    qualitaet: str = Query(...),
    stichtag: str = Query(...),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Preisauskunft: letzter Kontraktpreis fuer Sorte/Qualitaet."""
    try:
        row = db.execute(text("""
            SELECT ac.fixed_price
            FROM domain_inventory.agrar_contracts ac
            WHERE LOWER(ac.article_name) = LOWER(:sorte)
              AND ac.tenant_id = :tenant_id
              AND ac.status IN ('active', 'aktiv')
            ORDER BY ac.created_at DESC
            LIMIT 1
        """), {"sorte": sorte, "tenant_id": tenant_id}).fetchone()

        if row and row.fixed_price:
            return SupplierPreisauskunft(
                sorte=sorte, qualitaet=qualitaet, stichtag=stichtag,
                preis_eur_t=float(row.fixed_price), verfuegbar=True,
            )
    except Exception:
        pass

    return SupplierPreisauskunft(
        sorte=sorte, qualitaet=qualitaet, stichtag=stichtag,
        preis_eur_t=None, verfuegbar=False,
    )


@router.get("/silo-bestaende")
def get_silo_bestaende(
    tenant_id: str = Depends(get_tenant_id),
    lieferant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Aggregierte Silo-Bestaende, optional gefiltert nach Lieferant."""
    try:
        params = {"tenant_id": tenant_id, "lieferant_id": lieferant_id}
        rows = db.execute(text("""
            SELECT s.silo_number, s.article_name,
                   COALESCE(SUM(sl.current_quantity_kg), 0) / 1000.0 AS bestand_t,
                   s.capacity_kg / 1000.0 AS kapazitaet_t
            FROM domain_inventory.silos s
            LEFT JOIN domain_inventory.silo_lots sl
              ON sl.silo_id = s.id
             AND sl.tenant_id = :tenant_id
             AND (:lieferant_id IS NULL OR sl.source_partner_id = :lieferant_id)
            WHERE s.tenant_id = :tenant_id
            GROUP BY s.id, s.silo_number, s.article_name, s.capacity_kg
            ORDER BY s.silo_number
        """), params).fetchall()

        zellen = [
            {
                "silo_nr": r.silo_number,
                "sorte": r.article_name or "",
                "bestand_t": float(r.bestand_t),
                "kapazitaet_t": float(r.kapazitaet_t) if r.kapazitaet_t else 0,
            }
            for r in rows
        ]
        gesamt = sum(z["bestand_t"] for z in zellen)

        return {
            "tenant_id": tenant_id,
            "gesamtbestand_t": round(gesamt, 2),
            "zellen": zellen,
            "schema_version": 1,
        }
    except Exception:
        return {"tenant_id": tenant_id, "gesamtbestand_t": 0.0, "zellen": [], "schema_version": 1}
