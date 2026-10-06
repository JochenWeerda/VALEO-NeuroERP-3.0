"""Die Einwilligungserklaerung in Fassungen — welchem Wortlaut zugestimmt wurde.

Bis hierher trug jede Erteilung ihren Wortlaut als freien Text. Jede Erteilung
konnte einen anderen Text haben, und niemand merkte es; ein Tippfehler im
Personalbuero erzeugte still eine neue "Erklaerung". Nachweisbar (Art. 7 Abs. 1
DSGVO) ist eine Einwilligung erst, wenn feststeht, **welcher Fassung** zugestimmt
wurde — und dass diese Fassung sich seitdem nicht geaendert hat.

Was diese Vertraege festhalten:

* Fassungen sind je Mandant **fortlaufend** (1, 2, 3 …), auch wenn zwei
  gleichzeitig angelegt werden.
* Derselbe Wortlaut ist **eine** Fassung — ein zweites Anlegen sagt, welche es ist.
* Eine Fassung ist **unveraenderlich**, und zwar in der Datenbank: Wer sie aendert,
  aendert rueckwirkend, wozu alle frueheren Bewerber eingewilligt haben.
* Eine Fassung, auf die eine Erteilung verweist, ist nicht loeschbar; eine nie
  benutzte schon — sie belegt nichts.
* Erteilt wird gegen eine **Fassung des eigenen Mandanten**; eine unbekannte oder
  fremde wird abgewiesen, ohne etwas zu schreiben.
* Die Tabelle traegt **keinen Personenbezug**.

Geprueft wird gegen die gemeinsame, vorhandene Pruefstand-Datenbank.
"""

from __future__ import annotations

import os
import uuid
from concurrent.futures import ThreadPoolExecutor
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

HAUS_A = f"erk-a-{uuid.uuid4().hex[:6]}"
HAUS_B = f"erk-b-{uuid.uuid4().hex[:6]}"

WEG = "/api/v1/personal/applications"
ERKLAERUNGEN_WEG = f"{WEG}/einwilligungserklaerungen"

BEWERBUNGEN = "domain_hr.applications"
VERZEICHNIS = "domain_hr.bewerbung_einwilligungen"
ERKLAERUNGEN = "domain_hr.bewerbung_einwilligungserklaerungen"

WORTLAUT_1 = (
    "Ich bin damit einverstanden, dass meine Bewerbungsunterlagen fuer kuenftige "
    "Stellenangebote aufbewahrt werden."
)
WORTLAUT_2 = (
    "Ich bin damit einverstanden, dass meine Bewerbungsunterlagen bis zu drei Jahre "
    "fuer kuenftige Stellenangebote aufbewahrt werden. Ich kann jederzeit widerrufen."
)


@pytest.fixture(scope="module")
def engine():
    from sqlalchemy import create_engine, text

    try:
        motor = create_engine(DB_URL)
        with motor.connect() as conn:
            tabelle = conn.execute(
                text("SELECT to_regclass('domain_hr.bewerbung_einwilligungserklaerungen')")
            ).scalar()
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank nicht erreichbar: {fehler}")
    if not tabelle:
        pytest.skip("Migration bewerbung_erklaerung_fassung_20261006 nicht angewandt")
    return motor


def aufraeumen(engine):
    from sqlalchemy import text

    with engine.begin() as v:
        # Erst die Vorgaenge (sie verweisen auf die Fassungen), dann die Fassungen.
        for tabelle in (VERZEICHNIS, BEWERBUNGEN, ERKLAERUNGEN):
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


def fassung_anlegen(client, haus: str, wortlaut: str = WORTLAUT_1):
    return client.post(
        ERKLAERUNGEN_WEG,
        json={"wortlaut": wortlaut, "erstellt_durch": "Personalbuero"},
        headers=kopf(haus),
    )


def bewerbung_anlegen(engine, haus: str) -> str:
    from sqlalchemy import text

    kennung = str(uuid.uuid4())
    with engine.begin() as v:
        v.execute(
            text(
                f"INSERT INTO {BEWERBUNGEN} "  # nosec B608
                "(id, tenant_id, applicant_name, applicant_email, status, applied_at) "
                "VALUES (:id, :tid, :name, :mail, 'EINGANG', NOW())"
            ),
            {
                "id": kennung,
                "tid": haus,
                "name": f"Bewerber {kennung[:6]}",
                "mail": f"{kennung[:6]}@example.org",
            },
        )
    return kennung


def erteilen(client, haus: str, bewerbung_id: str, fassung):
    return client.post(
        f"{WEG}/{bewerbung_id}/einwilligung",
        json={
            "gueltig_bis": (date.today() + timedelta(days=365)).isoformat(),
            "kanal": "PAPIER",
            "fassung": fassung,
        },
        headers=kopf(haus),
    )


def zaehlen(engine, tabelle: str, haus: str) -> int:
    from sqlalchemy import text

    with engine.connect() as v:
        return v.execute(
            text(f"SELECT COUNT(*) FROM {tabelle} WHERE tenant_id = :h"),  # nosec B608
            {"h": haus},
        ).scalar()


def erklaerung_id(engine, haus: str, fassung: int) -> str:
    from sqlalchemy import text

    with engine.connect() as v:
        return v.execute(
            text(
                f"SELECT id FROM {ERKLAERUNGEN} "  # nosec B608
                "WHERE tenant_id = :h AND fassung = :f"
            ),
            {"h": haus, "f": fassung},
        ).scalar()


# ── 1. Fassungen sind je Mandant fortlaufend ────────────────────────────────


class TestFassungen:
    def test_die_erste_fassung_ist_eins(self, client):
        antwort = fassung_anlegen(client, HAUS_A)
        assert antwort.status_code == 201
        daten = antwort.json()
        assert daten["fassung"] == 1
        assert daten["wortlaut"] == WORTLAUT_1
        assert daten["erstellt_durch"] == "Personalbuero"
        assert daten["erstellt_am"]

    def test_ein_neuer_wortlaut_ist_die_naechste_fassung(self, client):
        fassung_anlegen(client, HAUS_A, WORTLAUT_1)
        assert fassung_anlegen(client, HAUS_A, WORTLAUT_2).json()["fassung"] == 2

    def test_jeder_mandant_zaehlt_fuer_sich(self, client):
        fassung_anlegen(client, HAUS_A, WORTLAUT_1)
        fassung_anlegen(client, HAUS_A, WORTLAUT_2)
        assert fassung_anlegen(client, HAUS_B, WORTLAUT_2).json()["fassung"] == 1

    def test_gleichzeitig_angelegt_bleibt_lueckenlos(self, engine):
        """Zwei Sachbearbeiter, ein Augenblick: keine doppelte, keine fehlende Nummer."""
        from sqlalchemy.orm import sessionmaker

        from app.services import bewerbung_einwilligung_service as dienst

        sitzungen = sessionmaker(bind=engine)

        def anlegen(nummer: int) -> int:
            with sitzungen() as db:
                ergebnis = dienst.erklaerung_anlegen(
                    db, HAUS_A, str(uuid.uuid4()), f"{WORTLAUT_1} (Variante {nummer})", None
                )
                db.commit()
                return ergebnis["fassung"]

        with ThreadPoolExecutor(max_workers=6) as pool:
            fassungen = sorted(pool.map(anlegen, range(6)))
        assert fassungen == [1, 2, 3, 4, 5, 6]

    def test_derselbe_wortlaut_ist_eine_fassung(self, client, engine):
        fassung_anlegen(client, HAUS_A, WORTLAUT_1)
        # Randleerzeichen machen keinen anderen Text.
        antwort = fassung_anlegen(client, HAUS_A, f"  {WORTLAUT_1}\n")
        assert antwort.status_code == 409
        # Wer anlegen wollte, will wissen, welche es schon gibt.
        assert antwort.json()["detail"]["fassung"] == 1
        assert zaehlen(engine, ERKLAERUNGEN, HAUS_A) == 1

    @pytest.mark.parametrize("wortlaut", ["", "   ", "\n\t"])
    def test_ohne_wortlaut_keine_fassung(self, client, engine, wortlaut):
        assert fassung_anlegen(client, HAUS_A, wortlaut).status_code == 422
        assert zaehlen(engine, ERKLAERUNGEN, HAUS_A) == 0

    def test_unbekanntes_feld_abgewiesen(self, client):
        antwort = client.post(
            ERKLAERUNGEN_WEG,
            json={"wortlaut": WORTLAUT_1, "fassung": 7},
            headers=kopf(HAUS_A),
        )
        # Die Nummer vergibt das System; wer sie mitschickt, wird nicht still
        # ueberstimmt.
        assert antwort.status_code == 422


# ── 2. Lesen ────────────────────────────────────────────────────────────────


class TestLesen:
    def test_die_liste_zeigt_die_neueste_zuerst(self, client):
        fassung_anlegen(client, HAUS_A, WORTLAUT_1)
        fassung_anlegen(client, HAUS_A, WORTLAUT_2)
        antwort = client.get(ERKLAERUNGEN_WEG, headers=kopf(HAUS_A))
        # Der Weg steht vor `/applications/{application_id}`; sonst laese der
        # Platzhalter "einwilligungserklaerungen" als Bewerbungskennung.
        assert antwort.status_code == 200
        assert [e["fassung"] for e in antwort.json()] == [2, 1]

    def test_eine_fassung_lesen(self, client):
        fassung_anlegen(client, HAUS_A, WORTLAUT_1)
        antwort = client.get(f"{ERKLAERUNGEN_WEG}/1", headers=kopf(HAUS_A))
        assert antwort.status_code == 200
        assert antwort.json()["wortlaut"] == WORTLAUT_1

    def test_unbekannte_fassung_404(self, client):
        assert client.get(f"{ERKLAERUNGEN_WEG}/9", headers=kopf(HAUS_A)).status_code == 404

    def test_fremde_fassung_unsichtbar(self, client):
        fassung_anlegen(client, HAUS_A, WORTLAUT_1)
        assert client.get(f"{ERKLAERUNGEN_WEG}/1", headers=kopf(HAUS_B)).status_code == 404
        assert client.get(ERKLAERUNGEN_WEG, headers=kopf(HAUS_B)).json() == []


# ── 3. Erteilt wird gegen eine Fassung ──────────────────────────────────────


class TestErteilenGegenFassung:
    def test_die_erteilung_nennt_fassung_und_wortlaut(self, client, engine):
        fassung_anlegen(client, HAUS_A, WORTLAUT_1)
        fassung_anlegen(client, HAUS_A, WORTLAUT_2)
        kennung = bewerbung_anlegen(engine, HAUS_A)
        antwort = erteilen(client, HAUS_A, kennung, 1)
        assert antwort.status_code == 201
        daten = antwort.json()
        # Auch eine aeltere Fassung ist zulaessig: Wer ein frueher gedrucktes
        # Formular unterschrieben hat, hat **diesem** Text zugestimmt.
        assert daten["fassung"] == 1
        assert daten["einwilligungstext"] == WORTLAUT_1
        stand = client.get(f"{WEG}/{kennung}/einwilligung", headers=kopf(HAUS_A)).json()
        assert stand["vorgaenge"][0]["fassung"] == 1
        assert stand["vorgaenge"][0]["einwilligungstext"] == WORTLAUT_1

    @pytest.mark.parametrize("fassung", [None, 0, 3])
    def test_ohne_gueltige_fassung_wird_nichts_geschrieben(self, client, engine, fassung):
        fassung_anlegen(client, HAUS_A, WORTLAUT_1)
        kennung = bewerbung_anlegen(engine, HAUS_A)
        assert erteilen(client, HAUS_A, kennung, fassung).status_code == 422
        assert zaehlen(engine, VERZEICHNIS, HAUS_A) == 0

    def test_die_fassung_eines_fremden_mandanten_gilt_nicht(self, client, engine):
        fassung_anlegen(client, HAUS_B, WORTLAUT_1)
        kennung = bewerbung_anlegen(engine, HAUS_A)
        antwort = erteilen(client, HAUS_A, kennung, 1)
        assert antwort.status_code == 422
        assert "Fassung" in str(antwort.json()["detail"])
        assert zaehlen(engine, VERZEICHNIS, HAUS_A) == 0

    def test_freier_text_wird_nicht_mehr_angenommen(self, client, engine):
        fassung_anlegen(client, HAUS_A, WORTLAUT_1)
        kennung = bewerbung_anlegen(engine, HAUS_A)
        antwort = client.post(
            f"{WEG}/{kennung}/einwilligung",
            json={
                "gueltig_bis": (date.today() + timedelta(days=30)).isoformat(),
                "kanal": "WEB",
                "fassung": 1,
                "einwilligungstext": "Ein anderer Text",
            },
            headers=kopf(HAUS_A),
        )
        # Zwei Quellen fuer den Wortlaut waeren genau die stille Abweichung, die
        # dieser Slice beseitigt.
        assert antwort.status_code == 422


# ── 4. Die Datenbank haelt die Fassung fest ─────────────────────────────────


class TestDatenbank:
    @pytest.mark.parametrize(
        "zuweisung",
        ["wortlaut = wortlaut || ' (ergaenzt)'", "fassung = fassung + 10", "erstellt_durch = 'jemand'"],
    )
    def test_eine_fassung_ist_unveraenderlich(self, client, engine, zuweisung):
        from sqlalchemy import text
        from sqlalchemy.exc import DBAPIError

        fassung_anlegen(client, HAUS_A, WORTLAUT_1)
        with pytest.raises(DBAPIError, match="unveraenderlich"):
            with engine.begin() as v:
                v.execute(
                    text(f"UPDATE {ERKLAERUNGEN} SET {zuweisung} WHERE tenant_id = :h"),  # nosec B608
                    {"h": HAUS_A},
                )

    def test_eine_benutzte_fassung_ist_nicht_loeschbar(self, client, engine):
        from sqlalchemy import text
        from sqlalchemy.exc import IntegrityError

        fassung_anlegen(client, HAUS_A, WORTLAUT_1)
        kennung = bewerbung_anlegen(engine, HAUS_A)
        assert erteilen(client, HAUS_A, kennung, 1).status_code == 201
        with pytest.raises(IntegrityError):
            with engine.begin() as v:
                v.execute(
                    text(f"DELETE FROM {ERKLAERUNGEN} WHERE tenant_id = :h"),  # nosec B608
                    {"h": HAUS_A},
                )

    def test_eine_nie_benutzte_fassung_ist_loeschbar(self, client, engine):
        from sqlalchemy import text

        fassung_anlegen(client, HAUS_A, WORTLAUT_1)
        with engine.begin() as v:
            v.execute(
                text(f"DELETE FROM {ERKLAERUNGEN} WHERE tenant_id = :h"),  # nosec B608
                {"h": HAUS_A},
            )
        assert zaehlen(engine, ERKLAERUNGEN, HAUS_A) == 0

    def test_mit_der_bewerbung_bleibt_die_fassung(self, client, engine):
        from sqlalchemy import text

        # Die Fassung haelt keinen Menschen; sie ist der Text, dem andere noch
        # zugestimmt haben koennen.
        fassung_anlegen(client, HAUS_A, WORTLAUT_1)
        kennung = bewerbung_anlegen(engine, HAUS_A)
        erteilen(client, HAUS_A, kennung, 1)
        with engine.begin() as v:
            v.execute(
                text(f"DELETE FROM {BEWERBUNGEN} WHERE id = :id"),  # nosec B608
                {"id": kennung},
            )
        assert zaehlen(engine, VERZEICHNIS, HAUS_A) == 0
        assert zaehlen(engine, ERKLAERUNGEN, HAUS_A) == 1

    @pytest.mark.parametrize(
        "werte,warum",
        [
            ("'ERTEILT', CURRENT_DATE + 10, 'WEB', NULL", "Erteilung ohne Fassung"),
            ("'WIDERRUFEN', NULL, NULL, :e", "Widerruf mit Fassung"),
        ],
    )
    def test_erteilung_genau_dann_mit_fassung(self, client, engine, werte, warum):
        from sqlalchemy import text
        from sqlalchemy.exc import IntegrityError

        fassung_anlegen(client, HAUS_A, WORTLAUT_1)
        kennung = bewerbung_anlegen(engine, HAUS_A)
        with pytest.raises(IntegrityError):
            with engine.begin() as v:
                v.execute(
                    text(
                        f"INSERT INTO {VERZEICHNIS} "  # nosec B608
                        "(id, tenant_id, bewerbung_id, vorgang, gueltig_bis, kanal, "
                        " erklaerung_id) "
                        f"VALUES (:id, :t, :b, {werte})"
                    ),
                    {
                        "id": str(uuid.uuid4()),
                        "t": HAUS_A,
                        "b": kennung,
                        "e": erklaerung_id(engine, HAUS_A, 1),
                    },
                )

    def test_die_datenbank_verlangt_einen_wortlaut(self, engine):
        from sqlalchemy import text
        from sqlalchemy.exc import IntegrityError

        with pytest.raises(IntegrityError):
            with engine.begin() as v:
                v.execute(
                    text(
                        f"INSERT INTO {ERKLAERUNGEN} (id, tenant_id, fassung, wortlaut) "  # nosec B608
                        "VALUES (:id, :h, 1, '   ')"
                    ),
                    {"id": str(uuid.uuid4()), "h": HAUS_A},
                )

    def test_kein_personenbezug_in_der_fassung(self, engine):
        from sqlalchemy import text

        with engine.connect() as v:
            spalten = {
                z[0]
                for z in v.execute(
                    text(
                        "SELECT column_name FROM information_schema.columns "
                        "WHERE table_schema = 'domain_hr' "
                        "AND table_name = 'bewerbung_einwilligungserklaerungen'"
                    )
                )
            }
        assert spalten == {
            "id", "tenant_id", "fassung", "wortlaut", "erstellt_am", "erstellt_durch"
        }

    def test_der_freie_text_ist_entfallen(self, engine):
        from sqlalchemy import text

        # Der Wortlaut steht an **einer** Stelle.
        with engine.connect() as v:
            vorhanden = v.execute(
                text(
                    "SELECT COUNT(*) FROM information_schema.columns "
                    "WHERE table_schema = 'domain_hr' "
                    "AND table_name = 'bewerbung_einwilligungen' "
                    "AND column_name = 'einwilligungstext'"
                )
            ).scalar()
        assert vorhanden == 0


# ── 5. Montage ──────────────────────────────────────────────────────────────


class TestMontage:
    def test_kein_weg_aendert_oder_loescht_eine_fassung(self):
        from app.main import app

        methoden: dict[str, set] = {}
        for r in app.routes:
            pfad = getattr(r, "path", "")
            if pfad.startswith(ERKLAERUNGEN_WEG):
                methoden.setdefault(pfad, set()).update(getattr(r, "methods", set()))
        assert methoden == {
            ERKLAERUNGEN_WEG: {"GET", "POST"},
            f"{ERKLAERUNGEN_WEG}/{{fassung}}": {"GET"},
        }

    def test_die_wege_stehen_vor_dem_platzhalter(self):
        from app.main import app

        pfade = [getattr(r, "path", "") for r in app.routes]
        platzhalter = pfade.index(f"{WEG}/{{application_id}}")
        assert pfade.index(ERKLAERUNGEN_WEG) < platzhalter
        assert pfade.index(f"{ERKLAERUNGEN_WEG}/{{fassung}}") < platzhalter
