"""Service layer for Agrar Drying Rule Sets, Lookup Rows, and Factor Ranges."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, EntityNotFoundError, ValidationFailedError
from app.core.uuid7 import uuid7
from app.infrastructure.models import DryingRuleFactorRange, DryingRuleLookupRow, DryingRuleSet


class DryingRuleService:
    """CRUD for DryingRuleSet + child entities (Lookup Rows, Factor Ranges)."""

    def __init__(self, db: Session, tenant_id: str) -> None:
        self.db = db
        self.tenant_id = tenant_id

    # ── DryingRuleSet ─────────────────────────────────────────────────────────

    def _get_rule_or_404(self, rule_id: str) -> DryingRuleSet:
        rule = self.db.query(DryingRuleSet).filter(
            DryingRuleSet.id == rule_id,
            DryingRuleSet.tenant_id == self.tenant_id,
        ).first()
        if not rule:
            raise EntityNotFoundError("DryingRuleSet", rule_id)
        return rule

    def list_rules(
        self,
        crop_code: Optional[str] = None,
        contract_id: Optional[str] = None,
        customer_id: Optional[str] = None,
        is_customer_specific: Optional[bool] = None,
    ) -> list[DryingRuleSet]:
        q = self.db.query(DryingRuleSet).filter(DryingRuleSet.tenant_id == self.tenant_id)
        if crop_code:
            q = q.filter(DryingRuleSet.crop_code == crop_code)
        if contract_id:
            q = q.filter(DryingRuleSet.contract_id == contract_id)
        if customer_id:
            q = q.filter(DryingRuleSet.customer_id == customer_id)
        if is_customer_specific is not None:
            q = q.filter(DryingRuleSet.is_customer_specific == is_customer_specific)
        return q.order_by(DryingRuleSet.crop_code.asc(), DryingRuleSet.version.desc()).all()

    def get_rule(self, rule_id: str) -> DryingRuleSet:
        return self._get_rule_or_404(rule_id)

    def create_rule(self, payload: Any, user_id: str) -> DryingRuleSet:
        valid_from_date = datetime.fromisoformat(payload.valid_from).date() if payload.valid_from else None
        valid_to_date = datetime.fromisoformat(payload.valid_to).date() if payload.valid_to else None
        rule = DryingRuleSet(
            id=uuid7(),
            tenant_id=self.tenant_id,
            crop_code=payload.crop_code,
            site_id=payload.site_id,
            valid_from=valid_from_date,
            valid_to=valid_to_date,
            version=1,
            is_active=True,
            method=payload.method,
            base_moisture_pct=Decimal(str(payload.base_moisture_pct)),
            rounding_mode=payload.rounding_mode,
            clamp_mode=payload.clamp_mode,
            min_moisture_pct=Decimal(str(payload.min_moisture_pct)),
            max_moisture_pct=Decimal(str(payload.max_moisture_pct)),
            start_threshold_moisture_pct=(
                Decimal(str(payload.start_threshold_moisture_pct))
                if payload.start_threshold_moisture_pct is not None
                else None
            ),
            fee_basis=payload.fee_basis,
            created_by=user_id,
            contract_id=payload.contract_id,
            customer_id=payload.customer_id,
            is_customer_specific=payload.is_customer_specific,
            justification=payload.justification,
            document_id=payload.document_id,
        )
        self.db.add(rule)
        self.db.commit()
        self.db.refresh(rule)
        return rule

    def update_rule(self, rule_id: str, payload: Any, user_id: str) -> DryingRuleSet:
        rule = self._get_rule_or_404(rule_id)
        needs_new_version = any([
            payload.method is not None and payload.method != rule.method,
            payload.base_moisture_pct is not None and Decimal(str(payload.base_moisture_pct)) != rule.base_moisture_pct,
            payload.rounding_mode is not None and payload.rounding_mode != rule.rounding_mode,
            payload.clamp_mode is not None and payload.clamp_mode != rule.clamp_mode,
            payload.min_moisture_pct is not None and Decimal(str(payload.min_moisture_pct)) != rule.min_moisture_pct,
            payload.max_moisture_pct is not None and Decimal(str(payload.max_moisture_pct)) != rule.max_moisture_pct,
            payload.start_threshold_moisture_pct is not None and (
                rule.start_threshold_moisture_pct is None
                or Decimal(str(payload.start_threshold_moisture_pct)) != rule.start_threshold_moisture_pct
            ),
            payload.fee_basis is not None and payload.fee_basis != rule.fee_basis,
        ])
        if needs_new_version:
            rule.is_active = False
            self.db.flush()
            new_rule = DryingRuleSet(
                id=uuid7(),
                tenant_id=self.tenant_id,
                crop_code=rule.crop_code,
                site_id=payload.site_id if payload.site_id is not None else rule.site_id,
                valid_from=(
                    datetime.fromisoformat(payload.valid_from).date() if payload.valid_from else rule.valid_from
                ),
                valid_to=(
                    datetime.fromisoformat(payload.valid_to).date() if payload.valid_to else rule.valid_to
                ),
                version=rule.version + 1,
                is_active=True,
                method=payload.method if payload.method is not None else rule.method,
                base_moisture_pct=(
                    Decimal(str(payload.base_moisture_pct)) if payload.base_moisture_pct is not None else rule.base_moisture_pct
                ),
                rounding_mode=payload.rounding_mode if payload.rounding_mode is not None else rule.rounding_mode,
                clamp_mode=payload.clamp_mode if payload.clamp_mode is not None else rule.clamp_mode,
                min_moisture_pct=(
                    Decimal(str(payload.min_moisture_pct)) if payload.min_moisture_pct is not None else rule.min_moisture_pct
                ),
                max_moisture_pct=(
                    Decimal(str(payload.max_moisture_pct)) if payload.max_moisture_pct is not None else rule.max_moisture_pct
                ),
                start_threshold_moisture_pct=(
                    Decimal(str(payload.start_threshold_moisture_pct))
                    if payload.start_threshold_moisture_pct is not None
                    else rule.start_threshold_moisture_pct
                ),
                fee_basis=payload.fee_basis if payload.fee_basis is not None else rule.fee_basis,
                created_by=user_id,
                contract_id=payload.contract_id if payload.contract_id is not None else rule.contract_id,
                customer_id=payload.customer_id if payload.customer_id is not None else rule.customer_id,
                is_customer_specific=(
                    payload.is_customer_specific if payload.is_customer_specific is not None else rule.is_customer_specific
                ),
                justification=payload.justification if payload.justification is not None else rule.justification,
                document_id=payload.document_id if payload.document_id is not None else rule.document_id,
            )
            self.db.add(new_rule)
            self.db.commit()
            self.db.refresh(new_rule)
            return new_rule
        # metadata-only update
        if payload.site_id is not None:
            rule.site_id = payload.site_id
        if payload.valid_from is not None:
            rule.valid_from = datetime.fromisoformat(payload.valid_from).date()
        if payload.valid_to is not None:
            rule.valid_to = datetime.fromisoformat(payload.valid_to).date()
        if payload.is_active is not None:
            rule.is_active = payload.is_active
        if payload.contract_id is not None:
            rule.contract_id = payload.contract_id
        if payload.customer_id is not None:
            rule.customer_id = payload.customer_id
        if payload.is_customer_specific is not None:
            rule.is_customer_specific = payload.is_customer_specific
        if payload.justification is not None:
            rule.justification = payload.justification
        if payload.document_id is not None:
            rule.document_id = payload.document_id
        rule.updated_by = user_id
        self.db.commit()
        self.db.refresh(rule)
        return rule

    def delete_rule(self, rule_id: str, user_id: str) -> None:
        rule = self._get_rule_or_404(rule_id)
        rule.is_active = False
        rule.updated_by = user_id
        self.db.commit()

    def get_rule_download_data(self, rule_id: str) -> dict:
        rule = self._get_rule_or_404(rule_id)
        data: dict = {
            "rule_id": rule.id,
            "crop_code": rule.crop_code,
            "version": int(rule.version),
            "valid_from": rule.valid_from.isoformat() if rule.valid_from else None,
            "valid_to": rule.valid_to.isoformat() if rule.valid_to else None,
            "document_id": rule.document_id,
            "method": rule.method,
            "base_moisture_pct": float(rule.base_moisture_pct),
        }
        if rule.document_id:
            data["dms_download_url"] = f"/api/v1/dms/documents/{rule.document_id}/download"
        return data

    # ── Lookup Rows ───────────────────────────────────────────────────────────

    def _get_lookup_row_or_404(self, row_id: str) -> DryingRuleLookupRow:
        row = self.db.query(DryingRuleLookupRow).filter(DryingRuleLookupRow.id == row_id).first()
        if not row:
            raise EntityNotFoundError("DryingRuleLookupRow", row_id)
        self._get_rule_or_404(row.rule_set_id)  # tenant check
        return row

    def list_lookup_rows(self, rule_id: str) -> list[DryingRuleLookupRow]:
        self._get_rule_or_404(rule_id)
        return (
            self.db.query(DryingRuleLookupRow)
            .filter(DryingRuleLookupRow.rule_set_id == rule_id)
            .order_by(DryingRuleLookupRow.moisture_pct.asc())
            .all()
        )

    def create_lookup_row(self, payload: Any) -> DryingRuleLookupRow:
        rule = self._get_rule_or_404(payload.rule_set_id)
        if rule.method != "LOOKUP_TABLE":
            raise ValidationFailedError("Rule set method must be LOOKUP_TABLE")
        moisture = Decimal(str(round(payload.moisture_pct, 1)))
        existing = self.db.query(DryingRuleLookupRow).filter(
            DryingRuleLookupRow.rule_set_id == payload.rule_set_id,
            DryingRuleLookupRow.moisture_pct == moisture,
        ).first()
        if existing:
            raise ConflictError(f"Lookup row for moisture {payload.moisture_pct} already exists")
        row = DryingRuleLookupRow(
            id=uuid7(),
            rule_set_id=payload.rule_set_id,
            moisture_pct=moisture,
            entzug_pct_points=Decimal(str(payload.entzug_pct_points)),
            loss_pct=Decimal(str(payload.loss_pct)),
            fee_value=Decimal(str(payload.fee_value)) if payload.fee_value is not None else None,
            fee_unit=payload.fee_unit,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row

    def update_lookup_row(self, row_id: str, payload: Any) -> DryingRuleLookupRow:
        row = self._get_lookup_row_or_404(row_id)
        if payload.moisture_pct is not None:
            new_moisture = Decimal(str(round(payload.moisture_pct, 1)))
            conflict = self.db.query(DryingRuleLookupRow).filter(
                DryingRuleLookupRow.rule_set_id == row.rule_set_id,
                DryingRuleLookupRow.moisture_pct == new_moisture,
                DryingRuleLookupRow.id != row_id,
            ).first()
            if conflict:
                raise ConflictError(f"Lookup row for moisture {payload.moisture_pct} already exists")
            row.moisture_pct = new_moisture
        if payload.entzug_pct_points is not None:
            row.entzug_pct_points = Decimal(str(payload.entzug_pct_points))
        if payload.loss_pct is not None:
            row.loss_pct = Decimal(str(payload.loss_pct))
        if payload.fee_value is not None:
            row.fee_value = Decimal(str(payload.fee_value))
        if payload.fee_unit is not None:
            row.fee_unit = payload.fee_unit
        self.db.commit()
        self.db.refresh(row)
        return row

    def delete_lookup_row(self, row_id: str) -> None:
        row = self._get_lookup_row_or_404(row_id)
        self.db.delete(row)
        self.db.commit()

    # ── Factor Ranges ─────────────────────────────────────────────────────────

    def _get_factor_range_or_404(self, range_id: str) -> DryingRuleFactorRange:
        r = self.db.query(DryingRuleFactorRange).filter(DryingRuleFactorRange.id == range_id).first()
        if not r:
            raise EntityNotFoundError("DryingRuleFactorRange", range_id)
        self._get_rule_or_404(r.rule_set_id)  # tenant check
        return r

    def list_factor_ranges(self, rule_id: str) -> list[DryingRuleFactorRange]:
        self._get_rule_or_404(rule_id)
        return (
            self.db.query(DryingRuleFactorRange)
            .filter(DryingRuleFactorRange.rule_set_id == rule_id)
            .order_by(DryingRuleFactorRange.from_moisture_incl.asc())
            .all()
        )

    def create_factor_range(self, payload: Any) -> DryingRuleFactorRange:
        rule = self._get_rule_or_404(payload.rule_set_id)
        if rule.method != "FACTOR_FROM_BASE":
            raise ValidationFailedError("Rule set method must be FACTOR_FROM_BASE")
        from_m = Decimal(str(round(payload.from_moisture_incl, 1)))
        to_m = Decimal(str(round(payload.to_moisture_incl, 1)))
        existing = self.db.query(DryingRuleFactorRange).filter(
            DryingRuleFactorRange.rule_set_id == payload.rule_set_id
        ).all()
        for r in existing:
            if not (to_m < Decimal(str(r.from_moisture_incl)) or from_m > Decimal(str(r.to_moisture_incl))):
                raise ConflictError(
                    f"Factor range overlaps with existing range ({r.from_moisture_incl}-{r.to_moisture_incl})"
                )
        range_obj = DryingRuleFactorRange(
            id=uuid7(),
            rule_set_id=payload.rule_set_id,
            from_moisture_incl=from_m,
            to_moisture_incl=to_m,
            factor=Decimal(str(payload.factor)),
        )
        self.db.add(range_obj)
        self.db.commit()
        self.db.refresh(range_obj)
        return range_obj

    def update_factor_range(self, range_id: str, payload: Any) -> DryingRuleFactorRange:
        range_obj = self._get_factor_range_or_404(range_id)
        from_m = (
            Decimal(str(round(payload.from_moisture_incl, 1)))
            if payload.from_moisture_incl is not None
            else range_obj.from_moisture_incl
        )
        to_m = (
            Decimal(str(round(payload.to_moisture_incl, 1)))
            if payload.to_moisture_incl is not None
            else range_obj.to_moisture_incl
        )
        if payload.from_moisture_incl is not None or payload.to_moisture_incl is not None:
            existing = self.db.query(DryingRuleFactorRange).filter(
                DryingRuleFactorRange.rule_set_id == range_obj.rule_set_id,
                DryingRuleFactorRange.id != range_id,
            ).all()
            for r in existing:
                if not (to_m < r.from_moisture_incl or from_m > r.to_moisture_incl):
                    raise ConflictError(
                        f"Factor range overlaps with existing range ({r.from_moisture_incl}-{r.to_moisture_incl})"
                    )
        if payload.from_moisture_incl is not None:
            range_obj.from_moisture_incl = from_m
        if payload.to_moisture_incl is not None:
            range_obj.to_moisture_incl = to_m
        if payload.factor is not None:
            range_obj.factor = Decimal(str(payload.factor))
        self.db.commit()
        self.db.refresh(range_obj)
        return range_obj

    def delete_factor_range(self, range_id: str) -> None:
        range_obj = self._get_factor_range_or_404(range_id)
        self.db.delete(range_obj)
        self.db.commit()
