"""Formula interpreter and preview contract; HTTP identity/DB boundaries are doubles."""
import copy

import pytest

from app.api.v1.endpoints.rohware_schema import _eval_formula
from app.services.rohware_formula import evaluate_formula
from test_rohware_schema_tenant_contract import TOKEN, URL, client

pytestmark = pytest.mark.unit


@pytest.fixture(autouse=True)
def _enable_dev_token():
    """The explicitly isolated router fixture does not use the compatibility app."""
    yield


@pytest.mark.parametrize("formula,expected", [
    ("basis_preis", 200), ("basis_preis * feuchte_abzug_prozent / 100", 2),
    ("round(basis_preis / 3, 2)", 66.67), ("max(0, feuchte - 14)", 1),
    ("min(hl_gewicht, 76)", 74), ("abs(-bruch)", 2), ("round(125, -1)", 120),
    ("3 + 4 * 2 / (1 - 5) ** 2", 3.5), ("9 // 2 + 9 % 2", 5),
    ("-(+basis_preis)", -200), ("min(5, max(2, 3))", 3), ("round(2.5)", 2),
])
def test_supported_business_arithmetic(formula, expected):
    assert _eval_formula(formula, {"basis_preis": 200.0, "feuchte": 15.0,
                                  "hl_gewicht": 74.0, "bruch": 2.0}) == pytest.approx(expected)


@pytest.mark.parametrize("formula", [
    "(1).__class__.__name__ == 'int'", "basis_preis.real", "().__class__.__mro__",
    "[1][0]", "(lambda: 1)()", "[x for x in (1, 2)]", "__import__('os')",
    "abs.__call__(1)", "round(1, **{})", "max(*(1, 2))", "'x' * 1000000000",
    "9 ** 9 ** 9", "1e309", "1 / 0", "True", "float('nan')",
    "round(1, 400)", "round(1, 2.5)", "unknown_value", "{'x': 1}",
    "1" * 1025, "+".join(["1"] * 80), "+" * 33 + "1",
])
def test_unsafe_nonfinite_or_unbounded_expressions_are_rejected(formula):
    assert evaluate_formula(formula, {"basis_preis": 200.0}) is None


def test_context_cannot_invoke_conversion_magic_or_shadow_callable():
    calls = []

    class ObjectInput:
        def __float__(self):
            calls.append("conversion")
            return 2.0

    assert evaluate_formula("basis_preis", {"basis_preis": ObjectInput()}) is None
    assert evaluate_formula("abs(-1)", {"abs": lambda value: calls.append(value)}) is None
    assert calls == []


@pytest.mark.parametrize("value", [float("nan"), float("inf"), True, "2"])
def test_interpreter_requires_finite_numeric_context(value):
    assert evaluate_formula("basis_preis", {"basis_preis": value}) is None


@pytest.mark.parametrize("value", ["NaN", "Infinity", "private-invalid-value", None, True, [], {}])
def test_http_preview_rejects_invalid_numbers_without_writes(client, value):
    http, db, _ = client
    before = copy.deepcopy((db.schemas, db.lines))
    result = http.post(URL + "/a/testrechnung", headers=TOKEN, json={"basis_preis": value})
    assert result.status_code == 422
    assert "private-invalid-value" not in result.text
    assert (db.schemas, db.lines) == before
    assert db.commits == 0


def test_http_preview_rejects_invalid_formula_instead_of_returning_a_price(client):
    http, db, _ = client
    formula = "(1).__class__.__name__ == 'int'"
    db.lines["la"]["berechnungsformel"] = formula
    result = http.post(URL + "/a/testrechnung", headers=TOKEN, json={"basis_preis": 200})
    assert result.status_code == 422
    assert formula not in result.text
    assert "gesamt_preis" not in result.json()
    assert db.commits == 0


def test_http_preview_rejects_overflow_in_aggregate(client):
    http, db, _ = client
    db.lines["la"]["berechnungsformel"] = "1e308"
    db.lines["lc"] = {**db.lines["la"], "id": "lc"}
    assert http.post(URL + "/a/testrechnung", headers=TOKEN, json={}).status_code == 422
    assert db.commits == 0


def test_http_preview_preserves_legacy_numeric_strings(client):
    http, db, _ = client
    result = http.post(URL + "/a/testrechnung", headers=TOKEN, json={"basis_preis": "200.5"})
    assert result.status_code == 200
    assert result.json()["gesamt_preis"] == 200.5
    assert db.commits == 0
