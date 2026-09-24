"""Die Bestellliste zeigt die Bestellungen, die es wirklich gibt.

Es gibt zwei Bestellwelten: Die Compat-Schnittstelle ``/api/v1/purchase-orders``
legt Dokumente in einem generischen Dokumentenspeicher ab, die fuehrende Maske
(``einkauf/purchase-order``) schreibt nach ``domain_einkauf.bestellungen``. Wer
die Liste aufrief, sah nur die eine Haelfte — und gerade die Bestellungen, die
aus einem Verkaufsauftrag entstanden sind, fehlten vollstaendig.

Zusammengelegt sind die Speicher damit nicht; das ist ein eigener Schritt mit
Migration und Nummernkreis. Was geprueft wird, ist das Noetige: Lesen zeigt
beides, und zwar nur den eigenen Mandanten.

Ohne erreichbare Datenbank wird uebersprungen, nicht als gruen gewertet.
"""

from __future__ import annotations

import os
import uuid
from datetime import date

import pytest

pytestmark = pytest.mark.integration

DB_URL = os.environ.get(
    "DATABASE_URL", "postgresql://valeo_dev:valeo_dev_2024@127.0.0.1:5432/valeo_neuro_erp"
)
os.environ.setdefault("DATABASE_URL", DB_URL)
os.environ.setdefault("API_DEV_TOKEN", "dev-token")


@pytest.fixture(scope="module")
def engine():
    from sqlalchemy import create_engine, text

    try:
        e = create_engine(DB_URL)
        with e.connect() as c:
            c.execute(text("SELECT 1"))
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank nicht erreichbar: {fehler}")
    return e


@pytest.fixture(scope="module")
def client():
    from fastapi.testclient import TestClient

    from app.main import app

    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture()
def bestellung_im_einkauf(engine):
    """Eine Bestellung im fuehrenden Speicher — so wie die Maske sie anlegt."""
    from sqlalchemy import text

    mandant = f"test-{uuid.uuid4().hex[:8]}"
    lieferant_id = str(uuid.uuid4())
    bestell_id = str(uuid.uuid4())
    nummer = f"EK-{uuid.uuid4().hex[:8].upper()}"

    with engine.begin() as v:
        v.execute(
            text(
                "INSERT INTO domain_shared.tenants (id, name, domain, is_active) "
                "VALUES (:id, :id, :d, true) ON CONFLICT (id) DO NOTHING"
            ),
            {"id": mandant, "d": f"{mandant}.test"},
        )
        v.execute(
            text(
                "INSERT INTO domain_einkauf.lieferanten "
                "(id, tenant_id, lieferantennummer, firmenname) "
                "VALUES (:id, :t, :nr, 'Sichtbarer Lieferant')"
            ),
            {"id": lieferant_id, "t": mandant, "nr": f"LF-{uuid.uuid4().hex[:5].upper()}"},
        )
        v.execute(
            text(
                "INSERT INTO domain_einkauf.bestellungen "
                "(id, tenant_id, bestellnummer, lieferant_id, bestelldatum, status, "
                " bestellfall, netto_summe, brutto_summe, kommission) "
                "VALUES (:id, :t, :nr, :lf, :d, 'bestellt', 'direktlieferung', "
                "        1000, 1190, 'AU-TEST-1')"
            ),
            {
                "id": bestell_id, "t": mandant, "nr": nummer,
                "lf": lieferant_id, "d": date.today(),
            },
        )

    try:
        yield {"mandant": mandant, "id": bestell_id, "nummer": nummer}
    finally:
        with engine.begin() as v:
            for sql in (
                "DELETE FROM domain_einkauf.bestellungen WHERE tenant_id = :t",
                "DELETE FROM domain_einkauf.lieferanten WHERE tenant_id = :t",
                "DELETE FROM domain_shared.tenants WHERE id = :t",
            ):
                v.execute(text(sql), {"t": mandant})


def kopf(mandant: str) -> dict[str, str]:
    return {
        "Authorization": "Bearer dev-token",
        "X-Tenant-ID": mandant,
        "X-Tenant-Id": mandant,
    }


def test_die_liste_zeigt_die_bestellung_aus_dem_fuehrenden_speicher(
    client, bestellung_im_einkauf
) -> None:
    antwort = client.get(
        "/api/v1/purchase-orders", headers=kopf(bestellung_im_einkauf["mandant"])
    )
    assert antwort.status_code == 200, antwort.text
    nummern = [z.get("purchaseOrderNumber") for z in antwort.json().get("data", [])]
    assert bestellung_im_einkauf["nummer"] in nummern, (
        f"Die Bestellung fehlt in der Liste: {nummern}"
    )


def test_die_zeile_traegt_lieferant_und_betrag(client, bestellung_im_einkauf) -> None:
    """Eine Zeile ohne Lieferant und Betrag waere nur ein halber Beleg."""
    daten = client.get(
        "/api/v1/purchase-orders", headers=kopf(bestellung_im_einkauf["mandant"])
    ).json()["data"]
    zeile = next(z for z in daten if z["purchaseOrderNumber"] == bestellung_im_einkauf["nummer"])

    assert zeile["supplierName"] == "Sichtbarer Lieferant"
    assert zeile["totalAmount"] == pytest.approx(1190.0, abs=0.01)
    assert zeile["status"] == "BESTELLT"
    # Solange es zwei Speicher gibt, bleibt sichtbar, aus welchem der Beleg kommt.
    assert zeile["herkunft"] == "einkauf"


def test_der_einzelabruf_findet_sie_auch(client, bestellung_im_einkauf) -> None:
    antwort = client.get(
        f"/api/v1/purchase-orders/{bestellung_im_einkauf['id']}",
        headers=kopf(bestellung_im_einkauf["mandant"]),
    )
    assert antwort.status_code == 200, antwort.text
    assert antwort.json()["purchaseOrderNumber"] == bestellung_im_einkauf["nummer"]


def test_ein_fremder_mandant_sieht_sie_nicht(client, bestellung_im_einkauf) -> None:
    """Der Rueckfall auf alle Mandanten ist raus.

    Er sprang ein, sobald der eigene Mandant nichts hatte, und haette dann
    fremde Bestellungen gezeigt — mit Lieferant, Betrag und Adresse.
    """
    antwort = client.get(
        "/api/v1/purchase-orders", headers=kopf(f"test-leer-{uuid.uuid4().hex[:6]}")
    )
    assert antwort.status_code == 200
    nummern = [z.get("purchaseOrderNumber") for z in antwort.json().get("data", [])]
    assert bestellung_im_einkauf["nummer"] not in nummern
