"""Tests fuer das Constraint-Meta-Modell (RATION-CANON-02, Skill §5).

Kern ist der **Konsistenztest** gegen die produktive Klassifikation
``_CONSTRAINT_CLASSIFICATION`` im Endpoint: das Meta-Modell darf nicht vom realen
Solververhalten abdriften. Zusaetzlich die Invariante §11.2 (safety_hard nie
auto-relaxiert).

Reine Unit-Tests. Der Import des Endpoints laedt viel Modulcode, laeuft aber
ohne DB. Ausfuehrung:

    pytest tests/test_rations_constraint_meta.py \
        --noconftest -p no:cacheprovider --no-cov -o addopts=""
"""

import pytest

from app.agrar.rations.constraint_meta import (
    CONSTRAINT_META,
    Hardness,
    SourceType,
    assert_safety_hard_not_relaxed,
    get_meta,
    is_auto_relaxable,
    meta_row,
    safety_hard_names,
)


class TestHardnessInvariant:
    def test_safety_and_business_hard_never_relaxable(self):
        for name, meta in CONSTRAINT_META.items():
            if meta.hardness in (Hardness.SAFETY_HARD, Hardness.BUSINESS_HARD):
                assert meta.relaxable is False, f"{name} darf nicht relaxierbar sein"

    def test_advisory_and_working_are_relaxable(self):
        for name, meta in CONSTRAINT_META.items():
            if meta.hardness in (Hardness.ADVISORY, Hardness.SOLVER_WORKING):
                assert meta.relaxable is True, f"{name} sollte relaxierbar sein"

    def test_is_auto_relaxable_matches_hardness(self):
        assert is_auto_relaxable("ME (MJ/d)") is False  # business_hard
        assert is_auto_relaxable("Magnesium (g/d)") is False  # safety_hard
        assert is_auto_relaxable("XL Rohfett (g/kg TM)") is True  # advisory

    def test_unknown_constraint_is_fail_safe_not_relaxable(self):
        assert is_auto_relaxable("voellig-unbekannt") is False
        assert get_meta("voellig-unbekannt") is None


class TestSafetyHardGuard:
    def test_guard_passes_when_only_advisory_relaxed(self):
        # Darf nicht werfen.
        assert_safety_hard_not_relaxed(
            ["XL Rohfett (g/kg TM)", "aNDFom (g/d)", "K:Mg-Ratio"]
        )

    def test_guard_raises_when_safety_hard_relaxed(self):
        with pytest.raises(AssertionError):
            assert_safety_hard_not_relaxed(["Magnesium (g/d)"])

    def test_safety_hard_names_nonempty_and_include_minerals(self):
        names = set(safety_hard_names())
        assert {"Calcium (g/d)", "Phosphor (g/d)", "Magnesium (g/d)"} <= names


class TestMetaRow:
    def test_known_row_has_hardness_and_source(self):
        row = meta_row("ME (MJ/d)")
        assert row["hardness"] == "business_hard"
        assert row["source_type"] == "gfe"
        assert row["relaxable"] is False
        assert isinstance(row["priority"], int)

    def test_unknown_row_is_conservative(self):
        row = meta_row("unbekannt")
        assert row["hardness"] is None
        assert row["relaxable"] is False

    def test_priority_orders_safety_above_advisory(self):
        assert meta_row("Magnesium (g/d)")["priority"] > meta_row("XL Rohfett (g/kg TM)")["priority"]


class TestConsistencyWithLiveClassification:
    """Bindet das Meta-Modell an die produktive LP-Klassifikation."""

    def _live_table(self):
        from app.api.v1.endpoints.rations_optimization import (
            _CONSTRAINT_CLASSIFICATION,
        )

        return _CONSTRAINT_CLASSIFICATION

    def test_every_meta_name_exists_in_live_table(self):
        live = self._live_table()
        missing = [n for n in CONSTRAINT_META if n not in live]
        assert not missing, f"Meta-Namen fehlen in _CONSTRAINT_CLASSIFICATION: {missing}"

    def test_every_live_name_has_meta(self):
        live = self._live_table()
        missing = [n for n in live if n not in CONSTRAINT_META]
        assert not missing, f"Live-Constraints ohne Meta-Eintrag: {missing}"

    def test_kind_and_penalty_class_match_live(self):
        live = self._live_table()
        for name, meta in CONSTRAINT_META.items():
            kind, klass, _unit, _hw, _dir = live[name]
            assert meta.expected_kind == kind, (
                f"{name}: expected_kind {meta.expected_kind} != live {kind}"
            )
            assert meta.penalty_class == klass, (
                f"{name}: penalty_class {meta.penalty_class} != live {klass}"
            )

    def test_hard_live_constraints_are_never_auto_relaxable(self):
        """Der eigentliche Sicherheitsnachweis: jede LP-harte Grenze ist im
        Meta-Modell nicht auto-relaxierbar."""
        live = self._live_table()
        for name, (kind, *_rest) in live.items():
            if kind == "hart":
                assert is_auto_relaxable(name) is False, (
                    f"LP-harte Grenze {name} darf nicht auto-relaxierbar sein"
                )

    def test_soft_live_constraints_are_advisory_or_working(self):
        live = self._live_table()
        for name, (kind, *_rest) in live.items():
            if kind == "weich":
                meta = get_meta(name)
                assert meta is not None
                assert meta.hardness in (Hardness.ADVISORY, Hardness.SOLVER_WORKING)


class TestEnumsSerializable:
    def test_hardness_is_plain_string(self):
        assert Hardness.SAFETY_HARD.value == "safety_hard"
        assert isinstance(Hardness.SAFETY_HARD.value, str)

    def test_source_type_values(self):
        vals = {s.value for s in SourceType}
        assert {"law", "gfe", "dlg", "farm_policy", "advisor"} <= vals
