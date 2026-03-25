from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


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
