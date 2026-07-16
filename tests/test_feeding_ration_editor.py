"""FEED-EDITOR-021 / FEED-T071: Deterministische Draft-Bewertung des Rationseditors.

TDD-Red-Welle 1: vor der Implementierung geschrieben (ModuleNotFoundError auf
app.agrar.rations.ration_draft).
"""
from __future__ import annotations

import pytest


def _feed(feed_id: str, **overrides):
    base = {
        "id": feed_id, "name": f"Feed {feed_id}", "group": "test", "futterart": "grundfutter",
        "forage": True, "structural_coproduct": False,
        "dm_frac": 0.35, "price": 0.20,  # €/kg TM
        "me": 10.5, "cp": 160.0, "sidp": 70.0, "ndf": 420.0, "st": 30.0, "zu": 40.0,
    }
    base.update(overrides)
    return base


REQUIREMENTS = {
    "me_mj": 210.0, "sidp_g": 1600.0,
    "dmi_min_kg": 19.0, "dmi_max_kg": 24.0, "dmi_target_kg": 21.5,
}


def test_draft_evaluation_sums_positions_deterministically() -> None:
    """Positionen: kg TM, Kosten und Naehrstoffbeitraege je Komponente; Summen
    sind reine Funktion der Eingaben (reproduzierbar)."""
    from app.agrar.rations.ration_draft import evaluate_draft

    feeds = {"gras": _feed("gras"), "mais": _feed("mais", dm_frac=0.33, me=11.2, sidp=62.0, price=0.18)}
    components = [{"feed_id": "gras", "kg_fm": 20.0}, {"feed_id": "mais", "kg_fm": 18.0}]

    result_a = evaluate_draft(components, feeds, REQUIREMENTS)
    result_b = evaluate_draft(components, feeds, REQUIREMENTS)
    assert result_a == result_b

    gras = next(p for p in result_a["positions"] if p["feed_id"] == "gras")
    assert gras["kg_tm"] == pytest.approx(20.0 * 0.35)
    assert gras["cost_eur"] == pytest.approx(20.0 * 0.35 * 0.20)
    assert gras["me_mj"] == pytest.approx(20.0 * 0.35 * 10.5)

    totals = result_a["totals"]
    expected_dm = 20.0 * 0.35 + 18.0 * 0.33
    assert totals["dm_kg"] == pytest.approx(expected_dm)
    assert totals["me_mj"] == pytest.approx(20.0 * 0.35 * 10.5 + 18.0 * 0.33 * 11.2)
    assert totals["cost_eur"] == pytest.approx(20.0 * 0.35 * 0.20 + 18.0 * 0.33 * 0.18)


def test_draft_evaluation_compares_against_requirements_with_textual_findings() -> None:
    """Deltas gegen das Bedarfsprofil erzeugen Befunde mit Code, Schweregrad und
    Text (nie nur Farbe); Ueber-/Unterdeckung und TM-Band werden benannt."""
    from app.agrar.rations.ration_draft import evaluate_draft

    feeds = {"gras": _feed("gras")}
    # 10 kg FM Gras = 3,5 kg TM -> weit unter DMI-Band und Bedarf
    result = evaluate_draft([{"feed_id": "gras", "kg_fm": 10.0}], feeds, REQUIREMENTS)

    codes = {f["code"]: f for f in result["findings"]}
    assert "dmi_below_band" in codes
    # Vertragsschaerfung FEED-EDITOR-022: 4-stufige Prioritaet
    assert codes["dmi_below_band"]["severity"] in {"high", "critical"}
    assert "energy_deficit" in codes
    assert codes["energy_deficit"]["message"], "Befund braucht verstaendlichen Text"
    assert codes["energy_deficit"]["actual"] < codes["energy_deficit"]["target"]

    deltas = {d["metric"]: d for d in result["deltas"]}
    assert deltas["me_mj"]["delta"] == pytest.approx(result["totals"]["me_mj"] - REQUIREMENTS["me_mj"])


def test_missing_nutrient_values_are_reported_as_incomplete_never_zero() -> None:
    """Fehlt ein Naehrstoffwert (z. B. sidP am Futter), wird die Kennzahl als
    unvollstaendig gekennzeichnet statt still mit 0 summiert (Lastenheft 7.1)."""
    from app.agrar.rations.ration_draft import evaluate_draft

    feed_without_sidp = _feed("mineral", dm_frac=0.90, me=0.0)
    del feed_without_sidp["sidp"]
    feeds = {"gras": _feed("gras"), "mineral": feed_without_sidp}
    components = [{"feed_id": "gras", "kg_fm": 20.0}, {"feed_id": "mineral", "kg_fm": 0.2}]

    result = evaluate_draft(components, feeds, REQUIREMENTS)

    coverage = result["coverage"]["sidp_g"]
    assert coverage["complete"] is False
    assert "mineral" in coverage["missing_feed_ids"]
    # Teilsumme nur aus bekannten Beitraegen — Gras liefert 20*0.35*70
    assert result["totals"]["sidp_g"] == pytest.approx(20.0 * 0.35 * 70.0)
    incomplete = {f["code"] for f in result["findings"]}
    assert "sidp_g_incomplete" in incomplete


def test_unknown_feed_raises_lookup_error() -> None:
    from app.agrar.rations.ration_draft import evaluate_draft

    with pytest.raises(LookupError):
        evaluate_draft([{"feed_id": "fehlt", "kg_fm": 5.0}], {}, REQUIREMENTS)


def test_findings_carry_four_level_priority_and_are_ordered() -> None:
    """FEED-EDITOR-022: Befunde tragen eine der vier Stufen critical/high/medium/info
    und kommen nach Prioritaet geordnet zurueck (TDD-Red-Welle 2)."""
    from app.agrar.rations.ration_draft import SEVERITY_ORDER, evaluate_draft

    assert SEVERITY_ORDER == ("critical", "high", "medium", "info")

    feed_without_sidp = _feed("mineral", dm_frac=0.90, me=0.0)
    del feed_without_sidp["sidp"]
    feeds = {"gras": _feed("gras"), "mineral": feed_without_sidp}
    # Unterdeckung (high) + Abdeckungsluecke (info) in einem Bild
    result = evaluate_draft([
        {"feed_id": "gras", "kg_fm": 10.0},
        {"feed_id": "mineral", "kg_fm": 0.2},
    ], feeds, REQUIREMENTS)

    severities = [f["severity"] for f in result["findings"]]
    assert set(severities) <= {"critical", "high", "medium", "info"}
    assert "high" in severities, "Unterdeckung muss Stufe high tragen"
    ranks = [SEVERITY_ORDER.index(s) for s in severities]
    assert ranks == sorted(ranks), "Befunde muessen nach Prioritaet geordnet sein"


def test_compare_drafts_diffs_components_and_metrics() -> None:
    """FEED-EDITOR-023 (TDD-Red-Welle 3): Vergleich zweier Komponentenbilder
    liefert je Futtermittel Basis/Variante/Delta inkl. hinzugefuegt/entfernt
    sowie Kennzahlen-Deltas beider Bewertungen."""
    from app.agrar.rations.ration_draft import compare_drafts, evaluate_draft

    feeds = {
        "gras": _feed("gras"),
        "mais": _feed("mais", dm_frac=0.33, me=11.2, price=0.18),
        "soja": _feed("soja", dm_frac=0.88, me=13.5, sidp=350.0, price=0.45),
    }
    base = [{"feed_id": "gras", "kg_fm": 20.0}, {"feed_id": "mais", "kg_fm": 18.0}]
    variant = [{"feed_id": "gras", "kg_fm": 16.0}, {"feed_id": "soja", "kg_fm": 2.0}]

    base_eval = evaluate_draft(base, feeds, REQUIREMENTS)
    variant_eval = evaluate_draft(variant, feeds, REQUIREMENTS)
    comparison = compare_drafts(base_eval, variant_eval)

    rows = {row["feed_id"]: row for row in comparison["component_diff"]}
    assert rows["gras"]["base_kg_fm"] == 20.0
    assert rows["gras"]["variant_kg_fm"] == 16.0
    assert rows["gras"]["delta_kg_fm"] == -4.0
    assert rows["gras"]["change"] == "changed"
    assert rows["mais"]["change"] == "removed"
    assert rows["mais"]["variant_kg_fm"] is None, "entfernt bleibt unbekannt, nie 0-guenstig"
    assert rows["soja"]["change"] == "added"
    assert rows["soja"]["base_kg_fm"] is None

    metric_rows = {row["metric"]: row for row in comparison["metric_diff"]}
    assert metric_rows["cost_eur"]["delta"] == (
        variant_eval["totals"]["cost_eur"] - base_eval["totals"]["cost_eur"])
    assert metric_rows["me_mj"]["base"] == base_eval["totals"]["me_mj"]
    # Reihenfolge deterministisch (Basisreihenfolge, dann Neuzugaenge)
    assert [row["feed_id"] for row in comparison["component_diff"]] == ["gras", "mais", "soja"]
