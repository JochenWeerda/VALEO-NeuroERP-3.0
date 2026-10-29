"""Contract checks for the functional Studio Debitoren OP list."""

import json
from pathlib import Path

from app.core.screen_definitions_listen import LISTEN_SCREEN_BUILDERS


def test_debitoren_op_uses_canonical_open_item_fields_and_read_contract() -> None:
    screen = LISTEN_SCREEN_BUILDERS["fibu/debitoren-liste"]()
    table = screen["tables"][0]
    columns = table["columns"]
    keys = [column["key"] for column in columns]

    assert screen["dataSources"][0]["endpoint"] == (
        "/api/v1/finance/open-items?konto_typ=debitoren&only_open=true"
    )
    assert keys == [
        "rechnungsnr", "kunde_name", "konto_nr", "rechnungsdatum", "faelligkeit",
        "op_betrag", "offen", "mahn_stufe", "ueberfaellig", "waehrung",
    ]
    assert table["rowRouteTemplate"] == "/finance/ar-open-item/{id}"
    assert screen["layout"]["tableProfile"] == "financial"
    assert next(column for column in columns if column["key"] == "waehrung")["filterable"] is True
    assert next(column for column in columns if column["key"] == "offen")["currencyField"] == "waehrung"

    experience = screen["listExperience"]
    assert experience["searchFields"] == ["rechnungsnr", "kunde_name", "konto_nr"]
    assert experience["aggregates"] == [
        {"key": "all", "label": "Offene Posten", "conditions": [], "kind": "count"},
        {"key": "open_amount", "label": "Gesamt offen", "conditions": [], "kind": "sum", "field": "offen", "format": "currency", "currencyField": "waehrung"},
        {"key": "overdue", "label": "Überfällig", "conditions": [{"field": "ueberfaellig", "op": "eq", "value": "true"}], "kind": "count"},
        {"key": "dunning", "label": "In Mahnung", "conditions": [{"field": "mahn_stufe", "op": "neq", "value": "0"}], "kind": "count"},
    ]
    assert experience["notice"] == {
        "aggregate": "overdue", "text": "{overdue} überfällige Rechnung(en)!"
    }
    assert len(experience["export"]["columns"]) == 9
    assert not any(action.get("key") == "neu" for action in screen["actions"])
    back = next(action for action in screen["actions"] if action.get("navigationRoute") == "/fibu/op-verwaltung")
    assert back["key"] == "zurueck-op-verwaltung" and back["kind"] == "secondary"
    assert back["localEffect"] == "navigation" and back["dangerLevel"] == "safe"
    assert "Rolle und Mandant" in back["stubReason"]


def test_debitoren_legacy_route_identity_remains_registered() -> None:
    """The old route's screen identity is intentionally retained pending route inventory proof."""
    assert "fibu/debitoren-liste" in LISTEN_SCREEN_BUILDERS


def test_frontend_runtime_fixture_is_the_real_python_builder_output() -> None:
    fixture = Path("packages/frontend-web/src/__tests__/fixtures/fibu-debitoren-builder-contract.json")
    assert json.loads(fixture.read_text(encoding="utf-8")) == LISTEN_SCREEN_BUILDERS["fibu/debitoren-liste"]()
