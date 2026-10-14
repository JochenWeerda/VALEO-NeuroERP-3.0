"""Bewerbung und Einwilligungsfassung anlegen: Urheber, Idempotenz, Fehlermeldungen.

Drei Befunde aus der Pruefung der Masken-Commands vom 11.10.2026:

* Der Urheber einer Einwilligungsfassung kam aus dem Kopf ``X-User-ID``, sonst aus dem
  Rumpf, sonst ``"personal-user"`` — nichts davon geprueft, und die Fassung laesst sich
  nicht loeschen. Der fachliche Weg nahm ihn ebenfalls aus dem Rumpf.
* Der Idempotenzschluessel wurde gespeichert, aber nicht durchgesetzt: Ein wiederholtes
  ``execute`` legte eine zweite Bewerbung an.
* Fehlermeldungen trugen Bewerberdaten: der Pydantic-Text samt Eingabe, und bei
  Datenbankfehlern die Anweisung samt Parametern.

Die Vertraege laufen gegen ``valeo_probe``; Rollen und Kennung kommen aus der Anmeldung.
"""

from __future__ import annotations

import os
import uuid

import pytest

pytestmark = pytest.mark.integration

DB_URL = os.environ.get(
    "TEST_DATABASE_URL",
    os.environ.get("DATABASE_URL", "postgresql://valeo_dev:valeo_dev_2024@127.0.0.1:5432/valeo_probe"),
)
os.environ.setdefault("DATABASE_URL", DB_URL)
os.environ.setdefault("API_DEV_TOKEN", "dev-token")

HAUS = f"bu-{uuid.uuid4().hex[:8]}"
BEWERBUNG_WEG = "/api/v1/personal/applications/actions/speichern"
FASSUNG_WEG = "/api/v1/personal/applications/einwilligungserklaerungen"
FASSUNG_COMMAND = f"{FASSUNG_WEG}/actions/anlegen"

LEITUNG = {"sub": "h.janssen", "roles": ["PERSONAL_ADMIN"]}
SACHBEARBEITUNG = {"sub": "t.de-vries", "roles": ["PERSONAL_BEARBEITEN"]}
OHNE_KENNUNG = {"sub": "", "roles": ["PERSONAL_ADMIN"]}

BEWERBUNG = {"applicant_name": "Wiebke Harms", "applicant_email": "wiebke.harms@privat.example",
             "position_title": "Disponentin", "source": "Website"}


def _aufraeumen(v) -> None:
    from sqlalchemy import text

    h = {"h": HAUS}
    for anweisung in (
        "DELETE FROM domain_crm.crm_action_audit_log WHERE tenant_id = :h",
        "DELETE FROM public.outbox_events WHERE tenant_id = :h",
        "DELETE FROM domain_hr.bewerbung_einwilligungen WHERE tenant_id = :h",
        "DELETE FROM domain_hr.applications WHERE tenant_id = :h",
        "DELETE FROM domain_hr.bewerbung_einwilligungserklaerungen WHERE tenant_id = :h",
        "DELETE FROM domain_hr.bewerbung_loeschlaeufe WHERE tenant_id = :h",
        "DELETE FROM domain_hr.bewerbung_aufbewahrung WHERE tenant_id = :h",
    ):
        v.execute(text(anweisung), h)


@pytest.fixture(scope="module")
def engine():
    from sqlalchemy import create_engine, text

    try:
        motor = create_engine(DB_URL)
        with motor.connect() as v:
            v.execute(text("SELECT performed_by FROM domain_crm.crm_action_audit_log LIMIT 0"))
            v.execute(text("SELECT 1 FROM domain_hr.applications LIMIT 0"))
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank/Migration nicht bereit: {fehler}")
    yield motor
    with motor.begin() as v:
        _aufraeumen(v)


@pytest.fixture(autouse=True)
def leer(engine):
    with engine.begin() as v:
        _aufraeumen(v)
    yield


@pytest.fixture
def client(engine):
    from fastapi.testclient import TestClient

    from app.main import app

    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture
def als(client):
    from app.auth.deps import get_current_user
    from app.main import app

    def setzen(nutzer):
        app.dependency_overrides[get_current_user] = lambda: nutzer

    yield setzen
    app.dependency_overrides.pop(get_current_user, None)


def kopf(**zusatz: str) -> dict[str, str]:
    return {"X-Tenant-ID": HAUS, "Authorization": "Bearer dev-token", **zusatz}


def zeilen(engine, sql: str, **parameter) -> list:
    from sqlalchemy import text

    with engine.connect() as v:
        return [tuple(z) for z in v.execute(text(sql), {"h": HAUS, **parameter})]


def wortlaut() -> str:
    """Je Test ein eigener Text: derselbe Wortlaut waere dieselbe Fassung und damit 409."""
    return f"Ich willige ein, dass meine Bewerbung zwoelf Monate aufbewahrt wird. [{uuid.uuid4().hex}]"


# ── Urheber ───────────────────────────────────────────────────────────────────
class TestUrheber:
    def test_fachlicher_weg_nimmt_die_anmeldung_nicht_den_rumpf(self, client, als):
        als(LEITUNG)
        antwort = client.post(FASSUNG_WEG, headers=kopf(**{"X-User-ID": "jemand-anderes"}),
                              json={"wortlaut": wortlaut(), "erstellt_durch": "Vorstand persoenlich"})
        assert antwort.status_code == 201, antwort.text
        assert antwort.json()["erstellt_durch"] == "h.janssen"

    def test_command_nimmt_die_anmeldung_nicht_kopf_oder_rumpf(self, engine, client, als):
        als(LEITUNG)
        antwort = client.post(FASSUNG_COMMAND, headers=kopf(**{"X-User-ID": "jemand-anderes"}),
                              json={"wortlaut": wortlaut(), "erstellt_durch": "Vorstand persoenlich"})
        ergebnis = antwort.json()
        assert antwort.status_code == 200 and ergebnis["success"] is True, antwort.text
        fassung = client.get(FASSUNG_WEG, headers=kopf()).json()
        assert [f["erstellt_durch"] for f in fassung if f["id"] == ergebnis["affectedIds"][0]] == ["h.janssen"]
        assert zeilen(engine, "SELECT performed_by, result_summary FROM domain_crm.crm_action_audit_log "
                              "WHERE tenant_id = :h") == [("h.janssen", "Einwilligungsfassung angelegt")]

    def test_die_vorschau_nennt_den_urheber_der_schreiben_wuerde(self, client, als):
        als(LEITUNG)
        antwort = client.post(FASSUNG_COMMAND, headers=kopf(**{"X-User-ID": "jemand-anderes"}),
                              json={"_mode": "dryRun", "wortlaut": wortlaut()})
        assert antwort.json()["proposedChanges"][0]["erstellt_durch"] == "h.janssen"

    @pytest.mark.parametrize("weg,rumpf", [
        (FASSUNG_WEG, {"wortlaut": "Ohne Urheber wird nichts geschrieben."}),
        (FASSUNG_COMMAND, {"wortlaut": "Ohne Urheber wird nichts geschrieben."}),
        (BEWERBUNG_WEG, BEWERBUNG),
    ])
    def test_ohne_kennung_in_der_anmeldung_wird_nichts_geschrieben(self, engine, client, als, weg, rumpf):
        als(OHNE_KENNUNG)
        vorher = len(client.get(FASSUNG_WEG, headers=kopf()).json())
        assert client.post(weg, headers=kopf(**{"X-User-ID": "ersatzname"}), json=rumpf).status_code == 403
        assert len(client.get(FASSUNG_WEG, headers=kopf()).json()) == vorher
        assert zeilen(engine, "SELECT count(*) FROM domain_hr.applications WHERE tenant_id = :h") == [(0,)]

    def test_audit_der_bewerbung_nennt_den_urheber_und_keinen_namen(self, engine, client, als):
        als(SACHBEARBEITUNG)
        ergebnis = client.post(BEWERBUNG_WEG, headers=kopf(), json=BEWERBUNG).json()
        assert ergebnis["success"] is True, ergebnis
        assert "Harms" not in ergebnis["summary"]
        # Das Audit ueberlebt den Loeschlauf der Bewerbung — darin steht, wer handelte, nicht wer sich bewarb.
        assert zeilen(engine, "SELECT performed_by, result_summary, entity_id FROM domain_crm.crm_action_audit_log "
                              "WHERE tenant_id = :h") == [("t.de-vries", "Bewerbung erfasst", ergebnis["affectedIds"][0])]


# ── Idempotenz ────────────────────────────────────────────────────────────────
class TestIdempotenz:
    def anzahl(self, engine) -> int:
        return zeilen(engine, "SELECT count(*) FROM domain_hr.applications WHERE tenant_id = :h")[0][0]

    def test_derselbe_schluessel_legt_nur_eine_bewerbung_an(self, engine, client, als):
        als(SACHBEARBEITUNG)
        rumpf = {**BEWERBUNG, "_idempotencyKey": "maske-4711"}
        erste = client.post(BEWERBUNG_WEG, headers=kopf(), json=rumpf).json()
        zweite = client.post(BEWERBUNG_WEG, headers=kopf(), json=rumpf).json()
        assert erste["success"] is True and zweite["success"] is True, (erste, zweite)
        assert zweite["affectedIds"] == erste["affectedIds"]
        assert zweite["auditEntryId"] == erste["auditEntryId"]
        assert "bereits ausgefuehrt" in zweite["summary"]
        assert self.anzahl(engine) == 1
        assert zeilen(engine, "SELECT count(*) FROM domain_crm.crm_action_audit_log WHERE tenant_id = :h") == [(1,)]
        assert zeilen(engine, "SELECT count(*) FROM public.outbox_events WHERE tenant_id = :h") == [(1,)]

    def test_derselbe_schluessel_mit_anderen_angaben_wird_abgewiesen(self, engine, client, als):
        als(SACHBEARBEITUNG)
        client.post(BEWERBUNG_WEG, headers=kopf(), json={**BEWERBUNG, "_idempotencyKey": "maske-4712"})
        andere = {**BEWERBUNG, "applicant_name": "Enno Poppinga", "_idempotencyKey": "maske-4712"}
        ergebnis = client.post(BEWERBUNG_WEG, headers=kopf(), json=andere).json()
        assert ergebnis["success"] is False
        assert ergebnis["validationErrors"][0]["field"] == "_idempotencyKey"
        assert "Poppinga" not in str(ergebnis) and "Harms" not in str(ergebnis)
        assert self.anzahl(engine) == 1

    def test_ohne_schluessel_bleibt_jede_bewerbung_eine_eigene(self, engine, client, als):
        """Wer sich zweimal bewirbt, hat zwei Bewerbungen; ohne Schluessel gibt es nichts zu erkennen."""
        als(SACHBEARBEITUNG)
        for _ in range(2):
            assert client.post(BEWERBUNG_WEG, headers=kopf(), json=BEWERBUNG).json()["success"] is True
        assert self.anzahl(engine) == 2

    def test_vorschau_verbraucht_den_schluessel_nicht(self, engine, client, als):
        als(SACHBEARBEITUNG)
        rumpf = {**BEWERBUNG, "_idempotencyKey": "maske-4713"}
        assert client.post(BEWERBUNG_WEG, headers=kopf(), json={**rumpf, "_mode": "dryRun"}).json()["success"] is True
        assert self.anzahl(engine) == 0
        assert client.post(BEWERBUNG_WEG, headers=kopf(), json=rumpf).json()["success"] is True
        assert self.anzahl(engine) == 1

    def test_geloeschte_bewerbung_wird_durch_den_schluessel_nicht_wiederbelebt(self, engine, client, als):
        from sqlalchemy import text

        als(SACHBEARBEITUNG)
        rumpf = {**BEWERBUNG, "_idempotencyKey": "maske-4714"}
        erste = client.post(BEWERBUNG_WEG, headers=kopf(), json=rumpf).json()
        with engine.begin() as v:
            v.execute(text("DELETE FROM domain_hr.applications WHERE id = :i"), {"i": erste["affectedIds"][0]})
        zweite = client.post(BEWERBUNG_WEG, headers=kopf(), json=rumpf).json()
        assert zweite["success"] is True and "bereits ausgefuehrt" in zweite["summary"]
        assert self.anzahl(engine) == 0

    def test_fassung_mit_demselben_schluessel_entsteht_einmal(self, client, als):
        als(LEITUNG)
        rumpf = {"wortlaut": wortlaut(), "_idempotencyKey": f"fassung-{uuid.uuid4().hex[:8]}"}
        vorher = len(client.get(FASSUNG_WEG, headers=kopf()).json())
        erste = client.post(FASSUNG_COMMAND, headers=kopf(), json=rumpf).json()
        zweite = client.post(FASSUNG_COMMAND, headers=kopf(), json=rumpf).json()
        assert erste["success"] is True and zweite["success"] is True, (erste, zweite)
        assert zweite["affectedIds"] == erste["affectedIds"]
        assert len(client.get(FASSUNG_WEG, headers=kopf()).json()) == vorher + 1
        anderer_text = client.post(FASSUNG_COMMAND, headers=kopf(),
                                   json={**rumpf, "wortlaut": wortlaut()}).json()
        assert anderer_text["success"] is False
        assert len(client.get(FASSUNG_WEG, headers=kopf()).json()) == vorher + 1


# ── Fehlermeldungen ───────────────────────────────────────────────────────────
class TestFehlermeldungen:
    def test_eingabefehler_nennt_feld_und_regel_nicht_den_wert(self, client, als):
        als(SACHBEARBEITUNG)
        zu_lang = "wiebke.harms@" + "x" * 250 + ".example"
        ergebnis = client.post(BEWERBUNG_WEG, headers=kopf(),
                               json={**BEWERBUNG, "applicant_email": zu_lang}).json()
        assert ergebnis["success"] is False
        assert [f["field"] for f in ergebnis["validationErrors"]] == ["applicant_email"]
        assert "wiebke" not in str(ergebnis) and "Harms" not in str(ergebnis)

    def test_datenbankfehler_nennt_regel_nicht_anweisung_oder_werte(self):
        from sqlalchemy.exc import IntegrityError

        from app.services.bewerbung_service import grund_ohne_daten

        class Diag:
            constraint_name = "ck_applications_status"
            table_name = "applications"
            column_name = None
            message_detail = "Failing row contains (Wiebke Harms, wiebke.harms@privat.example)."

        class Urgrund(Exception):
            pgcode = "23514"
            diag = Diag()

        fehler = IntegrityError(
            "INSERT INTO domain_hr.applications (applicant_name) VALUES (%(name)s)",
            {"name": "Wiebke Harms", "email": "wiebke.harms@privat.example"},
            Urgrund('new row violates check constraint; value "Wiebke Harms"'),
        )
        assert "Wiebke" in str(fehler)  # genau das ging vorher an den Aufrufer
        grund = grund_ohne_daten(fehler)
        assert grund == "Urgrund, SQLSTATE 23514, Regel ck_applications_status, Tabelle applications"

    @pytest.mark.parametrize("weg", [BEWERBUNG_WEG, "/api/v1/personal/applications"])
    def test_von_der_datenbank_abgewiesen_nennt_die_regel_ohne_bewerberdaten(self, engine, client, als, weg):
        """Ein Name nur aus Leerraum besteht das Eingabemodell und verletzt ``ck_bewerbung_name_gefuellt``."""
        als(SACHBEARBEITUNG)
        antwort = client.post(weg, headers=kopf(), json={**BEWERBUNG, "applicant_name": "   "})
        assert antwort.status_code == (200 if weg == BEWERBUNG_WEG else 409), antwort.text
        assert "ck_bewerbung_name_gefuellt" in antwort.text
        assert "wiebke.harms" not in antwort.text and "INSERT" not in antwort.text
        assert zeilen(engine, "SELECT count(*) FROM domain_hr.applications WHERE tenant_id = :h") == [(0,)]


# ── Anmeldekennung statt getippter Namen (BEWERBUNG-ANMELDEKENNUNG-20261011) ─────
class TestAnmeldekennung:
    """Wer handelt, traegt das System ein. Ein Name im Rumpf oder in der Abfrage wird nicht gelesen."""

    PERSONALBUERO = {"sub": "5f0c2a9e-0b7d-4e55-9d0e-1c2a3b4c5d6e", "name": "t.de-vries",
                     "roles": ["PERSONAL_ADMIN"]}

    def bewerbung(self, client) -> str:
        return client.post("/api/v1/personal/applications", headers=kopf(), json=BEWERBUNG).json()["id"]

    def test_anmeldename_ist_der_lesbare_name_die_kennung_bleibt_im_audit(self, engine, client, als):
        """``sub`` ist bei Keycloak eine UUID: richtig im Audit, unlesbar in "Erfasst durch"."""
        als(self.PERSONALBUERO)
        ergebnis = client.post(FASSUNG_COMMAND, headers=kopf(), json={"wortlaut": wortlaut()}).json()
        assert ergebnis["success"] is True, ergebnis
        fassungen = client.get(FASSUNG_WEG, headers=kopf()).json()
        assert [f["erstellt_durch"] for f in fassungen if f["id"] == ergebnis["affectedIds"][0]] == ["t.de-vries"]
        assert zeilen(engine, "SELECT performed_by FROM domain_crm.crm_action_audit_log WHERE tenant_id = :h") == [
            ("5f0c2a9e-0b7d-4e55-9d0e-1c2a3b4c5d6e",)]

    def test_token_liefert_den_anmeldenamen(self, monkeypatch):
        from types import SimpleNamespace

        from fastapi.security import HTTPAuthorizationCredentials

        from app.auth import deps

        def anmeldung(**claims):
            # Die geprueften Claims liegen im Request-Zustand (seit 12.10.2026 ohne eigenes decode_token).
            zustand = SimpleNamespace(tenant_verified=True, authenticated_token="jwt",
                                      token_claims={"sub": "uuid-1", "roles": ["x"], **claims})
            return deps.get_current_user(SimpleNamespace(state=zustand),
                                         HTTPAuthorizationCredentials(scheme="Bearer", credentials="jwt"))

        assert anmeldung(preferred_username="h.janssen", name="Hilke Janssen")["name"] == "h.janssen"
        assert anmeldung(name="Hilke Janssen")["name"] == "Hilke Janssen"
        assert anmeldung(email="hilke@haus.example")["name"] == "hilke@haus.example"
        assert anmeldung()["name"] == "uuid-1"
        assert deps.anmeldename({"sub": "uuid-1"}) == "uuid-1" and deps.anmeldename(None) == ""

    def test_entscheidung_traegt_die_anmeldung(self, client, als):
        als(self.PERSONALBUERO)
        kennung = self.bewerbung(client)
        antwort = client.patch(f"/api/v1/personal/applications/{kennung}/stage", headers=kopf(),
                               json={"stage": "ABGELEHNT", "ablehnungsgrund": "Stelle intern besetzt",
                                     "entschieden_durch": "Vorstand persoenlich"})
        assert antwort.status_code == 200, antwort.text
        assert antwort.json()["entschieden_durch"] == "t.de-vries"

    def test_einwilligung_erteilen_und_widerrufen_tragen_die_anmeldung(self, client, als):
        import datetime

        als(self.PERSONALBUERO)
        kennung = self.bewerbung(client)
        fassung = client.post(FASSUNG_WEG, headers=kopf(), json={"wortlaut": wortlaut()}).json()["fassung"]
        weg = f"/api/v1/personal/applications/{kennung}/einwilligung"
        bis = (datetime.date.today() + datetime.timedelta(days=200)).isoformat()
        erteilt = client.post(weg, headers=kopf(), json={"fassung": fassung, "gueltig_bis": bis, "kanal": "PAPIER",
                                                         "erfasst_durch": "jemand anderes"})
        assert erteilt.status_code == 201, erteilt.text
        assert erteilt.json()["erfasst_durch"] == "t.de-vries"
        widerrufen = client.delete(weg, headers=kopf(), params={"erfasst_durch": "jemand anderes"})
        assert widerrufen.status_code == 201, widerrufen.text
        assert widerrufen.json()["erfasst_durch"] == "t.de-vries"

    def test_loeschlauf_braucht_keinen_getippten_namen(self, client, als):
        als(self.PERSONALBUERO)
        frist = client.put("/api/v1/personal/applications/aufbewahrung", headers=kopf(),
                           json={"aufbewahrung_tage": 180, "gesetzliche_grundlage": "§ 15 Abs. 4 AGG",
                                 "beschluss_durch": "Vorstand"})
        assert frist.status_code == 200, frist.text
        # Der Beschluss beschreibt das Gremium und bleibt, wie er eingegeben wurde.
        assert frist.json()["beschluss_durch"] == "Vorstand"
        lauf = client.post("/api/v1/personal/applications/loeschlauf", headers=kopf(),
                           json={"bestaetigung": "ENDGUELTIG LOESCHEN"})
        assert lauf.status_code == 201, lauf.text
        assert lauf.json()["durchgefuehrt_durch"] == "t.de-vries"

    def test_die_masken_fragen_nicht_mehr_nach_dem_eigenen_namen(self):
        from app.core.screen_definitions import get_screen_definition

        def eingabefelder(sd: dict) -> set[str]:
            felder = {f["key"] for f in sd.get("fields", [])}
            for abschnitt in sd.get("sections", []) or []:
                felder |= {f["key"] for f in abschnitt.get("fields", [])}
            for reiter in sd.get("tabs", []) or []:
                felder |= {f["key"] for f in reiter.get("fields", [])}
                for abschnitt in reiter.get("sections", []) or []:
                    felder |= {f["key"] for f in abschnitt.get("fields", [])}
            for aktion in sd.get("actions", []):
                felder |= {f["key"] for f in aktion.get("inputFields", []) or []}
            return felder

        for maske in ("personal/einwilligungserklaerungen", "personal/bewerbung-einwilligung"):
            sd = get_screen_definition(maske)
            assert sd is not None, maske
            assert not ({"erstellt_durch", "erfasst_durch"} & eingabefelder(sd)), maske


# ── Rechte unveraendert ───────────────────────────────────────────────────────
class TestRechte:
    def test_fassung_anlegen_bleibt_der_verwaltung_vorbehalten(self, client, als):
        als(SACHBEARBEITUNG)
        assert client.post(FASSUNG_WEG, headers=kopf(), json={"wortlaut": wortlaut()}).status_code == 403
        assert client.post(FASSUNG_COMMAND, headers=kopf(), json={"wortlaut": wortlaut()}).status_code == 403

    def test_ohne_personalrolle_keine_bewerbung(self, client, als):
        als({"sub": "lagerist", "roles": ["LAGER_BEARBEITEN"]})
        assert client.post(BEWERBUNG_WEG, headers=kopf(), json=BEWERBUNG).status_code == 403
