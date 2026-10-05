"""Ein Webhook gehört einem Haus.

Zwei Module hängen unter `/api/v1/webhooks`, und beide kannten den Mandanten
nicht richtig:

- `webhook_system.py` schrieb in `domain_shared.webhooks` — eine Tabelle, die
  keine Migration anlegt — und kannte `get_tenant_id` überhaupt nicht. Die Liste
  zeigte die Ziel-URLs **aller** Häuser, die laufende Nummer kam aus
  `MAX(nr) + 1` über alle, und `_trigger_webhook` hätte ein Ereignis aus Haus A
  an die URL von Haus B geschickt (die Funktion hat derzeit keinen Aufrufer —
  der Abfluss war angelegt, nicht in Betrieb).
- `webhooks.py` nahm das Haus als **Abfrageparameter** entgegen, mit
  `DEFAULT_TENANT_ID` als Rückfall. Wer `?tenant_id=` setzte, las und schrieb
  fremde Anbindungen. Sein `DELETE /{webhook_id}` hatte **keinen** Filter.

Dazu: `secret` wurde entgegengenommen und verworfen; ein Empfänger konnte nicht
prüfen, ob ein Aufruf echt ist.

Hier war keine Migration die Antwort: `domain_shared.webhook_registrations`
existiert, ist migriert und trägt `tenant_id` und `secret`. Eine zweite
Webhook-Tabelle wäre eine zweite Wahrheit darüber, wohin wir Ereignisse melden.

Geprüft wird gegen die gemeinsame, vorhandene Prüfstand-Datenbank. Die Testzeilen
tragen eigene Mandantenkennungen und werden hinterher entfernt — die Datenbank
wird **nicht** zurückgesetzt.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import uuid

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

HAUS_A = f"wh-a-{uuid.uuid4().hex[:6]}"
HAUS_B = f"wh-b-{uuid.uuid4().hex[:6]}"

URL_A = "https://haus-a.example/ereignis"
URL_B = "https://haus-b.example/ereignis"

TABELLE = "domain_shared.webhook_registrations"


@pytest.fixture(scope="module")
def engine():
    from sqlalchemy import create_engine, text

    try:
        motor = create_engine(DB_URL)
        with motor.connect() as conn:
            vorhanden = conn.execute(
                text(f"SELECT to_regclass('{TABELLE}')")
            ).scalar()
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank nicht erreichbar: {fehler}")
    if not vorhanden:
        pytest.skip(f"{TABELLE} nicht vorhanden")
    return motor


@pytest.fixture(scope="module", autouse=True)
def eigene_haeuser(engine):
    """Zwei Testmandanten. `webhook_registrations.tenant_id` ist ein
    Fremdschluessel auf `tenants` — auf einer frischen Datenbank eine echte
    Bedingung."""
    from sqlalchemy import text

    with engine.begin() as v:
        for name in (HAUS_A, HAUS_B):
            v.execute(
                text(
                    "INSERT INTO domain_shared.tenants (id, name, domain, is_active) "
                    "VALUES (:id, :id, :d, true) ON CONFLICT (id) DO NOTHING"
                ),
                {"id": name, "d": f"{name}.test"},
            )
    yield
    with engine.begin() as v:
        v.execute(
            text(f"DELETE FROM {TABELLE} WHERE tenant_id IN (:a, :b)"),
            {"a": HAUS_A, "b": HAUS_B},
        )
        v.execute(
            text("DELETE FROM domain_shared.tenants WHERE id IN (:a, :b)"),
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
            text(f"DELETE FROM {TABELLE} WHERE tenant_id IN (:a, :b)"),
            {"a": HAUS_A, "b": HAUS_B},
        )


@pytest.fixture()
def beide_haeuser(client, engine):
    """Je ein Webhook in Haus A und Haus B, auf denselben Bereich."""
    _aufraeumen(engine)
    a = client.post(
        "/api/v1/webhooks/bereiche/KONTRAKT_NEU",
        json={"url": URL_A, "bereich": "KONTRAKT_NEU", "secret": "geheim-a"},
        headers=kopf(HAUS_A),
    )
    b = client.post(
        "/api/v1/webhooks/bereiche/KONTRAKT_NEU",
        json={"url": URL_B, "bereich": "KONTRAKT_NEU"},
        headers=kopf(HAUS_B),
    )
    assert a.status_code == 201, a.text
    assert b.status_code == 201, b.text
    try:
        yield a.json(), b.json()
    finally:
        _aufraeumen(engine)


# 1 -- Es bleibt bei einer Webhook-Tabelle ------------------------------------

def test_die_registrierung_landet_in_der_migrierten_tabelle(engine, beide_haeuser):
    from sqlalchemy import text

    with engine.connect() as conn:
        zeilen = conn.execute(
            text(f"SELECT tenant_id, url, event_area FROM {TABELLE} WHERE tenant_id = :t"),
            {"t": HAUS_A},
        ).mappings().all()
    assert [(z["tenant_id"], z["url"], z["event_area"]) for z in zeilen] == [
        (HAUS_A, URL_A, "KONTRAKT_NEU")
    ]


def test_keine_zweite_webhook_tabelle(engine):
    """`domain_shared.webhooks` darf nicht wieder entstehen."""
    from pathlib import Path
    import re

    wurzel = Path(__file__).resolve().parents[1]
    muster = re.compile(r"\b(?:FROM|JOIN|INTO|UPDATE)\s+domain_shared\.webhooks\b", re.I)
    funde = [
        str(pfad.relative_to(wurzel))
        for verzeichnis in ("app", "modules", "alembic")
        for pfad in (wurzel / verzeichnis).rglob("*.py")
        if muster.search(pfad.read_text(encoding="utf-8", errors="ignore"))
    ]
    assert not funde, (
        "Die Anbindungen liegen in domain_shared.webhook_registrations: "
        + ", ".join(funde)
    )


# 2 -- Die Liste zeigt nur das eigene Haus ------------------------------------

def test_liste_zeigt_keine_fremden_ziel_urls(client, beide_haeuser):
    antwort = client.get("/api/v1/webhooks", headers=kopf(HAUS_A))
    assert antwort.status_code == 200, antwort.text
    assert [e["url"] for e in antwort.json()] == [URL_A]
    assert URL_B not in antwort.text


def test_nummer_beginnt_in_jedem_haus_bei_eins(client, beide_haeuser):
    a, b = beide_haeuser
    assert a["nr"] == 1
    assert b["nr"] == 1


def test_das_geheimnis_wird_hinterlegt_aber_nie_ausgegeben(client, engine, beide_haeuser):
    """Vorher nahm die API `secret` entgegen und verwarf es."""
    from sqlalchemy import text

    with engine.connect() as conn:
        hinterlegt = conn.execute(
            text(f"SELECT secret FROM {TABELLE} WHERE tenant_id = :t"),
            {"t": HAUS_A},
        ).scalar()
    assert hinterlegt == "geheim-a"

    antwort = client.get("/api/v1/webhooks", headers=kopf(HAUS_A))
    assert antwort.status_code == 200, antwort.text
    assert "geheim-a" not in antwort.text
    assert antwort.json()[0]["signiert"] is True


# 3 -- Der Abfrageparameter befiehlt nicht mehr -------------------------------

def test_fremdes_haus_im_abfrageparameter_wird_nicht_befolgt(client, beide_haeuser):
    """`webhooks.py` las bis zum 01.10.2026 das Haus aus `?tenant_id=`."""
    antwort = client.get(
        f"/api/v1/webhooks/?tenant_id={HAUS_B}", headers=kopf(HAUS_A)
    )
    assert antwort.status_code == 200, antwort.text
    urls = [e["url"] for e in antwort.json()["items"]]
    assert urls == [URL_A]
    assert URL_B not in antwort.text


def test_registrierung_landet_im_eigenen_haus_trotz_fremdem_parameter(client, engine):
    from sqlalchemy import text

    _aufraeumen(engine)
    antwort = client.post(
        f"/api/v1/webhooks/?tenant_id={HAUS_B}",
        json={"url": "https://haus-a.example/neu", "event_area": "auftrag"},
        headers=kopf(HAUS_A),
    )
    assert antwort.status_code == 201, antwort.text
    try:
        with engine.connect() as conn:
            besitzer = conn.execute(
                text(f"SELECT tenant_id FROM {TABELLE} WHERE url = :u"),
                {"u": "https://haus-a.example/neu"},
            ).scalar()
        assert besitzer == HAUS_A
    finally:
        _aufraeumen(engine)


# 4 -- Kein fremder Webhook ist loeschbar -------------------------------------

def test_fremde_kennung_ist_nicht_loeschbar(client, engine, beide_haeuser):
    from sqlalchemy import text

    _, b = beide_haeuser
    antwort = client.delete(f"/api/v1/webhooks/{b['id']}", headers=kopf(HAUS_A))
    assert antwort.status_code == 404, antwort.text

    with engine.connect() as conn:
        noch_da = conn.execute(
            text(f"SELECT count(*) FROM {TABELLE} WHERE id = :i"),
            {"i": b["id"]},
        ).scalar()
    assert noch_da == 1


def test_abmelden_trifft_die_eigene_nummer(client, engine, beide_haeuser):
    from sqlalchemy import text

    a, b = beide_haeuser
    assert a["nr"] == b["nr"] == 1

    antwort = client.delete("/api/v1/webhooks/abmelden/1", headers=kopf(HAUS_A))
    assert antwort.status_code == 204, antwort.text

    with engine.connect() as conn:
        verbleibend = conn.execute(
            text(f"SELECT tenant_id, url FROM {TABELLE} WHERE tenant_id IN (:a, :b)"),
            {"a": HAUS_A, "b": HAUS_B},
        ).mappings().all()
    assert [(z["tenant_id"], z["url"]) for z in verbleibend] == [(HAUS_B, URL_B)]


def test_unbekannte_nummer_ist_404_und_loescht_nichts(client, engine, beide_haeuser):
    from sqlalchemy import text

    antwort = client.delete("/api/v1/webhooks/abmelden/4242", headers=kopf(HAUS_A))
    assert antwort.status_code == 404, antwort.text

    with engine.connect() as conn:
        anzahl = conn.execute(
            text(f"SELECT count(*) FROM {TABELLE} WHERE tenant_id IN (:a, :b)"),
            {"a": HAUS_A, "b": HAUS_B},
        ).scalar()
    assert anzahl == 2


# 5 -- Der Ausloeser verlaesst das Haus nicht ---------------------------------

class _Antwort:
    status_code = 200


def _mit_falschem_klienten(engine, mandant, gesendet, status_code: int = 200):
    """Ruft `_trigger_webhook` mit einem httpx-Doppel auf."""
    import asyncio

    import httpx
    from sqlalchemy.orm import Session

    from app.api.v1.endpoints import webhook_system

    class _Klient:
        def __init__(self, *_, **__):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *_):
            return False

        async def post(self, url, content=None, headers=None, **__):
            gesendet.append((url, content, headers or {}))
            antwort = _Antwort()
            antwort.status_code = status_code
            return antwort

    echt = httpx.AsyncClient
    httpx.AsyncClient = _Klient  # type: ignore[misc, assignment]
    try:
        with Session(engine) as db:
            asyncio.run(
                webhook_system._trigger_webhook(
                    "KONTRAKT_NEU", {"kontrakt": "K-1"}, db, mandant
                )
            )
    finally:
        httpx.AsyncClient = echt  # type: ignore[misc]


def test_ausloeser_sendet_nur_an_das_eigene_haus(engine, beide_haeuser):
    gesendet: list[tuple] = []
    _mit_falschem_klienten(engine, HAUS_A, gesendet)
    assert [z[0] for z in gesendet] == [URL_A], "Haus B darf nichts erhalten"


def test_ausloeser_signiert_genau_das_was_er_sendet(engine, beide_haeuser):
    from app.api.v1.endpoints import webhook_system

    gesendet: list[tuple] = []
    _mit_falschem_klienten(engine, HAUS_A, gesendet)

    assert len(gesendet) == 1
    _url, rumpf, kopfzeilen = gesendet[0]
    erwartet = "sha256=" + hmac.new(
        b"geheim-a", rumpf, hashlib.sha256
    ).hexdigest()
    assert kopfzeilen[webhook_system.SIGNATUR_KOPF] == erwartet
    assert json.loads(rumpf) == {"kontrakt": "K-1"}


def test_ohne_geheimnis_keine_signatur(engine, beide_haeuser):
    from app.api.v1.endpoints import webhook_system

    gesendet: list[tuple] = []
    _mit_falschem_klienten(engine, HAUS_B, gesendet)
    assert [z[0] for z in gesendet] == [URL_B]
    assert webhook_system.SIGNATUR_KOPF not in gesendet[0][2]


def test_ausloeser_ohne_mandant_sendet_nichts(engine, beide_haeuser):
    gesendet: list[tuple] = []
    _mit_falschem_klienten(engine, "", gesendet)
    assert gesendet == [], "Ein Ereignis ohne Haus darf nirgendwohin gehen"


# 6 -- Eine Stoerung ist keine leere Liste ------------------------------------

def test_stoerung_ist_keine_leere_webhookliste(client, engine):
    """Die Spalte, nach der gefiltert wird, wird kurzzeitig umbenannt.

    Vorher gab die Liste bei jedem Fehler `[]` zurueck. Ein Haus haette eine
    bestehende Anbindung fuer abgemeldet gehalten und doppelt registriert.
    """
    from sqlalchemy import text

    with engine.begin() as v:
        v.execute(text(f"ALTER TABLE {TABELLE} RENAME COLUMN tenant_id TO tenant_id_weg"))
    try:
        antwort = client.get("/api/v1/webhooks", headers=kopf(HAUS_A))
        assert antwort.status_code == 503, antwort.text
    finally:
        with engine.begin() as v:
            v.execute(
                text(f"ALTER TABLE {TABELLE} RENAME COLUMN tenant_id_weg TO tenant_id")
            )


# 7 -- Eine Ziel-URL darf nicht ins eigene Netz zeigen ------------------------

@pytest.mark.parametrize(
    "url",
    [
        "https://127.0.0.1/hook",
        "https://localhost/hook",
        "https://169.254.169.254/latest/meta-data",
    ],
)
def test_ziel_im_eigenen_netz_wird_abgewiesen(client, url):
    """`webhook_system` prueft jetzt dieselbe Bedingung wie `webhooks.py`.

    Vorher genuegte `https://` — damit liess sich die Anwendung als Bote in das
    eigene Netz oder an den Metadatendienst der Cloud schicken.
    """
    antwort = client.post(
        "/api/v1/webhooks/bereiche/KONTRAKT_NEU",
        json={"url": url, "bereich": "KONTRAKT_NEU"},
        headers=kopf(HAUS_A),
    )
    assert antwort.status_code in (400, 422), antwort.text


# 8 -- Ein Vokabular, mit den alten Namen als Alias ---------------------------

def test_bereiche_sind_eine_liste_in_einer_schreibweise(client):
    antwort = client.get("/api/v1/webhooks/bereiche", headers=kopf(HAUS_A))
    assert antwort.status_code == 200, antwort.text
    bereiche = antwort.json()
    # Beide alten Listen sind aufgegangen: das Ereignis aus `webhook_system`
    # und die Objekte, die `webhooks.py` anbot.
    assert "KONTRAKT_NEU" in bereiche
    assert "AUFTRAG_NEU" in bereiche
    assert "STAMMDATEN_GEAENDERT" in bereiche
    # Und nur eine Schreibweise.
    assert all(b == b.upper() for b in bereiche), bereiche
    assert "auftrag" not in bereiche


@pytest.mark.parametrize(
    "alias,kanonisch",
    [
        ("wiegeschein", "WIEGUNG_NEU"),
        ("rechnung", "RECHNUNG_NEU"),
        ("auftrag", "AUFTRAG_NEU"),
        ("lager", "LAGERBEWEGUNG_GEBUCHT"),
    ],
)
def test_alter_objektname_wird_angenommen_und_kanonisch_gespeichert(
    client, engine, alias, kanonisch
):
    """`webhooks.py` nahm Objektnamen an. Sie bleiben gueltig — als Alias."""
    from sqlalchemy import text

    _aufraeumen(engine)
    antwort = client.post(
        "/api/v1/webhooks/",
        json={"url": "https://haus-a.example/alias", "event_area": alias},
        headers=kopf(HAUS_A),
    )
    assert antwort.status_code == 201, antwort.text
    assert antwort.json()["event_area"] == kanonisch
    try:
        with engine.connect() as conn:
            gespeichert = conn.execute(
                text(f"SELECT event_area FROM {TABELLE} WHERE tenant_id = :t"),
                {"t": HAUS_A},
            ).scalar()
        assert gespeichert == kanonisch
    finally:
        _aufraeumen(engine)


def test_unbekannter_bereich_wird_abgewiesen(client, engine):
    _aufraeumen(engine)
    antwort = client.post(
        "/api/v1/webhooks/",
        json={"url": "https://haus-a.example/x", "event_area": "GIBT_ES_NICHT"},
        headers=kopf(HAUS_A),
    )
    assert antwort.status_code in (400, 422), antwort.text


def test_beide_wege_sehen_dieselbe_anbindung(client, engine, beide_haeuser):
    """Zwei Router, ein Dienst, eine Tabelle — kein getrennter Bestand mehr."""
    ueber_system = client.get("/api/v1/webhooks", headers=kopf(HAUS_A))
    ueber_l3c = client.get("/api/v1/webhooks/", headers=kopf(HAUS_A))
    assert ueber_system.status_code == 200, ueber_system.text
    assert ueber_l3c.status_code == 200, ueber_l3c.text

    kennungen_system = [e["id"] for e in ueber_system.json()]
    kennungen_l3c = [e["id"] for e in ueber_l3c.json()["items"]]
    assert kennungen_system == kennungen_l3c
    assert len(kennungen_system) == 1


# 9 -- Ein Zustellversuch hat einen Nachweis ---------------------------------

def test_zustellversuch_wird_protokolliert_und_zaehlt(client, engine, beide_haeuser):
    """`fehler_count` und `letzte_auslosung_am` waren Behauptungen ohne Beleg.

    Jetzt stehen sie im Zustellprotokoll: ein erfolgreicher und ein
    fehlgeschlagener Versuch.
    """
    a, _b = beide_haeuser

    gesendet: list[tuple] = []
    _mit_falschem_klienten(engine, HAUS_A, gesendet, status_code=200)
    _mit_falschem_klienten(engine, HAUS_A, gesendet, status_code=500)
    assert len(gesendet) == 2

    antwort = client.get("/api/v1/webhooks", headers=kopf(HAUS_A))
    assert antwort.status_code == 200, antwort.text
    eintrag = antwort.json()[0]
    # Ein Fehlschlag (HTTP 500), ein Erfolg.
    assert eintrag["fehler_count"] == 1
    assert eintrag["letzte_auslosung_am"] is not None

    versuche = client.get(
        f"/api/v1/webhooks/{a['id']}/zustellversuche", headers=kopf(HAUS_A)
    )
    assert versuche.status_code == 200, versuche.text
    zeilen = versuche.json()
    assert len(zeilen) == 2
    assert {z["erfolgreich"] for z in zeilen} == {True, False}
    misslungen = next(z for z in zeilen if not z["erfolgreich"])
    assert misslungen["status_code"] == 500
    assert "500" in (misslungen["fehler"] or "")


def test_fremde_zustellversuche_sind_nicht_lesbar(client, engine, beide_haeuser):
    _a, b = beide_haeuser
    gesendet: list[tuple] = []
    _mit_falschem_klienten(engine, HAUS_B, gesendet, status_code=200)
    assert len(gesendet) == 1

    # Haus A fragt nach der Anbindung von Haus B.
    antwort = client.get(
        f"/api/v1/webhooks/{b['id']}/zustellversuche", headers=kopf(HAUS_A)
    )
    assert antwort.status_code == 200, antwort.text
    assert antwort.json() == []


def test_abmelden_nimmt_das_protokoll_mit(client, engine, beide_haeuser):
    """Das Protokoll ist Betriebsnachweis einer Anbindung, keine Buchung."""
    from sqlalchemy import text

    a, _b = beide_haeuser
    gesendet: list[tuple] = []
    _mit_falschem_klienten(engine, HAUS_A, gesendet, status_code=200)

    with engine.connect() as conn:
        vorher = conn.execute(
            text(
                "SELECT count(*) FROM domain_shared.webhook_deliveries WHERE webhook_id = :w"
            ),
            {"w": a["id"]},
        ).scalar()
    assert vorher == 1

    assert client.delete("/api/v1/webhooks/abmelden/1", headers=kopf(HAUS_A)).status_code == 204

    with engine.connect() as conn:
        nachher = conn.execute(
            text(
                "SELECT count(*) FROM domain_shared.webhook_deliveries WHERE webhook_id = :w"
            ),
            {"w": a["id"]},
        ).scalar()
    assert nachher == 0
