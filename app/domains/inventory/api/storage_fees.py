"""Consigned stock storage-fee monthly engine (DOCFLOW-P0-08)."""

from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional
from uuid import uuid4
import calendar
import json

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from ....core.database import engine, get_db
from .inventory_auth import get_current_tenant_id, require_inventory_access, require_inventory_admin
from app.auth.bereich_roles import SCHREIBEN  # Schreibrecht je Bereich (WRITE-ROLES)

router = APIRouter()


class StorageFeeRunRequest(BaseModel):
    period: str = Field(..., description="Billing period as YYYY-MM")
    dry_run: bool = Field(default=False, description="Preview only, no DB write")
    post_to_ledger: bool = Field(
        default=False,
        description=(
            "Entfallen: Lagergeld wird ueber die Ausgangsrechnung gebucht (Umsatzsteuer, offener Posten). "
            "true wird mit 422 abgewiesen."
        ),
    )
    posting_date: Optional[date] = None
    currency: str = Field(default="EUR", min_length=3, max_length=3)
    idempotency_key: Optional[str] = Field(default=None, max_length=120)
    created_by: Optional[str] = Field(default=None, max_length=100)
    note: Optional[str] = None


class StorageFeeChargeOut(BaseModel):
    owner_partner_id: str
    article_id: str
    warehouse_id: str
    charge: Optional[str] = None
    basis_quantity: float
    monthly_rate: float
    amount: float
    currency: str = "EUR"


class StorageFeeRunOut(BaseModel):
    run_id: Optional[str] = None
    tenant_id: str
    period: str
    dry_run: bool
    idempotent_hit: bool = False
    post_to_ledger: bool
    posting_date: str
    journal_entry_id: Optional[str] = None
    total_items: int
    total_amount: float
    charges: list[StorageFeeChargeOut]


def _period_bounds(period: str) -> tuple[date, date]:
    try:
        year, month = period.split("-")
        y = int(year)
        m = int(month)
        if m < 1 or m > 12:
            raise ValueError("month out of range")
        first = date(y, m, 1)
        last = date(y, m, calendar.monthrange(y, m)[1])
        return first, last
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid period '{period}', expected YYYY-MM") from exc


def _round_money(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _collect_charge_candidates(db: Session, tenant_id: str, period_end: date, currency: str) -> list[StorageFeeChargeOut]:
    rows = db.execute(
        text(
            """
            WITH stock AS (
                SELECT
                    m.owner_partner_id,
                    m.article_id,
                    m.warehouse_id,
                    COALESCE(m.charge, '') AS charge_key,
                    SUM(m.quantity) AS closing_qty
                FROM domain_inventory.inventory_stock_movements m
                WHERE m.tenant_id = :tenant_id
                  AND m.ownership_type = 'consigned'
                  AND m.owner_partner_id IS NOT NULL
                  AND m.movement_date <= :period_end
                GROUP BY m.owner_partner_id, m.article_id, m.warehouse_id, COALESCE(m.charge, '')
            ),
            rates AS (
                SELECT DISTINCT ON (
                    m.owner_partner_id, m.article_id, m.warehouse_id, COALESCE(m.charge, '')
                )
                    m.owner_partner_id,
                    m.article_id,
                    m.warehouse_id,
                    COALESCE(m.charge, '') AS charge_key,
                    COALESCE(m.storage_fee_monthly_rate, 0) AS monthly_rate
                FROM domain_inventory.inventory_stock_movements m
                WHERE m.tenant_id = :tenant_id
                  AND m.ownership_type = 'consigned'
                  AND m.storage_fee_relevant = TRUE
                  AND m.owner_partner_id IS NOT NULL
                  AND (m.storage_fee_start_date IS NULL OR m.storage_fee_start_date <= :period_end)
                  AND m.movement_date <= :period_end
                ORDER BY
                    m.owner_partner_id, m.article_id, m.warehouse_id, COALESCE(m.charge, ''),
                    m.movement_date DESC, m.created_at DESC
            )
            SELECT
                s.owner_partner_id,
                s.article_id,
                s.warehouse_id,
                NULLIF(s.charge_key, '') AS charge,
                s.closing_qty,
                r.monthly_rate
            FROM stock s
            JOIN rates r
              ON r.owner_partner_id = s.owner_partner_id
             AND r.article_id = s.article_id
             AND r.warehouse_id = s.warehouse_id
             AND r.charge_key = s.charge_key
            WHERE s.closing_qty > 0
              AND r.monthly_rate > 0
            ORDER BY s.owner_partner_id, s.article_id, s.warehouse_id, s.charge_key
            """
        ),
        {"tenant_id": tenant_id, "period_end": period_end},
    ).mappings().all()

    out: list[StorageFeeChargeOut] = []
    for row in rows:
        qty = Decimal(str(row["closing_qty"] or 0))
        rate = Decimal(str(row["monthly_rate"] or 0))
        amount = _round_money(qty * rate)
        out.append(
            StorageFeeChargeOut(
                owner_partner_id=str(row["owner_partner_id"]),
                article_id=str(row["article_id"]),
                warehouse_id=str(row["warehouse_id"]),
                charge=row.get("charge"),
                basis_quantity=float(qty),
                monthly_rate=float(rate),
                amount=float(amount),
                currency=currency,
            )
        )
    return out


def _write_audit_entry(
    *,
    run_id: str,
    tenant_id: str,
    period: str,
    total_items: int,
    total_amount: Decimal,
) -> None:
    try:
        with engine.begin() as conn:
            conn.execute(
                text(
                    """
                    INSERT INTO infrastructure.audit_log
                    (id, user_id, action, resource_type, resource_id, old_values, new_values, timestamp)
                    VALUES (CAST(:id AS uuid), NULL, :action, :resource_type, CAST(:resource_id AS uuid), NULL, CAST(:new_values AS jsonb), NOW())
                    """
                ),
                {
                    "id": str(uuid4()),
                    "action": "storage_fee_run_posted",
                    "resource_type": "consignment_storage_fee_run",
                    "resource_id": run_id,
                    "new_values": json.dumps(
                        {
                            "tenant_id": tenant_id,
                            "period": period,
                            "total_items": total_items,
                            "total_amount": float(total_amount),
                        }
                    ),
                },
            )
    except Exception:
        # audit table is optional in some environments
        pass


@router.post("/run", response_model=StorageFeeRunOut, dependencies=SCHREIBEN["LAGER"])
async def run_storage_fee_engine(
    payload: StorageFeeRunRequest,
    db: Session = Depends(get_db),
    _: str = Depends(require_inventory_admin),
    effective_tenant: str = Depends(get_current_tenant_id),
):
    """Run monthly storage-fee calculation for consigned stock.

    Der Lauf berechnet und protokolliert das Lagergeld je Eigentuemer. Gebucht wird es nicht hier: Die fruehere
    Direktbuchung (Forderung an Erloes) umging Umsatzsteuer und offenen Posten und legte fehlende Konten selbst an.
    Lagergeld ist eine Leistung an den Einlagerer und wird wie jede Leistung ueber die Ausgangsrechnung gebucht
    (belegfuehrende Domaene, Finance als Buchungsautoritaet).
    """
    if payload.post_to_ledger:
        raise HTTPException(
            status_code=422,
            detail=(
                "Lagergeld wird nicht direkt ins Journal gebucht, sondern ueber eine Ausgangsrechnung an den "
                "Einlagerer (Umsatzsteuer, offener Posten). post_to_ledger weglassen."
            ),
        )
    period_start, period_end = _period_bounds(payload.period)
    posting_date = payload.posting_date or period_end
    charges = _collect_charge_candidates(db, effective_tenant, period_end, payload.currency.upper())
    total_amount = _round_money(sum((Decimal(str(i.amount)) for i in charges), Decimal("0")))

    if payload.dry_run:
        return StorageFeeRunOut(
            run_id=None,
            tenant_id=effective_tenant,
            period=payload.period,
            dry_run=True,
            idempotent_hit=False,
            post_to_ledger=False,
            posting_date=posting_date.isoformat(),
            journal_entry_id=None,
            total_items=len(charges),
            total_amount=float(total_amount),
            charges=charges,
        )

    existing = db.execute(
        text(
            """
            SELECT id, journal_entry_id, total_items, total_amount
            FROM domain_inventory.consignment_storage_fee_runs
            WHERE tenant_id = :tenant_id
              AND period_month = :period_month
              AND run_type = 'post'
              AND status = 'posted'
            ORDER BY started_at DESC
            LIMIT 1
            """
        ),
        {"tenant_id": effective_tenant, "period_month": period_start},
    ).mappings().first()

    if existing:
        existing_charges = db.execute(
            text(
                """
                SELECT owner_partner_id, article_id, warehouse_id, charge, basis_quantity, monthly_rate, amount, currency
                FROM domain_inventory.consignment_storage_fee_charges
                WHERE run_id = :run_id
                ORDER BY owner_partner_id, article_id, warehouse_id, charge
                """
            ),
            {"run_id": str(existing["id"])},
        ).mappings().all()
        return StorageFeeRunOut(
            run_id=str(existing["id"]),
            tenant_id=effective_tenant,
            period=payload.period,
            dry_run=False,
            idempotent_hit=True,
            post_to_ledger=bool(existing.get("journal_entry_id")),
            posting_date=posting_date.isoformat(),
            journal_entry_id=existing.get("journal_entry_id"),
            total_items=int(existing.get("total_items") or 0),
            total_amount=float(existing.get("total_amount") or 0),
            charges=[
                StorageFeeChargeOut(
                    owner_partner_id=str(r["owner_partner_id"]),
                    article_id=str(r["article_id"]),
                    warehouse_id=str(r["warehouse_id"]),
                    charge=r.get("charge"),
                    basis_quantity=float(r["basis_quantity"] or 0),
                    monthly_rate=float(r["monthly_rate"] or 0),
                    amount=float(r["amount"] or 0),
                    currency=str(r.get("currency") or "EUR"),
                )
                for r in existing_charges
            ],
        )

    run_id = str(uuid4())
    now = datetime.now(timezone.utc)
    journal_entry_id = None
    try:
        db.execute(
                text(
                    """
                    INSERT INTO domain_inventory.consignment_storage_fee_runs
                    (id, tenant_id, period_month, run_type, status, idempotency_key, posting_date, currency, total_items, total_amount, created_by, note, started_at)
                    VALUES (:id, :tenant_id, :period_month, 'post', 'running', :idempotency_key, :posting_date, :currency, 0, 0, :created_by, :note, :started_at)
                    """
                ),
                {
                    "id": run_id,
                    "tenant_id": effective_tenant,
                    "period_month": period_start,
                    "idempotency_key": payload.idempotency_key,
                    "posting_date": posting_date,
                    "currency": payload.currency.upper(),
                    "created_by": payload.created_by,
                    "note": payload.note,
                    "started_at": now,
                },
            )

        for item in charges:
            db.execute(
                    text(
                        """
                        INSERT INTO domain_inventory.consignment_storage_fee_charges
                        (id, run_id, tenant_id, owner_partner_id, article_id, warehouse_id, charge, basis_quantity, monthly_rate, amount, currency, calculation_details)
                        VALUES (:id, :run_id, :tenant_id, :owner_partner_id, :article_id, :warehouse_id, :charge, :basis_quantity, :monthly_rate, :amount, :currency, CAST(:calculation_details AS jsonb))
                        """
                    ),
                    {
                        "id": str(uuid4()),
                        "run_id": run_id,
                        "tenant_id": effective_tenant,
                        "owner_partner_id": item.owner_partner_id,
                        "article_id": item.article_id,
                        "warehouse_id": item.warehouse_id,
                        "charge": item.charge,
                        "basis_quantity": Decimal(str(item.basis_quantity)),
                        "monthly_rate": Decimal(str(item.monthly_rate)),
                        "amount": Decimal(str(item.amount)),
                        "currency": item.currency,
                        "calculation_details": json.dumps(
                            {
                                "period": payload.period,
                                "algorithm": "closing_stock_qty * monthly_rate",
                            }
                        ),
                    },
                )

        db.execute(
                text(
                    """
                    UPDATE domain_inventory.consignment_storage_fee_runs
                    SET status = 'posted',
                        total_items = :total_items,
                        total_amount = :total_amount,
                        journal_entry_id = :journal_entry_id,
                        finished_at = NOW()
                    WHERE id = :run_id
                    """
                ),
                {
                    "run_id": run_id,
                    "total_items": len(charges),
                    "total_amount": total_amount,
                    "journal_entry_id": journal_entry_id,
                },
            )

        db.execute(
                text(
                    """
                    UPDATE domain_inventory.inventory_stock_movements m
                    SET storage_fee_last_charged_until = :period_end
                    WHERE m.tenant_id = :tenant_id
                      AND m.ownership_type = 'consigned'
                      AND m.storage_fee_relevant = TRUE
                      AND m.owner_partner_id IN (
                          SELECT DISTINCT c.owner_partner_id
                          FROM domain_inventory.consignment_storage_fee_charges c
                          WHERE c.run_id = :run_id
                      )
                      AND (m.storage_fee_last_charged_until IS NULL OR m.storage_fee_last_charged_until < :period_end)
                      AND m.movement_date <= :period_end
                    """
                ),
                {"tenant_id": effective_tenant, "period_end": period_end, "run_id": run_id},
            )

        # ensure committed before verification read
        db.commit()
        _write_audit_entry(
            run_id=run_id,
            tenant_id=effective_tenant,
            period=payload.period,
            total_items=len(charges),
            total_amount=total_amount,
        )
        return StorageFeeRunOut(
            run_id=run_id,
            tenant_id=effective_tenant,
            period=payload.period,
            dry_run=False,
            idempotent_hit=False,
            post_to_ledger=payload.post_to_ledger,
            posting_date=posting_date.isoformat(),
            journal_entry_id=journal_entry_id,
            total_items=len(charges),
            total_amount=float(total_amount),
            charges=charges,
        )
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to run storage fee engine: {exc}") from exc


@router.get("/runs")
async def list_storage_fee_runs(
    limit: int = Query(20, ge=1, le=200),
    db: Session = Depends(get_db),
    _: str = Depends(require_inventory_access),
    effective_tenant: str = Depends(get_current_tenant_id),
):
    rows = db.execute(
        text(
            """
            SELECT id, period_month, run_type, status, posting_date, total_items, total_amount, journal_entry_id, started_at, finished_at
            FROM domain_inventory.consignment_storage_fee_runs
            WHERE tenant_id = :tenant_id
            ORDER BY period_month DESC, started_at DESC
            LIMIT :limit
            """
        ),
        {"tenant_id": effective_tenant, "limit": limit},
    ).mappings().all()
    return {
        "items": [
            {
                "id": str(r["id"]),
                "period_month": r["period_month"].isoformat() if r.get("period_month") else None,
                "run_type": r.get("run_type"),
                "status": r.get("status"),
                "posting_date": r["posting_date"].isoformat() if r.get("posting_date") else None,
                "total_items": int(r.get("total_items") or 0),
                "total_amount": float(r.get("total_amount") or 0),
                "journal_entry_id": r.get("journal_entry_id"),
                "started_at": r["started_at"].isoformat() if r.get("started_at") else None,
                "finished_at": r["finished_at"].isoformat() if r.get("finished_at") else None,
            }
            for r in rows
        ]
    }


@router.get("/runs/{run_id}")
async def get_storage_fee_run(
    run_id: str,
    db: Session = Depends(get_db),
    _: str = Depends(require_inventory_access),
    effective_tenant: str = Depends(get_current_tenant_id),
):
    run = db.execute(
        text(
            """
            SELECT id, tenant_id, period_month, run_type, status, posting_date, total_items, total_amount, journal_entry_id, started_at, finished_at, created_by, note
            FROM domain_inventory.consignment_storage_fee_runs
            WHERE id = :run_id AND tenant_id = :tenant_id
            """
        ),
        {"run_id": run_id, "tenant_id": effective_tenant},
    ).mappings().first()
    if not run:
        raise HTTPException(status_code=404, detail="Storage fee run not found")

    charges = db.execute(
        text(
            """
            SELECT owner_partner_id, article_id, warehouse_id, charge, basis_quantity, monthly_rate, amount, currency
            FROM domain_inventory.consignment_storage_fee_charges
            WHERE run_id = :run_id
            ORDER BY owner_partner_id, article_id, warehouse_id, charge
            """
        ),
        {"run_id": run_id},
    ).mappings().all()

    return {
        "run": {
            "id": str(run["id"]),
            "tenant_id": str(run["tenant_id"]),
            "period_month": run["period_month"].isoformat() if run.get("period_month") else None,
            "run_type": run.get("run_type"),
            "status": run.get("status"),
            "posting_date": run["posting_date"].isoformat() if run.get("posting_date") else None,
            "total_items": int(run.get("total_items") or 0),
            "total_amount": float(run.get("total_amount") or 0),
            "journal_entry_id": run.get("journal_entry_id"),
            "started_at": run["started_at"].isoformat() if run.get("started_at") else None,
            "finished_at": run["finished_at"].isoformat() if run.get("finished_at") else None,
            "created_by": run.get("created_by"),
            "note": run.get("note"),
        },
        "charges": [
            {
                "owner_partner_id": str(r["owner_partner_id"]),
                "article_id": str(r["article_id"]),
                "warehouse_id": str(r["warehouse_id"]),
                "charge": r.get("charge"),
                "basis_quantity": float(r.get("basis_quantity") or 0),
                "monthly_rate": float(r.get("monthly_rate") or 0),
                "amount": float(r.get("amount") or 0),
                "currency": str(r.get("currency") or "EUR"),
            }
            for r in charges
        ],
    }


class LagergeldRechnungIn(BaseModel):
    steuerschluessel: str = Field(..., min_length=1, max_length=2,
                                  description="Verkaufs-Steuerschluessel des Mandanten (keine Vorgabe)")
    artikel_nr: str = Field(default="LAGERGELD", min_length=1, max_length=80)


class LagergeldRechnungOut(BaseModel):
    partner_id: str
    beleg_id: str
    positionen: int
    betrag_netto: float


@router.post("/runs/{run_id}/rechnungen", response_model=list[LagergeldRechnungOut], status_code=201,
             dependencies=SCHREIBEN["LAGER"])
async def lagergeld_rechnungen(
    run_id: str,
    payload: LagergeldRechnungIn,
    request: Request,
    db: Session = Depends(get_db),
    _: str = Depends(require_inventory_admin),
    effective_tenant: str = Depends(get_current_tenant_id),
):
    """Je Einlagerer ein Rechnungsentwurf (DocFlow ``sales_invoice``) aus einem abgeschlossenen Lagergeld-Lauf.

    Freigabe und Buchung (Umsatzsteuer, offener Posten) laufen danach ueber die Belegmaske. Wiederholbar: derselbe
    Lauf legt fuer denselben Einlagerer keinen zweiten Entwurf an.
    """
    from app.core.akteur import gepruefter_akteur_aus_request
    from app.services.lagergeld_rechnung import rechnungen_zum_lauf

    try:
        return rechnungen_zum_lauf(db, effective_tenant, run_id, steuerschluessel=payload.steuerschluessel,
                                   artikel_nr=payload.artikel_nr, akteur=gepruefter_akteur_aus_request(request))
    except Exception:
        db.rollback()
        raise
