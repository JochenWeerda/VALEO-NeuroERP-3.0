"""Service layer for Agrar contract management and allocation logic."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from app.core.data_quality_enforcement import build_dq_error_detail, evaluate_contract_datensatz
from app.core.exceptions import ConflictError, EntityNotFoundError, ValidationFailedError
from app.core.uuid7 import uuid7
from app.infrastructure.models import AgrarContract, AgrarContractAllocation

ContractStatus = str  # "open" | "partially_allocated" | "fulfilled" | "cancelled" | "closed"


def _compute_status(total: Decimal, remaining: Decimal, current: str) -> str:
    if current == "cancelled":
        return "cancelled"
    if remaining <= Decimal("0"):
        return "fulfilled"
    if remaining < total:
        return "partially_allocated"
    return "open"


def _build_dq_datensatz(data: dict) -> dict:
    return {
        "kontrakt_nr": data.get("contract_number"),
        "lieferant_nr": data.get("partner_id"),
        "ware": data.get("article_id"),
        "menge_tonnen": (
            float(data["total_quantity_kg"]) / 1000.0
            if data.get("total_quantity_kg") is not None
            else None
        ),
        "preis_eur_pro_t": data.get("fixed_price"),
        "kontrakt_status": str(data.get("status") or "AKTIV").upper(),
        "preismodell": data.get("pricing_model"),
    }


class AgrarContractService:
    """Encapsulates all business logic for Agrar contracts and allocations."""

    def __init__(self, db: Session, tenant_id: str) -> None:
        self.db = db
        self.tenant_id = tenant_id

    # ── internal ──────────────────────────────────────────────────────────────

    def _get_or_raise(self, contract_id: str) -> AgrarContract:
        obj = (
            self.db.query(AgrarContract)
            .filter(AgrarContract.id == contract_id, AgrarContract.tenant_id == self.tenant_id)
            .first()
        )
        if obj is None:
            raise EntityNotFoundError("AgrarContract", contract_id)
        return obj

    def _validate_dq(self, data: dict) -> None:
        result = evaluate_contract_datensatz(_build_dq_datensatz(data))
        if not result.bestanden:
            raise ValidationFailedError(build_dq_error_detail("Kontrakt", result))

    # ── queries ───────────────────────────────────────────────────────────────

    def list_contracts(
        self,
        status: Optional[str] = None,
        pricing_model: Optional[str] = None,
        skip: int = 0,
        limit: int = 25,
    ) -> Tuple[List[AgrarContract], int]:
        q = self.db.query(AgrarContract).filter(AgrarContract.tenant_id == self.tenant_id)
        if status:
            q = q.filter(AgrarContract.status == status)
        if pricing_model:
            q = q.filter(AgrarContract.pricing_model == pricing_model)
        total = q.count()
        items = q.order_by(AgrarContract.created_at.desc()).offset(skip).limit(limit).all()
        return items, total

    def get_contract(self, contract_id: str) -> AgrarContract:
        return self._get_or_raise(contract_id)

    def list_allocations(self, contract_id: str) -> List[AgrarContractAllocation]:
        self._get_or_raise(contract_id)  # ownership check
        return (
            self.db.query(AgrarContractAllocation)
            .filter(
                AgrarContractAllocation.contract_id == contract_id,
                AgrarContractAllocation.tenant_id == self.tenant_id,
            )
            .order_by(AgrarContractAllocation.allocated_at.desc())
            .all()
        )

    # ── mutations ─────────────────────────────────────────────────────────────

    def create_contract(self, payload: dict) -> AgrarContract:
        self._validate_dq({**payload, "status": "AKTIV"})
        exists = (
            self.db.query(AgrarContract)
            .filter(
                AgrarContract.tenant_id == self.tenant_id,
                AgrarContract.contract_number == payload["contract_number"],
            )
            .first()
        )
        if exists:
            raise ConflictError("contract_number already exists")

        contract = AgrarContract(
            id=uuid7(),
            tenant_id=self.tenant_id,
            status="open",
            remaining_quantity_kg=payload["total_quantity_kg"],
            **{k: v for k, v in payload.items()},
        )
        self.db.add(contract)
        self.db.commit()
        self.db.refresh(contract)
        return contract

    def update_contract(self, contract_id: str, data: dict) -> AgrarContract:
        contract = self._get_or_raise(contract_id)

        effective = {
            "contract_number": contract.contract_number,
            "partner_id": data.get("partner_id", contract.partner_id),
            "article_id": data.get("article_id", contract.article_id),
            "total_quantity_kg": float(contract.total_quantity_kg),
            "fixed_price": data.get("fixed_price", float(contract.fixed_price) if contract.fixed_price is not None else None),
            "status": data.get("status", contract.status),
            "pricing_model": data.get("pricing_model", contract.pricing_model),
        }
        self._validate_dq(effective)

        if data.get("status") == "cancelled":
            contract.status = "cancelled"
            self.db.commit()
            self.db.refresh(contract)
            return contract

        for field, value in data.items():
            setattr(contract, field, value)

        contract.status = _compute_status(
            Decimal(str(contract.total_quantity_kg)),
            Decimal(str(contract.remaining_quantity_kg)),
            contract.status,
        )
        self.db.commit()
        self.db.refresh(contract)
        return contract

    def allocate(self, contract_id: str, allocation_quantity_kg: float, ticket_id: Optional[str], note: Optional[str]) -> AgrarContractAllocation:
        contract = self._get_or_raise(contract_id)
        if contract.status == "cancelled":
            raise ValidationFailedError("Contract is cancelled")
        if contract.status == "fulfilled":
            raise ValidationFailedError("Contract already fulfilled")

        quantity = Decimal(str(allocation_quantity_kg))
        remaining = Decimal(str(contract.remaining_quantity_kg))
        if quantity > remaining:
            raise ValidationFailedError("Allocation exceeds remaining quantity")

        contract.remaining_quantity_kg = remaining - quantity
        contract.status = _compute_status(
            Decimal(str(contract.total_quantity_kg)),
            Decimal(str(contract.remaining_quantity_kg)),
            contract.status,
        )

        allocation = AgrarContractAllocation(
            id=uuid7(),
            contract_id=contract.id,
            ticket_id=ticket_id,
            allocation_quantity_kg=allocation_quantity_kg,
            note=note,
            tenant_id=self.tenant_id,
        )
        self.db.add(allocation)
        self.db.commit()
        self.db.refresh(allocation)
        return allocation

    def delete_contract(self, contract_id: str) -> None:
        contract = self._get_or_raise(contract_id)
        if contract.status not in ("open", "draft"):
            raise ValidationFailedError("Only open/draft contracts can be deleted")
        alloc_count = (
            self.db.query(AgrarContractAllocation)
            .filter(AgrarContractAllocation.contract_id == contract_id)
            .count()
        )
        if alloc_count > 0:
            raise ValidationFailedError("Contract has allocations; cancel instead of delete")
        self.db.delete(contract)
        self.db.commit()

    def cancel_contract(self, contract_id: str) -> AgrarContract:
        contract = self._get_or_raise(contract_id)
        if contract.status == "cancelled":
            raise ConflictError("Contract is already cancelled")
        if contract.status == "fulfilled":
            raise ValidationFailedError("Fulfilled contracts cannot be cancelled")
        contract.status = "cancelled"
        self.db.commit()
        self.db.refresh(contract)
        return contract

    def close_contract(self, contract_id: str) -> AgrarContract:
        contract = self._get_or_raise(contract_id)
        if contract.status not in ("fulfilled", "partially_allocated"):
            raise ValidationFailedError(f"Cannot close contract in status '{contract.status}'")
        contract.status = "closed"
        self.db.commit()
        self.db.refresh(contract)
        return contract
