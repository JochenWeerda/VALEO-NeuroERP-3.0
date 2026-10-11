"""Security/runtime regressions without a database or real mail transport."""
import asyncio
import logging
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest


def test_newsletter_failure_cannot_inject_logs_or_expose_recipient(monkeypatch, caplog):
    from app.api.v1.endpoints import compat
    from app.services import mail_versand

    monkeypatch.setattr(mail_versand, "zugang", lambda *a, **k: None)
    def send(address, *args, **kwargs):
        if address == "private@example.org":
            raise mail_versand.MailVersandFehler("SMTP failure\r\nERROR forged log entry")
    monkeypatch.setattr(mail_versand, "sende_mail", send)
    with caplog.at_level(logging.WARNING):
        result = asyncio.run(compat.crm_newsletter(
            compat.NewsletterRequest(empfaenger=["private@example.org", "accepted@example.org"], text="Ernte"),
            tenant_id="unit-tenant", db=object(), nutzer={"sub": "unit-user"},
        ))
    assert (result["versendet"], result["fehlgeschlagen"], result["status"]) == (1, 1, "teilweise_versendet")
    assert caplog.messages == ["Newsletter: SMTP-Versand fehlgeschlagen"]
    assert "private@example.org" not in caplog.text
    assert "forged log" not in caplog.text


def test_invoice_approver_comes_from_verified_user_not_query(monkeypatch):
    from app.api.v1.endpoints import ap_invoices as api

    invoice = {"status": "ENTWURF", "tenantId": "unit-tenant"}
    result = SimpleNamespace(status="approved", model_dump=lambda **k: {"status": "approved"})
    gateway = SimpleNamespace(
        get_status=AsyncMock(return_value=SimpleNamespace(status="not_requested")),
        request_approval=AsyncMock(), approve_invoice=AsyncMock(return_value=result),
    )
    monkeypatch.setattr(api, "get_repository", lambda db: object())
    monkeypatch.setattr(api, "_rechnung", lambda *a: invoice)
    monkeypatch.setattr(api, "save_to_store", lambda *a: None)
    monkeypatch.setattr(api.endpoint_gateways, "get_approval_workflow_gateway", lambda: gateway)
    db = object()
    asyncio.run(api.approve_ap_invoice(
        "unit-invoice", approved_by="forged-user", db=db, tenant_id="unit-tenant", user={"sub": "verified-user"},
    ))
    gateway.request_approval.assert_awaited_once_with("unit-invoice", "unit-tenant", "verified-user", None, db)
    gateway.approve_invoice.assert_awaited_once_with("unit-invoice", "unit-tenant", "verified-user", "approve", None, db)
    assert invoice["approvedBy"] == "verified-user"


@pytest.mark.parametrize("turnover", [Decimal("0"), Decimal("-1")])
def test_nonpositive_turnover_returns_requirement_without_dividing(turnover):
    from modules.einkauf.services.bestellvorschlag_service import _optimale_menge

    amount, storage, freight, reason = _optimale_menge(
        Decimal("100"), lagerkosten_satz=Decimal("1"), frachtkosten_fix=Decimal("10"), abverkauf_pro_tag=turnover,
    )
    assert (amount, storage, freight) == (Decimal("100"), Decimal("0"), Decimal("0"))
    assert "Kein Abverkauf" in reason


def test_positive_turnover_retains_lot_size_and_cost_calculation():
    from modules.einkauf.services.bestellvorschlag_service import _optimale_menge

    amount, storage, freight, _ = _optimale_menge(
        Decimal("100"), lagerkosten_satz=Decimal("1"), frachtkosten_fix=Decimal("10"), abverkauf_pro_tag=Decimal("2"),
    )
    assert amount == Decimal("44.72")
    assert storage == Decimal("499.97")
    assert freight == Decimal("22.36")
