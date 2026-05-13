"""Repository for AgrarSettlement and its deductions."""

from __future__ import annotations

from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from app.core.exceptions import EntityNotFoundError
from app.core.repository import BaseRepository
from app.infrastructure.models import AgrarSettlement, AgrarSettlementDeduction


class AgrarSettlementRepository(BaseRepository[AgrarSettlement]):
    model = AgrarSettlement

    # ── query helpers ─────────────────────────────────────────────────────────

    def list_by_supplier(
        self,
        supplier_id: str,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[AgrarSettlement], int]:
        q = self._base_query().filter(AgrarSettlement.supplier_id == supplier_id)
        if status:
            q = q.filter(AgrarSettlement.status == status)
        total = q.count()
        items = (
            q.order_by(AgrarSettlement.settlement_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        return items, total

    def list_by_status(
        self,
        status: str,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[AgrarSettlement], int]:
        q = self._base_query().filter(AgrarSettlement.status == status)
        total = q.count()
        items = q.order_by(AgrarSettlement.settlement_date.desc()).offset(skip).limit(limit).all()
        return items, total

    def get_by_settlement_number(self, settlement_number: str) -> Optional[AgrarSettlement]:
        return self._base_query().filter(
            AgrarSettlement.settlement_number == settlement_number
        ).first()

    # ── deductions ────────────────────────────────────────────────────────────

    def list_deductions(self, settlement_id: str) -> List[AgrarSettlementDeduction]:
        return (
            self.db.query(AgrarSettlementDeduction)
            .filter(AgrarSettlementDeduction.settlement_id == settlement_id)
            .all()
        )

    def add_deduction(self, deduction: AgrarSettlementDeduction) -> AgrarSettlementDeduction:
        self.db.add(deduction)
        self.db.commit()
        self.db.refresh(deduction)
        return deduction

    def delete_deductions(self, settlement_id: str) -> int:
        deleted = (
            self.db.query(AgrarSettlementDeduction)
            .filter(AgrarSettlementDeduction.settlement_id == settlement_id)
            .delete()
        )
        self.db.commit()
        return deleted

    # ── status transitions ────────────────────────────────────────────────────

    def transition_status(self, settlement_id: str, new_status: str) -> AgrarSettlement:
        obj = self.get_by_id(settlement_id)
        obj.status = new_status  # type: ignore[assignment]
        self.db.commit()
        self.db.refresh(obj)
        return obj
