"""
Silo capacity and virtual lot endpoints (AGRAR-SILO-01).
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional
from app.core.uuid7 import uuid7

from fastapi import Response, APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import func, text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.infrastructure.models import Silo, SiloLot, SiloLotMovement, SiloQualitySnapshot

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.silo_schemas import (
    LeermeldungCreate,
    SiloCreate,
    SiloLotCreate,
    SiloLotMovementCreate,
    SiloOut,
)
from pydantic import ConfigDict as _ConfigDict

router = APIRouter()


def _to_float(value: Decimal | float | int | None) -> float:
    if value is None:
        return 0.0
    return float(value)


def _weighted_quality_snapshot(lots: list[SiloLot]) -> dict[str, Optional[float]]:
    active = [lot for lot in lots if lot.status == "active" and _to_float(lot.quantity_tons) > 0]
    if not active:
        return {
            "total_quantity_tons": 0.0,
            "moisture_avg_pct": None,
            "protein_avg_pct": None,
            "impurities_avg_pct": None,
            "hl_weight_avg": None,
            "lot_count": 0,
        }

    total = sum(_to_float(lot.quantity_tons) for lot in active)

    def _avg(field_name: str) -> Optional[float]:
        weighted_sum = 0.0
        weighted_total = 0.0
        for lot in active:
            metric = getattr(lot, field_name)
            if metric is None:
                continue
            qty = _to_float(lot.quantity_tons)
            weighted_sum += float(metric) * qty
            weighted_total += qty
        if weighted_total <= 0:
            return None
        return round(weighted_sum / weighted_total, 2)

    return {
        "total_quantity_tons": round(total, 3),
        "moisture_avg_pct": _avg("moisture_pct"),
        "protein_avg_pct": _avg("protein_pct"),
        "impurities_avg_pct": _avg("impurities_pct"),
        "hl_weight_avg": _avg("hl_weight"),
        "lot_count": len(active),
    }


def _create_snapshot(db: Session, silo_id: str, tenant_id: str) -> SiloQualitySnapshot:
    lots = (
        db.query(SiloLot)
        .filter(SiloLot.silo_id == silo_id, SiloLot.tenant_id == tenant_id)
        .all()
    )
    snapshot_values = _weighted_quality_snapshot(lots)
    snapshot = SiloQualitySnapshot(
        id=uuid7(),
        silo_id=silo_id,
        total_quantity_tons=snapshot_values["total_quantity_tons"],
        moisture_avg_pct=snapshot_values["moisture_avg_pct"],
        protein_avg_pct=snapshot_values["protein_avg_pct"],
        impurities_avg_pct=snapshot_values["impurities_avg_pct"],
        hl_weight_avg=snapshot_values["hl_weight_avg"],
        lot_count=snapshot_values["lot_count"],
        tenant_id=tenant_id,
    )
    db.add(snapshot)
    return snapshot

@router.get("/kapazitaeten", response_model=SiloOut, summary="Silo capacities abrufen")
async def get_silo_capacities(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    silos = (
        db.query(Silo)
        .filter(Silo.tenant_id == tenant_id, Silo.is_active == True)  # noqa: E712
        .order_by(Silo.silo_number.asc())
        .all()
    )

    occupied_by_silo = {
        str(row.silo_id): _to_float(row.occupied)
        for row in (
            db.query(
                SiloLot.silo_id.label("silo_id"),
                func.coalesce(func.sum(SiloLot.quantity_tons), 0).label("occupied"),
            )
            .filter(
                SiloLot.tenant_id == tenant_id,
                SiloLot.status == "active",
            )
            .group_by(SiloLot.silo_id)
            .all()
        )
    }

    total_capacity = sum(_to_float(silo.capacity_tons) for silo in silos)
    total_occupied = sum(occupied_by_silo.get(str(silo.id), 0.0) for silo in silos)

    silo_list: list[dict[str, object]] = []
    for silo in silos:
        occupied = occupied_by_silo.get(str(silo.id), 0.0)
        capacity = _to_float(silo.capacity_tons)
        percent = round((occupied / capacity * 100.0), 2) if capacity > 0 else 0.0
        silo_list.append(
            {
                "id": str(silo.id),
                "nummer": silo.silo_number,
                "artikel": silo.article_id or "-",
                "kapazitaet": round(capacity, 3),
                "belegt": round(occupied, 3),
                "prozent": percent,
            }
        )

    return {
        "gesamt": len(silos),
        "kapazitaet": round(total_capacity, 3),
        "belegt": round(total_occupied, 3),
        "liste": silo_list,
        "generated_at": datetime.utcnow().isoformat(),
    }


@router.get("/silos", response_model=list[SiloOut], summary="Silos auflisten")
async def list_silos(
    include_inactive: bool = Query(False),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> list[dict]:
    query = db.query(Silo).filter(Silo.tenant_id == tenant_id)
    if not include_inactive:
        query = query.filter(Silo.is_active == True)  # noqa: E712
    silos = query.order_by(Silo.silo_number.asc()).all()
    return [
        {
            "id": str(silo.id),
            "silo_number": silo.silo_number,
            "name": silo.name,
            "article_id": silo.article_id,
            "capacity_tons": _to_float(silo.capacity_tons),
            "is_active": bool(silo.is_active),
        }
        for silo in silos
    ]


@router.get("/silos/{silo_id}/details", response_model=SiloOut, summary="Silo details abrufen")
async def get_silo_details(
    silo_id: str,
    include_movements: bool = Query(True),
    movement_limit: int = Query(25, ge=1, le=200),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    silo = (
        db.query(Silo)
        .filter(Silo.id == silo_id, Silo.tenant_id == tenant_id)
        .first()
    )
    if not silo:
        raise HTTPException(status_code=404, detail="Silo not found")

    lots = (
        db.query(SiloLot)
        .filter(SiloLot.silo_id == silo_id, SiloLot.tenant_id == tenant_id)
        .order_by(SiloLot.created_at.desc())
        .all()
    )
    snapshot = _create_snapshot(db, silo_id, tenant_id)
    db.commit()
    db.refresh(snapshot)

    lot_ids = [lot.id for lot in lots]
    movement_items: list[dict[str, object]] = []
    if include_movements and lot_ids:
        movements = (
            db.query(SiloLotMovement)
            .filter(SiloLotMovement.silo_lot_id.in_(lot_ids), SiloLotMovement.tenant_id == tenant_id)
            .order_by(SiloLotMovement.created_at.desc())
            .limit(movement_limit)
            .all()
        )
        movement_items = [
            {
                "id": m.id,
                "silo_lot_id": m.silo_lot_id,
                "movement_type": m.movement_type,
                "quantity_tons": _to_float(m.quantity_tons),
                "note": m.note,
                "created_at": m.created_at.isoformat() if m.created_at else None,
            }
            for m in movements
        ]

    return {
        "silo": {
            "id": str(silo.id),
            "silo_number": silo.silo_number,
            "name": silo.name,
            "article_id": silo.article_id,
            "capacity_tons": _to_float(silo.capacity_tons),
            "is_active": bool(silo.is_active),
        },
        "snapshot": {
            "id": snapshot.id,
            "silo_id": snapshot.silo_id,
            "total_quantity_tons": _to_float(snapshot.total_quantity_tons),
            "moisture_avg_pct": _to_float(snapshot.moisture_avg_pct) if snapshot.moisture_avg_pct is not None else None,
            "protein_avg_pct": _to_float(snapshot.protein_avg_pct) if snapshot.protein_avg_pct is not None else None,
            "impurities_avg_pct": _to_float(snapshot.impurities_avg_pct) if snapshot.impurities_avg_pct is not None else None,
            "hl_weight_avg": _to_float(snapshot.hl_weight_avg) if snapshot.hl_weight_avg is not None else None,
            "lot_count": int(snapshot.lot_count),
            "created_at": snapshot.created_at.isoformat() if snapshot.created_at else None,
        },
        "lots": [
            {
                "id": lot.id,
                "virtual_lot_number": lot.virtual_lot_number,
                "source_ticket_id": lot.source_ticket_id,
                "source_partner_id": lot.source_partner_id,
                "article_id": lot.article_id,
                "quantity_tons": _to_float(lot.quantity_tons),
                "moisture_pct": _to_float(lot.moisture_pct) if lot.moisture_pct is not None else None,
                "protein_pct": _to_float(lot.protein_pct) if lot.protein_pct is not None else None,
                "impurities_pct": _to_float(lot.impurities_pct) if lot.impurities_pct is not None else None,
                "hl_weight": _to_float(lot.hl_weight) if lot.hl_weight is not None else None,
                "status": lot.status,
                "created_at": lot.created_at.isoformat() if lot.created_at else None,
            }
            for lot in lots
        ],
        "movements": movement_items,
    }


@router.post("/silos", response_model=SiloOut, status_code=201, summary="Silo anlegen")
async def create_silo(
    payload: SiloCreate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    existing = (
        db.query(Silo)
        .filter(Silo.tenant_id == tenant_id, Silo.silo_number == payload.silo_number)
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="Silo number already exists")

    silo = Silo(
        id=uuid7(),
        silo_number=payload.silo_number,
        name=payload.name,
        article_id=payload.article_id,
        capacity_tons=payload.capacity_tons,
        tenant_id=tenant_id,
        is_active=True,
    )
    db.add(silo)
    db.commit()
    db.refresh(silo)
    return {
        "id": str(silo.id),
        "silo_number": silo.silo_number,
        "name": silo.name,
        "article_id": silo.article_id,
        "capacity_tons": _to_float(silo.capacity_tons),
        "is_active": bool(silo.is_active),
    }


@router.put("/silos/{silo_id}", response_model=SiloOut, summary="Silo aktualisieren")
async def update_silo(
    silo_id: str,
    payload: SiloCreate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    silo = db.query(Silo).filter(Silo.id == silo_id, Silo.tenant_id == tenant_id).first()
    if not silo:
        raise HTTPException(status_code=404, detail="Silo not found")
    for field in ("silo_number", "name", "article_id", "capacity_tons"):
        val = getattr(payload, field, None)
        if val is not None:
            setattr(silo, field, val)
    db.commit()
    db.refresh(silo)
    return {
        "id": str(silo.id),
        "silo_number": silo.silo_number,
        "name": silo.name,
        "article_id": silo.article_id,
        "capacity_tons": _to_float(silo.capacity_tons),
        "is_active": bool(silo.is_active),
    }


@router.delete("/silos/{silo_id}", status_code=204, response_class=Response, response_model=None, summary="Silo löschen")
async def delete_silo(
    silo_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    silo = db.query(Silo).filter(Silo.id == silo_id, Silo.tenant_id == tenant_id).first()
    if not silo:
        raise HTTPException(status_code=404, detail="Silo not found")
    active_lots = db.query(SiloLot).filter(
        SiloLot.silo_id == silo_id, SiloLot.tenant_id == tenant_id, SiloLot.status == "active"
    ).count()
    if active_lots > 0:
        raise HTTPException(status_code=400, detail="Silo hat aktive Lots — zuerst auslagern")
    silo.is_active = False
    db.commit()


@router.post("/silos/{silo_id}/lots", response_model=SiloOut, status_code=201, summary="Silo lot anlegen")
async def create_silo_lot(
    silo_id: str,
    payload: SiloLotCreate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    silo = (
        db.query(Silo)
        .filter(Silo.id == silo_id, Silo.tenant_id == tenant_id, Silo.is_active == True)  # noqa: E712
        .first()
    )
    if not silo:
        raise HTTPException(status_code=404, detail="Silo not found")

    lot = SiloLot(
        id=uuid7(),
        silo_id=str(silo.id),
        virtual_lot_number=payload.virtual_lot_number,
        source_ticket_id=payload.source_ticket_id,
        source_partner_id=payload.source_partner_id,
        article_id=payload.article_id or silo.article_id,
        quantity_tons=payload.quantity_tons,
        moisture_pct=payload.moisture_pct,
        protein_pct=payload.protein_pct,
        impurities_pct=payload.impurities_pct,
        hl_weight=payload.hl_weight,
        status="active",
        tenant_id=tenant_id,
    )
    db.add(lot)
    db.flush()

    db.add(
        SiloLotMovement(
            id=uuid7(),
            silo_lot_id=lot.id,
            movement_type="in",
            quantity_tons=payload.quantity_tons,
            note="initial lot booking",
            tenant_id=tenant_id,
        )
    )
    snapshot = _create_snapshot(db, str(silo.id), tenant_id)
    db.commit()
    db.refresh(lot)
    db.refresh(snapshot)

    return {
        "lot": {
            "id": lot.id,
            "silo_id": lot.silo_id,
            "virtual_lot_number": lot.virtual_lot_number,
            "quantity_tons": _to_float(lot.quantity_tons),
            "status": lot.status,
        },
        "snapshot": {
            "id": snapshot.id,
            "silo_id": snapshot.silo_id,
            "total_quantity_tons": _to_float(snapshot.total_quantity_tons),
            "moisture_avg_pct": _to_float(snapshot.moisture_avg_pct) if snapshot.moisture_avg_pct is not None else None,
            "protein_avg_pct": _to_float(snapshot.protein_avg_pct) if snapshot.protein_avg_pct is not None else None,
            "impurities_avg_pct": _to_float(snapshot.impurities_avg_pct) if snapshot.impurities_avg_pct is not None else None,
            "hl_weight_avg": _to_float(snapshot.hl_weight_avg) if snapshot.hl_weight_avg is not None else None,
            "lot_count": int(snapshot.lot_count),
        },
    }


@router.put("/silos/{silo_id}/lots/{lot_id}", response_model=SiloOut, summary="Silo lot aktualisieren")
async def update_silo_lot(
    silo_id: str,
    lot_id: str,
    payload: SiloLotCreate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    lot = db.query(SiloLot).filter(
        SiloLot.id == lot_id, SiloLot.silo_id == silo_id, SiloLot.tenant_id == tenant_id
    ).first()
    if not lot:
        raise HTTPException(status_code=404, detail="Silo lot not found")
    if lot.status != "active":
        raise HTTPException(status_code=400, detail="Nur aktive Lots können bearbeitet werden")
    for field in ("moisture_pct", "protein_pct", "impurities_pct", "hl_weight"):
        val = getattr(payload, field, None)
        if val is not None:
            setattr(lot, field, val)
    snapshot = _create_snapshot(db, silo_id, tenant_id)
    db.commit()
    db.refresh(lot)
    db.refresh(snapshot)
    return {"id": str(lot.id), "silo_id": lot.silo_id, "status": lot.status,
            "quantity_tons": _to_float(lot.quantity_tons)}


@router.delete("/silos/{silo_id}/lots/{lot_id}", status_code=204, response_class=Response, response_model=None, summary="Silo lot löschen")
async def delete_silo_lot(
    silo_id: str,
    lot_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    lot = db.query(SiloLot).filter(
        SiloLot.id == lot_id, SiloLot.silo_id == silo_id, SiloLot.tenant_id == tenant_id
    ).first()
    if not lot:
        raise HTTPException(status_code=404, detail="Silo lot not found")
    if lot.status == "active" and _to_float(lot.quantity_tons) > 0:
        raise HTTPException(status_code=400, detail="Lot hat Restmenge — zuerst ausbuchen")
    lot.status = "closed"
    _create_snapshot(db, silo_id, tenant_id)
    db.commit()


@router.post("/silos/{silo_id}/lots/{lot_id}/movements", response_model=SiloOut, status_code=201, summary="Silo lot movement anlegen")
async def create_silo_lot_movement(
    silo_id: str,
    lot_id: str,
    payload: SiloLotMovementCreate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    lot = (
        db.query(SiloLot)
        .filter(SiloLot.id == lot_id, SiloLot.silo_id == silo_id, SiloLot.tenant_id == tenant_id)
        .first()
    )
    if not lot:
        raise HTTPException(status_code=404, detail="Silo lot not found")
    if lot.status != "active":
        raise HTTPException(status_code=400, detail="Silo lot is not active")

    qty = Decimal(str(payload.quantity_tons))
    if payload.movement_type == "out":
        current_qty = Decimal(str(lot.quantity_tons))
        if qty > current_qty:
            raise HTTPException(status_code=400, detail="Movement exceeds lot quantity")
        lot.quantity_tons = current_qty - qty
        if Decimal(str(lot.quantity_tons)) <= Decimal("0"):
            lot.status = "closed"
    elif payload.movement_type == "in":
        lot.quantity_tons = Decimal(str(lot.quantity_tons)) + qty

    movement = SiloLotMovement(
        id=uuid7(),
        silo_lot_id=lot.id,
        movement_type=payload.movement_type,
        quantity_tons=payload.quantity_tons,
        note=payload.note,
        tenant_id=tenant_id,
    )
    db.add(movement)
    snapshot = _create_snapshot(db, silo_id, tenant_id)
    db.commit()
    db.refresh(movement)
    db.refresh(snapshot)

    return {
        "movement": {
            "id": movement.id,
            "silo_lot_id": movement.silo_lot_id,
            "movement_type": movement.movement_type,
            "quantity_tons": _to_float(movement.quantity_tons),
            "note": movement.note,
        },
        "snapshot": {
            "id": snapshot.id,
            "silo_id": snapshot.silo_id,
            "total_quantity_tons": _to_float(snapshot.total_quantity_tons),
            "moisture_avg_pct": _to_float(snapshot.moisture_avg_pct) if snapshot.moisture_avg_pct is not None else None,
            "protein_avg_pct": _to_float(snapshot.protein_avg_pct) if snapshot.protein_avg_pct is not None else None,
            "impurities_avg_pct": _to_float(snapshot.impurities_avg_pct) if snapshot.impurities_avg_pct is not None else None,
            "hl_weight_avg": _to_float(snapshot.hl_weight_avg) if snapshot.hl_weight_avg is not None else None,
            "lot_count": int(snapshot.lot_count),
        },
    }


# ============================================================
# SILO-LEER-001 — Silo-Leermeldung
# ============================================================

def _silo_columns(db: Session) -> set[str]:
    """Return set of column names for agrar_silos table."""
    rows = db.execute(
        text(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name = 'agrar_silos'"
        )
    ).fetchall()
    return {r[0] for r in rows}


@router.post("/silos/{silo_id}/leermeldung", response_model=SiloOut, status_code=201, summary="Leermeldung anlegen")
async def create_leermeldung(
    silo_id: str,
    payload: LeermeldungCreate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    """SILO-LEER-001: Silo vollständig leeren mit Schwundbuchung."""
    # 1. Prüfe Silo
    silo = db.query(Silo).filter(Silo.id == silo_id, Silo.tenant_id == tenant_id).first()
    if not silo:
        raise HTTPException(status_code=404, detail="Silo nicht gefunden")
    if getattr(silo, "status", None) not in (None, "active", "AKTIV"):
        raise HTTPException(status_code=422, detail="Silo ist nicht aktiv")

    # 2. Offene Lots prüfen
    open_lot_count = (
        db.query(func.count(SiloLot.id))
        .filter(
            SiloLot.silo_id == silo_id,
            SiloLot.tenant_id == tenant_id,
            SiloLot.status.notin_(["closed", "ABGESCHLOSSEN", "LEER"]),
        )
        .scalar()
    )
    if open_lot_count and open_lot_count > 0:
        raise HTTPException(status_code=422, detail="Offene Lots vorhanden")

    # 3. Physischer Restbestand (in tons, convert to kg)
    restbestand_row = db.execute(
        text(
            "SELECT COALESCE(SUM(quantity_tons), 0) FROM agrar_silo_lots "
            "WHERE silo_id = :silo_id "
            "AND status NOT IN ('closed', 'ABGESCHLOSSEN', 'LEER')"
        ),
        {"silo_id": silo_id},
    ).fetchone()
    restbestand_kg = float(restbestand_row[0]) * 1000 if restbestand_row else 0.0

    # 4. Schwund-Deckung prüfen
    if restbestand_kg > 0 and payload.schwund_kg < restbestand_kg:
        raise HTTPException(
            status_code=422,
            detail=f"Schwund deckt Restbestand nicht vollständig (Restbestand: {restbestand_kg:.1f} kg)",
        )

    # 5. Silo-Status auf LEER setzen
    leermeldung_id = str(uuid7())
    now_iso = datetime.now(timezone.utc).isoformat()
    cols = _silo_columns(db)

    if "leermeldung_meta" in cols:
        meta = {
            "leermeldung_id": leermeldung_id,
            "wiegung_id": payload.wiegung_id,
            "schwund_kg": payload.schwund_kg,
            "grund": payload.grund,
            "bearbeiter": payload.bearbeiter,
            "timestamp": now_iso,
        }
        db.execute(
            text("UPDATE agrar_silos SET leermeldung_meta = :meta WHERE id = :id"),
            {"meta": json.dumps(meta), "id": silo_id},
        )
    if "status" in cols:
        db.execute(
            text("UPDATE agrar_silos SET status = 'LEER' WHERE id = :id"),
            {"id": silo_id},
        )
    optional_updates = {
        "last_empty_at": now_iso,
        "last_empty_wiegung_id": payload.wiegung_id,
        "last_empty_schwund_kg": payload.schwund_kg,
        "last_empty_grund": payload.grund,
        "last_empty_by": payload.bearbeiter,
    }
    for col, val in optional_updates.items():
        if col in cols and val is not None:
            db.execute(
                text(f"UPDATE agrar_silos SET {col} = :{col} WHERE id = :id"),  # noqa: S608  # nosec S608 — reviewed-safe: column names code-controlled, values parameterized
                {col: val, "id": silo_id},
            )

    # 6. Schwundbuchung als SiloLotMovement
    any_lot = (
        db.query(SiloLot)
        .filter(SiloLot.silo_id == silo_id, SiloLot.tenant_id == tenant_id)
        .first()
    )
    if any_lot and payload.schwund_kg > 0:
        schwund_tons = Decimal(str(payload.schwund_kg)) / Decimal("1000")
        movement = SiloLotMovement(
            id=uuid7(),
            silo_lot_id=any_lot.id,
            movement_type="SCHWUND",
            quantity_tons=schwund_tons,
            note=f"Leermeldung {leermeldung_id}: {payload.grund}",
            tenant_id=tenant_id,
        )
        db.add(movement)

    # 7. Verbleibende aktive Lots auf LEER setzen
    db.query(SiloLot).filter(
        SiloLot.silo_id == silo_id,
        SiloLot.tenant_id == tenant_id,
        SiloLot.status.notin_(["closed", "ABGESCHLOSSEN", "LEER"]),
    ).update({"status": "LEER"}, synchronize_session=False)

    _create_snapshot(db, silo_id, tenant_id)
    db.commit()

    return {
        "silo_id": silo_id,
        "status": "LEER",
        "schwund_kg": payload.schwund_kg,
        "wiegung_id": payload.wiegung_id,
        "leermeldung_id": leermeldung_id,
        "message": "Silo erfolgreich geleert",
    }


@router.get("/silos/{silo_id}/leermeldungen", response_model=list[SiloOut], summary="Leermeldungen auflisten")
async def list_leermeldungen(
    silo_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> list:
    """SILO-LEER-001: Leermeldungs-Historie für ein Silo."""
    silo = db.query(Silo).filter(Silo.id == silo_id, Silo.tenant_id == tenant_id).first()
    if not silo:
        raise HTTPException(status_code=404, detail="Silo nicht gefunden")

    cols = _silo_columns(db)

    # Aus leermeldung_meta JSONB falls vorhanden
    if "leermeldung_meta" in cols:
        row = db.execute(
            text("SELECT leermeldung_meta FROM agrar_silos WHERE id = :id"),
            {"id": silo_id},
        ).fetchone()
        if row and row[0]:
            meta = row[0] if isinstance(row[0], dict) else json.loads(row[0])
            return [meta]

    # Fallback: SCHWUND-Movements
    movements = (
        db.query(SiloLotMovement)
        .join(SiloLot, SiloLotMovement.silo_lot_id == SiloLot.id)
        .filter(
            SiloLot.silo_id == silo_id,
            SiloLot.tenant_id == tenant_id,
            SiloLotMovement.movement_type == "SCHWUND",
        )
        .all()
    )
    return [
        {
            "movement_id": str(m.id),
            "schwund_tons": _to_float(m.quantity_tons),
            "note": m.note,
        }
        for m in movements
    ]
