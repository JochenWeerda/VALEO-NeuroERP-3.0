"""Preserve measured zero separately from absent laboratory measurements."""
import asyncio
from decimal import Decimal
from types import SimpleNamespace
import pytest
from app.api.v1.endpoints import quality_protocols as api

FIELDS = ("moisture_pct", "impurities_pct", "hl_weight_kg_per_hl", "protein_pct", "mycotoxin_ppb")

def protocol(**values):
    fields = {name: None for name in api.QualityProtocolOut.model_fields}
    fields.update(id="protocol", tenant_id="tenant", protocol_number="SYNTH-QS", version=1, is_final=False)
    fields.update(values)
    return SimpleNamespace(**fields)

@pytest.mark.parametrize("field", FIELDS)
@pytest.mark.parametrize("value", [None, Decimal("0"), Decimal("1.25")])
def test_output_preserves_zero_and_absence(field, value):
    result = api._to_out(protocol(**{field: value}))
    assert getattr(result, field) == (None if value is None else float(value))

@pytest.mark.parametrize("operation", ["create", "update"])
@pytest.mark.parametrize("field", FIELDS)
@pytest.mark.parametrize("value", [None, 0.0, 1.25])
def test_write_contract_passes_zero_as_decimal(monkeypatch, operation, field, value):
    stored = protocol()
    captured = []
    class Repository:
        def __init__(self, db, tenant_id):
            pass
        def get_by_id(self, protocol_id):
            return stored
    monkeypatch.setattr(api, "QualityProtocolRepositoryImpl", Repository)
    monkeypatch.setattr(api, "_get_user_id_from_request", lambda request: "synthetic-actor")
    monkeypatch.setattr(api, "evaluate_quality_protocol_datensatz", lambda data: SimpleNamespace(bestanden=True))
    def create(repo, payload):
        captured.append(payload)
        return stored
    def update(repo, protocol_id, payload):
        captured.append(payload)
        return stored
    monkeypatch.setattr(api, "create_quality_protocol", create)
    monkeypatch.setattr(api, "update_quality_protocol", update)
    if operation == "create":
        asyncio.run(api.create_protocol(api.QualityProtocolCreateIn(**{field: value}), db=None, tenant_id="tenant", request=None))
    else:
        asyncio.run(api.update_protocol("protocol", api.QualityProtocolUpdateIn(**{field: value}), db=None, tenant_id="tenant", request=None))
    actual = getattr(captured[0], field)
    assert actual == (None if value is None else Decimal(str(value)))
    if value is not None:
        assert isinstance(actual, Decimal)
