from __future__ import annotations

import json
from datetime import date
from decimal import Decimal

import httpx
import pytest

from app.services.fiscalization.contracts import (
    ExportCommand,
    FinishTransactionCommand,
    FiscalLine,
    PaymentLine,
    StartTransactionCommand,
)
from app.services.fiscalization.providers import (
    FiscalProviderError,
    FiskalyProvider,
    SimulationProvider,
    SwissbitProvider,
)


def _command(command_type=StartTransactionCommand):
    return command_type(
        terminal_id="TERM-1",
        cash_register_id="TSS-1",
        client_id="CLIENT-1",
        transaction_id="TX-1",
        lines=[FiscalLine(text="Artikel", gross_amount=Decimal("11.90"), vat_rate=Decimal("19"))],
        payments=[PaymentLine(method="CASH", amount=Decimal("11.90"))],
    )


def test_fiskaly_uses_access_token_and_put_for_active_and_finished(monkeypatch):
    monkeypatch.setenv("FISKALY_API_KEY", "key")
    monkeypatch.setenv("FISKALY_API_SECRET", "secret")
    requests: list[tuple[str, str, dict, str | None]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        payload = json.loads(request.content) if request.content else {}
        requests.append((request.method, str(request.url), payload, request.headers.get("Authorization")))
        if request.url.path.endswith("/auth"):
            return httpx.Response(200, json={"access_token": "token-123"})
        return httpx.Response(
            200,
            json={
                "_id": "TX-1",
                "state": payload["state"],
                "signature": {"value": "sig", "counter": 7},
                "qr_code_data": "V0;...",
            },
        )

    provider = FiskalyProvider(transport=httpx.MockTransport(handler))
    active = provider.start(_command())
    finished = provider.finish(_command(FinishTransactionCommand))

    assert active.state == "ACTIVE"
    assert finished.state == "FINISHED"
    assert requests[0][1].endswith("/api/v2/auth")
    assert requests[1][0] == "PUT"
    assert requests[1][3] == "Bearer token-123"
    assert requests[2][2]["state"] == "FINISHED"
    assert len([request for request in requests if request[1].endswith("/auth")]) == 1


def test_fiskaly_keeps_tse_and_dsfinvk_exports_separate(monkeypatch):
    monkeypatch.setenv("FISKALY_API_KEY", "key")
    monkeypatch.setenv("FISKALY_API_SECRET", "secret")
    paths: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        paths.append(request.url.path)
        if request.url.path.endswith("/auth"):
            return httpx.Response(200, json={"access_token": "token"})
        return httpx.Response(200, json={"_id": "EXP", "state": "PENDING"})

    provider = FiskalyProvider(transport=httpx.MockTransport(handler))
    for export_type in ("tse", "dsfinvk"):
        provider.request_export(
            ExportCommand(
                export_id=f"EXP-{export_type}",
                cash_register_id="REGISTER-1",
                period_from=date(2026, 6, 1),
                period_to=date(2026, 6, 9),
                export_type=export_type,
            )
        )

    assert any("/tss/REGISTER-1/export/EXP-tse" in path for path in paths)
    assert any("/cash_registers/REGISTER-1/exports/EXP-dsfinvk" in path for path in paths)


def test_swissbit_is_blocked_without_partner_contract(monkeypatch):
    monkeypatch.setenv("SWISSBIT_CLOUD_BASE_URL", "https://swissbit.example/api")
    monkeypatch.setenv("SWISSBIT_CLOUD_API_TOKEN", "token")
    monkeypatch.delenv("SWISSBIT_API_CONTRACT_VERSION", raising=False)

    readiness = SwissbitProvider(gateway=False).readiness()

    assert readiness.ready is False
    assert any("Partnerdokumentation" in blocker for blocker in readiness.blockers)


def test_swissbit_cloud_and_gateway_share_transaction_contract(monkeypatch):
    monkeypatch.setenv("SWISSBIT_API_CONTRACT_VERSION", "partner-v1")
    monkeypatch.setenv("SWISSBIT_CLOUD_BASE_URL", "https://cloud.example/api")
    monkeypatch.setenv("SWISSBIT_CLOUD_API_TOKEN", "cloud-token")
    monkeypatch.setenv("SWISSBIT_GATEWAY_BASE_URL", "http://127.0.0.1:8765")
    monkeypatch.setenv("SWISSBIT_GATEWAY_API_TOKEN", "gateway-token")

    def handler(request: httpx.Request) -> httpx.Response:
        payload = json.loads(request.content)
        assert request.headers["X-API-Contract-Version"] == "partner-v1"
        return httpx.Response(
            200,
            json={
                "id": payload["transaction_id"],
                "state": payload["state"],
                "signature_value": "swissbit-signature",
                "signature_counter": 3,
            },
        )

    for gateway in (False, True):
        result = SwissbitProvider(
            gateway=gateway,
            transport=httpx.MockTransport(handler),
        ).finish(_command(FinishTransactionCommand))
        assert result.state == "FINISHED"
        assert result.signature == "swissbit-signature"


def test_swissbit_rejects_dsfinvk_as_tse_is_not_dsfinvk(monkeypatch):
    monkeypatch.setenv("SWISSBIT_API_CONTRACT_VERSION", "partner-v1")
    monkeypatch.setenv("SWISSBIT_CLOUD_BASE_URL", "https://cloud.example/api")
    monkeypatch.setenv("SWISSBIT_CLOUD_API_TOKEN", "token")
    provider = SwissbitProvider(gateway=False)

    with pytest.raises(FiscalProviderError, match="nur TSE-Exporte"):
        provider.request_export(
            ExportCommand(
                export_id="EXP",
                cash_register_id="REGISTER",
                period_from=date(2026, 6, 1),
                period_to=date(2026, 6, 9),
                export_type="dsfinvk",
            )
        )


def test_simulation_is_explicit_and_blocked_in_production(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    provider = SimulationProvider()

    assert provider.readiness().ready is False
    with pytest.raises(FiscalProviderError, match="Produktion"):
        provider.start(_command())
