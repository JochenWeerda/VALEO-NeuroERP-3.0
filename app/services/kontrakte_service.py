from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.uuid7 import uuid7
from app.domains.operations.models import (
    KonAuditLog,
    KonContract,
    KonContractLine,
    KonContractMovement,
    KonNumberRange,
)


class KontraktSecurityService:
    ROLE_LESEN = "KONTRAKT_LESEN"
    ROLE_BEARBEITEN = "KONTRAKT_BEARBEITEN"
    ROLE_LOESCHEN = "KONTRAKT_LOESCHEN"
    ROLE_ADMIN = "KONTRAKT_ADMIN"

    @staticmethod
    def has_any_role(user_roles: list[str], *needed: str) -> bool:
        roles = set(user_roles or [])
        return bool(roles.intersection(set(needed)))


class KontraktValidationService:
    ALLOWED_TYPES = {"EINKAUF", "ZUKAUF", "VERKAUF"}
    ALLOWED_STATUS = {"OFFEN", "ERLEDIGT", "STORNIERT"}
    ALLOWED_QTY_TYPES = {"GESAMTKONTRAKT", "EINZELMENGEN"}

    @classmethod
    def validate_contract_type(cls, value: str) -> None:
        if value not in cls.ALLOWED_TYPES:
            raise ValueError(f"invalid contract_type: {value}")

    @classmethod
    def validate_status(cls, value: str) -> None:
        if value not in cls.ALLOWED_STATUS:
            raise ValueError(f"invalid status: {value}")

    @classmethod
    def validate_quantity_type(cls, value: str) -> None:
        if value not in cls.ALLOWED_QTY_TYPES:
            raise ValueError(f"invalid quantity_type: {value}")


class KontraktNumberRangeService:
    def __init__(self, db: Session):
        self.db = db

    def next_contract_no(self, tenant_id: str, contract_type: str, branch_id: Optional[str]) -> str:
        # row-level lock avoids duplicate numbers under parallel requests
        row = (
            self.db.query(KonNumberRange)
            .filter(
                KonNumberRange.tenant_id == tenant_id,
                KonNumberRange.contract_type == contract_type,
                KonNumberRange.branch_id.is_(branch_id) if branch_id is None else KonNumberRange.branch_id == branch_id,
            )
            .with_for_update()
            .first()
        )
        if not row:
            prefix = f"{contract_type[:3]}-{(branch_id or 'ALL')[:4].upper()}"
            row = KonNumberRange(
                id=uuid7(),
                tenant_id=tenant_id,
                contract_type=contract_type,
                branch_id=branch_id,
                prefix=prefix,
                next_number=1,
                padding=6,
            )
            self.db.add(row)
            self.db.flush()
        number = row.next_number
        row.next_number += 1
        return f"{row.prefix}-{str(number).zfill(row.padding)}"


@dataclass
class RestSnapshot:
    line_rest: dict[str, Decimal]
    contract_rest: Decimal


class KontraktRestmengenService:
    def __init__(self, db: Session):
        self.db = db

    def compute_rest(self, tenant_id: str, contract_id: str) -> RestSnapshot:
        lines = (
            self.db.query(KonContractLine)
            .filter(KonContractLine.tenant_id == tenant_id, KonContractLine.contract_id == contract_id)
            .all()
        )
        line_rest: dict[str, Decimal] = {}
        contract_rest = Decimal("0")
        for line in lines:
            moved = (
                self.db.query(func.coalesce(func.sum(KonContractMovement.quantity), 0))
                .filter(
                    KonContractMovement.tenant_id == tenant_id,
                    KonContractMovement.contract_id == contract_id,
                    KonContractMovement.line_id == line.line_id,
                )
                .scalar()
            )
            qty_contract = Decimal(str(line.qty_contract or 0))
            qty_moved = Decimal(str(moved or 0))
            rest = qty_contract - qty_moved
            line_rest[line.line_id] = rest
            contract_rest += rest
        return RestSnapshot(line_rest=line_rest, contract_rest=contract_rest)

    def enforce_overdelivery(self, allow_overdelivery: bool, line_rest: Decimal, quantity_to_move: Decimal) -> None:
        if not allow_overdelivery and quantity_to_move > line_rest:
            raise ValueError("Movement exceeds remaining quantity")

    @staticmethod
    def determine_status_from_rest(
        allow_overdelivery: bool,
        current_status: str,
        contract_rest: Decimal,
    ) -> str:
        if current_status == "STORNIERT":
            return "STORNIERT"
        if allow_overdelivery:
            return current_status or "OFFEN"
        return "ERLEDIGT" if contract_rest <= Decimal("0") else "OFFEN"


class KontraktAuditService:
    def __init__(self, db: Session):
        self.db = db

    def log_change(
        self,
        *,
        tenant_id: str,
        entity_type: str,
        entity_id: str,
        field_name: str,
        action: str,
        changed_by: Optional[str],
        old_value: Optional[object],
        new_value: Optional[object],
    ) -> None:
        row = KonAuditLog(
            audit_id=uuid7(),
            tenant_id=tenant_id,
            entity_type=entity_type,
            entity_id=entity_id,
            field_name=field_name,
            old_value=None if old_value is None else str(old_value),
            new_value=None if new_value is None else str(new_value),
            action=action,
            changed_by=changed_by,
        )
        self.db.add(row)

    def log_diff_for_contract(
        self,
        *,
        tenant_id: str,
        contract_id: str,
        changed_by: Optional[str],
        before: KonContract,
        after_payload: dict,
    ) -> None:
        for key, new_value in after_payload.items():
            old_value = getattr(before, key, None)
            if str(old_value) != str(new_value):
                self.log_change(
                    tenant_id=tenant_id,
                    entity_type="kon_contract",
                    entity_id=contract_id,
                    field_name=key,
                    action="UPDATE",
                    changed_by=changed_by,
                    old_value=old_value,
                    new_value=new_value,
                )
