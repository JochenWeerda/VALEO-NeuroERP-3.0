"""Bewerbungspipeline — Wörterbuch, Übergänge und ein ehrlicher Fehler.

Die sieben Mängel, die der Zerlegungsslice benannt und absichtlich nicht behoben
hat:

1. `except Exception: raise HTTPException(503, "applications table not available")`
   machte aus **jedem** Fehler eine Tabellenaussage — auch aus einem Rechtefehler
   oder einer verletzten Prüfbedingung. Wer das liest, migriert und sucht an der
   falschen Stelle.
2. `response_model=PersonalOut` mit `extra="allow"` — drei verschiedene
   Antwortformen unter einem Namen.
3. `list_applications` ohne `limit`.
4. `APPLICATION_STAGES` als `set` ohne Übergänge: Eine **abgelehnte** Bewerbung
   ließ sich auf `EINGESTELLT` setzen.
5. `uuid4` statt `uuid7`.
6. `domain_hr.applications.status` war freier Text — die Datenbank nahm jedes Wort.
7. Die Lohnwege nahmen `tenant_id` mit `noqa: ARG001` entgegen und verwarfen ihn.

Geprüft wird gegen die gemeinsame, vorhandene Prüfstand-Datenbank.
"""

from __future__ import annotations

import ast
import os
import uuid
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

HAUS_A = f"bew-a-{uuid.uuid4().hex[:6]}"
HAUS_B = f"bew-b-{uuid.uuid4().hex[:6]}"

WEG = "/api/v1/personal/applications"
LOHN = "/api/v1/personal/lohn"
BEWERBUNGEN = "domain_hr.applications"


@pytest.fixture(scope="module")
def engine():
    from sqlalchemy import create_engine, text

    try:
        motor = create_engine(DB_URL)
        with motor.connect() as conn:
            spalte = conn.execute(
                text(
                    "SELECT column_name FROM information_schema.columns "
                    "WHERE table_schema='domain_hr' AND table_name='applications' "
                    "AND column_name='ablehnungsgrund'"
                )
            ).scalar()
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank nicht erreichbar: {fehler}")
    if not spalte:
        pytest.skip("Migration bewerbung_statuswoerterbuch_20261006 nicht angewandt")
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
                {"id": haus, "name": f"Pruefbetrieb {haus}"},
            )
    yield
    with engine.begin() as v:
        v.execute(
            text(f"DELETE FROM {BEWERBUNGEN} WHERE tenant_id = ANY(:h)"), {"h": [HAUS_A, HAUS_B]}
        )
        v.execute(
            text("DELETE FROM domain_shared.tenants WHERE id = ANY(:h)"), {"h": [HAUS_A, HAUS_B]}
        )


@pytest.fixture(autouse=True)
def leer(engine):
    from sqlalchemy import text

    with engine.begin() as v:
        v.execute(
            text(f"DELETE FROM {BEWERBUNGEN} WHERE tenant_id = ANY(:h)"), {"h": [HAUS_A, HAUS_B]}
        )
    yield


@pytest.fixture(scope="module")
def client(engine):
    from fastapi.testclient import TestClient

    from app.main import app

    return TestClient(app, raise_server_exceptions=False)


def kopf(haus: str) -> dict[str, str]:
    return {"X-Tenant-ID": haus, "Authorization": "Bearer dev-token"}


def bewerben(client, haus: str, **felder):
    nutzlast = {
        "applicant_name": felder.pop("applicant_name", f"Bewerber {uuid.uuid4().hex[:5]}"),
        "applicant_email": felder.pop("applicant_email", "bewerber@example.org"),
    }
    nutzlast.update(felder)
    return client.post(WEG, json=nutzlast, headers=kopf(haus))


def stufe(client, haus: str, bewerbung_id: str, stage: str, **felder):
    nutzlast = {"stage": stage}
    nutzlast.update(felder)
    return client.patch(f"{WEG}/{bewerbung_id}/stage", json=nutzlast, headers=kopf(haus))


# ── 1. Das Wörterbuch steht in der Datenbank ────────────────────────────────


class TestWoerterbuch:
    @pytest.mark.parametrize(
        "bedingung",
        [
            "ck_bewerbung_status",
            "ck_bewerbung_ablehnung_begruendet",
            "ck_bewerbung_entscheidung_datiert",
            "ck_bewerbung_name_gefuellt",
        ],
    )
    def test_pruefbedingung_vorhanden(self, engine, bedingung):
        from sqlalchemy import text

        with engine.connect() as c:
            assert c.execute(
                text("SELECT 1 FROM pg_constraint WHERE conname = :n"), {"n": bedingung}
            ).scalar() == 1

    def test_unbekannter_stand_ist_in_der_datenbank_unmoeglich(self, engine, client):
        """Vorher war `status` freier Text — ein Importweg schrieb jedes Wort."""
        from sqlalchemy import text
        from sqlalchemy.exc import IntegrityError

        b = bewerben(client, HAUS_A).json()
        with pytest.raises(IntegrityError):
            with engine.begin() as v:
                v.execute(
                    text(f"UPDATE {BEWERBUNGEN} SET status = 'VIELLEICHT' WHERE id = :id"),
                    {"id": b["id"]},
                )

    def test_ablehnung_ohne_grund_ist_in_der_datenbank_unmoeglich(self, engine, client):
        from sqlalchemy import text
        from sqlalchemy.exc import IntegrityError

        b = bewerben(client, HAUS_A).json()
        with pytest.raises(IntegrityError):
            with engine.begin() as v:
                v.execute(
                    text(
                        f"UPDATE {BEWERBUNGEN} SET status = 'ABGELEHNT', "
                        "entschieden_am = NOW() WHERE id = :id"
                    ),
                    {"id": b["id"]},
                )

    def test_endgueltiger_stand_ohne_zeitpunkt_ist_unmoeglich(self, engine, client):
        from sqlalchemy import text
        from sqlalchemy.exc import IntegrityError

        b = bewerben(client, HAUS_A).json()
        with pytest.raises(IntegrityError):
            with engine.begin() as v:
                v.execute(
                    text(f"UPDATE {BEWERBUNGEN} SET status = 'EINGESTELLT' WHERE id = :id"),
                    {"id": b["id"]},
                )

    def test_woerterbuch_und_uebergaenge_stammen_aus_zwei_mengen(self):
        from app.services import bewerbung_service as dienst

        assert set(dienst.UEBERGAENGE) == set(dienst.STUFEN)
        assert set(dienst.LAUFEND) | set(dienst.ENDGUELTIG) == set(dienst.STUFEN)
        for stand in dienst.ENDGUELTIG:
            assert dienst.UEBERGAENGE[stand] == ()


# ── 2. Die Übergänge ────────────────────────────────────────────────────────


class TestUebergaenge:
    def test_pipeline_laeuft_vorwaerts(self, client):
        b = bewerben(client, HAUS_A).json()
        assert b["status"] == "EINGANG"
        assert stufe(client, HAUS_A, b["id"], "VORAUSWAHL").status_code == 200
        assert stufe(client, HAUS_A, b["id"], "ERSTGESPRAECH").status_code == 200

    def test_rueckschritt_innerhalb_der_pipeline_ist_erlaubt(self, client):
        """Eine Vorauswahl kann sich als zu frueh erweisen."""
        b = bewerben(client, HAUS_A).json()
        stufe(client, HAUS_A, b["id"], "ERSTGESPRAECH")
        assert stufe(client, HAUS_A, b["id"], "VORAUSWAHL").status_code == 200

    def test_abgelehnte_bewerbung_wird_nicht_eingestellt(self, client):
        """Der Kern des Mangels: Vorher ging das, und niemand konnte sagen, ob die
        Ablehnung je galt."""
        b = bewerben(client, HAUS_A).json()
        assert stufe(
            client, HAUS_A, b["id"], "ABGELEHNT", ablehnungsgrund="Profil passt nicht"
        ).status_code == 200
        antwort = stufe(client, HAUS_A, b["id"], "EINGESTELLT")
        assert antwort.status_code == 409
        assert "endgueltig" in antwort.text

    def test_eingestellte_bewerbung_wird_nicht_zurueckgesetzt(self, client):
        b = bewerben(client, HAUS_A).json()
        stufe(client, HAUS_A, b["id"], "ANGEBOT")
        assert stufe(client, HAUS_A, b["id"], "EINGESTELLT").status_code == 200
        assert stufe(client, HAUS_A, b["id"], "EINGANG").status_code == 409

    def test_derselbe_stand_zweimal_wird_abgewiesen(self, client):
        b = bewerben(client, HAUS_A).json()
        assert stufe(client, HAUS_A, b["id"], "EINGANG").status_code == 409

    def test_unbekannte_stufe_wird_abgewiesen(self, client):
        b = bewerben(client, HAUS_A).json()
        assert stufe(client, HAUS_A, b["id"], "VIELLEICHT").status_code == 422

    def test_der_fehler_nennt_die_erlaubten_ziele(self, client):
        b = bewerben(client, HAUS_A).json()
        stufe(client, HAUS_A, b["id"], "EINGESTELLT", note="direkt")
        antwort = stufe(client, HAUS_A, b["id"], "ANGEBOT")
        assert antwort.status_code == 409
        assert "neuer Vorgang" in antwort.text


class TestAblehnung:
    def test_ablehnung_braucht_einen_grund(self, client):
        """§ 22 AGG: Im Streitfall traegt der Arbeitgeber die Beweislast."""
        b = bewerben(client, HAUS_A).json()
        ohne = stufe(client, HAUS_A, b["id"], "ABGELEHNT")
        assert ohne.status_code == 422
        assert "22 AGG" in ohne.text

    @pytest.mark.parametrize("grund", ["", "   "])
    def test_leerer_grund_zaehlt_nicht(self, client, grund):
        b = bewerben(client, HAUS_A).json()
        assert stufe(
            client, HAUS_A, b["id"], "ABGELEHNT", ablehnungsgrund=grund
        ).status_code == 422

    def test_grund_und_entscheidung_werden_festgehalten(self, engine, client):
        from sqlalchemy import text

        b = bewerben(client, HAUS_A).json()
        antwort = stufe(
            client, HAUS_A, b["id"], "ABGELEHNT",
            ablehnungsgrund="Stelle intern besetzt", entschieden_durch="A. Leitung",
        )
        assert antwort.status_code == 200, antwort.text
        daten = antwort.json()
        assert daten["ablehnungsgrund"] == "Stelle intern besetzt"
        assert daten["entschieden_am"] is not None
        assert daten["entschieden_durch"] == "A. Leitung"
        assert daten["endgueltig"] is True
        with engine.connect() as c:
            zeile = c.execute(
                text(
                    f"SELECT ablehnungsgrund, entschieden_am FROM {BEWERBUNGEN} WHERE id = :id"
                ),
                {"id": b["id"]},
            ).first()
        assert zeile[0] == "Stelle intern besetzt"
        assert zeile[1] is not None

    def test_der_grund_steht_nicht_im_verlaufsfeld(self, client):
        """`notes` ist ein Verlaufsfeld — ein Grund, der darin untergeht, ist kein
        Nachweis."""
        b = bewerben(client, HAUS_A).json()
        daten = stufe(
            client, HAUS_A, b["id"], "ABGELEHNT", ablehnungsgrund="Eigener Grund",
            note="Verlaufsnotiz",
        ).json()
        assert daten["ablehnungsgrund"] == "Eigener Grund"
        assert "Verlaufsnotiz" in (daten["notes"] or "")
        assert "Eigener Grund" not in (daten["notes"] or "")


# ── 3. Der Fehler nennt seine Ursache ───────────────────────────────────────


class TestFehlerdeutung:
    def test_fehlende_tabelle_ist_ein_503_mit_hinweis(self):
        """Nur **das** ist eine Tabellenaussage."""
        from unittest.mock import MagicMock

        from psycopg2.errors import UndefinedTable
        from sqlalchemy.exc import ProgrammingError

        from app.services import bewerbung_service as dienst

        db = MagicMock()
        fehler = ProgrammingError("stmt", {}, UndefinedTable())
        umgewandelt = dienst.fehler_deuten(db, fehler, "Bewerbungen lesen", HAUS_A)
        assert umgewandelt.status_code == 503
        assert "migration_hint" in str(umgewandelt.detail)
        db.rollback.assert_called_once()

    def test_jeder_andere_fehler_ist_ein_409_mit_grund(self):
        """Vorher wurde auch ein Rechtefehler zu "applications table not available"."""
        from unittest.mock import MagicMock

        from app.services import bewerbung_service as dienst

        db = MagicMock()
        umgewandelt = dienst.fehler_deuten(
            db, Exception("permission denied for table applications"), "Bewerbung anlegen", HAUS_A
        )
        assert umgewandelt.status_code == 409
        assert "permission denied" in str(umgewandelt.detail)
        assert "migration_hint" not in str(umgewandelt.detail)

    def test_die_alte_tabellenaussage_kommt_nicht_mehr_vor(self):
        quelle = Path("app/api/v1/endpoints/personal_bewerbungen.py").read_text(encoding="utf-8")
        anweisungen = [
            z for z in quelle.splitlines()
            if "applications table not available" in z and not z.lstrip().startswith(("#", "*"))
            and "``" not in z
        ]
        assert not anweisungen


# ── 4. Form, Grenze und Kennung ─────────────────────────────────────────────


class TestFormUndGrenze:
    def test_antwortmodelle_sind_typisiert(self):
        """Vorher hingen alle Wege an `PersonalOut` mit `extra="allow"`.

        Die Prüfung nennt nicht mehr eine feste Liste erlaubter Modelle — der Slice
        BEWERBUNG-LOESCHLAUF-20261006 hat vier Wege ergänzt, und eine Aufzählung
        hätte hier nur verlangt, sie nachzutragen. Geprüft wird die Eigenschaft, auf
        die es ankommt: **jedes** Antwortmodell ist in diesem Fach erklärt und nimmt
        keine unbekannten Felder an.
        """
        import typing

        from pydantic import BaseModel

        from app.api.v1.endpoints import personal_bewerbungen as modul
        from app.api.v1.schemas import personal_bewerbung_schemas as fach
        from app.api.v1.schemas.personal_bewerbung_schemas import BewerbungOut

        def kern(modell):
            """`List[X]`/`list[X]` sind dasselbe Versprechen wie `X`."""
            argumente = typing.get_args(modell)
            return argumente[0] if argumente else modell

        modelle = {
            kern(getattr(r, "response_model", None))
            for r in modul.router.routes
            if "applications" in r.path
        } - {None}

        assert BewerbungOut in modelle
        for modell in modelle:
            assert issubclass(modell, BaseModel), modell
            # In diesem Fach erklärt — nicht ein Sammelmodell aus der Nachbarschaft.
            assert getattr(fach, modell.__name__, None) is modell, modell
            # `extra="allow"` war der Mangel: Ein Modell, das alles erlaubt,
            # beschreibt nichts.
            assert modell.model_config.get("extra") != "allow", modell.__name__

    def test_die_liste_ist_begrenzt(self, client):
        for _ in range(3):
            bewerben(client, HAUS_A)
        begrenzt = client.get(WEG, params={"limit": 2}, headers=kopf(HAUS_A))
        assert begrenzt.status_code == 200
        assert len(begrenzt.json()) == 2
        assert client.get(WEG, params={"limit": 5000}, headers=kopf(HAUS_A)).status_code == 422

    def test_unbekanntes_feld_wird_abgewiesen(self, client):
        antwort = client.post(
            WEG,
            json={
                "applicant_name": "X",
                "applicant_email": "x@example.org",
                "status": "EINGESTELLT",
            },
            headers=kopf(HAUS_A),
        )
        assert antwort.status_code == 422

    def test_die_kennung_ist_zeitgeordnet(self, client):
        """`uuid7` ist zeitgeordnet — zwei Bewerbungen behalten ihre Reihenfolge."""
        erste = bewerben(client, HAUS_A).json()["id"]
        zweite = bewerben(client, HAUS_A).json()["id"]
        assert erste < zweite

    def test_kein_uuid4_mehr_im_weg(self):
        for pfad in (
            "app/api/v1/endpoints/personal_bewerbungen.py",
            "app/services/bewerbung_service.py",
        ):
            quelle = Path(pfad).read_text(encoding="utf-8")
            # Der Aufruf zaehlt, nicht die Erwaehnung im Docstring, der den alten
            # Stand beschreibt.
            assert "uuid4(" not in quelle, pfad
            assert "import uuid4" not in quelle, pfad


class TestMandantentrennung:
    def test_fremde_bewerbungen_sind_nicht_sichtbar(self, client):
        bewerben(client, HAUS_B, applicant_name="Nur Haus B")
        assert client.get(WEG, headers=kopf(HAUS_A)).json() == []

    def test_fremde_bewerbung_ist_nicht_lesbar(self, client):
        fremd = bewerben(client, HAUS_B).json()
        assert client.get(f"{WEG}/{fremd['id']}", headers=kopf(HAUS_A)).status_code == 404

    def test_fremde_stufe_wird_nicht_gewechselt(self, client):
        fremd = bewerben(client, HAUS_B).json()
        assert stufe(client, HAUS_A, fremd["id"], "VORAUSWAHL").status_code == 404

    def test_fremde_bewerbung_wird_nicht_geloescht(self, client):
        fremd = bewerben(client, HAUS_B).json()
        assert client.delete(f"{WEG}/{fremd['id']}", headers=kopf(HAUS_A)).status_code == 404

    def test_eigene_bewerbung_wird_geloescht(self, client):
        b = bewerben(client, HAUS_A).json()
        assert client.delete(f"{WEG}/{b['id']}", headers=kopf(HAUS_A)).status_code == 204
        assert client.get(f"{WEG}/{b['id']}", headers=kopf(HAUS_A)).status_code == 404


# ── 5. Die Lohnwege nennen den Mandanten ────────────────────────────────────


class TestLohnMandant:
    def test_die_berechnung_nennt_den_mandanten(self, client):
        """Vorher wurde `tenant_id` mit `noqa: ARG001` entgegengenommen und verworfen."""
        antwort = client.post(
            f"{LOHN}/berechnung",
            json={"brutto": 3500.0, "steuerklasse": 1},
            headers=kopf(HAUS_A),
        )
        assert antwort.status_code == 200, antwort.text
        assert antwort.json()["mandant"] == HAUS_A

    def test_der_closeout_nennt_den_mandanten(self, client):
        """Eine Uebergabe an DATEV ohne Haus laesst sich dem falschen zuordnen."""
        antwort = client.post(
            f"{LOHN}/closeout-preview",
            json={
                "period": "2026-05",
                "employees": [
                    {"employeeRef": "EMP-1", "gross": 3500.0, "taxClass": 1}
                ],
            },
            headers=kopf(HAUS_A),
        )
        assert antwort.status_code == 200, antwort.text
        assert antwort.json()["mandant"] == HAUS_A

    def test_der_vorbehalt_bleibt(self, client):
        """Die Rechnung ist eine Vorschau — das muss in der Antwort stehen bleiben."""
        antwort = client.post(
            f"{LOHN}/berechnung",
            json={"brutto": 3500.0, "steuerklasse": 1},
            headers=kopf(HAUS_A),
        )
        assert "BMF-PAP" in antwort.json()["hinweis"]

    def test_kein_verworfener_mandant_mehr(self):
        quelle = Path("app/api/v1/endpoints/personal_lohnabrechnung.py").read_text(encoding="utf-8")
        # Keine Signatur traegt die Unterdrueckung mehr; der Docstring darf den
        # alten Stand nennen.
        signaturen = [
            z for z in quelle.splitlines()
            if "noqa: ARG001" in z and "tenant_id" in z and "Depends" in z
        ]
        assert not signaturen, signaturen
        baum = ast.parse(quelle)
        for knoten in ast.walk(baum):
            if isinstance(knoten, ast.AsyncFunctionDef):
                namen = {a.arg for a in knoten.args.args + knoten.args.kwonlyargs}
                if "tenant_id" in namen:
                    koerper = ast.dump(ast.Module(body=knoten.body, type_ignores=[]))
                    assert "tenant_id" in koerper, knoten.name
