"""HTTP-Vertrag der Launcher-Inbox am vorhandenen Documents-Router."""

from __future__ import annotations

import uuid

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.core.database import SessionLocal
from app.documents.router import router
from helpers.dms_inbox import has_tenant_column, insert_inbox
from testgrenze import ersetze_mandant, ersetze_nutzer

pytestmark = [pytest.mark.integration, pytest.mark.needs_live_db]

WEG = "/api/mcp/documents"


@pytest.fixture
def client(require_db):
    mandant = f"inbox-{uuid.uuid4().hex[:8]}"
    app = FastAPI()
    app.include_router(router)
    ersetze_nutzer(app, "EINKAUF_BEARBEITEN")
    ersetze_mandant(app, mandant)
    return TestClient(app, raise_server_exceptions=False), mandant


# Artikel-FK braucht kanonischen Tenant; Inbox-Zeilen teilen denselben Mandanten.
_TENANT_A = "00000000-0000-0000-0000-000000000001"


@pytest.fixture
def demo_client(require_db):
    app = FastAPI()
    app.include_router(router)
    ersetze_nutzer(app, "EINKAUF_BEARBEITEN")
    ersetze_mandant(app, _TENANT_A)
    return TestClient(app, raise_server_exceptions=False), _TENANT_A


def test_queue_maps_pending_inbox_and_does_not_book(client):
    http, mandant = client
    item_id = f"INBOX-{uuid.uuid4().hex[:10]}"
    number = f"RE-{uuid.uuid4().hex[:6]}"
    with SessionLocal() as db:
        if not has_tenant_column(db):
            pytest.skip("dms_inbox.tenant_id fehlt — Migration dms_inbox_tenant_20261022 zuerst")
        insert_inbox(db, item_id=item_id, tenant_id=mandant, number=number)
        db.commit()
    try:
        response = http.get(f"{WEG}/inbox/queue")
        assert response.status_code == 200, response.text
        body = response.json()
        assert body["ok"] is True
        assert body["booking_allowed"] is False
        assert body["source"] == "dms_inbox"
        match = next(item for item in body["items"] if item["id"] == item_id)
        assert match["proposal"]["target_route"] == "/einkauf/rechnung-eingang-erfassung"
        assert match["can_open"] is True
        assert match["command"]["executable"] is False
        assert match["match_values"]["supplierId"] == "L-22"
        assert match["actions"][0]["enabled"] is True
        assert match["actions"][0]["href"] == f"{match['proposal']['target_route']}?inbox={item_id}"
        assert match["command"]["prefill"]["documentId"] == item_id
        assert match["command"]["prefill"]["partner"]["id"] == "L-22"
        assert match["command"]["prefill"]["booking"] is False
        assert match["command"]["prefill"]["maskConsumesPrefill"] is True
        assert match["proposal"]["document_kind"] is None

        prepared = http.post(f"{WEG}/inbox/{item_id}/prepare")
        assert prepared.status_code == 200, prepared.text
        command = prepared.json()["command"]
        assert command["booking"] is False
        assert command["target_route"] == "/einkauf/rechnung-eingang-erfassung"

        approve = http.post(f"{WEG}/inbox/{item_id}/approve")
        assert approve.status_code == 409, approve.text
        detail = approve.json()["detail"]
        assert detail["code"] == "booking_not_from_inbox"
        assert detail["open_mask"] == "/einkauf/rechnung-eingang-erfassung"
    finally:
        with SessionLocal() as db:
            db.execute(text("DELETE FROM domain_shared.dms_inbox WHERE id = :id"), {"id": item_id})
            db.commit()
    assert mandant.startswith("inbox-")


def test_queue_hides_foreign_tenant_entries(client):
    http, mandant = client
    own_id = f"INBOX-{uuid.uuid4().hex[:10]}"
    foreign_id = f"INBOX-{uuid.uuid4().hex[:10]}"
    foreign_tenant = f"fremd-{uuid.uuid4().hex[:8]}"
    with SessionLocal() as db:
        if not has_tenant_column(db):
            pytest.skip("dms_inbox.tenant_id fehlt — Migration dms_inbox_tenant_20261022 zuerst")
        insert_inbox(db, item_id=own_id, tenant_id=mandant, number=f"RE-{uuid.uuid4().hex[:6]}")
        insert_inbox(
            db,
            item_id=foreign_id,
            tenant_id=foreign_tenant,
            number=f"RE-{uuid.uuid4().hex[:6]}",
        )
        db.commit()
    try:
        response = http.get(f"{WEG}/inbox/queue")
        assert response.status_code == 200, response.text
        ids = {item["id"] for item in response.json()["items"]}
        assert own_id in ids
        assert foreign_id not in ids

        foreign = http.get(f"{WEG}/inbox/{foreign_id}")
        assert foreign.status_code == 404
    finally:
        with SessionLocal() as db:
            db.execute(
                text("DELETE FROM domain_shared.dms_inbox WHERE id = :a OR id = :b"),
                {"a": own_id, "b": foreign_id},
            )
            db.commit()


def test_queue_maps_existing_document_kind_without_booking(client):
    http, mandant = client
    item_id = f"INBOX-{uuid.uuid4().hex[:10]}"
    number = f"RE-{uuid.uuid4().hex[:6]}"
    with SessionLocal() as db:
        if not has_tenant_column(db):
            pytest.skip("dms_inbox.tenant_id fehlt — Migration dms_inbox_tenant_20261022 zuerst")
        insert_inbox(
            db,
            item_id=item_id,
            tenant_id=mandant,
            number=number,
            ocr="Rechnung Rechnungsnummer MwSt Zahlungsziel",
        )
        db.commit()
    try:
        response = http.get(f"{WEG}/inbox/queue")
        assert response.status_code == 200, response.text
        match = next(item for item in response.json()["items"] if item["id"] == item_id)
        assert match["proposal"]["document_kind"] == "EINGANGSRECHNUNG"
        assert match["can_open"] is True
        assert match["command"]["prefill"]["maskConsumesPrefill"] is True

        approve = http.post(f"{WEG}/inbox/{item_id}/approve")
        assert approve.status_code == 409, approve.text
        detail = approve.json()["detail"]
        assert detail["code"] == "booking_not_from_inbox"
        assert detail["can_open"] is True
        assert detail["prefill"]["maskConsumesPrefill"] is True
    finally:
        with SessionLocal() as db:
            db.execute(text("DELETE FROM domain_shared.dms_inbox WHERE id = :id"), {"id": item_id})
            db.commit()


def test_unknown_inbox_item_is_404(client):
    http, _mandant = client
    response = http.get(f"{WEG}/inbox/missing-{uuid.uuid4().hex}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Inbox-Dokument nicht gefunden"


def test_demo_inbox_chain_match_propose_prefill_without_booking(demo_client):
    """DEMO-NWF/GAP per TestClient: Position→Artikel-Match, partner_gap→Propose, Prefill."""
    from app.infrastructure.models import Article

    http, mandant = demo_client
    suffix = uuid.uuid4().hex[:8]
    nwf_id = f"INBOX-DEMO-LF-NWF-{suffix}"
    gap_id = f"INBOX-DEMO-LF-GAP-{suffix}"
    article_id = f"art-demo-{suffix}"
    article_nr = f"DEMO-NWF-WHEAT-{suffix}"
    position = {
        "artikel_name": "Demo-Schrot Weizen",
        "artikel_nr": article_nr,
        "menge": 10,
        "einheit": "t",
    }
    with SessionLocal() as db:
        if not has_tenant_column(db):
            pytest.skip("dms_inbox.tenant_id fehlt — Migration dms_inbox_tenant_20261022 zuerst")
        db.add(
            Article(
                id=article_id,
                article_number=article_nr,
                name="Demo-Schrot Weizen",
                unit="t",
                category="Futtermittel",
                sales_price=0,
                tenant_id=mandant,
            )
        )
        insert_inbox(
            db,
            item_id=nwf_id,
            tenant_id=mandant,
            number=f"DEMO-NWF-{suffix}",
            ocr="Nordwestdeutsche Futtermittel Rechnung DEMO",
            confidence=0.85,
            parsed_fields={
                "invoice_number": f"DEMO-NWF-{suffix}",
                "supplier": "Nordwestdeutsche Futtermittel GmbH & Co. KG",
                "supplier_id": "DEMO-LF-NWF",
                "domain": "purchase",
                "document_type": "supplier_invoice",
                "positionen": [position],
            },
        )
        insert_inbox(
            db,
            item_id=gap_id,
            tenant_id=mandant,
            number=f"DEMO-GAP-{suffix}",
            ocr="Nordkorn Handelsgesellschaft Demo OHG DEMO-LF-GAP",
            confidence=0.85,
            parsed_fields={
                "invoice_number": f"DEMO-GAP-{suffix}",
                "supplier": "Nordkorn Handelsgesellschaft Demo OHG",
                "supplier_id": "DEMO-LF-GAP",
                "domain": "purchase",
                "document_type": "supplier_invoice",
                "positionen": [position],
            },
        )
        db.commit()
    try:
        response = http.get(f"{WEG}/inbox/queue")
        assert response.status_code == 200, response.text
        body = response.json()
        assert body["ok"] is True
        assert body["booking_allowed"] is False
        by_id = {item["id"]: item for item in body["items"]}
        assert nwf_id in by_id and gap_id in by_id

        nwf = by_id[nwf_id]
        assert any(u["code"] == "partner_nicht_gefunden" for u in nwf["uncertainties"])
        nwf_supplier = nwf["master_data_proposals"]["supplier"]
        assert nwf_supplier["status"] == "propose"
        assert nwf_supplier["payload"]["lieferantennummer"] == "DEMO-LF-NWF"
        nwf_articles = nwf["master_data_proposals"]["articles"]
        assert any(
            row.get("kind") == "article_match" and row.get("status") == "matched"
            for row in nwf_articles
        )
        assert nwf["command"]["prefill"]["documentId"] == nwf_id
        assert nwf["command"]["prefill"]["maskConsumesPrefill"] is True
        assert nwf["command"]["prefill"]["booking"] is False
        assert nwf["command"]["executable"] is False
        assert "/einkauf/rechnung-eingang-erfassung" in (nwf["actions"][0]["href"] or "")

        gap = by_id[gap_id]
        assert any(u["code"] == "partner_nicht_gefunden" for u in gap["uncertainties"])
        gap_supplier = gap["master_data_proposals"]["supplier"]
        assert gap_supplier["status"] == "propose"
        assert gap_supplier["payload"]["lieferantennummer"] == "DEMO-LF-GAP"
        assert gap_supplier["payload"]["firmenname"] == "Nordkorn Handelsgesellschaft Demo OHG"
        assert any(a["key"] == "propose_supplier_create" for a in gap["actions"])
        assert gap["command"]["prefill"]["documentId"] == gap_id
        assert gap["command"]["prefill"]["matchValues"]["supplierId"] == "DEMO-LF-GAP"

        approve = http.post(f"{WEG}/inbox/{gap_id}/approve")
        assert approve.status_code == 409, approve.text
        assert approve.json()["detail"]["code"] == "booking_not_from_inbox"
    finally:
        with SessionLocal() as db:
            db.execute(
                text("DELETE FROM domain_shared.dms_inbox WHERE id IN (:a, :b)"),
                {"a": nwf_id, "b": gap_id},
            )
            db.execute(
                text("DELETE FROM domain_inventory.articles WHERE id = :id"),
                {"id": article_id},
            )
            db.commit()
