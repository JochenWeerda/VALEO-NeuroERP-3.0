"""SQLAlchemy-backed DryingRuleRepository implementation."""

from __future__ import annotations

from decimal import Decimal
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.infrastructure.models import DryingRuleFactorRange, DryingRuleLookupRow, DryingRuleSet
from modules.agrar.services.drying_rule_engine import (
    DryingFactorRange as _DryingFactorRange,
    DryingLookupRow as _DryingLookupRow,
    DryingRuleRepository as _DryingRuleRepository,
    DryingRuleSet as _DryingRuleSet,
)


class DbDryingRuleRepo(_DryingRuleRepository):
    """DB-backed implementation of DryingRuleRepository used by compute_settlement()."""

    def __init__(self, db: Session, *, tenant_id: str) -> None:
        self.db = db
        self.tenant_id = tenant_id

    def find_rule_set(
        self,
        *,
        crop_code: str,
        site_id: Optional[str],
        calc_date,
        contract_id: Optional[str] = None,
        customer_id: Optional[str] = None,
    ) -> _DryingRuleSet:
        """
        Find rule set with priority:
        1. Customer-specific rule (if customer_id provided)
        2. Contract-specific rule (if contract_id provided)
        3. Site-specific rule
        4. Global rule (site_id=NULL)
        """

        def _base_q():
            return (
                self.db.query(DryingRuleSet)
                .filter(DryingRuleSet.tenant_id == self.tenant_id)
                .filter(DryingRuleSet.crop_code == crop_code)
                .filter(DryingRuleSet.is_active == True)  # noqa: E712
                .filter((DryingRuleSet.valid_from.is_(None)) | (DryingRuleSet.valid_from <= calc_date))
                .filter((DryingRuleSet.valid_to.is_(None)) | (DryingRuleSet.valid_to >= calc_date))
            )

        # 1. Customer-specific rule (höchste Priorität)
        if customer_id:
            row = (
                _base_q()
                .filter(DryingRuleSet.customer_id == customer_id)
                .filter(DryingRuleSet.is_customer_specific == True)  # noqa: E712
                .order_by(DryingRuleSet.valid_from.desc().nullslast(), DryingRuleSet.version.desc())
                .first()
            )
            if row:
                return self._row_to_rule_set(row)

        # 2. Contract-specific rule
        if contract_id:
            row = (
                _base_q()
                .filter(DryingRuleSet.contract_id == contract_id)
                .filter(DryingRuleSet.is_customer_specific == False)  # noqa: E712
                .order_by(DryingRuleSet.valid_from.desc().nullslast(), DryingRuleSet.version.desc())
                .first()
            )
            if row:
                return self._row_to_rule_set(row)

        # 3. Site-specific rule (nur allgemeingültige)
        row = None
        if site_id is not None:
            row = (
                _base_q()
                .filter(DryingRuleSet.site_id == site_id)
                .filter(DryingRuleSet.contract_id.is_(None))
                .filter(DryingRuleSet.is_customer_specific == False)  # noqa: E712
                .order_by(DryingRuleSet.valid_from.desc().nullslast(), DryingRuleSet.version.desc())
                .first()
            )
        # 4. Global rule (fallback)
        if row is None:
            row = (
                _base_q()
                .filter(DryingRuleSet.site_id.is_(None))
                .filter(DryingRuleSet.contract_id.is_(None))
                .filter(DryingRuleSet.is_customer_specific == False)  # noqa: E712
                .order_by(DryingRuleSet.valid_from.desc().nullslast(), DryingRuleSet.version.desc())
                .first()
            )
        if not row:
            raise HTTPException(
                status_code=404,
                detail=(
                    f"No drying rule set found for crop_code={crop_code}"
                    f" (site_id={site_id}, contract_id={contract_id}, customer_id={customer_id})"
                ),
            )
        return self._row_to_rule_set(row)

    def _row_to_rule_set(self, row) -> _DryingRuleSet:
        return _DryingRuleSet(
            id=row.id,
            version=int(row.version),
            crop_code=row.crop_code,
            site_id=row.site_id,
            valid_from=row.valid_from,
            valid_to=row.valid_to,
            method=row.method,  # type: ignore[arg-type]
            base_moisture_pct=Decimal(str(row.base_moisture_pct)),
            rounding_mode=row.rounding_mode,  # type: ignore[arg-type]
            clamp_mode=row.clamp_mode,  # type: ignore[arg-type]
            min_moisture_pct=Decimal(str(row.min_moisture_pct)),
            max_moisture_pct=Decimal(str(row.max_moisture_pct)),
            start_threshold_moisture_pct=(
                Decimal(str(row.start_threshold_moisture_pct))
                if row.start_threshold_moisture_pct is not None
                else None
            ),
            fee_basis=row.fee_basis,  # type: ignore[arg-type]
        )

    def list_lookup_rows(self, *, rule_set_id: str) -> list[_DryingLookupRow]:
        rows = (
            self.db.query(DryingRuleLookupRow)
            .filter(DryingRuleLookupRow.rule_set_id == rule_set_id)
            .order_by(DryingRuleLookupRow.moisture_pct.asc())
            .all()
        )
        return [
            _DryingLookupRow(
                moisture_pct=Decimal(str(r.moisture_pct)),
                entzug_pct_points=Decimal(str(r.entzug_pct_points)),
                loss_pct=Decimal(str(r.loss_pct)),
                fee_value=Decimal(str(r.fee_value)) if r.fee_value is not None else None,
                fee_unit=r.fee_unit,  # type: ignore[arg-type]
            )
            for r in rows
        ]

    def list_factor_ranges(self, *, rule_set_id: str) -> list[_DryingFactorRange]:
        rows = (
            self.db.query(DryingRuleFactorRange)
            .filter(DryingRuleFactorRange.rule_set_id == rule_set_id)
            .order_by(DryingRuleFactorRange.from_moisture_incl.asc())
            .all()
        )
        return [
            _DryingFactorRange(
                from_moisture_incl=Decimal(str(r.from_moisture_incl)),
                to_moisture_incl=Decimal(str(r.to_moisture_incl)),
                factor=Decimal(str(r.factor)),
            )
            for r in rows
        ]
