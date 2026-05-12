"""
No-Speculation Guard Service for Commodity Positions.
Prüft ob Verkauf/Vorgang Short erzeugt; Freigabe (Override) anfordern/genehmigen/ablehnen.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional

from sqlalchemy.orm import Session

from app.core.uuid7 import uuid7
from app.domains.operations.models import PosPositionOverride, PosPositionRule
from app.services.position_service import PositionCalculationService


@dataclass
class GuardResult:
    allowed: bool
    reason: str
    article_id: Optional[str] = None
    period_key: Optional[str] = None
    net_after: Optional[Decimal] = None
    tolerance: Optional[Decimal] = None
    override_required: bool = False


class PositionGuardService:
    def __init__(self, db: Session):
        self.db = db
        self._pos_svc = PositionCalculationService(db)

    def _rule_for_article(self, tenant_id: str, article_id: str, at_date: datetime) -> Optional[PosPositionRule]:
        rule = (
            self.db.query(PosPositionRule)
            .filter(
                PosPositionRule.tenant_id == tenant_id,
                PosPositionRule.scope_type == "ARTICLE",
                PosPositionRule.scope_id == article_id,
                (PosPositionRule.active_from.is_(None)) | (PosPositionRule.active_from <= at_date),
                (PosPositionRule.active_to.is_(None)) | (PosPositionRule.active_to >= at_date),
            )
            .order_by(PosPositionRule.active_from.desc().nullsfirst())
            .first()
        )
        return rule

    def _active_override(
        self,
        tenant_id: str,
        branch_id: Optional[str],
        article_id: str,
        period_key: str,
    ) -> Optional[PosPositionOverride]:
        return (
            self.db.query(PosPositionOverride)
            .filter(
                PosPositionOverride.tenant_id == tenant_id,
                PosPositionOverride.article_id == article_id,
                PosPositionOverride.period_key == period_key,
                (PosPositionOverride.branch_id.is_(None)) | (PosPositionOverride.branch_id == branch_id),
                PosPositionOverride.status == "APPROVED",
                (PosPositionOverride.valid_until.is_(None)) | (PosPositionOverride.valid_until >= datetime.utcnow()),
            )
            .first()
        )

    def check_impact(
        self,
        tenant_id: str,
        branch_id: Optional[str],
        article_id: str,
        period_key: str,
        delta_sell_qty: Decimal,
        as_of_date: Optional[datetime] = None,
        period_mode: str = "M",
        user_roles: Optional[list[str]] = None,
    ) -> GuardResult:
        """
        Prüft ob eine zusätzliche Verkaufsmenge (delta_sell_qty) zu Short unter Toleranz führt.
        Wenn Regel approval_required hat und User approval_role hat und aktiver Override: erlauben.
        """
        as_of = (as_of_date or datetime.utcnow()).date()
        rule = self._rule_for_article(tenant_id, article_id, datetime.combine(as_of, datetime.max.time()))
        matrix = self._pos_svc.calculate_matrix(
            tenant_id=tenant_id,
            branch_id=branch_id,
            as_of_date=as_of,
            period_mode=period_mode,
            period_from=period_key,
            period_to=period_key,
            article_ids=[article_id],
        )
        if not matrix.rows:
            net_after = -delta_sell_qty
        else:
            cell = next((c for c in matrix.rows[0].cells if c.period_key == period_key), None)
            net_after = (cell.qty_net - delta_sell_qty) if cell else -delta_sell_qty

        if rule is None:
            return GuardResult(allowed=True, reason="Keine Positionsregel aktiv")

        tolerance = rule.neg_tolerance_qty or Decimal("0")
        if net_after >= tolerance:
            return GuardResult(allowed=True, reason="Position innerhalb Toleranz")

        override = self._active_override(tenant_id, branch_id, article_id, period_key)
        if override:
            return GuardResult(
                allowed=True,
                reason="Aktive Freigabe vorhanden",
                article_id=article_id,
                period_key=period_key,
                net_after=net_after,
                tolerance=tolerance,
            )

        if rule and rule.approval_required:
            has_role = user_roles and rule.approval_role and rule.approval_role.lower() in [r.lower() for r in user_roles]
            if has_role:
                return GuardResult(
                    allowed=True,
                    reason="Benutzer hat Freigaberolle",
                    article_id=article_id,
                    period_key=period_key,
                    net_after=net_after,
                    tolerance=tolerance,
                )
            return GuardResult(
                allowed=False,
                reason="Short unter Toleranz; Freigabe erforderlich",
                article_id=article_id,
                period_key=period_key,
                net_after=net_after,
                tolerance=tolerance,
                override_required=True,
            )

        return GuardResult(
            allowed=False,
            reason="Short unter Toleranz",
            article_id=article_id,
            period_key=period_key,
            net_after=net_after,
            tolerance=tolerance,
        )

    def request_override(
        self,
        tenant_id: str,
        branch_id: Optional[str],
        article_id: str,
        period_key: str,
        requested_by: str,
        reason: str,
        related_doc_type: Optional[str] = None,
        related_doc_id: Optional[str] = None,
    ) -> PosPositionOverride:
        row = PosPositionOverride(
            override_id=uuid7(),
            tenant_id=tenant_id,
            branch_id=branch_id,
            article_id=article_id,
            period_key=period_key,
            requested_by=requested_by,
            status="REQUESTED",
            reason=reason,
            related_doc_type=related_doc_type,
            related_doc_id=related_doc_id,
        )
        self.db.add(row)
        self.db.flush()
        return row

    def approve_override(
        self,
        override_id: str,
        tenant_id: str,
        approved_by: str,
        comment: str,
        valid_days: int = 14,
    ) -> Optional[PosPositionOverride]:
        row = (
            self.db.query(PosPositionOverride)
            .filter(
                PosPositionOverride.override_id == override_id,
                PosPositionOverride.tenant_id == tenant_id,
                PosPositionOverride.status == "REQUESTED",
            )
            .first()
        )
        if not row:
            return None
        row.status = "APPROVED"
        row.approved_by = approved_by
        row.approved_at = datetime.utcnow()
        row.valid_until = datetime.utcnow() + timedelta(days=valid_days)
        row.comment = comment
        self.db.flush()
        return row

    def reject_override(
        self,
        override_id: str,
        tenant_id: str,
        rejected_by: str,
        comment: str,
    ) -> Optional[PosPositionOverride]:
        row = (
            self.db.query(PosPositionOverride)
            .filter(
                PosPositionOverride.override_id == override_id,
                PosPositionOverride.tenant_id == tenant_id,
                PosPositionOverride.status == "REQUESTED",
            )
            .first()
        )
        if not row:
            return None
        row.status = "REJECTED"
        row.approved_by = rejected_by
        row.approved_at = datetime.utcnow()
        row.comment = comment
        self.db.flush()
        return row
