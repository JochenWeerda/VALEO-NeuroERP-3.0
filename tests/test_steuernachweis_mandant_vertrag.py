"""Steuerliche Nachweise gehören einem Haus.

`domain_compliance.gelangensbestaetigung` und `.intrastat_meldungen` legte keine
Migration an, und beide Module nahmen `get_tenant_id` entgegen und **benutzten
ihn nicht** — kein einziger Filter.

Was ein fremdes Haus damit konnte:

- die Gelangensbestätigungen **aller** Häuser lesen, mit Kundennummer,
  Empfängername und der **USt-IdNr.** des Empfängers,
- die Fälligkeitsliste ebenso — und bei einem Lesefehler kam `[]`, also
  „nichts nachzufassen",
- die **Intrastat-Meldung eines fremden Hauses löschen**,
- einen Intrastat-Export ziehen, der die Zeilen **aller** Häuser enthält.

Rechtsfolge, nicht Schönheitsfehler: Ohne Gelangensbestätigung entfällt die
Steuerfreiheit der innergemeinschaftlichen Lieferung (§ 6a UStG, § 17a UStDV).
Und ein Intrastat-Export mit fremden Zeilen ist eine falsche Meldung an das
Statistische Bundesamt.

Geprüft wird gegen die gemeinsame, vorhandene Prüfstand-Datenbank. Die Testzeilen
tragen eigene Mandantenkennungen und werden hinterher entfernt.
"""

from __future__ import annotations

import os
import uuid
from datetime import date, timedelta

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

HAUS_A = f"stn-a-{uuid.uuid4().hex[:6]}"
HAUS_B = f"stn-b-{uuid.uuid4().hex[:6]}"
ZEITRAUM = "2026-08"

GB = "domain_compliance.gelangensbestaetigung"
INTRA = "domain_compliance.intrastat_meldungen"


@pytest.fixture(scope="module")
def engine():
    from sqlalchemy import create_engine, text

    try:
        motor = create_engine(DB_URL)
        with motor.connect() as conn:
            vorhanden = conn.execute(text(f"SELECT to_regclass('{GB}')")).scalar()
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank nicht erreichbar: {fehler}")
    if not vorhanden:
        pytest.skip("Migration steuernachweis_mandant_20261001 nicht angewandt")
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
        for tabelle in (GB, INTRA):
            v.execute(
                text(f"DELETE FROM {tabelle} WHERE tenant_id IN (:a, :b)"),
                {"a": HAUS_A, "b": HAUS_B},
            )


@pytest.fixture(autouse=True)
def sauber(engine):
    _aufraeumen(engine)
    yield
    _aufraeumen(engine)


# ── Gelangensbestätigung ────────────────────────────────────────────────────

def _gb_anlegen(client, tenant: str, lieferschein: str = "LS-1") -> dict:
    antwort = client.post(
        "/api/v1/gelangensbestaetigung",
        json={
            "lieferschein_nr": lieferschein,
            "rechnung_nr": "RE-1",
            "kunde_nr": "KD-7",
            "bestimmungsland_code": "NL",
            "warenwert_eur": 24500.0,
            "versanddatum": date.today().isoformat(),
            "empfaenger_name": "De Boer Handel BV",
            "empfaenger_ust_id_nr": "NL123456789B01",
        },
        headers=kopf(tenant),
    )
    assert antwort.status_code == 201, antwort.text
    return antwort.json()


def test_gelangensbestaetigung_gehoert_dem_anlegenden_haus(client, engine):
    from sqlalchemy import text

    angelegt = _gb_anlegen(client, HAUS_A)
    with engine.connect() as conn:
        besitzer = conn.execute(
            text(f"SELECT tenant_id FROM {GB} WHERE id = :i"), {"i": angelegt["id"]}
        ).scalar()
    assert besitzer == HAUS_A


def test_liste_zeigt_keine_fremde_ust_id(client):
    _gb_anlegen(client, HAUS_A)

    fremd = client.get("/api/v1/gelangensbestaetigung", headers=kopf(HAUS_B))
    assert fremd.status_code == 200, fremd.text
    assert fremd.json() == []
    assert "NL123456789B01" not in fremd.text
    assert "De Boer" not in fremd.text

    eigen = client.get("/api/v1/gelangensbestaetigung", headers=kopf(HAUS_A))
    assert eigen.status_code == 200, eigen.text
    assert len(eigen.json()) == 1


def test_faellige_liste_zeigt_nur_eigene(client, engine):
    """Die Liste, die sagt, was nachzufassen ist."""
    from sqlalchemy import text

    angelegt = _gb_anlegen(client, HAUS_A)
    # Erinnerung in die Vergangenheit legen, damit der Nachweis faellig ist.
    with engine.begin() as v:
        v.execute(
            text(f"UPDATE {GB} SET erinnerung_am = :tag WHERE id = :i"),
            {"tag": date.today() - timedelta(days=3), "i": angelegt["id"]},
        )

    eigen = client.get("/api/v1/gelangensbestaetigung/faellig", headers=kopf(HAUS_A))
    assert eigen.status_code == 200, eigen.text
    assert [z["lieferschein_nr"] for z in eigen.json()] == ["LS-1"]

    fremd = client.get("/api/v1/gelangensbestaetigung/faellig", headers=kopf(HAUS_B))
    assert fremd.status_code == 200, fremd.text
    assert fremd.json() == []


def test_fremder_nachweis_ist_nicht_bestaetigbar(client, engine):
    from sqlalchemy import text

    angelegt = _gb_anlegen(client, HAUS_A)
    antwort = client.post(
        f"/api/v1/gelangensbestaetigung/{angelegt['id']}/bestaetigen",
        headers=kopf(HAUS_B),
    )
    assert antwort.status_code == 404, antwort.text

    with engine.connect() as conn:
        zeile = conn.execute(
            text(f"SELECT status, erhalten_am FROM {GB} WHERE id = :i"),
            {"i": angelegt["id"]},
        ).mappings().one()
    assert zeile["status"] == "AUSSTEHEND"
    assert zeile["erhalten_am"] is None


def test_eigener_nachweis_wird_bestaetigt(client, engine):
    from sqlalchemy import text

    angelegt = _gb_anlegen(client, HAUS_A)
    antwort = client.post(
        f"/api/v1/gelangensbestaetigung/{angelegt['id']}/bestaetigen",
        headers=kopf(HAUS_A),
    )
    assert antwort.status_code == 200, antwort.text

    with engine.connect() as conn:
        zeile = conn.execute(
            text(f"SELECT status, erhalten_am FROM {GB} WHERE id = :i"),
            {"i": angelegt["id"]},
        ).mappings().one()
    assert zeile["status"] == "ERHALTEN"
    assert zeile["erhalten_am"] is not None


def test_fremde_mahnung_gibt_kein_token_heraus(client):
    """Das Token ist der Link, mit dem der Empfaenger bestaetigt."""
    angelegt = _gb_anlegen(client, HAUS_A)
    antwort = client.post(
        f"/api/v1/gelangensbestaetigung/{angelegt['id']}/mahnung",
        headers=kopf(HAUS_B),
    )
    assert antwort.status_code == 404, antwort.text


def test_erhalten_ohne_zeitpunkt_ist_nicht_speicherbar(engine):
    """Ein erhaltener Nachweis braucht den Zeitpunkt — das ist das Beweisstueck."""
    from sqlalchemy import text
    from sqlalchemy.exc import IntegrityError

    with pytest.raises(IntegrityError):
        with engine.begin() as v:
            v.execute(
                text(
                    f"INSERT INTO {GB} (id, tenant_id, lieferschein_nr, kunde_nr, "
                    " bestimmungsland_code, warenwert_eur, versanddatum, "
                    " empfaenger_name, status, token) "
                    "VALUES (:id, :t, 'LS-X', 'KD-1', 'NL', 100, CURRENT_DATE, "
                    "        'X', 'ERHALTEN', :tok)"
                ),
                {"id": str(uuid.uuid4()), "t": HAUS_A, "tok": uuid.uuid4().hex},
            )


def test_zwei_nachweise_zum_selben_lieferschein_sind_abgewiesen(client):
    _gb_anlegen(client, HAUS_A, lieferschein="LS-DOPPELT")
    zweiter = client.post(
        "/api/v1/gelangensbestaetigung",
        json={
            "lieferschein_nr": "LS-DOPPELT",
            "rechnung_nr": "RE-2",
            "kunde_nr": "KD-7",
            "bestimmungsland_code": "NL",
            "warenwert_eur": 100.0,
            "versanddatum": date.today().isoformat(),
            "empfaenger_name": "Zweiter",
            "empfaenger_ust_id_nr": "NL999999999B01",
        },
        headers=kopf(HAUS_A),
    )
    assert zweiter.status_code == 409, zweiter.text  # Dublette; bis 08.10.2026 faelschlich 503

    # Ein anderes Haus darf denselben Lieferscheinnummernkreis benutzen.
    anderes = _gb_anlegen(client, HAUS_B, lieferschein="LS-DOPPELT")
    assert anderes["id"]


# ── Intrastat ───────────────────────────────────────────────────────────────

def _intrastat_anlegen(client, tenant: str, cn8: str = "10019900") -> dict:
    antwort = client.post(
        "/api/v1/intrastat/meldungen",
        json={
            "meldezeitraum": ZEITRAUM,
            "meldungsart": "VERSAND",
            "cn8_warennummer": cn8,
            "ursprungsland": "DE",
            "bestimmungsland": "NL",
            "statistischer_wert_eur": 18000.0,
            "nettomasse_kg": 24000.0,
            "menge": 24.0,
            "mengeneinheit": "t",
            "geschaeftsvorgang_code": "11",
        },
        headers=kopf(tenant),
    )
    assert antwort.status_code == 201, antwort.text
    return antwort.json()


def test_meldenummer_laeuft_je_haus(client):
    """Vorher zaehlte `COUNT(*)` ueber alle Haeuser: Das zweite Haus begann dort,
    wo das erste stand."""
    a1 = _intrastat_anlegen(client, HAUS_A, cn8="10019900")
    b1 = _intrastat_anlegen(client, HAUS_B, cn8="10019900")
    a2 = _intrastat_anlegen(client, HAUS_A, cn8="12051090")

    assert a1["meldenummer"].endswith("-00001")
    assert b1["meldenummer"].endswith("-00001")
    assert a2["meldenummer"].endswith("-00002")


def test_liste_zeigt_nur_eigene_meldungen(client):
    _intrastat_anlegen(client, HAUS_A)
    _intrastat_anlegen(client, HAUS_B)

    eigen = client.get("/api/v1/intrastat/meldungen", headers=kopf(HAUS_A))
    assert eigen.status_code == 200, eigen.text
    assert len(eigen.json()) == 1


def test_fremde_meldung_ist_nicht_loeschbar(client, engine):
    from sqlalchemy import text

    fremd = _intrastat_anlegen(client, HAUS_B)
    antwort = client.delete(
        f"/api/v1/intrastat/meldungen/{fremd['id']}", headers=kopf(HAUS_A)
    )
    assert antwort.status_code == 404, antwort.text

    with engine.connect() as conn:
        noch_da = conn.execute(
            text(f"SELECT count(*) FROM {INTRA} WHERE id = :i"), {"i": fremd["id"]}
        ).scalar()
    assert noch_da == 1


def test_fremde_meldung_ist_nicht_aenderbar(client, engine):
    from sqlalchemy import text

    fremd = _intrastat_anlegen(client, HAUS_B)
    antwort = client.put(
        f"/api/v1/intrastat/meldungen/{fremd['id']}",
        json={"statistischer_wert_eur": 1.0},
        headers=kopf(HAUS_A),
    )
    # Die Antwort darf behaupten, was sie will — entscheidend ist die Tabelle.
    assert antwort.status_code in (200, 404), antwort.text
    with engine.connect() as conn:
        wert = conn.execute(
            text(f"SELECT statistischer_wert_eur FROM {INTRA} WHERE id = :i"),
            {"i": fremd["id"]},
        ).scalar()
    assert float(wert) == pytest.approx(18000.0)


def test_export_enthaelt_keine_fremden_zeilen(client):
    """Ein Export mit fremden Zeilen ist eine falsche Meldung an das
    Statistische Bundesamt."""
    _intrastat_anlegen(client, HAUS_A, cn8="10019900")
    _intrastat_anlegen(client, HAUS_B, cn8="12051090")

    antwort = client.post(
        f"/api/v1/intrastat/meldungen/{ZEITRAUM}/export-csv", headers=kopf(HAUS_A)
    )
    assert antwort.status_code == 200, antwort.text
    text_csv = antwort.text
    assert "10019900" in text_csv
    assert "12051090" not in text_csv
    # Kopfzeile plus genau eine Datenzeile.
    assert len([z for z in text_csv.strip().splitlines() if z]) == 2


def test_zusammenfassung_zaehlt_nur_das_eigene_haus(client):
    _intrastat_anlegen(client, HAUS_A)
    _intrastat_anlegen(client, HAUS_B)

    antwort = client.get(
        f"/api/v1/intrastat/meldungen/{ZEITRAUM}/zusammenfassung", headers=kopf(HAUS_A)
    )
    assert antwort.status_code == 200, antwort.text
    daten = antwort.json()
    assert len(daten["positionen"]) == 1
    assert daten["total_wert_eur"] == pytest.approx(18000.0)


def test_ein_unmoeglicher_meldezeitraum_wird_abgewiesen(engine):
    from sqlalchemy import text
    from sqlalchemy.exc import IntegrityError

    with pytest.raises(IntegrityError):
        with engine.begin() as v:
            v.execute(
                text(
                    f"INSERT INTO {INTRA} (id, tenant_id, meldenummer, meldezeitraum, "
                    " meldungsart, cn8_warennummer, statistischer_wert_eur, nettomasse_kg) "
                    "VALUES (:id, :t, 'INT-X', 'August', 'VERSAND', '10019900', 1, 1)"
                ),
                {"id": str(uuid.uuid4()), "t": HAUS_A},
            )


# ── Störung ist kein leeres Ergebnis ────────────────────────────────────────

@pytest.mark.parametrize(
    "pfad,tabelle,spalte",
    [
        ("/api/v1/gelangensbestaetigung", GB, "tenant_id"),
        ("/api/v1/gelangensbestaetigung/faellig", GB, "tenant_id"),
        ("/api/v1/intrastat/meldungen", INTRA, "tenant_id"),
    ],
)
def test_stoerung_ist_kein_leeres_ergebnis(client, engine, pfad, tabelle, spalte):
    """Die Spalte, nach der gefiltert wird, wird kurzzeitig umbenannt.

    Vorher gaben diese Wege bei jedem Lesefehler `[]` zurueck — bei der
    Faelligkeitsliste heisst das "nichts nachzufassen", mit Steuerwirkung.
    """
    from sqlalchemy import text

    with engine.begin() as v:
        v.execute(text(f"ALTER TABLE {tabelle} RENAME COLUMN {spalte} TO {spalte}_weg"))
    try:
        antwort = client.get(pfad, headers=kopf(HAUS_A))
        assert antwort.status_code == 503, antwort.text
    finally:
        with engine.begin() as v:
            v.execute(
                text(f"ALTER TABLE {tabelle} RENAME COLUMN {spalte}_weg TO {spalte}")
            )
