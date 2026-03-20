from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints import process_kernel_api
from app.core.action_execution import ActionExecutionResult, ActionExecutionStatus
from app.core.action_idempotency import get_action_idempotency_store


def _client() -> TestClient:
    app = FastAPI()
    app.include_router(process_kernel_api.router)
    return TestClient(app)


def test_idempotency_overview_surfaces_catalog_and_store_snapshot():
    client = _client()
    store = get_action_idempotency_store()
    store.clear()
    store.remember(
        tenant_id="tenant-1",
        idempotency_key="idem-1",
        request_fingerprint="fp-1",
        result=ActionExecutionResult(
            execution_id="exec-1",
            command_id="cmd-1",
            command_name="FinalizeAgrarSettlement",
            aggregate_type="agrar_settlement",
            aggregate_id="SET-1",
            aggregate_owner="agrar",
            idempotency_key="idem-1",
            status=ActionExecutionStatus.ACCEPTED,
        ),
    )

    response = client.get("/process/actions/idempotency/overview")

    assert response.status_code == 200
    body = response.json()
    assert body["schema_version"] == 1
    assert body["catalog"]["total_commands"] >= 1
    assert body["catalog"]["idempotent_commands"] >= 1
    assert body["store"]["total_records"] == 1
    assert body["store"]["commands"] == ["FinalizeAgrarSettlement"]
    assert body["confidence_score"] >= 1
    store.clear()


def test_supply_chain_eta_alarm_endpoint_returns_alarm_for_late_delivery():
    client = _client()

    response = client.post(
        "/process/supply-chain/eta/alarm",
        json={
            "lieferung_id": "L-ETA-1",
            "transport_modus": "LKW",
            "ursprungsort": "Hamburg",
            "zielort": "Bremen",
            "geplante_abfahrt": "2026-03-19T08:00:00",
            "distanz_km": 300,
            "ziel_ankunft": "2026-03-19T10:00:00",
            "zwischenstopps": 1,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["lieferung_id"] == "L-ETA-1"
    assert body["alarm_ausgeloest"] is True
    assert body["alarm"] is not None
    assert body["alarm"]["lieferung_id"] == "L-ETA-1"
    assert body["abweichung_stunden"] > 0


def test_dms_extract_builds_structured_kernfluss_for_invoice():
    client = _client()

    response = client.post(
        "/process/dms/extract",
        json={
            "dokument_id": "DOC-INV-1",
            "volltext": (
                "Rechnungsnummer: RE-2026-0001\n"
                "Datum: 19.03.2026\n"
                "Gesamtbetrag: 1.234,56 EUR\n"
                "IBAN: DE02120300000000202051\n"
                "Lieferant: Muster Agrar GmbH\n"
            ),
            "dokument_typ": "EINGANGSRECHNUNG",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["dokument_id"] == "DOC-INV-1"
    assert body["klassifikation"]["erkannter_typ"] == "EINGANGSRECHNUNG"
    assert body["ocr_ergebnis"]["dokument_typ"] == "EINGANGSRECHNUNG"
    assert "finance.ap_invoices" in body["zielprozesse"]
    assert "journal_entries.posting_candidate" in body["zielprozesse"]
    assert body["import_format"] == "ocr_pdf"
    assert isinstance(body["manuelle_pruefung_erforderlich"], bool)
