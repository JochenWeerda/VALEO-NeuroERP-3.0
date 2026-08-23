"""
Anlagenbuchhaltung (Asset Accounting) — thin-router pattern with sqlalchemy.text()
Tabellen: domain_finance.fixed_assets, domain_finance.asset_depreciation_runs
"""
from __future__ import annotations

import logging
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from ....core.database import get_db
from ....core.tenant import get_tenant_id

logger = logging.getLogger(__name__)

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict as _ConfigDict


class AssetAccountingOut(BaseSchema):
    model_config = _ConfigDict(extra="allow")


router = APIRouter(prefix="/finance/asset-accounting", tags=["finance", "asset-accounting"])

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

_TABLE_ASSETS = "domain_finance.fixed_assets"
_TABLE_RUNS = "domain_finance.asset_depreciation_runs"

VALID_CLASSES = {"GEBAEUDE", "FAHRZEUG", "MASCHINE", "IT", "BUERO"}
VALID_METHODS = {"LINEAR", "DEGRESSIV"}


def _503(hint: str = "alembic upgrade head") -> HTTPException:
    return HTTPException(
        status_code=503,
        detail={"error": "Tabelle nicht vorhanden", "migration_hint": hint},
    )


def _check_tables(db: Session) -> None:
    """Raise 503 if required tables are missing."""
    try:
        db.execute(text("SELECT 1 FROM domain_finance.fixed_assets LIMIT 0"))
        db.execute(text("SELECT 1 FROM domain_finance.asset_depreciation_runs LIMIT 0"))
    except Exception:
        raise _503()


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------

class AssetCreate(BaseModel):
    asset_number: str
    description: str
    asset_class: str = Field(..., description="GEBAEUDE/FAHRZEUG/MASCHINE/IT/BUERO")
    acquisition_date: date
    acquisition_cost: Decimal
    useful_life_years: int = Field(..., gt=0)
    residual_value: Decimal = Decimal("0")
    depreciation_method: str = Field("LINEAR", description="LINEAR/DEGRESSIV")


class AssetUpdate(BaseModel):
    description: Optional[str] = None
    asset_class: Optional[str] = None
    residual_value: Optional[Decimal] = None
    useful_life_years: Optional[int] = None
    depreciation_method: Optional[str] = None


class AssetDispose(BaseModel):
    disposal_date: date
    disposal_proceeds: Decimal = Decimal("0")
    disposal_reason: str = ""


class DepreciationRunRequest(BaseModel):
    year: int
    month: int = Field(..., ge=1, le=12)
    dry_run: bool = False


class BudgetLineIn(BaseModel):
    pass  # reused name; not used here


# ---------------------------------------------------------------------------
# GET /assets
# ---------------------------------------------------------------------------

@router.get("/assets", tags=["finance", "asset-accounting"], summary="Assets auflisten",
    response_model=AssetAccountingOut
)
def list_assets(
    asset_class: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    _check_tables(db)
    try:
        conditions = ["tenant_id = :tid"]
        params: dict = {"tid": tenant_id}
        if asset_class:
            conditions.append("asset_class = :ac")
            params["ac"] = asset_class.upper()
        if is_active is not None:
            conditions.append("is_active = :ia")
            params["ia"] = is_active
        where = " AND ".join(conditions)
        rows = db.execute(
            text(f"SELECT * FROM {_TABLE_ASSETS} WHERE {where} ORDER BY asset_number"),  # nosec B608  # reviewed-safe: column names code-controlled, values parameterized
            params,
        ).mappings().all()
        return {"items": [dict(r) for r in rows], "total": len(rows)}
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("list_assets: %s", exc)
        raise _503()


# ---------------------------------------------------------------------------
# POST /assets
# ---------------------------------------------------------------------------

@router.post("/assets", status_code=201, tags=["finance", "asset-accounting"], summary="Asset anlegen",
    response_model=AssetAccountingOut
)
def create_asset(
    body: AssetCreate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    _check_tables(db)
    if body.asset_class.upper() not in VALID_CLASSES:
        raise HTTPException(422, f"asset_class muss einer von {VALID_CLASSES} sein")
    if body.depreciation_method.upper() not in VALID_METHODS:
        raise HTTPException(422, f"depreciation_method muss LINEAR oder DEGRESSIV sein")
    try:
        from app.core.uuid7 import uuid7
        aid = str(uuid7())
        db.execute(
            text(
                f"""INSERT INTO {_TABLE_ASSETS}
                (id, asset_number, description, asset_class, acquisition_date,
                 acquisition_cost, useful_life_years, residual_value,
                 current_book_value, depreciation_method, tenant_id, is_active)
                VALUES (:id, :an, :desc, :ac, :adt, :cost, :life, :resid,
                        :bv, :dm, :tid, true)"""
            ),
            {
                "id": aid,
                "an": body.asset_number,
                "desc": body.description,
                "ac": body.asset_class.upper(),
                "adt": body.acquisition_date,
                "cost": float(body.acquisition_cost),
                "life": body.useful_life_years,
                "resid": float(body.residual_value),
                "bv": float(body.acquisition_cost),
                "dm": body.depreciation_method.upper(),
                "tid": tenant_id,
            },
        )
        db.commit()
        return {"id": aid, "asset_number": body.asset_number}
    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        logger.error("create_asset: %s", exc)
        raise _503()


# ---------------------------------------------------------------------------
# GET /assets/{id}
# ---------------------------------------------------------------------------

@router.get("/assets/{asset_id}", tags=["finance", "asset-accounting"], summary="Asset abrufen",
    response_model=AssetAccountingOut
)
def get_asset(
    asset_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    _check_tables(db)
    try:
        row = db.execute(
            text("SELECT * FROM domain_finance.fixed_assets WHERE id = :id AND tenant_id = :tid"),
            {"id": asset_id, "tid": tenant_id},
        ).mappings().first()
        if not row:
            raise HTTPException(404, "Anlage nicht gefunden")
        history = db.execute(
            text(
                f"""SELECT * FROM {_TABLE_RUNS}
                WHERE asset_id = :aid AND tenant_id = :tid
                ORDER BY period_year, period_month"""
            ),
            {"aid": asset_id, "tid": tenant_id},
        ).mappings().all()
        return {"asset": dict(row), "depreciation_history": [dict(h) for h in history]}
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("get_asset: %s", exc)
        raise _503()


# ---------------------------------------------------------------------------
# PATCH /assets/{id}
# ---------------------------------------------------------------------------

@router.patch("/assets/{asset_id}", tags=["finance", "asset-accounting"], summary="Asset aktualisieren",
    response_model=AssetAccountingOut
)
def update_asset(
    asset_id: str,
    body: AssetUpdate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    _check_tables(db)
    try:
        # Check that no depreciation run has been executed for this asset
        run_count = db.execute(
            text(
                f"SELECT COUNT(*) FROM {_TABLE_RUNS} WHERE asset_id = :aid AND tenant_id = :tid"
            ),
            {"aid": asset_id, "tid": tenant_id},
        ).scalar()
        if run_count and run_count > 0:
            raise HTTPException(409, "Anlage hat bereits AfA-Läufe; Änderung nicht erlaubt")

        asset_row = db.execute(
            text("SELECT id FROM domain_finance.fixed_assets WHERE id = :id AND tenant_id = :tid"),
            {"id": asset_id, "tid": tenant_id},
        ).first()
        if not asset_row:
            raise HTTPException(404, "Anlage nicht gefunden")

        fields = body.model_dump(exclude_none=True)
        if not fields:
            raise HTTPException(422, "Keine Felder zum Aktualisieren angegeben")

        set_parts = [f"{k} = :{k}" for k in fields]
        params = {**fields, "id": asset_id, "tid": tenant_id}
        db.execute(
            text(
                f"UPDATE {_TABLE_ASSETS} SET {', '.join(set_parts)} WHERE id = :id AND tenant_id = :tid"
            ),
            params,
        )
        db.commit()
        return {"updated": True, "id": asset_id}
    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        logger.error("update_asset: %s", exc)
        raise _503()


# ---------------------------------------------------------------------------
# POST /assets/{id}/dispose
# ---------------------------------------------------------------------------

@router.post("/assets/{asset_id}/dispose", tags=["finance", "asset-accounting"], summary="Asset dispose",
    response_model=AssetAccountingOut
)
def dispose_asset(
    asset_id: str,
    body: AssetDispose,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    _check_tables(db)
    try:
        row = db.execute(
            text(
                f"SELECT current_book_value FROM {_TABLE_ASSETS} WHERE id = :id AND tenant_id = :tid AND is_active = true"
            ),
            {"id": asset_id, "tid": tenant_id},
        ).first()
        if not row:
            raise HTTPException(404, "Aktive Anlage nicht gefunden")

        book_value = float(row[0])
        gain_loss = float(body.disposal_proceeds) - book_value

        db.execute(
            text(
                f"""UPDATE {_TABLE_ASSETS}
                SET is_active = false,
                    current_book_value = 0
                WHERE id = :id AND tenant_id = :tid"""
            ),
            {"id": asset_id, "tid": tenant_id},
        )
        db.commit()

        # ASSET-DISPOSE-JE-001: GL-Buchung für Anlagen-Abgang (Belegbruch schliessen)
        try:
            from app.services.finance_transaction_service import FinanceTransactionService
            fin = FinanceTransactionService(db, tenant_id)
            lines = [
                {"account_id": "0800", "debit_amount": float(body.disposal_proceeds), "credit_amount": 0.0,
                 "description": "Veräußerungserlös Anlage"},
                {"account_id": "0200", "debit_amount": 0.0, "credit_amount": book_value,
                 "description": f"Abgang Anlage Buchwert {asset_id[:8]}"},
            ]
            if gain_loss > 0:
                lines.append({"account_id": "2650", "debit_amount": 0.0, "credit_amount": gain_loss,
                               "description": "Gewinn Anlagenabgang"})
            elif gain_loss < 0:
                lines.append({"account_id": "6800", "debit_amount": abs(gain_loss), "credit_amount": 0.0,
                               "description": "Verlust Anlagenabgang"})
            fin.create(
                entry_number=f"ABGANG-{asset_id[:8].upper()}-{body.disposal_date.strftime('%Y%m%d')}",
                description=f"Anlagenabgang {body.disposal_reason or asset_id}",
                entry_date=body.disposal_date,
                lines=lines,
                reference=asset_id,
                source="asset_disposal",
                document_type="asset_disposal",
                period=body.disposal_date.strftime("%Y-%m"),
            )
        except Exception as exc:  # noqa: BLE001 — GL-Buchung nicht kritisch für Abgang
            logger.warning("Asset disposal GL booking failed (non-blocking): %s", exc)

        return {
            "asset_id": asset_id,
            "disposal_date": body.disposal_date.isoformat(),
            "disposal_proceeds_eur": float(body.disposal_proceeds),
            "book_value_at_disposal_eur": book_value,
            "gain_loss_eur": gain_loss,
            "disposal_reason": body.disposal_reason,
        }
    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        logger.error("dispose_asset: %s", exc)
        raise _503()


# ---------------------------------------------------------------------------
# POST /depreciation-run
# ---------------------------------------------------------------------------

@router.post("/depreciation-run", tags=["finance", "asset-accounting"], summary="Depreciation ausführen",
    response_model=AssetAccountingOut
)
def run_depreciation(
    body: DepreciationRunRequest,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    _check_tables(db)
    try:
        assets = db.execute(
            text(
                f"""SELECT id, acquisition_cost, useful_life_years, residual_value,
                           current_book_value, depreciation_method
                FROM {_TABLE_ASSETS}
                WHERE tenant_id = :tid AND is_active = true"""
            ),
            {"tid": tenant_id},
        ).mappings().all()

        results = []
        for a in assets:
            # Skip if already run for this period
            existing = db.execute(
                text(
                    f"""SELECT 1 FROM {_TABLE_RUNS}
                    WHERE asset_id = :aid AND period_year = :yr AND period_month = :mo AND tenant_id = :tid"""
                ),
                {"aid": a["id"], "yr": body.year, "mo": body.month, "tid": tenant_id},
            ).first()
            if existing:
                results.append({"asset_id": a["id"], "status": "skipped", "reason": "Bereits gebucht"})
                continue

            cost = float(a["acquisition_cost"])
            resid = float(a["residual_value"])
            life = int(a["useful_life_years"])
            bv = float(a["current_book_value"])

            # Linear: (cost - residual) / life / 12
            monthly_dep = round((cost - resid) / life / 12, 2)
            # Do not depreciate below residual value
            actual_dep = min(monthly_dep, max(0.0, bv - resid))
            new_bv = round(bv - actual_dep, 2)

            if not body.dry_run:
                from app.core.uuid7 import uuid7
                run_id = str(uuid7())
                db.execute(
                    text(
                        f"""INSERT INTO {_TABLE_RUNS}
                        (id, asset_id, period_year, period_month, depreciation_amount, book_value_after, tenant_id)
                        VALUES (:id, :aid, :yr, :mo, :dep, :bv, :tid)"""
                    ),
                    {
                        "id": run_id,
                        "aid": a["id"],
                        "yr": body.year,
                        "mo": body.month,
                        "dep": actual_dep,
                        "bv": new_bv,
                        "tid": tenant_id,
                    },
                )
                db.execute(
                    text(
                        f"UPDATE {_TABLE_ASSETS} SET current_book_value = :bv WHERE id = :id AND tenant_id = :tid"
                    ),
                    {"bv": new_bv, "id": a["id"], "tid": tenant_id},
                )

            results.append(
                {
                    "asset_id": a["id"],
                    "depreciation_amount_eur": actual_dep,
                    "book_value_after_eur": new_bv,
                    "status": "dry_run" if body.dry_run else "booked",
                }
            )

        if not body.dry_run:
            db.commit()

        return {
            "year": body.year,
            "month": body.month,
            "dry_run": body.dry_run,
            "processed": len(results),
            "items": results,
        }
    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        logger.error("run_depreciation: %s", exc)
        raise _503()


# ---------------------------------------------------------------------------
# GET /asset-register  (Anlagespiegel)
# ---------------------------------------------------------------------------

@router.get("/asset-register", tags=["finance", "asset-accounting"], summary="Register asset",
    response_model=AssetAccountingOut
)
def asset_register(
    year: int = Query(..., description="Geschäftsjahr"),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    _check_tables(db)
    try:
        assets = db.execute(
            text(
                f"""SELECT asset_class,
                       SUM(acquisition_cost) AS total_acquisition_cost,
                       SUM(current_book_value) AS total_book_value,
                       COUNT(*) AS asset_count
                FROM {_TABLE_ASSETS}
                WHERE tenant_id = :tid
                GROUP BY asset_class"""
            ),
            {"tid": tenant_id},
        ).mappings().all()

        afa_by_class = db.execute(
            text(
                f"""SELECT a.asset_class,
                       SUM(r.depreciation_amount) AS total_depreciation
                FROM {_TABLE_RUNS} r
                JOIN {_TABLE_ASSETS} a ON a.id = r.asset_id
                WHERE r.tenant_id = :tid AND r.period_year = :yr
                GROUP BY a.asset_class"""
            ),
            {"tid": tenant_id, "yr": year},
        ).mappings().all()

        dep_map = {row["asset_class"]: float(row["total_depreciation"]) for row in afa_by_class}

        register = []
        for row in assets:
            cls = row["asset_class"]
            acq = float(row["total_acquisition_cost"])
            bv = float(row["total_book_value"])
            dep = dep_map.get(cls, 0.0)
            register.append(
                {
                    "asset_class": cls,
                    "asset_count": row["asset_count"],
                    "acquisition_cost_eur": acq,
                    "accumulated_depreciation_eur": round(acq - bv, 2),
                    "depreciation_current_year_eur": dep,
                    "book_value_end_eur": bv,
                }
            )

        return {"year": year, "register": register}
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("asset_register: %s", exc)
        raise _503()


# ---------------------------------------------------------------------------
# GET /depreciation-forecast  (5-Jahres-Vorschau)
# ---------------------------------------------------------------------------

@router.get("/depreciation-forecast", tags=["finance", "asset-accounting"], summary="Forecast depreciation",
    response_model=AssetAccountingOut
)
def depreciation_forecast(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    _check_tables(db)
    try:
        assets = db.execute(
            text(
                f"""SELECT id, asset_number, description,
                       acquisition_cost, useful_life_years, residual_value,
                       current_book_value, acquisition_date
                FROM {_TABLE_ASSETS}
                WHERE tenant_id = :tid AND is_active = true"""
            ),
            {"tid": tenant_id},
        ).mappings().all()

        base_year = datetime.now(tz=timezone.utc).year
        forecast = []
        for a in assets:
            cost = float(a["acquisition_cost"])
            resid = float(a["residual_value"])
            life = int(a["useful_life_years"])
            bv = float(a["current_book_value"])
            annual_dep = round((cost - resid) / life, 2)
            years = []
            running_bv = bv
            for offset in range(5):
                yr = base_year + offset
                dep = min(annual_dep, max(0.0, running_bv - resid))
                running_bv = round(running_bv - dep, 2)
                years.append({"year": yr, "depreciation_eur": dep, "book_value_end_eur": running_bv})
            forecast.append(
                {
                    "asset_id": a["id"],
                    "asset_number": a["asset_number"],
                    "description": a["description"],
                    "current_book_value_eur": bv,
                    "annual_depreciation_eur": annual_dep,
                    "forecast": years,
                }
            )

        return {"base_year": base_year, "assets": forecast}
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("depreciation_forecast: %s", exc)
        raise _503()
