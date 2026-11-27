"""Unit-Tests Self-Billing-API (M3) — Coverage New Code ohne Absenkung der QG.

Ruft die Endpoint-Funktionen direkt auf (wie wave31-DQ-Tests); Services/Repo werden
gezielt gepatcht, der Endpoint-Code selbst läuft.
"""
from __future__ import annotations

import asyncio
from datetime import date, datetime
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from app.api.v1.endpoints import self_billing as sb
from app.api.v1.endpoints.self_billing import (
    CreditNoteCreateIn,
    DisputeCreateIn,
    EinvoiceGenerateIn,
)


def _invoice(**kwargs):
    base = dict(
        id="inv-1",
        tenant_id="own",
        harvest_acceptance_id="ha-1",
        invoice_number="GS-1",
        provisional_invoice_number=None,
        status="draft",
        dispute_status=None,
        dispute_reason=None,
        dispute_date=None,
        dispute_user_id=None,
        total_net_amount_eur=Decimal("100"),
        total_vat_amount_eur=Decimal("7"),
        total_gross_amount_eur=Decimal("107"),
        vat_rate_percent=Decimal("7"),
        einvoice_sent_at=None,
        einvoice_received_at=None,
        mandatory_texts=None,
        created_at=datetime(2026, 1, 1),
        created_by="u",
        updated_at=None,
        updated_by=None,
        journal_entry_id=None,
        docflow_header_id=None,
        taxation_type="regular",
        tax_context={"taxation_type": "regular"},
        einvoice_xml=None,
        einvoice_pdf=None,
    )
    base.update(kwargs)
    return SimpleNamespace(**base)


def test_to_out_maps_service_invoice():
    out = sb._to_out(_invoice())
    assert out.id == "inv-1"
    assert out.total_gross_amount_eur == 107.0
    assert out.vat_rate_percent == 7.0


def test_create_credit_note_happy_path(monkeypatch):
    inv = _invoice()
    db = MagicMock()
    db.execute.return_value.rowcount = 1

    monkeypatch.setattr(sb, "create_credit_note", lambda *a, **k: inv)
    monkeypatch.setattr(sb, "SelfBillingRepositoryImpl", lambda *a, **k: MagicMock())

    payload = CreditNoteCreateIn(
        harvest_acceptance_id="ha-1",
        total_net_amount_eur=Decimal("100"),
        total_vat_amount_eur=Decimal("7"),
        total_gross_amount_eur=Decimal("107"),
        vat_rate_percent=Decimal("7"),
        taxation_type="regular",
    )
    result = asyncio.run(
        sb.create_credit_note_endpoint("ha-1", payload, db=db, tenant_id="own", request=None)
    )
    assert result.id == "inv-1"
    db.commit.assert_called_once()


def test_create_credit_note_ha_missing_404(monkeypatch):
    inv = _invoice()
    db = MagicMock()
    first = MagicMock(rowcount=0)
    second = MagicMock()
    second.scalar.return_value = None
    db.execute.side_effect = [first, second]
    monkeypatch.setattr(sb, "create_credit_note", lambda *a, **k: inv)
    monkeypatch.setattr(sb, "SelfBillingRepositoryImpl", lambda *a, **k: MagicMock())

    payload = CreditNoteCreateIn(
        harvest_acceptance_id="ha-x",
        total_net_amount_eur=Decimal("100"),
        total_vat_amount_eur=Decimal("7"),
        total_gross_amount_eur=Decimal("107"),
        vat_rate_percent=Decimal("7"),
    )
    with pytest.raises(HTTPException) as exc:
        asyncio.run(
            sb.create_credit_note_endpoint("ha-x", payload, db=db, tenant_id="own", request=None)
        )
    assert exc.value.status_code == 404


def test_create_credit_note_already_linked_409(monkeypatch):
    inv = _invoice()
    db = MagicMock()
    first = MagicMock(rowcount=0)
    second = MagicMock()
    second.scalar.return_value = "other-inv"
    db.execute.side_effect = [first, second]
    monkeypatch.setattr(sb, "create_credit_note", lambda *a, **k: inv)
    monkeypatch.setattr(sb, "SelfBillingRepositoryImpl", lambda *a, **k: MagicMock())

    payload = CreditNoteCreateIn(
        harvest_acceptance_id="ha-1",
        total_net_amount_eur=Decimal("100"),
        total_vat_amount_eur=Decimal("7"),
        total_gross_amount_eur=Decimal("107"),
        vat_rate_percent=Decimal("7"),
    )
    with pytest.raises(HTTPException) as exc:
        asyncio.run(
            sb.create_credit_note_endpoint("ha-1", payload, db=db, tenant_id="own", request=None)
        )
    assert exc.value.status_code == 409


def test_get_invoice_not_found_and_forbidden(monkeypatch):
    repo = MagicMock()
    repo.get_invoice_by_id.return_value = None
    monkeypatch.setattr(sb, "SelfBillingRepositoryImpl", lambda *a, **k: repo)
    with pytest.raises(HTTPException) as exc:
        asyncio.run(sb.get_invoice("missing", db=MagicMock(), tenant_id="own"))
    assert exc.value.status_code == 404

    repo.get_invoice_by_id.return_value = _invoice(tenant_id="other")
    with pytest.raises(HTTPException) as exc:
        asyncio.run(sb.get_invoice("inv-1", db=MagicMock(), tenant_id="own"))
    assert exc.value.status_code == 403

    repo.get_invoice_by_id.return_value = _invoice()
    out = asyncio.run(sb.get_invoice("inv-1", db=MagicMock(), tenant_id="own"))
    assert out.id == "inv-1"


def test_get_invoice_by_harvest_acceptance_paths(monkeypatch):
    repo = MagicMock()
    monkeypatch.setattr(sb, "SelfBillingRepositoryImpl", lambda *a, **k: repo)

    repo.get_invoice_by_harvest_acceptance.return_value = None
    assert (
        asyncio.run(
            sb.get_invoice_by_harvest_acceptance("ha-1", db=MagicMock(), tenant_id="own")
        )
        is None
    )

    repo.get_invoice_by_harvest_acceptance.return_value = _invoice(tenant_id="x")
    with pytest.raises(HTTPException) as exc:
        asyncio.run(
            sb.get_invoice_by_harvest_acceptance("ha-1", db=MagicMock(), tenant_id="own")
        )
    assert exc.value.status_code == 403

    repo.get_invoice_by_harvest_acceptance.return_value = _invoice()
    out = asyncio.run(
        sb.get_invoice_by_harvest_acceptance("ha-1", db=MagicMock(), tenant_id="own")
    )
    assert out.invoice_number == "GS-1"


def test_issue_invoice_requires_supplier_and_profile(monkeypatch):
    repo = MagicMock()
    inv = _invoice()
    repo.get_invoice_by_id.return_value = inv
    monkeypatch.setattr(sb, "SelfBillingRepositoryImpl", lambda *a, **k: repo)

    harvest = SimpleNamespace(customer_id=None, delivery_date=date(2026, 1, 15))
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = harvest

    with pytest.raises(HTTPException) as exc:
        asyncio.run(sb.issue_invoice_endpoint("inv-1", db=db, tenant_id="own", request=None))
    assert exc.value.status_code == 422
    assert "Lieferant" in str(exc.value.detail)


def test_issue_invoice_happy_path(monkeypatch):
    repo = MagicMock()
    inv = _invoice(status="issued")
    repo.get_invoice_by_id.return_value = _invoice()
    monkeypatch.setattr(sb, "SelfBillingRepositoryImpl", lambda *a, **k: repo)
    monkeypatch.setattr(sb, "issue_invoice", lambda *a, **k: inv)

    harvest = SimpleNamespace(customer_id="cust-1", delivery_date=date(2026, 1, 15))
    customer = SimpleNamespace(business_partner_id="bp-1")
    db = MagicMock()

    def _query(model):
        q = MagicMock()
        name = getattr(model, "__name__", str(model))
        if "Harvest" in name:
            q.filter.return_value.first.return_value = harvest
        else:
            q.filter.return_value.first.return_value = customer
        return q

    db.query.side_effect = _query

    with patch(
        "modules.agrar.services.tax_profile_service.require_self_billing_agreement"
    ), patch(
        "modules.agrar.services.tax_profile_service.get_taxation_type_for_supplier",
        return_value="regular",
    ):
        out = asyncio.run(
            sb.issue_invoice_endpoint("inv-1", db=db, tenant_id="own", request=None)
        )
    assert out.status == "issued"


def test_generate_and_send_einvoice(monkeypatch):
    repo = MagicMock()
    inv = _invoice()
    repo.get_invoice_by_id.return_value = inv
    monkeypatch.setattr(sb, "SelfBillingRepositoryImpl", lambda *a, **k: repo)
    monkeypatch.setattr(sb, "generate_einvoice", lambda *a, **k: inv)
    monkeypatch.setattr(sb, "send_einvoice", lambda *a, **k: inv)

    payload = EinvoiceGenerateIn(
        supplier_data={"name": "A"},
        customer_data={"name": "B"},
        line_items=[{"qty": 1}],
        format="xrechnung",
    )
    out = asyncio.run(
        sb.generate_einvoice_endpoint("inv-1", payload, db=MagicMock(), tenant_id="own")
    )
    assert out.id == "inv-1"
    out2 = asyncio.run(
        sb.send_einvoice_endpoint("inv-1", recipient_email="a@b.c", db=MagicMock(), tenant_id="own")
    )
    assert out2.id == "inv-1"


def test_create_dispute_endpoint(monkeypatch):
    repo = MagicMock()
    inv = _invoice(status="disputed")
    dispute = SimpleNamespace(
        id="d1",
        dispute_type="amount",
        dispute_reason="zu hoch",
        disputed_amount_eur=Decimal("10"),
        status="open",
        created_at=datetime(2026, 1, 2),
    )
    repo.get_invoice_by_id.return_value = _invoice()
    monkeypatch.setattr(sb, "SelfBillingRepositoryImpl", lambda *a, **k: repo)
    monkeypatch.setattr(sb, "create_dispute", lambda *a, **k: (inv, dispute))

    payload = DisputeCreateIn(
        dispute_type="amount", dispute_reason="zu hoch", disputed_amount_eur=10
    )
    result = asyncio.run(
        sb.create_dispute_endpoint("inv-1", payload, db=MagicMock(), tenant_id="own", request=None)
    )
    assert result["dispute"]["id"] == "d1"
    assert result["invoice"].id == "inv-1"


def test_storno_invoice_with_journal(monkeypatch):
    repo = MagicMock()
    inv = _invoice(status="booked", journal_entry_id="j1")
    repo.get_invoice_by_id.return_value = inv
    storno = _invoice(id="inv-st", invoice_number="GS-1-ST", status="draft")
    monkeypatch.setattr(sb, "SelfBillingRepositoryImpl", lambda *a, **k: repo)
    monkeypatch.setattr(sb, "create_credit_note", lambda *a, **k: storno)
    monkeypatch.setattr(
        "app.services.self_billing_buchung.storno_self_billing",
        lambda *a, **k: {"journal_entry_id": "j1", "reversal_entry_id": "j2"},
    )
    db = MagicMock()
    result = asyncio.run(
        sb.storno_invoice("inv-1", db=db, tenant_id="own", request=None)
    )
    assert result["storno_invoice"].invoice_number == "GS-1-ST"
    db.commit.assert_called_once()


def test_export_invoice_xml_pdf_and_bad_format(monkeypatch):
    repo = MagicMock()
    monkeypatch.setattr(sb, "SelfBillingRepositoryImpl", lambda *a, **k: repo)

    repo.get_invoice_by_id.return_value = _invoice(einvoice_xml=None)
    with pytest.raises(HTTPException) as exc:
        asyncio.run(sb.export_invoice("inv-1", format="xml", db=MagicMock(), tenant_id="own"))
    assert exc.value.status_code == 404

    repo.get_invoice_by_id.return_value = _invoice(einvoice_xml="<Invoice/>")
    resp = asyncio.run(sb.export_invoice("inv-1", format="xml", db=MagicMock(), tenant_id="own"))
    assert resp.media_type == "application/xml"

    repo.get_invoice_by_id.return_value = _invoice(einvoice_pdf=b"%PDF")
    resp = asyncio.run(sb.export_invoice("inv-1", format="pdf", db=MagicMock(), tenant_id="own"))
    assert resp.media_type == "application/pdf"

    with pytest.raises(HTTPException) as exc:
        asyncio.run(sb.export_invoice("inv-1", format="csv", db=MagicMock(), tenant_id="own"))
    assert exc.value.status_code == 400


def test_get_disputes_list(monkeypatch):
    repo = MagicMock()
    repo.get_invoice_by_id.return_value = _invoice()
    repo.get_disputes_by_invoice.return_value = [
        SimpleNamespace(
            id="d1",
            dispute_type="quality",
            dispute_reason="Feucht",
            disputed_amount_eur=None,
            status="open",
            resolution_notes=None,
            resolved_by=None,
            resolved_at=None,
            created_at=datetime(2026, 1, 3),
            created_by="u",
        )
    ]
    monkeypatch.setattr(sb, "SelfBillingRepositoryImpl", lambda *a, **k: repo)
    rows = asyncio.run(sb.get_disputes("inv-1", db=MagicMock(), tenant_id="own"))
    assert rows[0]["id"] == "d1"


def test_buche_gutschrift_already_booked_409(monkeypatch):
    repo = MagicMock()
    repo.get_invoice_by_id.return_value = _invoice(status="booked", journal_entry_id="j1")
    monkeypatch.setattr(sb, "SelfBillingRepositoryImpl", lambda *a, **k: repo)
    with pytest.raises(HTTPException) as exc:
        asyncio.run(sb.buche_gutschrift("inv-1", db=MagicMock(), tenant_id="own", request=None))
    assert exc.value.status_code == 409


def test_preview_self_billing_happy_path():
    from app.api.v1.endpoints.self_billing import PreviewIn

    db = MagicMock()
    owned = MagicMock()
    owned.first.return_value = ("ha-1",)
    positions = MagicMock()
    positions.fetchall.return_value = [
        SimpleNamespace(
            position_number=1,
            description="Weizen",
            menge_kg=1000,
            preis_eur_t=200,
            qualitaet="A",
        )
    ]
    db.execute.side_effect = [owned, positions]
    payload = PreviewIn(
        harvest_acceptance_id="ha-1",
        total_net_amount_eur=Decimal("200"),
        total_gross_amount_eur=Decimal("214"),
        vat_rate_percent=Decimal("7"),
        taxation_type="regular",
    )
    result = asyncio.run(sb.preview_self_billing(payload, db=db, tenant_id="own"))
    assert result["status"] == "draft"
    assert result["line_items"][0]["description"] == "Weizen"
    assert result["total_net_amount_eur"] == 200.0


def test_preview_missing_acceptance_404():
    from app.api.v1.endpoints.self_billing import PreviewIn

    db = MagicMock()
    db.execute.return_value.first.return_value = None
    payload = PreviewIn(
        harvest_acceptance_id="missing",
        total_net_amount_eur=Decimal("10"),
        total_gross_amount_eur=Decimal("10.7"),
        vat_rate_percent=Decimal("7"),
    )
    with pytest.raises(HTTPException) as exc:
        asyncio.run(sb.preview_self_billing(payload, db=db, tenant_id="own"))
    assert exc.value.status_code == 404


def test_storno_rejects_wrong_status(monkeypatch):
    repo = MagicMock()
    repo.get_invoice_by_id.return_value = _invoice(status="draft")
    monkeypatch.setattr(sb, "SelfBillingRepositoryImpl", lambda *a, **k: repo)
    with pytest.raises(HTTPException) as exc:
        asyncio.run(sb.storno_invoice("inv-1", db=MagicMock(), tenant_id="own", request=None))
    assert exc.value.status_code == 400


def test_buche_gutschrift_happy_path(monkeypatch):
    repo = MagicMock()
    inv = _invoice(status="draft")
    booked = _invoice(status="booked", journal_entry_id="j-new", docflow_header_id="d1")
    repo.get_invoice_by_id.side_effect = [inv, booked]
    monkeypatch.setattr(sb, "SelfBillingRepositoryImpl", lambda *a, **k: repo)

    harvest = SimpleNamespace(
        customer_id="cust-1",
        delivery_date=date(2026, 1, 15),
        release_status="final",
        invoice_id=inv.id,
        article_id="art-1",
    )
    customer = SimpleNamespace(business_partner_id=None)
    db = MagicMock()

    def _query(model):
        q = MagicMock()
        name = getattr(model, "__name__", str(model))
        q.filter.return_value.first.return_value = (
            harvest if "Harvest" in name else customer
        )
        return q

    db.query.side_effect = _query

    with patch(
        "modules.agrar.services.tax_profile_service.require_self_billing_agreement"
    ), patch(
        "app.services.harvest_acceptance_service.HarvestAcceptanceService._book_self_billing_credit_note"
    ):
        result = asyncio.run(
            sb.buche_gutschrift("inv-1", db=db, tenant_id="own", request=None)
        )
    assert result["buchung_id"] == "j-new"
    db.commit.assert_called_once()
