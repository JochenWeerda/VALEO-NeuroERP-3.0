"""Compatibility facade for the canonical fiscalization provider layer.

New code must use ``app.services.fiscalization``. This module keeps the
existing admin endpoints callable while removing the former proprietary HMAC
authentication and silent simulator fallback.
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import uuid4

from app.services.fiscalization.contracts import (
    ExportCommand,
    FinishTransactionCommand,
    FiscalLine,
    PaymentLine,
    StartTransactionCommand,
)
from app.services.fiscalization.providers import FiskalyProvider


def create_tse(tss_id: str | None = None) -> dict:
    provider = FiskalyProvider()
    readiness = provider.readiness()
    if not readiness.ready:
        raise RuntimeError("; ".join(readiness.blockers))
    return {
        "tss_id": tss_id or str(uuid4()),
        "status": "EXTERNAL_PROVISIONING_REQUIRED",
        "provider": "fiskaly",
        "hint": "TSS in fiskaly Dashboard/Management API provisionieren und danach dem VALEO-Terminal zuordnen.",
    }


def start_transaction(
    tss_id: str,
    client_id: str,
    amount_cents: int,
    payment_type: str = "Unbar",
) -> dict:
    tx_id = str(uuid4())
    amount = Decimal(amount_cents) / Decimal("100")
    result = FiskalyProvider().start(
        StartTransactionCommand(
            terminal_id=client_id,
            cash_register_id=tss_id,
            client_id=client_id,
            transaction_id=tx_id,
            lines=[FiscalLine(text="Legacy POS transaction", gross_amount=amount, vat_rate=Decimal("0"))],
            payments=[PaymentLine(method=payment_type, amount=amount)],
        )
    )
    return result.model_dump(mode="json")


def finish_transaction(tss_id: str, tx_id: str, amount_cents: int, counter: int) -> dict:
    amount = Decimal(amount_cents) / Decimal("100")
    result = FiskalyProvider().finish(
        FinishTransactionCommand(
            terminal_id="legacy-client",
            cash_register_id=tss_id,
            client_id="legacy-client",
            transaction_id=tx_id,
            lines=[FiscalLine(text="Legacy POS transaction", gross_amount=amount, vat_rate=Decimal("0"))],
            payments=[PaymentLine(method="Unbar", amount=amount)],
        )
    )
    return result.model_dump(mode="json")


def export_data(tss_id: str, start_date: str, end_date: str) -> dict:
    result = FiskalyProvider().request_export(
        ExportCommand(
            export_id=str(uuid4()),
            cash_register_id=tss_id,
            period_from=date.fromisoformat(start_date),
            period_to=date.fromisoformat(end_date),
            export_type="tse",
        )
    )
    return result.model_dump(mode="json")


def get_status() -> dict:
    return FiskalyProvider().readiness().model_dump(mode="json")
