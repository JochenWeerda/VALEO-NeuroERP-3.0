"""Interessent und Lead sind dasselbe — und die Löschung traf die leere Tabelle.

Vier Dinge, die vorher fehlten:

1. **Drei Modelle für einen Begriff, und der benutzte war der leere.**
   `public.crm_leads` führt 97 Zeilen (Durchdringungs-Akquise, `source`: `lkv`,
   `gap`); `domain_crm.leads` hängt an einem `customer_id` — eine Verkaufschance
   an einem bestehenden Kunden; `domain_crm.interessenten` existiert in keiner
   Datenbank, und `customers.py` schrieb sie.
2. **Eine Quittung ohne Vorgang:** `POST /customers/interessenten` fing den
   INSERT-Fehlschlag und antwortete trotzdem `201` mit einer Interessentennummer.
3. **Die Löschung nach Art. 17 DSGVO traf die falschen Spalten.**
   `UPDATE domain_crm.leads SET company_name = …, contact_person = …` — vier
   Spalten, die es dort nicht gibt. Der Schritt scheiterte, der Antrag blieb
   **dauerhaft offen** (Art. 12 Abs. 3), und die Personendaten in
   `public.crm_leads` blieben unberührt.
4. **`konvertieren` quittierte einen Kunden, den es verwarf:** Der Kundensatz
   wurde angelegt, das Status-UPDATE in einem eigenen `try/except: rollback`
   nahm ihn bei einem Fehlschlag mit, und die Antwort meldete trotzdem
   `status: "KUNDE"` samt Kundennummer.

Geprüft wird gegen die gemeinsame, vorhandene Prüfstand-Datenbank.
"""

from __future__ import annotations

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

HAUS_A = str(uuid.uuid4())
HAUS_B = str(uuid.uuid4())

WEG = "/api/v1/crm/customers/interessenten"
DSGVO = "/api/v1/compliance/dsgvo"
LEADS = "public.crm_leads"
CHANCEN = "domain_crm.leads"


@pytest.fixture(scope="module")
def engine():
    from sqlalchemy import create_engine, text

    try:
        motor = create_engine(DB_URL)
        with motor.connect() as conn:
            vorhanden = conn.execute(
                text(
                    "SELECT 1 FROM information_schema.tables "
                    "WHERE table_schema='public' AND table_name='crm_leads'"
                )
            ).scalar()
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank nicht erreichbar: {fehler}")
    if not vorhanden:
        pytest.skip("public.crm_leads fehlt")
    return motor


@pytest.fixture(scope="module", autouse=True)
def haeuser(engine):
    from sqlalchemy import text

    with engine.begin() as v:
        for haus in (HAUS_A, HAUS_B):
            v.execute(
                text(
                    "INSERT INTO domain_shared.tenants (id, name) VALUES (:id, :name) "
                    "ON CONFLICT (id) DO NOTHING"
                ),
                {"id": haus, "name": f"Pruefakquise {haus[:8]}"},
            )
    yield
    with engine.begin() as v:
        v.execute(text(f"DELETE FROM {LEADS} WHERE tenant_id = ANY(:h)"), {"h": [HAUS_A, HAUS_B]})
        for tabelle in ("domain_crm.customers", "domain_crm.business_partners"):
            v.execute(
                text(f"DELETE FROM {tabelle} WHERE tenant_id = ANY(:h)"),
                {"h": [HAUS_A, HAUS_B]},
            )
        v.execute(
            text("DELETE FROM domain_shared.tenants WHERE id = ANY(:h)"), {"h": [HAUS_A, HAUS_B]}
        )


@pytest.fixture(autouse=True)
def leer(engine):
    from sqlalchemy import text

    with engine.begin() as v:
        v.execute(text(f"DELETE FROM {LEADS} WHERE tenant_id = ANY(:h)"), {"h": [HAUS_A, HAUS_B]})
    yield


@pytest.fixture(scope="module")
def client(engine):
    from fastapi.testclient import TestClient

    from app.main import app

    return TestClient(app, raise_server_exceptions=False)


def kopf(haus: str) -> dict[str, str]:
    return {"X-Tenant-ID": haus, "Authorization": "Bearer dev-token"}


def anlegen(client, haus: str, **felder):
    nutzlast = {"name": felder.pop("name", f"Agrar {uuid.uuid4().hex[:5]} GmbH")}
    nutzlast.update(felder)
    return client.post(WEG, json=nutzlast, headers=kopf(haus))


# ── 1. Das Register, das Daten führt ────────────────────────────────────────


class TestRegister:
    def test_interessent_landet_in_crm_leads(self, engine, client):
        """Vorher schrieb der Weg `domain_crm.interessenten` — es gibt sie nicht."""
        from sqlalchemy import text

        antwort = anlegen(client, HAUS_A, name="Hof Nordwind GmbH", email="n@example.org")
        assert antwort.status_code == 201, antwort.text
        daten = antwort.json()
        with engine.connect() as c:
            zeile = c.execute(
                text(f"SELECT company, email, status, notes FROM {LEADS} WHERE id::text = :id"),
                {"id": daten["id"]},
            ).first()
        assert zeile is not None
        assert zeile[0] == "Hof Nordwind GmbH"
        assert zeile[1] == "n@example.org"
        assert zeile[2] == "NEW"
        assert daten["interessenten_nr"] in (zeile[3] or "")

    def test_domain_crm_interessenten_wird_nicht_angelegt(self, engine):
        """Ein vierter Begriff fuer dieselbe Sache waere das Gegenteil einer Ordnung."""
        from sqlalchemy import text

        with engine.connect() as c:
            assert c.execute(
                text(
                    "SELECT 1 FROM information_schema.tables "
                    "WHERE table_schema='domain_crm' AND table_name='interessenten'"
                )
            ).scalar() is None

    def test_code_verweist_nicht_mehr_auf_interessenten(self):
        from pathlib import Path

        for pfad in (
            "app/api/v1/endpoints/customers.py",
            "app/services/interessent_service.py",
        ):
            quelle = Path(pfad).read_text(encoding="utf-8")
            sql = [
                z for z in quelle.splitlines()
                if "domain_crm.interessenten" in z and not z.lstrip().startswith("#")
                and "`" not in z
            ]
            assert not sql, pfad

    def test_liste_zeigt_genau_das_geschriebene(self, client):
        assert client.get(WEG, headers=kopf(HAUS_A)).json() == []
        angelegt = anlegen(client, HAUS_A, name="Milchhof Süd").json()
        liste = client.get(WEG, headers=kopf(HAUS_A)).json()
        assert [z["id"] for z in liste] == [angelegt["id"]]
        assert liste[0]["name"] == "Milchhof Süd"

    def test_uebernommene_akquise_leads_erscheinen_mit(self, engine, client):
        """Die Leads aus `lkv`/`gap` sind dieselben Interessenten."""
        from sqlalchemy import text

        with engine.begin() as v:
            v.execute(
                text(
                    f"INSERT INTO {LEADS} (id, tenant_id, company, source, status, created_at) "
                    "VALUES (gen_random_uuid(), :tid, 'Betrieb aus LKV', 'lkv', 'NEW', NOW())"
                ),
                {"tid": HAUS_A},
            )
        liste = client.get(WEG, headers=kopf(HAUS_A)).json()
        assert [z["name"] for z in liste] == ["Betrieb aus LKV"]
        # Ohne vermerkte Nummer wird keine erfunden.
        assert liste[0]["interessenten_nr"] is None
        assert liste[0]["herkunft"] == "lkv"

    def test_unbekannter_stand_wird_abgewiesen(self, client):
        antwort = client.get(WEG, params={"status": "VIELLEICHT"}, headers=kopf(HAUS_A))
        assert antwort.status_code == 422

    def test_liste_ist_begrenzt(self, client):
        for _ in range(3):
            anlegen(client, HAUS_A)
        begrenzt = client.get(WEG, params={"limit": 2}, headers=kopf(HAUS_A))
        assert len(begrenzt.json()) == 2
        assert client.get(WEG, params={"limit": 5000}, headers=kopf(HAUS_A)).status_code == 422


class TestNummer:
    def test_nummern_laufen_hoch(self, client):
        erste = anlegen(client, HAUS_A).json()["interessenten_nr"]
        zweite = anlegen(client, HAUS_A).json()["interessenten_nr"]
        assert erste.startswith("INT-")
        assert int(erste.rsplit("-", 1)[1]) + 1 == int(zweite.rsplit("-", 1)[1])

    def test_akquise_leads_ohne_nummer_verschieben_die_zaehlung_nicht(self, engine, client):
        """Vorher zaehlte `COUNT(*) + 1` — jede nummernlose Zeile ergab eine Doppelnummer."""
        from sqlalchemy import text

        erste = anlegen(client, HAUS_A).json()["interessenten_nr"]
        with engine.begin() as v:
            for _ in range(3):
                v.execute(
                    text(
                        f"INSERT INTO {LEADS} (id, tenant_id, company, source, status, created_at) "
                        "VALUES (gen_random_uuid(), :tid, 'Ohne Nummer', 'gap', 'NEW', NOW())"
                    ),
                    {"tid": HAUS_A},
                )
        zweite = anlegen(client, HAUS_A).json()["interessenten_nr"]
        assert int(erste.rsplit("-", 1)[1]) + 1 == int(zweite.rsplit("-", 1)[1])

    def test_lesefehler_vergibt_nicht_die_nummer_eins(self):
        """Vorher: `except: pass` — und `seq` blieb 1."""
        from unittest.mock import MagicMock

        from app.services import interessent_service as dienst

        db = MagicMock()
        db.execute.side_effect = Exception("not readable")
        with pytest.raises(Exception) as fehler:
            dienst.naechste_nummer(db, HAUS_A)
        assert "not readable" in str(fehler.value)


# ── 2. Keine Quittung ohne Vorgang ──────────────────────────────────────────


class TestKeineQuittung:
    def test_schreibfehler_ist_ein_409_und_keine_nummer(self):
        """Vorher: `except Exception: db.rollback()` — und danach `201`."""
        from unittest.mock import MagicMock

        from fastapi import HTTPException

        from app.api.v1.endpoints import customers

        db = MagicMock()
        db.execute.side_effect = Exception("permission denied")
        nutzlast = customers.InteressentCreate(name="Kein Interessent")
        with pytest.raises(HTTPException) as fehler:
            customers.create_interessent(payload=nutzlast, db=db, tenant_id=HAUS_A)
        assert fehler.value.status_code == 409
        db.rollback.assert_called()

    def test_kein_verschlucktes_rollback_in_den_wegen(self):
        from pathlib import Path

        import ast

        quelle = Path("app/api/v1/endpoints/customers.py").read_text(encoding="utf-8")
        baum = ast.parse(quelle)
        gesucht = {"list_interessenten", "create_interessent", "konvertieren"}
        gefunden = set()
        for knoten in ast.walk(baum):
            if not isinstance(knoten, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if knoten.name not in gesucht:
                continue
            gefunden.add(knoten.name)
            # Jeder `except`-Zweig, der zurueckrollt, muss erneut werfen — sonst
            # waere die Antwort eine Quittung ohne Vorgang.
            for teil in ast.walk(knoten):
                if not isinstance(teil, ast.ExceptHandler):
                    continue
                anweisungen = ast.dump(ast.Module(body=teil.body, type_ignores=[]))
                if "rollback" in anweisungen:
                    assert "Raise" in anweisungen, f"{knoten.name}: rollback ohne raise"
        assert gefunden == gesucht, gefunden


# ── 3. Die Konvertierung ist eine Transaktion ───────────────────────────────


class TestKonvertierung:
    def test_konvertieren_erzeugt_kunde_und_setzt_den_stand(self, engine, client):
        from sqlalchemy import text

        i = anlegen(client, HAUS_A, name="Wird Kunde GmbH", email="k@example.org").json()
        antwort = client.post(f"{WEG}/{i['id']}/konvertieren", headers=kopf(HAUS_A))
        assert antwort.status_code == 200, antwort.text
        daten = antwort.json()
        assert daten["status"] == "KUNDE"
        assert daten["kunden_nr"].startswith("KD-")
        with engine.connect() as c:
            stand = c.execute(
                text(f"SELECT status FROM {LEADS} WHERE id::text = :id"), {"id": i["id"]}
            ).scalar()
            kunde = c.execute(
                text(
                    "SELECT customer_number FROM domain_crm.customers "
                    "WHERE customer_number = :nr AND tenant_id = :tid"
                ),
                {"nr": daten["kunden_nr"], "tid": HAUS_A},
            ).scalar()
        assert stand == "CONVERTED"
        assert kunde == daten["kunden_nr"]

    def test_zweites_konvertieren_wird_abgewiesen(self, client):
        """Ein zweiter Durchlauf legte einen zweiten Kundensatz an."""
        i = anlegen(client, HAUS_A).json()
        assert client.post(f"{WEG}/{i['id']}/konvertieren", headers=kopf(HAUS_A)).status_code == 200
        zweite = client.post(f"{WEG}/{i['id']}/konvertieren", headers=kopf(HAUS_A))
        assert zweite.status_code == 409
        assert "bereits konvertiert" in zweite.text

    def test_kein_kunde_wenn_der_standwechsel_scheitert(self, engine, client):
        """Vorher nahm das `rollback` den Kundensatz mit — und die Antwort log.

        Hier scheitert der Standwechsel, weil die Zeile zwischenzeitlich einem
        anderen Mandanten gehoert: Es darf **kein** Kundensatz zurueckbleiben.
        """
        from sqlalchemy import text

        i = anlegen(client, HAUS_A, name="Scheitert GmbH").json()
        with engine.begin() as v:
            v.execute(
                text(f"UPDATE {LEADS} SET tenant_id = :fremd WHERE id::text = :id"),
                {"fremd": HAUS_B, "id": i["id"]},
            )
        antwort = client.post(f"{WEG}/{i['id']}/konvertieren", headers=kopf(HAUS_A))
        assert antwort.status_code == 404
        with engine.connect() as c:
            anzahl = c.execute(
                text(
                    "SELECT COUNT(*) FROM domain_crm.customers "
                    "WHERE company_name = 'Scheitert GmbH' AND tenant_id = :tid"
                ),
                {"tid": HAUS_A},
            ).scalar()
        assert anzahl == 0

    def test_fremder_interessent_wird_nicht_konvertiert(self, client):
        fremd = anlegen(client, HAUS_B).json()
        assert client.post(
            f"{WEG}/{fremd['id']}/konvertieren", headers=kopf(HAUS_A)
        ).status_code == 404


# ── 4. Die Löschung nach Art. 17 DSGVO ──────────────────────────────────────


class TestArtikel17:
    def test_loeschung_trifft_das_register(self, engine, client):
        """Vorher anonymisierte der Weg `domain_crm.leads.company_name` — die
        Spalte gibt es dort nicht, der Antrag blieb offen, und die Daten blieben."""
        from sqlalchemy import text

        i = anlegen(
            client, HAUS_A, name="Löschkandidat GmbH", email="weg@example.org",
            telefon="0421-1234", notizen="Interner Vermerk",
        ).json()

        antrag = client.post(
            f"{DSGVO}/erasure-requests",
            json={
                "requester_name": "Löschkandidat GmbH",
                "requester_email": "weg@example.org",
                "subject_id": i["id"],
                "subject_type": "LEAD",
            },
            headers=kopf(HAUS_A),
        )
        assert antrag.status_code == 201, antrag.text
        ausgefuehrt = client.post(
            f"{DSGVO}/erasure-requests/{antrag.json()['id']}/process", json={}, headers=kopf(HAUS_A)
        )
        assert ausgefuehrt.status_code == 200, ausgefuehrt.text

        with engine.connect() as c:
            zeile = c.execute(
                text(
                    f"SELECT company, contact_person, email, phone, notes FROM {LEADS} "
                    "WHERE id::text = :id"
                ),
                {"id": i["id"]},
            ).first()
        assert zeile is not None, "Die Zeile bleibt — anonymisiert, nicht geloescht"
        assert "Löschkandidat" not in (zeile[0] or "")
        assert "weg@example.org" not in (zeile[2] or "")
        assert zeile[3] is None
        assert zeile[4] is None

    def test_der_antrag_wird_abgeschlossen(self, client):
        """Vorher blieb jeder Lead-Antrag offen (Art. 12 Abs. 3 DSGVO)."""
        i = anlegen(client, HAUS_A, name="Abschluss GmbH", email="a@example.org").json()
        antrag = client.post(
            f"{DSGVO}/erasure-requests",
            json={
                "requester_name": "Abschluss GmbH",
                "requester_email": "a@example.org",
                "subject_id": i["id"],
                "subject_type": "LEAD",
            },
            headers=kopf(HAUS_A),
        )
        ergebnis = client.post(
            f"{DSGVO}/erasure-requests/{antrag.json()['id']}/process", json={}, headers=kopf(HAUS_A)
        ).json()
        protokoll = ergebnis.get("deletion_log") or ergebnis.get("log") or []
        tabellen = [e.get("table") for e in protokoll]
        assert "public.crm_leads" in tabellen, protokoll
        eintrag = next(e for e in protokoll if e.get("table") == "public.crm_leads")
        assert not eintrag.get("error"), eintrag
        assert eintrag.get("rows_affected") == 1

    def test_die_loeschung_nennt_nicht_mehr_die_falschen_spalten(self):
        from pathlib import Path

        quelle = Path("app/api/v1/endpoints/compliance_dsgvo.py").read_text(encoding="utf-8")
        sql = [
            z for z in quelle.splitlines()
            if "domain_crm.leads SET company_name" in z and not z.lstrip().startswith("#")
        ]
        assert not sql
