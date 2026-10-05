"""Tenant-aware read service for feeding nutrient and unit reference data."""
from __future__ import annotations

from decimal import Decimal
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.agrar.rations.reference_data import (
    BasisValueKind,
    MatterBasis,
    RoundingMode,
    convert_basis,
    round_decimal,
)


class RationsReferenceDataService:
    def __init__(self, db: Session, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id

    def list_nutrients(self, *, include_inactive: bool = False) -> list[dict[str, Any]]:
        rows = self.db.execute(text("""
          SELECT DISTINCT ON (code)
            id,tenant_id,code,display_name,canonical_unit_code,default_basis,value_kind,
            minimum_value,maximum_value,sort_order,revision,source,active,updated_at
          FROM domain_agrar.feeding_nutrient_definitions
          WHERE (tenant_id IS NULL OR tenant_id=:tenant_id)
            AND (:include_inactive OR active=TRUE)
          ORDER BY code,(tenant_id IS NOT NULL) DESC,revision DESC
        """), {"tenant_id": self.tenant_id, "include_inactive": include_inactive}).mappings().all()
        return [dict(row) for row in sorted(rows, key=lambda item: (item["sort_order"], item["code"]))]

    def list_units(self, *, include_inactive: bool = False) -> list[dict[str, Any]]:
        rows = self.db.execute(text("""
          SELECT DISTINCT ON (code)
            id,tenant_id,code,display_name,dimension,factor_to_base,precision,
            revision,source,active,updated_at
          FROM domain_agrar.feeding_unit_definitions
          WHERE (tenant_id IS NULL OR tenant_id=:tenant_id)
            AND (:include_inactive OR active=TRUE)
          ORDER BY code,(tenant_id IS NOT NULL) DESC,revision DESC
        """), {"tenant_id": self.tenant_id, "include_inactive": include_inactive}).mappings().all()
        return [dict(row) for row in sorted(rows, key=lambda item: (item["dimension"], item["code"]))]

    @staticmethod
    def convert_matter_basis(*, value: Decimal, from_basis: MatterBasis,
                             to_basis: MatterBasis, dry_matter_pct: Decimal,
                             kind: BasisValueKind, precision: int,
                             rounding_mode: RoundingMode) -> dict[str, Any]:
        unrounded = convert_basis(value, from_basis, to_basis, dry_matter_pct, kind)
        return {
            "value": round_decimal(unrounded, precision, rounding_mode),
            "unrounded_value": unrounded,
            "from_basis": from_basis,
            "to_basis": to_basis,
            "dry_matter_pct": dry_matter_pct,
            "kind": kind,
            "precision": precision,
            "rounding_mode": rounding_mode,
        }
