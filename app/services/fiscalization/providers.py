from __future__ import annotations

import hashlib
import os
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

import httpx

from .contracts import (
    CashPointClosingCommand,
    ExportCommand,
    FinishTransactionCommand,
    FiscalTransactionResult,
    FiscalProductReadiness,
    ProviderReadiness,
    ProviderResult,
    StartTransactionCommand,
)


class FiscalProviderError(RuntimeError):
    pass


class FiscalProvider(ABC):
    @abstractmethod
    def readiness(self) -> ProviderReadiness: ...

    @abstractmethod
    def start(self, command: StartTransactionCommand) -> FiscalTransactionResult: ...

    @abstractmethod
    def finish(self, command: FinishTransactionCommand) -> FiscalTransactionResult: ...

    @abstractmethod
    def close_cash_point(self, command: CashPointClosingCommand) -> ProviderResult: ...

    @abstractmethod
    def request_export(self, command: ExportCommand) -> ProviderResult: ...


class _HttpProvider(FiscalProvider):
    def __init__(self, *, timeout: float = 15.0, transport: httpx.BaseTransport | None = None):
        self.client = httpx.Client(timeout=timeout, transport=transport)

    def _request(self, method: str, url: str, **kwargs: Any) -> dict[str, Any]:
        try:
            response = self.client.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json() if response.content else {}
        except (httpx.HTTPError, ValueError) as exc:
            raise FiscalProviderError(f"Provider request failed: {method} {url}: {exc}") from exc


class FiskalyProvider(_HttpProvider):
    name = "fiskaly"

    def __init__(self, *, transport: httpx.BaseTransport | None = None):
        super().__init__(transport=transport)
        self.api_key = os.getenv("FISKALY_API_KEY", "")
        self.api_secret = os.getenv("FISKALY_API_SECRET", "")
        self.sign_base = os.getenv(
            "FISKALY_SIGN_BASE_URL",
            "https://kassensichv-middleware.fiskaly.com/api/v2",
        ).rstrip("/")
        self.dsfinvk_base = os.getenv(
            "FISKALY_DSFINVK_BASE_URL",
            "https://dsfinvk.fiskaly.com/api/v1",
        ).rstrip("/")
        self._token: str | None = None

    def readiness(self) -> ProviderReadiness:
        blockers = []
        if not self.api_key:
            blockers.append("FISKALY_API_KEY fehlt")
        if not self.api_secret:
            blockers.append("FISKALY_API_SECRET fehlt")
        return ProviderReadiness(
            provider="fiskaly",
            ready=not blockers,
            live=not blockers,
            blockers=blockers,
            capabilities=["sign", "tse_export", "dsfinvk_closing", "dsfinvk_export"],
            details={"sign_base_url": self.sign_base, "dsfinvk_base_url": self.dsfinvk_base},
        )

    def product_readiness(self) -> list[FiscalProductReadiness]:
        common_blockers = []
        if not self.api_key:
            common_blockers.append("FISKALY_API_KEY fehlt")
        if not self.api_secret:
            common_blockers.append("FISKALY_API_SECRET fehlt")
        products = (
            (
                "submit_de",
                "SUBMIT DE",
                "FISKALY_SUBMIT_DE_CONTRACT_VERSION",
                "https://developer.fiskaly.com/api/sign-de/submission/v1",
            ),
            (
                "receipt",
                "RECEIPT",
                "FISKALY_RECEIPT_CONTRACT_VERSION",
                "https://developer.fiskaly.com/api/receipt/v1",
            ),
            (
                "safe",
                "SAFE",
                "FISKALY_SAFE_CONTRACT_VERSION",
                "https://developer.fiskaly.com/api/safe/v1",
            ),
        )
        result: list[FiscalProductReadiness] = []
        for product, label, contract_env, documentation_url in products:
            contract_version = os.getenv(contract_env, "")
            blockers = list(common_blockers)
            if not contract_version:
                blockers.append(f"{contract_env} fehlt; Produktvertrag/Lizenz nicht freigegeben")
            result.append(
                FiscalProductReadiness(
                    product=product,  # type: ignore[arg-type]
                    label=label,
                    ready=not blockers,
                    blockers=blockers,
                    details={
                        "contract_version": contract_version or None,
                        "documentation_url": documentation_url,
                        "execution_enabled": False,
                        "execution_note": (
                            "Live-Ausfuehrung benoetigt einen separat abgenommenen "
                            "OpenAPI-Vertrag und wird nicht aus geratenen Payloads erzeugt."
                        ),
                    },
                )
            )
        return result

    def _headers(self) -> dict[str, str]:
        if not self.readiness().ready:
            raise FiscalProviderError("; ".join(self.readiness().blockers))
        if self._token is None:
            data = self._request(
                "POST",
                f"{self.sign_base}/auth",
                json={"api_key": self.api_key, "api_secret": self.api_secret},
            )
            self._token = str(data.get("access_token") or "")
            if not self._token:
                raise FiscalProviderError("fiskaly auth response has no access_token")
        return {"Authorization": f"Bearer {self._token}", "Content-Type": "application/json"}

    @staticmethod
    def _receipt_payload(command: StartTransactionCommand, state: str) -> dict[str, Any]:
        amounts: dict[str, str] = {}
        for line in command.lines:
            key = {
                Decimal("19"): "NORMAL",
                Decimal("7"): "REDUCED_1",
                Decimal("10.7"): "SPECIAL_RATE_1",
                Decimal("5.5"): "SPECIAL_RATE_2",
                Decimal("0"): "NULL",
            }.get(line.vat_rate, "NORMAL")
            amounts[key] = str(line.gross_amount + type(line.gross_amount)(amounts.get(key, "0")))
        return {
            "client_id": command.client_id,
            "type": command.transaction_type,
            "state": state,
            "schema": {
                "standard_v1": {
                    "receipt": {
                        "receipt_type": "RECEIPT",
                        "amounts_per_vat_rate": [
                            {"vat_rate": rate, "amount": amount} for rate, amount in amounts.items()
                        ],
                        "amounts_per_payment_type": [
                            {"payment_type": payment.method, "amount": str(payment.amount)}
                            for payment in command.payments
                        ],
                    }
                }
            },
        }

    @staticmethod
    def _result(transaction_id: str, state: str, data: dict[str, Any]) -> FiscalTransactionResult:
        signature = data.get("signature") or {}
        tss = data.get("tss") or {}
        return FiscalTransactionResult(
            provider="fiskaly",
            transaction_id=transaction_id,
            state=str(data.get("state") or state),
            signature=signature.get("value"),
            signature_counter=signature.get("counter"),
            serial_number=tss.get("serial_number") or data.get("tss_serial_number"),
            qr_code_data=data.get("qr_code_data"),
            started_at=data.get("time_start"),
            finished_at=data.get("time_end"),
            provider_reference=str(data.get("_id") or transaction_id),
            raw=data,
        )

    def start(self, command: StartTransactionCommand) -> FiscalTransactionResult:
        data = self._request(
            "PUT",
            f"{self.sign_base}/tss/{command.cash_register_id}/tx/{command.transaction_id}",
            headers=self._headers(),
            json=self._receipt_payload(command, "ACTIVE"),
        )
        return self._result(command.transaction_id, "ACTIVE", data)

    def finish(self, command: FinishTransactionCommand) -> FiscalTransactionResult:
        data = self._request(
            "PUT",
            f"{self.sign_base}/tss/{command.cash_register_id}/tx/{command.transaction_id}",
            headers=self._headers(),
            json=self._receipt_payload(command, "FINISHED"),
        )
        return self._result(command.transaction_id, "FINISHED", data)

    def close_cash_point(self, command: CashPointClosingCommand) -> ProviderResult:
        data = self._request(
            "PUT",
            f"{self.dsfinvk_base}/cash_registers/{command.cash_register_id}/cash_point_closings/{command.closing_id}",
            headers=self._headers(),
            json={
                "business_date": command.business_date.isoformat(),
                "transaction_count": command.transaction_count,
                "gross_total": str(command.gross_total),
                "payments": [payment.model_dump(mode="json") for payment in command.payments],
                **command.payload,
            },
        )
        return ProviderResult(
            provider="fiskaly",
            operation="dsfinvk_closing",
            provider_reference=str(data.get("_id") or command.closing_id),
            status=str(data.get("state") or data.get("status") or "COMPLETED"),
            raw=data,
        )

    def request_export(self, command: ExportCommand) -> ProviderResult:
        if command.export_type == "tse":
            url = f"{self.sign_base}/tss/{command.cash_register_id}/export/{command.export_id}"
        else:
            url = f"{self.dsfinvk_base}/cash_registers/{command.cash_register_id}/exports/{command.export_id}"
        data = self._request(
            "PUT",
            url,
            headers=self._headers(),
            json={"start_date": command.period_from.isoformat(), "end_date": command.period_to.isoformat()},
        )
        return ProviderResult(
            provider="fiskaly",
            operation=f"{command.export_type}_export",
            provider_reference=str(data.get("_id") or command.export_id),
            status=str(data.get("state") or data.get("status") or "PENDING"),
            download_url=data.get("download_url"),
            raw=data,
        )


class SwissbitProvider(_HttpProvider):
    def __init__(self, *, gateway: bool, transport: httpx.BaseTransport | None = None):
        super().__init__(transport=transport)
        self.gateway = gateway
        self.provider_name = "swissbit_gateway" if gateway else "swissbit_cloud"
        prefix = "SWISSBIT_GATEWAY" if gateway else "SWISSBIT_CLOUD"
        self.base_url = os.getenv(f"{prefix}_BASE_URL", "").rstrip("/")
        self.api_token = os.getenv(f"{prefix}_API_TOKEN", "")
        self.contract_version = os.getenv("SWISSBIT_API_CONTRACT_VERSION", "")

    def readiness(self) -> ProviderReadiness:
        blockers = []
        if not self.base_url:
            blockers.append("Swissbit Base URL fehlt")
        if not self.api_token:
            blockers.append("Swissbit API Token fehlt")
        if not self.contract_version:
            blockers.append("SWISSBIT_API_CONTRACT_VERSION fehlt; Partnerdokumentation nicht freigegeben")
        return ProviderReadiness(
            provider=self.provider_name,  # type: ignore[arg-type]
            ready=not blockers,
            live=not blockers and not self.gateway,
            blockers=blockers,
            capabilities=["sign", "tse_export"] + ([] if self.gateway else ["cloud_management"]),
            details={
                "base_url": self.base_url,
                "contract_version": self.contract_version or None,
                "mode": "hardware_gateway" if self.gateway else "cloud",
            },
        )

    def _headers(self) -> dict[str, str]:
        status = self.readiness()
        if not status.ready:
            raise FiscalProviderError("; ".join(status.blockers))
        return {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
            "X-API-Contract-Version": self.contract_version,
        }

    @staticmethod
    def _payload(command: StartTransactionCommand, state: str) -> dict[str, Any]:
        return {
            "transaction_id": command.transaction_id,
            "client_id": command.client_id,
            "cash_register_id": command.cash_register_id,
            "state": state,
            "type": command.transaction_type,
            "receipt_number": command.receipt_number,
            "lines": [line.model_dump(mode="json") for line in command.lines],
            "payments": [payment.model_dump(mode="json") for payment in command.payments],
        }

    def _transaction(self, command: StartTransactionCommand, state: str) -> FiscalTransactionResult:
        data = self._request(
            "PUT",
            f"{self.base_url}/transactions/{command.transaction_id}",
            headers=self._headers(),
            json=self._payload(command, state),
        )
        signature = data.get("signature") or {}
        return FiscalTransactionResult(
            provider=self.provider_name,  # type: ignore[arg-type]
            transaction_id=command.transaction_id,
            state=str(data.get("state") or state),
            signature=signature.get("value") or data.get("signature_value"),
            signature_counter=signature.get("counter") or data.get("signature_counter"),
            serial_number=data.get("serial_number"),
            qr_code_data=data.get("qr_code_data"),
            started_at=data.get("started_at"),
            finished_at=data.get("finished_at"),
            provider_reference=str(data.get("id") or command.transaction_id),
            raw=data,
        )

    def start(self, command: StartTransactionCommand) -> FiscalTransactionResult:
        return self._transaction(command, "ACTIVE")

    def finish(self, command: FinishTransactionCommand) -> FiscalTransactionResult:
        return self._transaction(command, "FINISHED")

    def close_cash_point(self, command: CashPointClosingCommand) -> ProviderResult:
        raise FiscalProviderError(
            "Swissbit TSE stellt keinen DSFinV-K-Cash-Point-Closing-Service bereit; "
            "verwenden Sie VALEO DSFinV-K oder einen getrennten DSFinV-K-Provider"
        )

    def request_export(self, command: ExportCommand) -> ProviderResult:
        if command.export_type != "tse":
            raise FiscalProviderError("Swissbit Adapter unterstuetzt nur TSE-Exporte")
        data = self._request(
            "POST",
            f"{self.base_url}/exports",
            headers=self._headers(),
            json={
                "export_id": command.export_id,
                "cash_register_id": command.cash_register_id,
                "period_from": command.period_from.isoformat(),
                "period_to": command.period_to.isoformat(),
            },
        )
        return ProviderResult(
            provider=self.provider_name,  # type: ignore[arg-type]
            operation="tse_export",
            provider_reference=str(data.get("id") or command.export_id),
            status=str(data.get("status") or "PENDING"),
            download_url=data.get("download_url"),
            raw=data,
        )


class SimulationProvider(FiscalProvider):
    def readiness(self) -> ProviderReadiness:
        production = os.getenv("APP_ENV", "").lower() in {"prod", "production"}
        return ProviderReadiness(
            provider="simulation",
            ready=not production,
            live=False,
            blockers=["Simulation ist in Produktion gesperrt"] if production else [],
            capabilities=["sign", "tse_export", "dsfinvk_closing", "dsfinvk_export"],
        )

    def _tx(self, command: StartTransactionCommand, state: str) -> FiscalTransactionResult:
        status = self.readiness()
        if not status.ready:
            raise FiscalProviderError(status.blockers[0])
        digest = hashlib.sha384(f"{command.transaction_id}:{state}".encode()).hexdigest()
        now = datetime.now(timezone.utc)
        return FiscalTransactionResult(
            provider="simulation",
            transaction_id=command.transaction_id,
            state=state,
            signature=digest,
            signature_counter=int(digest[:8], 16),
            serial_number="VALEO-EXPLICIT-SIMULATION",
            qr_code_data=f"V0;SIMULATION;{command.transaction_id};{digest[:24]}",
            started_at=now,
            finished_at=now if state == "FINISHED" else None,
            provider_reference=command.transaction_id,
            raw={"explicit_simulation": True},
            simulated=True,
        )

    def start(self, command: StartTransactionCommand) -> FiscalTransactionResult:
        return self._tx(command, "ACTIVE")

    def finish(self, command: FinishTransactionCommand) -> FiscalTransactionResult:
        return self._tx(command, "FINISHED")

    def close_cash_point(self, command: CashPointClosingCommand) -> ProviderResult:
        if not self.readiness().ready:
            raise FiscalProviderError(self.readiness().blockers[0])
        return ProviderResult(
            provider="simulation",
            operation="dsfinvk_closing",
            provider_reference=command.closing_id,
            status="SIMULATED",
            raw={"explicit_simulation": True},
            simulated=True,
        )

    def request_export(self, command: ExportCommand) -> ProviderResult:
        if not self.readiness().ready:
            raise FiscalProviderError(self.readiness().blockers[0])
        return ProviderResult(
            provider="simulation",
            operation=f"{command.export_type}_export",
            provider_reference=command.export_id,
            status="SIMULATED",
            raw={"explicit_simulation": True},
            simulated=True,
        )
