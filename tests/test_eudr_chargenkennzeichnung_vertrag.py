"""Charge, Nachweis und die zwei Richtungen der EU-Anbindung.

Verordnung (EU) 2023/1115. Drei Dinge, die vorher fehlten:

1. **Welche Erklärung deckt diese Charge?** Art. 4 verbietet das
   Inverkehrbringen ohne Sorgfaltserklärung — also muss eine Charge sagen
   können, welche Erklärung sie deckt. Im Landhandel wird verschnitten, deshalb
   eine Verbindung mit Menge, nicht eine Spalte.
2. **Ist die eigene Erklärung übermittelt?** Fachlich eingereicht und technisch
   an das EU-Informationssystem übermittelt (Art. 33) sind zwei Dinge, die
   auseinanderfallen können.
3. **Ist die zugekaufte Erklärung geprüft?** Ein Händler ist öfter
   Zwischenhändler als Erst-Inverkehrbringer und gibt fremde Referenznummern
   weiter. Bis hierhin trug das Register die Nummern, aber nichts darüber, ob
   sie jemand nachgeprüft hat — eine abgeschriebene Nummer sah aus wie ein
   Nachweis.

Geprüft wird gegen die gemeinsame, vorhandene Prüfstand-Datenbank.
"""

from __future__ import annotations

import os
import uuid
from datetime import date

import pytest

pytestmark = pytest.mark.integration

DB_URL = os.environ.get(
    "TEST_DATABASE_URL",
    os.environ.get(
        "DATABASE_URL",
        "postgresql://valeo_dev:valeo_dev_2024@127.0.0.1:5432/valeo_probe",
    ),
)
os.environ.setdefault("DATABASE_URL", DB_URL)
os.environ.setdefault("API_DEV_TOKEN", "dev-token")

HAUS_A = f"eudrc-a-{uuid.uuid4().hex[:6]}"
HAUS_B = f"eudrc-b-{uuid.uuid4().hex[:6]}"

REGISTER = "/api/v1/eudr/sorgfaltserklaerungen"
ERKLAERUNGEN = "domain_compliance.eudr_due_diligence"
CHARGEN = "domain_inventory.inventory_lots"
BINDUNGEN = "domain_inventory.lot_eudr_erklaerungen"
VORGELAGERT = "domain_compliance.eudr_vorgelagerte_erklaerungen"


@pytest.fixture(scope="module")
def engine():
    from sqlalchemy import create_engine, text

    try:
        motor = create_engine(DB_URL)
        with motor.connect() as conn:
            spalte = conn.execute(
                text(
                    "SELECT column_name FROM information_schema.columns "
                    "WHERE table_schema='domain_inventory' AND table_name='inventory_lots' "
                    "AND column_name='eudr_relevant'"
                )
            ).scalar()
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank nicht erreichbar: {fehler}")
    if not spalte:
        pytest.skip("Migration eudr_chargenkennzeichnung_20261001 nicht angewandt")
    return motor


@pytest.fixture(scope="module")
def client(engine):
    from fastapi.testclient import TestClient

    from app.main import app

    return TestClient(app, raise_server_exceptions=False)


def kopf(tenant: str) -> dict[str, str]:
    return {"X-Tenant-Id": tenant, "Authorization": "Bearer dev-token"}


def _aufraeumen(engine) -> None:
    from sqlalchemy import text

    with engine.begin() as v:
        v.execute(
            text(f"DELETE FROM {BINDUNGEN} WHERE tenant_id IN (:a, :b)"),
            {"a": HAUS_A, "b": HAUS_B},
        )
        v.execute(
            text(f"DELETE FROM {CHARGEN} WHERE tenant_id IN (:a, :b)"),
            {"a": HAUS_A, "b": HAUS_B},
        )
        v.execute(
            text(f"DELETE FROM {ERKLAERUNGEN} WHERE tenant_id IN (:a, :b)"),
            {"a": HAUS_A, "b": HAUS_B},
        )


@pytest.fixture(autouse=True)
def sauber(engine):
    _aufraeumen(engine)
    yield
    _aufraeumen(engine)


def _charge(engine, tenant: str, menge: float = 26000.0, relevant: bool = True) -> str:
    from sqlalchemy import text

    lot_id = str(uuid.uuid4())
    with engine.begin() as v:
        v.execute(
            text(
                f"INSERT INTO {CHARGEN} (id, tenant_id, article_id, warehouse_id, "
                " lot_number, initial_qty, current_qty, unit, status, created_at, eudr_relevant) "
                "VALUES (:id, :t, 'ART-SOJA', 'SILO-1', :nr, :menge, :menge, 'kg', "
                "        'frei', NOW(), :relevant)"
            ),
            {
                "id": lot_id,
                "t": tenant,
                "nr": f"CH-{lot_id[:8]}",
                "menge": menge,
                "relevant": relevant,
            },
        )
    return lot_id


def _eingereichte_erklaerung(client, tenant: str, referenz: str, **felder) -> dict:
    rumpf = {
        "betreiber_name": "Landhandel Nord eG",
        "betreiber_adresse": "Hafenstrasse 1, 26789 Leer",
        "rohstoff": "SOJA",
        "hs_code": "230400",
        "warenbeschreibung": "Sojaextraktionsschrot",
        "menge_netto_kg": 26000.0,
        "produktionsland": "BR",
        "produktion_von": "2026-02-01",
        "produktion_bis": "2026-04-30",
        "lieferant_name": "Cooperativa Agricola Sul",
        "nachweis_abholzungsfrei": True,
        "nachweis_rechtskonform": True,
    }
    rumpf.update(felder)
    angelegt = client.post(REGISTER, json=rumpf, headers=kopf(tenant))
    assert angelegt.status_code == 201, angelegt.text
    erklaerung = angelegt.json()
    client.post(
        f"{REGISTER}/{erklaerung['id']}/risikobewertung",
        json={"risikostufe": "VERNACHLAESSIGBAR", "bewertet_durch": "QS"},
        headers=kopf(tenant),
    )
    eingereicht = client.post(
        f"{REGISTER}/{erklaerung['id']}/einreichen",
        json={
            "referenznummer": referenz,
            "verifizierungsnummer": f"VER-{referenz}",
            "erklaerung_durch_name": "A. Meyer",
            "erklaerung_durch_funktion": "Geschaeftsfuehrung",
        },
        headers=kopf(tenant),
    )
    assert eingereicht.status_code == 200, eingereicht.text
    return eingereicht.json()


# 1 ── Die Charge sagt, welche Erklärung sie deckt ───────────────────────────

def test_charge_wird_an_eine_eingereichte_erklaerung_gebunden(client, engine):
    erklaerung = _eingereichte_erklaerung(client, HAUS_A, "REF-CH-1")
    lot_id = _charge(engine, HAUS_A, menge=26000.0)

    antwort = client.post(
        f"{REGISTER}/{erklaerung['id']}/chargen",
        json={"lot_id": lot_id, "menge_kg": 26000.0, "verknuepft_durch": "Wareneingang"},
        headers=kopf(HAUS_A),
    )
    assert antwort.status_code == 201, antwort.text

    stand = client.get(f"{REGISTER}/chargen/{lot_id}", headers=kopf(HAUS_A))
    assert stand.status_code == 200, stand.text
    daten = stand.json()
    assert daten["kennzeichnung"] == "NACHGEWIESEN"
    assert daten["gedeckte_menge_kg"] == pytest.approx(26000.0)
    assert daten["offene_menge_kg"] == pytest.approx(0.0)
    assert daten["erklaerungen"] == [erklaerung["id"]]


def test_eine_charge_kann_von_mehreren_erklaerungen_gedeckt_sein(client, engine):
    """Im Landhandel wird verschnitten: eine Silocharge aus zwei Partien."""
    erste = _eingereichte_erklaerung(client, HAUS_A, "REF-MIX-1")
    zweite = _eingereichte_erklaerung(client, HAUS_A, "REF-MIX-2")
    lot_id = _charge(engine, HAUS_A, menge=30000.0)

    for erklaerung, menge in ((erste, 20000.0), (zweite, 10000.0)):
        antwort = client.post(
            f"{REGISTER}/{erklaerung['id']}/chargen",
            json={"lot_id": lot_id, "menge_kg": menge},
            headers=kopf(HAUS_A),
        )
        assert antwort.status_code == 201, antwort.text

    daten = client.get(f"{REGISTER}/chargen/{lot_id}", headers=kopf(HAUS_A)).json()
    assert daten["kennzeichnung"] == "NACHGEWIESEN"
    assert daten["gedeckte_menge_kg"] == pytest.approx(30000.0)
    assert sorted(daten["erklaerungen"]) == sorted([erste["id"], zweite["id"]])


def test_teilweise_gedeckte_charge_bleibt_offen(client, engine):
    """Art. 4: Solange nicht die ganze Charge gedeckt ist, darf sie nicht in
    Verkehr gebracht werden."""
    erklaerung = _eingereichte_erklaerung(client, HAUS_A, "REF-TEIL-1")
    lot_id = _charge(engine, HAUS_A, menge=26000.0)

    client.post(
        f"{REGISTER}/{erklaerung['id']}/chargen",
        json={"lot_id": lot_id, "menge_kg": 10000.0},
        headers=kopf(HAUS_A),
    )
    daten = client.get(f"{REGISTER}/chargen/{lot_id}", headers=kopf(HAUS_A)).json()
    assert daten["kennzeichnung"] == "OFFEN"
    assert daten["offene_menge_kg"] == pytest.approx(16000.0)


def test_mehr_als_die_chargenmenge_wird_abgewiesen(client, engine):
    erklaerung = _eingereichte_erklaerung(client, HAUS_A, "REF-ZUVIEL-1")
    lot_id = _charge(engine, HAUS_A, menge=1000.0)

    antwort = client.post(
        f"{REGISTER}/{erklaerung['id']}/chargen",
        json={"lot_id": lot_id, "menge_kg": 1500.0},
        headers=kopf(HAUS_A),
    )
    assert antwort.status_code == 409, antwort.text
    assert "uebersteigen" in antwort.text


def test_ein_entwurf_deckt_keine_charge(client, engine):
    """Art. 4: Vorher darf nichts in Verkehr gebracht werden."""
    angelegt = client.post(
        REGISTER,
        json={
            "betreiber_name": "X",
            "betreiber_adresse": "Y",
            "rohstoff": "SOJA",
            "hs_code": "230400",
            "warenbeschreibung": "Z",
            "menge_netto_kg": 100.0,
            "produktionsland": "BR",
            "produktion_von": "2026-01-01",
            "produktion_bis": "2026-02-01",
            "lieferant_name": "L",
        },
        headers=kopf(HAUS_A),
    )
    assert angelegt.status_code == 201, angelegt.text
    lot_id = _charge(engine, HAUS_A, menge=100.0)

    antwort = client.post(
        f"{REGISTER}/{angelegt.json()['id']}/chargen",
        json={"lot_id": lot_id, "menge_kg": 100.0},
        headers=kopf(HAUS_A),
    )
    assert antwort.status_code == 409, antwort.text
    assert "eingereichte" in antwort.text


def test_eine_nicht_relevante_charge_wird_nicht_gebunden(client, engine):
    erklaerung = _eingereichte_erklaerung(client, HAUS_A, "REF-NREL-1")
    lot_id = _charge(engine, HAUS_A, relevant=False)

    antwort = client.post(
        f"{REGISTER}/{erklaerung['id']}/chargen",
        json={"lot_id": lot_id, "menge_kg": 10.0},
        headers=kopf(HAUS_A),
    )
    assert antwort.status_code == 409, antwort.text

    daten = client.get(f"{REGISTER}/chargen/{lot_id}", headers=kopf(HAUS_A)).json()
    assert daten["kennzeichnung"] == "NICHT_RELEVANT"


def test_dieselbe_erklaerung_deckt_eine_charge_nur_einmal(client, engine):
    erklaerung = _eingereichte_erklaerung(client, HAUS_A, "REF-DOPPEL-1")
    lot_id = _charge(engine, HAUS_A, menge=26000.0)
    for erwartet in (201, 409):
        antwort = client.post(
            f"{REGISTER}/{erklaerung['id']}/chargen",
            json={"lot_id": lot_id, "menge_kg": 1000.0},
            headers=kopf(HAUS_A),
        )
        assert antwort.status_code == erwartet, antwort.text


def test_eine_gebundene_erklaerung_ist_nicht_loeschbar(client, engine):
    """Der Nachweis, mit dem die Ware in Verkehr gebracht wurde, darf nicht
    verschwinden."""
    from sqlalchemy import text
    from sqlalchemy.exc import IntegrityError

    erklaerung = _eingereichte_erklaerung(client, HAUS_A, "REF-SCHUTZ-1")
    lot_id = _charge(engine, HAUS_A, menge=100.0)
    client.post(
        f"{REGISTER}/{erklaerung['id']}/chargen",
        json={"lot_id": lot_id, "menge_kg": 100.0},
        headers=kopf(HAUS_A),
    )
    with pytest.raises(IntegrityError):
        with engine.begin() as v:
            v.execute(
                text(f"DELETE FROM {ERKLAERUNGEN} WHERE id = :i"), {"i": erklaerung["id"]}
            )


def test_offene_chargen_sind_die_liste_der_nicht_verkehrsfaehigen(client, engine):
    erklaerung = _eingereichte_erklaerung(client, HAUS_A, "REF-LISTE-1")
    gedeckt = _charge(engine, HAUS_A, menge=100.0)
    offen = _charge(engine, HAUS_A, menge=5000.0)
    _charge(engine, HAUS_A, menge=700.0, relevant=False)
    client.post(
        f"{REGISTER}/{erklaerung['id']}/chargen",
        json={"lot_id": gedeckt, "menge_kg": 100.0},
        headers=kopf(HAUS_A),
    )

    antwort = client.get(f"{REGISTER}/chargen/offen", headers=kopf(HAUS_A))
    assert antwort.status_code == 200, antwort.text
    kennungen = [z["lot_id"] for z in antwort.json()]
    assert kennungen == [offen]


def test_fremde_charge_ist_nicht_sichtbar_und_nicht_bindbar(client, engine):
    erklaerung = _eingereichte_erklaerung(client, HAUS_A, "REF-FREMD-1")
    fremde_charge = _charge(engine, HAUS_B, menge=100.0)

    antwort = client.post(
        f"{REGISTER}/{erklaerung['id']}/chargen",
        json={"lot_id": fremde_charge, "menge_kg": 100.0},
        headers=kopf(HAUS_A),
    )
    assert antwort.status_code == 404, antwort.text

    sicht = client.get(f"{REGISTER}/chargen/{fremde_charge}", headers=kopf(HAUS_A))
    assert sicht.status_code == 404, sicht.text


def test_der_stand_zaehlt_die_chargen(client, engine):
    erklaerung = _eingereichte_erklaerung(client, HAUS_A, "REF-STAND-1")
    gedeckt = _charge(engine, HAUS_A, menge=100.0)
    _charge(engine, HAUS_A, menge=5000.0)
    client.post(
        f"{REGISTER}/{erklaerung['id']}/chargen",
        json={"lot_id": gedeckt, "menge_kg": 100.0},
        headers=kopf(HAUS_A),
    )

    stand = client.get(f"{REGISTER}/status", headers=kopf(HAUS_A)).json()
    assert stand["chargen_relevant"] == 2
    assert stand["chargen_nachgewiesen"] == 1
    assert stand["chargen_offen"] == 1
    assert stand["offene_menge_kg"] == pytest.approx(5000.0)
    # Eine offene Charge macht den Stand unvollstaendig, auch wenn jede
    # Erklaerung eingereicht ist.
    assert stand["status"] == "UNVOLLSTAENDIG"


# 2 ── Hinaus: ist die eigene Erklärung übermittelt? ─────────────────────────

def test_eingereicht_heisst_noch_nicht_uebermittelt(client):
    erklaerung = _eingereichte_erklaerung(client, HAUS_A, "REF-UEB-0")
    assert erklaerung["status"] == "EINGEREICHT"
    assert erklaerung["uebermittlung_status"] == "NICHT_UEBERMITTELT"
    assert erklaerung["uebermittelt_am"] is None


def test_uebermittlung_wird_festgehalten(client):
    erklaerung = _eingereichte_erklaerung(client, HAUS_A, "REF-UEB-1")
    antwort = client.post(
        f"{REGISTER}/{erklaerung['id']}/uebermittlung",
        json={
            "uebermittlung_status": "UEBERMITTELT",
            "eu_system_id": "EU-DDS-4711",
            "dienst": "EudrSubmissionClientV3",
            "umgebung": "PRODUKTION",
        },
        headers=kopf(HAUS_A),
    )
    assert antwort.status_code == 200, antwort.text
    daten = antwort.json()
    assert daten["uebermittlung_status"] == "UEBERMITTELT"
    assert daten["eu_system_id"] == "EU-DDS-4711"
    assert daten["uebermittelt_am"] is not None
    assert daten["uebermittlung_dienst"] == "EudrSubmissionClientV3"
    assert daten["uebermittlung_umgebung"] == "PRODUKTION"
    assert daten["uebermittlung_versuche"] == 1


def test_eine_uebermittlung_ohne_umgebung_wird_abgewiesen(client):
    """Ohne Umgebung ist nicht einzuordnen, ob die Uebermittlung rechtlich gilt
    oder eine Probe war."""
    erklaerung = _eingereichte_erklaerung(client, HAUS_A, "REF-UEB-UMG")
    antwort = client.post(
        f"{REGISTER}/{erklaerung['id']}/uebermittlung",
        json={"uebermittlung_status": "UEBERMITTELT"},
        headers=kopf(HAUS_A),
    )
    assert antwort.status_code == 422, antwort.text
    assert "Umgebung" in antwort.text


def test_der_annahmetest_zaehlt_nicht_als_abgabe(client):
    """Ein eingerichteter Testzugang darf nicht wie Erfuellung aussehen."""
    erklaerung = _eingereichte_erklaerung(client, HAUS_A, "REF-UEB-TEST")
    antwort = client.post(
        f"{REGISTER}/{erklaerung['id']}/uebermittlung",
        json={
            "uebermittlung_status": "UEBERMITTELT",
            "umgebung": "ANNAHMETEST",
            "dienst": "EudrSubmissionClientV3",
        },
        headers=kopf(HAUS_A),
    )
    assert antwort.status_code == 200, antwort.text
    assert antwort.json()["uebermittlung_umgebung"] == "ANNAHMETEST"

    stand = client.get(f"{REGISTER}/status", headers=kopf(HAUS_A)).json()
    assert stand["erklaerungen_nur_annahmetest"] == 1
    # Und sie gilt weiter als nicht uebermittelt.
    assert stand["erklaerungen_nicht_uebermittelt"] == 1


def test_die_datenbank_haelt_die_umgebungspflicht(engine):
    from sqlalchemy import text
    from sqlalchemy.exc import IntegrityError

    with pytest.raises(IntegrityError):
        with engine.begin() as v:
            v.execute(
                text(
                    f"INSERT INTO {ERKLAERUNGEN} (id, tenant_id, betreiber_name, "
                    " betreiber_adresse, rohstoff, hs_code, warenbeschreibung, "
                    " menge_netto_kg, produktionsland, produktion_von, produktion_bis, "
                    " lieferant_name, referenznummer, uebermittlung_status, uebermittelt_am) "
                    "VALUES (:id, :t, 'X', 'Y', 'SOJA', '230400', 'Z', 1, 'BR', "
                    "        '2026-01-01', '2026-02-01', 'L', 'REF-DB-UMG', "
                    "        'UEBERMITTELT', NOW())"
                ),
                {"id": str(uuid.uuid4()), "t": HAUS_A},
            )


def test_eine_abweisung_braucht_einen_grund(client):
    erklaerung = _eingereichte_erklaerung(client, HAUS_A, "REF-UEB-2")
    ohne = client.post(
        f"{REGISTER}/{erklaerung['id']}/uebermittlung",
        json={"uebermittlung_status": "ABGEWIESEN"},
        headers=kopf(HAUS_A),
    )
    assert ohne.status_code == 422, ohne.text

    mit = client.post(
        f"{REGISTER}/{erklaerung['id']}/uebermittlung",
        json={
            "uebermittlung_status": "ABGEWIESEN",
            "fehler": "HS-Code nicht im Anhang I des Dienstes",
        },
        headers=kopf(HAUS_A),
    )
    assert mit.status_code == 200, mit.text
    assert mit.json()["uebermittlung_fehler"].startswith("HS-Code")


def test_ein_entwurf_wird_nicht_uebermittelt(client):
    angelegt = client.post(
        REGISTER,
        json={
            "betreiber_name": "X",
            "betreiber_adresse": "Y",
            "rohstoff": "HOLZ",
            "hs_code": "4407",
            "warenbeschreibung": "Schnittholz",
            "menge_netto_kg": 100.0,
            "produktionsland": "PL",
            "produktion_von": "2026-01-01",
            "produktion_bis": "2026-02-01",
            "lieferant_name": "L",
        },
        headers=kopf(HAUS_A),
    )
    antwort = client.post(
        f"{REGISTER}/{angelegt.json()['id']}/uebermittlung",
        json={"uebermittlung_status": "UEBERMITTELT", "referenznummer": "REF-X"},
        headers=kopf(HAUS_A),
    )
    assert antwort.status_code == 409, antwort.text


def test_der_stand_zeigt_was_nicht_draussen_ist(client):
    erklaerung = _eingereichte_erklaerung(client, HAUS_A, "REF-UEB-3")
    stand = client.get(f"{REGISTER}/status", headers=kopf(HAUS_A)).json()
    assert stand["erklaerungen_nicht_uebermittelt"] == 1
    assert stand["erklaerungen_abgewiesen"] == 0

    client.post(
        f"{REGISTER}/{erklaerung['id']}/uebermittlung",
        json={"uebermittlung_status": "UEBERMITTELT", "umgebung": "PRODUKTION"},
        headers=kopf(HAUS_A),
    )
    stand = client.get(f"{REGISTER}/status", headers=kopf(HAUS_A)).json()
    assert stand["erklaerungen_nicht_uebermittelt"] == 0


def test_die_datenbank_haelt_die_uebermittlungsbedingung(engine):
    """``UEBERMITTELT`` ohne Zeitpunkt und Referenznummer ist keine
    Uebermittlung."""
    from sqlalchemy import text
    from sqlalchemy.exc import IntegrityError

    with pytest.raises(IntegrityError):
        with engine.begin() as v:
            v.execute(
                text(
                    f"INSERT INTO {ERKLAERUNGEN} (id, tenant_id, betreiber_name, "
                    " betreiber_adresse, rohstoff, hs_code, warenbeschreibung, "
                    " menge_netto_kg, produktionsland, produktion_von, produktion_bis, "
                    " lieferant_name, uebermittlung_status) "
                    "VALUES (:id, :t, 'X', 'Y', 'SOJA', '230400', 'Z', 1, 'BR', "
                    "        '2026-01-01', '2026-02-01', 'L', 'UEBERMITTELT')"
                ),
                {"id": str(uuid.uuid4()), "t": HAUS_A},
            )


# 3 ── Herein: ist die zugekaufte Erklärung geprüft? ────────────────────────

def _mit_vorgelagerter(client, tenant: str, referenz: str, **vorgelagert) -> dict:
    eintrag = {"referenznummer": referenz}
    eintrag.update(vorgelagert)
    angelegt = client.post(
        REGISTER,
        json={
            "betreiber_name": "Landhandel Nord eG",
            "betreiber_adresse": "Hafenstrasse 1",
            "rohstoff": "SOJA",
            "hs_code": "230400",
            "warenbeschreibung": "Sojaschrot, zugekauft",
            "menge_netto_kg": 24000.0,
            "produktionsland": "BR",
            "produktion_von": "2026-02-01",
            "produktion_bis": "2026-04-30",
            "lieferant_name": "Importeur Hamburg GmbH",
            "vorgelagerte_erklaerungen": [eintrag],
        },
        headers=kopf(tenant),
    )
    assert angelegt.status_code == 201, angelegt.text
    return angelegt.json()


def test_eine_zugekaufte_nummer_ist_zuerst_ungeprueft(client):
    erklaerung = _mit_vorgelagerter(client, HAUS_A, "UP-REF-1")
    vorgelagert = erklaerung["vorgelagerte_erklaerungen"][0]
    assert vorgelagert["pruefung_status"] == "UNGEPRUEFT"
    assert vorgelagert["geprueft_am"] is None


def test_bestaetigung_aus_dem_eu_system_braucht_die_verifizierungsnummer(client):
    """Abgefragt wird eine Erklaerung ueber Referenz- **und**
    Verifizierungsnummer. Wer nur die Referenznummer hat, kann nicht
    bestaetigen."""
    erklaerung = _mit_vorgelagerter(client, HAUS_A, "UP-REF-2")
    vorgelagert = erklaerung["vorgelagerte_erklaerungen"][0]

    ohne = client.post(
        f"{REGISTER}/vorgelagerte/{vorgelagert['id']}/pruefung",
        json={"pruefung_status": "BESTAETIGT", "quelle": "EU_INFORMATIONSSYSTEM"},
        headers=kopf(HAUS_A),
    )
    assert ohne.status_code == 422, ohne.text

    mit = client.post(
        f"{REGISTER}/vorgelagerte/{vorgelagert['id']}/pruefung",
        json={
            "pruefung_status": "BESTAETIGT",
            "quelle": "EU_INFORMATIONSSYSTEM",
            "verifizierungsnummer": "UP-VER-2",
        },
        headers=kopf(HAUS_A),
    )
    assert mit.status_code == 200, mit.text
    daten = mit.json()
    assert daten["pruefung_status"] == "BESTAETIGT"
    assert daten["geprueft_am"] is not None
    assert daten["pruefung_quelle"] == "EU_INFORMATIONSSYSTEM"


def test_eine_nummer_die_es_nicht_gibt_wird_als_solche_festgehalten(client):
    erklaerung = _mit_vorgelagerter(client, HAUS_A, "UP-REF-3")
    vorgelagert = erklaerung["vorgelagerte_erklaerungen"][0]
    antwort = client.post(
        f"{REGISTER}/vorgelagerte/{vorgelagert['id']}/pruefung",
        json={
            "pruefung_status": "NICHT_GEFUNDEN",
            "quelle": "EU_INFORMATIONSSYSTEM",
            "hinweis": "Abfrage lieferte keine Erklaerung zu dieser Nummer",
        },
        headers=kopf(HAUS_A),
    )
    assert antwort.status_code == 200, antwort.text
    assert antwort.json()["pruefung_status"] == "NICHT_GEFUNDEN"


def test_ungepruefte_zukaeufe_sind_eine_liste(client):
    _mit_vorgelagerter(client, HAUS_A, "UP-REF-4")
    erklaerung = _mit_vorgelagerter(client, HAUS_A, "UP-REF-5", verifizierungsnummer="UP-VER-5")
    geprueft = erklaerung["vorgelagerte_erklaerungen"][0]
    client.post(
        f"{REGISTER}/vorgelagerte/{geprueft['id']}/pruefung",
        json={"pruefung_status": "BESTAETIGT", "quelle": "EU_INFORMATIONSSYSTEM"},
        headers=kopf(HAUS_A),
    )

    antwort = client.get(f"{REGISTER}/vorgelagerte/ungeprueft", headers=kopf(HAUS_A))
    assert antwort.status_code == 200, antwort.text
    assert [z["referenznummer"] for z in antwort.json()] == ["UP-REF-4"]

    stand = client.get(f"{REGISTER}/status", headers=kopf(HAUS_A)).json()
    assert stand["vorgelagerte_gesamt"] == 2
    assert stand["vorgelagerte_ungeprueft"] == 1


def test_fremde_vorgelagerte_erklaerung_ist_nicht_pruefbar(client, engine):
    from sqlalchemy import text

    erklaerung = _mit_vorgelagerter(client, HAUS_B, "UP-REF-FREMD")
    vorgelagert = erklaerung["vorgelagerte_erklaerungen"][0]

    antwort = client.post(
        f"{REGISTER}/vorgelagerte/{vorgelagert['id']}/pruefung",
        json={"pruefung_status": "BESTAETIGT", "quelle": "MANUELL"},
        headers=kopf(HAUS_A),
    )
    assert antwort.status_code == 404, antwort.text

    with engine.connect() as conn:
        stand = conn.execute(
            text(f"SELECT pruefung_status FROM {VORGELAGERT} WHERE id = :i"),
            {"i": vorgelagert["id"]},
        ).scalar()
    assert stand == "UNGEPRUEFT"


def test_die_datenbank_haelt_die_pruefbedingung(engine, client):
    """Geprueft heisst: es gibt einen Zeitpunkt und eine Quelle."""
    from sqlalchemy import text
    from sqlalchemy.exc import IntegrityError

    erklaerung = _mit_vorgelagerter(client, HAUS_A, "UP-REF-DB")
    with pytest.raises(IntegrityError):
        with engine.begin() as v:
            v.execute(
                text(
                    f"INSERT INTO {VORGELAGERT} (id, tenant_id, erklaerung_id, "
                    " referenznummer, pruefung_status) "
                    "VALUES (:id, :t, :e, 'UP-REF-DB-2', 'BESTAETIGT')"
                ),
                {"id": str(uuid.uuid4()), "t": HAUS_A, "e": erklaerung["id"]},
            )


# 4 ── Der alte Statusweg zeigt beide Richtungen ────────────────────────────

def test_compliance_eudr_zeigt_chargen_und_offene_mengen(client, engine):
    erklaerung = _eingereichte_erklaerung(client, HAUS_A, "REF-KOMPAKT-1")
    gedeckt = _charge(engine, HAUS_A, menge=100.0)
    _charge(engine, HAUS_A, menge=2500.0)
    client.post(
        f"{REGISTER}/{erklaerung['id']}/chargen",
        json={"lot_id": gedeckt, "menge_kg": 100.0},
        headers=kopf(HAUS_A),
    )

    daten = client.get("/api/v1/compliance/eudr", headers=kopf(HAUS_A)).json()
    assert daten["lots_relevant"] == 2
    assert daten["lots_covered"] == 1
    assert daten["lots_open"] == 1
    assert daten["open_quantity_kg"] == pytest.approx(2500.0)
    assert daten["status"] == "UNVOLLSTAENDIG"
