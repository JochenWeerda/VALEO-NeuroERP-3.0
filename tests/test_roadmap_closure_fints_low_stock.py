from __future__ import annotations

from decimal import Decimal

from fastapi.testclient import TestClient

from main import app
from app.services.fints_connector import (
    bestaetige_tan,
    get_tan_medien,
    initiiere_ueberweisung_mit_tan,
)
from app.workers.low_stock_agent import LowStockEvent, berechne_empfohlene_menge


AUTH = {
    "Authorization": "Bearer dev-token",
    "X-Tenant-ID": "test-tenant",
}


def test_fints_tan_simulator_challenge_and_confirm() -> None:
    result, challenge = initiiere_ueberweisung_mit_tan(
        auftraggeber_iban="DE89370400440532013000",
        empfaenger_iban="DE27200400600572005900",
        empfaenger_name="Test GmbH",
        betrag=Decimal("100.00"),
        verwendungszweck="Roadmap Closure Test",
    )

    assert result.erfolg is True
    assert challenge is not None
    assert challenge.session_token
    assert challenge.tan_verfahren == "pushTAN"

    confirm = bestaetige_tan(challenge.session_token, "000000")
    assert confirm.erfolg is True
    assert confirm.rohdaten["schritt"] == "abgeschlossen"


def test_fints_tan_medien_simulator() -> None:
    result = get_tan_medien()

    assert result.erfolg is True
    assert result.rohdaten is not None
    assert result.rohdaten["mode"] == "simulator"
    assert {m["tan_verfahren"] for m in result.rohdaten["tan_medien"]} == {"chipTAN", "pushTAN"}


def test_fints_routes_are_mounted_under_single_banken_prefix() -> None:
    client = TestClient(app, raise_server_exceptions=False)

    media = client.get("/api/v1/banken/fints/tan-medien", headers=AUTH)
    assert media.status_code == 200
    assert media.json()["erfolg"] is True

    accounts = client.get("/api/v1/banken/fints/konten", headers=AUTH)
    assert accounts.status_code == 200
    assert accounts.json()["konten"]

    duplicate = client.get("/api/v1/banken/banken/fints/konten", headers=AUTH)
    assert duplicate.status_code == 404


def test_low_stock_eoq_respects_gap_and_safety_cap() -> None:
    event = LowStockEvent(
        tenant_id="test-tenant",
        artikel_id="ART-1",
        artikel_name="Weizen Saatgut",
        bestand=2,
        mindestbestand=10,
        durchschnittlicher_verbrauch_pro_tag=20,
    )

    menge = berechne_empfohlene_menge(event)
    assert menge >= 8
    assert menge <= 50


def test_low_stock_agent_routes() -> None:
    client = TestClient(app, raise_server_exceptions=False)

    status = client.get("/api/v1/agents/low-stock/status", headers=AUTH)
    assert status.status_code == 200
    assert status.json()["subject"] == "erp.lager.bestand_unterschritten"

    simulate = client.post(
        "/api/v1/agents/low-stock/simulate",
        headers=AUTH,
        json={
            "tenant_id": "test-tenant",
            "artikel_id": "ART-1",
            "artikel_name": "Saatgut",
            "bestand": 2,
            "mindestbestand": 10,
            "durchschnittlicher_verbrauch_pro_tag": 5,
        },
    )
    assert simulate.status_code == 200
    assert simulate.json()["erfolg"] is True
    assert simulate.json()["empfohlene_menge"] >= 8
