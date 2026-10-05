"""EUDR-Sorgfaltserklärung — der Nachweis, ohne den nichts in Verkehr darf.

Verordnung (EU) 2023/1115. `domain_compliance.eudr_due_diligence` legte keine
Migration an, und der Code kannte davon nur ein `COUNT(*) WHERE tenant_id` — zu
wenig, um eine Tabelle abzuleiten. Die Lücke ist jetzt nach dem Verordnungstext
geschlossen: Inhalt der Erklärung nach **Anhang II**, Informationspflichten nach
**Art. 9**, Risikobewertung und -minderung nach **Art. 10/11**, Referenz- und
Verifizierungsnummer nach **Art. 33**.

Der Befund, der es dringlich machte: `GET /api/v1/compliance/eudr` meldete bei
**jedem** Lesefehler `status: "KONFORM"` und `deforestation_risk: "NIEDRIG"` —
gelesen wurde `domain_inventory.lots`, eine Tabelle, die kein Migrationsstand
anlegt. Die Maske behauptete Konformität, die nie geprüft wurde.

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

HAUS_A = f"eudr-a-{uuid.uuid4().hex[:6]}"
HAUS_B = f"eudr-b-{uuid.uuid4().hex[:6]}"

REGISTER = "/api/v1/eudr/sorgfaltserklaerungen"
TABELLE = "domain_compliance.eudr_due_diligence"


@pytest.fixture(scope="module")
def engine():
    from sqlalchemy import create_engine, text

    try:
        motor = create_engine(DB_URL)
        with motor.connect() as conn:
            vorhanden = conn.execute(
                text("SELECT to_regclass('domain_compliance.eudr_geolokationen')")
            ).scalar()
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank nicht erreichbar: {fehler}")
    if not vorhanden:
        pytest.skip("Migration eudr_sorgfaltserklaerung_20261001 nicht angewandt")
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
        # Geolokationen und vorgelagerte Erklaerungen haengen am Kopf (CASCADE).
        v.execute(
            text(f"DELETE FROM {TABELLE} WHERE tenant_id IN (:a, :b)"),
            {"a": HAUS_A, "b": HAUS_B},
        )


@pytest.fixture(autouse=True)
def sauber(engine):
    _aufraeumen(engine)
    yield
    _aufraeumen(engine)


def _rumpf(**felder) -> dict:
    basis = {
        "betreiber_name": "Landhandel Nord eG",
        "betreiber_adresse": "Hafenstrasse 1, 26789 Leer",
        "eori_nummer": "DE123456789012345",
        "rohstoff": "SOJA",
        "hs_code": "230400",
        "warenbeschreibung": "Sojaextraktionsschrot, 46 % Rohprotein",
        "menge_netto_kg": 26000.0,
        "produktionsland": "BR",
        "produktion_von": "2026-02-01",
        "produktion_bis": "2026-04-30",
        "lieferant_name": "Cooperativa Agricola Sul",
        "lieferant_email": "ddr@coop-sul.example",
        "nachweis_abholzungsfrei": True,
        "nachweis_abholzungsfrei_quelle": "Satellitenauswertung 2020-2026, Bericht SAT-551",
        "nachweis_rechtskonform": True,
        "nachweis_rechtskonform_quelle": "CAR-Registrierung und Flaechennutzungsnachweis",
        "geolokationen": [
            {
                "flurstueck_kennung": "CAR-123",
                "breitengrad": -13.1234,
                "laengengrad": -56.4321,
                "flaeche_ha": 3.5,
            }
        ],
    }
    basis.update(felder)
    return basis


def _anlegen(client, tenant: str, **felder) -> dict:
    antwort = client.post(REGISTER, json=_rumpf(**felder), headers=kopf(tenant))
    assert antwort.status_code == 201, antwort.text
    return antwort.json()


# 1 ── Anhang II: die Erklärung trägt, was sie tragen muss ───────────────────

def test_erklaerung_entsteht_als_entwurf_mit_allen_angaben(client):
    erklaerung = _anlegen(client, HAUS_A)

    assert erklaerung["status"] == "ENTWURF"
    assert erklaerung["eori_nummer"] == "DE123456789012345"
    assert erklaerung["rohstoff"] == "SOJA"
    assert erklaerung["hs_code"] == "230400"
    assert erklaerung["produktionsland"] == "BR"
    assert erklaerung["menge_netto_kg"] == pytest.approx(26000.0)
    # Art. 9: die Geolokation gehoert zur Erklaerung, nicht daneben.
    assert len(erklaerung["geolokationen"]) == 1
    assert erklaerung["geolokationen"][0]["flurstueck_kennung"] == "CAR-123"
    # Noch nicht bewertet, also auch nicht einreichbar.
    assert erklaerung["risikostufe"] is None
    assert erklaerung["referenznummer"] is None


def test_vorgelagerte_erklaerungen_werden_mitgefuehrt(client):
    """Anhang II Nr. 4: Wer sich auf vorgelagerte Erklaerungen stuetzt, fuehrt
    deren Referenznummern mit."""
    erklaerung = _anlegen(
        client,
        HAUS_A,
        vorgelagerte_erklaerungen=[
            {
                "referenznummer": "EUDR-REF-UPSTREAM-1",
                "verifizierungsnummer": "VER-1",
                "lieferant_name": "Cooperativa Agricola Sul",
            }
        ],
    )
    assert [v["referenznummer"] for v in erklaerung["vorgelagerte_erklaerungen"]] == [
        "EUDR-REF-UPSTREAM-1"
    ]


@pytest.mark.parametrize("rohstoff", ["SOJA", "OELPALME", "HOLZ", "RIND", "KAKAO", "KAFFEE", "KAUTSCHUK"])
def test_die_sieben_rohstoffe_des_anhangs_i(client, rohstoff):
    erklaerung = _anlegen(client, HAUS_A, rohstoff=rohstoff)
    assert erklaerung["rohstoff"] == rohstoff


def test_unbekannter_rohstoff_wird_abgewiesen(client):
    antwort = client.post(
        REGISTER, json=_rumpf(rohstoff="WEIZEN"), headers=kopf(HAUS_A)
    )
    assert antwort.status_code == 422, antwort.text
    assert "Anhang I" in antwort.text


def test_produktionszeitraum_endet_nicht_vor_seinem_beginn(client):
    antwort = client.post(
        REGISTER,
        json=_rumpf(produktion_von="2026-04-30", produktion_bis="2026-02-01"),
        headers=kopf(HAUS_A),
    )
    assert antwort.status_code == 422, antwort.text


# 2 ── Art. 9: Flurstücke über vier Hektar nur als Polygon ───────────────────

def test_flurstueck_ueber_vier_hektar_braucht_ein_polygon(client):
    antwort = client.post(
        REGISTER,
        json=_rumpf(
            geolokationen=[
                {"breitengrad": -13.0, "laengengrad": -56.0, "flaeche_ha": 12.5}
            ]
        ),
        headers=kopf(HAUS_A),
    )
    assert antwort.status_code == 422, antwort.text
    assert "Polygon" in antwort.text


def test_flurstueck_ueber_vier_hektar_mit_polygon_geht(client):
    erklaerung = _anlegen(
        client,
        HAUS_A,
        geolokationen=[
            {
                "flurstueck_kennung": "CAR-GROSS",
                "breitengrad": -13.0,
                "laengengrad": -56.0,
                "flaeche_ha": 12.5,
                "polygon": {
                    "type": "Polygon",
                    "coordinates": [
                        [[-56.0, -13.0], [-56.1, -13.0], [-56.1, -13.1], [-56.0, -13.0]]
                    ],
                },
            }
        ],
    )
    ort = erklaerung["geolokationen"][0]
    assert ort["flaeche_ha"] == pytest.approx(12.5)
    assert ort["polygon"]["type"] == "Polygon"


def test_die_datenbank_haelt_die_polygonpflicht(engine):
    """Auch ein Weg, der die Pruefung im Dienst umgeht, kommt nicht durch."""
    from sqlalchemy import text
    from sqlalchemy.exc import IntegrityError

    kopf_id = str(uuid.uuid4())
    with engine.begin() as v:
        v.execute(
            text(
                f"INSERT INTO {TABELLE} (id, tenant_id, betreiber_name, betreiber_adresse, "
                " rohstoff, hs_code, warenbeschreibung, menge_netto_kg, produktionsland, "
                " produktion_von, produktion_bis, lieferant_name) "
                "VALUES (:id, :t, 'X', 'Y', 'SOJA', '230400', 'Z', 1, 'BR', "
                "        '2026-01-01', '2026-02-01', 'L')"
            ),
            {"id": kopf_id, "t": HAUS_A},
        )
    with pytest.raises(IntegrityError):
        with engine.begin() as v:
            v.execute(
                text(
                    "INSERT INTO domain_compliance.eudr_geolokationen "
                    "(id, tenant_id, erklaerung_id, breitengrad, laengengrad, flaeche_ha) "
                    "VALUES (:id, :t, :e, -13.0, -56.0, 9.9)"
                ),
                {"id": str(uuid.uuid4()), "t": HAUS_A, "e": kopf_id},
            )


# 3 ── Art. 10/11: Risikobewertung und Minderung ─────────────────────────────

def test_nicht_vernachlaessigbares_risiko_braucht_minderungsmassnahmen(client):
    erklaerung = _anlegen(client, HAUS_A)
    antwort = client.post(
        f"{REGISTER}/{erklaerung['id']}/risikobewertung",
        json={"risikostufe": "NICHT_VERNACHLAESSIGBAR", "bewertet_durch": "QS"},
        headers=kopf(HAUS_A),
    )
    assert antwort.status_code == 422, antwort.text
    assert "Art. 11" in antwort.text


def test_risikobewertung_wird_festgehalten(client):
    erklaerung = _anlegen(client, HAUS_A)
    antwort = client.post(
        f"{REGISTER}/{erklaerung['id']}/risikobewertung",
        json={"risikostufe": "VERNACHLAESSIGBAR", "bewertet_durch": "QS Nord"},
        headers=kopf(HAUS_A),
    )
    assert antwort.status_code == 200, antwort.text
    bewertet = antwort.json()
    assert bewertet["risikostufe"] == "VERNACHLAESSIGBAR"
    assert bewertet["risikobewertung_am"] is not None
    assert bewertet["risikobewertung_durch"] == "QS Nord"


# 4 ── Art. 3/4: eingereicht nur, was eingereicht werden darf ────────────────

def test_ohne_risikobewertung_keine_einreichung(client):
    erklaerung = _anlegen(client, HAUS_A)
    antwort = client.post(
        f"{REGISTER}/{erklaerung['id']}/einreichen",
        json={
            "referenznummer": "EUDR-REF-1",
            "erklaerung_durch_name": "A. Meyer",
            "erklaerung_durch_funktion": "Geschaeftsfuehrung",
        },
        headers=kopf(HAUS_A),
    )
    assert antwort.status_code == 409, antwort.text
    assert "Art. 10" in antwort.text


def test_bei_nicht_vernachlaessigbarem_risiko_keine_einreichung(client):
    erklaerung = _anlegen(client, HAUS_A)
    bewertung = client.post(
        f"{REGISTER}/{erklaerung['id']}/risikobewertung",
        json={
            "risikostufe": "NICHT_VERNACHLAESSIGBAR",
            "bewertet_durch": "QS",
            "minderungsmassnahmen": "Zusaetzliche Satellitenauswertung beauftragt",
        },
        headers=kopf(HAUS_A),
    )
    assert bewertung.status_code == 200, bewertung.text

    antwort = client.post(
        f"{REGISTER}/{erklaerung['id']}/einreichen",
        json={
            "referenznummer": "EUDR-REF-2",
            "erklaerung_durch_name": "A. Meyer",
            "erklaerung_durch_funktion": "Geschaeftsfuehrung",
        },
        headers=kopf(HAUS_A),
    )
    assert antwort.status_code == 409, antwort.text


def test_ohne_nachweise_keine_einreichung(client):
    erklaerung = _anlegen(
        client, HAUS_A, nachweis_abholzungsfrei=False, nachweis_rechtskonform=True
    )
    client.post(
        f"{REGISTER}/{erklaerung['id']}/risikobewertung",
        json={"risikostufe": "VERNACHLAESSIGBAR", "bewertet_durch": "QS"},
        headers=kopf(HAUS_A),
    )
    antwort = client.post(
        f"{REGISTER}/{erklaerung['id']}/einreichen",
        json={
            "referenznummer": "EUDR-REF-3",
            "erklaerung_durch_name": "A. Meyer",
            "erklaerung_durch_funktion": "Geschaeftsfuehrung",
        },
        headers=kopf(HAUS_A),
    )
    assert antwort.status_code == 409, antwort.text
    assert "abholzungsfrei" in antwort.text


def _einreichbar(client, tenant: str, referenz: str) -> dict:
    erklaerung = _anlegen(client, tenant)
    client.post(
        f"{REGISTER}/{erklaerung['id']}/risikobewertung",
        json={"risikostufe": "VERNACHLAESSIGBAR", "bewertet_durch": "QS"},
        headers=kopf(tenant),
    )
    antwort = client.post(
        f"{REGISTER}/{erklaerung['id']}/einreichen",
        json={
            "referenznummer": referenz,
            "verifizierungsnummer": "VER-" + referenz,
            "erklaerung_durch_name": "A. Meyer",
            "erklaerung_durch_funktion": "Geschaeftsfuehrung",
        },
        headers=kopf(tenant),
    )
    assert antwort.status_code == 200, antwort.text
    return antwort.json()


def test_einreichung_haelt_referenz_und_unterzeichnung_fest(client):
    eingereicht = _einreichbar(client, HAUS_A, "EUDR-REF-OK-1")
    assert eingereicht["status"] == "EINGEREICHT"
    assert eingereicht["referenznummer"] == "EUDR-REF-OK-1"
    assert eingereicht["verifizierungsnummer"] == "VER-EUDR-REF-OK-1"
    assert eingereicht["eingereicht_am"] is not None
    # Anhang II Nr. 6: Name und Funktion der unterzeichnenden Person.
    assert eingereicht["erklaerung_durch_name"] == "A. Meyer"
    assert eingereicht["erklaerung_durch_funktion"] == "Geschaeftsfuehrung"


def test_zweimal_einreichen_wird_abgewiesen(client):
    eingereicht = _einreichbar(client, HAUS_A, "EUDR-REF-OK-2")
    nochmal = client.post(
        f"{REGISTER}/{eingereicht['id']}/einreichen",
        json={
            "referenznummer": "EUDR-REF-OK-2b",
            "erklaerung_durch_name": "A. Meyer",
            "erklaerung_durch_funktion": "Geschaeftsfuehrung",
        },
        headers=kopf(HAUS_A),
    )
    assert nochmal.status_code == 409, nochmal.text


def test_eine_eingereichte_erklaerung_wird_nicht_nachtraeglich_veraendert(client):
    eingereicht = _einreichbar(client, HAUS_A, "EUDR-REF-OK-3")
    nachtrag = client.post(
        f"{REGISTER}/{eingereicht['id']}/geolokationen",
        json={"breitengrad": -12.0, "laengengrad": -55.0, "flaeche_ha": 1.0},
        headers=kopf(HAUS_A),
    )
    assert nachtrag.status_code == 409, nachtrag.text

    bewertung = client.post(
        f"{REGISTER}/{eingereicht['id']}/risikobewertung",
        json={"risikostufe": "VERNACHLAESSIGBAR", "bewertet_durch": "QS"},
        headers=kopf(HAUS_A),
    )
    assert bewertung.status_code == 409, bewertung.text


def test_die_datenbank_haelt_die_einreichungsbedingung(engine):
    """Art. 3/4 — auch an der Datenbank, nicht nur im Dienst."""
    from sqlalchemy import text
    from sqlalchemy.exc import IntegrityError

    with pytest.raises(IntegrityError):
        with engine.begin() as v:
            v.execute(
                text(
                    f"INSERT INTO {TABELLE} (id, tenant_id, betreiber_name, betreiber_adresse, "
                    " rohstoff, hs_code, warenbeschreibung, menge_netto_kg, produktionsland, "
                    " produktion_von, produktion_bis, lieferant_name, status) "
                    "VALUES (:id, :t, 'X', 'Y', 'SOJA', '230400', 'Z', 1, 'BR', "
                    "        '2026-01-01', '2026-02-01', 'L', 'EINGEREICHT')"
                ),
                {"id": str(uuid.uuid4()), "t": HAUS_A},
            )


def test_eine_referenznummer_gibt_es_nur_einmal(client, engine):
    """Art. 33: Die Nummer stammt aus dem EU-System und ist dort eindeutig."""
    from sqlalchemy import text

    _einreichbar(client, HAUS_A, "EUDR-REF-EINMALIG")

    zweite = _anlegen(client, HAUS_B)
    client.post(
        f"{REGISTER}/{zweite['id']}/risikobewertung",
        json={"risikostufe": "VERNACHLAESSIGBAR", "bewertet_durch": "QS"},
        headers=kopf(HAUS_B),
    )
    antwort = client.post(
        f"{REGISTER}/{zweite['id']}/einreichen",
        json={
            "referenznummer": "EUDR-REF-EINMALIG",
            "erklaerung_durch_name": "B. Jansen",
            "erklaerung_durch_funktion": "Einkauf",
        },
        headers=kopf(HAUS_B),
    )
    assert antwort.status_code == 409, antwort.text

    with engine.connect() as conn:
        anzahl = conn.execute(
            text(f"SELECT count(*) FROM {TABELLE} WHERE referenznummer = :r"),
            {"r": "EUDR-REF-EINMALIG"},
        ).scalar()
    assert anzahl == 1


# 5 ── Mandantentrennung ────────────────────────────────────────────────────

def test_fremde_erklaerung_ist_nicht_lesbar(client):
    erklaerung = _anlegen(client, HAUS_A)
    antwort = client.get(f"{REGISTER}/{erklaerung['id']}", headers=kopf(HAUS_B))
    assert antwort.status_code == 404, antwort.text
    assert "Cooperativa" not in antwort.text


def test_liste_zeigt_nur_eigene_erklaerungen(client):
    _anlegen(client, HAUS_A)
    _anlegen(client, HAUS_B)
    eigen = client.get(REGISTER, headers=kopf(HAUS_A))
    assert eigen.status_code == 200, eigen.text
    assert len(eigen.json()) == 1


def test_fremde_erklaerung_ist_nicht_bewertbar(client, engine):
    from sqlalchemy import text

    erklaerung = _anlegen(client, HAUS_A)
    antwort = client.post(
        f"{REGISTER}/{erklaerung['id']}/risikobewertung",
        json={"risikostufe": "VERNACHLAESSIGBAR", "bewertet_durch": "fremd"},
        headers=kopf(HAUS_B),
    )
    assert antwort.status_code == 404, antwort.text

    with engine.connect() as conn:
        stufe = conn.execute(
            text(f"SELECT risikostufe FROM {TABELLE} WHERE id = :i"),
            {"i": erklaerung["id"]},
        ).scalar()
    assert stufe is None


# 6 ── Der Registerstand behauptet nichts ───────────────────────────────────

def test_leeres_register_ist_nicht_konform(client):
    """"Nichts erfasst" ist kein Nachweis — Art. 3/4 verbietet das
    Inverkehrbringen ohne Erklaerung."""
    antwort = client.get(f"{REGISTER}/status", headers=kopf(HAUS_A))
    assert antwort.status_code == 200, antwort.text
    daten = antwort.json()
    assert daten["status"] == "OHNE_ERKLAERUNG"
    assert daten["erklaerungen_gesamt"] == 0


def test_entwurf_allein_ist_unvollstaendig(client):
    _anlegen(client, HAUS_A)
    antwort = client.get(f"{REGISTER}/status", headers=kopf(HAUS_A))
    daten = antwort.json()
    assert daten["status"] == "UNVOLLSTAENDIG"
    assert daten["ohne_risikobewertung"] == 1


def test_riskante_erklaerung_macht_den_stand_kritisch(client):
    erklaerung = _anlegen(client, HAUS_A)
    client.post(
        f"{REGISTER}/{erklaerung['id']}/risikobewertung",
        json={
            "risikostufe": "NICHT_VERNACHLAESSIGBAR",
            "bewertet_durch": "QS",
            "minderungsmassnahmen": "Lieferant ausgesetzt",
        },
        headers=kopf(HAUS_A),
    )
    antwort = client.get(f"{REGISTER}/status", headers=kopf(HAUS_A))
    assert antwort.json()["status"] == "KRITISCH"


def test_eingereichte_erklaerung_ist_konform(client):
    _einreichbar(client, HAUS_A, "EUDR-REF-STAND")
    antwort = client.get(f"{REGISTER}/status", headers=kopf(HAUS_A))
    daten = antwort.json()
    assert daten["status"] == "KONFORM"
    assert daten["erklaerungen_eingereicht"] == 1
    assert daten["produktionslaender"] == ["BR"]
    assert daten["rohstoffe"] == ["SOJA"]


# 7 ── Der alte Statusweg meldet nicht mehr grün ────────────────────────────

def test_compliance_eudr_meldet_kein_konform_ohne_erklaerung(client):
    """Vorher: `status: "KONFORM"`, `deforestation_risk: "NIEDRIG"` — aus einem
    `except`, weil `domain_inventory.lots` nicht existiert."""
    antwort = client.get("/api/v1/compliance/eudr", headers=kopf(HAUS_A))
    assert antwort.status_code == 200, antwort.text
    daten = antwort.json()
    assert daten["status"] == "OHNE_ERKLAERUNG"
    assert daten["deforestation_risk"] != "NIEDRIG"
    # Die chargenbezogene Kennzeichnung ist seit
    # eudr_chargenkennzeichnung_20261001 umgesetzt: Statt des Platzhalters
    # stehen hier Zahlen — ohne Charge sind sie null, und das ist wahr.
    assert daten["lots_relevant"] == 0
    assert daten["lots_open"] == 0


def test_compliance_eudr_unbewertet_ist_kein_niedriges_risiko(client):
    _anlegen(client, HAUS_A)
    daten = client.get("/api/v1/compliance/eudr", headers=kopf(HAUS_A)).json()
    assert daten["deforestation_risk"] == "UNBEKANNT"
    assert daten["statements_unassessed"] == 1


def test_compliance_eudr_liest_nicht_mehr_aus_dem_abfrageparameter(client):
    """Der Mandant kam aus `?tenant_id=` mit Rueckfall "default"."""
    _anlegen(client, HAUS_A)
    daten = client.get(
        f"/api/v1/compliance/eudr?tenant_id={HAUS_B}", headers=kopf(HAUS_A)
    ).json()
    assert daten["due_diligence_statements"] == 1


def test_stoerung_ist_kein_gruener_stand(client, engine):
    """Die Spalte, nach der gefiltert wird, wird kurzzeitig umbenannt."""
    from sqlalchemy import text

    with engine.begin() as v:
        v.execute(text(f"ALTER TABLE {TABELLE} RENAME COLUMN tenant_id TO tenant_id_weg"))
    try:
        for pfad in (f"{REGISTER}/status", "/api/v1/compliance/eudr", REGISTER):
            antwort = client.get(pfad, headers=kopf(HAUS_A))
            assert antwort.status_code == 503, f"{pfad}: {antwort.text}"
            assert "KONFORM" not in antwort.text
    finally:
        with engine.begin() as v:
            v.execute(
                text(f"ALTER TABLE {TABELLE} RENAME COLUMN tenant_id_weg TO tenant_id")
            )
