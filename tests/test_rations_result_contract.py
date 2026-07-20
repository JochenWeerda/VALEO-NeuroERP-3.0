"""Tests fuer den kanonischen Ergebnisvertrag (RATION-CANON-01).

Deckt Skill §4.4 (Statusenum), §3/Phase 2 (Erreichbarkeits-Fuenfling) und die
Invariante §2.3/§11.2 (Wunschleistung nie als erreicht ausgeben, wenn die
Versorgung sie nicht deckt) ab.

Reine Unit-Tests ohne DB/HTTP – Ausfuehrung z. B.:

    pytest tests/test_rations_result_contract.py \
        --noconftest -p no:cacheprovider --no-cov -o addopts=""
"""

import pytest

from app.agrar.rations.contract import (
    AttainabilityReport,
    RationResultStatus,
    build_attainability,
    build_result_contract,
    derive_result_status,
    limiting_axis_from_milk,
)


class TestLimitingAxis:
    def test_energy_limits(self):
        assert limiting_axis_from_milk(34.0, 37.0) == "energy"

    def test_protein_limits(self):
        assert limiting_axis_from_milk(38.0, 35.5) == "protein"

    def test_tie_is_none(self):
        assert limiting_axis_from_milk(36.0, 36.0) is None

    def test_missing_is_none(self):
        assert limiting_axis_from_milk(None, 36.0) is None
        assert limiting_axis_from_milk(36.0, None) is None


class TestBuildAttainability:
    def test_gap_positive_when_undersupplied(self):
        rep = build_attainability(target=38.0, safe_attainable=34.0)
        assert rep.target_gap == pytest.approx(4.0)
        assert rep.meets_target is False

    def test_gap_negative_when_exceeded(self):
        rep = build_attainability(target=34.0, safe_attainable=37.6)
        assert rep.target_gap == pytest.approx(-3.6)
        assert rep.meets_target is True

    def test_within_tolerance_counts_as_met(self):
        rep = build_attainability(target=38.0, safe_attainable=37.6, tolerance_kg=0.5)
        assert rep.meets_target is True
        assert rep.target_gap == pytest.approx(0.4)

    def test_just_outside_tolerance_not_met(self):
        rep = build_attainability(target=38.0, safe_attainable=37.4, tolerance_kg=0.5)
        assert rep.meets_target is False

    def test_no_target_means_nothing_to_miss(self):
        rep = build_attainability(target=0.0, safe_attainable=30.0)
        assert rep.meets_target is True
        assert rep.target_gap is None

    def test_missing_safe_attainable_gap_none(self):
        rep = build_attainability(target=38.0, safe_attainable=None)
        assert rep.target_gap is None
        assert rep.meets_target is False

    def test_technical_max_not_fabricated(self):
        # Skill §10.3: fehlender Kennwert bleibt None, keine Schaetzung.
        rep = build_attainability(target=38.0, safe_attainable=34.0)
        assert rep.technical_max is None

    def test_to_dict_rounds_to_one_decimal(self):
        rep = build_attainability(target=38.0, safe_attainable=34.5555)
        d = rep.to_dict()
        assert d["safe_attainable"] == 34.6
        assert d["unit"] == "kg_milk_day"


class TestDeriveResultStatusSuccess:
    def _rep(self, target, safe, tol=0.5):
        return build_attainability(target=target, safe_attainable=safe, tolerance_kg=tol)

    def test_feasible_optimal(self):
        rep = self._rep(38.0, 38.0)
        st = derive_result_status(solver_ok=True, attainability=rep)
        assert st is RationResultStatus.FEASIBLE_OPTIMAL

    def test_feasible_non_optimal(self):
        rep = self._rep(38.0, 38.0)
        st = derive_result_status(solver_ok=True, attainability=rep, optimal=False)
        assert st is RationResultStatus.FEASIBLE_NON_OPTIMAL

    def test_relaxed_acceptable(self):
        rep = self._rep(38.0, 38.0)
        st = derive_result_status(
            solver_ok=True, attainability=rep, relaxation_applied=True
        )
        assert st is RationResultStatus.RELAXED_ACCEPTABLE

    def test_best_attainable_when_target_missed_with_relaxation(self):
        rep = self._rep(38.0, 35.6)
        st = derive_result_status(
            solver_ok=True, attainability=rep, relaxation_applied=True
        )
        assert st is RationResultStatus.BEST_ATTAINABLE

    def test_target_not_attainable_without_relaxation(self):
        # Golden Case 1: Ziel 38, nur 34 deckbar.
        rep = self._rep(38.0, 34.0)
        st = derive_result_status(solver_ok=True, attainability=rep)
        assert st is RationResultStatus.TARGET_NOT_ATTAINABLE


class TestDeriveResultStatusFailure:
    def test_infeasible_constraint_conflict(self):
        # Golden Case 2/3: harte Grenzen widersprechen sich.
        rep = build_attainability(target=38.0, safe_attainable=None)
        st = derive_result_status(
            solver_ok=False, attainability=rep, constraint_conflict=True
        )
        assert st is RationResultStatus.CONSTRAINT_CONFLICT

    def test_infeasible_data_incomplete(self):
        # Golden Case 12: fehlende Analysewerte.
        rep = build_attainability(target=38.0, safe_attainable=None)
        st = derive_result_status(
            solver_ok=False, attainability=rep, data_incomplete=True
        )
        assert st is RationResultStatus.DATA_INCOMPLETE

    def test_infeasible_generic_target_not_attainable(self):
        rep = build_attainability(target=38.0, safe_attainable=None)
        st = derive_result_status(solver_ok=False, attainability=rep)
        assert st is RationResultStatus.TARGET_NOT_ATTAINABLE

    def test_unsafe_rejected_wins_over_everything(self):
        # Invariante §11.2: Sicherheitsgrenze schlaegt jeden anderen Status.
        rep = build_attainability(target=38.0, safe_attainable=38.0)
        st = derive_result_status(
            solver_ok=True,
            attainability=rep,
            relaxation_applied=True,
            unsafe_rejected=True,
        )
        assert st is RationResultStatus.UNSAFE_REJECTED

    def test_solver_ok_but_data_incomplete_is_flagged(self):
        rep = build_attainability(target=38.0, safe_attainable=38.0)
        st = derive_result_status(
            solver_ok=True, attainability=rep, data_incomplete=True
        )
        assert st is RationResultStatus.DATA_INCOMPLETE


class TestInvariantWishNotTruth:
    """Skill §2.3: Die Wunschleistung darf nicht als erreicht gelten, wenn die
    Versorgung sie nicht deckt."""

    def test_target_not_met_never_maps_to_feasible_optimal(self):
        rep = build_attainability(target=40.0, safe_attainable=34.0)
        st = derive_result_status(solver_ok=True, attainability=rep)
        assert st is not RationResultStatus.FEASIBLE_OPTIMAL
        assert rep.meets_target is False


class TestBuildResultContractFacade:
    def test_facade_shapes_full_contract(self):
        contract = build_result_contract(
            solver_ok=True,
            target=38.0,
            safe_attainable=34.0,
            milk_from_energy=34.0,
            milk_from_protein=37.0,
        )
        assert contract["result_status"] == "TARGET_NOT_ATTAINABLE"
        att = contract["attainability"]
        assert att["safe_attainable"] == 34.0
        assert att["target"] == 38.0
        assert att["target_gap"] == 4.0
        assert att["limiting_axis"] == "energy"
        assert att["meets_target"] is False
        assert att["technical_max"] is None

    def test_facade_status_is_plain_string(self):
        contract = build_result_contract(
            solver_ok=True, target=0.0, safe_attainable=30.0
        )
        assert isinstance(contract["result_status"], str)
        assert contract["result_status"] == "FEASIBLE_OPTIMAL"

    def test_facade_infeasible_has_null_safe_attainable(self):
        contract = build_result_contract(
            solver_ok=False, target=38.0, safe_attainable=None
        )
        assert contract["attainability"]["safe_attainable"] is None
        assert contract["result_status"] == "TARGET_NOT_ATTAINABLE"


class TestReportDataclassDefaults:
    def test_defaults_are_none_not_zero(self):
        rep = AttainabilityReport()
        assert rep.baseline_supported is None
        assert rep.safe_attainable is None
        assert rep.technical_max is None
        assert rep.unit == "kg_milk_day"
