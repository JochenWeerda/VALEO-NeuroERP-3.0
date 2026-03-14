from __future__ import annotations

from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.infrastructure.models import DryingRuleFactorRange, DryingRuleLookupRow, DryingRuleSet
from modules.agrar.services.drying_rule_engine import (
    DryingFactorRange,
    DryingLookupRow,
    DryingRuleRepository,
    DryingRuleSet as ServiceDryingRuleSet,
)


class DbDryingRuleRepo(DryingRuleRepository):
    def __init__(self, db: Session, *, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id

    def find_rule_set(self, *, crop_code: str, site_id: Optional[str], calc_date, contract_id: Optional[str] = None, customer_id: Optional[str] = None) -> ServiceDryingRuleSet:
        def _base_q():
            return (
                self.db.query(DryingRuleSet)
                .filter(DryingRuleSet.tenant_id == self.tenant_id)
                .filter(DryingRuleSet.crop_code == crop_code)
                .filter(DryingRuleSet.is_active == True)  # noqa: E712
                .filter((DryingRuleSet.valid_from.is_(None)) | (DryingRuleSet.valid_from <= calc_date))
                .filter((DryingRuleSet.valid_to.is_(None)) | (DryingRuleSet.valid_to >= calc_date))
            )

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
            raise HTTPException(status_code=404, detail=f"No drying rule set found for crop_code={crop_code} (site_id={site_id}, contract_id={contract_id}, customer_id={customer_id})")
        return self._row_to_rule_set(row)

    def _row_to_rule_set(self, row) -> ServiceDryingRuleSet:
        lookup_rows = [
            DryingLookupRow(
                moisture_pct=float(entry.moisture_pct),
                deduction_pct=float(entry.deduction_pct),
            )
            for entry in (
                self.db.query(DryingRuleLookupRow)
                .filter(DryingRuleLookupRow.rule_set_id == row.id)
                .order_by(DryingRuleLookupRow.moisture_pct.asc())
                .all()
            )
        ]
        factor_ranges = [
            DryingFactorRange(
                moisture_from_pct=float(entry.moisture_from_pct),
                moisture_to_pct=float(entry.moisture_to_pct) if entry.moisture_to_pct is not None else None,
                factor=float(entry.factor),
            )
            for entry in (
                self.db.query(DryingRuleFactorRange)
                .filter(DryingRuleFactorRange.rule_set_id == row.id)
                .order_by(DryingRuleFactorRange.moisture_from_pct.asc())
                .all()
            )
        ]
        return ServiceDryingRuleSet(
            id=str(row.id),
            version=int(row.version),
            tenant_id=str(row.tenant_id),
            crop_code=str(row.crop_code),
            site_id=str(row.site_id) if row.site_id is not None else None,
            contract_id=str(row.contract_id) if row.contract_id is not None else None,
            valid_from=row.valid_from,
            valid_to=row.valid_to,
            target_moisture_pct=float(row.target_moisture_pct),
            method=str(row.method),
            deduction_mode=str(row.deduction_mode),
            fee_mode=str(row.fee_mode),
            fee_rate_eur_per_ton=float(row.fee_rate_eur_per_ton) if row.fee_rate_eur_per_ton is not None else None,
            fee_free_moisture_pct=float(row.fee_free_moisture_pct) if row.fee_free_moisture_pct is not None else None,
            fee_per_pct_point_eur_per_ton=float(row.fee_per_pct_point_eur_per_ton) if row.fee_per_pct_point_eur_per_ton is not None else None,
            rounding_mode=str(row.rounding_mode),
            lookup_rows=lookup_rows,
            factor_ranges=factor_ranges,
        )
