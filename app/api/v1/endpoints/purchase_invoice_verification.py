"""
Einkauf — 3-Wege-Match (Purchase Order / Goods Receipt / Invoice Receipt)

Endpoints:
  POST  /einkauf/invoice-verification/match        → 3-Wege-Match durchführen
  GET   /einkauf/invoice-verification/pending      → Offene Prüfvorgänge
  PATCH /einkauf/invoice-verification/{id}/approve → Manuelle Freigabe
  PATCH /einkauf/invoice-verification/{id}/block   → Blockierung
  GET   /einkauf/invoice-verification/statistics   → Auswertung
"""
from __future__ import annotations

import uuid as _uuid
from datetime import date as _date, datetime
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id

from app.api.v1.schemas.base import BaseSchema, IDResponse
from app.api.v1.schemas.purchase_invoice_verification_schemas import PurchaseInvoiceVerificationOut


router = APIRouter(prefix="/einkauf/invoice-verification", tags=["einkauf", "3-wege-match"])


# ─────────────────────────────────────────────────────────────────────────────
# Schemas
# ─────────────────────────────────────────────────────────────────────────────

class MatchRequest(BaseModel):
    po_id: str
    gr_id: str
    invoice_id: str
    tolerance_percent: float = 2.0


class ApproveRequest(BaseModel):
    comment: Optional[str] = None


class BlockRequest(BaseModel):
    reason: Optional[str] = None


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _ensure_schema(db: Session) -> None:
    """Verify migration was applied; raise 503 if table is missing."""
    count = db.execute(text("""
        SELECT COUNT(*) FROM information_schema.tables
        WHERE table_schema = 'domain_einkauf' AND table_name = 'invoice_verification'
    """)).scalar()
    if not count:
        raise HTTPException(
            status_code=503,
            detail="3-Wege-Match-Tabelle nicht vorhanden — bitte 'alembic upgrade head' ausführen.",
        )


def _fetch_po_amount(db: Session, po_id: str, tenant_id: str) -> Optional[float]:
    """Betrag aus Bestellung lesen (verschiedene mögliche Tabellen)."""
    for table in [
        "domain_einkauf.bestellungen",
        "public.purchase_orders",
        "public.einkauf_bestellungen",
    ]:
        try:
            row = db.execute(
                text(f"SELECT gesamtbetrag FROM {table} WHERE id = :id AND tenant_id = :tid LIMIT 1"),  # nosec B608  # reviewed-safe: column names code-controlled, values parameterized
                {"id": po_id, "tid": tenant_id},
            ).fetchone()
            if row:
                return float(row[0])
        except Exception:  # noqa: BLE001 — Tabelle nicht gefunden; gibt None zurück
            pass
    return None


def _fetch_gr_amount(db: Session, gr_id: str, tenant_id: str) -> Optional[float]:
    """Betrag aus Wareneingang lesen."""
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


def _fetch_invoice_amount(db: Session, invoice_id: str, tenant_id: str) -> Optional[float]:
    """Betrag aus Eingangsrechnung lesen."""
    for col, table in [
        ("gesamtbetrag", "public.ap_invoices"),
        ("amount",       "public.ap_invoices"),
        ("total_amount", "public.ap_invoices"),
    ]:
        try:
            row = db.execute(
                text(f"SELECT {col} FROM {table} WHERE id = :id AND tenant_id = :tid LIMIT 1"),  # nosec B608  # reviewed-safe: column names code-controlled, values parameterized
                {"id": invoice_id, "tid": tenant_id},
            ).fetchone()
            if row:
                return float(row[0])
        except Exception:  # noqa: BLE001 — Tabelle nicht gefunden; gibt None zurück
            pass
    return None


def _compute_match_status(
    po_amount: Optional[float],
    gr_amount: Optional[float],
    invoice_amount: Optional[float],
    tolerance_percent: float,
) -> tuple[str, float, float]:
    """Returns (match_status, variance_amount, variance_percent)."""
    if po_amount is None or gr_amount is None or invoice_amount is None:
        return "OFFEN", 0.0, 0.0

    reference = min(po_amount, gr_amount)
    base = max(po_amount, gr_amount)
    if base == 0:
        return "GEMATCHT", 0.0, 0.0

    variance_amount = abs(invoice_amount - reference)
    variance_percent = variance_amount / base * 100

    if variance_percent == 0:
        status = "GEMATCHT"
    elif variance_percent <= tolerance_percent:
        status = "TOLERANZ"
    else:
        status = "DIFFERENZ"

    return status, variance_amount, variance_percent


# ─────────────────────────────────────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/match", summary="Invoice match",
    response_model=PurchaseInvoiceVerificationOut
)
def match_invoice(
    body: MatchRequest,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    """3-Wege-Match durchführen und Ergebnis speichern."""
    _ensure_schema(db)  # raises HTTPException(503) if migration not applied

    po_amount = _fetch_po_amount(db, body.po_id, tenant_id)
    gr_amount = _fetch_gr_amount(db, body.gr_id, tenant_id)
    invoice_amount = _fetch_invoice_amount(db, body.invoice_id, tenant_id)

    status, variance_amount, variance_percent = _compute_match_status(
        po_amount, gr_amount, invoice_amount, body.tolerance_percent
    )

    try:
        row = db.execute(
            text("""
                INSERT INTO domain_einkauf.invoice_verification
                    (po_id, gr_id, invoice_id, match_status,
                     po_amount, gr_amount, invoice_amount,
                     variance_amount, variance_percent, tolerance_percent, tenant_id)
                VALUES
                    (:po_id, :gr_id, :invoice_id, :status,
                     :po_amount, :gr_amount, :invoice_amount,
                     :variance_amount, :variance_percent, :tolerance_percent, :tenant_id)
                RETURNING id, created_at
            """),
            {
                "po_id": body.po_id,
                "gr_id": body.gr_id,
                "invoice_id": body.invoice_id,
                "status": status,
                "po_amount": po_amount,
                "gr_amount": gr_amount,
                "invoice_amount": invoice_amount,
                "variance_amount": variance_amount,
                "variance_percent": variance_percent,
                "tolerance_percent": body.tolerance_percent,
                "tenant_id": tenant_id,
            },
        ).fetchone()
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=503, detail=f"Datenbankfehler: {exc}") from exc

    return {
        "id": row[0],
        "po_id": body.po_id,
        "gr_id": body.gr_id,
        "invoice_id": body.invoice_id,
        "match_status": status,
        "po_amount": po_amount,
        "gr_amount": gr_amount,
        "invoice_amount": invoice_amount,
        "variance_amount": variance_amount,
        "variance_percent": round(variance_percent, 4),
        "tolerance_percent": body.tolerance_percent,
        "created_at": row[1].isoformat() if row[1] else None,
    }


@router.get("/pending", summary="Pending auflisten",
    response_model=list[PurchaseInvoiceVerificationOut]
)
def list_pending(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict[str, Any]]:
    """Alle offenen Prüfvorgänge (OFFEN oder DIFFERENZ)."""
    try:
        _ensure_schema(db)
        rows = db.execute(
            text("""
                SELECT id, po_id, gr_id, invoice_id, match_status,
                       po_amount, gr_amount, invoice_amount,
                       variance_amount, variance_percent, tolerance_percent,
                       created_at
                FROM domain_einkauf.invoice_verification
                WHERE tenant_id = :tid
                  AND match_status IN ('OFFEN', 'DIFFERENZ')
                ORDER BY created_at DESC
            """),
            {"tid": tenant_id},
        ).fetchall()
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Datenbankfehler: {exc}") from exc

    return [
        {
            "id": r[0], "po_id": r[1], "gr_id": r[2], "invoice_id": r[3],
            "match_status": r[4], "po_amount": r[5], "gr_amount": r[6],
            "invoice_amount": r[7], "variance_amount": r[8],
            "variance_percent": r[9], "tolerance_percent": r[10],
            "created_at": r[11].isoformat() if r[11] else None,
        }
        for r in rows
    ]


@router.patch("/{verification_id}/approve", summary="Verification genehmigen",
    response_model=PurchaseInvoiceVerificationOut
)
def approve_verification(
    verification_id: int,
    body: ApproveRequest,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    """Manuelle Freigabe trotz Differenz."""
    try:
        _ensure_schema(db)
        result = db.execute(
            text("""
                UPDATE domain_einkauf.invoice_verification
                SET match_status = 'GEMATCHT',
                    verified_at = NOW(),
                    verified_by = 'manual',
                    comment = :comment
                WHERE id = :id AND tenant_id = :tid
                RETURNING id, match_status, verified_at
            """),
            {"id": verification_id, "tid": tenant_id, "comment": body.comment},
        ).fetchone()
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=503, detail=f"Datenbankfehler: {exc}") from exc

    if not result:
        raise HTTPException(status_code=404, detail="Prüfvorgang nicht gefunden")

    # EINK-VERIF-AP-001: Belegbruch schliessen — AP-Rechnung freigeben + Kreditoren-OP anlegen
    inv_row = db.execute(
        text("""
            SELECT invoice_id, invoice_amount, supplier_id
            FROM domain_einkauf.invoice_verification
            WHERE id = :id AND tenant_id = :tid
        """),
        {"id": verification_id, "tid": tenant_id},
    ).fetchone()
    if inv_row and inv_row[0]:
        try:
            db.execute(text("""
                UPDATE domain_einkauf.ap_invoices
                SET status = 'freigegeben', updated_at = NOW()
                WHERE id = :inv_id AND tenant_id = :tid
                  AND status NOT IN ('freigegeben', 'bezahlt', 'storniert')
            """), {"inv_id": inv_row[0], "tid": tenant_id})
            db.commit()
        except Exception:  # noqa: BLE001 — AP-Invoice-Update nicht kritisch
            pass
        try:
            today = _date.today().isoformat()
            due = _date.today().replace(day=min(_date.today().day + 30, 28)).isoformat()
            db.execute(text("""
                INSERT INTO domain_erp.offene_posten
                    (id, tenant_id, konto_typ, rechnungsnr, rechnungsdatum, datum, faelligkeit,
                     betrag, offen, lieferant_id, op_status)
                VALUES (:id, :tid, 'kreditoren', :rnr, :rdat, :dat, :faell,
                        :betrag, :betrag, :sid, 'offen')
                ON CONFLICT DO NOTHING
            """), {
                "id": str(_uuid.uuid4()),
                "tid": tenant_id,
                "rnr": inv_row[0],
                "rdat": today, "dat": today, "faell": due,
                "betrag": float(inv_row[1] or 0),
                "sid": inv_row[2],
            })
            db.commit()
        except Exception:  # noqa: BLE001 — OP-Anlage nicht kritisch
            pass

    return {
        "id": result[0],
        "match_status": result[1],
        "verified_at": result[2].isoformat() if result[2] else None,
    }


@router.patch("/{verification_id}/block", summary="Verification blockieren",
    response_model=IDResponse
)
def block_verification(
    verification_id: int,
    body: BlockRequest,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    """Rechnungsprüfung zur Klärung blockieren."""
    try:
        _ensure_schema(db)
        result = db.execute(
            text("""
                UPDATE domain_einkauf.invoice_verification
                SET match_status = 'BLOCKIERT',
                    comment = :reason
                WHERE id = :id AND tenant_id = :tid
                RETURNING id, match_status
            """),
            {"id": verification_id, "tid": tenant_id, "reason": body.reason},
        ).fetchone()
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=503, detail=f"Datenbankfehler: {exc}") from exc

    if not result:
        raise HTTPException(status_code=404, detail="Prüfvorgang nicht gefunden")

    return {"id": result[0], "match_status": result[1]}


@router.get("/statistics", summary="Statistics abrufen",
    response_model=PurchaseInvoiceVerificationOut
)
def get_statistics(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    """Auswertung aller Rechnungsprüfvorgänge."""
    try:
        _ensure_schema(db)
        row = db.execute(
            text("""
                SELECT
                    COUNT(*)                                                          AS total,
                    COUNT(*) FILTER (WHERE match_status = 'GEMATCHT'
                                       AND verified_by IS NULL)                      AS matched_auto,
                    COUNT(*) FILTER (WHERE match_status = 'GEMATCHT'
                                       AND verified_by = 'manual')                   AS approved_manual,
                    COUNT(*) FILTER (WHERE match_status = 'BLOCKIERT')               AS blocked,
                    ROUND(AVG(variance_percent)::NUMERIC, 4)                         AS avg_variance_percent
                FROM domain_einkauf.invoice_verification
                WHERE tenant_id = :tid
            """),
            {"tid": tenant_id},
        ).fetchone()
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Datenbankfehler: {exc}") from exc

    return {
        "total": row[0] or 0,
        "matched_auto": row[1] or 0,
        "approved_manual": row[2] or 0,
        "blocked": row[3] or 0,
        "avg_variance_percent": float(row[4]) if row[4] else 0.0,
    }
