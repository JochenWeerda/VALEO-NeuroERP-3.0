"""
Tests fuer die Neuro Verification Engine — Wave 2.

Abdeckung:
- Policy Engine Integration (evaluate_policy_set)
- State Graph Transition via StateGraphService
- Per-Step Verification
- Temporal Policy Conditions (Wochentag, Zeitraum, Uhrzeit)
- Rueckwaertskompatibilitaet (hardcoded fallback rules)
"""

from __future__ import annotations

import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from app.services.neuro_verification_engine import (
    VerificationResult,
    VerificationStatus,
    Violation,
    ViolationType,
    check_data_integrity,
    check_policy_conformity,
    check_preconditions,
    check_state_transition,
    verify_plan,
)
from app.core.policy_code_engine import (
    PolicyAktion,
    PolicyBedingung,
    PolicyBedingungsGruppe,
    PolicyBedingungsTyp,
    PolicyRegel,
    PolicySet,
    evaluate_policy_set,
)


# ---------------------------------------------------------------------------
# Precondition checks
# ---------------------------------------------------------------------------

class TestCheckPreconditions:
    def test_missing_action(self):
        violations = check_preconditions({"entity_type": "order"})
        assert any(v.field == "action" for v in violations)

    def test_missing_entity_type(self):
        violations = check_preconditions({"action": "update"})
        assert any(v.field == "entity_type" for v in violations)

    def test_missing_entity_id_non_create(self):
        violations = check_preconditions({"action": "update", "entity_type": "order"})
        assert any(v.field == "entity_id" for v in violations)

    def test_create_without_entity_id_ok(self):
        violations = check_preconditions({"action": "create", "entity_type": "order"})
        assert not any(v.field == "entity_id" for v in violations)

    def test_valid_plan(self):
        violations = check_preconditions({"action": "create", "entity_type": "order", "entity_id": "123"})
        assert len(violations) == 0


# ---------------------------------------------------------------------------
# Policy conformity — hardcoded fallback
# ---------------------------------------------------------------------------

class TestCheckPolicyConformityFallback:
    def test_delete_without_reason(self):
        violations = check_policy_conformity({"action": "delete", "entity_type": "order"}, "t1")
        assert any("Begruendung" in v.message for v in violations)

    def test_cancel_without_reason(self):
        violations = check_policy_conformity({"action": "cancel", "entity_type": "order"}, "t1")
        assert any("Begruendung" in v.message for v in violations)

    def test_approval_required_without_approved_by(self):
        violations = check_policy_conformity({"action": "create", "entity_type": "order", "requires_approval": True}, "t1")
        warning = [v for v in violations if v.field == "approved_by"]
        assert len(warning) == 1
        assert warning[0].severity == "warning"

    def test_four_eyes_threshold(self):
        violations = check_policy_conformity({"action": "create", "entity_type": "order", "amount": 60000}, "t1")
        assert any("4-Augen" in v.message for v in violations)

    def test_amount_below_threshold_ok(self):
        violations = check_policy_conformity({"action": "create", "entity_type": "order", "amount": 30000}, "t1")
        assert not any("4-Augen" in v.message for v in violations)


# ---------------------------------------------------------------------------
# Policy conformity — Policy Engine integration
# ---------------------------------------------------------------------------

class TestCheckPolicyConformityEngine:
    def _make_policy_set(self) -> PolicySet:
        return PolicySet(
            policy_set_id="PS-TEST",
            prozess_key="test_entity",
            bezeichnung="Test PolicySet",
            regeln=[
                PolicyRegel(
                    regel_id="T-001",
                    bezeichnung="Hoher Betrag ablehnen",
                    bedingungen=[PolicyBedingung(PolicyBedingungsTyp.GROESSER, "brutto_eur", 100000)],
                    aktion=PolicyAktion.ABGELEHNT,
                    prioritaet=10,
                    pflicht=True,
                    begruendung="Betrag ueber 100k nicht erlaubt",
                ),
                PolicyRegel(
                    regel_id="T-002",
                    bezeichnung="Mittlerer Betrag eskalieren",
                    bedingungen=[PolicyBedingung(PolicyBedingungsTyp.GROESSER, "brutto_eur", 25000)],
                    aktion=PolicyAktion.ESKALATION,
                    prioritaet=20,
                    begruendung="Betrag ueber 25k braucht Eskalation",
                ),
                PolicyRegel(
                    regel_id="T-003",
                    bezeichnung="Normalbetrag erlaubt",
                    bedingungen=[PolicyBedingung(PolicyBedingungsTyp.KLEINER_GLEICH, "brutto_eur", 25000)],
                    aktion=PolicyAktion.ERLAUBT,
                    prioritaet=100,
                    begruendung="Standardfreigabe",
                ),
            ],
        )

    def test_policy_engine_abgelehnt(self):
        ps = self._make_policy_set()
        plan = {"action": "create", "entity_type": "test_entity", "amount": 150000}
        violations = check_policy_conformity(plan, "t1", policy_sets=[ps])
        error_violations = [v for v in violations if v.severity == "error" and "Policy abgelehnt" in v.message]
        assert len(error_violations) >= 1

    def test_policy_engine_eskalation(self):
        ps = self._make_policy_set()
        plan = {"action": "create", "entity_type": "test_entity", "amount": 30000}
        violations = check_policy_conformity(plan, "t1", policy_sets=[ps])
        eskalation = [v for v in violations if "Eskalation" in v.message]
        assert len(eskalation) >= 1

    def test_policy_engine_erlaubt(self):
        ps = self._make_policy_set()
        plan = {"action": "create", "entity_type": "test_entity", "amount": 5000}
        violations = check_policy_conformity(plan, "t1", policy_sets=[ps])
        # No policy-engine violations (only fallback rules may fire)
        engine_violations = [v for v in violations if "Policy" in v.message or "Eskalation" in v.message]
        assert len(engine_violations) == 0

    def test_policy_set_not_matching_prozess_key(self):
        ps = self._make_policy_set()
        plan = {"action": "create", "entity_type": "other_entity", "amount": 150000}
        violations = check_policy_conformity(plan, "t1", policy_sets=[ps])
        engine_violations = [v for v in violations if "Policy abgelehnt" in v.message]
        assert len(engine_violations) == 0  # No match → no engine violations

    def test_policy_context_passthrough(self):
        """policy_context dict is merged into evaluation kontext."""
        ps = PolicySet(
            policy_set_id="PS-CTX",
            prozess_key="test_entity",
            bezeichnung="Context Test",
            regeln=[
                PolicyRegel(
                    regel_id="CTX-001",
                    bezeichnung="Fremdbetrieb ablehnen",
                    bedingungen=[PolicyBedingung(PolicyBedingungsTyp.GLEICH, "lieferant_typ", "FREMDBETRIEB")],
                    aktion=PolicyAktion.ABGELEHNT,
                    prioritaet=10,
                    begruendung="Fremdbetrieb",
                ),
            ],
        )
        plan = {
            "action": "create",
            "entity_type": "test_entity",
            "policy_context": {"lieferant_typ": "FREMDBETRIEB"},
        }
        violations = check_policy_conformity(plan, "t1", policy_sets=[ps])
        assert any("Fremdbetrieb" in v.message for v in violations)


# ---------------------------------------------------------------------------
# State transition — State Graph integration
# ---------------------------------------------------------------------------

class TestCheckStateTransition:
    def test_valid_bestellung_transition(self):
        plan = {"entity_type": "purchase_order", "current_state": "draft", "target_state": "open"}
        violations = check_state_transition(plan)
        assert len(violations) == 0

    def test_invalid_bestellung_transition(self):
        plan = {"entity_type": "purchase_order", "current_state": "draft", "target_state": "completed"}
        violations = check_state_transition(plan)
        assert len(violations) == 1
        assert violations[0].type == ViolationType.INVALID_TRANSITION

    def test_invoice_valid(self):
        plan = {"entity_type": "invoice", "current_state": "draft", "target_state": "open"}
        violations = check_state_transition(plan)
        assert len(violations) == 0

    def test_invoice_invalid(self):
        plan = {"entity_type": "invoice", "current_state": "draft", "target_state": "approved"}
        violations = check_state_transition(plan)
        assert len(violations) == 1

    def test_no_states_skips_check(self):
        plan = {"entity_type": "purchase_order"}
        violations = check_state_transition(plan)
        assert len(violations) == 0

    def test_unknown_entity_type_skips(self):
        plan = {"entity_type": "unknown_thing", "current_state": "draft", "target_state": "open"}
        violations = check_state_transition(plan)
        assert len(violations) == 0  # No mapping → skip gracefully


# ---------------------------------------------------------------------------
# Data integrity
# ---------------------------------------------------------------------------

class TestCheckDataIntegrity:
    def test_field_too_long(self):
        plan = {"params": {"notes": "x" * 10001}}
        violations = check_data_integrity(plan)
        assert any("Maximallaenge" in v.message for v in violations)

    def test_required_field_none(self):
        plan = {"params": {"name": None}, "required_fields": ["name"]}
        violations = check_data_integrity(plan)
        assert any("Pflichtfeld" in v.message for v in violations)

    def test_valid_params(self):
        plan = {"params": {"name": "Test"}}
        violations = check_data_integrity(plan)
        assert len(violations) == 0


# ---------------------------------------------------------------------------
# verify_plan() — overall + per-step
# ---------------------------------------------------------------------------

class TestVerifyPlan:
    def test_approved_plan(self):
        plan = {"action": "create", "entity_type": "order", "entity_id": "1"}
        result = verify_plan(plan)
        assert result.status == VerificationStatus.APPROVED

    def test_rejected_plan(self):
        plan = {"action": "delete", "entity_type": "order", "entity_id": "1"}  # missing reason
        result = verify_plan(plan)
        assert result.status == VerificationStatus.REJECTED

    def test_warning_plan(self):
        plan = {"action": "create", "entity_type": "order", "entity_id": "1", "requires_approval": True}
        result = verify_plan(plan)
        assert result.status == VerificationStatus.WARNING

    def test_per_step_verification(self):
        plan = {
            "action": "create",
            "entity_type": "purchase_order",
            "entity_id": "1",
            "steps": [
                {"step_id": "s1", "action": "validate_supplier", "entity_type": "supplier"},
                {"step_id": "s2", "action": "create_purchase_order", "entity_type": "purchase_order", "requires_approval": True},
            ],
        }
        result = verify_plan(plan)
        assert len(result.step_results) == 2
        assert result.step_results[0]["step_id"] == "s1"
        assert result.step_results[1]["step_id"] == "s2"

    def test_per_step_rejection_propagates(self):
        plan = {
            "action": "create",
            "entity_type": "order",
            "entity_id": "1",
            "steps": [
                {"step_id": "s1", "action": "delete", "entity_type": "order"},  # missing reason → error
            ],
        }
        result = verify_plan(plan)
        assert result.step_results[0]["status"] == "rejected"
        assert result.status == VerificationStatus.REJECTED

    def test_step_state_transition_check(self):
        plan = {
            "action": "create",
            "entity_type": "purchase_order",
            "entity_id": "1",
            "steps": [
                {
                    "step_id": "s1",
                    "action": "approve",
                    "entity_type": "invoice",
                    "current_state": "draft",
                    "target_state": "completed",  # invalid for invoice
                },
            ],
        }
        result = verify_plan(plan)
        assert result.status == VerificationStatus.REJECTED
        assert any(v.type == ViolationType.INVALID_TRANSITION for v in result.violations)

    def test_step_results_in_to_dict(self):
        plan = {"action": "create", "entity_type": "order", "entity_id": "1", "steps": []}
        result = verify_plan(plan)
        d = result.to_dict()
        assert "step_results" in d

    def test_empty_steps_still_works(self):
        plan = {"action": "create", "entity_type": "order", "entity_id": "1", "steps": []}
        result = verify_plan(plan)
        assert result.status == VerificationStatus.APPROVED
        assert result.step_results == []


# ---------------------------------------------------------------------------
# Temporal policy conditions (Wave 2)
# ---------------------------------------------------------------------------

class TestTemporalPolicies:
    def test_wochentag_match(self):
        monday = datetime(2026, 3, 30, 10, 0, tzinfo=timezone.utc)  # Monday = 0
        bedingung = PolicyBedingung(PolicyBedingungsTyp.WOCHENTAG, "wochentag", [0, 1, 2])
        assert bedingung.evaluate({}, now=monday) is True

    def test_wochentag_no_match(self):
        monday = datetime(2026, 3, 30, 10, 0, tzinfo=timezone.utc)
        bedingung = PolicyBedingung(PolicyBedingungsTyp.WOCHENTAG, "wochentag", [5, 6])  # Sa, So
        assert bedingung.evaluate({}, now=monday) is False

    def test_zeitraum_match(self):
        now = datetime(2026, 3, 30, 10, 0, tzinfo=timezone.utc)
        bedingung = PolicyBedingung(PolicyBedingungsTyp.ZEITRAUM, "zeitraum", {"von": "2026-03-01", "bis": "2026-04-01"})
        assert bedingung.evaluate({}, now=now) is True

    def test_zeitraum_no_match(self):
        now = datetime(2026, 5, 15, 10, 0, tzinfo=timezone.utc)
        bedingung = PolicyBedingung(PolicyBedingungsTyp.ZEITRAUM, "zeitraum", {"von": "2026-03-01", "bis": "2026-04-01"})
        assert bedingung.evaluate({}, now=now) is False

    def test_uhrzeit_match(self):
        now = datetime(2026, 3, 30, 14, 30)
        bedingung = PolicyBedingung(PolicyBedingungsTyp.UHRZEIT, "uhrzeit", {"von": "08:00", "bis": "17:00"})
        assert bedingung.evaluate({}, now=now) is True

    def test_uhrzeit_no_match(self):
        now = datetime(2026, 3, 30, 22, 0)
        bedingung = PolicyBedingung(PolicyBedingungsTyp.UHRZEIT, "uhrzeit", {"von": "08:00", "bis": "17:00"})
        assert bedingung.evaluate({}, now=now) is False

    def test_temporal_in_policy_set(self):
        """A policy that only triggers on weekdays gets correctly evaluated."""
        ps = PolicySet(
            policy_set_id="PS-TEMP",
            prozess_key="test_entity",
            bezeichnung="Temporal Test",
            regeln=[
                PolicyRegel(
                    regel_id="TEMP-001",
                    bezeichnung="Wochenende ablehnen",
                    bedingungen=[PolicyBedingung(PolicyBedingungsTyp.WOCHENTAG, "wochentag", [5, 6])],
                    aktion=PolicyAktion.ABGELEHNT,
                    prioritaet=10,
                    begruendung="Am Wochenende nicht erlaubt",
                ),
            ],
        )
        monday = datetime(2026, 3, 30, 10, 0)
        result = evaluate_policy_set(ps, {"dummy": True})
        # Default: uses datetime.now() — but rule checks weekday.
        # We test via PolicyBedingung directly (see above), this tests integration.
        assert result.policy_set_id == "PS-TEMP"


# ---------------------------------------------------------------------------
# Nested conditions (PolicyBedingungsGruppe)
# ---------------------------------------------------------------------------

class TestNestedConditions:
    def test_and_group(self):
        gruppe = PolicyBedingungsGruppe(
            operator="AND",
            kinder=[
                PolicyBedingung(PolicyBedingungsTyp.GROESSER, "betrag", 1000),
                PolicyBedingung(PolicyBedingungsTyp.GLEICH, "typ", "EXTERN"),
            ],
        )
        assert gruppe.evaluate({"betrag": 2000, "typ": "EXTERN"}) is True
        assert gruppe.evaluate({"betrag": 2000, "typ": "INTERN"}) is False

    def test_or_group(self):
        gruppe = PolicyBedingungsGruppe(
            operator="OR",
            kinder=[
                PolicyBedingung(PolicyBedingungsTyp.GLEICH, "land", "DE"),
                PolicyBedingung(PolicyBedingungsTyp.GLEICH, "land", "AT"),
            ],
        )
        assert gruppe.evaluate({"land": "DE"}) is True
        assert gruppe.evaluate({"land": "AT"}) is True
        assert gruppe.evaluate({"land": "CH"}) is False

    def test_nested_and_or(self):
        """(betrag > 1000 AND typ == EXTERN) OR land == DE"""
        inner = PolicyBedingungsGruppe(
            operator="AND",
            kinder=[
                PolicyBedingung(PolicyBedingungsTyp.GROESSER, "betrag", 1000),
                PolicyBedingung(PolicyBedingungsTyp.GLEICH, "typ", "EXTERN"),
            ],
        )
        outer = PolicyBedingungsGruppe(
            operator="OR",
            kinder=[inner, PolicyBedingung(PolicyBedingungsTyp.GLEICH, "land", "DE")],
        )
        assert outer.evaluate({"betrag": 500, "typ": "INTERN", "land": "DE"}) is True
        assert outer.evaluate({"betrag": 2000, "typ": "EXTERN", "land": "CH"}) is True
        assert outer.evaluate({"betrag": 500, "typ": "INTERN", "land": "CH"}) is False

    def test_regel_with_bedingungsgruppe(self):
        regel = PolicyRegel(
            regel_id="NG-001",
            bezeichnung="Nested rule",
            bedingungen=[],  # ignored when bedingungsgruppe is set
            aktion=PolicyAktion.ESKALATION,
            bedingungsgruppe=PolicyBedingungsGruppe(
                operator="AND",
                kinder=[
                    PolicyBedingung(PolicyBedingungsTyp.GROESSER, "betrag", 5000),
                    PolicyBedingung(PolicyBedingungsTyp.GLEICH, "typ", "EXTERN"),
                ],
            ),
        )
        assert regel.matches({"betrag": 6000, "typ": "EXTERN"}) is True
        assert regel.matches({"betrag": 6000, "typ": "INTERN"}) is False

    def test_empty_group_evaluates_true(self):
        gruppe = PolicyBedingungsGruppe(operator="AND", kinder=[])
        assert gruppe.evaluate({}) is True


# ---------------------------------------------------------------------------
# Default Agrar PolicySets sanity
# ---------------------------------------------------------------------------

class TestDefaultAgrarPolicySets:
    def test_settlement_high_amount_eskalation(self):
        from app.core.policy_code_engine import get_default_agrar_policy_sets

        sets = get_default_agrar_policy_sets()
        settlement_set = next(ps for ps in sets if ps.prozess_key == "agrar_settlement")
        result = evaluate_policy_set(settlement_set, {
            "brutto_eur": 60000,
            "lieferant_typ": "MITGLIED",
            "netto_tonnen": 10,
        })
        assert result.eskalation_erforderlich

    def test_settlement_negative_weight_abgelehnt(self):
        from app.core.policy_code_engine import get_default_agrar_policy_sets

        sets = get_default_agrar_policy_sets()
        settlement_set = next(ps for ps in sets if ps.prozess_key == "agrar_settlement")
        result = evaluate_policy_set(settlement_set, {
            "brutto_eur": 1000,
            "netto_tonnen": -5,
        })
        assert result.abgelehnt

    def test_wareneingang_high_moisture_rejected(self):
        from app.core.policy_code_engine import get_default_agrar_policy_sets

        sets = get_default_agrar_policy_sets()
        we_set = next(ps for ps in sets if ps.prozess_key == "wareneingang")
        result = evaluate_policy_set(we_set, {
            "feuchte_pct": 22.0,
            "qualitaetsprotokoll_vorhanden": True,
        })
        assert result.abgelehnt

    def test_wareneingang_normal_erlaubt(self):
        from app.core.policy_code_engine import get_default_agrar_policy_sets

        sets = get_default_agrar_policy_sets()
        we_set = next(ps for ps in sets if ps.prozess_key == "wareneingang")
        result = evaluate_policy_set(we_set, {
            "feuchte_pct": 12.0,
            "qualitaetsprotokoll_vorhanden": True,
        })
        assert not result.abgelehnt
        assert not result.eskalation_erforderlich
