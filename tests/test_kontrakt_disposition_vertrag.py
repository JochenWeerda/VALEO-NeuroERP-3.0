"""Abruf kontrahierter Mengen — Tabelle, Menge, Freigabe, Beleg.

Fünf Dinge, die vorher fehlten:

1. **Eine Migration.** `domain_agrar.kontrakt_dispositionen` existierte in keiner
   Datenbank. Angelegt wurde sie vom Anwendungscode beim ersten Schreibzugriff
   (`CREATE TABLE IF NOT EXISTS`), und der Fehlschlag dieses DDL lief in ein
   stilles `except: rollback`. Vor dem ersten POST antwortete das Auflisten `[]`.
2. **Die Mengenprüfung.** Nichts verglich die Summe der Abrufe mit
   `kon_contract_line.qty_contract` — dabei stand die Regel schon im Modell:
   `kon_contract.allow_overdelivery` wurde nie gelesen.
3. **Der Mandant.** Gefiltert wurde nur nach `kontrakt_id`.
4. **Eine Wahrheit über die Freigabe.** Sie stand als Boolean `freigabe` **und**
   als `status = 'FREIGEGEBEN'`.
5. **Zustandsregeln.** Eine stornierte Disposition ließ sich als geliefert
   melden, eine gelieferte stornieren, und geliefert werden konnte ohne Freigabe.

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

HAUS_A = f"dispo-a-{uuid.uuid4().hex[:6]}"
HAUS_B = f"dispo-b-{uuid.uuid4().hex[:6]}"

WEG = "/api/v1/kontrakte"
DISPOSITIONEN = "domain_agrar.kontrakt_dispositionen"
KONTRAKTE = "domain_ops.kon_contract"
ZEILEN = "domain_ops.kon_contract_line"
SCHEINE = "domain_inventory.weighing_tickets"

#: Kontrakt ohne Überlieferung, Position 1 mit 100 t kontrahiert.
KONTRAKT_STRENG = str(uuid.uuid4())
#: Kontrakt mit erlaubter Überlieferung.
KONTRAKT_OFFEN = str(uuid.uuid4())
#: Kontrakt des fremden Hauses.
KONTRAKT_FREMD = str(uuid.uuid4())

WIEGESCHEIN_NR = f"WS-2026-{uuid.uuid4().hex[:6].upper()}"


@pytest.fixture(scope="module")
def engine():
    from sqlalchemy import create_engine, text

    try:
        motor = create_engine(DB_URL)
        with motor.connect() as conn:
            vorhanden = conn.execute(
                text(
                    "SELECT 1 FROM information_schema.tables "
                    "WHERE table_schema='domain_agrar' AND table_name='kontrakt_dispositionen'"
                )
            ).scalar()
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank nicht erreichbar: {fehler}")
    if not vorhanden:
        pytest.skip("Migration kontrakt_disposition_20261005 nicht angewandt")
    return motor


@pytest.fixture(scope="module", autouse=True)
def bestand(engine):
    """Zwei Mandanten, drei Kontrakte, ein Wiegeschein."""
    from sqlalchemy import text

    with engine.begin() as v:
        for haus in (HAUS_A, HAUS_B):
            v.execute(
                text(
                    "INSERT INTO domain_shared.tenants (id, name) VALUES (:id, :name) "
                    "ON CONFLICT (id) DO NOTHING"
                ),
                {"id": haus, "name": f"Pruefhandel {haus}"},
            )
        for kid, haus, nr, ueber in (
            (KONTRAKT_STRENG, HAUS_A, "K-STRENG", False),
            (KONTRAKT_OFFEN, HAUS_A, "K-OFFEN", True),
            (KONTRAKT_FREMD, HAUS_B, "K-FREMD", False),
        ):
            v.execute(
                text(
                    f"INSERT INTO {KONTRAKTE} (contract_id, tenant_id, contract_no, "
                    " contract_type, party_id, contract_date, quantity_type, "
                    " total_quantity, unit, allow_overdelivery, status) "
                    "VALUES (:id, :tid, :nr, 'VERKAUF', 'P-1', '2026-01-01', 'FEST', "
                    "        100, 't', :ueber, 'AKTIV')"
                ),
                {"id": kid, "tid": haus, "nr": nr, "ueber": ueber},
            )
            v.execute(
                text(
                    f"INSERT INTO {ZEILEN} (line_id, contract_id, tenant_id, position_no, "
                    " article_id, qty_contract, is_bio, is_matif) "
                    "VALUES (:lid, :cid, :tid, 1, 'ART-1', 100, FALSE, FALSE)"
                ),
                {"lid": str(uuid.uuid4()), "cid": kid, "tid": haus},
            )
        v.execute(
            text(
                f"INSERT INTO {SCHEINE} (id, tenant_id, ticket_number, gross_weight, "
                " tare_weight, net_weight, direction) "
                "VALUES (:id, :tid, :nr, 30000, 10000, 20000, 'out')"
            ),
            {"id": str(uuid.uuid4()), "tid": HAUS_A, "nr": WIEGESCHEIN_NR},
        )
    yield
    with engine.begin() as v:
        v.execute(
            text(f"DELETE FROM {DISPOSITIONEN} WHERE tenant_id = ANY(:h)"),
            {"h": [HAUS_A, HAUS_B]},
        )
        v.execute(text(f"DELETE FROM {SCHEINE} WHERE tenant_id = ANY(:h)"), {"h": [HAUS_A, HAUS_B]})
        v.execute(text(f"DELETE FROM {ZEILEN} WHERE tenant_id = ANY(:h)"), {"h": [HAUS_A, HAUS_B]})
        v.execute(text(f"DELETE FROM {KONTRAKTE} WHERE tenant_id = ANY(:h)"), {"h": [HAUS_A, HAUS_B]})
        v.execute(
            text("DELETE FROM domain_shared.tenants WHERE id = ANY(:h)"), {"h": [HAUS_A, HAUS_B]}
        )


@pytest.fixture(scope="module")
def client(engine):
    from fastapi.testclient import TestClient

    from app.auth.deps import get_current_user
    from app.main import app

    app.dependency_overrides[get_current_user] = lambda: {
        "sub": "pruefer",
        "roles": ["KONTRAKT_BEARBEITEN", "KONTRAKT_LESEN", "KONTRAKT_ADMIN"],
    }
    mandant = TestClient(app, raise_server_exceptions=False)
    yield mandant
    app.dependency_overrides.pop(get_current_user, None)


def kopf(haus: str) -> dict[str, str]:
    return {"X-Tenant-Id": haus, "Authorization": "Bearer dev-token"}


def abrufen(client, haus: str, kontrakt_id: str, menge: float, **felder):
    nutzlast = {"kontrakt_pos_nr": felder.pop("pos", 1), "menge": menge}
    nutzlast.update(felder)
    return client.post(
        f"{WEG}/{kontrakt_id}/dispositionen", json=nutzlast, headers=kopf(haus)
    )


def freigeben(client, haus: str, kontrakt_id: str, disp_id: str):
    return client.patch(
        f"{WEG}/{kontrakt_id}/dispositionen/{disp_id}/freigabe", headers=kopf(haus)
    )


def liefern(client, haus: str, kontrakt_id: str, disp_id: str, **felder):
    return client.patch(
        f"{WEG}/{kontrakt_id}/dispositionen/{disp_id}/geliefert",
        json=felder,
        headers=kopf(haus),
    )


def stornieren(client, haus: str, kontrakt_id: str, disp_id: str):
    return client.delete(f"{WEG}/{kontrakt_id}/dispositionen/{disp_id}", headers=kopf(haus))


# ── 1. Das Schema statt der Laufzeit-DDL ────────────────────────────────────


class TestSchema:
    def test_tabelle_kommt_aus_der_migration(self, engine):
        from sqlalchemy import text

        with engine.connect() as c:
            spalten = {
                r[0]
                for r in c.execute(
                    text(
                        "SELECT column_name FROM information_schema.columns "
                        "WHERE table_schema='domain_agrar' "
                        "AND table_name='kontrakt_dispositionen'"
                    )
                ).all()
            }
        assert {"tenant_id", "wiegeschein_id", "status", "menge"} <= spalten

    def test_freigabe_ist_keine_spalte(self, engine):
        """Sie stand als Boolean **und** als Zustand — der Lieferweg setzte einen."""
        from sqlalchemy import text

        with engine.connect() as c:
            spalten = {
                r[0]
                for r in c.execute(
                    text(
                        "SELECT column_name FROM information_schema.columns "
                        "WHERE table_schema='domain_agrar' "
                        "AND table_name='kontrakt_dispositionen'"
                    )
                ).all()
            }
        assert "freigabe" not in spalten
        assert "wiegeschein_nr" not in spalten

    def test_kein_create_table_im_anwendungscode(self):
        """Ein Schema gehoert in eine Migration, nicht in den ersten POST."""
        from pathlib import Path

        for pfad in (
            "app/services/kontrakte_service.py",
            "app/services/kontrakt_disposition_service.py",
            "app/api/v1/endpoints/kontrakte.py",
        ):
            quelle = Path(pfad).read_text(encoding="utf-8")
            # Nur echter Code zaehlt; der Kommentar, der den alten Weg
            # beschreibt, darf das Wort nennen.
            anweisungen = [
                z for z in quelle.splitlines() if not z.lstrip().startswith("#")
            ]
            assert not [z for z in anweisungen if "CREATE TABLE" in z.upper()], pfad
        assert "ensure_disposition_table" not in Path(
            "app/services/kontrakte_service.py"
        ).read_text(encoding="utf-8")

    @pytest.mark.parametrize(
        "bedingung",
        [
            "ck_dispo_status",
            "ck_dispo_menge_positiv",
            "ck_dispo_nummer_positiv",
            "ck_dispo_lieferdatum_bei_lieferung",
            "ck_dispo_wiegeschein_nur_bei_lieferung",
            "fk_dispo_wiegeschein",
        ],
    )
    def test_bedingung_vorhanden(self, engine, bedingung):
        from sqlalchemy import text

        with engine.connect() as c:
            assert c.execute(
                text("SELECT 1 FROM pg_constraint WHERE conname = :n"), {"n": bedingung}
            ).scalar() == 1

    def test_lieferdatum_nur_bei_lieferung(self, engine):
        from sqlalchemy import text
        from sqlalchemy.exc import IntegrityError

        with pytest.raises(IntegrityError):
            with engine.begin() as v:
                v.execute(
                    text(
                        f"INSERT INTO {DISPOSITIONEN} (id, tenant_id, kontrakt_id, "
                        " kontrakt_nr, disposition_nr, menge, status, lieferdatum) "
                        "VALUES (:id, :tid, :kid, 'K-X', 999, 5, 'OFFEN', '2026-05-01')"
                    ),
                    {"id": str(uuid.uuid4()), "tid": HAUS_A, "kid": KONTRAKT_STRENG},
                )


# ── 2. Die Kontraktmenge ────────────────────────────────────────────────────


class TestMengenpruefung:
    def test_abruf_innerhalb_der_kontraktmenge(self, client):
        antwort = abrufen(client, HAUS_A, KONTRAKT_STRENG, 40)
        assert antwort.status_code == 201, antwort.text
        assert antwort.json()["menge"] == pytest.approx(40.0)
        assert antwort.json()["status"] == "OFFEN"
        assert antwort.json()["freigabe"] is False

    def test_summe_ueber_der_kontraktmenge_wird_abgewiesen(self, client):
        """Die Regel stand mit `allow_overdelivery` im Modell und wurde nie gelesen."""
        kontrakt = KONTRAKT_STRENG
        assert abrufen(client, HAUS_A, kontrakt, 50).status_code == 201
        antwort = abrufen(client, HAUS_A, kontrakt, 60)
        assert antwort.status_code == 409
        assert "allow_overdelivery" in antwort.text

    def test_ueberlieferung_wenn_der_kontrakt_sie_erlaubt(self, client):
        assert abrufen(client, HAUS_A, KONTRAKT_OFFEN, 90).status_code == 201
        antwort = abrufen(client, HAUS_A, KONTRAKT_OFFEN, 50)
        assert antwort.status_code == 201, antwort.text

    def test_stornierter_abruf_bindet_keine_menge(self, client, engine):
        from sqlalchemy import text

        with engine.begin() as v:
            v.execute(
                text(f"DELETE FROM {DISPOSITIONEN} WHERE kontrakt_id = :k"),
                {"k": KONTRAKT_STRENG},
            )
        erster = abrufen(client, HAUS_A, KONTRAKT_STRENG, 100).json()
        assert abrufen(client, HAUS_A, KONTRAKT_STRENG, 10).status_code == 409
        assert stornieren(client, HAUS_A, KONTRAKT_STRENG, erster["id"]).status_code == 200
        assert abrufen(client, HAUS_A, KONTRAKT_STRENG, 10).status_code == 201

    @pytest.mark.parametrize("menge", [0, -5])
    def test_menge_muss_positiv_sein(self, client, menge):
        assert abrufen(client, HAUS_A, KONTRAKT_OFFEN, menge).status_code == 422

    def test_unbekannte_position_ist_ein_404(self, client):
        assert abrufen(client, HAUS_A, KONTRAKT_OFFEN, 1, pos=99).status_code == 404

    def test_abrufstand_nennt_die_offene_menge(self, client, engine):
        from sqlalchemy import text

        with engine.begin() as v:
            v.execute(
                text(f"DELETE FROM {DISPOSITIONEN} WHERE kontrakt_id = :k"),
                {"k": KONTRAKT_STRENG},
            )
        abrufen(client, HAUS_A, KONTRAKT_STRENG, 30)
        antwort = client.get(f"{WEG}/{KONTRAKT_STRENG}/abrufstand", headers=kopf(HAUS_A))
        assert antwort.status_code == 200, antwort.text
        stand = antwort.json()[0]
        assert stand["menge_kontrahiert"] == pytest.approx(100.0)
        assert stand["menge_abgerufen"] == pytest.approx(30.0)
        assert stand["menge_offen"] == pytest.approx(70.0)
        assert stand["ueberlieferung_erlaubt"] is False


# ── 3. Die Freigabe ist der Zustand ─────────────────────────────────────────


class TestZustaende:
    def _frischer_abruf(self, client) -> dict:
        return abrufen(client, HAUS_A, KONTRAKT_OFFEN, 1).json()

    def test_freigabe_ist_abgeleitet(self, client):
        abruf = self._frischer_abruf(client)
        assert abruf["freigabe"] is False
        frei = freigeben(client, HAUS_A, KONTRAKT_OFFEN, abruf["id"]).json()
        assert frei["status"] == "FREIGEGEBEN"
        assert frei["freigabe"] is True

    def test_lieferung_nur_aus_der_freigabe(self, client):
        """Sonst waere die Freigabe kein Tor, sondern eine Notiz."""
        abruf = self._frischer_abruf(client)
        antwort = liefern(client, HAUS_A, KONTRAKT_OFFEN, abruf["id"])
        assert antwort.status_code == 409
        assert "Freigabe" in antwort.text

    def test_gelieferter_abruf_ist_endgueltig(self, client):
        abruf = self._frischer_abruf(client)
        freigeben(client, HAUS_A, KONTRAKT_OFFEN, abruf["id"])
        assert liefern(
            client, HAUS_A, KONTRAKT_OFFEN, abruf["id"], wiegeschein_nr=WIEGESCHEIN_NR
        ).status_code == 200
        antwort = stornieren(client, HAUS_A, KONTRAKT_OFFEN, abruf["id"])
        assert antwort.status_code == 409
        assert "endgueltig" in antwort.text

    def test_stornierter_abruf_wird_nicht_geliefert(self, client):
        abruf = self._frischer_abruf(client)
        assert stornieren(client, HAUS_A, KONTRAKT_OFFEN, abruf["id"]).status_code == 200
        antwort = liefern(client, HAUS_A, KONTRAKT_OFFEN, abruf["id"])
        assert antwort.status_code == 409

    def test_doppelte_freigabe_wird_abgewiesen(self, client):
        abruf = self._frischer_abruf(client)
        assert freigeben(client, HAUS_A, KONTRAKT_OFFEN, abruf["id"]).status_code == 200
        assert freigeben(client, HAUS_A, KONTRAKT_OFFEN, abruf["id"]).status_code == 409

    def test_uebergangstabelle_ist_die_einzige_quelle(self):
        from app.services import kontrakt_disposition_service as dienst

        assert set(dienst.UEBERGAENGE) == set(dienst.ZUSTAENDE)
        for zustand in dienst.ENDGUELTIG:
            assert dienst.UEBERGAENGE[zustand] == ()
        assert "GELIEFERT" in dienst.UEBERGAENGE["FREIGEGEBEN"]
        assert "GELIEFERT" not in dienst.UEBERGAENGE["OFFEN"]


# ── 4. Der Wiegeschein als Beleg ────────────────────────────────────────────


class TestLieferbeleg:
    def test_lieferung_bindet_den_kanonischen_wiegeschein(self, client, engine):
        from sqlalchemy import text

        abruf = abrufen(client, HAUS_A, KONTRAKT_OFFEN, 1).json()
        freigeben(client, HAUS_A, KONTRAKT_OFFEN, abruf["id"])
        antwort = liefern(
            client, HAUS_A, KONTRAKT_OFFEN, abruf["id"], wiegeschein_nr=WIEGESCHEIN_NR
        )
        assert antwort.status_code == 200, antwort.text
        daten = antwort.json()
        assert daten["status"] == "GELIEFERT"
        assert daten["lieferdatum"] == date.today().isoformat()
        with engine.connect() as c:
            nummer = c.execute(
                text(f"SELECT ticket_number FROM {SCHEINE} WHERE id = :id"),
                {"id": daten["wiegeschein_id"]},
            ).scalar()
        assert nummer == WIEGESCHEIN_NR

    def test_unbekannte_wiegescheinnummer_ist_kein_beleg(self, client):
        abruf = abrufen(client, HAUS_A, KONTRAKT_OFFEN, 1).json()
        freigeben(client, HAUS_A, KONTRAKT_OFFEN, abruf["id"])
        antwort = liefern(
            client, HAUS_A, KONTRAKT_OFFEN, abruf["id"], wiegeschein_nr="WS-GIBT-ES-NICHT"
        )
        assert antwort.status_code == 422
        assert "kein Beleg" in antwort.text

    def test_fremder_wiegeschein_ist_kein_beleg(self, client, engine):
        """Der Schein des anderen Hauses darf die eigene Lieferung nicht belegen."""
        from sqlalchemy import text

        fremde_nr = f"WS-FREMD-{uuid.uuid4().hex[:5].upper()}"
        with engine.begin() as v:
            v.execute(
                text(
                    f"INSERT INTO {SCHEINE} (id, tenant_id, ticket_number, net_weight) "
                    "VALUES (:id, :tid, :nr, 1000)"
                ),
                {"id": str(uuid.uuid4()), "tid": HAUS_B, "nr": fremde_nr},
            )
        abruf = abrufen(client, HAUS_A, KONTRAKT_OFFEN, 1).json()
        freigeben(client, HAUS_A, KONTRAKT_OFFEN, abruf["id"])
        antwort = liefern(client, HAUS_A, KONTRAKT_OFFEN, abruf["id"], wiegeschein_nr=fremde_nr)
        assert antwort.status_code == 422

    def test_lieferung_ohne_wiegeschein_bleibt_moeglich(self, client):
        """Nicht jede Lieferung wird gewogen — aber dann steht auch kein Schein da."""
        abruf = abrufen(client, HAUS_A, KONTRAKT_OFFEN, 1).json()
        freigeben(client, HAUS_A, KONTRAKT_OFFEN, abruf["id"])
        antwort = liefern(client, HAUS_A, KONTRAKT_OFFEN, abruf["id"])
        assert antwort.status_code == 200, antwort.text
        assert antwort.json()["wiegeschein_id"] is None


# ── 5. Der Mandant ──────────────────────────────────────────────────────────


class TestMandantentrennung:
    def test_fremde_abrufe_sind_nicht_lesbar(self, client):
        fremd = abrufen(client, HAUS_B, KONTRAKT_FREMD, 5)
        assert fremd.status_code == 201, fremd.text
        antwort = client.get(f"{WEG}/{KONTRAKT_FREMD}/dispositionen", headers=kopf(HAUS_A))
        assert antwort.status_code == 200
        assert antwort.json() == []

    def test_auf_fremden_kontrakt_wird_nicht_abgerufen(self, client):
        assert abrufen(client, HAUS_A, KONTRAKT_FREMD, 5).status_code == 404

    def test_fremder_abruf_wird_nicht_freigegeben(self, client):
        fremd = abrufen(client, HAUS_B, KONTRAKT_FREMD, 5).json()
        assert freigeben(client, HAUS_A, KONTRAKT_FREMD, fremd["id"]).status_code == 404

    def test_eigene_abrufe_tragen_den_mandanten(self, client):
        abruf = abrufen(client, HAUS_A, KONTRAKT_OFFEN, 1).json()
        assert abruf["tenant_id"] == HAUS_A


# ── 6. Ein Fehler ist keine leere Liste ─────────────────────────────────────


class TestFehlerIstKeinLeererZustand:
    def test_unlesbare_liste_ist_ein_503(self):
        """Vorher: `if "relation" in err: return []` — ein ganz offener Kontrakt."""
        from unittest.mock import MagicMock

        from fastapi import HTTPException

        from app.services import kontrakt_disposition_service as dienst

        db = MagicMock()
        db.execute.side_effect = Exception('relation "kontrakt_dispositionen" does not exist')
        with pytest.raises(Exception) as fehler:
            dienst.auflisten(db, HAUS_A, KONTRAKT_OFFEN, 200)
        assert not isinstance(fehler.value, HTTPException)
        # Der Endpunkt macht daraus ein 503.
        umgewandelt = dienst.nicht_lesbar(db, fehler.value, "Kontraktabrufe", HAUS_A)
        assert umgewandelt.status_code == 503
        assert "migration_hint" in str(umgewandelt.detail)

    def test_antwortmodelle_sind_nicht_offen(self):
        """Vorher hingen alle fuenf Wege an `KontraktOut` mit `extra="allow"`."""
        from app.api.v1.endpoints import kontrakte
        from app.api.v1.schemas.kontrakt_disposition_schemas import (
            AbrufstandOut,
            DispositionOut,
        )

        modelle = [
            getattr(r, "response_model", None)
            for r in kontrakte.router.routes
            if "disposition" in r.path or "abrufstand" in r.path
        ]
        assert all(m in (DispositionOut, list[DispositionOut], list[AbrufstandOut]) for m in modelle), modelle

    def test_unbekanntes_feld_wird_abgewiesen(self, client):
        """`freigabe` und `wiegeschein_nr` bestimmt der Abruf nicht selbst."""
        antwort = client.post(
            f"{WEG}/{KONTRAKT_OFFEN}/dispositionen",
            json={"kontrakt_pos_nr": 1, "menge": 1, "freigabe": True},
            headers=kopf(HAUS_A),
        )
        assert antwort.status_code == 422
