"""
Einkauf — ERS (Evaluated Receipt Settlement)

Automatische Rechnungserzeugung bei Wareneingang für qualifizierte Lieferanten.

Endpoints:
  GET  /einkauf/ers/suppliers             → ERS-qualifizierte Lieferanten
  POST /einkauf/ers/suppliers/{id}/qualify → Lieferant als ERS-fähig markieren
  POST /einkauf/ers/trigger               → ERS-Lauf für Wareneingang auslösen
  GET  /einkauf/ers/invoices              → Liste aller ERS-erzeugten Rechnungen
"""
from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.ers_settlement_schemas import ErsSettlementOut


router = APIRouter(prefix="/einkauf/ers", tags=["einkauf", "ers"])


# ─────────────────────────────────────────────────────────────────────────────
# Schemas
# ─────────────────────────────────────────────────────────────────────────────

class QualifyRequest(BaseModel):
    ers_tolerance_percent: float = 2.0


class ErsRunRequest(BaseModel):
    gr_id: str
    supplier_id: str


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _ensure_schema(db: Session) -> None:
    db.execute(text("CREATE SCHEMA IF NOT EXISTS domain_einkauf"))
    db.execute(text("""
        CREATE TABLE IF NOT EXISTS domain_einkauf.ers_suppliers (
            id                   BIGSERIAL PRIMARY KEY,
            supplier_id          TEXT NOT NULL,
            is_ers_qualified     BOOLEAN NOT NULL DEFAULT FALSE,
            ers_tolerance_percent NUMERIC(10,4) DEFAULT 2.0,
            tenant_id            TEXT,
            UNIQUE (supplier_id, tenant_id)
        )
    """))
    db.execute(text("""
        CREATE TABLE IF NOT EXISTS domain_einkauf.ers_invoices (
            id              BIGSERIAL PRIMARY KEY,
            gr_id           TEXT NOT NULL,
            supplier_id     TEXT NOT NULL,
            amount          NUMERIC(18,4),
            status          TEXT NOT NULL DEFAULT 'ERSTELLT',
            auto_created_at TIMESTAMPTZ DEFAULT NOW(),
            tenant_id       TEXT
        )
    """))
    db.commit()


def _fetch_gr_amount(db: Session, gr_id: str, tenant_id: str) -> Optional[float]:
    for table in [
        "domain_einkauf.wareneingaenge",
        "public.goods_receipts",
        "public.einkauf_wareneingaenge",
    ]:
        try:
            row = db.execute(
                text(f"SELECT gesamtbetrag FROM {table} WHERE id = :id AND tenant_id = :tid LIMIT 1"),  # nosec B608  # reviewed-safe: column names code-controlled, values parameterized
                {"id": gr_id, "tid": tenant_id},
            ).fetchone()
            if row:
                return float(row[0])
        except Exception:  # noqa: BLE001 — Tabelle nicht gefunden; gibt None zurück
            pass
    return None


# ─────────────────────────────────────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/suppliers", summary="Ers suppliers auflisten",
    response_model=list[ErsSettlementOut]
)
def list_ers_suppliers(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict[str, Any]]:
    """ERS-qualifizierte Lieferanten auflisten."""
    try:
        _ensure_schema(db)
        rows = db.execute(
            text("""
                SELECT id, supplier_id, is_ers_qualified, ers_tolerance_percent
                FROM domain_einkauf.ers_suppliers
                WHERE tenant_id = :tid AND is_ers_qualified = TRUE
                ORDER BY supplier_id
            """),
            {"tid": tenant_id},
        ).fetchall()
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Datenbankfehler: {exc}") from exc

    return [
        {
            "id": r[0],
            "supplier_id": r[1],
            "is_ers_qualified": r[2],
            "ers_tolerance_percent": float(r[3]) if r[3] else 2.0,
        }
        for r in rows
    ]


@router.post("/suppliers/{supplier_id}/qualify", summary="Supplier qualify",
    response_model=ErsSettlementOut
)
def qualify_supplier(
    supplier_id: str,
    body: QualifyRequest,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    """Lieferant als ERS-fähig markieren (INSERT OR UPDATE)."""
    try:
        _ensure_schema(db)
        row = db.execute(
            text("""
                INSERT INTO domain_einkauf.ers_suppliers
                    (supplier_id, is_ers_qualified, ers_tolerance_percent, tenant_id)
                VALUES (:sid, TRUE, :tol, :tid)
                ON CONFLICT (supplier_id, tenant_id)
                DO UPDATE SET
                    is_ers_qualified = TRUE,
                    ers_tolerance_percent = EXCLUDED.ers_tolerance_percent
                RETURNING id, supplier_id, is_ers_qualified, ers_tolerance_percent
            """),
            {"sid": supplier_id, "tol": body.ers_tolerance_percent, "tid": tenant_id},
        ).fetchone()
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=503, detail=f"Datenbankfehler: {exc}") from exc

    return {
        "id": row[0],
        "supplier_id": row[1],
        "is_ers_qualified": row[2],
        "ers_tolerance_percent": float(row[3]) if row[3] else 2.0,
    }


@router.post("/trigger", summary="Ers auslösen",
    response_model=ErsSettlementOut
)
def trigger_ers(
    body: ErsRunRequest,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    """ERS-Lauf für Wareneingang auslösen.

    Prüft ob Lieferant ERS-qualifiziert ist und erzeugt automatisch eine ap_invoice.
    """
    try:
        _ensure_schema(db)

        # Lieferant ERS-Qualifikation prüfen
        supplier_row = db.execute(
            text("""
                SELECT id, is_ers_qualified, ers_tolerance_percent
                FROM domain_einkauf.ers_suppliers
                WHERE supplier_id = :sid AND tenant_id = :tid
                LIMIT 1
            """),
            {"sid": body.supplier_id, "tid": tenant_id},
        ).fetchone()
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Datenbankfehler: {exc}") from exc

    if not supplier_row or not supplier_row[1]:
        return {
            "success": False,
            "reason": "Lieferant nicht ERS-qualifiziert",
            "supplier_id": body.supplier_id,
            "gr_id": body.gr_id,
        }

    # GR-Betrag ermitteln
    gr_amount = _fetch_gr_amount(db, body.gr_id, tenant_id)

    try:
        # ERS-Rechnung anlegen
        inv_row = db.execute(
            text("""
                INSERT INTO domain_einkauf.ers_invoices
                    (gr_id, supplier_id, amount, status, tenant_id)
                VALUES (:gr_id, :sid, :amount, 'ERSTELLT', :tid)
                RETURNING id, auto_created_at
            """),
            {
                "gr_id": body.gr_id,
                "sid": body.supplier_id,
                "amount": gr_amount,
                "tid": tenant_id,
            },
        ).fetchone()
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=503, detail=f"Datenbankfehler: {exc}") from exc

    # Belegbruch schließen: Kreditoren-OP für ERS-Rechnung anlegen
    if gr_amount and gr_amount > 0:
        try:
            from datetime import date as _date
            import uuid as _uuid
            today = _date.today().isoformat()
            due_in_30 = (_date.today().replace(day=min(_date.today().day + 30, 28))).isoformat()
            ers_inv_nr = f"ERS-{inv_row[0]}"
            db.execute(text("""
                INSERT INTO domain_erp.offene_posten
                    (id, tenant_id, konto_typ, rechnungsnr, rechnungsdatum, datum, faelligkeit,
                     betrag, offen, lieferant_id, op_status)
                VALUES
                    (:id, :tid, 'kreditoren', :rnr, :rdat, :dat, :faell,
                     :betrag, :betrag, :sid, 'offen')
                ON CONFLICT DO NOTHING
            """), {
                "id": str(_uuid.uuid4()),
                "tid": tenant_id,
                "rnr": ers_inv_nr,
                "rdat": today, "dat": today, "faell": due_in_30,
                "betrag": gr_amount,
                "sid": body.supplier_id,
            })
            db.commit()
        except Exception:  # noqa: BLE001 — OP-Anlage nicht kritisch für ERS-Erfolg
            pass

    # Event: invoice_auto_created (best-effort, nicht blockierend)
    # In Produktion: NATS JetStream publish hier einfügen

    return {
        "success": True,
        "event": "invoice_auto_created",
        "ers_invoice_id": inv_row[0],
        "gr_id": body.gr_id,
        "supplier_id": body.supplier_id,
        "amount": gr_amount,
        "auto_created_at": inv_row[1].isoformat() if inv_row[1] else None,
    }


@router.get("/invoices", summary="Ers invoices auflisten",
    response_model=list[ErsSettlementOut]
)
def list_ers_invoices(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict[str, Any]]:
    """Liste aller ERS-erzeugten Rechnungen."""
    try:
        _ensure_schema(db)
        rows = db.execute(
            text("""
                SELECT id, gr_id, supplier_id, amount, status, auto_created_at
                FROM domain_einkauf.ers_invoices
                WHERE tenant_id = :tid
                ORDER BY auto_created_at DESC
            """),
            {"tid": tenant_id},
        ).fetchall()
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Datenbankfehler: {exc}") from exc

    return [
        {
            "id": r[0],
            "gr_id": r[1],
            "supplier_id": r[2],
            "amount": float(r[3]) if r[3] else None,
            "status": r[4],
            "auto_created_at": r[5].isoformat() if r[5] else None,
        }
        for r in rows
    ]
