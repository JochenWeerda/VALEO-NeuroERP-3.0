"""UIX-082: ESG-Footprint API und Persistenzvertrag."""
from __future__ import annotations

import asyncio
import json
from decimal import Decimal
from typing import Any

import pytest

from app.api.v1.endpoints.esg_footprint import get_charge_footprint

pytestmark = pytest.mark.unit


class _MappedResult:
    def __init__(self, row: dict[str, Any] | None = None):
        self.row = row

    def mappings(self) -> "_MappedResult":
        return self

    def first(self) -> dict[str, Any] | None:
        return self.row


class _Db:
    def __init__(self, rows: list[dict[str, Any] | None]):
        self.rows = rows
        self.calls: list[tuple[Any, dict[str, Any]]] = []
        self.commits = 0

    def execute(self, statement: Any, params: dict[str, Any]) -> _MappedResult:
        self.calls.append((statement, params))
        row = self.rows.pop(0) if self.rows else None
        return _MappedResult(row)

    def commit(self) -> None:
        self.commits += 1


def _call(db: _Db, **kwargs: Any):
    return asyncio.run(
        get_charge_footprint(
            charge_id=kwargs.pop("charge_id", "charge-1"),
            recompute=kwargs.pop("recompute", False),
            drying_kwh=kwargs.pop("drying_kwh", None),
            electricity_kwh=kwargs.pop("electricity_kwh", None),
            transport_tkm=kwargs.pop("transport_tkm", None),
            tenant_id=kwargs.pop("tenant_id", "tenant-a"),
            db=db,  # type: ignore[arg-type]
        )
    )


def test_get_charge_footprint_computes_and_persists_auditable_components() -> None:
    persisted = {
        "tenant_id": "tenant-a",
        "charge_id": "charge-1",
        "factor_version": "2026-07",
        "co2e_kg": Decimal("400.840"),
        "components": json.dumps([
            {
                "key": "transport_tkm",
                "input": {"tkm": 500},
                "factor_version": "2026-07",
                "co2e_kg": 31.0,
                "source_ref": "transport:charge-1",
                "source": "GLEC v3, LKW 26-40t",
            },
            {
                "key": "trocknung_gas_kwh",
                "input": {"kWh": 1840},
                "factor_version": "2026-07",
                "co2e_kg": 369.84,
                "source_ref": "trocknung:charge-1",
                "source": "UBA 2025, Erdgas",
            },
        ]),
        "inputs": json.dumps([
            {"factor_key": "transport_tkm", "value": 500, "source_ref": "transport:charge-1"},
            {"factor_key": "trocknung_gas_kwh", "value": 1840, "source_ref": "trocknung:charge-1"},
        ]),
    }
    db = _Db([persisted])

    result = _call(db, drying_kwh=1840, transport_tkm=500)

    params = db.calls[0][1]
    assert params["tenant_id"] == "tenant-a"
    assert params["charge_id"] == "charge-1"
    assert params["factor_version"] == "2026-07"
    assert result.co2e_kg == 400.84
    assert [component.key for component in result.components] == ["transport_tkm", "trocknung_gas_kwh"]
    assert all(component.source_ref for component in result.components)
    assert db.commits == 1


def test_get_charge_footprint_reads_existing_tenant_row_without_recompute() -> None:
    existing = {
        "tenant_id": "tenant-b",
        "charge_id": "charge-2",
        "factor_version": "2026-07",
        "co2e_kg": Decimal("31.000"),
        "components": [{"key": "transport_tkm", "input": {"tkm": 500}, "factor_version": "2026-07", "co2e_kg": 31.0, "source_ref": "tour:88", "source": "GLEC v3"}],
        "inputs": [],
    }
    db = _Db([existing])

    result = _call(db, tenant_id="tenant-b", charge_id="charge-2")

    params = db.calls[0][1]
    assert params["tenant_id"] == "tenant-b"
    assert params["charge_id"] == "charge-2"
    assert result.persisted is True
    assert result.components[0].source_ref == "tour:88"
    assert db.commits == 0
