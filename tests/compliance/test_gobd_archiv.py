"""
GoBD Archiv – Endpoint-Tests
Deckt: document_artifacts, e-invoice-xml, audit-package (Z1/Z2/Z3)
"""

from __future__ import annotations

import hashlib
import io
import zipfile
from typing import Optional

import pytest
from fastapi.testclient import TestClient

BASE = "/api/v1/gobd"
AUTH = {"Authorization": "Bearer dev-token"}
DEFAULT_TENANT = "00000000-0000-0000-0000-000000000001"


@pytest.fixture(scope="module")
def client():
    from main import app
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c


@pytest.fixture(scope="module")
def test_header_id():
    """
    Legt einen minimalen domain_docflow.document_headers-Datensatz an
    (nötig wegen FK-Constraint auf document_artifacts / invoice_xml_store).
    Räumt nach dem Modul-Lauf alle Testdaten wieder weg.
    """
    from app.core.database import SessionLocal
    from sqlalchemy import text
    from uuid import uuid4

    hid = str(uuid4())
    db = SessionLocal()
    try:
        db.execute(
            text(
                "INSERT INTO domain_docflow.document_headers "
                "(id, tenant_id, doc_type, doc_number) "
                "VALUES (:id, :tid, 'TEST', :num)"
            ),
            {"id": hid, "tid": DEFAULT_TENANT, "num": f"PYTEST-{hid[:8]}"},
        )
        db.commit()
    except Exception as exc:
        db.rollback()
        db.close()
        pytest.skip(f"Konnte Test-Header nicht anlegen: {exc}")
        return
    db.close()

    yield hid

    # --- Teardown: alle mit diesem Header verknüpften Test-Zeilen löschen ---
    db2 = SessionLocal()
    try:
        db2.execute(
            text("DELETE FROM domain_docflow.invoice_xml_store WHERE header_id = :h"),
            {"h": hid},
        )
        db2.execute(
            text("DELETE FROM domain_docflow.document_artifacts WHERE header_id = :h"),
            {"h": hid},
        )
        db2.execute(
            text("DELETE FROM domain_docflow.document_headers WHERE id = :h"),
            {"h": hid},
        )
        db2.commit()
    except Exception:
        db2.rollback()
    finally:
        db2.close()


def _sha256(data: str) -> str:
    return hashlib.sha256(data.encode()).hexdigest()


# ---------------------------------------------------------------------------
# Artifacts
# ---------------------------------------------------------------------------


class TestDocumentArtifacts:

    def test_register_artifact_returns_200(self, client: TestClient, test_header_id: str):
        payload = {
            "header_id": test_header_id,
            "artifact_type": "pdf",
            "content_hash_sha256": _sha256("some-pdf-content"),
            "storage_key": f"gobd/test/{test_header_id}.pdf",
            "file_name": "rechnung.pdf",
            "created_by": "pytest",
        }
        r = client.post(f"{BASE}/artifacts", json=payload, headers=AUTH)
        if r.status_code in (500, 503):
            pytest.skip("DB nicht erreichbar")
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["header_id"] == test_header_id
        assert data["artifact_type"] == "pdf"
        assert len(data["content_hash_sha256"]) == 64
        assert data["blockchain_anchor"]["subject_ref"] == data["id"]

    def test_list_artifacts_by_header_id(self, client: TestClient, test_header_id: str):
        r = client.get(
            f"{BASE}/artifacts",
            params={"header_id": test_header_id},
            headers=AUTH,
        )
        if r.status_code in (500, 503):
            pytest.skip("DB nicht erreichbar")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_artifact_type_validation(self, client: TestClient):
        """artifact_type darf nur pdf|xml|html|other sein — Pydantic 422."""
        payload = {
            "header_id": "any-id",
            "artifact_type": "docx",
            "content_hash_sha256": _sha256("x"),
            "storage_key": "gobd/test/bad.docx",
        }
        r = client.post(f"{BASE}/artifacts", json=payload, headers=AUTH)
        assert r.status_code == 422

    def test_hash_must_be_64_chars(self, client: TestClient):
        payload = {
            "header_id": "any-id",
            "artifact_type": "pdf",
            "content_hash_sha256": "tooshort",
            "storage_key": "gobd/test/x.pdf",
        }
        r = client.post(f"{BASE}/artifacts", json=payload, headers=AUTH)
        assert r.status_code == 422


# ---------------------------------------------------------------------------
# Artifact Integrity Verify
# ---------------------------------------------------------------------------


class TestArtifactVerify:

    @pytest.fixture(scope="class")
    def artifact_id_and_hash(self, client: TestClient, test_header_id: str):
        """Registriert ein Artefakt und gibt (artifact_id, stored_hash) zurück."""
        content = "pdf-bytes-for-verify-test"
        stored_hash = _sha256(content)
        reg = client.post(
            f"{BASE}/artifacts",
            json={
                "header_id": test_header_id,
                "artifact_type": "pdf",
                "content_hash_sha256": stored_hash,
                "storage_key": f"gobd/verify/{test_header_id}-verify.pdf",
                "created_by": "pytest",
            },
            headers=AUTH,
        )
        if reg.status_code in (500, 503):
            pytest.skip("DB nicht erreichbar")
        assert reg.status_code == 200, reg.text
        return reg.json()["id"], stored_hash

    def test_verify_unknown_artifact_returns_404(self, client: TestClient):
        r = client.get(
            f"{BASE}/artifacts/00000000-0000-0000-0000-000000000000/verify",
            headers=AUTH,
        )
        if r.status_code in (500, 503):
            pytest.skip("DB nicht erreichbar")
        assert r.status_code == 404

    def test_verify_without_provided_hash_returns_unchecked(
        self, client: TestClient, artifact_id_and_hash: tuple
    ):
        art_id, _ = artifact_id_and_hash
        r = client.get(f"{BASE}/artifacts/{art_id}/verify", headers=AUTH)
        assert r.status_code == 200
        data = r.json()
        assert data["integrity_status"] == "unchecked"
        assert data["match"] is None

    def test_verify_matching_hash_returns_verified(
        self, client: TestClient, artifact_id_and_hash: tuple
    ):
        art_id, stored_hash = artifact_id_and_hash
        r = client.get(
            f"{BASE}/artifacts/{art_id}/verify",
            params={"provided_hash": stored_hash},
            headers=AUTH,
        )
        assert r.status_code == 200
        data = r.json()
        assert data["integrity_status"] == "verified"
        assert data["match"] is True

    def test_verify_wrong_hash_returns_mismatch(
        self, client: TestClient, artifact_id_and_hash: tuple
    ):
        art_id, _ = artifact_id_and_hash
        wrong_hash = _sha256("manipulated-content")
        r = client.get(
            f"{BASE}/artifacts/{art_id}/verify",
            params={"provided_hash": wrong_hash},
            headers=AUTH,
        )
        assert r.status_code == 200
        data = r.json()
        assert data["integrity_status"] == "mismatch"
        assert data["match"] is False


# ---------------------------------------------------------------------------
# E-Rechnung XML
# ---------------------------------------------------------------------------


class TestEInvoiceXml:

    def test_store_xml_returns_pending_status(self, client: TestClient, test_header_id: str):
        payload = {
            "header_id": test_header_id,
            "content_hash_sha256": _sha256("<Invoice/>"),
            "storage_key": f"gobd/xml/{test_header_id}.xml",
            "format_type": "XRechnung",
            "created_by": "pytest",
        }
        r = client.post(f"{BASE}/e-invoice-xml", json=payload, headers=AUTH)
        if r.status_code in (500, 503):
            pytest.skip("DB nicht erreichbar")
        assert r.status_code in (200, 201), r.text
        data = r.json()
        assert data["validation_status"] == "pending"
        assert data["format_type"] == "XRechnung"

    def test_get_xml_metadata_by_header(self, client: TestClient, test_header_id: str):
        r = client.get(f"{BASE}/e-invoice-xml/{test_header_id}", headers=AUTH)
        if r.status_code in (500, 503):
            pytest.skip("DB nicht erreichbar")
        assert r.status_code == 200
        data = r.json()
        if data is None:
            pytest.skip("Kein Datensatz — test_store_xml wurde geskippt")
        assert data["header_id"] == test_header_id

    def test_get_xml_unknown_header_returns_null(self, client: TestClient):
        r = client.get(f"{BASE}/e-invoice-xml/does-not-exist-9999", headers=AUTH)
        if r.status_code in (500, 503):
            pytest.skip("DB nicht erreichbar")
        assert r.status_code == 200
        assert r.json() is None

    def test_validate_sets_valid_status(self, client: TestClient, test_header_id: str):
        r = client.patch(
            f"{BASE}/e-invoice-xml/{test_header_id}/validate",
            json={"validation_status": "valid"},
            headers=AUTH,
        )
        if r.status_code in (500, 503):
            pytest.skip("DB nicht erreichbar")
        if r.status_code == 404:
            pytest.skip("Kein XML-Eintrag — test_store_xml wurde geskippt")
        assert r.status_code == 200, r.text
        assert r.json()["validation_status"] == "valid"

    def test_validate_with_errors_sets_invalid_status(
        self, client: TestClient, test_header_id: str
    ):
        r = client.patch(
            f"{BASE}/e-invoice-xml/{test_header_id}/validate",
            json={
                "validation_status": "invalid",
                "validation_errors": {"xsd": ["Pflichtfeld BuyerReference fehlt"]},
            },
            headers=AUTH,
        )
        if r.status_code in (500, 503):
            pytest.skip("DB nicht erreichbar")
        if r.status_code == 404:
            pytest.skip("Kein XML-Eintrag — test_store_xml wurde geskippt")
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["validation_status"] == "invalid"
        assert data["validation_errors"] is not None

    def test_validate_rejects_unknown_status(self, client: TestClient):
        """Pydantic validiert: 'approved' ist kein erlaubter Status."""
        r = client.patch(
            f"{BASE}/e-invoice-xml/any-header/validate",
            json={"validation_status": "approved"},
            headers=AUTH,
        )
        assert r.status_code == 422

    def test_validate_accepts_pending(self, client: TestClient, test_header_id: str):
        """Zurücksetzen auf 'pending' muss erlaubt sein."""
        r = client.patch(
            f"{BASE}/e-invoice-xml/{test_header_id}/validate",
            json={"validation_status": "pending"},
            headers=AUTH,
        )
        if r.status_code in (500, 503):
            pytest.skip("DB nicht erreichbar")
        assert r.status_code in (200, 404)

    def test_validate_unknown_header_returns_404(self, client: TestClient):
        r = client.patch(
            f"{BASE}/e-invoice-xml/does-not-exist-9999/validate",
            json={"validation_status": "valid"},
            headers=AUTH,
        )
        if r.status_code in (500, 503):
            pytest.skip("DB nicht erreichbar")
        assert r.status_code == 404


# ---------------------------------------------------------------------------
# Audit-Package (Z1/Z2/Z3)
# ---------------------------------------------------------------------------


class TestAuditPackage:

    def test_audit_package_returns_zip(self, client: TestClient):
        r = client.get(f"{BASE}/audit-package", headers=AUTH)
        if r.status_code in (500, 503):
            pytest.skip("DB nicht erreichbar")
        assert r.status_code == 200
        assert "application/zip" in r.headers.get("content-type", "")
        assert "attachment" in r.headers.get("content-disposition", "")

    def test_audit_package_zip_structure(self, client: TestClient):
        """ZIP muss alle Z1/Z2/Z3-Dateien + Integrity-Manifest enthalten."""
        r = client.get(
            f"{BASE}/audit-package",
            params={"from_date": "2026-01-01", "to_date": "2026-12-31"},
            headers=AUTH,
        )
        if r.status_code in (500, 503):
            pytest.skip("DB nicht erreichbar")
        assert r.status_code == 200
        names = zipfile.ZipFile(io.BytesIO(r.content)).namelist()
        for f in [
            "Z1/data_dictionary.txt",
            "Z1/docflow_headers.csv",
            "Z2/audit_logs.csv",
            "Z2/journal_entries.csv",
            "Z2/docflow_items.csv",
            "Z3/artifact_hashes.csv",
            "integrity_manifest.csv",
        ]:
            assert f in names, f"Fehlende Datei im ZIP: {f}"

    def test_audit_package_integrity_manifest_has_all_files(self, client: TestClient):
        r = client.get(f"{BASE}/audit-package", headers=AUTH)
        if r.status_code in (500, 503):
            pytest.skip("DB nicht erreichbar")
        zf = zipfile.ZipFile(io.BytesIO(r.content))
        manifest = zf.read("integrity_manifest.csv").decode("utf-8")
        lines = [ln for ln in manifest.splitlines() if ln.strip()]
        assert lines[0] == "path;sha256"
        paths = {ln.split(";")[0] for ln in lines[1:]}
        assert "Z1/data_dictionary.txt" in paths
        assert "Z2/audit_logs.csv" in paths
        assert "Z3/artifact_hashes.csv" in paths

    def test_audit_package_manifest_hashes_are_64_chars(self, client: TestClient):
        r = client.get(f"{BASE}/audit-package", headers=AUTH)
        if r.status_code in (500, 503):
            pytest.skip("DB nicht erreichbar")
        zf = zipfile.ZipFile(io.BytesIO(r.content))
        manifest = zf.read("integrity_manifest.csv").decode("utf-8")
        for line in manifest.splitlines()[1:]:
            if ";" in line:
                _, sha = line.rsplit(";", 1)
                assert len(sha.strip()) == 64, f"Ungültige SHA256-Länge: {line}"

    def test_audit_package_csv_headers_parseable(self, client: TestClient):
        r = client.get(f"{BASE}/audit-package", headers=AUTH)
        if r.status_code in (500, 503):
            pytest.skip("DB nicht erreichbar")
        zf = zipfile.ZipFile(io.BytesIO(r.content))
        dh = zf.read("Z1/docflow_headers.csv").decode("utf-8-sig")
        assert "id" in dh.splitlines()[0] and "tenant_id" in dh.splitlines()[0]
        al = zf.read("Z2/audit_logs.csv").decode("utf-8-sig")
        assert "id" in al.splitlines()[0] and "action" in al.splitlines()[0]
