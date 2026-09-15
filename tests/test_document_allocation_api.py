"""FSX-MENGENMODELL — die Endpunkte, gegen die echte Datenbank.

Geprueft wird der Weg, den die Maske geht: zuordnen, Stand lesen, loesen. Die
Auskunft, auf die es ankommt, ist eine einzige Zeile je Position —
"100 dt geliefert · 60 dt berechnet · 40 dt offen".

Ohne erreichbare Datenbank wird uebersprungen, nicht als gruen gewertet.
"""

from __future__ import annotations

import os
import uuid
from decimal import Decimal

import pytest

pytestmark = pytest.mark.integration

DB_URL = os.environ.get(
    "DATABASE_URL", "postgresql://valeo_dev:valeo_dev_2024@127.0.0.1:5432/valeo_neuro_erp"
)
os.environ.setdefault("DATABASE_URL", DB_URL)
os.environ.setdefault("API_DEV_TOKEN", "dev-token")


@pytest.fixture(scope="module")
def client():
    from sqlalchemy import create_engine, text

    try:
        with create_engine(DB_URL).connect() as conn:
            vorhanden = conn.execute(
                text("SELECT to_regclass('domain_docs.doc_allocation_sources')")
            ).scalar()
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank nicht erreichbar: {fehler}")
    if not vorhanden:
        pytest.skip("Migration doc_allocations_20260915 nicht angewandt")

    from fastapi.testclient import TestClient

    from app.main import app

    return TestClient(app)


@pytest.fixture()
def mandant() -> str:
    return f"test-{uuid.uuid4().hex[:8]}"


@pytest.fixture()
def kopf(mandant: str) -> dict[str, str]:
    return {
        "Authorization": "Bearer dev-token",
        "X-Tenant-ID": mandant,
        "X-Tenant-Id": mandant,
    }


@pytest.fixture()
def quelle(mandant: str):
    """Eine Lieferposition mit 100 dt registrieren und hinterher aufraeumen."""
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker

    from app.services.document_allocation_service import (
        DocumentAllocationService,
        PositionRef,
    )

    engine = create_engine(DB_URL)
    sitzung = sessionmaker(bind=engine)()
    dienst = DocumentAllocationService(sitzung, mandant)
    ref = PositionRef("delivery_note", f"LS-{uuid.uuid4().hex[:6]}", "1")
    dienst.register_source(ref, Decimal(100), "dt", article_id="ART-WEIZEN")
    sitzung.commit()
    try:
        yield ref
    finally:
        sitzung.execute(
            text("DELETE FROM domain_docs.doc_allocation_sources WHERE tenant_id = :t"),
            {"t": mandant},
        )
        sitzung.commit()
        sitzung.close()


BASIS = "/api/v1/docflow"


def test_stand_zeigt_geliefert_berechnet_offen(client, kopf, quelle) -> None:
    antwort = client.post(
        f"{BASIS}/allocations",
        headers=kopf,
        json={
            "source_document_type": quelle.document_type,
            "source_document_id": quelle.document_id,
            "source_line_id": quelle.line_id,
            "target_document_type": "sales_invoice",
            "target_document_id": "RE-X",
            "target_line_id": "1",
            "quantity": "60",
            "unit": "dt",
            "reason": "teilrechnung",
        },
    )
    assert antwort.status_code == 201, antwort.text
    assert antwort.json()["open_quantity"] == "40"
    assert antwort.json()["status"] == "teilweise"

    stand = client.get(
        f"{BASIS}/documents/{quelle.document_type}/{quelle.document_id}/allocations",
        headers=kopf,
    )
    assert stand.status_code == 200
    zeile = stand.json()["lines"][0]
    # Genau die drei Zahlen, die an der Position stehen sollen.
    assert zeile["quantity"] == "100"
    assert zeile["allocated_quantity"] == "60"
    assert zeile["open_quantity"] == "40"
    assert zeile["unit"] == "dt"
    assert len(zeile["allocations"]) == 1


def test_ueberbuchung_liefert_409_mit_offener_menge(client, kopf, quelle) -> None:
    def zuordnen(menge: str, ziel: str):
        return client.post(
            f"{BASIS}/allocations",
            headers=kopf,
            json={
                "source_document_type": quelle.document_type,
                "source_document_id": quelle.document_id,
                "source_line_id": quelle.line_id,
                "target_document_type": "sales_invoice",
                "target_document_id": ziel,
                "target_line_id": "1",
                "quantity": menge,
                "unit": "dt",
            },
        )

    assert zuordnen("60", "RE-X").status_code == 201
    zu_viel = zuordnen("50", "RE-Y")
    assert zu_viel.status_code == 409
    # Die Meldung nennt die offene Menge, statt den Anwender raten zu lassen.
    assert "40" in zu_viel.json()["detail"]


def test_nicht_umrechenbare_einheit_liefert_422(client, kopf, quelle) -> None:
    antwort = client.post(
        f"{BASIS}/allocations",
        headers=kopf,
        json={
            "source_document_type": quelle.document_type,
            "source_document_id": quelle.document_id,
            "source_line_id": quelle.line_id,
            "target_document_type": "sales_invoice",
            "target_document_id": "RE-X",
            "target_line_id": "1",
            "quantity": "10",
            "unit": "l",
        },
    )
    assert antwort.status_code == 422
    assert "umrechnen" in antwort.json()["detail"]


def test_eingabe_bleibt_neben_der_umgerechneten_menge_erhalten(client, kopf, quelle) -> None:
    client.post(
        f"{BASIS}/allocations",
        headers=kopf,
        json={
            "source_document_type": quelle.document_type,
            "source_document_id": quelle.document_id,
            "source_line_id": quelle.line_id,
            "target_document_type": "sales_invoice",
            "target_document_id": "RE-X",
            "target_line_id": "1",
            "quantity": "2000",
            "unit": "kg",
        },
    )
    zeile = client.get(
        f"{BASIS}/documents/{quelle.document_type}/{quelle.document_id}/allocations",
        headers=kopf,
    ).json()["lines"][0]

    zuordnung = zeile["allocations"][0]
    assert zuordnung["quantity"] == "20"  # gerechnet wird in dt
    assert zuordnung["entered_quantity"] == "2000"  # eingegeben wurde in kg
    assert zuordnung["entered_unit"] == "kg"


def test_gutschrift_gibt_die_menge_nur_auf_ansage_frei(client, kopf, quelle) -> None:
    angelegt = client.post(
        f"{BASIS}/allocations",
        headers=kopf,
        json={
            "source_document_type": quelle.document_type,
            "source_document_id": quelle.document_id,
            "source_line_id": quelle.line_id,
            "target_document_type": "sales_invoice",
            "target_document_id": "RE-X",
            "target_line_id": "1",
            "quantity": "60",
            "unit": "dt",
        },
    ).json()

    # Preisnachlass: die Ware bleibt beim Kunden, die Menge bleibt berechnet.
    nachlass = client.post(
        f"{BASIS}/allocations/{angelegt['allocation_id']}/release",
        headers=kopf,
        json={"frees_quantity": False},
    )
    assert nachlass.status_code == 200
    assert nachlass.json()["open_quantity"] == "40"
    assert nachlass.json()["freed"] is False


def test_freigabe_ohne_angabe_wird_abgewiesen(client, kopf, quelle) -> None:
    """Kein Vorgabewert: Wer nichts sagt, bekommt keine stille Entscheidung."""
    antwort = client.post(
        f"{BASIS}/allocations/irgendeine-id/release", headers=kopf, json={}
    )
    assert antwort.status_code == 422


def test_beleg_ohne_zuordnungen_meldet_leer_statt_fehler(client, kopf) -> None:
    antwort = client.get(
        f"{BASIS}/documents/delivery_note/GIBTESNICHT/allocations", headers=kopf
    )
    assert antwort.status_code == 200
    assert antwort.json()["lines"] == []
