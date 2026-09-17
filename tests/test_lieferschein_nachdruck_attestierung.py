"""Ein gebuchter Lieferschein wird nur mit Begruendung nachgedruckt — und die
Begruendung bleibt stehen.

``domain_audit.attestations`` gab es nie, und der INSERT steht ungeschuetzt im
Druckpfad. Jeder Nachdruck eines gebuchten Lieferscheins lief deshalb in einen
500, und der Lieferschein blieb ungedruckt: Die Governance war nicht streng,
sondern kaputt. Wer nachdrucken musste, kam gar nicht durch — und wenn doch,
gaebe es keine Spur.

Ohne erreichbare Datenbank wird uebersprungen, nicht als gruen gewertet.
"""

from __future__ import annotations

import os
import uuid

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
        with create_engine(DB_URL).connect() as verbindung:
            vorhanden = verbindung.execute(
                text("SELECT to_regclass('domain_audit.attestations')")
            ).scalar()
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank nicht erreichbar: {fehler}")
    if not vorhanden:
        pytest.skip("Tabelle domain_audit.attestations fehlt")

    from fastapi.testclient import TestClient

    from app.main import app

    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture()
def gebuchter_lieferschein():
    from sqlalchemy import create_engine, text

    mandant = f"test-{uuid.uuid4().hex[:8]}"
    ls_id = str(uuid.uuid4())
    nummer = f"LS-{uuid.uuid4().hex[:6].upper()}"

    engine = create_engine(DB_URL)
    with engine.begin() as verbindung:
        verbindung.execute(
            text(
                "INSERT INTO domain_shared.tenants (id, name, domain, is_active) "
                "VALUES (:id, :id, :domain, true) ON CONFLICT (id) DO NOTHING"
            ),
            {"id": mandant, "domain": f"{mandant}.test"},
        )
        spalten = [
            r[0]
            for r in verbindung.execute(
                text(
                    "SELECT column_name FROM information_schema.columns "
                    "WHERE table_schema = 'domain_sales' AND table_name = 'delivery_notes'"
                )
            )
        ]
        if "delivery_note_number" in spalten:
            nummernspalte = "delivery_note_number"
        elif "ls_nr" in spalten:
            nummernspalte = "ls_nr"
        else:  # pragma: no cover — Form unbekannt, dann ist der Test nicht aussagekraeftig
            pytest.skip("Lieferscheintabelle hat keine erkennbare Nummernspalte")

        verbindung.execute(
            text(
                f"INSERT INTO domain_sales.delivery_notes "
                f"(id, tenant_id, {nummernspalte}, delivery_date, status) "
                f"VALUES (:id, :tid, :nr, CURRENT_DATE, 'posted')"
            ),
            {"id": ls_id, "tid": mandant, "nr": nummer},
        )
    try:
        yield {"id": ls_id, "mandant": mandant, "nummer": nummer}
    finally:
        with engine.begin() as verbindung:
            verbindung.execute(
                text("DELETE FROM domain_audit.attestations WHERE tenant_id = :tid"),
                {"tid": mandant},
            )
            verbindung.execute(
                text("DELETE FROM domain_sales.delivery_notes WHERE id = :id"), {"id": ls_id}
            )
            verbindung.execute(
                text("DELETE FROM domain_shared.tenants WHERE id = :tid"), {"tid": mandant}
            )


def kopf(mandant: str) -> dict[str, str]:
    return {
        "Authorization": "Bearer dev-token",
        "X-Tenant-ID": mandant,
        "X-Tenant-Id": mandant,
    }


def test_ohne_begruendung_kein_nachdruck(client, gebuchter_lieferschein) -> None:
    antwort = client.post(
        f"/api/v1/sales/delivery-notes/{gebuchter_lieferschein['id']}/print",
        headers=kopf(gebuchter_lieferschein["mandant"]),
    )
    assert antwort.status_code == 400, antwort.text


def test_mit_begruendung_gelingt_der_nachdruck(client, gebuchter_lieferschein) -> None:
    antwort = client.post(
        f"/api/v1/sales/delivery-notes/{gebuchter_lieferschein['id']}/print",
        params={"attestation": "Fahrer hat das Original verloren"},
        headers=kopf(gebuchter_lieferschein["mandant"]),
    )
    assert antwort.status_code == 200, antwort.text


def test_die_begruendung_bleibt_nachlesbar(client, gebuchter_lieferschein) -> None:
    """Ohne Spur waere die Attestierung nur eine Huerde, keine Auskunft."""
    from sqlalchemy import create_engine, text

    grund = "Kunde verlangt Zweitschrift"
    client.post(
        f"/api/v1/sales/delivery-notes/{gebuchter_lieferschein['id']}/print",
        params={"attestation": grund},
        headers=kopf(gebuchter_lieferschein["mandant"]),
    )
    with create_engine(DB_URL).connect() as verbindung:
        zeile = verbindung.execute(
            text(
                "SELECT entity_type, action, reason, created_by "
                "FROM domain_audit.attestations "
                "WHERE tenant_id = :tid AND entity_id = :eid"
            ),
            {"tid": gebuchter_lieferschein["mandant"], "eid": gebuchter_lieferschein["id"]},
        ).first()
    assert zeile is not None, "Der Nachdruck hat keine Spur hinterlassen"
    assert zeile[0] == "delivery_note"
    assert zeile[1] == "print"
    assert zeile[2] == grund
    assert zeile[3], "Kein Urheber vermerkt"
