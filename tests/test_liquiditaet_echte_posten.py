"""Die Liquiditaetssicht liest die offenen Posten, die es wirklich gibt.

Drei Tabellen fuehren in diesem Haus offene Posten:

- ``domain_erp.offene_posten`` — hier schreibt der Belegfluss hinein
  (Rechnung aus Lieferschein, Sammelrechnung). **Die volle.**
- ``domain_erp.open_items`` — leer.
- ``domain_shared.open_items`` — leer.

Uebersicht und Planung lasen die beiden leeren und meldeten 0,00. Eine Null
sieht aus wie „nichts offen", nicht wie „falsche Tabelle" — deshalb faellt so
etwas nicht auf, sondern beruhigt.

Ohne erreichbare Datenbank wird uebersprungen, nicht als gruen gewertet.
"""

from __future__ import annotations

import os
import uuid
from datetime import date, timedelta

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
                text("SELECT to_regclass('domain_erp.offene_posten')")
            ).scalar()
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank nicht erreichbar: {fehler}")
    if not vorhanden:
        pytest.skip("Tabelle domain_erp.offene_posten fehlt")

    from fastapi.testclient import TestClient

    from app.main import app

    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture()
def mandant_mit_posten():
    """Ein Mandant mit je einem offenen Debitoren- und Kreditorenposten."""
    from sqlalchemy import create_engine, text

    name = f"test-{uuid.uuid4().hex[:8]}"
    faellig = date.today() + timedelta(days=10)
    engine = create_engine(DB_URL)
    with engine.begin() as verbindung:
        verbindung.execute(
            text(
                "INSERT INTO domain_shared.tenants (id, name, domain, is_active) "
                "VALUES (:id, :id, :domain, true) ON CONFLICT (id) DO NOTHING"
            ),
            {"id": name, "domain": f"{name}.test"},
        )
        for konto_typ, betrag in (("debitoren", 1500), ("kreditoren", 400)):
            verbindung.execute(
                text(
                    "INSERT INTO domain_erp.offene_posten "
                    "(id, tenant_id, konto_typ, rechnungsnr, rechnungsdatum, datum, "
                    " faelligkeit, betrag, offen, op_status) "
                    "VALUES (:id, :tid, :typ, :nr, :heute, :heute, :faellig, "
                    "        :betrag, :betrag, 'offen')"
                ),
                {
                    "id": str(uuid.uuid4()),
                    "tid": name,
                    "typ": konto_typ,
                    "nr": f"RE-{uuid.uuid4().hex[:6].upper()}",
                    "heute": date.today().isoformat(),
                    "faellig": faellig.isoformat(),
                    "betrag": betrag,
                },
            )
        # Ein stornierter Posten zaehlt nicht mit.
        verbindung.execute(
            text(
                "INSERT INTO domain_erp.offene_posten "
                "(id, tenant_id, konto_typ, rechnungsnr, rechnungsdatum, datum, "
                " faelligkeit, betrag, offen, op_status) "
                "VALUES (:id, :tid, 'debitoren', :nr, :heute, :heute, :faellig, "
                "        9999, 9999, 'storniert')"
            ),
            {
                "id": str(uuid.uuid4()),
                "tid": name,
                "nr": f"RE-{uuid.uuid4().hex[:6].upper()}",
                "heute": date.today().isoformat(),
                "faellig": faellig.isoformat(),
            },
        )
    try:
        yield name
    finally:
        with engine.begin() as verbindung:
            verbindung.execute(
                text("DELETE FROM domain_erp.offene_posten WHERE tenant_id = :id"), {"id": name}
            )
            verbindung.execute(
                text("DELETE FROM domain_shared.tenants WHERE id = :id"), {"id": name}
            )


@pytest.fixture()
def kopf(mandant_mit_posten: str) -> dict[str, str]:
    return {
        "Authorization": "Bearer dev-token",
        "X-Tenant-ID": mandant_mit_posten,
        "X-Tenant-Id": mandant_mit_posten,
    }


def test_uebersicht_zeigt_die_offenen_posten(client, kopf) -> None:
    antwort = client.get("/api/v1/finance/liquidity/overview", headers=kopf)
    assert antwort.status_code == 200, antwort.text
    daten = antwort.json()

    assert float(daten["forderungen_offen"]) == pytest.approx(1500.0, abs=0.01)
    assert float(daten["verbindlichkeiten_offen"]) == pytest.approx(400.0, abs=0.01)
    assert float(daten["netto_working_capital"]) == pytest.approx(1100.0, abs=0.01)


def test_stornierte_posten_zaehlen_nicht_mit(client, kopf) -> None:
    """9.999 auf storniert — wer sie mitzaehlt, plant mit Geld, das nicht kommt."""
    daten = client.get("/api/v1/finance/liquidity/overview", headers=kopf).json()
    assert float(daten["forderungen_offen"]) < 9000


def test_prognose_ordnet_nach_faelligkeit_ein(client, kopf) -> None:
    daten = client.get("/api/v1/finance/liquidity/overview", headers=kopf).json()
    erste = daten["prognose"][0]
    # Beide Posten sind in zehn Tagen faellig, also im ersten Fenster.
    assert float(erste["erwartete_eingaenge"]) == pytest.approx(1500.0, abs=0.01)
    assert float(erste["erwartete_ausgaenge"]) == pytest.approx(400.0, abs=0.01)


def test_fremde_posten_bleiben_draussen(client) -> None:
    fremd = {
        "Authorization": "Bearer dev-token",
        "X-Tenant-ID": "test-ohne-posten",
        "X-Tenant-Id": "test-ohne-posten",
    }
    daten = client.get("/api/v1/finance/liquidity/overview", headers=fremd).json()
    assert float(daten["forderungen_offen"]) == 0.0


def test_management_dashboard_zeigt_dieselben_offenen_posten(client, kopf) -> None:
    """Dasselbe Haus, dieselbe Zahl.

    Das Management-Dashboard las ebenfalls eine leere Tabelle und wies die
    offenen Posten mit 0 aus — waehrend die Belegseite 1.900 EUR fuehrte.
    """
    antwort = client.get("/api/v1/management/dashboard", headers=kopf)
    assert antwort.status_code == 200, antwort.text
    kennzahlen = {k["label"]: k["value"] for k in antwort.json().get("kpis", [])}
    assert "Offene Posten" in kennzahlen
    # 1.500 Debitoren + 400 Kreditoren, stornierte bleiben draussen.
    roh = str(kennzahlen["Offene Posten"]).replace("K", "000").replace(",", ".")
    assert float(roh) >= 1900 * 0.9
