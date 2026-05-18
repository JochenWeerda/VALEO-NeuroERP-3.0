"""Approval workflow service for Agrar settlements (AGRAR-SET-FREIGABE)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, EntityNotFoundError, ValidationFailedError
from app.core.settlement_approval import (
    SettlementActorType,
    SettlementApprovalRequest,
    SettlementApprovalStatus,
    evaluate_settlement_approval,
    get_allowed_transitions,
    is_terminal,
)
from app.infrastructure.models import AgrarSettlement


class SettlementApprovalService:
    """Encapsulates the approval (Freigabe) lifecycle for AgrarSettlement records.

    All methods that touch the database accept the settlement ORM object directly
    (already loaded by the caller) to avoid redundant round-trips.  Methods that
    need to load a settlement accept a ``settlement_id`` and a ``db`` session.
    """

    def __init__(self, db: Session, tenant_id: str) -> None:
        self.db = db
        self.tenant_id = tenant_id

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _load(self, settlement_id: str) -> AgrarSettlement:
        from app.repositories.agrar_settlement_repository import AgrarSettlementRepository
        return AgrarSettlementRepository(self.db, self.tenant_id).get_by_id(settlement_id)

    @staticmethod
    def _current_approval_status(settlement: AgrarSettlement) -> SettlementApprovalStatus:
        raw = (settlement.drying_result or {}).get("approval_status", "ENTWURF")
        try:
            return SettlementApprovalStatus(raw)
        except ValueError:
            return SettlementApprovalStatus.ENTWURF

    def _persist_transition(
        self,
        settlement: AgrarSettlement,
        result: "SettlementApprovalResult",  # noqa: F821
    ) -> None:
        """Write new approval_status and append audit entry to drying_result JSONB."""
        new_state = dict(settlement.drying_result or {})
        new_state["approval_status"] = result.new_status.value
        history = list(new_state.get("approval_history") or [])
        history.append(result.audit_entry)
        new_state["approval_history"] = history
        settlement.drying_result = new_state
        try:
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise ConflictError("Abrechnung wurde zwischenzeitlich geändert.")

    def _apply_transition(
        self,
        settlement: AgrarSettlement,
        actor_id: str,
        actor_type_str: str,
        target_status_str: str,
        reason: Optional[str],
        expected_row_version: Optional[int],
    ) -> dict:
        """Shared logic: validate, evaluate, persist, return audit dict."""
        # Optimistic locking
        if expected_row_version is not None:
            current_version = int(getattr(settlement, "row_version", 0) or 0)
            if current_version != expected_row_version:
                raise ConflictError(
                    f"row_version_conflict: expected {expected_row_version}, got {current_version}"
                )

        try:
            actor_type = SettlementActorType(actor_type_str)
            target_status = SettlementApprovalStatus(target_status_str)
        except ValueError as exc:
            raise ValidationFailedError(str(exc)) from exc

        current_status = self._current_approval_status(settlement)

        req = SettlementApprovalRequest(
            settlement_id=str(settlement.id),
            tenant_id=self.tenant_id,
            actor_id=actor_id,
            actor_type=actor_type,
            target_status=target_status,
            reason=reason,
        )
        result = evaluate_settlement_approval(req, current_status)

        if not result.allowed:
            raise ValidationFailedError(
                f"Transition {current_status.value} → {target_status_str} not allowed: {result.reason}"
            )

        self._persist_transition(settlement, result)
        effective_status = result.new_status if result.allowed else current_status
        return {
            **result.audit_entry,
            "allowed_transitions": [s.value for s in get_allowed_transitions(effective_status)],
            "is_terminal": is_terminal(effective_status),
        }

    # ── Public API ────────────────────────────────────────────────────────────

    def submit_for_approval(
        self,
        settlement_id: str,
        user_id: str,
        db: Optional[Session] = None,
    ) -> AgrarSettlement:
        """Transition settlement to ZUR_FREIGABE status.

        Args:
            settlement_id: ID of the settlement to submit.
            user_id: ID of the user initiating the submission.
            db: Optional override db session.

        Returns:
            Updated AgrarSettlement ORM object.

        Raises:
            EntityNotFoundError: settlement not found.
            ValidationFailedError: transition not allowed.
        """
        session = db or self.db
        from app.repositories.agrar_settlement_repository import AgrarSettlementRepository
        svc = SettlementApprovalService(session, self.tenant_id)
        settlement = AgrarSettlementRepository(session, self.tenant_id).get_by_id(settlement_id)
        svc._apply_transition(
            settlement,
            actor_id=user_id,
            actor_type_str="SACHBEARBEITER",
            target_status_str="ZUR_FREIGABE",
            reason="Zur Freigabe eingereicht",
            expected_row_version=None,
        )
        session.refresh(settlement)
        return settlement

    def approve_settlement(
        self,
        settlement_id: str,
        approver_id: str,
        db: Optional[Session] = None,
    ) -> AgrarSettlement:
        """Transition settlement to FREIGEGEBEN status.

        Args:
            settlement_id: ID of the settlement to approve.
            approver_id: ID of the approving user/actor.
            db: Optional override db session.

        Returns:
            Updated AgrarSettlement ORM object.

        Raises:
            EntityNotFoundError: settlement not found.
            ValidationFailedError: transition not allowed (e.g., not in ZUR_FREIGABE).
        """
        session = db or self.db
        from app.repositories.agrar_settlement_repository import AgrarSettlementRepository
        svc = SettlementApprovalService(session, self.tenant_id)
        settlement = AgrarSettlementRepository(session, self.tenant_id).get_by_id(settlement_id)
        svc._apply_transition(
            settlement,
            actor_id=approver_id,
            actor_type_str="ABTEILUNGSLEITER",
            target_status_str="FREIGEGEBEN",
            reason="Freigabe erteilt",
            expected_row_version=None,
        )
        session.refresh(settlement)
        return settlement

    def reject_settlement(
        self,
        settlement_id: str,
        reason: str,
        db: Optional[Session] = None,
    ) -> AgrarSettlement:
        """Transition settlement to ABGELEHNT status.

        Args:
            settlement_id: ID of the settlement to reject.
            reason: Mandatory rejection reason (GoBD audit trail).
            db: Optional override db session.

        Returns:
            Updated AgrarSettlement ORM object.

        Raises:
            EntityNotFoundError: settlement not found.
            ValidationFailedError: transition not allowed or reason missing.
        """
        if not reason or not reason.strip():
            raise ValidationFailedError("Ablehnungsgrund (reason) ist Pflichtfeld")

        session = db or self.db
        from app.repositories.agrar_settlement_repository import AgrarSettlementRepository
        svc = SettlementApprovalService(session, self.tenant_id)
        settlement = AgrarSettlementRepository(session, self.tenant_id).get_by_id(settlement_id)
        svc._apply_transition(
            settlement,
            actor_id="system",
            actor_type_str="SACHBEARBEITER",
            target_status_str="ABGELEHNT",
            reason=reason,
            expected_row_version=None,
        )
        session.refresh(settlement)
        return settlement

    def get_approval_status(
        self,
        settlement_id: str,
        db: Optional[Session] = None,
    ) -> dict:
        """Return the current approval status and allowed transitions for a settlement.

        Args:
            settlement_id: ID of the settlement.
            db: Optional override db session.

        Returns:
            Dict with keys:
              - settlement_id: str
              - approval_status: str (SettlementApprovalStatus value)
              - allowed_transitions: list[str]
              - is_terminal: bool
              - approval_history: list[dict]
        """
        session = db or self.db
        from app.repositories.agrar_settlement_repository import AgrarSettlementRepository

        settlement = AgrarSettlementRepository(session, self.tenant_id).get_by_id(settlement_id)
        current = self._current_approval_status(settlement)
        history = (settlement.drying_result or {}).get("approval_history") or []

        return {
            "settlement_id": settlement_id,
            "approval_status": current.value,
            "allowed_transitions": [s.value for s in get_allowed_transitions(current)],
            "is_terminal": is_terminal(current),
            "approval_history": list(history),
        }
