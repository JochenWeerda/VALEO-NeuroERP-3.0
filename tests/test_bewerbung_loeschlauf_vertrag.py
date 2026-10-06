"""Der Löschlauf für Bewerberdaten — Frist, Schutz und Nachweis.

Art. 5 Abs. 1 lit. e DSGVO verlangt, personenbezogene Daten nicht länger zu halten
als für den Zweck nötig. Es gab einen Löschweg je Bewerbung, aber keine Frist und
keinen Lauf, der ihn anstößt.

Was diese Verträge festhalten:

* **Ohne beschlossene Frist löscht der Lauf nichts** und sagt warum. Eine Frist,
  die niemand beschlossen hat, ist keine Grundlage, um Daten zu vernichten.
* **Offene Bewerbungen bleiben.** Nur entschiedene haben einen Fristanker.
* **Eine Löschsperre und eine laufende Einwilligung schützen** — und erscheinen im
  Protokoll als übersprungen, nicht als gelöscht.
* **Der Trockenlauf ändert nichts.**
* **Das Protokoll trägt keinen Personenbezug.** Man muss beweisen können, *dass*
  gelöscht wurde, ohne zu behalten, *was* gelöscht wurde.
* Die Sperrtabelle führt ihr Wörterbuch auf **englisch** (`ACTIVE`) — ein deutsches
  „AKTIV" hätte nie getroffen und jede Sperre übergangen.
* Die festen Pfade stehen **vor** `/applications/{application_id}`.

Geprüft wird gegen die gemeinsame, vorhandene Prüfstand-Datenbank.
"""

from __future__ import annotations

import ast
import os
import uuid
from datetime import date, timedelta
from pathlib import Path

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

HAUS_A = f"loe-a-{uuid.uuid4().hex[:6]}"
HAUS_B = f"loe-b-{uuid.uuid4().hex[:6]}"

WEG = "/api/v1/personal/applications"
FRIST = f"{WEG}/aufbewahrung"
TROCKEN = f"{WEG}/loeschlauf/faellig"
LAUF = f"{WEG}/loeschlauf"
PROTOKOLL = f"{WEG}/loeschlaeufe"

BEWERBUNGEN = "domain_hr.applications"
REGELN = "domain_hr.bewerbung_aufbewahrung"
LAEUFE = "domain_hr.bewerbung_loeschlaeufe"
SPERREN = "public.gobd_loeschsperren"

#: Die üblichen sechs Monate: § 15 Abs. 4 AGG plus Zustellung und Klagefrist-Puffer.
TAGE = 180

GRUNDLAGE = "Art. 5 Abs. 1 lit. e DSGVO, § 15 Abs. 4 AGG"
AUFTRAG = {"durchgefuehrt_durch": "Pruefstand", "bestaetigung": "ENDGUELTIG LOESCHEN"}


@pytest.fixture(scope="module")
def engine():
    from sqlalchemy import create_engine, text

    try:
        motor = create_engine(DB_URL)
        with motor.connect() as conn:
            tabelle = conn.execute(
                text("SELECT to_regclass('domain_hr.bewerbung_loeschlaeufe')")
            ).scalar()
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank nicht erreichbar: {fehler}")
    if not tabelle:
        pytest.skip("Migration bewerbung_loeschlauf_20261006 nicht angewandt")
    return motor


def aufraeumen(engine):
    from sqlalchemy import text

    haeuser_liste = [HAUS_A, HAUS_B]
    with engine.begin() as v:
        for tabelle in (BEWERBUNGEN, LAEUFE, REGELN, SPERREN):
            v.execute(
                text(f"DELETE FROM {tabelle} WHERE tenant_id = ANY(:h)"),  # nosec B608
                {"h": haeuser_liste},
            )


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
                {"id": haus, "name": f"Pruefbetrieb {haus}"},
            )
    yield
    aufraeumen(engine)
    with engine.begin() as v:
        v.execute(
            text("DELETE FROM domain_shared.tenants WHERE id = ANY(:h)"),
            {"h": [HAUS_A, HAUS_B]},
        )


@pytest.fixture(autouse=True)
def leer(engine):
    aufraeumen(engine)
    yield


@pytest.fixture(scope="module")
def client(engine):
    from fastapi.testclient import TestClient

    from app.main import app

    return TestClient(app, raise_server_exceptions=False)


def kopf(haus: str) -> dict[str, str]:
    return {"X-Tenant-ID": haus, "Authorization": "Bearer dev-token"}


def frist_setzen(client, haus: str, tage: int = TAGE):
    return client.put(
        FRIST,
        json={
            "aufbewahrung_tage": tage,
            "gesetzliche_grundlage": GRUNDLAGE,
            "beschluss_am": "2026-01-15",
            "beschluss_durch": "Datenschutzbeauftragter",
        },
        headers=kopf(haus),
    )


def bewerbung_anlegen(
    engine,
    haus: str,
    status: str = "ABGELEHNT",
    tage_her: int = TAGE + 10,
    einwilligung_bis: date | None = None,
) -> str:
    """Legt eine Bewerbung direkt in der Datenbank an — mit datierter Entscheidung."""
    from sqlalchemy import text

    kennung = str(uuid.uuid4())
    entschieden = (
        None if status in ("EINGANG", "VORAUSWAHL") else date.today() - timedelta(days=tage_her)
    )
    with engine.begin() as v:
        v.execute(
            text(
                f"INSERT INTO {BEWERBUNGEN} "  # nosec B608
                "(id, tenant_id, applicant_name, applicant_email, status, "
                " ablehnungsgrund, entschieden_am, aufbewahrung_einwilligung_bis, "
                " aufbewahrung_einwilligung_am, applied_at) "
                "VALUES (:id, :tid, :name, :mail, :status, :grund, :ent, :bis, :am, NOW())"
            ),
            {
                "id": kennung,
                "tid": haus,
                "name": f"Bewerber {kennung[:6]}",
                "mail": f"{kennung[:6]}@example.org",
                "status": status,
                "grund": "Fachlich nicht passend" if status == "ABGELEHNT" else None,
                "ent": entschieden,
                "bis": einwilligung_bis,
                "am": date.today() if einwilligung_bis else None,
            },
        )
    return kennung


def sperre_setzen(engine, haus: str, bewerbung_id: str, status: str = "ACTIVE"):
    from sqlalchemy import text

    with engine.begin() as v:
        v.execute(
            text(
                f"INSERT INTO {SPERREN} "  # nosec B608
                "(id, tenant_id, dokument_id, dokument_typ, sperrgrund, hold_start_date, status) "
                "VALUES (:id, :tid, :dok, 'BEWERBUNG', 'RECHTSSTREIT', CURRENT_DATE, :st)"
            ),
            {"id": str(uuid.uuid4()), "tid": haus, "dok": bewerbung_id, "st": status},
        )


def anzahl(engine, haus: str) -> int:
    from sqlalchemy import text

    with engine.connect() as v:
        return v.execute(
            text(f"SELECT COUNT(*) FROM {BEWERBUNGEN} WHERE tenant_id = :t"),  # nosec B608
            {"t": haus},
        ).scalar()


# ── 1. Ohne beschlossene Frist wird nicht gelöscht ──────────────────────────


class TestOhneFrist:
    def test_trockenlauf_weist_ab_und_nennt_den_grund(self, client, engine):
        bewerbung_anlegen(engine, HAUS_A)
        antwort = client.get(TROCKEN, headers=kopf(HAUS_A))
        assert antwort.status_code == 409
        detail = antwort.json()["detail"]
        assert "keine Aufbewahrungsfrist" in detail["error"]
        # Dass der Lauf nichts tut, darf nicht wie eine Fehlfunktion aussehen:
        # die Antwort nennt den Weg, auf dem die Frist beschlossen wird.
        assert "aufbewahrung" in detail["weg"]

    def test_lauf_loescht_nichts(self, client, engine):
        bewerbung_anlegen(engine, HAUS_A)
        antwort = client.post(LAUF, json=AUFTRAG, headers=kopf(HAUS_A))
        assert antwort.status_code == 409
        assert anzahl(engine, HAUS_A) == 1

    def test_kein_standardwert_wird_angenommen(self, client):
        antwort = client.get(FRIST, headers=kopf(HAUS_A))
        assert antwort.status_code == 409

    def test_kein_protokolleintrag_ohne_frist(self, client, engine):
        from sqlalchemy import text

        bewerbung_anlegen(engine, HAUS_A)
        client.post(LAUF, json=AUFTRAG, headers=kopf(HAUS_A))
        with engine.connect() as v:
            laeufe = v.execute(
                text(f"SELECT COUNT(*) FROM {LAEUFE} WHERE tenant_id = :t"),  # nosec B608
                {"t": HAUS_A},
            ).scalar()
        # Ein Protokolleintrag über einen Lauf, der nicht stattgefunden hat, wäre
        # eine falsche Zusage.
        assert laeufe == 0


# ── 2. Die Frist ist eine Entscheidung mit Grenzen ──────────────────────────


class TestFrist:
    def test_festlegen_und_lesen(self, client):
        assert frist_setzen(client, HAUS_A).status_code == 200
        antwort = client.get(FRIST, headers=kopf(HAUS_A))
        assert antwort.status_code == 200
        daten = antwort.json()
        assert daten["aufbewahrung_tage"] == TAGE
        assert daten["gesetzliche_grundlage"] == GRUNDLAGE
        assert daten["aktiv"] is True

    def test_je_mandant_gilt_eine(self, client, engine):
        from sqlalchemy import text

        frist_setzen(client, HAUS_A, 180)
        frist_setzen(client, HAUS_A, 200)
        with engine.connect() as v:
            zeilen = v.execute(
                text(
                    f"SELECT COUNT(*) FROM {REGELN} "  # nosec B608
                    "WHERE tenant_id = :t AND aktiv"
                ),
                {"t": HAUS_A},
            ).scalar()
        assert zeilen == 1
        assert client.get(FRIST, headers=kopf(HAUS_A)).json()["aufbewahrung_tage"] == 200

    def test_grundlage_ist_pflicht(self, client):
        antwort = client.put(FRIST, json={"aufbewahrung_tage": 180}, headers=kopf(HAUS_A))
        assert antwort.status_code == 422

    @pytest.mark.parametrize("tage", [0, -1, 1096, 3650])
    def test_unsinnige_fristen_abgewiesen(self, client, tage):
        antwort = client.put(
            FRIST,
            json={"aufbewahrung_tage": tage, "gesetzliche_grundlage": GRUNDLAGE},
            headers=kopf(HAUS_A),
        )
        assert antwort.status_code == 422

    def test_datenbank_haelt_die_grenze_auch_bei_direktem_sql(self, engine):
        from sqlalchemy import text
        from sqlalchemy.exc import IntegrityError

        with pytest.raises(IntegrityError):
            with engine.begin() as v:
                v.execute(
                    text(
                        f"INSERT INTO {REGELN} "  # nosec B608
                        "(id, tenant_id, aufbewahrung_tage, gesetzliche_grundlage) "
                        "VALUES (:id, :t, 4000, 'frei erfunden')"
                    ),
                    {"id": str(uuid.uuid4()), "t": HAUS_A},
                )

    def test_leere_grundlage_ist_in_der_datenbank_unmoeglich(self, engine):
        from sqlalchemy import text
        from sqlalchemy.exc import IntegrityError

        with pytest.raises(IntegrityError):
            with engine.begin() as v:
                v.execute(
                    text(
                        f"INSERT INTO {REGELN} "  # nosec B608
                        "(id, tenant_id, aufbewahrung_tage, gesetzliche_grundlage) "
                        "VALUES (:id, :t, 180, '   ')"
                    ),
                    {"id": str(uuid.uuid4()), "t": HAUS_A},
                )

    def test_fremde_frist_ist_nicht_sichtbar(self, client):
        frist_setzen(client, HAUS_A)
        assert client.get(FRIST, headers=kopf(HAUS_B)).status_code == 409


# ── 3. Der Trockenlauf zeigt und ändert nichts ──────────────────────────────


class TestTrockenlauf:
    def test_zeigt_die_faelligen(self, client, engine):
        frist_setzen(client, HAUS_A)
        bewerbung_anlegen(engine, HAUS_A)
        antwort = client.get(TROCKEN, headers=kopf(HAUS_A))
        assert antwort.status_code == 200
        daten = antwort.json()
        assert daten["geprueft"] == 1
        assert daten["wird_geloescht"] == 1
        assert daten["aufbewahrung_tage"] == TAGE
        assert daten["stichtag"] == (date.today() - timedelta(days=TAGE)).isoformat()
        assert daten["faellige"][0]["wird_geloescht"] is True
        assert daten["faellige"][0]["bleibt_wegen"] is None

    def test_aendert_nichts(self, client, engine):
        frist_setzen(client, HAUS_A)
        bewerbung_anlegen(engine, HAUS_A)
        client.get(TROCKEN, headers=kopf(HAUS_A))
        assert anzahl(engine, HAUS_A) == 1

    def test_schreibt_kein_protokoll(self, client, engine):
        from sqlalchemy import text

        frist_setzen(client, HAUS_A)
        bewerbung_anlegen(engine, HAUS_A)
        client.get(TROCKEN, headers=kopf(HAUS_A))
        with engine.connect() as v:
            laeufe = v.execute(
                text(f"SELECT COUNT(*) FROM {LAEUFE} WHERE tenant_id = :t"),  # nosec B608
                {"t": HAUS_A},
            ).scalar()
        assert laeufe == 0

    def test_nennt_den_grund_des_bleibens(self, client, engine):
        frist_setzen(client, HAUS_A)
        gesperrt = bewerbung_anlegen(engine, HAUS_A)
        sperre_setzen(engine, HAUS_A, gesperrt)
        bewerbung_anlegen(engine, HAUS_A, einwilligung_bis=date.today() + timedelta(days=90))
        daten = client.get(TROCKEN, headers=kopf(HAUS_A)).json()
        gruende = {z["bleibt_wegen"] for z in daten["faellige"]}
        assert gruende == {"LOESCHSPERRE", "EINWILLIGUNG"}
        assert daten["wird_geloescht"] == 0

    def test_traegt_den_namen_damit_geprueft_werden_kann(self, client, engine):
        # Der Trockenlauf **darf** den Namen zeigen: Wer personenbezogene Daten
        # vernichtet, soll vorher sehen können, welche. Das Protokoll darf es nicht.
        frist_setzen(client, HAUS_A)
        bewerbung_anlegen(engine, HAUS_A)
        zeile = client.get(TROCKEN, headers=kopf(HAUS_A)).json()["faellige"][0]
        assert zeile["applicant_name"]
        assert zeile["applicant_email"]

    def test_fremde_bewerbungen_erscheinen_nicht(self, client, engine):
        frist_setzen(client, HAUS_A)
        frist_setzen(client, HAUS_B)
        bewerbung_anlegen(engine, HAUS_B)
        assert client.get(TROCKEN, headers=kopf(HAUS_A)).json()["geprueft"] == 0


# ── 4. Der Lauf löscht genau das Fällige ────────────────────────────────────


class TestLauf:
    def test_loescht_die_abgelaufene_ablehnung(self, client, engine):
        frist_setzen(client, HAUS_A)
        bewerbung_anlegen(engine, HAUS_A)
        antwort = client.post(LAUF, json=AUFTRAG, headers=kopf(HAUS_A))
        assert antwort.status_code == 201
        assert antwort.json()["geloescht"] == 1
        assert anzahl(engine, HAUS_A) == 0

    def test_laesst_die_noch_laufende_frist_stehen(self, client, engine):
        frist_setzen(client, HAUS_A)
        bewerbung_anlegen(engine, HAUS_A, tage_her=30)
        antwort = client.post(LAUF, json=AUFTRAG, headers=kopf(HAUS_A))
        assert antwort.json()["geprueft"] == 0
        assert anzahl(engine, HAUS_A) == 1

    @pytest.mark.parametrize("stand", ["EINGANG", "VORAUSWAHL"])
    def test_offene_bewerbungen_bleiben_unberuehrt(self, client, engine, stand):
        # Eine offene Bewerbung hat keinen Fristanker: Der Zweck ist noch nicht
        # erledigt. Sie zu löschen wäre kein Datenschutz, sondern ein Datenverlust.
        frist_setzen(client, HAUS_A)
        bewerbung_anlegen(engine, HAUS_A, status=stand)
        antwort = client.post(LAUF, json=AUFTRAG, headers=kopf(HAUS_A))
        assert antwort.json()["geprueft"] == 0
        assert anzahl(engine, HAUS_A) == 1

    def test_eingestellte_mit_abgelaufener_frist_wird_geloescht(self, client, engine):
        frist_setzen(client, HAUS_A)
        bewerbung_anlegen(engine, HAUS_A, status="EINGESTELLT")
        antwort = client.post(LAUF, json=AUFTRAG, headers=kopf(HAUS_A))
        assert antwort.json()["geloescht"] == 1

    def test_loeschsperre_schuetzt(self, client, engine):
        frist_setzen(client, HAUS_A)
        gesperrt = bewerbung_anlegen(engine, HAUS_A)
        sperre_setzen(engine, HAUS_A, gesperrt)
        daten = client.post(LAUF, json=AUFTRAG, headers=kopf(HAUS_A)).json()
        assert daten["geloescht"] == 0
        assert daten["uebersprungen_sperre"] == 1
        assert anzahl(engine, HAUS_A) == 1

    def test_freigegebene_sperre_schuetzt_nicht_mehr(self, client, engine):
        frist_setzen(client, HAUS_A)
        frei = bewerbung_anlegen(engine, HAUS_A)
        sperre_setzen(engine, HAUS_A, frei, status="RELEASED")
        assert client.post(LAUF, json=AUFTRAG, headers=kopf(HAUS_A)).json()["geloescht"] == 1

    def test_fremde_sperre_schuetzt_nicht_das_eigene_haus(self, client, engine):
        # Eine Sperre ist mandantengebunden; sonst könnte ein Haus die Löschung
        # eines anderen blockieren.
        frist_setzen(client, HAUS_A)
        kennung = bewerbung_anlegen(engine, HAUS_A)
        sperre_setzen(engine, HAUS_B, kennung)
        assert client.post(LAUF, json=AUFTRAG, headers=kopf(HAUS_A)).json()["geloescht"] == 1

    def test_laufende_einwilligung_schuetzt(self, client, engine):
        frist_setzen(client, HAUS_A)
        bewerbung_anlegen(engine, HAUS_A, einwilligung_bis=date.today() + timedelta(days=90))
        daten = client.post(LAUF, json=AUFTRAG, headers=kopf(HAUS_A)).json()
        assert daten["geloescht"] == 0
        assert daten["uebersprungen_einwilligung"] == 1

    def test_abgelaufene_einwilligung_schuetzt_nicht_mehr(self, client, engine):
        # Die Einwilligung hat selbst ein Ende; danach gilt wieder die Frist.
        frist_setzen(client, HAUS_A)
        bewerbung_anlegen(engine, HAUS_A, einwilligung_bis=date.today() - timedelta(days=1))
        assert client.post(LAUF, json=AUFTRAG, headers=kopf(HAUS_A)).json()["geloescht"] == 1

    def test_fremde_bewerbungen_bleiben(self, client, engine):
        frist_setzen(client, HAUS_A)
        bewerbung_anlegen(engine, HAUS_B)
        client.post(LAUF, json=AUFTRAG, headers=kopf(HAUS_A))
        assert anzahl(engine, HAUS_B) == 1

    def test_zaehler_und_bestand_stimmen_zusammen(self, client, engine):
        frist_setzen(client, HAUS_A)
        for _ in range(3):
            bewerbung_anlegen(engine, HAUS_A)
        gesperrt = bewerbung_anlegen(engine, HAUS_A)
        sperre_setzen(engine, HAUS_A, gesperrt)
        bewerbung_anlegen(engine, HAUS_A, einwilligung_bis=date.today() + timedelta(days=5))
        bewerbung_anlegen(engine, HAUS_A, status="EINGANG")
        daten = client.post(LAUF, json=AUFTRAG, headers=kopf(HAUS_A)).json()
        assert daten["geprueft"] == 5
        assert daten["geloescht"] == 3
        assert daten["uebersprungen_sperre"] == 1
        assert daten["uebersprungen_einwilligung"] == 1
        # Die offene Bewerbung und die beiden geschützten bleiben.
        assert anzahl(engine, HAUS_A) == 3


# ── 5. Der Auftrag ist bestätigt und zurechenbar ────────────────────────────


class TestAuftrag:
    def test_ohne_bestaetigung_kein_lauf(self, client, engine):
        frist_setzen(client, HAUS_A)
        bewerbung_anlegen(engine, HAUS_A)
        antwort = client.post(
            LAUF, json={"durchgefuehrt_durch": "Pruefstand"}, headers=kopf(HAUS_A)
        )
        assert antwort.status_code == 422
        assert anzahl(engine, HAUS_A) == 1

    def test_falsche_bestaetigung_kein_lauf(self, client, engine):
        frist_setzen(client, HAUS_A)
        bewerbung_anlegen(engine, HAUS_A)
        antwort = client.post(
            LAUF,
            json={"durchgefuehrt_durch": "Pruefstand", "bestaetigung": "ja"},
            headers=kopf(HAUS_A),
        )
        assert antwort.status_code == 422
        assert anzahl(engine, HAUS_A) == 1

    def test_ohne_namen_kein_lauf(self, client, engine):
        # Ein Eingriff, der Daten endgültig vernichtet, muss einem Menschen
        # zurechenbar sein.
        frist_setzen(client, HAUS_A)
        bewerbung_anlegen(engine, HAUS_A)
        antwort = client.post(
            LAUF, json={"bestaetigung": "ENDGUELTIG LOESCHEN"}, headers=kopf(HAUS_A)
        )
        assert antwort.status_code == 422
        assert anzahl(engine, HAUS_A) == 1

    def test_unbekanntes_feld_wird_abgewiesen(self, client):
        frist_setzen(client, HAUS_A)
        antwort = client.post(LAUF, json={**AUFTRAG, "alle": True}, headers=kopf(HAUS_A))
        assert antwort.status_code == 422


# ── 6. Das Protokoll ist der Nachweis — ohne Personenbezug ──────────────────


class TestProtokoll:
    def test_lauf_erscheint_im_protokoll(self, client, engine):
        frist_setzen(client, HAUS_A)
        bewerbung_anlegen(engine, HAUS_A)
        lauf = client.post(LAUF, json=AUFTRAG, headers=kopf(HAUS_A)).json()
        liste = client.get(PROTOKOLL, headers=kopf(HAUS_A)).json()
        assert [z["id"] for z in liste] == [lauf["id"]]
        assert liste[0]["durchgefuehrt_durch"] == "Pruefstand"
        assert liste[0]["aufbewahrung_tage"] == TAGE

    def test_protokoll_traegt_keinen_personenbezug(self, engine):
        from sqlalchemy import text

        with engine.connect() as v:
            spalten = {
                z[0]
                for z in v.execute(
                    text(
                        "SELECT column_name FROM information_schema.columns "
                        "WHERE table_schema='domain_hr' "
                        "AND table_name='bewerbung_loeschlaeufe'"
                    )
                ).fetchall()
            }
        # Man muss beweisen können, *dass* gelöscht wurde, ohne zu behalten, *was*.
        for verboten in (
            "applicant_name",
            "applicant_email",
            "bewerbung_id",
            "application_id",
            "geloeschte_ids",
            "namen",
        ):
            assert verboten not in spalten

    def test_antwort_des_laufs_nennt_keine_namen(self, client, engine):
        frist_setzen(client, HAUS_A)
        bewerbung_anlegen(engine, HAUS_A)
        antwort = client.post(LAUF, json=AUFTRAG, headers=kopf(HAUS_A)).json()
        text_der_antwort = str(antwort).lower()
        assert "@example.org" not in text_der_antwort
        assert "bewerber " not in text_der_antwort

    def test_summe_kann_die_pruefmenge_nicht_uebersteigen(self, engine):
        from sqlalchemy import text
        from sqlalchemy.exc import IntegrityError

        with pytest.raises(IntegrityError):
            with engine.begin() as v:
                v.execute(
                    text(
                        f"INSERT INTO {LAEUFE} "  # nosec B608
                        "(id, tenant_id, aufbewahrung_tage, stichtag, geprueft, geloescht) "
                        "VALUES (:id, :t, 180, CURRENT_DATE, 1, 5)"
                    ),
                    {"id": str(uuid.uuid4()), "t": HAUS_A},
                )

    def test_negative_zahlen_sind_unmoeglich(self, engine):
        from sqlalchemy import text
        from sqlalchemy.exc import IntegrityError

        with pytest.raises(IntegrityError):
            with engine.begin() as v:
                v.execute(
                    text(
                        f"INSERT INTO {LAEUFE} "  # nosec B608
                        "(id, tenant_id, aufbewahrung_tage, stichtag, geprueft, geloescht) "
                        "VALUES (:id, :t, 180, CURRENT_DATE, 0, -1)"
                    ),
                    {"id": str(uuid.uuid4()), "t": HAUS_A},
                )

    def test_fremdes_protokoll_ist_nicht_lesbar(self, client, engine):
        frist_setzen(client, HAUS_A)
        bewerbung_anlegen(engine, HAUS_A)
        client.post(LAUF, json=AUFTRAG, headers=kopf(HAUS_A))
        assert client.get(PROTOKOLL, headers=kopf(HAUS_B)).json() == []


# ── 7. Die Einwilligung ist datiert ─────────────────────────────────────────


class TestEinwilligung:
    def test_einwilligung_ohne_datum_ist_unmoeglich(self, engine):
        from sqlalchemy import text
        from sqlalchemy.exc import IntegrityError

        # Eine Einwilligung, von der niemand weiß, wann sie erteilt wurde, ist
        # keine Rechtsgrundlage.
        with pytest.raises(IntegrityError):
            with engine.begin() as v:
                v.execute(
                    text(
                        f"INSERT INTO {BEWERBUNGEN} "  # nosec B608
                        "(id, tenant_id, applicant_name, applicant_email, status, "
                        " aufbewahrung_einwilligung_bis) "
                        "VALUES (:id, :t, 'A', 'a@example.org', 'EINGANG', CURRENT_DATE)"
                    ),
                    {"id": str(uuid.uuid4()), "t": HAUS_A},
                )

    def test_bewerbung_zeigt_die_einwilligung(self, client, engine):
        kennung = bewerbung_anlegen(
            engine, HAUS_A, einwilligung_bis=date.today() + timedelta(days=30)
        )
        antwort = client.get(f"{WEG}/{kennung}", headers=kopf(HAUS_A))
        assert antwort.status_code == 200
        assert antwort.json()["aufbewahrung_einwilligung_bis"] is not None


# ── 8. Montage: feste Pfade vor dem Platzhalter ─────────────────────────────


class TestMontage:
    def test_feste_pfade_stehen_vor_dem_platzhalter(self):
        from app.main import app

        pfade = [getattr(r, "path", "") for r in app.routes]
        platzhalter = pfade.index("/api/v1/personal/applications/{application_id}")
        for fest in (
            "/api/v1/personal/applications/aufbewahrung",
            "/api/v1/personal/applications/loeschlaeufe",
        ):
            # Stünde der feste Pfad dahinter, läse der Platzhalter "aufbewahrung"
            # als Bewerbungskennung und antwortete 404.
            assert pfade.index(fest) < platzhalter

    def test_der_platzhalter_verschluckt_die_festen_wege_nicht(self, client):
        frist_setzen(client, HAUS_A)
        for weg in (FRIST, PROTOKOLL, TROCKEN):
            assert client.get(weg, headers=kopf(HAUS_A)).status_code == 200

    def test_alle_wege_sind_einmal_montiert(self):
        from app.main import app

        for weg, methode in (
            ("/api/v1/personal/applications/aufbewahrung", "GET"),
            ("/api/v1/personal/applications/aufbewahrung", "PUT"),
            ("/api/v1/personal/applications/loeschlauf/faellig", "GET"),
            ("/api/v1/personal/applications/loeschlauf", "POST"),
            ("/api/v1/personal/applications/loeschlaeufe", "GET"),
        ):
            treffer = [
                r
                for r in app.routes
                if getattr(r, "path", "") == weg and methode in getattr(r, "methods", set())
            ]
            assert len(treffer) == 1, f"{methode} {weg}: {len(treffer)} Montagen"


# ── 9. Das Wörterbuch der Sperrtabelle ist englisch ─────────────────────────


class TestWoerterbuchDerSperre:
    def test_dienst_nennt_den_englischen_stand(self):
        from app.services import bewerbung_loeschlauf_service as dienst

        # Die Sperrtabelle führt ACTIVE/RELEASED/EXPIRED (app/finance/models.py,
        # DocumentHold). Ein deutsches "AKTIV" hätte nie getroffen — und damit
        # **jede** Sperre übergangen und Beweismittel vernichtet.
        assert dienst.SPERRE_AKTIV == "ACTIVE"

    def test_kein_deutsches_aktiv_im_sperrvergleich(self):
        quelle = Path("app/services/bewerbung_loeschlauf_service.py").read_text(
            encoding="utf-8"
        )
        code = "\n".join(z for z in quelle.splitlines() if not z.lstrip().startswith("#"))
        assert '"AKTIV"' not in code

    def test_keine_zweite_sperrtabelle(self):
        """Eine eigene Sperrtabelle wäre genau die Dublette, die diese Welle abbaut.

        Geprüft werden die ``create_table``-Aufrufe selbst, nicht der Text der
        Datei: Eine Textsuche träfe die eigene Begründung im Modulkopf — derselbe
        Fehler, der in dieser Welle schon mehrfach einen Vertrag wertlos gemacht hat.
        """
        baum = ast.parse(
            Path("alembic/versions/bewerbung_loeschlauf_20261006.py").read_text(
                encoding="utf-8"
            )
        )
        angelegt = [
            k.args[0].value
            for k in ast.walk(baum)
            if isinstance(k, ast.Call)
            and isinstance(k.func, ast.Attribute)
            and k.func.attr == "create_table"
            and k.args
            and isinstance(k.args[0], ast.Constant)
        ]
        assert angelegt == ["bewerbung_aufbewahrung", "bewerbung_loeschlaeufe"]
        assert not [n for n in angelegt if "sperr" in n.lower()]


# ── 10. Die Frist ist keine GoBD-Frist ──────────────────────────────────────


class TestNichtGoBD:
    def test_eigene_tabelle_in_tagen(self, engine):
        from sqlalchemy import text

        with engine.connect() as v:
            typ = v.execute(
                text(
                    "SELECT data_type FROM information_schema.columns "
                    "WHERE table_schema='domain_hr' "
                    "AND table_name='bewerbung_aufbewahrung' "
                    "AND column_name='aufbewahrung_tage'"
                )
            ).scalar()
        assert typ == "integer"

    def test_die_gobd_richtlinie_wird_nicht_mitbenutzt(self):
        # Die GoBD-Richtlinie rechnet in Jahren und sagt "mindestens so lange";
        # hier gilt das Gegenteil. Zwei entgegengesetzte Pflichten in einer Tabelle
        # ließen später nicht mehr erkennen, ob eine Zahl Unter- oder Obergrenze ist.
        quelle = Path("app/services/bewerbung_loeschlauf_service.py").read_text(
            encoding="utf-8"
        )
        code = "\n".join(z for z in quelle.splitlines() if not z.lstrip().startswith("#"))
        assert "gobd_aufbewahrungsrichtlinien" not in code
