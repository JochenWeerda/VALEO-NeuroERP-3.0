from __future__ import annotations

from decimal import Decimal

from app.services.lohn_service import PayrollEmployeeInput, berechne_netto, build_payroll_closeout


_HEADERS = {"Authorization": "Bearer dev-token", "X-Tenant-ID": "tenant-payroll-deep"}


def test_lohn_service_calculates_employee_and_employer_side_for_2026():
    result = berechne_netto(
        4000,
        1,
        hat_kinder=True,
        kirchensteuersatz=0.09,
        zusatzbeitrag_kv=0.029,
        year=2026,
    )

    assert result.parameter_version == "DE-PAYROLL-2026-PREVIEW-1"
    assert result.employee_social.total > Decimal("0")
    assert result.employer_social.total > Decimal("0")
    assert result.netto < result.brutto
    assert result.employer_total_cost == result.brutto + result.employer_social.total
    assert "BMF_PAP_CERTIFIED_CALCULATION" in result.external_gates


def test_payroll_closeout_builds_balanced_fibu_and_datev_handoff():
    closeout = build_payroll_closeout(
        "2026-06",
        [
            PayrollEmployeeInput(
                employee_ref="emp-1",
                personnel_number="PN-1",
                gross=Decimal("4000.00"),
                tax_class=1,
                has_children=True,
                cost_center="HR",
            )
        ],
    )

    body = closeout.as_dict()
    line = body["lines"][0]
    entries = line["journalEntries"]
    debit = sum(Decimal(str(row["amount"])) for row in entries if row["side"] == "debit")
    credit = sum(Decimal(str(row["amount"])) for row in entries if row["side"] == "credit")

    assert body["status"] == "ready_for_external_approval"
    assert body["parameterVersion"] == "DE-PAYROLL-2026-PREVIEW-1"
    assert debit == credit
    assert {row["lohnart"] for row in line["datevAsciiRows"]} >= {"1000", "9010", "9020", "9030"}
    assert line["datevAsciiRows"][0]["personalnummer"] == "PN-1"
    assert "DATEV_TARGET_FORMAT_APPROVED" in body["externalGates"]


def test_lohn_berechnung_endpoint_uses_payroll_response_model():
    from fastapi.testclient import TestClient

    from app.core.database import get_db
    from main import app

    def override_db():
        yield object()

    app.dependency_overrides[get_db] = override_db
    try:
        client = TestClient(app, raise_server_exceptions=False)
        response = client.post(
            "/api/v1/personal/lohn/berechnung",
            headers=_HEADERS,
            json={"brutto": 4000, "steuerklasse": 1, "hat_kinder": True, "jahr": 2026},
        )
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 200
    body = response.json()
    assert body["ergebnis"]["parameter_version"] == "DE-PAYROLL-2026-PREVIEW-1"
    assert "employee_social" in body["ergebnis"]
    assert "id" not in body


def test_closeout_preview_endpoint_returns_datev_and_fibu_contract():
    from fastapi.testclient import TestClient

    from app.core.database import get_db
    from main import app

    def override_db():
        yield object()

    app.dependency_overrides[get_db] = override_db
    try:
        client = TestClient(app, raise_server_exceptions=False)
        response = client.post(
            "/api/v1/personal/lohn/closeout-preview",
            headers=_HEADERS,
            json={
                "period": "2026-06",
                "employees": [
                    {
                        "employeeRef": "emp-1",
                        "personnelNumber": "PN-1",
                        "gross": 4000,
                        "taxClass": 1,
                        "hasChildren": True,
                        "costCenter": "HR",
                    }
                ],
            },
        )
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ready_for_external_approval"
    assert body["totals"]["gross"] == 4000.0
    assert body["lines"][0]["datevAsciiRows"]
    assert body["lines"][0]["journalEntries"]
