from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints.personal import build_hrm_operations_gates, router


_HEADERS = {"Authorization": "Bearer dev-token", "X-Tenant-ID": "tenant-hrm"}
_APP = FastAPI()
_APP.include_router(router, prefix="/api/v1")


def _gate(data: dict, gate_id: str) -> dict:
    return next(item for item in data["gates"] if item["id"] == gate_id)


def test_hrm_operations_gates_builder_defines_professional_go_live_blockers():
    gates = build_hrm_operations_gates()

    assert gates.status == "external_gates_defined"
    assert gates.goLiveAllowed is False
    assert len(gates.gates) == 7
    assert all(gate.goLiveBlocking for gate in gates.gates)
    assert all(gate.evidenceRequired for gate in gates.gates)
    assert all(gate.acceptanceCriteria for gate in gates.gates)
    assert all(gate.auditTrail for gate in gates.gates)
    assert "Go-live ist nur erlaubt, wenn alle blocking Gates approved sind." in gates.closureDefinition


def test_hrm_operations_gates_endpoint_covers_external_integrations_and_legal_evidence():
    response = TestClient(_APP, raise_server_exceptions=False).get(
        "/api/v1/personal/hrm-operations-gates",
        headers=_HEADERS,
    )

    assert response.status_code == 200
    data = response.json()

    eau = _gate(data, "eau-communication")
    assert "keine Diagnosedaten" in " ".join(eau["evidenceRequired"] + eau["professionalPractice"])

    datev = _gate(data, "datev-payroll")
    assert "DATEV" in datev["title"]
    assert "Testexport" in " ".join(datev["evidenceRequired"])

    office = _gate(data, "office-sso-connectors")
    assert "Least-Privilege-Scopes" in office["professionalPractice"]
    assert "Busy-only Datenschutz" in office["professionalPractice"]

    privacy = _gate(data, "privacy-contracts")
    assert "AVV/DPA" in " ".join(privacy["evidenceRequired"])
    assert "Subprozessoren" in " ".join(privacy["evidenceRequired"])


def test_hrm_operations_gates_endpoint_covers_betriebsrat_dsfa_ai_and_retention():
    data = TestClient(_APP, raise_server_exceptions=False).get(
        "/api/v1/personal/hrm-operations-gates",
        headers=_HEADERS,
    ).json()

    works_council = _gate(data, "works-council-dsfa")
    assert "Betriebsvereinbarung" in " ".join(works_council["evidenceRequired"])
    assert "DSFA" in " ".join(works_council["evidenceRequired"])
    assert "KI-Assistenz erstellt nur Vorschlaege oder Zusammenfassungen mit menschlicher Freigabe" in works_council["acceptanceCriteria"]

    documents = _gate(data, "documents-esign")
    assert "LibreOffice-Rendering" in documents["title"]
    assert "E-Signatur" in documents["title"]
    assert "Signaturstatus" in documents["professionalPractice"]

    retention = _gate(data, "retention-legal")
    assert "Aufbewahrungsfristen" in " ".join(retention["evidenceRequired"])
    assert "Zweckbindung" in retention["professionalPractice"]
