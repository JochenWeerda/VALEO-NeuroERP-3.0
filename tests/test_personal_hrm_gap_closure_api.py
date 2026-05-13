from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints.personal import build_hrm_operating_system_contract, router
from app.services.personal_service import PersonalService


_HEADERS = {"Authorization": "Bearer dev-token", "X-Tenant-ID": "tenant-hrm"}
_APP = FastAPI()
_APP.include_router(router, prefix="/api/v1")


def _module(data: dict, module_id: str) -> dict:
    return next(item for item in data["modules"] if item["id"] == module_id)


def test_hrm_operating_system_closes_all_repo_plan_gaps():
    contract = build_hrm_operating_system_contract()

    assert contract.status == "repo_contract_complete"
    assert set(contract.closedRepoGaps) >= {
        "HRM-EAU-001",
        "HRM-DATEV-001",
        "HRM-CONTRACTS-001",
        "HRM-ESS-001",
        "HRM-MSS-001",
        "HRM-RECRUITING-001",
        "HRM-ANALYTICS-001",
        "HRM-AI-GOV-001",
        "HRM-M365-001",
        "HRM-GOOGLE-001",
        "HRM-LIBREOFFICE-001",
    }
    assert "Keine neue time_bookings- oder absences-Tabelle fuer HR-Time." in contract.timeEntryModelRules
    assert "Datumsspalte ist entry_date; Stundenfeld ist hours." in contract.timeEntryModelRules


def test_personal_service_uses_canonical_time_entries_model():
    service_source = "\n".join(
        str(value)
        for value in (
            PersonalService._TIME_ENTRY_COLS,
            PersonalService.list_zeiteintraege.__code__.co_consts,
            PersonalService.create_zeiteintrag.__code__.co_consts,
            PersonalService.list_abwesenheiten.__code__.co_consts,
            PersonalService.import_abwesenheit.__code__.co_consts,
        )
    )

    assert "domain_hr.time_entries" in service_source
    assert "entry_date" in service_source
    assert "hours" in service_source
    assert "RETURNING" in service_source
    assert "time_bookings" not in service_source
    assert "work_date" not in service_source


def test_hrm_operating_system_endpoint_exposes_eau_without_diagnosis_and_datev_closeout():
    response = TestClient(_APP, raise_server_exceptions=False).get(
        "/api/v1/personal/hrm-operating-system",
        headers=_HEADERS,
    )

    assert response.status_code == 200
    data = response.json()
    eau = _module(data, "eau")
    assert eau["status"] == "contract_complete"
    assert "keine Diagnosedaten" in eau["controls"]
    assert "Krankenkassenstatus" in eau["controls"]

    payroll = _module(data, "payroll-datev")
    assert "Lohnarten" in payroll["controls"]
    assert "Monatsabschlussprotokoll" in payroll["controls"]
    assert "DATEV-Zielformat" in " ".join(payroll["externalGates"])


def test_hrm_operating_system_endpoint_exposes_self_service_recruiting_analytics_ai_and_office():
    data = TestClient(_APP, raise_server_exceptions=False).get(
        "/api/v1/personal/hrm-operating-system",
        headers=_HEADERS,
    ).json()

    self_service = _module(data, "self-service")
    assert "Rollenfilter" in self_service["controls"]
    assert "Freigabequeue" in self_service["controls"]

    recruiting = _module(data, "recruiting-development")
    assert "Bewerber-Retention" in recruiting["controls"]
    assert "Human-in-the-loop" in recruiting["controls"]

    analytics = _module(data, "analytics-privacy")
    assert "Aggregationsschwellen" in analytics["controls"]
    assert "keine Einzel-Leistungsueberwachung" in analytics["controls"]

    ai = _module(data, "ai-governance")
    assert "Human-Gate" in ai["controls"]
    assert "Verbot Emotionserkennung" in ai["controls"]

    office = _module(data, "office-connectors")
    assert "OAuth-Scopes" in office["controls"]
    assert "Busy-only Datenschutz" in office["controls"]
    assert "produktive Tenant-Secrets" in " ".join(office["externalGates"])
