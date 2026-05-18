from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from app.core.database import SessionLocal
from app.domains.operations.models import FlowSpineInstance, FlowSpineInstanceEvent, PCNMeldung
from app.infrastructure.models import BusinessPartner, Customer
from app.main import app
from app.api.v1.endpoints import flow_spines


client = TestClient(app)
AUTH_HEADERS = {"Authorization": "Bearer dev-token"}


def _require_flow_spine_table(db) -> None:
    """Skipt den Test wenn DB nicht erreichbar oder Tabelle fehlt."""
    try:
        db.query(FlowSpineInstance).limit(1).all()
    except SQLAlchemyError:
        pytest.skip("DB nicht erreichbar oder ops_flow_spine_instances fehlt — alembic upgrade head ausführen")


def _require_flow_spine_event_table(db) -> None:
    """Skipt den Test wenn DB nicht erreichbar oder Event-Tabelle fehlt."""
    try:
        db.query(FlowSpineInstanceEvent).limit(1).all()
    except SQLAlchemyError:
        pytest.skip("DB nicht erreichbar oder ops_flow_spine_instance_events fehlt - alembic upgrade head ausfuehren")


def _require_pcn_table(db) -> None:
    """Skipt den Test wenn DB nicht erreichbar oder PCN-Tabelle fehlt."""
    try:
        db.query(PCNMeldung).limit(1).all()
    except SQLAlchemyError:
        pytest.skip("DB nicht erreichbar oder ops_pcn_meldungen fehlt — alembic upgrade head ausführen")


@pytest.fixture
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


# ── Catalog ───────────────────────────────────────────────────────────────────

def test_flow_spine_catalog_returns_all_processes():
    response = client.get("/api/v1/process/flow-spines/catalog")
    assert response.status_code == 200
    body = response.json()
    keys = {item["key"] for item in body["processes"]}
    assert {
        "order-to-cash",
        "procure-to-pay",
        "inventory-to-settlement",
        "harvest-to-settlement",
        "contract-to-settlement",
        "complaint-to-resolution",
        "service-to-customer",
        "finance-to-close",
        "compliance-to-report",
    }.issubset(keys)


def test_flow_spine_catalog_localizes_process_labels_for_german():
    response = client.get("/api/v1/process/flow-spines/catalog?lang=de")
    assert response.status_code == 200
    body = response.json()
    label_by_key = {item["key"]: item["label"] for item in body["processes"]}
    domain_by_key = {item["key"]: item["domain"] for item in body["processes"]}
    assert label_by_key["order-to-cash"] == "Auftrag bis Zahlung"
    assert label_by_key["procure-to-pay"] == "Bedarf bis Zahlung"
    assert domain_by_key["order-to-cash"] == "Vertrieb"
    assert domain_by_key["finance-to-close"] == "Finanzen"


# ── Workspace ─────────────────────────────────────────────────────────────────

def test_flow_spine_workspace_returns_contract_to_settlement_links():
    response = client.get("/api/v1/process/flow-spines/contract-to-settlement")
    assert response.status_code == 200
    body = response.json()
    assert body["process_key"] == "contract-to-settlement"
    assert body["focus_node_id"] == "acceptance"
    assert any(module["api_path"] == "/api/v1/agrar/harvest-acceptance" for module in body["right_panel"]["linked_modules"])
    assert any(node["label"] == "Settlement" for node in body["nodes"])


def test_flow_spine_workspace_returns_not_found_for_unknown_key():
    response = client.get("/api/v1/process/flow-spines/unknown-process")
    assert response.status_code == 404


def test_flow_spine_workspace_returns_compliance_to_report_links():
    response = client.get("/api/v1/process/flow-spines/compliance-to-report")
    assert response.status_code == 200
    body = response.json()
    assert body["process_key"] == "compliance-to-report"
    assert body["focus_node_id"] == "aggregation"
    assert any(module["api_path"] == "/api/v1/sustainability/read-model" for module in body["right_panel"]["linked_modules"])
    assert any(node["label"] == "Reporting" for node in body["nodes"])


def test_flow_spine_workspace_localizes_core_labels_for_german():
    response = client.get("/api/v1/process/flow-spines/order-to-cash?lang=de")
    assert response.status_code == 200
    body = response.json()
    assert body["breadcrumb"][0] == "Flow Spine"
    assert body["mode"] == "Ablauf"
    assert body["user_role"] == "Betriebsleitung"
    assert body["right_panel"]["domain"] == "Prozesse"


def test_flow_spine_workspace_resolves_customer_data_via_customer_record(monkeypatch, db):
    _require_flow_spine_table(db)

    tenant_id = "00000000-0000-0000-0000-000000000001"
    partner = BusinessPartner(
        partner_id="bp-flow-picker-001",
        tenant_id=tenant_id,
        partner_number="1004711",
        name_1="Raiffeisen Test eG",
        city="Oldenburg",
        postal_code="26121",
        is_customer=True,
    )
    customer = Customer(
        id="cust-flow-picker-001",
        tenant_id=tenant_id,
        customer_number="CUST-4711",
        company_name="Raiffeisen Test eG",
        business_partner_id=partner.partner_id,
        is_active=True,
    )
    db.add(partner)
    db.add(customer)
    db.commit()

    class _DummyNumbering:
        def next_number(self, domain: str) -> str:
            assert domain == "workflow_case"
            return "WF-CUST-001"

    monkeypatch.setattr(flow_spines, "get_numbering", lambda: _DummyNumbering())

    create_resp = client.post(
        "/api/v1/process/flow-spines/order-to-cash/instances",
        json={
            "customer_id": customer.id,
            "customer_name": customer.company_name,
            "subject": "Direktauftrag",
        },
        headers=AUTH_HEADERS,
    )
    assert create_resp.status_code == 201
    instance_id = create_resp.json()["instance_id"]

    workspace_resp = client.get(
        f"/api/v1/process/flow-spines/order-to-cash?instance_id={instance_id}",
        headers=AUTH_HEADERS,
    )
    assert workspace_resp.status_code == 200
    customer_data = workspace_resp.json()["customer_data"]
    assert customer_data["partner_id"] == partner.partner_id
    assert customer_data["partner_number"] == partner.partner_number
    assert customer_data["city"] == "Oldenburg"

    inst = db.get(FlowSpineInstance, instance_id)
    if inst:
        db.delete(inst)
    db.delete(customer)
    db.delete(partner)
    db.commit()


# ── Instance CRUD (PostgreSQL) ────────────────────────────────────────────────

def test_flow_spine_instance_creation_assigns_workflow_case_number(monkeypatch, db):
    _require_flow_spine_table(db)

    class _DummyNumbering:
        def next_number(self, domain: str) -> str:
            assert domain == "workflow_case"
            return "WF-00077"

    monkeypatch.setattr(flow_spines, "get_numbering", lambda: _DummyNumbering())

    response = client.post(
        "/api/v1/process/flow-spines/order-to-cash/instances",
        json={
            "customer_name": "Raiffeisen Nord eG",
            "subject": "24 t Kalkammonsalpeter",
            "entry_mode": "Direktauftrag",
        },
        headers=AUTH_HEADERS,
    )

    assert response.status_code == 201
    body = response.json()
    assert body["case_number"] == "WF-00077"
    assert body["entry_mode"] == "Direktauftrag"
    assert body["customer_name"] == "Raiffeisen Nord eG"
    assert body["label"] == "Raiffeisen Nord eG 24 t Kalkammonsalpeter"
    assert "instance_id" in body

    # Cleanup
    created_id = body["instance_id"]
    inst = db.get(FlowSpineInstance, created_id)
    if inst:
        db.delete(inst)
        db.commit()


def test_flow_spine_instance_list_returns_envelope(monkeypatch, db):
    _require_flow_spine_table(db)

    created_ids: list[str] = []

    class _DummyNumbering:
        _counter = 0

        def next_number(self, domain: str) -> str:
            self._counter += 1
            return f"WF-TEST-{self._counter:05d}"

    numbering = _DummyNumbering()
    monkeypatch.setattr(flow_spines, "get_numbering", lambda: numbering)

    resp = client.post(
        "/api/v1/process/flow-spines/order-to-cash/instances",
        json={"customer_name": "Genossen AG", "subject": "Raps 2026"},
        headers=AUTH_HEADERS,
    )
    assert resp.status_code == 201
    created_ids.append(resp.json()["instance_id"])

    response = client.get("/api/v1/process/flow-spines/order-to-cash/instances", headers=AUTH_HEADERS)
    assert response.status_code == 200
    body = response.json()
    assert "instances" in body
    assert "total" in body
    assert "skip" in body
    assert "limit" in body
    assert "tenant_id" in body
    assert isinstance(body["instances"], list)
    assert body["total"] >= 1

    # Cleanup
    for iid in created_ids:
        inst = db.get(FlowSpineInstance, iid)
        if inst:
            db.delete(inst)
    db.commit()


def test_flow_spine_instance_list_supports_search(monkeypatch, db):
    _require_flow_spine_table(db)

    created_ids: list[str] = []

    class _DummyNumbering:
        _counter = 0

        def next_number(self, domain: str) -> str:
            self._counter += 1
            return f"WF-SEARCH-{self._counter:05d}"

    numbering = _DummyNumbering()
    monkeypatch.setattr(flow_spines, "get_numbering", lambda: numbering)

    for payload in (
        {"customer_name": "Agrar Nord", "subject": "Raps 2026"},
        {"customer_name": "Muster Kunde", "subject": "Mais 2026"},
    ):
        resp = client.post(
            "/api/v1/process/flow-spines/order-to-cash/instances",
            json=payload,
            headers=AUTH_HEADERS,
        )
        assert resp.status_code == 201
        created_ids.append(resp.json()["instance_id"])

    response = client.get(
        "/api/v1/process/flow-spines/order-to-cash/instances?search=Muster",
        headers=AUTH_HEADERS,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["total"] >= 1
    assert all("Muster" in (item.get("customer_name") or item.get("label") or "") for item in body["instances"])

    for iid in created_ids:
        inst = db.get(FlowSpineInstance, iid)
        if inst:
            db.delete(inst)
    db.commit()


def test_flow_spine_instance_creation_roundtrips_partner_name_for_non_customer_flow(monkeypatch, db):
    _require_flow_spine_table(db)

    class _DummyNumbering:
        def next_number(self, domain: str) -> str:
            assert domain == "workflow_case"
            return "WF-00088"

    monkeypatch.setattr(flow_spines, "get_numbering", lambda: _DummyNumbering())

    response = client.post(
        "/api/v1/process/flow-spines/procure-to-pay/instances",
        json={
            "partner_name": "AGRAVIS Technik Nord",
            "subject": "Saisonbedarf 2026",
            "entry_mode": "Direktbestellung",
        },
        headers=AUTH_HEADERS,
    )

    assert response.status_code == 201
    body = response.json()
    assert body["case_number"] == "WF-00088"
    assert body["partner_name"] == "AGRAVIS Technik Nord"
    assert body["customer_name"] == "AGRAVIS Technik Nord"
    assert body["label"] == "AGRAVIS Technik Nord Saisonbedarf 2026"

    inst = db.get(FlowSpineInstance, body["instance_id"])
    if inst:
        db.delete(inst)
        db.commit()


def test_flow_spine_instance_transition(monkeypatch, db):
    _require_flow_spine_table(db)

    class _DummyNumbering:
        def next_number(self, domain: str) -> str:
            return "WF-TRANS-001"

    monkeypatch.setattr(flow_spines, "get_numbering", lambda: _DummyNumbering())

    create_resp = client.post(
        "/api/v1/process/flow-spines/order-to-cash/instances",
        json={"subject": "Weizen 500 t"},
        headers=AUTH_HEADERS,
    )
    assert create_resp.status_code == 201
    instance_id = create_resp.json()["instance_id"]

    trans_resp = client.post(
        f"/api/v1/process/flow-spines/order-to-cash/instances/{instance_id}/transitions",
        json={"node_id": "order", "new_status": "ok", "action_label": "Auftrag bestätigt", "user_id": "user-1"},
        headers=AUTH_HEADERS,
    )
    assert trans_resp.status_code == 200
    body = trans_resp.json()
    assert body["node_statuses"]["order"] == "ok"
    assert body["active_node_id"] == "order"
    assert body["last_actor"] == "user-1"

    # Cleanup
    inst = db.get(FlowSpineInstance, instance_id)
    if inst:
        db.delete(inst)
        db.commit()


def test_flow_spine_instance_delete(monkeypatch, db):
    _require_flow_spine_table(db)

    class _DummyNumbering:
        def next_number(self, domain: str) -> str:
            return "WF-DEL-001"

    monkeypatch.setattr(flow_spines, "get_numbering", lambda: _DummyNumbering())

    create_resp = client.post(
        "/api/v1/process/flow-spines/order-to-cash/instances",
        json={"subject": "Gerste 200 t"},
        headers=AUTH_HEADERS,
    )
    assert create_resp.status_code == 201
    instance_id = create_resp.json()["instance_id"]

    del_resp = client.delete(
        f"/api/v1/process/flow-spines/order-to-cash/instances/{instance_id}",
        headers=AUTH_HEADERS,
    )
    assert del_resp.status_code == 204

    get_resp = client.get(
        f"/api/v1/process/flow-spines/order-to-cash/instances/{instance_id}",
        headers=AUTH_HEADERS,
    )
    assert get_resp.status_code == 404


def test_flow_spine_instance_save_resume_and_timeline(monkeypatch, db):
    _require_flow_spine_table(db)
    _require_flow_spine_event_table(db)

    class _DummyNumbering:
        def next_number(self, domain: str) -> str:
            return "WF-LC-001"

    monkeypatch.setattr(flow_spines, "get_numbering", lambda: _DummyNumbering())

    create_resp = client.post(
        "/api/v1/process/flow-spines/order-to-cash/instances",
        json={"customer_name": "Timeline eG", "subject": "Raps 100 t"},
        headers=AUTH_HEADERS,
    )
    assert create_resp.status_code == 201
    instance_id = create_resp.json()["instance_id"]
    assert create_resp.json()["lifecycle_status"] == "draft"

    save_resp = client.post(
        f"/api/v1/process/flow-spines/order-to-cash/instances/{instance_id}/save",
        json={
            "resume_node_id": "order",
            "resume_route": "/workflow/flow-spine-order-to-cash?instanceId=test",
            "resume_payload": {"tab": "order-editor"},
            "business_status": "angebot_offen",
            "user_id": "user-save",
        },
        headers=AUTH_HEADERS,
    )
    assert save_resp.status_code == 200
    assert save_resp.json()["lifecycle_status"] == "in_progress"
    assert save_resp.json()["resume_node_id"] == "order"
    assert save_resp.json()["resume_payload"]["tab"] == "order-editor"

    hold_resp = client.post(
        f"/api/v1/process/flow-spines/order-to-cash/instances/{instance_id}/hold",
        json={
            "reason_category": "logistics",
            "reason_code": "delivery_deadline_missed",
            "reason_note": "Spedition blockiert",
            "blocked_until": "2026-04-20T08:00:00+00:00",
            "user_id": "user-hold",
        },
        headers=AUTH_HEADERS,
    )
    assert hold_resp.status_code == 200
    assert hold_resp.json()["lifecycle_status"] == "on_hold"

    resume_resp = client.post(
        f"/api/v1/process/flow-spines/order-to-cash/instances/{instance_id}/resume",
        json={"user_id": "user-resume"},
        headers=AUTH_HEADERS,
    )
    assert resume_resp.status_code == 200
    assert resume_resp.json()["lifecycle_status"] == "in_progress"
    assert resume_resp.json()["resume_target"]["node_id"] == "order"

    timeline_resp = client.get(
        f"/api/v1/process/flow-spines/order-to-cash/instances/{instance_id}/timeline",
        headers=AUTH_HEADERS,
    )
    assert timeline_resp.status_code == 200
    event_types = [event["event_type"] for event in timeline_resp.json()["events"]]
    assert event_types[:4] == ["created", "saved", "hold_set", "resumed"]

    inst = db.get(FlowSpineInstance, instance_id)
    if inst:
        db.delete(inst)
        db.commit()


def test_flow_spine_instance_cancel_and_fail_require_reasons(monkeypatch, db):
    _require_flow_spine_table(db)
    _require_flow_spine_event_table(db)

    class _DummyNumbering:
        _counter = 0

        def next_number(self, domain: str) -> str:
            self._counter += 1
            return f"WF-LC-{self._counter:03d}"

    numbering = _DummyNumbering()
    monkeypatch.setattr(flow_spines, "get_numbering", lambda: numbering)

    first = client.post(
        "/api/v1/process/flow-spines/order-to-cash/instances",
        json={"subject": "Abbruchtest"},
        headers=AUTH_HEADERS,
    )
    assert first.status_code == 201
    first_id = first.json()["instance_id"]

    invalid_cancel = client.post(
        f"/api/v1/process/flow-spines/order-to-cash/instances/{first_id}/cancel",
        json={"user_id": "user-cancel"},
        headers=AUTH_HEADERS,
    )
    assert invalid_cancel.status_code == 422

    cancel_resp = client.post(
        f"/api/v1/process/flow-spines/order-to-cash/instances/{first_id}/cancel",
        json={
            "reason_category": "customer",
            "reason_code": "customer_order_cancelled",
            "reason_note": "Kunde hat storniert",
            "user_id": "user-cancel",
        },
        headers=AUTH_HEADERS,
    )
    assert cancel_resp.status_code == 200
    assert cancel_resp.json()["lifecycle_status"] == "cancelled"
    assert cancel_resp.json()["cancellation_reason_code"] == "customer_order_cancelled"

    second = client.post(
        "/api/v1/process/flow-spines/order-to-cash/instances",
        json={"subject": "Fehlertest"},
        headers=AUTH_HEADERS,
    )
    assert second.status_code == 201
    second_id = second.json()["instance_id"]

    fail_resp = client.post(
        f"/api/v1/process/flow-spines/order-to-cash/instances/{second_id}/fail",
        json={
            "reason_category": "technical",
            "reason_code": "external_system_unavailable",
            "reason_note": "ERP-Downstream nicht erreichbar",
            "user_id": "user-fail",
        },
        headers=AUTH_HEADERS,
    )
    assert fail_resp.status_code == 200
    assert fail_resp.json()["lifecycle_status"] == "failed"
    assert fail_resp.json()["failure_reason_code"] == "external_system_unavailable"

    first_inst = db.get(FlowSpineInstance, first_id)
    second_inst = db.get(FlowSpineInstance, second_id)
    if first_inst:
        db.delete(first_inst)
    if second_inst:
        db.delete(second_inst)
    db.commit()


def test_flow_spine_instance_complete_sets_closed_fields(monkeypatch, db):
    _require_flow_spine_table(db)
    _require_flow_spine_event_table(db)

    class _DummyNumbering:
        def next_number(self, domain: str) -> str:
            return "WF-LC-COMPLETE"

    monkeypatch.setattr(flow_spines, "get_numbering", lambda: _DummyNumbering())

    create_resp = client.post(
        "/api/v1/process/flow-spines/order-to-cash/instances",
        json={"subject": "Abschlussfall"},
        headers=AUTH_HEADERS,
    )
    assert create_resp.status_code == 201
    instance_id = create_resp.json()["instance_id"]

    complete_resp = client.post(
        f"/api/v1/process/flow-spines/order-to-cash/instances/{instance_id}/complete",
        json={
            "reason_code": "workflow_completed",
            "reason_note": "Erfolgreich abgeschlossen",
            "user_id": "user-complete",
        },
        headers=AUTH_HEADERS,
    )
    assert complete_resp.status_code == 200
    body = complete_resp.json()
    assert body["lifecycle_status"] == "completed"
    assert body["completion_reason_code"] == "workflow_completed"
    assert body["closed_by"] == "user-complete"
    assert body["closed_at"] is not None

    timeline_resp = client.get(
        f"/api/v1/process/flow-spines/order-to-cash/instances/{instance_id}/timeline",
        headers=AUTH_HEADERS,
    )
    assert timeline_resp.status_code == 200
    assert timeline_resp.json()["events"][-1]["event_type"] == "completed"

    inst = db.get(FlowSpineInstance, instance_id)
    if inst:
        db.delete(inst)
        db.commit()


# ── PCN-Meldungen (Gap 104-C/D — DB-backed) ──────────────────────────────────

def test_pcn_meldung_create_valid(db):
    db.rollback()
    _require_pcn_table(db)
    response = client.post(
        "/api/v1/compliance/pcn-meldungen",
        json={
            "produktname": "Pflanzenschutzmittel XY",
            "ufi": "A1B2-C3D4-E5F6-G7H8",
            "cas_nummern": "1234-56-7",
            "gefahrenklassen": ["Akute Toxizität Kat. 3"],
            "verwendungskategorie": "Professionell",
            "pcnStatus": "entwurf",
        },
        headers=AUTH_HEADERS,
    )
    assert response.status_code == 201
    body = response.json()
    assert body["meldung_id"].startswith("PCN-")
    assert body["produktname"] == "Pflanzenschutzmittel XY"
    assert body["ufi"] == "A1B2-C3D4-E5F6-G7H8"
    assert body["pcnStatus"] == "entwurf"
    assert body["schema_version"] == 1

    # Cleanup
    m = db.get(PCNMeldung, body["meldung_id"])
    if m:
        db.delete(m)
        db.commit()


def test_pcn_meldung_create_invalid_ufi(db):
    _require_pcn_table(db)
    response = client.post(
        "/api/v1/compliance/pcn-meldungen",
        json={"produktname": "Test", "ufi": "INVALID-UFI", "gefahrenklassen": []},
        headers=AUTH_HEADERS,
    )
    assert response.status_code == 422


def test_pcn_meldung_create_without_ufi(db):
    _require_pcn_table(db)
    response = client.post(
        "/api/v1/compliance/pcn-meldungen",
        json={"produktname": "Düngemittel ABC", "gefahrenklassen": [], "pcnStatus": "entwurf"},
        headers=AUTH_HEADERS,
    )
    assert response.status_code == 201
    body = response.json()
    assert body["ufi"] == ""

    m = db.get(PCNMeldung, body["meldung_id"])
    if m:
        db.delete(m)
        db.commit()


def test_pcn_meldungen_list(db):
    _require_pcn_table(db)
    response = client.get("/api/v1/compliance/pcn-meldungen", headers=AUTH_HEADERS)
    assert response.status_code == 200
    body = response.json()
    assert "meldungen" in body
    assert "items" in body
    assert body["items"] == body["meldungen"]
    assert "total" in body
    assert "skip" in body
    assert "limit" in body
    assert isinstance(body["meldungen"], list)


def test_pcn_meldung_create_empty_produktname_rejected(db):
    _require_pcn_table(db)
    response = client.post(
        "/api/v1/compliance/pcn-meldungen",
        json={"produktname": "   ", "ufi": "", "gefahrenklassen": []},
        headers=AUTH_HEADERS,
    )
    assert response.status_code == 422


def test_pcn_meldung_create_respects_x_tenant_id_header(db):
    _require_pcn_table(db)
    tid = "pytest-tenant-pcn-xhdr"
    response = client.post(
        "/api/v1/compliance/pcn-meldungen",
        json={
            "produktname": "Tenant-Header-Test",
            "ufi": "K0L1-M2N3-O4P5-Q6R7",
            "cas_nummern": "",
            "gefahrenklassen": [],
            "verwendungskategorie": "Test",
            "pcnStatus": "entwurf",
        },
        headers={**AUTH_HEADERS, "X-Tenant-ID": tid},
    )
    assert response.status_code == 201
    assert response.json()["tenant_id"] == tid
    mid = response.json()["meldung_id"]
    m = db.get(PCNMeldung, mid)
    if m:
        assert m.tenant_id == tid
        db.delete(m)
        db.commit()


def test_pcn_meldungen_roundtrip_list_contains_created(db):
    _require_pcn_table(db)
    create = client.post(
        "/api/v1/compliance/pcn-meldungen",
        json={
            "produktname": "Roundtrip-Produkt",
            "ufi": "Z9Y8-X7W6-V5U4-T3S2",
            "cas_nummern": "",
            "gefahrenklassen": [],
            "verwendungskategorie": "Test",
            "pcnStatus": "entwurf",
        },
        headers=AUTH_HEADERS,
    )
    assert create.status_code == 201
    mid = create.json()["meldung_id"]

    listed = client.get("/api/v1/compliance/pcn-meldungen?limit=200", headers=AUTH_HEADERS)
    assert listed.status_code == 200
    ids = {m["meldung_id"] for m in listed.json()["items"]}
    assert mid in ids

    m = db.get(PCNMeldung, mid)
    if m:
        db.delete(m)
        db.commit()
