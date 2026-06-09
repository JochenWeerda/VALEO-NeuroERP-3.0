from __future__ import annotations

import json
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Any
from uuid import uuid4

from sqlalchemy import text
from sqlalchemy.orm import Session

from .contracts import (
    CashPointClosingCommand,
    ExportCommand,
    FinishTransactionCommand,
    FiscalTransactionResult,
    PaymentLine,
    ProviderReadiness,
    ProviderResult,
    StartTransactionCommand,
)
from .providers import (
    FiscalProvider,
    FiskalyProvider,
    SimulationProvider,
    SwissbitProvider,
)

_SECRET_SETTING_TOKENS = ("secret", "token", "password", "credential", "api_key", "apikey")


class FiscalizationService:
    def __init__(self, db: Session, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id

    def get_config(self) -> dict[str, Any]:
        row = self.db.execute(
            text(
                """
                SELECT provider, dsfinvk_provider, cash_register_id, client_id,
                       simulation_allowed, settings, updated_at
                FROM domain_docflow.pos_fiscal_provider_configs
                WHERE tenant_id = :tenant_id
                """
            ),
            {"tenant_id": self.tenant_id},
        ).mappings().first()
        if not row:
            return {
                "provider": "simulation",
                "dsfinvk_provider": "simulation",
                "cash_register_id": None,
                "client_id": None,
                "simulation_allowed": False,
                "settings": {},
                "configured": False,
            }
        result = dict(row)
        result["configured"] = True
        result["settings"] = self._public_settings(result.get("settings") or {})
        return result

    def save_config(
        self,
        *,
        provider: str,
        dsfinvk_provider: str,
        cash_register_id: str,
        client_id: str,
        simulation_allowed: bool,
        settings: dict[str, Any],
    ) -> dict[str, Any]:
        forbidden = self._secret_paths(settings)
        if forbidden:
            raise ValueError(
                "Provider-Secrets duerfen nicht in tenantbezogenen POS-Einstellungen "
                f"gespeichert werden: {', '.join(forbidden)}"
            )
        self.db.execute(
            text(
                """
                INSERT INTO domain_docflow.pos_fiscal_provider_configs
                (tenant_id, provider, dsfinvk_provider, cash_register_id, client_id,
                 simulation_allowed, settings, created_at, updated_at)
                VALUES
                (:tenant_id, :provider, :dsfinvk_provider, :cash_register_id, :client_id,
                 :simulation_allowed, CAST(:settings AS jsonb), NOW(), NOW())
                ON CONFLICT (tenant_id) DO UPDATE SET
                  provider = EXCLUDED.provider,
                  dsfinvk_provider = EXCLUDED.dsfinvk_provider,
                  cash_register_id = EXCLUDED.cash_register_id,
                  client_id = EXCLUDED.client_id,
                  simulation_allowed = EXCLUDED.simulation_allowed,
                  settings = EXCLUDED.settings,
                  updated_at = NOW()
                """
            ),
            {
                "tenant_id": self.tenant_id,
                "provider": provider,
                "dsfinvk_provider": dsfinvk_provider,
                "cash_register_id": cash_register_id,
                "client_id": client_id,
                "simulation_allowed": simulation_allowed,
                "settings": json.dumps(settings),
            },
        )
        self.db.commit()
        return self.get_config()

    @staticmethod
    def _provider(name: str) -> FiscalProvider:
        if name == "fiskaly":
            return FiskalyProvider()
        if name == "swissbit_cloud":
            return SwissbitProvider(gateway=False)
        if name == "swissbit_gateway":
            return SwissbitProvider(gateway=True)
        if name == "simulation":
            return SimulationProvider()
        raise ValueError(f"Unsupported fiscal provider: {name}")

    def provider(self, *, dsfinvk: bool = False) -> FiscalProvider:
        config = self.get_config()
        name = config["dsfinvk_provider"] if dsfinvk else config["provider"]
        if name == "simulation" and not config.get("simulation_allowed"):
            raise RuntimeError("Simulation ist fuer diesen Mandanten nicht freigegeben")
        return self._provider(name)

    def readiness(self) -> dict[str, Any]:
        config = self.get_config()
        sign = self._provider(config["provider"]).readiness()
        dsfinvk = self._provider(config["dsfinvk_provider"]).readiness()
        config_blockers = []
        if not config["configured"]:
            config_blockers.append("Mandant hat noch keine Fiskalisierungskonfiguration")
        if not config.get("cash_register_id"):
            config_blockers.append("Kassen-/TSS-ID fehlt")
        if not config.get("client_id"):
            config_blockers.append("Client-ID fehlt")
        if config["provider"] == "simulation" and not config.get("simulation_allowed"):
            sign.ready = False
            sign.blockers.append("Mandantenkonfiguration erlaubt keine Simulation")
        if config["dsfinvk_provider"] == "simulation" and not config.get("simulation_allowed"):
            dsfinvk.ready = False
            dsfinvk.blockers.append("Mandantenkonfiguration erlaubt keine Simulation")
        products = FiskalyProvider().product_readiness()
        return {
            "configured": config["configured"],
            "config_blockers": config_blockers,
            "sign": sign.model_dump(mode="json"),
            "dsfinvk": dsfinvk.model_dump(mode="json"),
            "products": [product.model_dump(mode="json") for product in products],
            "ready": not config_blockers and sign.ready and dsfinvk.ready,
        }

    @classmethod
    def _secret_paths(cls, value: Any, prefix: str = "settings") -> list[str]:
        if isinstance(value, dict):
            paths: list[str] = []
            for key, nested in value.items():
                path = f"{prefix}.{key}"
                if any(token in str(key).lower() for token in _SECRET_SETTING_TOKENS):
                    paths.append(path)
                paths.extend(cls._secret_paths(nested, path))
            return paths
        if isinstance(value, list):
            paths = []
            for index, nested in enumerate(value):
                paths.extend(cls._secret_paths(nested, f"{prefix}[{index}]"))
            return paths
        return []

    @classmethod
    def _public_settings(cls, settings: dict[str, Any]) -> dict[str, Any]:
        return {
            key: value
            for key, value in settings.items()
            if not cls._secret_paths({key: value}, prefix="settings")
        }

    def start(self, command: StartTransactionCommand) -> FiscalTransactionResult:
        existing = self._transaction(command.transaction_id)
        if existing and existing["state"] in {"ACTIVE", "FINISHED"}:
            return self._stored_result(existing)
        result = self.provider().start(command)
        self._persist_transaction(command, result)
        self.db.commit()
        return result

    def finish(self, command: FinishTransactionCommand) -> FiscalTransactionResult:
        existing = self._transaction(command.transaction_id)
        if existing and existing["state"] == "FINISHED":
            return self._stored_result(existing)
        result = self.provider().finish(command)
        self._persist_transaction(command, result)
        self.db.commit()
        return result

    def close_cash_point(self, command: CashPointClosingCommand) -> ProviderResult:
        row = self.db.execute(
            text(
                """
                SELECT provider_response, provider, provider_reference, status, simulated
                FROM domain_docflow.pos_fiscal_closings
                WHERE tenant_id = :tenant_id AND closing_id = :closing_id
                """
            ),
            {"tenant_id": self.tenant_id, "closing_id": command.closing_id},
        ).mappings().first()
        if row and row["status"] in {"COMPLETED", "ACCEPTED", "SIMULATED"}:
            return ProviderResult(
                provider=row["provider"],
                operation="dsfinvk_closing",
                provider_reference=row["provider_reference"],
                status=row["status"],
                raw=row["provider_response"] or {},
                simulated=bool(row["simulated"]),
            )
        result = self.provider(dsfinvk=True).close_cash_point(command)
        self.db.execute(
            text(
                """
                INSERT INTO domain_docflow.pos_fiscal_closings
                (id, tenant_id, closing_id, provider, provider_reference, cash_register_id,
                 terminal_id, business_date, transaction_count, gross_total, status,
                 provider_response, simulated, created_at, updated_at)
                VALUES
                (:id, :tenant_id, :closing_id, :provider, :provider_reference, :cash_register_id,
                 :terminal_id, :business_date, :transaction_count, :gross_total, :status,
                 CAST(:provider_response AS jsonb), :simulated, NOW(), NOW())
                ON CONFLICT (tenant_id, closing_id) DO UPDATE SET
                  provider = EXCLUDED.provider,
                  provider_reference = EXCLUDED.provider_reference,
                  status = EXCLUDED.status,
                  provider_response = EXCLUDED.provider_response,
                  simulated = EXCLUDED.simulated,
                  updated_at = NOW()
                """
            ),
            {
                "id": str(uuid4()),
                "tenant_id": self.tenant_id,
                "closing_id": command.closing_id,
                "provider": result.provider,
                "provider_reference": result.provider_reference,
                "cash_register_id": command.cash_register_id,
                "terminal_id": command.terminal_id,
                "business_date": command.business_date,
                "transaction_count": command.transaction_count,
                "gross_total": command.gross_total,
                "status": result.status,
                "provider_response": json.dumps(result.raw),
                "simulated": result.simulated,
            },
        )
        self.db.commit()
        return result

    def request_export(self, command: ExportCommand) -> ProviderResult:
        result = self.provider(dsfinvk=command.export_type == "dsfinvk").request_export(command)
        self.db.execute(
            text(
                """
                INSERT INTO domain_docflow.pos_fiscal_exports
                (id, tenant_id, export_id, export_type, provider, provider_reference,
                 cash_register_id, period_from, period_to, status, download_url,
                 provider_response, simulated, created_at, updated_at)
                VALUES
                (:id, :tenant_id, :export_id, :export_type, :provider, :provider_reference,
                 :cash_register_id, :period_from, :period_to, :status, :download_url,
                 CAST(:provider_response AS jsonb), :simulated, NOW(), NOW())
                ON CONFLICT (tenant_id, export_id) DO UPDATE SET
                  status = EXCLUDED.status,
                  download_url = EXCLUDED.download_url,
                  provider_response = EXCLUDED.provider_response,
                  updated_at = NOW()
                """
            ),
            {
                "id": str(uuid4()),
                "tenant_id": self.tenant_id,
                "export_id": command.export_id,
                "export_type": command.export_type,
                "provider": result.provider,
                "provider_reference": result.provider_reference,
                "cash_register_id": command.cash_register_id,
                "period_from": command.period_from,
                "period_to": command.period_to,
                "status": result.status,
                "download_url": result.download_url,
                "provider_response": json.dumps(result.raw),
                "simulated": result.simulated,
            },
        )
        self.db.commit()
        return result

    def daily_summary(self, business_date: date, terminal_id: str | None = None) -> dict[str, Any]:
        params: dict[str, Any] = {"tenant_id": self.tenant_id, "business_date": business_date}
        terminal_clause = ""
        if terminal_id:
            params["terminal_id"] = terminal_id
            terminal_clause = "AND terminal_id = :terminal_id"
        row = self.db.execute(
            text(
                f"""
                SELECT COUNT(*) AS transaction_count,
                       COALESCE(SUM(gross_total), 0) AS gross_total,
                       COALESCE(SUM(CASE WHEN payment_breakdown ? 'BAR'
                         THEN (payment_breakdown->>'BAR')::numeric ELSE 0 END), 0) AS cash_total,
                       COALESCE(SUM(CASE WHEN payment_breakdown ? 'KARTE'
                         THEN (payment_breakdown->>'KARTE')::numeric ELSE 0 END), 0) AS card_total,
                       COUNT(*) FILTER (WHERE state <> 'FINISHED') AS incomplete_count
                FROM domain_docflow.pos_fiscal_transactions
                WHERE tenant_id = :tenant_id
                  AND business_date = :business_date
                  {terminal_clause}
                """
            ),
            params,
        ).mappings().one()
        return dict(row)

    def _transaction(self, transaction_id: str) -> Any:
        return self.db.execute(
            text(
                """
                SELECT *
                FROM domain_docflow.pos_fiscal_transactions
                WHERE tenant_id = :tenant_id AND transaction_id = :transaction_id
                """
            ),
            {"tenant_id": self.tenant_id, "transaction_id": transaction_id},
        ).mappings().first()

    @staticmethod
    def _stored_result(row: Any) -> FiscalTransactionResult:
        return FiscalTransactionResult(
            provider=row["provider"],
            transaction_id=row["transaction_id"],
            state=row["state"],
            signature=row["signature"],
            signature_counter=row["signature_counter"],
            serial_number=row["serial_number"],
            qr_code_data=row["qr_code_data"],
            started_at=row["started_at"],
            finished_at=row["finished_at"],
            provider_reference=row["provider_reference"],
            raw=row["provider_response"] or {},
            simulated=bool(row["simulated"]),
        )

    def _persist_transaction(
        self,
        command: StartTransactionCommand,
        result: FiscalTransactionResult,
    ) -> None:
        payment_breakdown: dict[str, Decimal] = {}
        for payment in command.payments:
            normalized_method = {
                "CASH": "BAR",
                "NON_CASH": "KARTE",
                "INTERNAL": "B2B",
            }.get(payment.method.upper(), payment.method.upper())
            payment_breakdown[normalized_method] = (
                payment_breakdown.get(normalized_method, Decimal("0")) + payment.amount
            )
        gross_total = sum((line.gross_amount for line in command.lines), Decimal("0"))
        now = datetime.now(timezone.utc)
        self.db.execute(
            text(
                """
                INSERT INTO domain_docflow.pos_fiscal_transactions
                (id, tenant_id, transaction_id, provider, provider_reference, terminal_id,
                 cash_register_id, client_id, business_date, transaction_type, state,
                 receipt_number, gross_total, payment_breakdown, signature,
                 signature_counter, serial_number, qr_code_data, started_at, finished_at,
                 provider_response, simulated, created_at, updated_at)
                VALUES
                (:id, :tenant_id, :transaction_id, :provider, :provider_reference, :terminal_id,
                 :cash_register_id, :client_id, :business_date, :transaction_type, :state,
                 :receipt_number, :gross_total, CAST(:payment_breakdown AS jsonb), :signature,
                 :signature_counter, :serial_number, :qr_code_data, :started_at, :finished_at,
                 CAST(:provider_response AS jsonb), :simulated, NOW(), NOW())
                ON CONFLICT (tenant_id, transaction_id) DO UPDATE SET
                  state = EXCLUDED.state,
                  provider_reference = EXCLUDED.provider_reference,
                  signature = EXCLUDED.signature,
                  signature_counter = EXCLUDED.signature_counter,
                  serial_number = EXCLUDED.serial_number,
                  qr_code_data = EXCLUDED.qr_code_data,
                  finished_at = EXCLUDED.finished_at,
                  provider_response = EXCLUDED.provider_response,
                  updated_at = NOW()
                """
            ),
            {
                "id": str(uuid4()),
                "tenant_id": self.tenant_id,
                "transaction_id": command.transaction_id,
                "provider": result.provider,
                "provider_reference": result.provider_reference,
                "terminal_id": command.terminal_id,
                "cash_register_id": command.cash_register_id,
                "client_id": command.client_id,
                "business_date": (result.started_at or now).date(),
                "transaction_type": command.transaction_type,
                "state": result.state,
                "receipt_number": command.receipt_number,
                "gross_total": gross_total,
                "payment_breakdown": json.dumps({key: str(value) for key, value in payment_breakdown.items()}),
                "signature": result.signature,
                "signature_counter": result.signature_counter,
                "serial_number": result.serial_number,
                "qr_code_data": result.qr_code_data,
                "started_at": result.started_at or now,
                "finished_at": result.finished_at,
                "provider_response": json.dumps(result.raw),
                "simulated": result.simulated,
            },
        )
