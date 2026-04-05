from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from app.core.database import SessionLocal
from app.domains.operations.models import FlowSpineInstance, PCNMeldung
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


# ── PCN-Meldungen (Gap 104-C/D — DB-backed) ──────────────────────────────────

def test_pcn_meldung_create_valid(db):
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
