from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints.personal import build_hrm_readiness, router


_HEADERS = {"Authorization": "Bearer dev-token", "X-Tenant-ID": "tenant-hrm"}
_APP = FastAPI()
_APP.include_router(router, prefix="/api/v1")


def _capability(data: dict, capability_id: str) -> dict:
    return next(item for item in data["capabilities"] if item["id"] == capability_id)


def _integration(data: dict, integration_id: str) -> dict:
    return next(item for item in data["integrations"] if item["id"] == integration_id)


def test_hrm_readiness_builder_covers_german_minimum_checklist():
    readiness = build_hrm_readiness()

    assert readiness.country == "DE"
    assert len(readiness.minimumChecklist) == 15
    assert "Digitale Personalakte" in readiness.minimumChecklist
    assert "eAU-Prozess" in readiness.minimumChecklist
    assert "Payroll-/DATEV-Schnittstelle" in readiness.minimumChecklist
    assert "Sichere KI-Funktionen mit menschlicher Kontrolle" in readiness.minimumChecklist


def test_hrm_readiness_endpoint_exposes_compliance_and_gap_contract():
    client = TestClient(_APP, raise_server_exceptions=False)
    response = client.get("/api/v1/personal/hrm-readiness", headers=_HEADERS)

    assert response.status_code == 200
    data = response.json()

    personnel_file = _capability(data, "hrm-personnel-file")
    assert personnel_file["status"] == "contract_complete"
    assert "BDSG §26" in personnel_file["legalBasis"]
    assert "HRM-AKTE-001" in personnel_file["nextSlices"]

    time_absence = _capability(data, "hrm-time-absence")
    assert time_absence["status"] == "implemented"
    assert "BAG 1 ABR 22/21" in time_absence["legalBasis"]

    eau = _capability(data, "hrm-eau")
    assert eau["priority"] == "P0"
    assert "SGB IV §109" in eau["legalBasis"]
    assert "HRM-EAU-001" in eau["nextSlices"]


def test_hrm_readiness_exposes_office_payroll_and_ai_controls():
    client = TestClient(_APP, raise_server_exceptions=False)
    data = client.get("/api/v1/personal/hrm-readiness", headers=_HEADERS).json()

    assert _integration(data, "microsoft-365")["nextSlice"] == "HRM-M365-001"
    assert _integration(data, "google-workspace")["nextSlice"] == "HRM-GOOGLE-001"
    assert _integration(data, "libreoffice")["nextSlice"] == "HRM-LIBREOFFICE-001"
    assert "Lohnarten" in _integration(data, "datev-payroll")["minimumContract"]

    ai_high_risk = next(item for item in data["aiControls"] if item["id"] == "hrm-ai-high-risk")
    assert "high-risk" in ai_high_risk["classification"]
    assert "Blackbox-CV-Sorting" in ai_high_risk["prohibitedUse"]
    assert "menschliche Aufsicht" in " ".join(ai_high_risk["requiredControls"])

    ai_assist = next(item for item in data["aiControls"] if item["id"] == "hrm-ai-assist")
    assert "nicht freigegebene KI-Funktionen" in ai_assist["prohibitedUse"]
