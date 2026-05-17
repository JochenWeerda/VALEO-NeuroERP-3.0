"""Zentrale Kontrakte-Engine — thin-router, sqlalchemy.text()."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from ....core.database import get_db
from ....core.tenant import get_tenant_id

router = APIRouter()

# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------

ContractTypeValues = {"EINKAUF", "VERKAUF", "AGRAR", "DIENSTLEISTUNG", "MIETE", "PACHT"}
ContractStatusValues = {"ENTWURF", "AKTIV", "ABGELAUFEN", "GEKUENDIGT"}
CounterpartyTypeValues = {"CUSTOMER", "SUPPLIER"}
ObligationTypeValues = {"LIEFERUNG", "ZAHLUNG", "LEISTUNG", "MELDUNG"}
ObligationStatusValues = {"OFFEN", "ERLEDIGT", "UEBERFAELLIG"}


class ContractCreate(BaseModel):
    contract_number: Optional[str] = None
    contract_type: str
    title: str = Field(..., min_length=1)
    counterparty_id: str = Field(..., min_length=1)
    counterparty_type: str = "CUSTOMER"
    status: str = "ENTWURF"
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    auto_renewal_days: Optional[int] = None
    notice_period_days: Optional[int] = None
    total_value_eur: Optional[float] = None


class ContractUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    auto_renewal_days: Optional[int] = None
    notice_period_days: Optional[int] = None
    total_value_eur: Optional[float] = None
    change_summary: Optional[str] = None
    changed_by: Optional[str] = None


class ContractOut(BaseModel):
    id: str
    contract_number: str
    contract_type: str
    title: str
    counterparty_id: str
    counterparty_type: str
    status: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    auto_renewal_days: Optional[int] = None
    notice_period_days: Optional[int] = None
    total_value_eur: Optional[float] = None
    tenant_id: str
    created_at: Optional[datetime] = None


class ObligationCreate(BaseModel):
    obligation_type: str
    due_date: datetime
    description: str = Field(..., min_length=1)


class ObligationUpdate(BaseModel):
    status: str


class ObligationOut(BaseModel):
    id: str
    contract_id: str
    obligation_type: str
    due_date: datetime
    description: str
    status: str
    tenant_id: str


class RenewBody(BaseModel):
    new_end_date: datetime


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_contract(db: Session, contract_id: str, tenant_id: str) -> dict:
    row = db.execute(
        text(
            "SELECT * FROM domain_contracts.contracts WHERE id = :id AND tenant_id = :tid"
        ),
        {"id": contract_id, "tid": tenant_id},
    ).mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Kontrakt nicht gefunden")
    return dict(row)


def _row_to_contract(row: dict) -> ContractOut:
    return ContractOut(
        id=str(row["id"]),
        contract_number=str(row["contract_number"]),
        contract_type=str(row["contract_type"]),
        title=str(row["title"]),
        counterparty_id=str(row["counterparty_id"]),
        counterparty_type=str(row["counterparty_type"]),
        status=str(row["status"]),
        start_date=row.get("start_date"),
        end_date=row.get("end_date"),
        auto_renewal_days=row.get("auto_renewal_days"),
        notice_period_days=row.get("notice_period_days"),
        total_value_eur=float(row["total_value_eur"]) if row.get("total_value_eur") is not None else None,
        tenant_id=str(row["tenant_id"]),
        created_at=row.get("created_at"),
    )


def _create_version(
    db: Session,
    contract_id: str,
    tenant_id: str,
    version_number: int,
    changed_by: Optional[str],
    change_summary: Optional[str],
    snapshot: dict,
):
    db.execute(
        text(
            """
            INSERT INTO domain_contracts.contract_versions
              (id, contract_id, version_number, changed_at, changed_by, change_summary, content_snapshot, tenant_id)
            VALUES
              (:id, :cid, :ver, :now, :by, :summary, :snap::jsonb, :tid)
            """
        ),
        {
            "id": str(uuid4()),
            "cid": contract_id,
            "ver": version_number,
            "now": datetime.now(timezone.utc),
            "by": changed_by or "system",
            "summary": change_summary or "",
            "snap": json.dumps(snapshot),
            "tid": tenant_id,
        },
    )


def _next_version_number(db: Session, contract_id: str, tenant_id: str) -> int:
    val = db.execute(
        text(
            "SELECT COALESCE(MAX(version_number), 0) + 1 FROM domain_contracts.contract_versions "
            "WHERE contract_id = :cid AND tenant_id = :tid"
        ),
        {"cid": contract_id, "tid": tenant_id},
    ).scalar()
    return int(val or 1)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/contracts", response_model=list[ContractOut])
async def list_contracts(
    contract_type: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    counterparty_id: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=200),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    where = ["tenant_id = :tenant_id"]
    params: dict = {"tenant_id": tenant_id, "skip": skip, "limit": limit}
    if contract_type:
        where.append("contract_type = :contract_type")
        params["contract_type"] = contract_type
    if status_filter:
        where.append("status = :status")
        params["status"] = status_filter
    if counterparty_id:
        where.append("counterparty_id = :counterparty_id")
        params["counterparty_id"] = counterparty_id
    where_sql = " AND ".join(where)
    try:
        rows = db.execute(
            text(
                f"SELECT * FROM domain_contracts.contracts WHERE {where_sql} "
                "ORDER BY created_at DESC OFFSET :skip LIMIT :limit"
            ),
            params,
        ).mappings().all()
    except Exception:
        raise HTTPException(status_code=503, detail="Datenbankfehler")
    return [_row_to_contract(dict(r)) for r in rows]


@router.post("/contracts", response_model=ContractOut, status_code=status.HTTP_201_CREATED)
async def create_contract(
    payload: ContractCreate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    now = datetime.now(timezone.utc)
    cid = str(uuid4())
    contract_number = payload.contract_number or f"KT-{uuid4().hex[:8].upper()}"
    try:
        db.execute(
            text(
                """
                INSERT INTO domain_contracts.contracts
                  (id, tenant_id, contract_number, contract_type, title, counterparty_id,
                   counterparty_type, status, start_date, end_date, auto_renewal_days,
                   notice_period_days, total_value_eur, created_at)
                VALUES
                  (:id, :tid, :cn, :ct, :title, :cpid, :cpt, :status,
                   :start_date, :end_date, :ard, :npd, :tv, :now)
                """
            ),
            {
                "id": cid, "tid": tenant_id, "cn": contract_number,
                "ct": payload.contract_type, "title": payload.title,
                "cpid": payload.counterparty_id, "cpt": payload.counterparty_type,
                "status": payload.status, "start_date": payload.start_date,
                "end_date": payload.end_date, "ard": payload.auto_renewal_days,
                "npd": payload.notice_period_days, "tv": payload.total_value_eur,
                "now": now,
            },
        )
        _create_version(db, cid, tenant_id, 1, "system", "Erstanlage", {"status": payload.status, "title": payload.title})
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=503, detail="Datenbankfehler")
    return _row_to_contract(_get_contract(db, cid, tenant_id))


@router.get("/contracts/expiring", response_model=list[ContractOut])
async def expiring_contracts(
    days_ahead: int = Query(90, ge=1, le=365),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    try:
        rows = db.execute(
            text(
                """
                SELECT * FROM domain_contracts.contracts
                WHERE tenant_id = :tid
                  AND status = 'AKTIV'
                  AND end_date IS NOT NULL
                  AND end_date <= (NOW() + (:days || ' days')::interval)
                  AND end_date >= NOW()
                ORDER BY end_date ASC
                """
            ),
            {"tid": tenant_id, "days": days_ahead},
        ).mappings().all()
    except Exception:
        raise HTTPException(status_code=503, detail="Datenbankfehler")
    return [_row_to_contract(dict(r)) for r in rows]


@router.get("/contracts/{contract_id}", response_model=dict)
async def get_contract(
    contract_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    row = _get_contract(db, contract_id, tenant_id)
    try:
        versions = db.execute(
            text(
                "SELECT id, version_number, changed_at, changed_by, change_summary "
                "FROM domain_contracts.contract_versions "
                "WHERE contract_id = :cid AND tenant_id = :tid ORDER BY version_number ASC"
            ),
            {"cid": contract_id, "tid": tenant_id},
        ).mappings().all()
        obligations = db.execute(
            text(
                "SELECT * FROM domain_contracts.contract_obligations "
                "WHERE contract_id = :cid AND tenant_id = :tid ORDER BY due_date ASC"
            ),
            {"cid": contract_id, "tid": tenant_id},
        ).mappings().all()
    except Exception:
        raise HTTPException(status_code=503, detail="Datenbankfehler")
    return {
        **_row_to_contract(row).model_dump(),
        "versions": [dict(v) for v in versions],
        "obligations": [dict(o) for o in obligations],
    }


@router.patch("/contracts/{contract_id}", response_model=ContractOut)
async def update_contract(
    contract_id: str,
    payload: ContractUpdate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    row = _get_contract(db, contract_id, tenant_id)
    data = payload.model_dump(exclude_unset=True, exclude={"change_summary", "changed_by"})
    if not data:
        return _row_to_contract(row)
    sets = ", ".join(f"{k} = :{k}" for k in data)
    data["id"] = contract_id
    data["tenant_id"] = tenant_id
    try:
        db.execute(
            text(f"UPDATE domain_contracts.contracts SET {sets} WHERE id = :id AND tenant_id = :tenant_id"),
            data,
        )
        ver_no = _next_version_number(db, contract_id, tenant_id)
        updated = _get_contract(db, contract_id, tenant_id)
        _create_version(
            db, contract_id, tenant_id, ver_no,
            payload.changed_by, payload.change_summary or "Update",
            {k: str(updated.get(k)) for k in data if k not in ("id", "tenant_id")},
        )
        db.commit()
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise HTTPException(status_code=503, detail="Datenbankfehler")
    return _row_to_contract(_get_contract(db, contract_id, tenant_id))


@router.post("/contracts/{contract_id}/obligations", response_model=ObligationOut, status_code=status.HTTP_201_CREATED)
async def add_obligation(
    contract_id: str,
    payload: ObligationCreate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    _get_contract(db, contract_id, tenant_id)
    oid = str(uuid4())
    now = datetime.now(timezone.utc)
    initial_status = "OFFEN"
    if payload.due_date < now:
        initial_status = "UEBERFAELLIG"
    try:
        db.execute(
            text(
                """
                INSERT INTO domain_contracts.contract_obligations
                  (id, contract_id, obligation_type, due_date, description, status, tenant_id, created_at)
                VALUES
                  (:id, :cid, :otype, :due, :desc, :status, :tid, :now)
                """
            ),
            {
                "id": oid, "cid": contract_id, "otype": payload.obligation_type,
                "due": payload.due_date, "desc": payload.description,
                "status": initial_status, "tid": tenant_id, "now": now,
            },
        )
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=503, detail="Datenbankfehler")
    return ObligationOut(
        id=oid, contract_id=contract_id,
        obligation_type=payload.obligation_type,
        due_date=payload.due_date,
        description=payload.description,
        status=initial_status,
        tenant_id=tenant_id,
    )


@router.get("/contracts/{contract_id}/obligations", response_model=list[ObligationOut])
async def list_obligations(
    contract_id: str,
    status_filter: Optional[str] = Query(None, alias="status"),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    _get_contract(db, contract_id, tenant_id)
    where = ["contract_id = :cid", "tenant_id = :tid"]
    params: dict = {"cid": contract_id, "tid": tenant_id}
    if status_filter:
        where.append("status = :status")
        params["status"] = status_filter
    where_sql = " AND ".join(where)
    try:
        rows = db.execute(
            text(f"SELECT * FROM domain_contracts.contract_obligations WHERE {where_sql} ORDER BY due_date ASC"),
            params,
        ).mappings().all()
    except Exception:
        raise HTTPException(status_code=503, detail="Datenbankfehler")
    return [
        ObligationOut(
            id=str(r["id"]), contract_id=str(r["contract_id"]),
            obligation_type=str(r["obligation_type"]), due_date=r["due_date"],
            description=str(r["description"]), status=str(r["status"]),
            tenant_id=str(r["tenant_id"]),
        )
        for r in rows
    ]


@router.patch("/contracts/{contract_id}/obligations/{obligation_id}", response_model=ObligationOut)
async def update_obligation_status(
    contract_id: str,
    obligation_id: str,
    payload: ObligationUpdate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    _get_contract(db, contract_id, tenant_id)
    try:
        db.execute(
            text(
                "UPDATE domain_contracts.contract_obligations SET status = :status "
                "WHERE id = :oid AND contract_id = :cid AND tenant_id = :tid"
            ),
            {"status": payload.status, "oid": obligation_id, "cid": contract_id, "tid": tenant_id},
        )
        db.commit()
        row = db.execute(
            text(
                "SELECT * FROM domain_contracts.contract_obligations WHERE id = :oid AND tenant_id = :tid"
            ),
            {"oid": obligation_id, "tid": tenant_id},
        ).mappings().first()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=503, detail="Datenbankfehler")
    if not row:
        raise HTTPException(status_code=404, detail="Verpflichtung nicht gefunden")
    r = dict(row)
    return ObligationOut(
        id=str(r["id"]), contract_id=str(r["contract_id"]),
        obligation_type=str(r["obligation_type"]), due_date=r["due_date"],
        description=str(r["description"]), status=str(r["status"]),
        tenant_id=str(r["tenant_id"]),
    )


@router.post("/contracts/{contract_id}/renew", response_model=ContractOut)
async def renew_contract(
    contract_id: str,
    payload: RenewBody,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    row = _get_contract(db, contract_id, tenant_id)
    try:
        db.execute(
            text(
                "UPDATE domain_contracts.contracts SET end_date = :end_date, status = 'AKTIV' "
                "WHERE id = :id AND tenant_id = :tid"
            ),
            {"end_date": payload.new_end_date, "id": contract_id, "tid": tenant_id},
        )
        ver_no = _next_version_number(db, contract_id, tenant_id)
        _create_version(db, contract_id, tenant_id, ver_no, "system", "Verlängerung",
                        {"end_date": str(payload.new_end_date), "status": "AKTIV"})
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=503, detail="Datenbankfehler")
    return _row_to_contract(_get_contract(db, contract_id, tenant_id))


@router.get("/analytics", response_model=dict)
async def contract_analytics(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    now = datetime.now(timezone.utc)
    try:
        type_rows = db.execute(
            text(
                """
                SELECT contract_type, COUNT(*) AS cnt, COALESCE(SUM(total_value_eur), 0) AS total_value
                FROM domain_contracts.contracts
                WHERE tenant_id = :tid
                GROUP BY contract_type
                """
            ),
            {"tid": tenant_id},
        ).mappings().all()

        expiring_30 = db.execute(
            text(
                """
                SELECT COUNT(*) FROM domain_contracts.contracts
                WHERE tenant_id = :tid AND status = 'AKTIV'
                  AND end_date IS NOT NULL
                  AND end_date <= (NOW() + interval '30 days')
                  AND end_date >= NOW()
                """
            ),
            {"tid": tenant_id},
        ).scalar() or 0

        overdue = db.execute(
            text(
                """
                SELECT COUNT(*) FROM domain_contracts.contract_obligations
                WHERE tenant_id = :tid AND status = 'UEBERFAELLIG'
                """
            ),
            {"tid": tenant_id},
        ).scalar() or 0

    except Exception:
        raise HTTPException(status_code=503, detail="Datenbankfehler")

    total_by_type: dict = {}
    total_value_by_type: dict = {}
    for r in type_rows:
        ct = str(r["contract_type"])
        total_by_type[ct] = int(r["cnt"])
        total_value_by_type[ct] = float(r["total_value"])

    return {
        "total_by_type": total_by_type,
        "total_value_by_type": total_value_by_type,
        "expiring_30days": int(expiring_30),
        "obligations_overdue": int(overdue),
    }
