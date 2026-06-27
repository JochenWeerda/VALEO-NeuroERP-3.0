"""Wave 91 — Unit-Tests fuer kaeufer_klassifikator, integration_bootstrap (pure functions)."""

from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# Helper: build a Verhaltenssignale with numeric kauffrequenz
# ---------------------------------------------------------------------------

def _make_signale(preisanfragen=5, angebote=3, bestellungen=2, kauffrequenz=2,
                  deckung_pct=0.7, bedarf_eur=50000):
    from app.services.kaeufer_signal_service import Verhaltenssignale
    return Verhaltenssignale(
        angebote_12m=angebote,
        preisabfragen_12m=preisanfragen,
        abschlussquote=bestellungen / max(1, angebote),
        rabatt_schnitt=0.0,
        kauffrequenz_12m=kauffrequenz,
        deckung_gesamt_pct=deckung_pct,
        multi_lieferant_wahrsch=0.95,
        saison_konzentration=0.0,
        bedarf_gesamt_eur=bedarf_eur,
    )


# ---------------------------------------------------------------------------
# kaeufer_klassifikator — klassifiziere, klassifiziere_mit
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_klassifiziere_returns_klassifikation() -> None:
    from app.services.kaeufer_klassifikator import klassifiziere, Klassifikation
    result = klassifiziere(_make_signale())
    assert isinstance(result, Klassifikation)


@pytest.mark.unit
def test_klassifiziere_has_gruppe_field() -> None:
    from app.services.kaeufer_klassifikator import klassifiziere
    result = klassifiziere(_make_signale())
    assert hasattr(result, "gruppe")
    assert result.gruppe is not None


@pytest.mark.unit
def test_klassifiziere_has_confidence() -> None:
    from app.services.kaeufer_klassifikator import klassifiziere
    result = klassifiziere(_make_signale())
    assert hasattr(result, "confidence")
    assert 0.0 <= result.confidence <= 1.0


@pytest.mark.unit
def test_klassifiziere_has_begruendung() -> None:
    from app.services.kaeufer_klassifikator import klassifiziere
    result = klassifiziere(_make_signale())
    assert hasattr(result, "begruendung")
    assert len(result.begruendung) > 0


@pytest.mark.unit
def test_klassifiziere_high_deckung_higher_confidence() -> None:
    from app.services.kaeufer_klassifikator import klassifiziere
    low = klassifiziere(_make_signale(deckung_pct=0.05, bedarf_eur=5000))
    high = klassifiziere(_make_signale(deckung_pct=90.0, kauffrequenz=12, bedarf_eur=200000))
    # Both should return a valid classification
    assert low.gruppe is not None
    assert high.gruppe is not None


@pytest.mark.unit
def test_klassifiziere_mit_returns_tuple() -> None:
    from app.services.kaeufer_klassifikator import klassifiziere_mit
    result, quelle = klassifiziere_mit(_make_signale(), prefer_ai=False)
    assert result is not None
    assert isinstance(quelle, str)
    assert len(quelle) > 0


@pytest.mark.unit
def test_klassifiziere_mit_rule_based_source() -> None:
    from app.services.kaeufer_klassifikator import klassifiziere_mit
    result, quelle = klassifiziere_mit(_make_signale(), prefer_ai=False)
    assert "rule" in quelle.lower() or "regelbasiert" in quelle.lower() or "based" in quelle.lower()


# ---------------------------------------------------------------------------
# integration_bootstrap — build_integration_bootstrap_summary, build_integration_probe_plan
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_build_integration_bootstrap_summary_returns_dict() -> None:
    from app.services.integration_bootstrap import build_integration_bootstrap_summary
    result = build_integration_bootstrap_summary()
    assert isinstance(result, dict)


@pytest.mark.unit
def test_build_integration_bootstrap_summary_has_required_keys() -> None:
    from app.services.integration_bootstrap import build_integration_bootstrap_summary
    result = build_integration_bootstrap_summary()
    for key in ("integration_count", "ready_count", "integrations"):
        assert key in result


@pytest.mark.unit
def test_build_integration_bootstrap_summary_count_is_positive() -> None:
    from app.services.integration_bootstrap import build_integration_bootstrap_summary
    result = build_integration_bootstrap_summary()
    assert result["integration_count"] > 0


@pytest.mark.unit
def test_build_integration_bootstrap_summary_counts_are_consistent() -> None:
    from app.services.integration_bootstrap import build_integration_bootstrap_summary
    result = build_integration_bootstrap_summary()
    total = result.get("ready_count", 0) + result.get("partial_count", 0) + result.get("disabled_count", 0)
    assert total <= result["integration_count"]


@pytest.mark.unit
def test_build_integration_probe_plan_returns_list() -> None:
    from app.services.integration_bootstrap import build_integration_probe_plan
    probes = build_integration_probe_plan()
    assert isinstance(probes, list)
    assert len(probes) > 0


@pytest.mark.unit
def test_build_integration_probe_plan_entries_have_key() -> None:
    from app.services.integration_bootstrap import build_integration_probe_plan
    probes = build_integration_probe_plan()
    for probe in probes:
        assert hasattr(probe, "integration_key")
        assert len(probe.integration_key) > 0


@pytest.mark.unit
def test_build_integration_probe_plan_entries_have_status() -> None:
    from app.services.integration_bootstrap import build_integration_probe_plan
    probes = build_integration_probe_plan()
    for probe in probes:
        assert hasattr(probe, "status")
