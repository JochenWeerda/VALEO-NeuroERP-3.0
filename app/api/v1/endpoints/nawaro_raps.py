"""
NaWaRo Raps profile API: usage split, sustainability certificates, coproduct balances.
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
from app.core.uuid7 import uuid7

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, model_validator
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.infrastructure.models import (
    AgrarContract,
    AgrarSettlement,
    NawaroRapsProfile,
    NawaroRapsCertificate,
    NawaroRapsBalance,
    WeighingTicket,
)

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.base import CompatFlexOut


router = APIRouter()


def _to_decimal(value: str | float | int | None) -> Decimal | None:
    if value is None:
        return None
    if isinstance(value, (float, int)):
        return Decimal(str(value))
    normalized = value.strip().replace(',', '.')
    if not normalized:
        return None
    try:
        return Decimal(normalized)
    except InvalidOperation as exc:
        raise HTTPException(status_code=422, detail=f'Invalid decimal value: {value}') from exc


class RapsCertificateIn(BaseModel):
    scheme: str = Field(..., min_length=2, max_length=80)
    certificate_number: str = Field(..., min_length=2, max_length=120)
    chain_stage: str | None = Field(default=None, max_length=80)
    valid_from: date | None = None
    valid_until: date | None = None
    issuer: str | None = Field(default=None, max_length=120)
    status: str = Field(default='valid', max_length=40)


class RapsCertificateOut(RapsCertificateIn):
    id: str


class RapsBalanceIn(BaseModel):
    booking_period: str | None = Field(default=None, max_length=20)
    input_seed_tons: str = Field(default='0')
    output_oil_tons: str = Field(default='0')
    output_meal_tons: str = Field(default='0')
    output_other_tons: str = Field(default='0')
    allocation_oil_pct: str | None = None
    allocation_meal_pct: str | None = None
    heap_location: str | None = Field(default=None, max_length=255)
    logistics_note: str | None = None


class RapsBalanceOut(RapsBalanceIn):
    id: str


class RapsProfileIn(BaseModel):
    article_id: str | None = Field(default=None, max_length=64)
    article_number: str | None = Field(default=None, max_length=80)
    article_name: str = Field(default='Raps', min_length=2, max_length=255)
    harvest_year: int = Field(..., ge=2000, le=2100)
    usage_food_pct: str = Field(default='0')
    usage_feed_pct: str = Field(default='0')
    usage_energy_pct: str = Field(default='0')
    usage_material_pct: str = Field(default='0')
    thg_gco2eq_mj: str | None = None
    yield_dt_per_ha: str | None = None
    notes: str | None = None
    certificates: list[RapsCertificateIn] = Field(default_factory=list)
    balances: list[RapsBalanceIn] = Field(default_factory=list)

    @model_validator(mode='after')
    def validate_usage_sum(self):
        parts = [
            _to_decimal(self.usage_food_pct) or Decimal('0'),
            _to_decimal(self.usage_feed_pct) or Decimal('0'),
            _to_decimal(self.usage_energy_pct) or Decimal('0'),
            _to_decimal(self.usage_material_pct) or Decimal('0'),
        ]
        total = sum(parts)
        if total != Decimal('100'):
            raise ValueError(f'Usage split must total 100.00%, got {total}')
        return self


class RapsProfileOut(RapsProfileIn):
    id: str
    certificates: list[RapsCertificateOut]
    balances: list[RapsBalanceOut]
    created_at: str | None = None
    updated_at: str | None = None


class RapsDeriveOut(BaseModel):
    profile: RapsProfileOut
    period: str
    source_tickets_kg: str
    source_settlements_kg: str
    source_input_tons: str
    plausibility_messages: list[str] = Field(default_factory=list)


def _decimal_equal(left: Decimal, right: Decimal, tol: Decimal = Decimal("0.20")) -> bool:
    return abs(left - right) <= tol


def _validate_balances(payload: RapsProfileIn):
    errors: list[str] = []
    for idx, bal in enumerate(payload.balances):
        position = idx + 1
        input_seed_tons = _to_decimal(bal.input_seed_tons) or Decimal("0")
        output_oil_tons = _to_decimal(bal.output_oil_tons) or Decimal("0")
        output_meal_tons = _to_decimal(bal.output_meal_tons) or Decimal("0")
        output_other_tons = _to_decimal(bal.output_other_tons) or Decimal("0")
        allocation_oil_pct = _to_decimal(bal.allocation_oil_pct)
        allocation_meal_pct = _to_decimal(bal.allocation_meal_pct)

        if input_seed_tons < 0 or output_oil_tons < 0 or output_meal_tons < 0 or output_other_tons < 0:
            errors.append(f"Balance row {position}: quantities must be >= 0")
            continue

        outputs_total = output_oil_tons + output_meal_tons + output_other_tons
        if input_seed_tons > 0 and outputs_total > (input_seed_tons * Decimal("1.05")):
            errors.append(
                f"Balance row {position}: outputs ({outputs_total}) exceed input ({input_seed_tons}) by >5%"
            )

        if allocation_oil_pct is not None or allocation_meal_pct is not None:
            alloc_sum = (allocation_oil_pct or Decimal("0")) + (allocation_meal_pct or Decimal("0"))
            if not _decimal_equal(alloc_sum, Decimal("100.00")):
                errors.append(
                    f"Balance row {position}: allocation oil+meal must total 100.00% (+/-0.20), got {alloc_sum}"
                )

    if errors:
        raise HTTPException(status_code=422, detail=errors)


def _profile_out(db: Session, profile: NawaroRapsProfile) -> RapsProfileOut:
    certificates = (
        db.query(NawaroRapsCertificate)
        .filter(NawaroRapsCertificate.profile_id == profile.id, NawaroRapsCertificate.tenant_id == profile.tenant_id)
        .order_by(NawaroRapsCertificate.created_at.asc())
        .all()
    )
    balances = (
        db.query(NawaroRapsBalance)
        .filter(NawaroRapsBalance.profile_id == profile.id, NawaroRapsBalance.tenant_id == profile.tenant_id)
        .order_by(NawaroRapsBalance.created_at.asc())
        .all()
    )

    return RapsProfileOut(
        id=profile.id,
        article_id=profile.article_id,
        article_number=profile.article_number,
        article_name=profile.article_name,
        harvest_year=profile.harvest_year,
        usage_food_pct=str(profile.usage_food_pct),
        usage_feed_pct=str(profile.usage_feed_pct),
        usage_energy_pct=str(profile.usage_energy_pct),
        usage_material_pct=str(profile.usage_material_pct),
        thg_gco2eq_mj=str(profile.thg_gco2eq_mj) if profile.thg_gco2eq_mj is not None else None,
        yield_dt_per_ha=str(profile.yield_dt_per_ha) if profile.yield_dt_per_ha is not None else None,
        notes=profile.notes,
        certificates=[
            RapsCertificateOut(
                id=c.id,
                scheme=c.scheme,
                certificate_number=c.certificate_number,
                chain_stage=c.chain_stage,
                valid_from=c.valid_from,
                valid_until=c.valid_until,
                issuer=c.issuer,
                status=c.status,
            )
            for c in certificates
        ],
        balances=[
            RapsBalanceOut(
                id=b.id,
                booking_period=b.booking_period,
                input_seed_tons=str(b.input_seed_tons),
                output_oil_tons=str(b.output_oil_tons),
                output_meal_tons=str(b.output_meal_tons),
                output_other_tons=str(b.output_other_tons),
                allocation_oil_pct=str(b.allocation_oil_pct) if b.allocation_oil_pct is not None else None,
                allocation_meal_pct=str(b.allocation_meal_pct) if b.allocation_meal_pct is not None else None,
                heap_location=b.heap_location,
                logistics_note=b.logistics_note,
            )
            for b in balances
        ],
        created_at=profile.created_at.isoformat() if profile.created_at else None,
        updated_at=profile.updated_at.isoformat() if profile.updated_at else None,
    )


def _replace_children(db: Session, tenant_id: str, profile_id: str, payload: RapsProfileIn):
    db.query(NawaroRapsCertificate).filter(
        NawaroRapsCertificate.profile_id == profile_id,
        NawaroRapsCertificate.tenant_id == tenant_id,
    ).delete()
    db.query(NawaroRapsBalance).filter(
        NawaroRapsBalance.profile_id == profile_id,
        NawaroRapsBalance.tenant_id == tenant_id,
    ).delete()

    for cert in payload.certificates:
        db.add(
            NawaroRapsCertificate(
                id=uuid7(),
                profile_id=profile_id,
                scheme=cert.scheme,
                certificate_number=cert.certificate_number,
                chain_stage=cert.chain_stage,
                valid_from=cert.valid_from,
                valid_until=cert.valid_until,
                issuer=cert.issuer,
                status=cert.status,
                tenant_id=tenant_id,
            )
        )

    for bal in payload.balances:
        db.add(
            NawaroRapsBalance(
                id=uuid7(),
                profile_id=profile_id,
                booking_period=bal.booking_period,
                input_seed_tons=_to_decimal(bal.input_seed_tons) or Decimal('0'),
                output_oil_tons=_to_decimal(bal.output_oil_tons) or Decimal('0'),
                output_meal_tons=_to_decimal(bal.output_meal_tons) or Decimal('0'),
                output_other_tons=_to_decimal(bal.output_other_tons) or Decimal('0'),
                allocation_oil_pct=_to_decimal(bal.allocation_oil_pct),
                allocation_meal_pct=_to_decimal(bal.allocation_meal_pct),
                heap_location=bal.heap_location,
                logistics_note=bal.logistics_note,
                tenant_id=tenant_id,
            )
        )


def _month_window(period: str | None) -> tuple[str, datetime, datetime]:
    if period:
        try:
            year_str, month_str = period.split("-", 1)
            year = int(year_str)
            month = int(month_str)
            if month < 1 or month > 12:
                raise ValueError()
        except ValueError as exc:
            raise HTTPException(status_code=422, detail="period must be YYYY-MM") from exc
    else:
        now = datetime.now(tz=timezone.utc)
        year = now.year
        month = now.month

    start = datetime(year, month, 1, tzinfo=timezone.utc)
    if month == 12:
        end = datetime(year + 1, 1, 1, tzinfo=timezone.utc)
    else:
        end = datetime(year, month + 1, 1, tzinfo=timezone.utc)
    return f"{year:04d}-{month:02d}", start, end


def _derive_balance(
    db: Session,
    *,
    tenant_id: str,
    profile: NawaroRapsProfile,
    period: str | None,
) -> tuple[RapsBalanceIn, str, str, str]:
    if not profile.article_id:
        raise HTTPException(
            status_code=400,
            detail="profile.article_id is required for auto-derivation from operational data",
        )

    period_normalized, start, end = _month_window(period)

    ticket_kg = (
        db.query(func.coalesce(func.sum(WeighingTicket.net_weight), 0))
        .join(AgrarContract, WeighingTicket.contract_id == AgrarContract.id)
        .filter(
            WeighingTicket.tenant_id == tenant_id,
            AgrarContract.tenant_id == tenant_id,
            AgrarContract.article_id == profile.article_id,
            WeighingTicket.weighing_date >= start,
            WeighingTicket.weighing_date < end,
            WeighingTicket.net_weight.isnot(None),
        )
        .scalar()
    )

    settlement_kg = (
        db.query(func.coalesce(func.sum(AgrarSettlement.billing_quantity_kg), 0))
        .filter(
            AgrarSettlement.tenant_id == tenant_id,
            AgrarSettlement.article_id == profile.article_id,
            AgrarSettlement.created_at >= start,
            AgrarSettlement.created_at < end,
        )
        .scalar()
    )

    ticket_kg_dec = Decimal(str(ticket_kg or 0))
    settlement_kg_dec = Decimal(str(settlement_kg or 0))
    source_kg = ticket_kg_dec if ticket_kg_dec > 0 else settlement_kg_dec
    input_tons = (source_kg / Decimal("1000")).quantize(Decimal("0.001"))

    # Inference: 40/60 split for rapeseed processing when no explicit production-booking exists.
    oil_tons = (input_tons * Decimal("0.400")).quantize(Decimal("0.001"))
    meal_tons = (input_tons * Decimal("0.600")).quantize(Decimal("0.001"))
    other_tons = Decimal("0.000")

    derived = RapsBalanceIn(
        booking_period=period_normalized,
        input_seed_tons=str(input_tons),
        output_oil_tons=str(oil_tons),
        output_meal_tons=str(meal_tons),
        output_other_tons=str(other_tons),
        allocation_oil_pct="40.00",
        allocation_meal_pct="60.00",
        heap_location=None,
        logistics_note=f"Auto-derived from weighing_tickets/agrar_settlements for {period_normalized}",
    )

    return derived, str(ticket_kg_dec), str(settlement_kg_dec), str(input_tons)


@router.get('/raps-profiles', response_model=list[RapsProfileOut], summary="Raps profiles auflisten")
async def list_raps_profiles(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    items = (
        db.query(NawaroRapsProfile)
        .filter(NawaroRapsProfile.tenant_id == tenant_id)
        .order_by(NawaroRapsProfile.created_at.desc())
        .limit(200)
        .all()
    )
    return [_profile_out(db, item) for item in items]


@router.get('/raps-profiles/{profile_id}', response_model=RapsProfileOut, summary="Raps profile abrufen")
async def get_raps_profile(
    profile_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    item = (
        db.query(NawaroRapsProfile)
        .filter(NawaroRapsProfile.id == profile_id, NawaroRapsProfile.tenant_id == tenant_id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail='Raps profile not found')
    return _profile_out(db, item)


@router.post('/raps-profiles', response_model=RapsProfileOut, status_code=201, summary="Raps profile anlegen")
async def create_raps_profile(
    payload: RapsProfileIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    _validate_balances(payload)
    item = NawaroRapsProfile(
        id=uuid7(),
        article_id=payload.article_id,
        article_number=payload.article_number,
        article_name=payload.article_name,
        harvest_year=payload.harvest_year,
        usage_food_pct=_to_decimal(payload.usage_food_pct) or Decimal('0'),
        usage_feed_pct=_to_decimal(payload.usage_feed_pct) or Decimal('0'),
        usage_energy_pct=_to_decimal(payload.usage_energy_pct) or Decimal('0'),
        usage_material_pct=_to_decimal(payload.usage_material_pct) or Decimal('0'),
        thg_gco2eq_mj=_to_decimal(payload.thg_gco2eq_mj),
        yield_dt_per_ha=_to_decimal(payload.yield_dt_per_ha),
        notes=payload.notes,
        tenant_id=tenant_id,
    )
    db.add(item)
    db.flush()
    _replace_children(db, tenant_id, item.id, payload)
    db.commit()
    db.refresh(item)
    return _profile_out(db, item)


@router.put('/raps-profiles/{profile_id}', response_model=RapsProfileOut, summary="Raps profile aktualisieren")
async def update_raps_profile(
    profile_id: str,
    payload: RapsProfileIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    _validate_balances(payload)
    item = (
        db.query(NawaroRapsProfile)
        .filter(NawaroRapsProfile.id == profile_id, NawaroRapsProfile.tenant_id == tenant_id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail='Raps profile not found')

    item.article_id = payload.article_id
    item.article_number = payload.article_number
    item.article_name = payload.article_name
    item.harvest_year = payload.harvest_year
    item.usage_food_pct = _to_decimal(payload.usage_food_pct) or Decimal('0')
    item.usage_feed_pct = _to_decimal(payload.usage_feed_pct) or Decimal('0')
    item.usage_energy_pct = _to_decimal(payload.usage_energy_pct) or Decimal('0')
    item.usage_material_pct = _to_decimal(payload.usage_material_pct) or Decimal('0')
    item.thg_gco2eq_mj = _to_decimal(payload.thg_gco2eq_mj)
    item.yield_dt_per_ha = _to_decimal(payload.yield_dt_per_ha)
    item.notes = payload.notes

    _replace_children(db, tenant_id, item.id, payload)
    db.commit()
    db.refresh(item)
    return _profile_out(db, item)


@router.delete('/raps-profiles/{profile_id}', response_model=CompatFlexOut, summary="Raps profile löschen")
async def delete_raps_profile(
    profile_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    item = (
        db.query(NawaroRapsProfile)
        .filter(NawaroRapsProfile.id == profile_id, NawaroRapsProfile.tenant_id == tenant_id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail='Raps profile not found')

    db.query(NawaroRapsCertificate).filter(
        NawaroRapsCertificate.profile_id == profile_id,
        NawaroRapsCertificate.tenant_id == tenant_id,
    ).delete()
    db.query(NawaroRapsBalance).filter(
        NawaroRapsBalance.profile_id == profile_id,
        NawaroRapsBalance.tenant_id == tenant_id,
    ).delete()
    db.delete(item)
    db.commit()
    return {'ok': True, 'id': profile_id}


@router.post('/raps-profiles/{profile_id}/derive-from-ops', response_model=RapsDeriveOut, summary="Raps profile from ops derive")
async def derive_raps_profile_from_ops(
    profile_id: str,
    period: str | None = None,
    apply_update: bool = True,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    item = (
        db.query(NawaroRapsProfile)
        .filter(NawaroRapsProfile.id == profile_id, NawaroRapsProfile.tenant_id == tenant_id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail='Raps profile not found')

    derived_balance, ticket_kg, settlement_kg, source_input_tons = _derive_balance(
        db,
        tenant_id=tenant_id,
        profile=item,
        period=period,
    )

    payload = RapsProfileIn(
        article_id=item.article_id,
        article_number=item.article_number,
        article_name=item.article_name,
        harvest_year=item.harvest_year,
        usage_food_pct=str(item.usage_food_pct),
        usage_feed_pct=str(item.usage_feed_pct),
        usage_energy_pct=str(item.usage_energy_pct),
        usage_material_pct=str(item.usage_material_pct),
        thg_gco2eq_mj=str(item.thg_gco2eq_mj) if item.thg_gco2eq_mj is not None else None,
        yield_dt_per_ha=str(item.yield_dt_per_ha) if item.yield_dt_per_ha is not None else None,
        notes=item.notes,
        certificates=[
            RapsCertificateIn(
                scheme=c.scheme,
                certificate_number=c.certificate_number,
                chain_stage=c.chain_stage,
                valid_from=c.valid_from,
                valid_until=c.valid_until,
                issuer=c.issuer,
                status=c.status,
            )
            for c in db.query(NawaroRapsCertificate).filter(
                NawaroRapsCertificate.profile_id == item.id,
                NawaroRapsCertificate.tenant_id == tenant_id,
            ).all()
        ],
        balances=[derived_balance],
    )
    _validate_balances(payload)

    if apply_update:
        _replace_children(db, tenant_id, item.id, payload)
        db.commit()
        db.refresh(item)

    messages = []
    if Decimal(source_input_tons) <= Decimal("0"):
        messages.append("No operational quantities found for selected period")
    if Decimal(ticket_kg) == Decimal("0"):
        messages.append("No weighing ticket data used; fallback to settlements")
    if Decimal(settlement_kg) == Decimal("0"):
        messages.append("No settlement data available in selected period")

    return RapsDeriveOut(
        profile=_profile_out(db, item),
        period=derived_balance.booking_period or "",
        source_tickets_kg=ticket_kg,
        source_settlements_kg=settlement_kg,
        source_input_tons=source_input_tons,
        plausibility_messages=messages,
    )
