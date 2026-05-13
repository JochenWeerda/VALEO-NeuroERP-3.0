from __future__ import annotations

from typing import Any

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints.personal import router
from app.core.database import get_db


_HEADERS = {"Authorization": "Bearer dev-token", "X-Tenant-ID": "tenant-hrm"}
_APP = FastAPI()
_APP.include_router(router, prefix="/api/v1")


class _Result:
    def __init__(self, rows: list[dict[str, Any]]):
        self._rows = rows

    def mappings(self) -> "_Result":
        return self

    def all(self) -> list[dict[str, Any]]:
        return self._rows


class _EmployeeFileSession:
    def __init__(self, rows: list[dict[str, Any]] | None = None):
        self.rows = rows or []
        self.statements: list[tuple[str, dict[str, Any]]] = []
        self.committed = False

    def execute(self, statement: Any, params: dict[str, Any]) -> _Result:
        self.statements.append((str(statement), params))
        if "SELECT id, employee_ref, document_type" in str(statement):
            return _Result(self.rows)
        return _Result([])

    def commit(self) -> None:
        self.committed = True


def _override_db(session: _EmployeeFileSession):
    def _inner():
        yield session

    return _inner


def test_employee_file_hr_role_sees_document_classes_and_all_documents():
    session = _EmployeeFileSession([
        {
            "id": "doc-contract",
            "employee_ref": "emp-1",
            "document_type": "employment_contract",
            "title": "Arbeitsvertrag",
            "visibility": "hr",
            "issued_at": "2024-01-01",
            "dms_document_id": "dms-1",
        },
        {
            "id": "doc-certificate",
            "employee_ref": "emp-1",
            "document_type": "certificate",
            "title": "Staplerschein",
            "visibility": "employee",
            "issued_at": "2025-01-01",
            "dms_document_id": "dms-2",
        },
        {
            "id": "doc-payroll",
            "employee_ref": "emp-1",
            "document_type": "payroll_document",
            "title": "Payroll-Stammdaten",
            "visibility": "payroll",
            "issued_at": "2025-02-01",
            "dms_document_id": "dms-3",
        },
    ])
    _APP.dependency_overrides[get_db] = _override_db(session)
    try:
        response = TestClient(_APP, raise_server_exceptions=False).get(
            "/api/v1/personal/employee-files/emp-1?actorRole=hr",
            headers=_HEADERS,
        )
    finally:
        _APP.dependency_overrides.pop(get_db, None)

    assert response.status_code == 200
    data = response.json()
    assert data["source"] == "database"
    assert data["hiddenDocumentCount"] == 0
    assert {item["documentType"] for item in data["documentClasses"]} >= {
        "employment_contract",
        "payroll_document",
        "certificate",
        "absence_evidence",
    }
    assert {item["id"] for item in data["documents"]} == {"doc-contract", "doc-certificate", "doc-payroll"}
    assert data["exportPackage"]["includesAuditTrail"] is True
    assert data["retention"]["reviewCadence"] == "jaehrlich und bei Austritt"


def test_employee_file_manager_role_filters_sensitive_documents():
    session = _EmployeeFileSession([
        {"id": "doc-contract", "employee_ref": "emp-1", "document_type": "employment_contract", "title": "Arbeitsvertrag", "visibility": "hr"},
        {"id": "doc-certificate", "employee_ref": "emp-1", "document_type": "certificate", "title": "Zertifikat", "visibility": "employee"},
        {"id": "doc-payroll", "employee_ref": "emp-1", "document_type": "payroll_document", "title": "Payroll", "visibility": "payroll"},
    ])
    _APP.dependency_overrides[get_db] = _override_db(session)
    try:
        response = TestClient(_APP, raise_server_exceptions=False).get(
            "/api/v1/personal/employee-files/emp-1?actorRole=manager",
            headers=_HEADERS,
        )
    finally:
        _APP.dependency_overrides.pop(get_db, None)

    assert response.status_code == 200
    data = response.json()
    assert data["hiddenDocumentCount"] == 2
    assert [item["id"] for item in data["documents"]] == ["doc-certificate"]
    assert data["documents"][0]["canEmployeeView"] is True


def test_employee_file_document_create_persists_metadata_contract():
    session = _EmployeeFileSession()
    _APP.dependency_overrides[get_db] = _override_db(session)
    try:
        response = TestClient(_APP, raise_server_exceptions=False).post(
            "/api/v1/personal/employee-files/emp-1/documents?actorRole=hr",
            headers=_HEADERS,
            json={
                "documentType": "privacy_acknowledgement",
                "title": "Datenschutzverpflichtung",
                "issuedAt": "2026-05-13",
                "dmsDocumentId": "dms-privacy-1",
                "visibility": "employee",
                "createdBy": "hr-admin",
            },
        )
    finally:
        _APP.dependency_overrides.pop(get_db, None)

    assert response.status_code == 201
    data = response.json()
    assert data["documentType"] == "privacy_acknowledgement"
    assert data["retentionUntil"] == "2032-05-13"
    assert "BDSG §26" in data["legalBasis"]
    assert session.committed is True
    insert_params = session.statements[-1][1]
    assert insert_params["tenant_id"] == "tenant-hrm"
    assert insert_params["employee_ref"] == "emp-1"
    assert insert_params["dms_document_id"] == "dms-privacy-1"


def test_employee_file_document_create_rejects_employee_role():
    response = TestClient(_APP, raise_server_exceptions=False).post(
        "/api/v1/personal/employee-files/emp-1/documents?actorRole=employee",
        headers=_HEADERS,
        json={"documentType": "certificate", "title": "Eigenes Dokument"},
    )

    assert response.status_code == 403
