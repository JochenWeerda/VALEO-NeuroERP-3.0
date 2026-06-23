"""Tests fuer EXTERNAL-MOCK-HARNESS-001."""

import pytest
from app.services.external_mock_harness_service import ExternalMockHarnessService


@pytest.fixture()
def svc() -> ExternalMockHarnessService:
    return ExternalMockHarnessService()


def test_datev_export_start_simulated(svc: ExternalMockHarnessService) -> None:
    result = svc.datev_export_start("12345", "2026-01-01", "2026-01-31")
    assert result["simulated"] is True
    assert result["system"] == "datev"
    assert result["status"] == "queued"
    assert "job_id" in result
    assert result["job_id"].startswith("SIM-DATEV-")


def test_datev_export_start_deterministic(svc: ExternalMockHarnessService) -> None:
    r1 = svc.datev_export_start("12345", "2026-01-01", "2026-01-31")
    r2 = svc.datev_export_start("12345", "2026-01-01", "2026-01-31")
    assert r1["job_id"] == r2["job_id"]


def test_datev_export_status(svc: ExternalMockHarnessService) -> None:
    result = svc.datev_export_status("SIM-DATEV-ABCDEF012345")
    assert result["simulated"] is True
    assert result["status"] == "completed"


def test_tse_sign_transaction(svc: ExternalMockHarnessService) -> None:
    result = svc.tse_sign_transaction("KASSE-01", "BON-00123", 4999)
    assert result["simulated"] is True
    assert result["signatur"].startswith("SIM-TSE-")
    assert isinstance(result["transaktions_nr"], int)


def test_tse_sign_deterministic(svc: ExternalMockHarnessService) -> None:
    r1 = svc.tse_sign_transaction("KASSE-01", "BON-00123", 4999)
    r2 = svc.tse_sign_transaction("KASSE-01", "BON-00123", 4999)
    assert r1["signatur"] == r2["signatur"]
    assert r1["transaktions_nr"] == r2["transaktions_nr"]


def test_dsfinvk_export(svc: ExternalMockHarnessService) -> None:
    result = svc.dsfinvk_export("KASSE-01", "2026-06-23")
    assert result["simulated"] is True
    assert "transactions.csv" in result["dateien"]


def test_elster_submit(svc: ExternalMockHarnessService) -> None:
    result = svc.elster_submit("123/456/78901", "UStVA", "2026-05", {"umsatz": 10000})
    assert result["simulated"] is True
    assert result["status"] == "angenommen"
    assert result["rueckgabe_code"] == "0"


def test_elster_status(svc: ExternalMockHarnessService) -> None:
    result = svc.elster_status("SIM-ELSTER-ABCDEF")
    assert result["simulated"] is True
    assert result["status"] == "bestaetigt"


def test_dms_upload(svc: ExternalMockHarnessService) -> None:
    result = svc.dms_upload("Rechnung 2026-001", "eingangsrechnung", "")
    assert result["simulated"] is True
    assert result["status"] == "archiviert"
    assert result["dokument_id"].startswith("SIM-DMS-")


def test_dms_search(svc: ExternalMockHarnessService) -> None:
    result = svc.dms_search("Rechnung")
    assert result["simulated"] is True
    assert len(result["treffer"]) == 2


def test_bank_camt_import(svc: ExternalMockHarnessService) -> None:
    result = svc.bank_camt_import("DE89370400440532013000", 1)
    assert result["simulated"] is True
    assert len(result["buchungen"]) == 1
    assert result["buchungen"][0]["betrag_eur"] == 1234.56


def test_systems_overview(svc: ExternalMockHarnessService) -> None:
    result = svc.systems_overview()
    assert result["simulated"] is True
    system_names = [s["system"] for s in result["systems"]]
    assert "datev" in system_names
    assert "tse" in system_names
    assert "elster" in system_names
    assert "dms" in system_names
    assert "bank_camt" in system_names


def test_all_results_have_hinweis(svc: ExternalMockHarnessService) -> None:
    results = [
        svc.datev_export_start("1", "2026-01-01", "2026-01-31"),
        svc.tse_sign_transaction("K1", "B1", 100),
        svc.dsfinvk_export("K1", "2026-06-01"),
        svc.elster_submit("1", "UStVA", "2026-01", {}),
        svc.dms_upload("Test", "typ", ""),
        svc.bank_camt_import("DE00000000000000000000", 1),
    ]
    for r in results:
        assert "hinweis" in r, f"Kein Hinweis in {r.get('system')} {r.get('action')}"
