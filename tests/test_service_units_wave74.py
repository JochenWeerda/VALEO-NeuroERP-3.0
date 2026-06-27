"""Wave 74 — Unit-Tests fuer agrar_contract_service und agrar_settlement_service (DQ-Validierung, pure)."""

from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# agrar_contract_service — evaluate_contract_datensatz / build_dq_error_detail
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_evaluate_contract_valid_datensatz() -> None:
    from app.services.agrar_contract_service import evaluate_contract_datensatz
    ds = {
        "kontrakt_nr": "KT-001",
        "lieferant_nr": "L-001",
        "ware": "Weizen",
        "menge_to": 100,
        "preis_eur_to": 200,
    }
    result = evaluate_contract_datensatz(ds)
    assert result.bestanden is True
    assert result.fehler_anzahl == 0


@pytest.mark.unit
def test_evaluate_contract_empty_datensatz() -> None:
    from app.services.agrar_contract_service import evaluate_contract_datensatz
    result = evaluate_contract_datensatz({})
    assert result.bestanden is False
    assert result.fehler_anzahl > 0


@pytest.mark.unit
def test_evaluate_contract_missing_kontrakt_nr() -> None:
    from app.services.agrar_contract_service import evaluate_contract_datensatz
    result = evaluate_contract_datensatz({"lieferant_nr": "L-001", "ware": "Weizen"})
    assert result.bestanden is False
    felder = [v.feld for v in result.verletzungen]
    assert "kontrakt_nr" in felder


@pytest.mark.unit
def test_evaluate_contract_missing_lieferant_nr() -> None:
    from app.services.agrar_contract_service import evaluate_contract_datensatz
    result = evaluate_contract_datensatz({"kontrakt_nr": "KT-001", "ware": "Weizen"})
    felder = [v.feld for v in result.verletzungen]
    assert "lieferant_nr" in felder


@pytest.mark.unit
def test_evaluate_contract_result_has_ruleset_id() -> None:
    from app.services.agrar_contract_service import evaluate_contract_datensatz
    result = evaluate_contract_datensatz({})
    assert result.ruleset_id is not None
    assert len(result.ruleset_id) > 0


@pytest.mark.unit
def test_build_dq_error_detail_structure() -> None:
    from app.services.agrar_contract_service import evaluate_contract_datensatz, build_dq_error_detail
    result = evaluate_contract_datensatz({})
    detail = build_dq_error_detail("Kontrakt", result)
    for key in ("code", "entity_typ", "ruleset_id", "fehler_anzahl", "verletzungen"):
        assert key in detail


@pytest.mark.unit
def test_build_dq_error_detail_fehler_anzahl_matches() -> None:
    from app.services.agrar_contract_service import evaluate_contract_datensatz, build_dq_error_detail
    result = evaluate_contract_datensatz({})
    detail = build_dq_error_detail("Kontrakt", result)
    assert detail["fehler_anzahl"] == result.fehler_anzahl


@pytest.mark.unit
def test_evaluate_contract_violation_has_severity() -> None:
    from app.services.agrar_contract_service import evaluate_contract_datensatz
    result = evaluate_contract_datensatz({})
    for v in result.verletzungen:
        assert hasattr(v, "severity")
        assert hasattr(v, "meldung")


# ---------------------------------------------------------------------------
# agrar_settlement_service — evaluate_settlement_datensatz  (pure DQ)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_evaluate_settlement_empty_fails() -> None:
    from app.services.agrar_settlement_service import evaluate_settlement_datensatz
    result = evaluate_settlement_datensatz({})
    assert result.bestanden is False
    assert result.fehler_anzahl > 0


@pytest.mark.unit
def test_evaluate_settlement_result_fields() -> None:
    from app.services.agrar_settlement_service import evaluate_settlement_datensatz
    result = evaluate_settlement_datensatz({})
    assert hasattr(result, "entity_typ")
    assert hasattr(result, "ruleset_id")
    assert hasattr(result, "verletzungen")
    assert isinstance(result.verletzungen, list)


@pytest.mark.unit
def test_evaluate_settlement_violations_have_feld() -> None:
    from app.services.agrar_settlement_service import evaluate_settlement_datensatz
    result = evaluate_settlement_datensatz({})
    for v in result.verletzungen:
        assert hasattr(v, "feld")
        assert hasattr(v, "meldung")
