"""Die Kunden-360-Sicht zeigt die Kontrakte, die der Partner wirklich hat.

Gelesen wurde ``domain_agrar.agrar_contracts`` — dieses Schema gibt es nicht.
Gefuehrt werden die Kontrakte in ``domain_inventory.agrar_contracts``, mit
anderen Spalten (`valid_from` statt `lieferbeginn`, `total_quantity_kg` statt
`gesamtmenge_t`) **und** anderen Statuswerten: `open` und
`partially_allocated`, nicht `AKTIV`. Das blosse Umhaengen des Schemas haette
also weiterhin eine leere Liste ergeben — und eine leere Liste sieht aus wie
„keine Kontrakte", nicht wie „falsche Tabelle".

Ohne erreichbare Datenbank oder ohne einen Partner mit Kontrakt wird
uebersprungen, nicht als gruen gewertet.
"""

from __future__ import annotations

import os

import pytest

pytestmark = pytest.mark.integration

DB_URL = os.environ.get(
    "DATABASE_URL", "postgresql://valeo_dev:valeo_dev_2024@127.0.0.1:5432/valeo_neuro_erp"
)
os.environ.setdefault("DATABASE_URL", DB_URL)
os.environ.setdefault("API_DEV_TOKEN", "dev-token")


@pytest.fixture(scope="module")
def partner_mit_kontrakt() -> dict:
    """Ein Partner, der im Bestand wirklich einen laufenden Kontrakt hat."""
    from sqlalchemy import create_engine, text

    try:
        engine = create_engine(DB_URL)
        with engine.connect() as verbindung:
            zeile = verbindung.execute(
                text(
                    """
                    SELECT k.partner_id::text AS partner_id,
                           k.tenant_id::text  AS mandant,
                           k.contract_number  AS kontrakt_nr
                    FROM domain_inventory.agrar_contracts k
                    JOIN domain_crm.business_partners p
                      ON p.partner_id = k.partner_id
                    WHERE k.status IN ('open', 'partially_allocated')
                    LIMIT 1
                    """
                )
            ).mappings().first()
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank nicht erreichbar: {fehler}")

    if zeile is None:
        pytest.skip("Kein Partner mit laufendem Kontrakt im Bestand")
    return dict(zeile)


@pytest.fixture(scope="module")
def client():
    from fastapi.testclient import TestClient

    from app.main import app

    return TestClient(app, raise_server_exceptions=False)


def kopf(mandant: str) -> dict[str, str]:
    return {
        "Authorization": "Bearer dev-token",
        "X-Tenant-ID": mandant,
        "X-Tenant-Id": mandant,
    }


def test_der_kontrakt_des_partners_steht_in_der_360_sicht(client, partner_mit_kontrakt) -> None:
    antwort = client.get(
        f"/api/v1/crm/customers/{partner_mit_kontrakt['partner_id']}/360",
        headers=kopf(partner_mit_kontrakt["mandant"]),
    )
    assert antwort.status_code == 200, antwort.text

    kontrakte = antwort.json().get("active_contracts") or []
    nummern = [k.get("contract_number") for k in kontrakte]
    assert partner_mit_kontrakt["kontrakt_nr"] in nummern, (
        f"Kontrakt {partner_mit_kontrakt['kontrakt_nr']} fehlt in der 360-Sicht: {nummern}"
    )


def test_der_kontrakt_traegt_zeitraum_und_wert(client, partner_mit_kontrakt) -> None:
    """Leere Felder waeren derselbe stille Fehler eine Ebene tiefer."""
    antwort = client.get(
        f"/api/v1/crm/customers/{partner_mit_kontrakt['partner_id']}/360",
        headers=kopf(partner_mit_kontrakt["mandant"]),
    )
    kontrakt = next(
        k
        for k in antwort.json()["active_contracts"]
        if k["contract_number"] == partner_mit_kontrakt["kontrakt_nr"]
    )
    assert kontrakt["start_date"], "Kontrakt ohne Lieferbeginn"
    assert kontrakt["status"] in ("open", "partially_allocated")
    assert isinstance(kontrakt["total_value"], (int, float))


def test_ein_fremder_mandant_sieht_den_kontrakt_nicht(client, partner_mit_kontrakt) -> None:
    antwort = client.get(
        f"/api/v1/crm/customers/{partner_mit_kontrakt['partner_id']}/360",
        headers=kopf("test-mandant-ohne-kontrakte"),
    )
    if antwort.status_code == 404:
        return  # Den Partner gibt es dort gar nicht — auch eine Antwort.
    nummern = [k.get("contract_number") for k in antwort.json().get("active_contracts") or []]
    assert partner_mit_kontrakt["kontrakt_nr"] not in nummern
