"""Das zentrale Kontraktregister — der ganze Lebenszyklus auf einem frischen Stand.

`domain_contracts.contracts`, `.contract_versions` und `.contract_obligations`
legte keine Migration an. Auf einer frischen Installation meldete deshalb **jeder**
Weg der Kontrakte-Engine 503: anlegen, auflisten, verlängern, Pflichten führen,
Auswertung. Das Modul selbst ist ungewöhnlich sauber — Mandantenfilter auf jedem
Weg, 503 statt leerer Liste, Abfragegrenzen. Hier fehlte wirklich nur die
Migration.

Nebenbefund der Abnahme: Das Register lag unter `/api/v1/contracts` und teilte
den Pfad mit dem Warenkontrakt. Die Compat-Route `GET /contracts/{contract_id}`
ist zuerst eingebunden und verschluckte den Detailabruf **und**
`/contracts/expiring` — die Liste, die einen auslaufenden Vertrag anzeigt, bevor
er sich stillschweigend verlängert. Das Register hängt jetzt unter
`/api/v1/vertraege`.

Geprüft wird gegen die gemeinsame, vorhandene Prüfstand-Datenbank. Die Testzeilen
tragen eigene Mandantenkennungen und werden hinterher entfernt — die Datenbank
wird **nicht** zurückgesetzt.
"""

from __future__ import annotations

import os
import uuid
from datetime import datetime, timedelta, timezone

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

HAUS_A = f"kt-a-{uuid.uuid4().hex[:6]}"
HAUS_B = f"kt-b-{uuid.uuid4().hex[:6]}"


@pytest.fixture(scope="module")
def engine():
    from sqlalchemy import create_engine, text

    try:
        motor = create_engine(DB_URL)
        with motor.connect() as conn:
            vorhanden = conn.execute(
                text("SELECT to_regclass('domain_contracts.contracts')")
            ).scalar()
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank nicht erreichbar: {fehler}")
    if not vorhanden:
        pytest.skip("Migration kontraktregister_20261001 nicht angewandt")
    return motor


@pytest.fixture(scope="module", autouse=True)
def eigene_zeilen_wieder_weg(engine):
    from sqlalchemy import text

    yield
    with engine.begin() as v:
        # Versionen und Pflichten haengen am Kontrakt (ON DELETE CASCADE).
        v.execute(
            text("DELETE FROM domain_contracts.contracts WHERE tenant_id IN (:a, :b)"),
            {"a": HAUS_A, "b": HAUS_B},
        )


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
            text("DELETE FROM domain_contracts.contracts WHERE tenant_id IN (:a, :b)"),
            {"a": HAUS_A, "b": HAUS_B},
        )


def _anlegen(client, tenant: str, **felder) -> dict:
    rumpf = {
        "contract_type": "AGRAR",
        "title": "Weizenkontrakt 2026",
        "counterparty_id": "KD-1",
        "counterparty_type": "CUSTOMER",
        "status": "AKTIV",
        "start_date": "2026-01-01T00:00:00+00:00",
        "end_date": "2026-12-31T00:00:00+00:00",
        "total_value_eur": 125000.5,
    }
    rumpf.update(felder)
    antwort = client.post("/api/v1/vertraege", json=rumpf, headers=kopf(tenant))
    assert antwort.status_code == 201, antwort.text
    return antwort.json()


@pytest.fixture()
def kontrakt(client, engine):
    _aufraeumen(engine)
    try:
        yield _anlegen(client, HAUS_A)
    finally:
        _aufraeumen(engine)


# 1 -- Anlegen laeuft ueberhaupt erst jetzt -----------------------------------

def test_kontrakt_wird_angelegt_und_traegt_eine_erste_version(client, engine, kontrakt):
    from sqlalchemy import text

    assert kontrakt["contract_number"].startswith("KT-")
    assert kontrakt["tenant_id"] == HAUS_A
    assert kontrakt["status"] == "AKTIV"
    assert kontrakt["total_value_eur"] == pytest.approx(125000.5)

    with engine.connect() as conn:
        versionen = conn.execute(
            text(
                "SELECT version_number, change_summary, tenant_id "
                "FROM domain_contracts.contract_versions WHERE contract_id = :c"
            ),
            {"c": kontrakt["id"]},
        ).mappings().all()
    assert [(z["version_number"], z["change_summary"], z["tenant_id"]) for z in versionen] == [
        (1, "Erstanlage", HAUS_A)
    ]


def test_eine_aenderung_schreibt_die_naechste_version(client, kontrakt):
    antwort = client.patch(
        f"/api/v1/vertraege/{kontrakt['id']}",
        json={"title": "Weizenkontrakt 2026, angepasst", "change_summary": "Titel"},
        headers=kopf(HAUS_A),
    )
    assert antwort.status_code == 200, antwort.text
    assert antwort.json()["title"] == "Weizenkontrakt 2026, angepasst"

    voll = client.get(f"/api/v1/vertraege/{kontrakt['id']}", headers=kopf(HAUS_A))
    assert voll.status_code == 200, voll.text
    nummern = [v["version_number"] for v in voll.json()["versions"]]
    assert nummern == [1, 2]


# 2 -- Die Datenbank haelt, was die Anwendung verlangt -----------------------

@pytest.mark.parametrize(
    "spalte,wert",
    [
        ("contract_type", "GIBTESNICHT"),
        ("status", "HALBAKTIV"),
        ("counterparty_type", "PARTNER"),
    ],
)
def test_unbekannter_wert_wird_von_der_datenbank_abgewiesen(engine, spalte, wert):
    """Was das Modul prueft, soll die Datenbank halten — sonst steht beim
    naechsten Schreibweg ein Wort drin, das keine Maske kennt."""
    from sqlalchemy import text
    from sqlalchemy.exc import IntegrityError

    felder = {
        "contract_type": "AGRAR",
        "status": "AKTIV",
        "counterparty_type": "CUSTOMER",
    }
    felder[spalte] = wert
    with pytest.raises(IntegrityError):
        with engine.begin() as v:
            v.execute(
                text(
                    "INSERT INTO domain_contracts.contracts "
                    "(id, tenant_id, contract_number, contract_type, title, "
                    " counterparty_id, counterparty_type, status) "
                    "VALUES (:id, :tid, :nr, :ct, 'x', 'KD-1', :cpt, :st)"
                ),
                {
                    "id": str(uuid.uuid4()),
                    "tid": HAUS_A,
                    "nr": f"KT-{uuid.uuid4().hex[:8].upper()}",
                    "ct": felder["contract_type"],
                    "cpt": felder["counterparty_type"],
                    "st": felder["status"],
                },
            )


def test_ende_vor_beginn_wird_abgewiesen(engine):
    from sqlalchemy import text
    from sqlalchemy.exc import IntegrityError

    with pytest.raises(IntegrityError):
        with engine.begin() as v:
            v.execute(
                text(
                    "INSERT INTO domain_contracts.contracts "
                    "(id, tenant_id, contract_number, contract_type, title, "
                    " counterparty_id, start_date, end_date) "
                    "VALUES (:id, :tid, :nr, 'AGRAR', 'x', 'KD-1', "
                    "        '2026-12-31', '2026-01-01')"
                ),
                {
                    "id": str(uuid.uuid4()),
                    "tid": HAUS_A,
                    "nr": f"KT-{uuid.uuid4().hex[:8].upper()}",
                },
            )


def test_kontraktnummer_ist_je_haus_eindeutig(client, engine, kontrakt):
    """Zweimal dieselbe Nummer im selben Haus ist eine Fehlbedienung."""
    nummer = kontrakt["contract_number"]

    doppelt = client.post(
        "/api/v1/vertraege",
        json={
            "contract_number": nummer,
            "contract_type": "EINKAUF",
            "title": "Zweiter mit gleicher Nummer",
            "counterparty_id": "LF-1",
        },
        headers=kopf(HAUS_A),
    )
    assert doppelt.status_code == 503, doppelt.text

    # Ein anderes Haus darf dieselbe Nummer tragen.
    anderes = client.post(
        "/api/v1/vertraege",
        json={
            "contract_number": nummer,
            "contract_type": "EINKAUF",
            "title": "Gleiche Nummer, anderes Haus",
            "counterparty_id": "LF-1",
        },
        headers=kopf(HAUS_B),
    )
    assert anderes.status_code == 201, anderes.text


def test_versionszaehler_ist_je_kontrakt_eindeutig(engine, kontrakt):
    from sqlalchemy import text
    from sqlalchemy.exc import IntegrityError

    with pytest.raises(IntegrityError):
        with engine.begin() as v:
            v.execute(
                text(
                    "INSERT INTO domain_contracts.contract_versions "
                    "(id, contract_id, tenant_id, version_number, changed_by) "
                    "VALUES (:id, :c, :tid, 1, 'test')"
                ),
                {"id": str(uuid.uuid4()), "c": kontrakt["id"], "tid": HAUS_A},
            )


def test_version_ohne_kontrakt_ist_kein_dokument(engine):
    from sqlalchemy import text
    from sqlalchemy.exc import IntegrityError

    with pytest.raises(IntegrityError):
        with engine.begin() as v:
            v.execute(
                text(
                    "INSERT INTO domain_contracts.contract_versions "
                    "(id, contract_id, tenant_id, version_number, changed_by) "
                    "VALUES (:id, 'gibt-es-nicht', :tid, 1, 'test')"
                ),
                {"id": str(uuid.uuid4()), "tid": HAUS_A},
            )


# 3 -- Pflichten -------------------------------------------------------------

def test_pflicht_wird_angelegt_und_abgeschlossen(client, kontrakt):
    faellig = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
    neu = client.post(
        f"/api/v1/vertraege/{kontrakt['id']}/obligations",
        json={
            "obligation_type": "LIEFERUNG",
            "due_date": faellig,
            "description": "500 t Weizen andienen",
        },
        headers=kopf(HAUS_A),
    )
    assert neu.status_code == 201, neu.text
    pflicht = neu.json()
    assert pflicht["status"] == "OFFEN"

    erledigt = client.patch(
        f"/api/v1/vertraege/{kontrakt['id']}/obligations/{pflicht['id']}",
        json={"status": "ERLEDIGT"},
        headers=kopf(HAUS_A),
    )
    assert erledigt.status_code == 200, erledigt.text
    assert erledigt.json()["status"] == "ERLEDIGT"


def test_ueberfaellige_pflicht_wird_als_solche_angelegt(client, kontrakt):
    """Das Modul setzt den Stand aus dem Faelligkeitstag, nicht aus dem Rumpf."""
    vergangen = (datetime.now(timezone.utc) - timedelta(days=5)).isoformat()
    neu = client.post(
        f"/api/v1/vertraege/{kontrakt['id']}/obligations",
        json={
            "obligation_type": "ZAHLUNG",
            "due_date": vergangen,
            "description": "Anzahlung",
        },
        headers=kopf(HAUS_A),
    )
    assert neu.status_code == 201, neu.text
    assert neu.json()["status"] == "UEBERFAELLIG"


def test_pflichten_verschwinden_mit_dem_kontrakt(client, engine, kontrakt):
    from sqlalchemy import text

    faellig = (datetime.now(timezone.utc) + timedelta(days=10)).isoformat()
    neu = client.post(
        f"/api/v1/vertraege/{kontrakt['id']}/obligations",
        json={"obligation_type": "MELDUNG", "due_date": faellig, "description": "Meldung"},
        headers=kopf(HAUS_A),
    )
    assert neu.status_code == 201, neu.text

    with engine.begin() as v:
        v.execute(
            text("DELETE FROM domain_contracts.contracts WHERE id = :i"),
            {"i": kontrakt["id"]},
        )
    with engine.connect() as conn:
        rest = conn.execute(
            text(
                "SELECT count(*) FROM domain_contracts.contract_obligations "
                "WHERE contract_id = :c"
            ),
            {"c": kontrakt["id"]},
        ).scalar()
    assert rest == 0


# 4 -- Verlaengern und Auswertung --------------------------------------------

def test_verlaengern_setzt_das_neue_ende_und_aktiviert(client, kontrakt):
    neues_ende = (datetime.now(timezone.utc) + timedelta(days=400)).isoformat()
    antwort = client.post(
        f"/api/v1/vertraege/{kontrakt['id']}/renew",
        json={"new_end_date": neues_ende},
        headers=kopf(HAUS_A),
    )
    assert antwort.status_code == 200, antwort.text
    assert antwort.json()["status"] == "AKTIV"


def test_auslaufende_kontrakte_werden_gefunden(client, engine):
    _aufraeumen(engine)
    bald = (datetime.now(timezone.utc) + timedelta(days=10)).isoformat()
    spaet = (datetime.now(timezone.utc) + timedelta(days=300)).isoformat()
    try:
        _anlegen(client, HAUS_A, title="Laeuft bald aus", end_date=bald)
        _anlegen(client, HAUS_A, title="Laeuft spaeter aus", end_date=spaet)

        antwort = client.get(
            "/api/v1/vertraege/expiring?days_ahead=30", headers=kopf(HAUS_A)
        )
        assert antwort.status_code == 200, antwort.text
        titel = [k["title"] for k in antwort.json()]
        assert titel == ["Laeuft bald aus"]
    finally:
        _aufraeumen(engine)


def test_auswertung_zaehlt_nur_das_eigene_haus(client, engine):
    _aufraeumen(engine)
    try:
        _anlegen(client, HAUS_A, title="Eigener")
        _anlegen(client, HAUS_B, title="Fremder")
        _anlegen(client, HAUS_B, title="Fremder zwei")

        antwort = client.get("/api/v1/vertraege/analytics", headers=kopf(HAUS_A))
        assert antwort.status_code == 200, antwort.text
        daten = antwort.json()
        # Ein eigener AGRAR-Vertrag, zwei fremde — gezaehlt wird einer.
        assert daten["total_by_type"] == {"AGRAR": 1}
    finally:
        _aufraeumen(engine)


# 5 -- Mandantentrennung je Weg ----------------------------------------------

def test_fremder_kontrakt_ist_nicht_lesbar(client, kontrakt):
    antwort = client.get(f"/api/v1/vertraege/{kontrakt['id']}", headers=kopf(HAUS_B))
    assert antwort.status_code == 404, antwort.text
    assert "Weizenkontrakt" not in antwort.text


def test_liste_zeigt_nur_eigene_kontrakte(client, kontrakt):
    fremd = client.get("/api/v1/vertraege", headers=kopf(HAUS_B))
    assert fremd.status_code == 200, fremd.text
    assert kontrakt["id"] not in [k["id"] for k in fremd.json()]

    eigen = client.get("/api/v1/vertraege", headers=kopf(HAUS_A))
    assert eigen.status_code == 200, eigen.text
    assert kontrakt["id"] in [k["id"] for k in eigen.json()]


@pytest.mark.parametrize(
    "methode,pfad,rumpf",
    [
        ("patch", "/api/v1/vertraege/{id}", {"title": "fremd geaendert"}),
        ("post", "/api/v1/vertraege/{id}/renew", {"new_end_date": "2030-01-01T00:00:00+00:00"}),
        (
            "post",
            "/api/v1/vertraege/{id}/obligations",
            {"obligation_type": "LIEFERUNG", "due_date": "2030-01-01T00:00:00+00:00", "description": "x"},
        ),
    ],
)
def test_fremder_kontrakt_ist_nicht_veraenderbar(client, engine, kontrakt, methode, pfad, rumpf):
    from sqlalchemy import text

    antwort = getattr(client, methode)(
        pfad.format(id=kontrakt["id"]), json=rumpf, headers=kopf(HAUS_B)
    )
    assert antwort.status_code == 404, antwort.text

    # Der Beweis liegt in der Tabelle, nicht im Statuscode.
    with engine.connect() as conn:
        zeile = conn.execute(
            text(
                "SELECT title, end_date FROM domain_contracts.contracts WHERE id = :i"
            ),
            {"i": kontrakt["id"]},
        ).mappings().one()
        pflichten = conn.execute(
            text(
                "SELECT count(*) FROM domain_contracts.contract_obligations "
                "WHERE contract_id = :c"
            ),
            {"c": kontrakt["id"]},
        ).scalar()
    assert zeile["title"] == "Weizenkontrakt 2026"
    assert zeile["end_date"].year == 2026
    assert pflichten == 0
