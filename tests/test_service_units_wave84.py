"""Wave 84 — Unit-Tests fuer agrar_settlement_service, fast_track,
event_schema_registry, agribusiness_service (pure domain functions)."""

from __future__ import annotations

import pytest
from decimal import Decimal


# ---------------------------------------------------------------------------
# agrar_settlement_service — TrocknungsInput/compute/validate (pure math)
# ---------------------------------------------------------------------------

def _make_trocknung_input(eingangs_feuchte="18.0", brutto="10000"):
    from app.services.agrar_settlement_service import TrocknungsInput, TrocknungsMethode
    return TrocknungsInput(
        settlement_id="SET-001",
        tenant_id="T001",
        crop_code="WW",
        rule_set_id="RS-001",
        rule_set_version=1,
        brutto_gewicht_kg=Decimal(brutto),
        eingangs_feuchte_pct=Decimal(eingangs_feuchte),
        ziel_feuchte_pct=Decimal("14.0"),
        methode=TrocknungsMethode.FAKTOR_STUFUNG,
    )


@pytest.mark.unit
def test_compute_trocknungs_abrechnung_returns_ergebnis() -> None:
    from app.services.agrar_settlement_service import (
        compute_trocknungs_abrechnung, TrocknungsRegelParametrierung,
    )
    ergebnis = compute_trocknungs_abrechnung(_make_trocknung_input(), TrocknungsRegelParametrierung())
    assert ergebnis is not None
    assert ergebnis.settlement_id == "SET-001"


@pytest.mark.unit
def test_compute_trocknungs_abrechnung_positive_abzug_when_wet() -> None:
    from app.services.agrar_settlement_service import (
        compute_trocknungs_abrechnung, TrocknungsRegelParametrierung,
    )
    ergebnis = compute_trocknungs_abrechnung(_make_trocknung_input("18.0"), TrocknungsRegelParametrierung())
    assert ergebnis.gesamt_abzug_kg > 0


@pytest.mark.unit
def test_compute_trocknungs_abrechnung_no_abzug_when_dry() -> None:
    from app.services.agrar_settlement_service import (
        compute_trocknungs_abrechnung, TrocknungsRegelParametrierung,
    )
    # Moisture already at target — no deduction
    ergebnis = compute_trocknungs_abrechnung(_make_trocknung_input("14.0"), TrocknungsRegelParametrierung())
    assert ergebnis.gesamt_abzug_kg == Decimal("0")


@pytest.mark.unit
def test_compute_trocknungs_abrechnung_has_audit_hash() -> None:
    from app.services.agrar_settlement_service import (
        compute_trocknungs_abrechnung, TrocknungsRegelParametrierung,
    )
    ergebnis = compute_trocknungs_abrechnung(_make_trocknung_input(), TrocknungsRegelParametrierung())
    assert ergebnis.audit_hash is not None
    assert len(ergebnis.audit_hash) > 0


@pytest.mark.unit
def test_get_default_trocknungsregeln_covers_main_crops() -> None:
    from app.services.agrar_settlement_service import get_default_trocknungsregeln
    rules = get_default_trocknungsregeln()
    for crop in ("WW", "SG", "RA", "KM"):
        assert crop in rules


@pytest.mark.unit
def test_get_default_trocknungsregeln_ww_threshold() -> None:
    from app.services.agrar_settlement_service import get_default_trocknungsregeln
    rules = get_default_trocknungsregeln()
    ww = rules["WW"]
    assert ww.start_threshold_pct == Decimal("14.5")


@pytest.mark.unit
def test_evaluate_settlement_datensatz_valid() -> None:
    from app.services.agrar_settlement_service import evaluate_settlement_datensatz
    result = evaluate_settlement_datensatz({"abrechnungsnummer": "AB-001", "lieferant_id": "L-001"})
    assert result.bestanden is True
    assert result.fehler_anzahl == 0


@pytest.mark.unit
def test_evaluate_settlement_datensatz_empty_fails() -> None:
    from app.services.agrar_settlement_service import evaluate_settlement_datensatz
    result = evaluate_settlement_datensatz({})
    assert result.bestanden is False
    assert result.fehler_anzahl > 0


@pytest.mark.unit
def test_trocknungs_input_as_canonical_dict() -> None:
    inp = _make_trocknung_input()
    d = inp.as_canonical_dict()
    assert d["crop_code"] == "WW"
    assert d["settlement_id"] == "SET-001"
    assert "schema_version" in d


# ---------------------------------------------------------------------------
# fast_track — is_fast_track, classify_request  (pure routing logic)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_is_fast_track_whitelist_path_get() -> None:
    from app.services.fast_track import is_fast_track
    # Whitelisted paths are fast-track for GET
    result = is_fast_track("GET", "/api/v1/config")
    assert result is True


@pytest.mark.unit
def test_is_fast_track_article_pattern() -> None:
    from app.services.fast_track import is_fast_track
    # Pattern match: /api/v1/articles/<id>
    result = is_fast_track("GET", "/api/v1/articles/ART-001")
    assert result is True


@pytest.mark.unit
def test_is_fast_track_unknown_path_false() -> None:
    from app.services.fast_track import is_fast_track
    result = is_fast_track("GET", "/api/v1/unknown-endpoint-xyz")
    assert result is False


@pytest.mark.unit
def test_classify_request_ai_context_forces_neuro_core() -> None:
    from app.services.fast_track import classify_request
    result = classify_request("GET", "/api/v1/config", has_ai_context=True)
    assert result["route"] == "neuro-core"


@pytest.mark.unit
def test_classify_request_fast_track_route() -> None:
    from app.services.fast_track import classify_request
    result = classify_request("GET", "/api/v1/config", has_ai_context=False)
    assert result["route"] == "fast-track"


@pytest.mark.unit
def test_classify_request_unknown_returns_neuro_core() -> None:
    from app.services.fast_track import classify_request
    result = classify_request("POST", "/api/v1/custom-action", has_ai_context=False)
    assert result["route"] == "neuro-core"


# ---------------------------------------------------------------------------
# event_schema_registry — list_event_types, create_event, validate_event
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_list_event_types_returns_list() -> None:
    from app.services.event_schema_registry import list_event_types
    types = list_event_types()
    assert isinstance(types, list)
    assert len(types) > 0


@pytest.mark.unit
def test_list_event_types_entries_have_event_type() -> None:
    from app.services.event_schema_registry import list_event_types
    types = list_event_types()
    for entry in types:
        assert "event_type" in entry


@pytest.mark.unit
def test_create_event_returns_domain_event() -> None:
    from app.services.event_schema_registry import create_event
    evt = create_event("test.event", {"key": "val"}, "T001")
    assert evt is not None
    assert evt.payload == {"key": "val"}


@pytest.mark.unit
def test_create_event_header_tenant_id() -> None:
    from app.services.event_schema_registry import create_event
    evt = create_event("test.event", {}, "T-TENANT")
    assert evt.header.tenant_id == "T-TENANT"


@pytest.mark.unit
def test_validate_event_known_type_valid() -> None:
    from app.services.event_schema_registry import validate_event, list_event_types
    first_type = list_event_types()[0]["event_type"]
    result = validate_event(first_type, {
        "tenant_id": "T001", "entry_id": "E-001", "actor": "admin",
        "action": "create", "resource_type": "invoice", "resource_id": "INV-001",
    })
    assert result["valid"] is True


# ---------------------------------------------------------------------------
# agribusiness_service — safe_float  (pure type-coercion)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_safe_float_numeric_value() -> None:
    from app.services.agribusiness_service import safe_float
    assert safe_float(3.14) == pytest.approx(3.14)


@pytest.mark.unit
def test_safe_float_string_numeric() -> None:
    from app.services.agribusiness_service import safe_float
    assert safe_float("42.5") == pytest.approx(42.5)


@pytest.mark.unit
def test_safe_float_none_returns_zero() -> None:
    from app.services.agribusiness_service import safe_float
    assert safe_float(None) == 0.0


@pytest.mark.unit
def test_safe_float_invalid_string_returns_zero() -> None:
    from app.services.agribusiness_service import safe_float
    assert safe_float("not_a_number") == 0.0
