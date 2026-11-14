"""The aggregate action forwards explicit quantities to the same DocFlow command."""
from unittest.mock import MagicMock

import pytest

from app.core.exceptions import ValidationFailedError
from app.services import docflow_belegaktionen as actions


@pytest.fixture
def service(monkeypatch):
    svc = MagicMock()
    svc.fetch_header.return_value = {"doc_type": "sales_order", "version": 7, "doc_number": "SYNTH-1"}
    svc.convert.return_value = {"target_doc_id": "synthetic-delivery"}
    monkeypatch.setattr(actions, "DocflowService", lambda db, tenant_id, actor: svc)
    return svc


def run(values):
    return actions.fuehre_aus(object(), "tenant-a", "sales_order", "doc-1", "umwandeln:sales_delivery",
                            {"sub": "synthetic-actor"}, values)


def test_explizite_teilmenge_wird_nicht_durch_gesamten_rest_ersetzt(service):
    assert "synthetic-delivery" in run({"quantities_by_source_item_id": {"line-1": 4}})
    doc_id, request = service.convert.call_args.args
    assert doc_id == "doc-1"
    assert request.quantities_by_source_item_id == {"line-1": 4}
    assert request.expected_version == 7
    assert request.target_doc_type == "sales_delivery"
    service.fetch_items.assert_not_called()
    service.umgewandelte_mengen.assert_not_called()


@pytest.mark.parametrize("value", [{}, [], {"line-1": -1}, {"line-1": float("nan")}])
def test_ungueltige_explizite_mengen_fuehren_nicht_zum_kommando(service, value):
    with pytest.raises(ValidationFailedError):
        run({"quantities_by_source_item_id": value})
    service.convert.assert_not_called()


def test_dialogfixture_entspricht_dem_echten_studio_builder():
    import json
    from pathlib import Path
    from app.core.screen_definitions_beleg import build_beleg_screen_definition
    fixture = Path(__file__).resolve().parents[1] / "packages/frontend-web/src/__tests__/fixtures/docflow-sales-order-conversion.json"
    actual = next(a for a in build_beleg_screen_definition("sales_order")["actions"] if a["key"] == "umwandeln:sales_delivery")
    assert json.loads(fixture.read_text(encoding="utf-8")) == actual
