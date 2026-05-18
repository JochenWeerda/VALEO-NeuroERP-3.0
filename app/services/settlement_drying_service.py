"""Drying calculation service for Agrar settlements (AGRAR-SET-TROCKNUNG)."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

from sqlalchemy.orm import Session

from app.core.exceptions import EntityNotFoundError, ValidationFailedError
from app.core.trocknungs_abrechnung import (
    TrocknungsInput,
    TrocknungsMethode,
    TrocknungsRegelParametrierung,
    compute_trocknungs_abrechnung,
    get_default_trocknungsregeln,
    validate_trocknungs_ergebnis,
)
from app.infrastructure.drying_rule_repo import DbDryingRuleRepo
from modules.agrar.services.drying_rule_engine import compute_settlement as _compute_drying_settlement
from modules.agrar.services.settlement_calculator import round_qty as _round_qty


class SettlementDryingService:
    """Encapsulates drying cost calculation and rule application for settlements."""

    def __init__(self, db: Session, tenant_id: str) -> None:
        self.db = db
        self.tenant_id = tenant_id
        self._drying_repo = DbDryingRuleRepo(db, tenant_id=tenant_id)

    # ── Stateless computation ─────────────────────────────────────────────────

    @staticmethod
    def calculate_drying_costs(
        gross_kg: float,
        moisture_pct: float,
        target_pct: float,
        rate_eur_per_t: float,
    ) -> float:
        """Compute drying cost using the core Trocknungsabrechnung contract.

        Uses FAKTOR_STUFUNG method with the provided rate.  Returns the total
        drying fee in EUR.

        Args:
            gross_kg: Gross incoming weight in kg.
            moisture_pct: Measured moisture at intake in %.
            target_pct: Contractual target moisture in %.
            rate_eur_per_t: Drying cost rate in EUR per percent-point per tonne.

        Returns:
            Drying fee in EUR (float, ≥ 0).
        """
        inp = TrocknungsInput(
            settlement_id="calc",
            tenant_id="system",
            crop_code="GENERIC",
            rule_set_id="manual",
            rule_set_version=1,
            brutto_gewicht_kg=Decimal(str(gross_kg)),
            eingangs_feuchte_pct=Decimal(str(moisture_pct)),
            ziel_feuchte_pct=Decimal(str(target_pct)),
            methode=TrocknungsMethode.FAKTOR_STUFUNG,
        )
        params = TrocknungsRegelParametrierung(
            start_threshold_pct=Decimal(str(target_pct)),
            trocknungskosten_eur_per_pct_per_t=Decimal(str(rate_eur_per_t)),
        )
        ergebnis = compute_trocknungs_abrechnung(inp, params)
        return float(ergebnis.gesamt_abzug_eur)

    def apply_drying_rule(
        self,
        settlement_id: str,
        drying_rule_id: str,
        db: Optional[Session] = None,
    ) -> dict:
        """Apply a configured drying rule to an existing settlement.

        Looks up the settlement, computes drying via the rule engine, and
        returns a drying snapshot dict (does NOT persist — caller decides).

        Args:
            settlement_id: ID of the settlement to apply the rule to.
            drying_rule_id: Rule-set ID in the drying rule repository.
            db: Optional override db session (falls back to self.db).

        Returns:
            Dict with drying result fields (same shape as drying_result JSONB).
        """
        session = db or self.db
        from app.repositories.agrar_settlement_repository import AgrarSettlementRepository

        repo = AgrarSettlementRepository(session, self.tenant_id)
        settlement = repo.get_by_id(settlement_id)

        gross_qty = _round_qty(float(settlement.gross_quantity_kg))
        calc_date = datetime.utcnow().date().isoformat()

        try:
            result = _compute_drying_settlement(
                self._drying_repo,
                {
                    "cropCode": settlement.article_id or "UNKNOWN",
                    "siteId": None,
                    "netWeightKg": float(gross_qty),
                    "moisturePct": float(
                        (settlement.drying_result or {}).get("moisture_pct", 0)
                    ),
                    "calcDate": calc_date,
                    "roundingMode": None,
                },
            )
        except ValueError as exc:
            raise ValidationFailedError(str(exc)) from exc

        return {
            "settlement_id": settlement_id,
            "drying_rule_id": drying_rule_id,
            "net_weight_kg": float(gross_qty),
            "calc_date": calc_date,
            "entzug_pct_points": float(result.entzug_pct_points),
            "loss_pct": float(result.loss_pct),
            "loss_kg": float(result.loss_kg),
            "invoice_weight_kg": float(result.invoice_weight_kg),
            "drying_fee_eur": float(result.drying_fee_eur) if result.drying_fee_eur is not None else None,
            "used_rule_set_id": result.used_rule_set_id,
            "used_rule_version": int(result.used_rule_version),
            "warnings": list(result.warnings),
        }

    def get_drying_summary(
        self,
        settlement_id: str,
        db: Optional[Session] = None,
    ) -> dict:
        """Return the stored drying snapshot for a settlement, or empty dict.

        Args:
            settlement_id: ID of the settlement.
            db: Optional override db session.

        Returns:
            Dict with drying snapshot fields, or {"settlement_id": ..., "drying_result": None}
            when no drying data is stored.
        """
        session = db or self.db
        from app.repositories.agrar_settlement_repository import AgrarSettlementRepository

        repo = AgrarSettlementRepository(session, self.tenant_id)
        settlement = repo.get_by_id(settlement_id)

        drying_result = settlement.drying_result or {}
        # Filter out approval fields — keep only drying-relevant keys
        drying_keys = {
            "crop_code", "site_id", "net_weight_kg", "moisture_pct", "calc_date",
            "entzug_pct_points", "loss_pct", "loss_kg", "invoice_weight_kg",
            "drying_fee_eur", "used_rule_set_id", "used_rule_version",
            "used_row_moisture_pct", "warnings",
        }
        summary = {k: v for k, v in drying_result.items() if k in drying_keys}
        return {
            "settlement_id": settlement_id,
            "has_drying_data": bool(summary),
            **summary,
        }

    # ── Crop defaults ─────────────────────────────────────────────────────────

    @staticmethod
    def get_crop_defaults(crop_code: str) -> dict:
        """Return industry-standard drying parameters for a crop code."""
        defaults = get_default_trocknungsregeln()
        params = defaults.get(crop_code.upper())
        if params is None:
            return {}
        return {
            "crop_code": crop_code.upper(),
            "start_threshold_pct": float(params.start_threshold_pct),
            "trocknungskosten_eur_per_pct_per_t": float(params.trocknungskosten_eur_per_pct_per_t),
            "schwund_faktor": float(params.schwund_faktor),
            "max_abzug_pct": float(params.max_abzug_pct) if params.max_abzug_pct is not None else None,
        }

    # ── Compute via rule engine (stateless, for endpoint delegation) ──────────

    def compute_from_rule_engine(
        self,
        crop_code: str,
        net_weight_kg: float,
        moisture_pct: float,
        calc_date: Optional[str] = None,
        site_id: Optional[str] = None,
        rounding_mode: Optional[str] = None,
    ) -> dict:
        """Compute drying result via the DB-backed rule engine.

        Returns a dict matching the DryingComputeResponse schema.

        Raises:
            ValidationFailedError: when the rule engine raises ValueError.
        """
        effective_date = calc_date or datetime.utcnow().date().isoformat()
        try:
            result = _compute_drying_settlement(
                self._drying_repo,
                {
                    "cropCode": crop_code,
                    "siteId": site_id,
                    "netWeightKg": net_weight_kg,
                    "moisturePct": moisture_pct,
                    "calcDate": effective_date,
                    "roundingMode": rounding_mode,
                },
            )
        except ValueError as exc:
            raise ValidationFailedError(str(exc)) from exc

        return {
            "entzug_pct_points": float(result.entzug_pct_points),
            "loss_pct": float(result.loss_pct),
            "loss_kg": float(result.loss_kg),
            "invoice_weight_kg": float(result.invoice_weight_kg),
            "drying_fee_eur": float(result.drying_fee_eur) if result.drying_fee_eur is not None else None,
            "used_rule_set_id": result.used_rule_set_id,
            "used_rule_version": int(result.used_rule_version),
            "used_row_moisture_pct": float(result.used_row_moisture_pct) if result.used_row_moisture_pct is not None else None,
            "warnings": list(result.warnings),
        }
