"""UIX-082: ESG-CO2e-Fussabdruck-Berechnung — auditierbar, deterministisch.

Reine Unit-Tests (kein DB): fuehre mit
`pytest tests/test_uix082_esg_footprint.py --noconftest -p no:cacheprovider --no-cov -q -o addopts=""`
(die Root-conftest haengt in der DB-Fixture; siehe Testing-Gotcha).
"""
from __future__ import annotations

import pytest

from app.services.esg_footprint_service import (
    EsgInput,
    compute_footprint,
    current_factor_version,
    get_factor,
)

pytestmark = pytest.mark.unit


def test_factor_version_and_factors_loaded():
    assert current_factor_version() == "2026-07"
    assert get_factor("trocknung_gas_kwh")["co2e_kg"] == 0.201
    assert get_factor("gibtsnicht") is None


def test_single_component_kg_on_three_decimals():
    fp = compute_footprint("charge-1", [EsgInput("trocknung_gas_kwh", 1840, "trocknungslauf:4711")])
    assert len(fp.components) == 1
    comp = fp.components[0]
    assert comp.co2e_kg == 369.840  # 1840 * 0.201
    assert comp.input == {"kWh": 1840}
    assert comp.source_ref == "trocknungslauf:4711"
    assert comp.factor_version == "2026-07"
    assert fp.co2e_kg == 369.840


def test_total_sums_all_components():
    fp = compute_footprint(
        "charge-2",
        [
            EsgInput("trocknung_gas_kwh", 1840, "trocknungslauf:4711"),
            EsgInput("transport_tkm", 500, "tour:88"),
            EsgInput("strom_kwh", 1200, "pauschale:umschlag"),
        ],
        tenant_id="t-1",
    )
    keys = {c.key for c in fp.components}
    assert keys == {"trocknung_gas_kwh", "transport_tkm", "strom_kwh"}
    # 369.84 + 31.0 + 456.0
    assert fp.co2e_kg == 856.840
    assert fp.tenant_id == "t-1"


def test_missing_input_yields_no_component_not_zero():
    fp = compute_footprint("charge-3", [EsgInput("transport_tkm", 500, "tour:88")])
    assert [c.key for c in fp.components] == ["transport_tkm"]
    # keine trocknung/strom-Komponente mit 0 — sie fehlt schlicht
    assert all(c.co2e_kg > 0 for c in fp.components)


def test_unknown_factor_is_skipped():
    fp = compute_footprint("charge-4", [EsgInput("fantasie_faktor", 999, "x:1")])
    assert fp.components == []
    assert fp.co2e_kg == 0.0


def test_every_component_is_auditable():
    fp = compute_footprint("charge-5", [EsgInput("transport_tkm", 500, "tour:88")])
    for c in fp.components:
        assert c.source_ref  # Beleg-Verweis vorhanden
        assert c.source      # Faktor-Quelle vorhanden


def test_explicit_factor_version_is_carried_through():
    fp = compute_footprint("charge-6", [EsgInput("strom_kwh", 100, "z:1")], factor_version="2026-07")
    assert fp.factor_version == "2026-07"
    assert fp.components[0].factor_version == "2026-07"


def test_reproducible_same_inputs_same_result():
    inputs = [
        EsgInput("strom_kwh", 1200, "p:1"),
        EsgInput("trocknung_gas_kwh", 1840, "t:1"),
    ]
    a = compute_footprint("charge-7", inputs).to_dict()
    b = compute_footprint("charge-7", list(reversed(inputs))).to_dict()
    # gleiche Inputs (auch andere Reihenfolge) + gleiche Faktorversion → identisch
    assert a == b


def test_component_order_is_stable():
    fp = compute_footprint(
        "charge-8",
        [EsgInput("strom_kwh", 1, "a"), EsgInput("transport_tkm", 1, "b"), EsgInput("trocknung_gas_kwh", 1, "c")],
    )
    assert [c.key for c in fp.components] == sorted(c.key for c in fp.components)
