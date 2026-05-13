"""Service layer for Agrar self-billing settlements (AGRAR-SET-01)."""

from __future__ import annotations

import logging
from datetime import datetime
from decimal import Decimal
from typing import Any, List, Optional, Tuple

from sqlalchemy.orm import Session

from app.core.data_quality_enforcement import build_dq_error_detail, evaluate_settlement_datensatz
from app.core.exceptions import ConflictError, EntityNotFoundError, ValidationFailedError
from app.core.uuid7 import uuid7
from app.infrastructure.models import AgrarSettlement, AgrarSettlementDeduction
from app.repositories.agrar_settlement_repository import AgrarSettlementRepository
from modules.agrar.services.settlement_calculator import (
    calc_deduction_amount as _calc_deduction_amount,
    compute_settlement_amounts as _compute_settlement_amounts,
    round_money as _round_money,
    round_qty as _round_qty,
)

logger = logging.getLogger(__name__)


class AgrarSettlementService:
    """Encapsulates create/read/post/cancel lifecycle for AgrarSettlement records."""

    def __init__(self, db: Session, tenant_id: str) -> None:
        self.db = db
        self.tenant_id = tenant_id
        self.repo = AgrarSettlementRepository(db, tenant_id)

    # ── amount helpers (stateless, exposed for previews) ─────────────────────

    @staticmethod
    def compute_amounts(
        billing_quantity_kg: Decimal,
        unit_price_eur_per_ton: Decimal,
        deductions: list,
    ) -> dict[str, Decimal]:
        result = _compute_settlement_amounts(
            billing_quantity_kg=billing_quantity_kg,
            unit_price_eur_per_ton=unit_price_eur_per_ton,
            deductions=deductions,
        )
        if result["net_amount"] < Decimal("0"):
            raise ValidationFailedError("Deductions exceed gross amount")
        return result

    @staticmethod
    def round_money(value) -> Decimal:
        return _round_money(value)

    @staticmethod
    def round_qty(value) -> Decimal:
        return _round_qty(value)

    # ── queries ───────────────────────────────────────────────────────────────

    def list_settlements(
        self,
        supplier_id: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[AgrarSettlement], int]:
        if supplier_id:
            return self.repo.list_by_supplier(supplier_id, status=status, skip=skip, limit=limit)
        if status:
            return self.repo.list_by_status(status, skip=skip, limit=limit)
        items, total = self.repo.list_paginated(skip=skip, limit=limit)
        return items, total

    def get_settlement(self, settlement_id: str) -> Tuple[AgrarSettlement, list]:
        settlement = self.repo.get_by_id(settlement_id)
        deductions = self.repo.list_deductions(settlement_id)
        return settlement, deductions

    # ── status helpers ────────────────────────────────────────────────────────

    @staticmethod
    def get_approval_status(settlement: AgrarSettlement) -> str:
        meta = getattr(settlement, "approval_metadata", None) or {}
        if isinstance(meta, dict):
            return meta.get("status", "OFFEN")
        return "OFFEN"

    @staticmethod
    def get_approval_history(settlement: AgrarSettlement) -> list[dict]:
        meta = getattr(settlement, "approval_metadata", None) or {}
        if isinstance(meta, dict):
            return meta.get("history", [])
        return []

    @staticmethod
    def get_allowed_transitions(approval_status: str) -> list[str]:
        transitions = {
            "OFFEN": ["FREIGEGEBEN", "ABGELEHNT"],
            "FREIGEGEBEN": ["VERBUCHT"],
            "ABGELEHNT": ["OFFEN"],
            "VERBUCHT": [],
        }
        return transitions.get(approval_status, [])

    @staticmethod
    def build_correction_options(settlement: AgrarSettlement, approval_status: str) -> list[dict]:
        if settlement.status != "posted":
            return []
        base = f"Settlement {settlement.settlement_number} / Journal {settlement.posted_journal_ref or '-'}"
        return [
            {"memo_type": "credit", "label": "Gutschrift erstellen", "reason": f"Gutschrift zur Settlement-Korrektur ({base})"},
            {"memo_type": "debit", "label": "Belastung erstellen", "reason": f"Belastung zur Settlement-Korrektur ({base})"},
            {"memo_type": "rework", "label": "Korrektur ueber Belegpfad dokumentieren", "reason": f"Settlement ist bereits verbucht; Korrektur nur ueber Gutschrift/Belastung ({base})"},
        ]

    @staticmethod
    def get_row_version(settlement: AgrarSettlement) -> int:
        return getattr(settlement, "row_version", 0) or 0

    # ── mutations ─────────────────────────────────────────────────────────────

    def create_settlement(self, payload: Any, settlement_number: Optional[str] = None) -> Tuple[AgrarSettlement, list]:
        sn = settlement_number or payload.settlement_number or f"SET-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        dq_result = evaluate_settlement_datensatz({
            "abrechnungsnummer": sn,
            "lieferant_id": payload.supplier_id,
            "brutto_gewicht_kg": payload.gross_quantity_kg,
            "abrechnungsgewicht_kg": payload.billing_quantity_kg if payload.billing_quantity_kg is not None else payload.gross_quantity_kg,
            "preis_eur_pro_t": payload.unit_price_eur_per_ton,
            "waehrung": "EUR",
        })
        if not dq_result.bestanden:
            raise ValidationFailedError(build_dq_error_detail("Abrechnung", dq_result))

        if self.repo.get_by_settlement_number(sn):
            raise ConflictError("settlement_number already exists")

        gross_qty = _round_qty(payload.gross_quantity_kg)
        billing_qty = _round_qty(
            payload.billing_quantity_kg if payload.billing_quantity_kg is not None else payload.gross_quantity_kg
        )
        amounts = self.compute_amounts(
            billing_quantity_kg=billing_qty,
            unit_price_eur_per_ton=Decimal(str(payload.unit_price_eur_per_ton)),
            deductions=payload.deductions,
        )

        settlement = AgrarSettlement(
            id=uuid7(),
            settlement_number=sn,
            campaign_id=getattr(payload, "campaign_id", None),
            contract_id=payload.contract_id,
            ticket_id=payload.ticket_id,
            supplier_id=payload.supplier_id,
            article_id=payload.article_id,
            gross_quantity_kg=gross_qty,
            billing_quantity_kg=billing_qty,
            unit_price_eur_per_ton=Decimal(str(payload.unit_price_eur_per_ton)),
            gross_amount_eur=amounts["gross_amount"],
            total_deductions_eur=amounts["total_deductions"],
            net_amount_eur=amounts["net_amount"],
            currency="EUR",
            status="draft",
            note=payload.note,
            tenant_id=self.tenant_id,
        )
        self.db.add(settlement)
        self.db.flush()

        deduction_rows: list[AgrarSettlementDeduction] = []
        for d in payload.deductions:
            billing_tons = billing_qty / Decimal("1000")
            amt = _calc_deduction_amount(d, billing_tons)
            row = AgrarSettlementDeduction(
                id=uuid7(),
                settlement_id=settlement.id,
                deduction_type=d.deduction_type,
                mode=d.mode,
                rate_per_ton_eur=d.rate_per_ton_eur,
                fixed_amount_eur=d.fixed_amount_eur,
                basis_quantity_tons=d.basis_quantity_tons,
                amount_eur=amt,
                note=d.note,
                tenant_id=self.tenant_id,
            )
            self.db.add(row)
            deduction_rows.append(row)

        self.db.commit()
        self.db.refresh(settlement)
        return settlement, deduction_rows

    def cancel_settlement(self, settlement_id: str, reason: Optional[str] = None) -> AgrarSettlement:
        settlement = self.repo.get_by_id(settlement_id)
        if settlement.status == "cancelled":
            raise ConflictError("Settlement already cancelled")
        if settlement.status == "posted":
            raise ValidationFailedError("Posted settlements cannot be cancelled directly; use correction memo")
        settlement.status = "cancelled"
        if reason:
            settlement.note = f"[STORNO] {reason}"
        self.db.commit()
        self.db.refresh(settlement)
        return settlement

    def post_to_fibu(self, settlement_id: str, journal_ref: str) -> AgrarSettlement:
        settlement = self.repo.get_by_id(settlement_id)
        approval_status = self.get_approval_status(settlement)
        if settlement.status != "draft":
            raise ValidationFailedError(f"Settlement status '{settlement.status}' cannot be posted")
        if approval_status != "FREIGEGEBEN":
            raise ValidationFailedError(f"Settlement approval status '{approval_status}' must be FREIGEGEBEN before posting")
        settlement.status = "posted"
        settlement.posted_journal_ref = journal_ref
        settlement.posted_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(settlement)
        return settlement
