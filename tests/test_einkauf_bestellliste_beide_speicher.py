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


def test_der_stornogrund_bleibt_am_beleg_stehen(client, engine, bestellung_im_einkauf) -> None:
    """Ein Storno ohne Grund ist spaeter nicht mehr zu erklaeren.

    Die Maske fragt danach, der Beleg hielt ihn bisher nicht fest. Weder der
    Lieferant noch die Revision koennen sonst nachvollziehen, ob storniert
    wurde, weil falsch erfasst, weil nicht lieferbar oder weil der Kunde
    absprang.
    """
    from sqlalchemy import text

    antwort = client.post(
        f"/api/v1/einkauf/bestellungen/{bestellung_im_einkauf['id']}/stornieren",
        params={"grund": "Lieferant kann nicht liefern"},
        headers=kopf(bestellung_im_einkauf["mandant"]),
    )
    assert antwort.status_code == 200, antwort.text
    assert antwort.json()["status"] == "storniert"

    with engine.connect() as v:
        zeile = v.execute(
            text("SELECT status, notiz FROM domain_einkauf.bestellungen WHERE id::text = :id"),
            {"id": bestellung_im_einkauf["id"]},
        ).mappings().first()
    assert zeile["status"] == "storniert"
    assert "Lieferant kann nicht liefern" in (zeile["notiz"] or "")


def test_ohne_grund_wird_trotzdem_storniert(client, bestellung_im_einkauf) -> None:
    """Der Grund ist wichtig, aber kein Zwang — sonst blockiert er die Korrektur."""
    antwort = client.post(
        f"/api/v1/einkauf/bestellungen/{bestellung_im_einkauf['id']}/stornieren",
        headers=kopf(bestellung_im_einkauf["mandant"]),
    )
    assert antwort.status_code == 200, antwort.text
    assert antwort.json()["status"] == "storniert"


# ─────────────────────────────────────────────────────────────────────────────
# Der Schreibweg: Compat legt im fuehrenden Bestand an, nicht mehr als Dokument
# ─────────────────────────────────────────────────────────────────────────────


@pytest.fixture()
def lieferant(engine):
    """Ein Lieferant mit Stammsatz — ohne den gibt es keine Bestellung."""
    from sqlalchemy import text

    mandant = f"test-{uuid.uuid4().hex[:8]}"
    lieferant_id = str(uuid.uuid4())
    name = f"Saatgut {uuid.uuid4().hex[:5]}"

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
                "VALUES (:id, :t, :nr, :name)"
            ),
            {
                "id": lieferant_id, "t": mandant,
                "nr": f"LF-{uuid.uuid4().hex[:5].upper()}", "name": name,
            },
        )

    try:
        yield {"mandant": mandant, "id": lieferant_id, "name": name}
    finally:
        with engine.begin() as v:
            for sql in (
                "DELETE FROM domain_einkauf.bestellung_positionen WHERE bestellung_id IN "
                "(SELECT id FROM domain_einkauf.bestellungen WHERE tenant_id = :t)",
                "DELETE FROM domain_einkauf.bestellungen WHERE tenant_id = :t",
                "DELETE FROM domain_einkauf.lieferanten WHERE tenant_id = :t",
                "DELETE FROM domain_shared.tenants WHERE id = :t",
            ):
                v.execute(text(sql), {"t": mandant})


def test_compat_legt_im_fuehrenden_bestand_an(client, engine, lieferant) -> None:
    """Der Nummernkreis ist EK-, und der Beleg steht in domain_einkauf.

    Vorher entstand hier ein Dokument mit PO-Nummer. Damit waere die alte Welt
    weitergewachsen, obwohl beide Masken schon richtig lesen.
    """
    from sqlalchemy import text

    antwort = client.post(
        "/api/v1/purchase-orders",
        headers=kopf(lieferant["mandant"]),
        json={
            "supplierId": lieferant["name"],
            "subject": "Fruehjahrssaat",
            "items": [{"description": "Grassaat", "quantity": 10, "unitPrice": 3.15}],
        },
    )
    assert antwort.status_code == 201, antwort.text
    beleg = antwort.json()
    assert beleg["purchaseOrderNumber"].startswith("EK-"), beleg["purchaseOrderNumber"]
    assert beleg["herkunft"] == "einkauf"

    with engine.connect() as v:
        vorhanden = v.execute(
            text("SELECT count(*) FROM domain_einkauf.bestellungen WHERE id::text = :id"),
            {"id": beleg["id"]},
        ).scalar()
    assert vorhanden == 1


def test_die_summen_werden_gerechnet(client, lieferant) -> None:
    """Gerechnet wurde nie — jede Bestellung stand auf 0,00.

    Aufgefallen ist es erst, als die Compat-Anlage auf diesen Weg kam und eine
    frische Bestellung ueber zehn Sack Grassaat null zurueckmeldete.
    """
    antwort = client.post(
        "/api/v1/purchase-orders",
        headers=kopf(lieferant["mandant"]),
        json={
            "supplierId": lieferant["name"],
            "items": [
                {"description": "Grassaat", "quantity": 10, "unitPrice": 3.15},
                {"description": "Nachsaat", "quantity": 4, "unitPrice": 2.50,
                 "discountPercent": 10},
            ],
        },
    )
    beleg = antwort.json()
    netto = 10 * 3.15 + 4 * 2.50 * 0.9
    assert beleg["subtotal"] == pytest.approx(netto, abs=0.01)
    assert beleg["totalAmount"] == pytest.approx(netto * 1.19, abs=0.01)


def test_ohne_stammsatz_keine_bestellung(client, lieferant) -> None:
    """Der Dokumentenspeicher nahm jeden Namen entgegen, auch erfundene.

    Der fuehrende Beleg verlangt einen echten Lieferanten — ohne ihn gibt es
    keine Anschrift, keine Zahlungsbedingung und keine Auswertung. Erfunden
    wird hier nichts; wer fehlt, bekommt eine klare Absage.
    """
    antwort = client.post(
        "/api/v1/purchase-orders",
        headers=kopf(lieferant["mandant"]),
        json={"supplierId": "Gibtsnicht GmbH", "items": []},
    )
    assert antwort.status_code == 422, antwort.text
    assert "nicht zu finden" in str(antwort.json().get("detail", ""))


def test_storno_ueber_compat_wirkt_am_beleg(client, engine, lieferant) -> None:
    from sqlalchemy import text

    beleg = client.post(
        "/api/v1/purchase-orders",
        headers=kopf(lieferant["mandant"]),
        json={
            "supplierId": lieferant["name"],
            "items": [{"description": "Test", "quantity": 1, "unitPrice": 1}],
        },
    ).json()

    antwort = client.post(
        f"/api/v1/purchase-orders/{beleg['id']}/cancel-with-reason",
        headers=kopf(lieferant["mandant"]),
        json={"reason": "Doppelt erfasst"},
    )
    assert antwort.status_code == 200, antwort.text

    with engine.connect() as v:
        zeile = v.execute(
            text("SELECT status, notiz FROM domain_einkauf.bestellungen WHERE id::text = :id"),
            {"id": beleg["id"]},
        ).mappings().first()
    assert zeile["status"] == "storniert"
    assert "Doppelt erfasst" in (zeile["notiz"] or "")
