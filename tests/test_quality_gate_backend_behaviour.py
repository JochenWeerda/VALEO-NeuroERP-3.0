"""Security/runtime regressions without a database or real mail transport."""
import asyncio
import logging
from decimal import Decimal
from types import SimpleNamespace

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
    from app.api.v1.schemas.ap_approval_workflow_schemas import ApprovalDecisionReference

    entscheidungen = []

    class Freigabe:
        def __init__(self, db, tenant_id):
            self.tenant_id = tenant_id

        def decide(self, action, user):
            entscheidungen.append((self.tenant_id, action, user))
            return SimpleNamespace(model_dump=lambda **k: {"status": "approved"})

    monkeypatch.setattr(api, "APApprovalWorkflowService", Freigabe)
    # Kein Anfrageparameter fuer den Freigeber (20.10.2026): eine Faelschung ist gar nicht uebergebbar.
    import inspect
    assert "approved_by" not in inspect.signature(api.approve_ap_invoice).parameters
    asyncio.run(api.approve_ap_invoice(
        "unit-invoice", ApprovalDecisionReference(approval_request_id="req-1"), db=object(),
        tenant_id="unit-tenant", user={"sub": "verified-user"},
    ))
    ((mandant, aktion, nutzer),) = entscheidungen
    assert mandant == "unit-tenant" and nutzer == {"sub": "verified-user"}
    assert (aktion.invoice_id, aktion.approval_request_id, aktion.action) == ("unit-invoice", "req-1", "approve")


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
