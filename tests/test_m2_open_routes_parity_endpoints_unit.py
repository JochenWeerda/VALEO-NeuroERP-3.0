"""Executable Unit-Tests: M2 Open-Routes Parity-Endpunkte (Sonar New-Code)."""
from __future__ import annotations

import asyncio
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from app.api.v1.endpoints import external_gates, einkauf_compat_writes, pos_fiscalization


def test_external_gates_overview_and_items():
    overview = asyncio.run(external_gates.get_gates_overview(tenant_id="t1"))
    assert overview["gesamt"] == len(external_gates._SYSTEM_META)
    assert overview["ok_count"] >= 1
    assert overview["problem_count"] == overview["warning_count"] + overview["faellig_count"] + overview["fehler_count"]

    items = asyncio.run(external_gates.list_gate_items(tenant_id="t1"))
    assert len(items) == overview["gesamt"]
    assert {i["system_id"] for i in items} == set(external_gates._SYSTEM_META)

    one = asyncio.run(external_gates.get_gate("datev", tenant_id="t1"))
    assert one["system_id"] == "datev"
    assert one["simulated"] is True

    with pytest.raises(HTTPException) as exc:
        asyncio.run(external_gates.get_gate("unknown", tenant_id="t1"))
    assert exc.value.status_code == 404


def test_einkauf_compat_writes_create_update_and_404():
    db = MagicMock()
    with patch("app.api.v1.endpoints.einkauf_compat_writes.EinkaufCompatService") as svc_cls:
        svc = svc_cls.return_value
        svc.create_angebot.return_value = {"id": "a1"}
        svc.update_angebot.return_value = {"id": "a1"}
        svc.create_anlieferavis.return_value = {"id": "v1"}
        svc.update_anlieferavis.return_value = {"id": "v1"}
        assert asyncio.run(einkauf_compat_writes.einkauf_angebot_create({"x": 1}, tenant_id="t", db=db))["id"] == "a1"
        assert asyncio.run(
            einkauf_compat_writes.einkauf_angebot_update("a1", {"y": 2}, tenant_id="t", db=db)
        )["id"] == "a1"
        assert asyncio.run(
            einkauf_compat_writes.einkauf_anlieferavis_create({"z": 3}, tenant_id="t", db=db)
        )["id"] == "v1"
        assert asyncio.run(
            einkauf_compat_writes.einkauf_anlieferavis_update("v1", {"w": 4}, tenant_id="t", db=db)
        )["id"] == "v1"

        from app.core.exceptions import EntityNotFoundError

        svc.update_angebot.side_effect = EntityNotFoundError("Angebot", "missing")
        with pytest.raises(HTTPException) as exc:
            asyncio.run(einkauf_compat_writes.einkauf_angebot_update("missing", {}, tenant_id="t", db=db))
        assert exc.value.status_code == 404

        svc.update_anlieferavis.side_effect = EntityNotFoundError("Anlieferavis", "missing")
        with pytest.raises(HTTPException) as exc2:
            asyncio.run(einkauf_compat_writes.einkauf_anlieferavis_update("missing", {}, tenant_id="t", db=db))
        assert exc2.value.status_code == 404


def test_pos_fiscalization_put_config_terminal_and_overview_products():
    db = MagicMock()
    payload = SimpleNamespace(
        model_dump=lambda: {
            "provider": "fiskaly",
            "client_id": "cli-1",
            "terminal_id": " term-9 ",
            "settings": {},
        }
    )
    with patch("app.api.v1.endpoints.pos_fiscalization._service") as svc_factory:
        svc = svc_factory.return_value
        svc.save_config.return_value = {"ok": True}
        out = asyncio.run(pos_fiscalization.put_config(payload, tenant_id="t1", db=db))
        assert out == {"ok": True}
        kwargs = svc.save_config.call_args.kwargs
        assert kwargs["settings"]["terminal_id"] == "term-9"

        payload2 = SimpleNamespace(
            model_dump=lambda: {
                "provider": "fiskaly",
                "client_id": " cli-2 ",
                "settings": {},
            }
        )
        asyncio.run(pos_fiscalization.put_config(payload2, tenant_id="t1", db=db))
        kwargs2 = svc.save_config.call_args.kwargs
        assert kwargs2["settings"]["terminal_id"] == "cli-2"

        svc.save_config.side_effect = ValueError("bad")
        with pytest.raises(HTTPException) as exc:
            asyncio.run(pos_fiscalization.put_config(payload, tenant_id="t1", db=db))
        assert exc.value.status_code == 422

        svc.get_config.return_value = {
            "configured": True,
            "provider": "fiskaly",
            "dsfinvk_provider": "x",
            "cash_register_id": "c",
            "client_id": "cli",
            "settings": {"terminal_id": "t"},
            "simulation_allowed": True,
        }
        sign = SimpleNamespace(model_dump=lambda: {"ready": True, "provider": "s", "blockers": ["b1"]})
        dsfinvk = SimpleNamespace(model_dump=lambda: {"ready": False, "provider": "d", "blockers": []})
        product = SimpleNamespace(
            model_dump=lambda: {
                "product": "p1",
                "label": "P1",
                "ready": True,
                "blockers": ["x"],
                "details": SimpleNamespace(model_dump=lambda: {"execution_note": "note"}),
            }
        )
        svc.readiness.return_value = {
            "ready": False,
            "sign": sign,
            "dsfinvk": dsfinvk,
            "config_blockers": ["cfg"],
            "products": [product],
        }
        overview = asyncio.run(pos_fiscalization.fiscalization_overview(tenant_id="t1", db=db))
        assert overview["terminal_id"] == "t"
        assert overview["product_count"] == 1
        assert "cfg" in overview["blocker_text"]

        rows = asyncio.run(pos_fiscalization.list_fiscal_products(tenant_id="t1", db=db))
        assert rows[0].product == "p1"
        assert rows[0].execution_note == "note"
