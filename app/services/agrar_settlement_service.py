"""Service layer for Agrar self-billing settlements (AGRAR-SET-01)."""

from __future__ import annotations

import logging
from datetime import date, datetime
from decimal import Decimal
from types import SimpleNamespace
from typing import Any, List, Optional, Tuple

from sqlalchemy.orm import Session

from app.core.data_quality_enforcement import build_dq_error_detail, evaluate_settlement_datensatz
from app.core.exceptions import ConflictError, EntityNotFoundError, ValidationFailedError
from app.core.trocknungs_abrechnung import (
    TrocknungsInput,
    TrocknungsMethode,
    TrocknungsRegelParametrierung,
    compute_trocknungs_abrechnung,
    get_default_trocknungsregeln,
    validate_trocknungs_ergebnis,
)
from app.core.uuid7 import uuid7
from app.infrastructure.drying_rule_repo import DbDryingRuleRepo
from app.infrastructure.models import AgrarSettlement, AgrarSettlementDeduction
from app.repositories.agrar_settlement_repository import AgrarSettlementRepository
from modules.agrar.services.drying_rule_engine import compute_settlement as _compute_drying_settlement
from modules.agrar.services.moisture_engine import MoistureEngineInput, calculate_billing_weight
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

    @staticmethod
    def build_dq_datensatz(payload: Any, settlement_number: str) -> dict[str, Any]:
        return {
            "abrechnungsnummer": settlement_number,
            "lieferant_id": payload.supplier_id,
            "brutto_gewicht_kg": payload.gross_quantity_kg,
            "abrechnungsgewicht_kg": (
                payload.billing_quantity_kg
                if getattr(payload, "billing_quantity_kg", None) is not None
                else payload.gross_quantity_kg
            ),
            "preis_eur_pro_t": payload.unit_price_eur_per_ton,
            "waehrung": "EUR",
        }

    @staticmethod
    def preview_billing_weight(payload: Any) -> dict[str, float]:
        result = calculate_billing_weight(
            MoistureEngineInput(
                net_weight_kg=Decimal(str(payload.net_weight_kg)),
                moisture_pct=Decimal(str(payload.moisture_pct)),
                impurities_pct=Decimal(str(payload.impurities_pct)),
                target_moisture_pct=Decimal(str(payload.target_moisture_pct)),
                base_impurities_pct=Decimal(str(payload.base_impurities_pct)),
                allow_bonus=payload.allow_bonus,
            )
        )
        return {
            "net_weight_kg": float(result.net_weight_kg),
            "billing_weight_kg": float(result.billing_weight_kg),
            "deduction_kg": float(result.deduction_kg),
            "moisture_factor": float(result.moisture_factor),
            "impurities_factor": float(result.impurities_factor),
        }

    @classmethod
    def preview_settlement(cls, payload: Any) -> dict[str, float]:
        billing_qty = cls.round_qty(
            payload.billing_quantity_kg
            if payload.billing_quantity_kg is not None
            else payload.gross_quantity_kg
        )
        amounts = cls.compute_amounts(
            billing_quantity_kg=billing_qty,
            unit_price_eur_per_ton=Decimal(str(payload.unit_price_eur_per_ton)),
            deductions=payload.deductions,
        )
        return {
            "gross_quantity_kg": float(payload.gross_quantity_kg),
            "billing_quantity_kg": float(billing_qty),
            "gross_amount_eur": float(amounts["gross_amount"]),
            "total_deductions_eur": float(amounts["total_deductions"]),
            "net_amount_eur": float(amounts["net_amount"]),
        }

    def compute_drying_from_rules(self, payload: Any) -> dict[str, Any]:
        try:
            data = _compute_drying_settlement(
                DbDryingRuleRepo(self.db, tenant_id=self.tenant_id),
                {
                    "cropCode": payload.crop_code,
                    "siteId": payload.site_id,
                    "netWeightKg": payload.net_weight_kg,
                    "moisturePct": payload.moisture_pct,
                    "calcDate": payload.calc_date,
                    "roundingMode": payload.rounding_mode,
                },
            )
        except ValueError as exc:
            raise ValidationFailedError(str(exc)) from exc
        return {
            "entzug_pct_points": float(data.entzug_pct_points),
            "loss_pct": float(data.loss_pct),
            "loss_kg": float(data.loss_kg),
            "invoice_weight_kg": float(data.invoice_weight_kg),
            "drying_fee_eur": float(data.drying_fee_eur) if data.drying_fee_eur is not None else None,
            "used_rule_set_id": data.used_rule_set_id,
            "used_rule_version": int(data.used_rule_version),
            "used_row_moisture_pct": float(data.used_row_moisture_pct) if data.used_row_moisture_pct is not None else None,
            "warnings": list(data.warnings),
        }

    @staticmethod
    def preview_trocknungs_abrechnung(payload: Any) -> dict[str, Any]:
        try:
            methode = TrocknungsMethode(payload.methode)
        except ValueError as exc:
            allowed = [m.value for m in TrocknungsMethode]
            raise ValidationFailedError(f"Unbekannte Methode: {payload.methode}. Erlaubt: {allowed}") from exc

        inp = TrocknungsInput(
            settlement_id=payload.settlement_id,
            tenant_id=payload.tenant_id,
            crop_code=payload.crop_code,
            rule_set_id=payload.rule_set_id,
            rule_set_version=payload.rule_set_version,
            brutto_gewicht_kg=Decimal(str(payload.brutto_gewicht_kg)),
            eingangs_feuchte_pct=Decimal(str(payload.eingangs_feuchte_pct)),
            ziel_feuchte_pct=Decimal(str(payload.ziel_feuchte_pct)),
            methode=methode,
        )
        defaults = get_default_trocknungsregeln()
        default_params = defaults.get(payload.crop_code.upper(), TrocknungsRegelParametrierung())
        params = TrocknungsRegelParametrierung(
            start_threshold_pct=Decimal(str(payload.start_threshold_pct)) if payload.start_threshold_pct is not None else default_params.start_threshold_pct,
            trocknungskosten_eur_per_pct_per_t=Decimal(str(payload.trocknungskosten_eur_per_pct_per_t)) if payload.trocknungskosten_eur_per_pct_per_t is not None else default_params.trocknungskosten_eur_per_pct_per_t,
            schwund_faktor=Decimal(str(payload.schwund_faktor)) if payload.schwund_faktor is not None else default_params.schwund_faktor,
            max_abzug_pct=Decimal(str(payload.max_abzug_pct)) if payload.max_abzug_pct is not None else default_params.max_abzug_pct,
        )
        ergebnis = compute_trocknungs_abrechnung(inp, params)
        validierung = validate_trocknungs_ergebnis(ergebnis)
        return {**ergebnis.as_dict(), "validierung": validierung.as_dict()}

    @staticmethod
    def get_default_trocknungsregelsets() -> dict[str, Any]:
        defaults = get_default_trocknungsregeln()
        return {
            "schema_version": 1,
            "quelle": "DLG-Empfehlungen / UFOP-Richtwerte / Handelsusancen 2024",
            "regelsets": {
                crop_code: {
                    "crop_code": crop_code,
                    "start_threshold_pct": float(params.start_threshold_pct),
                    "trocknungskosten_eur_per_pct_per_t": float(params.trocknungskosten_eur_per_pct_per_t),
                    "schwund_faktor": float(params.schwund_faktor),
                    "max_abzug_pct": float(params.max_abzug_pct) if params.max_abzug_pct is not None else None,
                }
                for crop_code, params in defaults.items()
            },
        }

    @staticmethod
    def evaluate_freigabe_stateless(payload: Any) -> dict[str, Any]:
        from app.core.settlement_approval import (
            SettlementActorType,
            SettlementApprovalRequest,
            SettlementApprovalStatus,
            evaluate_settlement_approval,
            get_allowed_transitions,
            is_terminal,
        )
        try:
            actor_type = SettlementActorType(payload.actor_type)
            target_status = SettlementApprovalStatus(payload.target_status)
            current_status = SettlementApprovalStatus(payload.current_status or "ENTWURF")
        except ValueError as exc:
            raise ValidationFailedError(str(exc)) from exc
        request = SettlementApprovalRequest(
            settlement_id="preview",
            tenant_id="system",
            actor_id=payload.actor_id,
            actor_type=actor_type,
            target_status=target_status,
            reason=payload.reason,
        )
        result = evaluate_settlement_approval(request, current_status)
        return {
            **result.audit_entry,
            "allowed_transitions": [s.value for s in get_allowed_transitions(current_status)],
            "is_terminal": is_terminal(current_status),
        }

    # ── queries ───────────────────────────────────────────────────────────────

    def list_settlements(
        self,
        supplier_id: Optional[str] = None,
        status: Optional[str] = None,
        campaign_id: Optional[str] = None,
        limit: int = 500,
    ) -> List[Tuple[AgrarSettlement, List[AgrarSettlementDeduction]]]:
        q = self.repo._base_query()
        if status:
            q = q.filter(AgrarSettlement.status == status)
        if supplier_id:
            q = q.filter(AgrarSettlement.supplier_id == supplier_id)
        if campaign_id:
            q = q.filter(AgrarSettlement.campaign_id == campaign_id)
        items = q.order_by(AgrarSettlement.created_at.desc()).limit(limit).all()
        return [(s, self.repo.list_deductions(s.id)) for s in items]

    def get_settlement(self, settlement_id: str) -> Tuple[AgrarSettlement, list]:
        settlement = self.repo.get_by_id(settlement_id)
        deductions = self.repo.list_deductions(settlement_id)
        return settlement, deductions

    # ── status helpers ────────────────────────────────────────────────────────

    @staticmethod
    def get_approval_status(settlement: AgrarSettlement) -> str:
        # Primary: drying_result["approval_status"] (set by apply_freigabe)
        drying = getattr(settlement, "drying_result", None) or {}
        if isinstance(drying, dict) and drying.get("approval_status"):
            return drying["approval_status"]
        # Fallback: legacy approval_metadata["status"]
        meta = getattr(settlement, "approval_metadata", None) or {}
        if isinstance(meta, dict):
            return meta.get("status", "ENTWURF")
        return "ENTWURF"

    @staticmethod
    def get_approval_history(settlement: AgrarSettlement) -> list[dict]:
        # Primary: drying_result["approval_history"] (written by apply_freigabe/post_to_fibu)
        drying = getattr(settlement, "drying_result", None) or {}
        if isinstance(drying, dict) and drying.get("approval_history"):
            return drying["approval_history"]
        # Fallback: legacy approval_metadata["history"]
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

    def create_settlement(
        self,
        payload: Any,
        settlement_number: Optional[str] = None,
        drying_snapshot: Optional[dict] = None,
        billing_qty_override: Optional[Decimal] = None,
    ) -> Tuple[AgrarSettlement, list]:
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
        billing_qty = billing_qty_override if billing_qty_override is not None else _round_qty(
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
            drying_result=drying_snapshot or {},
            tenant_id=self.tenant_id,
        )
        self.db.add(settlement)
        self.db.flush()

        billing_qty_tons = amounts["billing_qty_tons"]
        deduction_rows: list[AgrarSettlementDeduction] = []
        for d in payload.deductions:
            amt = _calc_deduction_amount(d, billing_qty_tons)
            row = AgrarSettlementDeduction(
                id=uuid7(),
                settlement_id=settlement.id,
                deduction_type=d.deduction_type,
                mode=d.mode,
                rate_per_ton_eur=d.rate_per_ton_eur,
                fixed_amount_eur=d.fixed_amount_eur,
                basis_quantity_tons=d.basis_quantity_tons if d.basis_quantity_tons is not None else billing_qty_tons,
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

    def post_to_fibu(self, settlement_id: str, journal_ref: str, posting_date: Optional[Any] = None) -> AgrarSettlement:
        settlement = self.repo.get_by_id(settlement_id)
        approval_status = self.get_approval_status(settlement)
        if settlement.status != "draft":
            raise ValidationFailedError(f"Settlement status '{settlement.status}' cannot be posted")
        if approval_status != "FREIGEGEBEN":
            raise ValidationFailedError(f"Settlement approval status '{approval_status}' must be FREIGEGEBEN before posting")
        effective_date = posting_date or datetime.utcnow()
        settlement.status = "posted"
        settlement.posted_journal_ref = journal_ref
        settlement.posted_at = effective_date
        new_state = dict(settlement.drying_result or {})
        new_state["approval_status"] = "VERBUCHT"
        history = list(new_state.get("approval_history") or [])
        history.append({
            "settlement_id": settlement.id,
            "event": "settlement.approval.verbucht",
            "actor_id": "system",
            "actor_type": "SYSTEM",
            "previous_status": approval_status,
            "new_status": "VERBUCHT",
            "allowed": True,
            "reason": "Settlement nach erteilter Freigabe in FiBu verbucht.",
            "decided_at": effective_date.isoformat(),
        })
        new_state["approval_history"] = history
        settlement.drying_result = new_state
        self.db.commit()
        self.db.refresh(settlement)
        return settlement

    # ── optimistic locking + commit helpers ──────────────────────────────────

    def check_row_version(self, settlement: AgrarSettlement, expected: Optional[int]) -> None:
        if expected is None:
            return
        cur = self.get_row_version(settlement)
        if cur != expected:
            raise ConflictError({
                "code": "row_version_conflict",
                "message": "Abrechnung wurde zwischenzeitlich geändert.",
                "current_row_version": cur,
                "expected_row_version": expected,
            })

    def commit_mutation(self) -> None:
        from sqlalchemy.orm.exc import StaleDataError
        try:
            self.db.commit()
        except StaleDataError:
            self.db.rollback()
            raise ConflictError({
                "code": "row_version_conflict",
                "message": "Abrechnung wurde zwischenzeitlich geändert.",
            })

    # ── approval (freigabe) ───────────────────────────────────────────────────

    def apply_freigabe(
        self,
        settlement_id: str,
        actor_id: str,
        actor_type_str: str,
        target_status_str: str,
        reason: Optional[str] = None,
        expected_row_version: Optional[int] = None,
    ) -> dict:
        from app.core.settlement_approval import (
            SettlementActorType,
            SettlementApprovalRequest,
            SettlementApprovalStatus,
            evaluate_settlement_approval,
            get_allowed_transitions,
        )
        settlement = self.repo.get_by_id(settlement_id)
        self.check_row_version(settlement, expected_row_version)
        try:
            actor_type = SettlementActorType(actor_type_str)
            target_status = SettlementApprovalStatus(target_status_str)
            approval_state = (settlement.drying_result or {}).get("approval_status", "ENTWURF")
            current_status = SettlementApprovalStatus(approval_state)
        except ValueError as exc:
            raise ValidationFailedError(str(exc))
        req = SettlementApprovalRequest(
            settlement_id=settlement_id,
            tenant_id=self.tenant_id,
            actor_id=actor_id,
            actor_type=actor_type,
            target_status=target_status,
            reason=reason,
        )
        result = evaluate_settlement_approval(req, current_status)
        if result.allowed:
            new_state = dict(settlement.drying_result or {})
            new_state["approval_status"] = result.new_status.value
            if "approval_history" not in new_state:
                new_state["approval_history"] = []
            new_state["approval_history"].append(result.audit_entry)
            settlement.drying_result = new_state
            self.commit_mutation()
        return {
            **result.audit_entry,
            "allowed_transitions": [s.value for s in get_allowed_transitions(
                result.new_status if result.allowed else current_status
            )],
        }

    # ── campaign backfill ─────────────────────────────────────────────────────

    def apply_campaign_backfill(self, settlement_ids: list[str], campaign_id: str) -> None:
        updatable = set(settlement_ids)
        settlements = (
            self.db.query(AgrarSettlement)
            .filter(
                AgrarSettlement.tenant_id == self.tenant_id,
                AgrarSettlement.id.in_(updatable),
            )
            .all()
        )
        for s in settlements:
            if str(s.id) in updatable:
                s.campaign_id = campaign_id
        self.commit_mutation()

    # ── drying pre-computation (create with inline drying) ───────────────────

    def create_settlement_with_drying(
        self,
        payload: Any,
    ) -> Tuple["AgrarSettlement", list]:
        """Run drying computation, mutate payload.deductions, then create settlement."""
        drying_snapshot: dict | None = None
        billing_qty_override = None

        if payload.drying is not None:
            if any(d.deduction_type == "drying" for d in payload.deductions):
                raise ValidationFailedError(
                    "Do not provide deductions[].deduction_type='drying' together with payload.drying"
                    " (prevents double fee application)."
                )
            gross_qty = _round_qty(payload.gross_quantity_kg)
            calc_date = payload.drying.calc_date or datetime.utcnow().date().isoformat()
            try:
                drying_result = _compute_drying_settlement(
                    DbDryingRuleRepo(self.db, tenant_id=self.tenant_id),
                    {
                        "cropCode": payload.drying.crop_code,
                        "siteId": payload.drying.site_id,
                        "netWeightKg": float(gross_qty),
                        "moisturePct": payload.drying.moisture_pct,
                        "calcDate": calc_date,
                        "roundingMode": payload.drying.rounding_mode,
                    },
                )
            except ValueError as exc:
                raise ValidationFailedError(str(exc)) from exc

            drying_snapshot = {
                "crop_code": payload.drying.crop_code,
                "site_id": payload.drying.site_id,
                "net_weight_kg": float(gross_qty),
                "moisture_pct": float(payload.drying.moisture_pct),
                "calc_date": calc_date,
                "entzug_pct_points": float(drying_result.entzug_pct_points),
                "loss_pct": float(drying_result.loss_pct),
                "loss_kg": float(drying_result.loss_kg),
                "invoice_weight_kg": float(drying_result.invoice_weight_kg),
                "drying_fee_eur": float(drying_result.drying_fee_eur) if drying_result.drying_fee_eur is not None else None,
                "used_rule_set_id": drying_result.used_rule_set_id,
                "used_rule_version": int(drying_result.used_rule_version),
                "used_row_moisture_pct": float(drying_result.used_row_moisture_pct) if drying_result.used_row_moisture_pct is not None else None,
                "warnings": list(drying_result.warnings),
            }
            if payload.billing_quantity_kg is None:
                billing_qty_override = _round_qty(drying_result.invoice_weight_kg)
            if drying_result.drying_fee_eur is not None and drying_result.drying_fee_eur > 0:
                payload.deductions.append(
                    SimpleNamespace(
                        deduction_type="drying",
                        mode="fixed",
                        fixed_amount_eur=float(drying_result.drying_fee_eur),
                        rate_per_ton_eur=None,
                        basis_quantity_tons=None,
                        note=f"Drying fee via rule-set {drying_result.used_rule_set_id} v{drying_result.used_rule_version}",
                    )
                )

        return self.create_settlement(
            payload,
            drying_snapshot=drying_snapshot,
            billing_qty_override=billing_qty_override,
        )

    def backfill_campaign_reference(self, payload: Any, campaigns: list[dict[str, Any]]) -> dict[str, Any]:
        settlements = (
            self.db.query(AgrarSettlement)
            .filter(AgrarSettlement.tenant_id == self.tenant_id)
            .filter(AgrarSettlement.campaign_id.is_(None))
            .all()
        )
        plan = self.build_campaign_backfill_plan(
            campaign_id=payload.campaign_id,
            campaigns=campaigns,
            settlements=settlements,
        )
        if payload.dry_run or plan["updated_count"] == 0:
            return plan
        self.apply_campaign_backfill(plan["updated_settlement_ids"], payload.campaign_id)
        return plan

    def export_pdf(self, settlement_id: str, archive: bool = False) -> tuple[bytes, str]:
        from app.infrastructure.models import Article
        from app.infrastructure.models.business_partner import BusinessPartner
        from app.services.settlement_pdf_service import SettlementPdfService

        settlement, deductions = self.get_settlement(settlement_id)
        supplier = self.db.query(BusinessPartner).filter(
            BusinessPartner.id == settlement.supplier_id,
            BusinessPartner.tenant_id == self.tenant_id,
        ).first()
        article = None
        if settlement.article_id:
            article = self.db.query(Article).filter(Article.id == settlement.article_id).first()

        pdf_svc = SettlementPdfService(self.db, self.tenant_id)
        if archive:
            meta = pdf_svc.generate_and_archive(settlement, deductions, supplier, article)
            pdf_bytes = meta.pop("pdf_bytes")
        else:
            pdf_bytes = pdf_svc.generate_bytes(settlement, deductions, supplier, article)
        filename = f"abrechnung_{settlement.settlement_number or settlement.id}.pdf"
        return pdf_bytes, filename

    # ── post-fibu full (FIBU booking + PDF archive) ───────────────────────────

    def post_to_fibu_full(self, settlement_id: str, payload: Any) -> dict:
        """GL-Buchung + PDF-Archivierung + Status-Übergang in einem Schritt."""
        from app.services.finance_transaction_service import FinanceTransactionService
        from app.services.settlement_pdf_service import SettlementPdfService

        settlement, _ = self.get_settlement(settlement_id)
        self.check_row_version(settlement, payload.expected_row_version)

        approval_status = self.get_approval_status(settlement)
        if approval_status != "FREIGEGEBEN":
            raise ConflictError(
                f"Settlement cannot be posted: approval_status={approval_status}. Must be FREIGEGEBEN."
            )

        posting_date = payload.posting_date or datetime.utcnow()
        journal_ref = f"JE-SET-{datetime.utcnow().strftime('%Y%m%d')}-{settlement.id[:8].upper()}"
        gross = _round_money(settlement.gross_amount_eur)
        deductions_amt = _round_money(settlement.total_deductions_eur)
        net = _round_money(settlement.net_amount_eur)

        lines = [
            {"account_id": payload.debit_account, "debit_amount": float(gross), "credit_amount": 0.0,
             "description": f"Agrar settlement {settlement.settlement_number} gross"},
            {"account_id": payload.credit_account_supplier, "debit_amount": 0.0, "credit_amount": float(net),
             "description": f"Supplier payable {settlement.supplier_id}"},
        ]
        if deductions_amt > 0:
            lines.append({"account_id": payload.credit_account_deductions, "debit_amount": 0.0,
                          "credit_amount": float(deductions_amt), "description": "Settlement deductions"})

        fin = FinanceTransactionService(self.db, self.tenant_id)
        je = fin.create(
            entry_number=journal_ref,
            description=f"Agrar settlement {settlement.settlement_number}",
            entry_date=posting_date.date() if isinstance(posting_date, datetime) else posting_date,
            lines=lines,
            reference=settlement.settlement_number,
            source="agrar_settlement",
            document_type="agrar_settlement",
            period=posting_date.strftime("%Y-%m") if isinstance(posting_date, datetime) else str(posting_date)[:7],
        )
        journal_ref = str(je.entry_number)

        settlement = self.post_to_fibu(settlement_id, journal_ref, posting_date)

        pdf_meta: dict = {}
        try:
            from app.infrastructure.models import Article
            from app.infrastructure.models.business_partner import BusinessPartner
            supplier = self.db.query(BusinessPartner).filter(
                BusinessPartner.id == settlement.supplier_id,
                BusinessPartner.tenant_id == self.tenant_id,
            ).first()
            article = None
            if settlement.article_id:
                article = self.db.query(Article).filter(Article.id == settlement.article_id).first()
            deductions_rows = self.get_settlement(settlement_id)[1]
            pdf_meta = SettlementPdfService(self.db, self.tenant_id).generate_and_archive(
                settlement, deductions_rows, supplier, article
            )
            pdf_meta.pop("pdf_bytes", None)
        except Exception as exc:
            logger.warning("Settlement PDF archiving failed (non-blocking): %s", exc)

        return {
            "ok": True,
            "settlement_id": settlement.id,
            "journal_ref": journal_ref,
            **({"pdf": pdf_meta} if pdf_meta else {}),
        }

    # ── correction draft ──────────────────────────────────────────────────────

    def get_correction_draft(self, settlement_id: str, memo_type: str) -> dict:
        """Build correction draft data for a posted settlement."""
        settlement, _ = self.get_settlement(settlement_id)
        if settlement.status != "posted":
            raise ConflictError("Correction draft requires a posted settlement")

        supplier_name = None
        try:
            from app.documents.router_helpers import get_from_store, get_repository
            partner = get_from_store("partner", settlement.supplier_id, get_repository(self.db))
            if partner:
                supplier_name = partner.get("name")
        except Exception:
            pass

        amount = float(settlement.net_amount_eur)
        route_type = "credit" if memo_type == "credit" else "debit"
        return {
            "settlement_id": settlement.id,
            "settlement_number": settlement.settlement_number,
            "memo_type": memo_type,
            "supplier_id": settlement.supplier_id,
            "supplier_name": supplier_name,
            "posted_journal_ref": settlement.posted_journal_ref,
            "suggested_reason": f"{'Gutschrift' if memo_type == 'credit' else 'Belastung'} fuer Settlement {settlement.settlement_number}",
            "suggested_notes": (
                f"Settlement-ID: {settlement.id}\n"
                f"Settlement-Nummer: {settlement.settlement_number}\n"
                f"Journal-Ref: {settlement.posted_journal_ref or '-'}\n"
                f"Lieferant: {settlement.supplier_id}\n"
                f"Bitte Korrekturgrund fachlich dokumentieren und gegen Audit-Trail freigeben."
            ),
            "suggested_route": f"/einkauf/gutschriften-belastungen/{route_type}?settlementId={settlement.id}",
            "items": [{
                "productName": settlement.article_id or "Settlement-Korrektur",
                "quantity": 1,
                "unit": "Vorgang",
                "unitPrice": amount,
                "netAmount": amount,
                "taxRate": 0,
                "taxAmount": 0,
                "grossAmount": amount,
                "reason": "Nachtraegliche Preis-, Mengen- oder Qualitaetskorrektur",
            }],
        }

    # ── completion status ─────────────────────────────────────────────────────

    def get_completion_status(self, settlement_id: str, variant: str) -> dict:
        """Evaluate completion status for a settlement (GUTSCHRIFT/BELASTUNG/KORREKTUR)."""
        from app.core.settlement_approval import SettlementApprovalStatus
        from app.core.settlement_completion_contracts import (
            SettlementCompletionEvidence,
            SettlementCompletionVariant,
            SettlementFinancialDocumentKind,
            evaluate_settlement_completion,
        )
        from app.documents.router_helpers import get_repository, list_from_store

        settlement, _ = self.get_settlement(settlement_id)
        repo = get_repository(self.db)
        linked_documents: list[dict] = []
        for memo in (list_from_store("credit_memo", repo=repo).get("data") or []):
            if memo.get("settlementId") == settlement_id:
                linked_documents.append({"memo_id": memo.get("id"), "memo_type": "credit",
                                          "status": memo.get("status"), "journal_ref": memo.get("journalRef"),
                                          "correction_mode": memo.get("correctionMode")})
        for memo in (list_from_store("debit_memo", repo=repo).get("data") or []):
            if memo.get("settlementId") == settlement_id:
                linked_documents.append({"memo_id": memo.get("id"), "memo_type": "debit",
                                          "status": memo.get("status"), "journal_ref": memo.get("journalRef"),
                                          "correction_mode": memo.get("correctionMode")})

        approval_status = self.get_approval_status(settlement)
        approval_history = self.get_approval_history(settlement)
        has_journal_entry = bool(settlement.posted_journal_ref)

        completion_variant = SettlementCompletionVariant(variant)
        document_kind = None
        document_status = None
        correction_mode = None
        correction_links_complete = False

        if completion_variant == SettlementCompletionVariant.GUTSCHRIFT:
            credit = next((d for d in linked_documents if d["memo_type"] == "credit"), None)
            document_kind = SettlementFinancialDocumentKind.GUTSCHRIFT if credit else None
            document_status = credit["status"] if credit else None
        elif completion_variant == SettlementCompletionVariant.BELASTUNG:
            debit = next((d for d in linked_documents if d["memo_type"] == "debit"), None)
            document_kind = SettlementFinancialDocumentKind.BELASTUNG if debit else None
            document_status = debit["status"] if debit else None
        else:
            credit = next((d for d in linked_documents if d["memo_type"] == "credit"), None)
            debit = next((d for d in linked_documents if d["memo_type"] == "debit"), None)
            if credit and debit:
                document_kind = SettlementFinancialDocumentKind.KORREKTUR_NEU
                document_status = "BOOKED" if credit.get("journal_ref") and debit.get("journal_ref") else credit.get("status") or debit.get("status")
                correction_mode = "STORNO_UND_NEU"
                correction_links_complete = True
            elif credit or debit:
                document_kind = SettlementFinancialDocumentKind.STORNO
                document_status = (credit or debit).get("status")
                correction_mode = (credit or debit).get("correction_mode") or "STORNO"

        result = evaluate_settlement_completion(
            SettlementCompletionEvidence(
                settlement_id=settlement_id,
                variant=completion_variant,
                approval_status=approval_status,
                has_approval_history=bool(approval_history),
                has_audit_chain=bool(approval_history),
                has_gobd_check=has_journal_entry,
                has_journal_entry=has_journal_entry,
                financial_document_kind=document_kind,
                financial_document_status=document_status,
                correction_mode=correction_mode,
                correction_links_complete=correction_links_complete,
            )
        )
        return {
            "settlement_id": result.settlement_id,
            "variant": result.variant.value,
            "completed": result.completed,
            "completion_pct": result.completion_pct,
            "missing_controls": result.missing_controls,
            "next_step": result.next_step,
            "linked_documents": linked_documents,
        }

    # ── campaign backfill plan ────────────────────────────────────────────────

    @staticmethod
    def _parse_campaign_window(campaign: dict[str, Any]) -> tuple[date, date] | None:
        try:
            return (
                date.fromisoformat(str(campaign.get("start_date"))),
                date.fromisoformat(str(campaign.get("end_date"))),
            )
        except Exception:
            return None

    @staticmethod
    def _to_created_date(value: object) -> date | None:
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
            except ValueError:
                return None
        return None

    def build_campaign_backfill_plan(
        self,
        *,
        campaign_id: str,
        campaigns: list[dict[str, Any]],
        settlements: list[AgrarSettlement],
    ) -> dict:
        """Compute which settlements would be updated, return plan dict.

        Returns dict matching SettlementCampaignBackfillResponse fields:
        campaign_id, matched_count, updated_count, ambiguous_count, skipped_count,
        updated_settlement_ids, ambiguous_settlement_ids, skipped_settlement_ids.
        """
        target_campaign = next(
            (c for c in campaigns if str(c.get("id")) == campaign_id), None
        )
        if target_campaign is None:
            raise EntityNotFoundError("Campaign", campaign_id)

        target_window = self._parse_campaign_window(target_campaign)
        if target_window is None:
            raise ValidationFailedError("Campaign date range is invalid")

        updated_ids: list[str] = []
        ambiguous_ids: list[str] = []
        skipped_ids: list[str] = []
        start_date, end_date = target_window

        valid_campaigns = [
            (c, self._parse_campaign_window(c))
            for c in campaigns
        ]
        valid_campaigns = [(c, w) for c, w in valid_campaigns if w is not None]

        for settlement in settlements:
            if getattr(settlement, "campaign_id", None):
                continue
            created_on = self._to_created_date(getattr(settlement, "created_at", None))
            if created_on is None:
                skipped_ids.append(str(settlement.id))
                continue
            if created_on < start_date or created_on > end_date:
                continue

            matching_ids = [
                str(c.get("id"))
                for c, w in valid_campaigns
                if w[0] <= created_on <= w[1]
            ]
            if campaign_id not in matching_ids:
                continue
            if len(matching_ids) > 1:
                ambiguous_ids.append(str(settlement.id))
                continue
            updated_ids.append(str(settlement.id))

        return {
            "campaign_id": campaign_id,
            "matched_count": len(updated_ids) + len(ambiguous_ids) + len(skipped_ids),
            "updated_count": len(updated_ids),
            "ambiguous_count": len(ambiguous_ids),
            "skipped_count": len(skipped_ids),
            "updated_settlement_ids": updated_ids,
            "ambiguous_settlement_ids": ambiguous_ids,
            "skipped_settlement_ids": skipped_ids,
        }
