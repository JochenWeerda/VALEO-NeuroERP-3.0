"""Quality Lot Binding Endpoints — FEED-CHAIN-003.

Persistiert LotQualityProfile und QualityReleaseDecision in domain_ops statt
in-memory. Release-Entscheidung (approve/reject) schreibt qualitaetsstatus
auf die verknüpfte ops_chargen-Charge zurück.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from ....core.database import get_db
from ....core.tenant import get_tenant_id
from ....core.quality_lot_binding import (
    LotQualityProfile,
    QualityReleaseDecision,
)
from app.api.v1.schemas.base import BaseSchema

router = APIRouter(prefix="/agrar/quality-lots", tags=["agrar", "quality"])

QUALITY_REVISION = "feed_chain_quality_lot_20260613"

# ── Helpers ─────────────────────────────────────────────────────────────────


def _tables_ready(db: Session) -> bool:
    n = db.execute(
        text(
            "SELECT count(*) FROM information_schema.tables "
            "WHERE table_schema = 'domain_ops' "
            "AND table_name = 'quality_lot_profiles'"
        )
    ).scalar()
    return int(n or 0) == 1


def _ensure_tables(db: Session) -> None:
    if not _tables_ready(db):
        raise HTTPException(
            status_code=503,
            detail=f"Schema nicht migriert — bitte 'alembic upgrade {QUALITY_REVISION}' ausführen",
        )


def _row_to_profile(row) -> LotQualityProfile:
    d = dict(row._mapping)
    return LotQualityProfile(
        lot_id=d["lot_id"],
        tenant_id=d["tenant_id"],
        acceptance_id=d.get("acceptance_id"),
        contract_id=d.get("contract_id"),
        protocol_id=d.get("protocol_id"),
        moisture_pct=float(d["moisture_pct"]) if d.get("moisture_pct") is not None else None,
        impurities_pct=float(d["impurities_pct"]) if d.get("impurities_pct") is not None else None,
        protein_pct=float(d["protein_pct"]) if d.get("protein_pct") is not None else None,
        hl_weight=float(d["hl_weight"]) if d.get("hl_weight") is not None else None,
        overall_grade=d.get("overall_grade"),
        price_deduction_pct=float(d.get("price_deduction_pct") or 0),
        approval_status=d.get("approval_status", "pending"),
    )


def _row_to_decision(row) -> QualityReleaseDecision:
    d = dict(row._mapping)
    return QualityReleaseDecision(
        lot_id=d["lot_id"],
        protocol_id=d["protocol_id"],
        decision=d["decision"],
        decided_by=d["decided_by"],
        decided_at=d["decided_at"],
        reason=d.get("reason"),
        price_deduction_applied_pct=float(d.get("price_deduction_applied_pct") or 0),
    )


# ── Endpoints ────────────────────────────────────────────────────────────────


@router.get("", response_model=list[LotQualityProfile], summary="Lots auflisten")
async def list_lots(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    _ensure_tables(db)
    rows = db.execute(
        text("SELECT * FROM domain_ops.quality_lot_profiles WHERE tenant_id = :tid ORDER BY created_at DESC"),
        {"tid": tenant_id},
    ).fetchall()
    return [_row_to_profile(r) for r in rows]


@router.post("", response_model=LotQualityProfile, status_code=201, summary="Lot anlegen")
async def create_lot(
    profile: LotQualityProfile,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    _ensure_tables(db)
    profile = profile.model_copy(update={"tenant_id": tenant_id})
    rec_id = str(uuid.uuid4())
    db.execute(
        text("""
            INSERT INTO domain_ops.quality_lot_profiles
              (id, lot_id, tenant_id, acceptance_id, contract_id, protocol_id,
               moisture_pct, impurities_pct, protein_pct, hl_weight,
               overall_grade, price_deduction_pct, approval_status)
            VALUES
              (:id, :lot_id, :tid, :acc, :con, :proto,
               :moist, :imp, :prot, :hlw,
               :grade, :deduction, :status)
            ON CONFLICT (tenant_id, lot_id) DO UPDATE SET
              acceptance_id = EXCLUDED.acceptance_id,
              contract_id = EXCLUDED.contract_id,
              protocol_id = EXCLUDED.protocol_id,
              moisture_pct = EXCLUDED.moisture_pct,
              impurities_pct = EXCLUDED.impurities_pct,
              protein_pct = EXCLUDED.protein_pct,
              hl_weight = EXCLUDED.hl_weight,
              overall_grade = EXCLUDED.overall_grade,
              price_deduction_pct = EXCLUDED.price_deduction_pct,
              approval_status = EXCLUDED.approval_status,
              updated_at = NOW()
        """),
        {
            "id": rec_id, "lot_id": profile.lot_id, "tid": tenant_id,
            "acc": profile.acceptance_id, "con": profile.contract_id,
            "proto": profile.protocol_id,
            "moist": profile.moisture_pct, "imp": profile.impurities_pct,
            "prot": profile.protein_pct, "hlw": profile.hl_weight,
            "grade": profile.overall_grade,
            "deduction": profile.price_deduction_pct,
            "status": profile.approval_status,
        },
    )
    db.commit()
    return profile


@router.get("/{lot_id}", response_model=LotQualityProfile, summary="Lot abrufen")
async def get_lot(
    lot_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    _ensure_tables(db)
    row = db.execute(
        text("SELECT * FROM domain_ops.quality_lot_profiles WHERE lot_id = :lid AND tenant_id = :tid"),
        {"lid": lot_id, "tid": tenant_id},
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Lot not found")
    return _row_to_profile(row)


@router.post(
    "/{lot_id}/release-decision",
    response_model=QualityReleaseDecision,
    status_code=201,
    summary="Freigabeentscheidung anlegen",
)
async def create_release_decision(
    lot_id: str,
    decision: QualityReleaseDecision,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Freigabeentscheidung persistieren und ops_chargen.qualitaetsstatus synchronisieren."""
    _ensure_tables(db)
    lot_row = db.execute(
        text("SELECT * FROM domain_ops.quality_lot_profiles WHERE lot_id = :lid AND tenant_id = :tid"),
        {"lid": lot_id, "tid": tenant_id},
    ).fetchone()
    if not lot_row:
        raise HTTPException(status_code=404, detail="Lot not found")

    decision = decision.model_copy(update={"lot_id": lot_id})
    rec_id = str(uuid.uuid4())

    db.execute(
        text("""
            INSERT INTO domain_ops.quality_release_decisions
              (id, lot_id, tenant_id, protocol_id, decision, decided_by,
               decided_at, reason, price_deduction_applied_pct)
            VALUES
              (:id, :lot_id, :tid, :proto, :dec, :by, :at, :reason, :deduction)
            ON CONFLICT (tenant_id, lot_id) DO UPDATE SET
              protocol_id = EXCLUDED.protocol_id,
              decision = EXCLUDED.decision,
              decided_by = EXCLUDED.decided_by,
              decided_at = EXCLUDED.decided_at,
              reason = EXCLUDED.reason,
              price_deduction_applied_pct = EXCLUDED.price_deduction_applied_pct
        """),
        {
            "id": rec_id, "lot_id": lot_id, "tid": tenant_id,
            "proto": decision.protocol_id, "dec": decision.decision,
            "by": decision.decided_by, "at": decision.decided_at,
            "reason": decision.reason,
            "deduction": decision.price_deduction_applied_pct,
        },
    )

    # Update lot approval_status + price_deduction
    status_map = {"approve": "approved", "reject": "rejected", "hold": "pending"}
    new_status = status_map.get(decision.decision, "pending")
    db.execute(
        text("""
            UPDATE domain_ops.quality_lot_profiles
            SET approval_status = :status,
                price_deduction_pct = :deduction,
                updated_at = NOW()
            WHERE lot_id = :lid AND tenant_id = :tid
        """),
        {"status": new_status, "deduction": decision.price_deduction_applied_pct,
         "lid": lot_id, "tid": tenant_id},
    )

    # Charge-Rückkopplung: qualitaetsstatus auf ops_chargen setzen (lot_id = chargen_id)
    chargen_status_map = {"approve": "freigegeben", "reject": "gesperrt", "hold": "quarantaene"}
    chargen_status = chargen_status_map.get(decision.decision)
    if chargen_status:
        db.execute(
            text("""
                UPDATE domain_ops.ops_chargen
                SET qualitaetsstatus = :qs
                WHERE chargen_id = :cid
            """),
            {"qs": chargen_status, "cid": lot_id},
        )

    db.commit()
    return decision
