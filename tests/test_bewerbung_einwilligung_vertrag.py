"""Die Einwilligung zur längeren Aufbewahrung — Nachweis und Widerruf.

Der Löschlauf achtete eine Einwilligung (Talentpool, Art. 6 Abs. 1 lit. a DSGVO),
aber es gab keinen Weg, sie zu erteilen oder zu widerrufen: Die Spalten waren da und
niemand konnte sie füllen.

Was diese Verträge festhalten:

* **Art. 7 Abs. 3 DSGVO:** Der Widerruf ist jederzeit möglich und **nicht schwerer**
  als die Erteilung — kein Rumpf, kein Grund, keine Freigabe. Ein Vertrag prüft, dass
  der Weg überhaupt kein Eingabemodell hat.
* **Art. 7 Abs. 1 DSGVO:** Die Einwilligung ist **nachweisbar**. Der Widerruf ist eine
  **neue Zeile**; die Erteilung bleibt mit Wortlaut und Kanal stehen.
* Der Widerruf wirkt **sofort**: Der nächste Löschlauf nimmt die Bewerbung mit.
* Stand und Verzeichnis stimmen immer überein — sie werden nur zusammen geschrieben.
* Beim Widerruf ist der Kanal **leer**, nicht erfunden.
* Ist der Mensch gelöscht, ist auch der Nachweis weg (`ON DELETE CASCADE`): Ein
  Nachweis, der nur noch den Namen hält, ist selbst die Speicherung, die beendet
  werden sollte.

Geprüft wird gegen die gemeinsame, vorhandene Prüfstand-Datenbank.
"""

from __future__ import annotations

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

HAUS_A = f"ein-a-{uuid.uuid4().hex[:6]}"
HAUS_B = f"ein-b-{uuid.uuid4().hex[:6]}"

WEG = "/api/v1/personal/applications"
FRIST = f"{WEG}/aufbewahrung"
LAUF = f"{WEG}/loeschlauf"

BEWERBUNGEN = "domain_hr.applications"
VERZEICHNIS = "domain_hr.bewerbung_einwilligungen"
REGELN = "domain_hr.bewerbung_aufbewahrung"
LAEUFE = "domain_hr.bewerbung_loeschlaeufe"

TAGE = 180
GRUNDLAGE = "Art. 5 Abs. 1 lit. e DSGVO, § 15 Abs. 4 AGG"
AUFTRAG = {"durchgefuehrt_durch": "Pruefstand", "bestaetigung": "ENDGUELTIG LOESCHEN"}

WORTLAUT = (
    "Ich bin damit einverstanden, dass meine Bewerbungsunterlagen fuer kuenftige "
    "Stellenangebote aufbewahrt werden."
)


@pytest.fixture(scope="module")
def engine():
    from sqlalchemy import create_engine, text

    try:
        motor = create_engine(DB_URL)
        with motor.connect() as conn:
            tabelle = conn.execute(
                text("SELECT to_regclass('domain_hr.bewerbung_einwilligungen')")
            ).scalar()
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank nicht erreichbar: {fehler}")
    if not tabelle:
        pytest.skip("Migration bewerbung_einwilligung_20261006 nicht angewandt")
    return motor


def aufraeumen(engine):
    from sqlalchemy import text

    with engine.begin() as v:
        # Das Verzeichnis haengt per CASCADE an den Bewerbungen; die Reihenfolge
        # bleibt trotzdem ausdruecklich.
        for tabelle in (VERZEICHNIS, BEWERBUNGEN, LAEUFE, REGELN):
            v.execute(
                text(f"DELETE FROM {tabelle} WHERE tenant_id = ANY(:h)"),  # nosec B608
                {"h": [HAUS_A, HAUS_B]},
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


def bewerbung_anlegen(engine, haus: str, status: str = "ABGELEHNT", tage_her: int = TAGE + 10) -> str:
    from sqlalchemy import text

    kennung = str(uuid.uuid4())
    entschieden = None if status in ("EINGANG", "VORAUSWAHL") else date.today() - timedelta(days=tage_her)
    with engine.begin() as v:
        v.execute(
            text(
                f"INSERT INTO {BEWERBUNGEN} "  # nosec B608
                "(id, tenant_id, applicant_name, applicant_email, status, "
                " ablehnungsgrund, entschieden_am, applied_at) "
                "VALUES (:id, :tid, :name, :mail, :status, :grund, :ent, NOW())"
            ),
            {
                "id": kennung,
                "tid": haus,
                "name": f"Bewerber {kennung[:6]}",
                "mail": f"{kennung[:6]}@example.org",
                "status": status,
                "grund": "Fachlich nicht passend" if status == "ABGELEHNT" else None,
                "ent": entschieden,
            },
        )
    return kennung


def pfad(bewerbung_id: str) -> str:
    return f"{WEG}/{bewerbung_id}/einwilligung"


def erteilen(client, haus: str, bewerbung_id: str, **felder):
    nutzlast = {
        "gueltig_bis": felder.pop(
            "gueltig_bis", (date.today() + timedelta(days=365)).isoformat()
        ),
        "kanal": felder.pop("kanal", "WEB"),
        "einwilligungstext": felder.pop("einwilligungstext", WORTLAUT),
    }
    nutzlast.update(felder)
    return client.post(pfad(bewerbung_id), json=nutzlast, headers=kopf(haus))


def widerrufen(client, haus: str, bewerbung_id: str, **kwargs):
    """Ohne Rumpf — genau darum geht es."""
    return client.delete(pfad(bewerbung_id), headers=kopf(haus), **kwargs)


def frist_setzen(client, haus: str, tage: int = TAGE):
    return client.put(
        FRIST,
        json={"aufbewahrung_tage": tage, "gesetzliche_grundlage": GRUNDLAGE},
        headers=kopf(haus),
    )


def spalte(engine, bewerbung_id: str, name: str):
    from sqlalchemy import text

    with engine.connect() as v:
        return v.execute(
            text(f"SELECT {name} FROM {BEWERBUNGEN} WHERE id = :id"),  # nosec B608
            {"id": bewerbung_id},
        ).scalar()


def vorgaenge(engine, bewerbung_id: str) -> list[tuple]:
    from sqlalchemy import text

    with engine.connect() as v:
        return [
            tuple(z)
            for z in v.execute(
                text(
                    "SELECT vorgang, gueltig_bis, kanal, einwilligungstext "
                    f"FROM {VERZEICHNIS} WHERE bewerbung_id = :id "  # nosec B608
                    "ORDER BY erfolgt_am, id"
                ),
                {"id": bewerbung_id},
            ).fetchall()
        ]


# ── 1. Erteilen setzt Stand und Verzeichnis zusammen ────────────────────────


class TestErteilen:
    def test_stand_und_verzeichnis_in_einem(self, client, engine):
        kennung = bewerbung_anlegen(engine, HAUS_A)
        bis = (date.today() + timedelta(days=200)).isoformat()
        antwort = erteilen(client, HAUS_A, kennung, gueltig_bis=bis)
        assert antwort.status_code == 201
        daten = antwort.json()
        assert daten["vorgang"] == "ERTEILT"
        assert daten["gueltig_bis"] == bis
        assert daten["kanal"] == "WEB"
        assert daten["einwilligungstext"] == WORTLAUT
        # Eine Verzeichniszeile ohne Stand waere ein Nachweis ohne Wirkung.
        assert str(spalte(engine, kennung, "aufbewahrung_einwilligung_bis")) == bis
        assert spalte(engine, kennung, "aufbewahrung_einwilligung_am") is not None
        assert len(vorgaenge(engine, kennung)) == 1

    def test_stand_zeigt_lauf_und_verzeichnis(self, client, engine):
        kennung = bewerbung_anlegen(engine, HAUS_A)
        erteilen(client, HAUS_A, kennung)
        antwort = client.get(pfad(kennung), headers=kopf(HAUS_A))
        assert antwort.status_code == 200
        daten = antwort.json()
        assert daten["laeuft"] is True
        assert [v["vorgang"] for v in daten["vorgaenge"]] == ["ERTEILT"]

    def test_ohne_wortlaut_kein_nachweis(self, client, engine):
        # Ohne Wortlaut ist nicht nachweisbar, **wozu** eingewilligt wurde.
        kennung = bewerbung_anlegen(engine, HAUS_A)
        assert erteilen(client, HAUS_A, kennung, einwilligungstext="").status_code == 422
        assert erteilen(client, HAUS_A, kennung, einwilligungstext=None).status_code == 422

    def test_ende_in_der_vergangenheit_abgewiesen(self, client, engine):
        kennung = bewerbung_anlegen(engine, HAUS_A)
        vergangen = (date.today() - timedelta(days=1)).isoformat()
        antwort = erteilen(client, HAUS_A, kennung, gueltig_bis=vergangen)
        assert antwort.status_code == 422
        assert spalte(engine, kennung, "aufbewahrung_einwilligung_bis") is None

    def test_heute_ist_kein_ende(self, client, engine):
        kennung = bewerbung_anlegen(engine, HAUS_A)
        antwort = erteilen(client, HAUS_A, kennung, gueltig_bis=date.today().isoformat())
        assert antwort.status_code == 422

    def test_erlaubnis_ohne_nahes_ende_abgewiesen(self, client, engine):
        # Eine Erlaubnis ohne nahes Ende ist ein Vorrat, keine Einwilligung.
        kennung = bewerbung_anlegen(engine, HAUS_A)
        weit = (date.today() + timedelta(days=1096)).isoformat()
        antwort = erteilen(client, HAUS_A, kennung, gueltig_bis=weit)
        assert antwort.status_code == 422
        assert "Vorrat" in str(antwort.json()["detail"])

    def test_grenze_selbst_ist_erlaubt(self, client, engine):
        kennung = bewerbung_anlegen(engine, HAUS_A)
        genau = (date.today() + timedelta(days=1095)).isoformat()
        assert erteilen(client, HAUS_A, kennung, gueltig_bis=genau).status_code == 201

    @pytest.mark.parametrize("kanal", ["POST", "telefon", "", "web"])
    def test_unbekannter_kanal_abgewiesen(self, client, engine, kanal):
        kennung = bewerbung_anlegen(engine, HAUS_A)
        assert erteilen(client, HAUS_A, kennung, kanal=kanal).status_code == 422

    def test_unbekanntes_feld_abgewiesen(self, client, engine):
        kennung = bewerbung_anlegen(engine, HAUS_A)
        assert erteilen(client, HAUS_A, kennung, unbefristet=True).status_code == 422

    def test_fremde_bewerbung_nicht_erreichbar(self, client, engine):
        kennung = bewerbung_anlegen(engine, HAUS_B)
        assert erteilen(client, HAUS_A, kennung).status_code == 404
        assert client.get(pfad(kennung), headers=kopf(HAUS_A)).status_code == 404
        assert vorgaenge(engine, kennung) == []


# ── 2. Der Widerruf ist nicht schwerer als die Erteilung ────────────────────


class TestWiderruf:
    def test_ohne_rumpf_und_ohne_grund(self, client, engine):
        kennung = bewerbung_anlegen(engine, HAUS_A)
        erteilen(client, HAUS_A, kennung)
        antwort = widerrufen(client, HAUS_A, kennung)
        assert antwort.status_code == 201
        assert antwort.json()["vorgang"] == "WIDERRUFEN"

    def test_der_weg_hat_kein_eingabemodell(self):
        """Art. 7 Abs. 3: Ein Rumpf waere eine Angabe mehr als bei der Erteilung."""
        from app.main import app

        treffer = [
            r
            for r in app.routes
            if getattr(r, "path", "") == f"{WEG}/{{application_id}}/einwilligung"
            and "DELETE" in getattr(r, "methods", set())
        ]
        assert len(treffer) == 1
        assert getattr(treffer[0], "body_field", None) is None

    def test_loescht_den_stand(self, client, engine):
        kennung = bewerbung_anlegen(engine, HAUS_A)
        erteilen(client, HAUS_A, kennung)
        widerrufen(client, HAUS_A, kennung)
        assert spalte(engine, kennung, "aufbewahrung_einwilligung_bis") is None
        assert spalte(engine, kennung, "aufbewahrung_einwilligung_am") is None

    def test_die_erteilung_bleibt_im_verzeichnis(self, client, engine):
        # Art. 7 Abs. 1: Wer die Erteilung ueberschreibt, vernichtet den Nachweis,
        # warum die Daten im abgelaufenen Zeitraum ueberhaupt noch da waren.
        kennung = bewerbung_anlegen(engine, HAUS_A)
        erteilen(client, HAUS_A, kennung)
        widerrufen(client, HAUS_A, kennung)
        zeilen = vorgaenge(engine, kennung)
        assert [z[0] for z in zeilen] == ["ERTEILT", "WIDERRUFEN"]
        # Wortlaut und Kanal der Erteilung stehen noch da.
        assert zeilen[0][2] == "WEB"
        assert zeilen[0][3] == WORTLAUT

    def test_kanal_bleibt_leer_statt_erfunden(self, client, engine):
        kennung = bewerbung_anlegen(engine, HAUS_A)
        erteilen(client, HAUS_A, kennung)
        antwort = widerrufen(client, HAUS_A, kennung)
        # Leer heisst "nicht erhoben". "WEB" waere eine Behauptung ueber einen
        # Vorgang, von dem niemand weiss, wie er einging.
        assert antwort.json()["kanal"] is None
        assert vorgaenge(engine, kennung)[1][2] is None

    def test_ohne_einwilligung_sagt_der_weg_das(self, client, engine):
        kennung = bewerbung_anlegen(engine, HAUS_A)
        antwort = widerrufen(client, HAUS_A, kennung)
        assert antwort.status_code == 409
        # Stillzuhalten waere die bequemere Antwort und die schlechtere.
        assert "keine Einwilligung" in antwort.json()["detail"]["error"]
        assert vorgaenge(engine, kennung) == []

    def test_zweimal_widerrufen_schreibt_nur_einen_vorgang(self, client, engine):
        kennung = bewerbung_anlegen(engine, HAUS_A)
        erteilen(client, HAUS_A, kennung)
        assert widerrufen(client, HAUS_A, kennung).status_code == 201
        assert widerrufen(client, HAUS_A, kennung).status_code == 409
        assert [z[0] for z in vorgaenge(engine, kennung)] == ["ERTEILT", "WIDERRUFEN"]

    def test_erneut_erteilen_ist_moeglich(self, client, engine):
        kennung = bewerbung_anlegen(engine, HAUS_A)
        erteilen(client, HAUS_A, kennung)
        widerrufen(client, HAUS_A, kennung)
        assert erteilen(client, HAUS_A, kennung).status_code == 201
        assert [z[0] for z in vorgaenge(engine, kennung)] == [
            "ERTEILT",
            "WIDERRUFEN",
            "ERTEILT",
        ]
        assert spalte(engine, kennung, "aufbewahrung_einwilligung_bis") is not None

    def test_fremder_widerruf_wirkt_nicht(self, client, engine):
        kennung = bewerbung_anlegen(engine, HAUS_A)
        erteilen(client, HAUS_A, kennung)
        assert widerrufen(client, HAUS_B, kennung).status_code == 404
        assert spalte(engine, kennung, "aufbewahrung_einwilligung_bis") is not None


# ── 3. Der Widerruf wirkt sofort ────────────────────────────────────────────


class TestWirkungAufDenLoeschlauf:
    def test_einwilligung_schuetzt_sofort(self, client, engine):
        frist_setzen(client, HAUS_A)
        kennung = bewerbung_anlegen(engine, HAUS_A)
        erteilen(client, HAUS_A, kennung)
        daten = client.post(LAUF, json=AUFTRAG, headers=kopf(HAUS_A)).json()
        assert daten["geloescht"] == 0
        assert daten["uebersprungen_einwilligung"] == 1

    def test_widerruf_macht_wieder_loeschfaehig(self, client, engine):
        frist_setzen(client, HAUS_A)
        kennung = bewerbung_anlegen(engine, HAUS_A)
        erteilen(client, HAUS_A, kennung)
        widerrufen(client, HAUS_A, kennung)
        daten = client.post(LAUF, json=AUFTRAG, headers=kopf(HAUS_A)).json()
        # Das ist gewollt und nicht umkehrbar, sobald der Lauf gelaufen ist.
        assert daten["geloescht"] == 1
        assert daten["uebersprungen_einwilligung"] == 0

    def test_abgelaufene_einwilligung_laeuft_nicht_mehr(self, client, engine):
        from sqlalchemy import text

        kennung = bewerbung_anlegen(engine, HAUS_A)
        erteilen(client, HAUS_A, kennung)
        with engine.begin() as v:
            v.execute(
                text(
                    f"UPDATE {BEWERBUNGEN} SET "  # nosec B608
                    "aufbewahrung_einwilligung_bis = CURRENT_DATE - 1 WHERE id = :id"
                ),
                {"id": kennung},
            )
        assert client.get(pfad(kennung), headers=kopf(HAUS_A)).json()["laeuft"] is False


# ── 4. Das Verzeichnis ist fortschreibend und die Datenbank hält es ─────────


class TestVerzeichnis:
    def test_kein_weg_aendert_eine_zeile(self):
        """Ein Widerruf ist eine neue Zeile, keine Aenderung."""
        from app.main import app

        methoden = set()
        for r in app.routes:
            if getattr(r, "path", "").endswith("/einwilligung"):
                methoden |= set(getattr(r, "methods", set()))
        assert methoden == {"GET", "POST", "DELETE"}
        assert "PUT" not in methoden and "PATCH" not in methoden

    @pytest.mark.parametrize(
        "werte,warum",
        [
            ("'ERTEILT', NULL, 'WEB', 'Text'", "Erteilung ohne Ende"),
            ("'ERTEILT', CURRENT_DATE + 10, 'WEB', '   '", "Erteilung ohne Wortlaut"),
            ("'ERTEILT', CURRENT_DATE + 10, NULL, 'Text'", "Erteilung ohne Kanal"),
            ("'WIDERRUFEN', CURRENT_DATE + 10, NULL, NULL", "Widerruf mit Ende"),
            ("'WIDERRUFEN', NULL, 'WEB', NULL", "Widerruf mit Kanal"),
            ("'GEAENDERT', NULL, NULL, NULL", "unbekannter Vorgang"),
            ("'ERTEILT', CURRENT_DATE + 10, 'FAX', 'Text'", "unbekannter Kanal"),
        ],
    )
    def test_die_datenbank_haelt_die_form(self, engine, werte, warum):
        from sqlalchemy import text
        from sqlalchemy.exc import IntegrityError

        kennung = bewerbung_anlegen(engine, HAUS_A)
        with pytest.raises(IntegrityError):
            with engine.begin() as v:
                v.execute(
                    text(
                        f"INSERT INTO {VERZEICHNIS} "  # nosec B608
                        "(id, tenant_id, bewerbung_id, vorgang, gueltig_bis, kanal, "
                        " einwilligungstext) "
                        f"VALUES (:id, :t, :b, {werte})"
                    ),
                    {"id": str(uuid.uuid4()), "t": HAUS_A, "b": kennung},
                )

    def test_ein_vorgang_ohne_bewerbung_ist_unmoeglich(self, engine):
        from sqlalchemy import text
        from sqlalchemy.exc import IntegrityError

        with pytest.raises(IntegrityError):
            with engine.begin() as v:
                v.execute(
                    text(
                        f"INSERT INTO {VERZEICHNIS} "  # nosec B608
                        "(id, tenant_id, bewerbung_id, vorgang, gueltig_bis, kanal, "
                        " einwilligungstext) "
                        "VALUES (:id, :t, :b, 'ERTEILT', CURRENT_DATE + 10, 'WEB', 'Text')"
                    ),
                    {"id": str(uuid.uuid4()), "t": HAUS_A, "b": str(uuid.uuid4())},
                )

    def test_mit_der_bewerbung_geht_der_nachweis(self, client, engine):
        from sqlalchemy import text

        # Ist der Mensch geloescht, gibt es keine Aufbewahrung mehr zu rechtfertigen —
        # und ein Nachweis, der nur noch den Namen haelt, ist selbst die Speicherung.
        kennung = bewerbung_anlegen(engine, HAUS_A)
        erteilen(client, HAUS_A, kennung)
        assert len(vorgaenge(engine, kennung)) == 1
        with engine.begin() as v:
            v.execute(
                text(f"DELETE FROM {BEWERBUNGEN} WHERE id = :id"),  # nosec B608
                {"id": kennung},
            )
        assert vorgaenge(engine, kennung) == []

    def test_der_stand_entspricht_der_letzten_zeile(self, client, engine):
        from sqlalchemy import text

        kennung = bewerbung_anlegen(engine, HAUS_A)
        for _ in range(2):
            erteilen(client, HAUS_A, kennung)
            widerrufen(client, HAUS_A, kennung)
        erteilen(client, HAUS_A, kennung)
        with engine.connect() as v:
            letzte = v.execute(
                text(
                    "SELECT vorgang, gueltig_bis FROM " + VERZEICHNIS + " "  # nosec B608
                    "WHERE bewerbung_id = :id ORDER BY erfolgt_am DESC, id DESC LIMIT 1"
                ),
                {"id": kennung},
            ).first()
        assert letzte[0] == "ERTEILT"
        assert spalte(engine, kennung, "aufbewahrung_einwilligung_bis") == letzte[1]

    def test_die_abfrage_ist_begrenzt(self):
        quelle = Path("app/services/bewerbung_einwilligung_service.py").read_text(
            encoding="utf-8"
        )
        assert "fetchmany(limit)" in quelle
        assert "LIMIT :limit" in quelle


# ── 5. Keine vierte Tabelle für einen fremden Begriff ───────────────────────


class TestEigeneTabelle:
    def test_der_dienst_fasst_die_crm_einwilligungen_nicht_an(self):
        """Die CRM-Tabellen beschreiben die Erlaubnis, **angesprochen** zu werden.

        Hier geht es um die Erlaubnis, Daten **aufzubewahren**. Wer beides
        zusammenlegt, laesst einen widerrufenen Werbe-Opt-In wie einen widerrufenen
        Aufbewahrungs-Opt-In aussehen.
        """
        quelle = Path("app/services/bewerbung_einwilligung_service.py").read_text(
            encoding="utf-8"
        )
        code = "\n".join(z for z in quelle.splitlines() if not z.lstrip().startswith("#"))
        for fremd in ("crm_contact_consents", "crm_consents", "crm_contact_consent_history"):
            assert fremd not in code

    def test_die_woerterbuecher_stehen_einmal(self):
        from app.services import bewerbung_einwilligung_service as dienst

        # Dieselbe Falle wie bei `gobd_loeschsperren`: Ein Vokabular, das zweimal
        # geschrieben wird, laeuft auseinander.
        assert dienst.VORGAENGE == ("ERTEILT", "WIDERRUFEN")
        assert dienst.KANAELE == ("WEB", "E_MAIL", "PAPIER", "MUENDLICH")

    def test_das_schema_nennt_dieselben_woerter(self):
        import typing

        from app.api.v1.schemas.personal_bewerbung_schemas import Kanal
        from app.services import bewerbung_einwilligung_service as dienst

        assert set(typing.get_args(Kanal)) == set(dienst.KANAELE)


# ── 6. Montage ──────────────────────────────────────────────────────────────


class TestMontage:
    def test_jeder_weg_einmal(self):
        from app.main import app

        weg = f"{WEG}/{{application_id}}/einwilligung"
        for methode in ("GET", "POST", "DELETE"):
            treffer = [
                r
                for r in app.routes
                if getattr(r, "path", "") == weg and methode in getattr(r, "methods", set())
            ]
            assert len(treffer) == 1, f"{methode} {weg}: {len(treffer)} Montagen"

    def test_der_platzhalter_verschluckt_nichts(self, client, engine):
        # Der Pfad hat ein Segment mehr als `/applications/{id}` und kann von ihm
        # nicht gelesen werden.
        kennung = bewerbung_anlegen(engine, HAUS_A)
        assert client.get(pfad(kennung), headers=kopf(HAUS_A)).status_code == 200
        assert client.get(f"{WEG}/{kennung}", headers=kopf(HAUS_A)).status_code == 200
