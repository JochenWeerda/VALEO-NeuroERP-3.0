"""Doppelwiegung auf dem kanonischen Wiegeschein.

Vier Dinge, die vorher fehlten:

1. **Eine Tabelle, die es gibt.** Der Weg schrieb `domain_agrar.wiegungen` —
   nicht angelegt, in keiner Datenbank vorhanden. Daneben standen drei weitere
   Wiegetabellen. Geschrieben wird jetzt `domain_inventory.weighing_tickets`,
   das Rückgrat der Rückverfolgbarkeit.
2. **Ein Netto, das stimmt.** `netto = abs(wiegung1 - wiegung2)` verdeckte den
   Vorzeichenfehler: Eine Tara schwerer als das Brutto ist ein Messfehler oder
   eine Verwechslung der Eingaben — und wurde zu einem plausiblen positiven
   Nettogewicht, auf dem die Rechnung aufbaute. Ein bestehender Test forderte
   das ein.
3. **Kein Erfolg ohne Gewicht.** Schlug der INSERT fehl, schrieb der Weg die
   ganze Wiegung als JSONB-Klumpen — ohne Gewicht, ohne Waage — und antwortete
   `201 created`.
4. **Der Mandant.** Weder beim Schreiben noch beim Lesen; `get_wiegung_extended`
   hatte die Abhängigkeit nicht einmal.

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

HAUS_A = f"wieg-a-{uuid.uuid4().hex[:6]}"
HAUS_B = f"wieg-b-{uuid.uuid4().hex[:6]}"

WEG = "/api/v1/waage"
SCHEINE = "domain_inventory.weighing_tickets"


@pytest.fixture(scope="module")
def engine():
    from sqlalchemy import create_engine, text

    try:
        motor = create_engine(DB_URL)
        with motor.connect() as conn:
            spalte = conn.execute(
                text(
                    "SELECT column_name FROM information_schema.columns "
                    "WHERE table_schema='domain_inventory' AND table_name='weighing_tickets' "
                    "AND column_name='handwiegung'"
                )
            ).scalar()
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank nicht erreichbar: {fehler}")
    if not spalte:
        pytest.skip("Migration wiegung_kanonisch_20261005 nicht angewandt")
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
                {"id": haus, "name": f"Pruefwaage {haus}"},
            )
    yield
    with engine.begin() as v:
        v.execute(text(f"DELETE FROM {SCHEINE} WHERE tenant_id = ANY(:h)"), {"h": [HAUS_A, HAUS_B]})
        v.execute(
            text("DELETE FROM domain_shared.tenants WHERE id = ANY(:h)"), {"h": [HAUS_A, HAUS_B]}
        )


@pytest.fixture(scope="module")
def client(engine):
    from fastapi.testclient import TestClient

    from app.main import app

    return TestClient(app, raise_server_exceptions=False)


def kopf(haus: str) -> dict[str, str]:
    return {"X-Tenant-Id": haus, "Authorization": "Bearer dev-token"}


def wiegen(client, haus: str, **felder):
    ext = {
        "waage_id": felder.pop("waage_id", "WA-1"),
        "brutto_kg": felder.pop("brutto_kg", 32500.0),
        "tara_kg": felder.pop("tara_kg", 12500.0),
    }
    for schluessel in ("netto_kg", "gosse", "muster_nr", "handwiegung", "ident_nr", "zielschein_typ"):
        if schluessel in felder:
            ext[schluessel] = felder.pop(schluessel)
    nutzlast = {"waage_id": ext["waage_id"], "wiegung_erweitert": ext}
    nutzlast.update(felder)
    return client.post(f"{WEG}/wiegungen/dual", json=nutzlast, headers=kopf(haus))


# ── 1. Das Schema ───────────────────────────────────────────────────────────


class TestSchema:
    def test_waagenspalten_stehen_auf_dem_kanonischen_schein(self, engine):
        """Ein fünfter Wiegebegriff wäre das Gegenteil von Rückverfolgbarkeit."""
        from sqlalchemy import text

        with engine.connect() as c:
            spalten = {
                r[0]
                for r in c.execute(
                    text(
                        "SELECT column_name FROM information_schema.columns "
                        "WHERE table_schema='domain_inventory' AND table_name='weighing_tickets'"
                    )
                ).all()
            }
        assert {
            "gosse", "muster_nr", "handwiegung", "ident_nr", "disposition_nr", "charge_nr"
        } <= spalten

    def test_domain_agrar_wiegungen_wird_nicht_angelegt(self, engine):
        """Die fehlende Tabelle wird abgelöst, nicht nachgebaut."""
        from sqlalchemy import text

        with engine.connect() as c:
            assert c.execute(
                text(
                    "SELECT 1 FROM information_schema.tables "
                    "WHERE table_schema='domain_agrar' AND table_name='wiegungen'"
                )
            ).scalar() is None

    def test_code_verweist_nicht_mehr_auf_die_fehlende_tabelle(self):
        from pathlib import Path

        quelle = Path("app/api/v1/endpoints/waage.py").read_text(encoding="utf-8")
        for schluesselwort in ("FROM domain_agrar.wiegungen", "INTO domain_agrar.wiegungen"):
            assert schluesselwort not in quelle

    @pytest.mark.parametrize(
        "bedingung",
        [
            "ck_wiegung_netto_stimmt",
            "ck_wiegung_tara_unter_brutto",
            "ck_wiegung_gewichte_nicht_negativ",
            "ck_wiegung_richtung",
        ],
    )
    def test_pruefbedingung_vorhanden(self, engine, bedingung):
        from sqlalchemy import text

        with engine.connect() as c:
            assert c.execute(
                text("SELECT 1 FROM pg_constraint WHERE conname = :n"), {"n": bedingung}
            ).scalar() == 1


class TestDatenbankgrenzen:
    def test_falsches_netto_wird_von_der_datenbank_abgewiesen(self, engine):
        """Das Nettogewicht ist die abgerechnete Menge — es muss der Messung entsprechen."""
        from sqlalchemy import text
        from sqlalchemy.exc import IntegrityError

        with pytest.raises(IntegrityError):
            with engine.begin() as v:
                v.execute(
                    text(
                        f"INSERT INTO {SCHEINE} (id, tenant_id, ticket_number, "
                        "gross_weight, tare_weight, net_weight) "
                        "VALUES (:id, :tid, :nr, 30000, 10000, 25000)"
                    ),
                    {"id": str(uuid.uuid4()), "tid": HAUS_A, "nr": f"X-{uuid.uuid4().hex[:8]}"},
                )

    def test_tara_ueber_brutto_wird_abgewiesen(self, engine):
        from sqlalchemy import text
        from sqlalchemy.exc import IntegrityError

        with pytest.raises(IntegrityError):
            with engine.begin() as v:
                v.execute(
                    text(
                        f"INSERT INTO {SCHEINE} (id, tenant_id, ticket_number, "
                        "gross_weight, tare_weight, net_weight) "
                        "VALUES (:id, :tid, :nr, 10000, 30000, -20000)"
                    ),
                    {"id": str(uuid.uuid4()), "tid": HAUS_A, "nr": f"X-{uuid.uuid4().hex[:8]}"},
                )

    def test_unbekannte_richtung_wird_abgewiesen(self, engine):
        """Eine dritte Richtung ließe die Wiegung aus der Lieferkette fallen."""
        from sqlalchemy import text
        from sqlalchemy.exc import IntegrityError

        with pytest.raises(IntegrityError):
            with engine.begin() as v:
                v.execute(
                    text(
                        f"INSERT INTO {SCHEINE} (id, tenant_id, ticket_number, direction) "
                        "VALUES (:id, :tid, :nr, 'umlagerung')"
                    ),
                    {"id": str(uuid.uuid4()), "tid": HAUS_A, "nr": f"X-{uuid.uuid4().hex[:8]}"},
                )


# ── 2. Das Netto ────────────────────────────────────────────────────────────


class TestNetto:
    def test_netto_ist_brutto_minus_tara(self, client, engine):
        from sqlalchemy import text

        antwort = wiegen(client, HAUS_A, brutto_kg=32500.0, tara_kg=12500.0)
        assert antwort.status_code == 201, antwort.text
        daten = antwort.json()
        assert daten["netto_kg"] == pytest.approx(20000.0)
        with engine.connect() as c:
            zeile = c.execute(
                text(
                    f"SELECT gross_weight, tare_weight, net_weight FROM {SCHEINE} WHERE id = :id"
                ),
                {"id": daten["id"]},
            ).first()
        assert float(zeile[0]) == 32500.0
        assert float(zeile[1]) == 12500.0
        assert float(zeile[2]) == 20000.0

    def test_vertauschte_waegungen_sind_ein_fehler_und_kein_netto(self, client):
        """`abs()` machte daraus ein plausibles Gewicht, auf dem abgerechnet wurde."""
        antwort = wiegen(client, HAUS_A, brutto_kg=12500.0, tara_kg=32500.0)
        assert antwort.status_code == 422
        assert "vertauscht" in antwort.text

    def test_gleiche_waegungen_sind_kein_netto(self, client):
        antwort = wiegen(client, HAUS_A, brutto_kg=20000.0, tara_kg=20000.0)
        assert antwort.status_code == 422

    def test_ohne_gewicht_entsteht_kein_wiegeschein(self, client, engine):
        """Ein Wiegeschein ohne Gewicht ist kein Beleg."""
        from sqlalchemy import text

        antwort = client.post(
            f"{WEG}/wiegungen/dual",
            json={"waage_id": "WA-9", "wiegung_erweitert": {"waage_id": "WA-9"}},
            headers=kopf(HAUS_A),
        )
        assert antwort.status_code == 422
        assert "kein Beleg" in antwort.text
        with engine.connect() as c:
            assert c.execute(
                text(f"SELECT COUNT(*) FROM {SCHEINE} WHERE tenant_id = :t AND scale_id = 'WA-9'"),
                {"t": HAUS_A},
            ).scalar() == 0

    def test_ausgewiesenes_netto_ohne_zwei_waegungen(self, client):
        """Handwiegung oder Fremdwaage: dann gibt es nichts nachzurechnen."""
        antwort = client.post(
            f"{WEG}/wiegungen/dual",
            json={
                "waage_id": "WA-2",
                "wiegung_erweitert": {
                    "waage_id": "WA-2", "netto_kg": 18000.0, "handwiegung": True,
                },
            },
            headers=kopf(HAUS_A),
        )
        assert antwort.status_code == 201, antwort.text
        assert antwort.json()["netto_kg"] == pytest.approx(18000.0)
        assert antwort.json()["handwiegung"] is True

    @pytest.mark.parametrize("netto", [0, -500])
    def test_netto_muss_positiv_sein(self, client, netto):
        antwort = client.post(
            f"{WEG}/wiegungen/dual",
            json={"waage_id": "WA-3", "wiegung_erweitert": {"netto_kg": netto}},
            headers=kopf(HAUS_A),
        )
        assert antwort.status_code == 422


# ── 3. Kein Erfolg ohne Beleg ───────────────────────────────────────────────


class TestKeinStillerRueckfall:
    def test_kein_jsonb_rueckfall_im_code(self):
        """Der Rückfall schrieb die Wiegung als Klumpen und meldete 201."""
        from pathlib import Path

        quelle = Path("app/api/v1/endpoints/waage.py").read_text(encoding="utf-8")
        teil = quelle[quelle.index("Doppelwiegung auf dem kanonischen"):]
        assert "extended_data" not in teil
        assert "JSONB-Fallback" not in teil
        assert not [z for z in teil.splitlines() if z.strip() == "pass"]

    def test_schreibfehler_ist_ein_503_mit_hinweis(self):
        from unittest.mock import MagicMock

        from fastapi import HTTPException

        from app.api.v1.endpoints import waage

        db = MagicMock()
        db.execute.side_effect = Exception("permission denied")
        nutzlast = waage.WiegescheinMitDoppelwiegung(
            waage_id="WA-1",
            wiegung_erweitert=waage.WiegungErweitert(brutto_kg=30000, tara_kg=10000),
        )
        import asyncio

        with pytest.raises(HTTPException) as fehler:
            asyncio.run(waage.create_dual_wiegung(payload=nutzlast, tenant_id=HAUS_A, db=db))
        assert fehler.value.status_code == 503
        assert "migration_hint" in str(fehler.value.detail)
        db.rollback.assert_called()


# ── 4. Der Mandant ──────────────────────────────────────────────────────────


class TestMandantentrennung:
    def test_fremder_wiegeschein_ist_nicht_lesbar(self, client):
        fremd = wiegen(client, HAUS_B).json()
        antwort = client.get(f"{WEG}/wiegungen/{fremd['id']}/extended", headers=kopf(HAUS_A))
        assert antwort.status_code == 404

    def test_eigener_wiegeschein_ist_lesbar(self, client):
        meiner = wiegen(client, HAUS_A, gosse=3, muster_nr="MU-7", ident_nr="ID-9").json()
        antwort = client.get(f"{WEG}/wiegungen/{meiner['id']}/extended", headers=kopf(HAUS_A))
        assert antwort.status_code == 200, antwort.text
        daten = antwort.json()
        assert daten["tenant_id"] == HAUS_A
        assert daten["gosse"] == 3
        assert daten["muster_nr"] == "MU-7"
        assert daten["ident_nr"] == "ID-9"
        assert daten["net_weight"] == pytest.approx(20000.0)

    def test_scheinnummern_laufen_je_mandant(self, client):
        erste = wiegen(client, HAUS_B).json()["ticket_number"]
        zweite = wiegen(client, HAUS_B).json()["ticket_number"]
        assert erste.startswith("WS-") and zweite.startswith("WS-")
        assert int(erste.rsplit("-", 1)[1]) + 1 == int(zweite.rsplit("-", 1)[1])

    def test_schreiben_setzt_den_mandanten(self, client, engine):
        from sqlalchemy import text

        daten = wiegen(client, HAUS_A).json()
        with engine.connect() as c:
            assert c.execute(
                text(f"SELECT tenant_id FROM {SCHEINE} WHERE id = :id"), {"id": daten["id"]}
            ).scalar() == HAUS_A


# ── 5. Richtung und Lieferkette ─────────────────────────────────────────────


class TestRichtung:
    def test_el_ist_ein_zugang(self, client, engine):
        from sqlalchemy import text

        daten = wiegen(client, HAUS_A, zielschein_typ="EL").json()
        assert daten["richtung"] == "in"
        with engine.connect() as c:
            assert c.execute(
                text(f"SELECT direction FROM {SCHEINE} WHERE id = :id"), {"id": daten["id"]}
            ).scalar() == "in"

    def test_vl_ist_ein_abgang(self, client):
        assert wiegen(client, HAUS_A, zielschein_typ="VL").json()["richtung"] == "out"

    def test_unbekannter_zielscheintyp_wird_abgewiesen(self, client):
        antwort = client.post(
            f"{WEG}/wiegungen/dual",
            json={
                "waage_id": "WA-1",
                "wiegung_erweitert": {
                    "brutto_kg": 30000, "tara_kg": 10000, "zielschein_typ": "XX",
                },
            },
            headers=kopf(HAUS_A),
        )
        assert antwort.status_code == 422

    def test_rueckverfolgbarkeit_findet_die_wiegung(self, client, engine):
        """Dieselbe Tabelle, auf die der Lieferketten-Spine zeigt."""
        from sqlalchemy import text

        daten = wiegen(client, HAUS_A, zielschein_typ="EL").json()
        with engine.connect() as c:
            gefunden = c.execute(
                text(
                    "SELECT id, net_weight, direction FROM domain_inventory.weighing_tickets "
                    "WHERE id = :id AND tenant_id = :tid"
                ),
                {"id": daten["id"], "tid": HAUS_A},
            ).first()
        assert gefunden is not None
        assert float(gefunden[1]) == pytest.approx(20000.0)
        assert gefunden[2] == "in"


class TestVokabular:
    def test_richtungsabbildung_hat_eine_quelle(self):
        from app.services import wiegung_service as dienst

        assert set(dienst.RICHTUNG_JE_ZIELSCHEIN.values()) <= set(dienst.RICHTUNGEN)
        assert dienst.RICHTUNG_JE_ZIELSCHEIN == {"EL": "in", "VL": "out"}

    def test_unbekanntes_feld_wird_abgewiesen(self, client):
        """Ein Tippfehler darf nicht als stille Nichtangabe durchgehen."""
        antwort = client.post(
            f"{WEG}/wiegungen/dual",
            json={
                "waage_id": "WA-1",
                "wiegung_erweitert": {"brutto_kg": 30000, "tara_kg": 10000, "wiegung1": 30000},
            },
            headers=kopf(HAUS_A),
        )
        assert antwort.status_code == 422

    def test_antwortmodelle_sind_nicht_offen(self):
        """`WaageOut` mit `extra="allow"` hing an beiden Wegen."""
        from app.api.v1.endpoints import waage
        from app.api.v1.schemas.waage_schemas import WiegescheinOut, WiegungAngelegt

        modelle = {
            r.path: getattr(r, "response_model", None)
            for r in waage.router.routes
            if "dual" in r.path or "extended" in r.path
        }
        assert set(modelle.values()) == {WiegungAngelegt, WiegescheinOut}
