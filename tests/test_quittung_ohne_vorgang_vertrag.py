"""Ein Weg darf nicht quittieren, was er nicht getan hat.

Drei Wege antworteten mit einer Bestätigung und taten nichts:

1. `POST /schaeden/meldungen` → `201`, Meldungsnummer, `status: "gemeldet"` —
   **kein INSERT**. `GET /schaeden/meldungen` lieferte eine erfundene
   Hagelschadenmeldung über 12.500 € mit Zeuge „Hans Müller", die Versicherungs­liste
   vier erfundene Verträge.
2. `POST /etiketten/druckauftrag` → `201`, Auftragsnummer, `status: "erstellt"` —
   kein INSERT, kein Druck. Drucker standen als Literale im Code, jede
   Druckerkennung ging durch.
3. `POST /gelangensbestaetigung/{id}/mahnung` → `erinnerung_gesendet:
   true` — „Stub: In production this would send email/fax".

Das ist nicht derselbe Fehler wie eine fehlende Tabelle: Dort antwortet der Weg
503 und jemand merkt es. Hier hat ein Haus eine Meldungsnummer in der Hand und
meldet deshalb nicht noch einmal, während die Frist nach § 30 Abs. 1 VVG läuft.

Geprüft wird gegen die gemeinsame, vorhandene Prüfstand-Datenbank.
"""

from __future__ import annotations

import os
import uuid
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

HAUS_A = f"quitt-a-{uuid.uuid4().hex[:6]}"
HAUS_B = f"quitt-b-{uuid.uuid4().hex[:6]}"

SCHADEN = "/api/v1/schaeden"
ETIKETT = "/api/v1/etiketten"
GELANGEN = "/api/v1/gelangensbestaetigung"

MELDUNGEN = "domain_erp.schaden_meldungen"
VERSICHERUNGEN = "domain_erp.versicherungen"
AUFTRAEGE = "domain_erp.druckauftraege"
DRUCKER = "domain_erp.drucker"
BESTAETIGUNGEN = "domain_compliance.gelangensbestaetigung"


@pytest.fixture(scope="module")
def engine():
    from sqlalchemy import create_engine, text

    try:
        motor = create_engine(DB_URL)
        with motor.connect() as conn:
            vorhanden = conn.execute(
                text(
                    "SELECT 1 FROM information_schema.tables "
                    "WHERE table_schema='domain_erp' AND table_name='schaden_meldungen'"
                )
            ).scalar()
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank nicht erreichbar: {fehler}")
    if not vorhanden:
        pytest.skip("Migration quittung_ohne_vorgang_20261006 nicht angewandt")
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
        for tabelle in (AUFTRAEGE, DRUCKER, MELDUNGEN, VERSICHERUNGEN, BESTAETIGUNGEN):
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
        for tabelle in (AUFTRAEGE, DRUCKER, MELDUNGEN, VERSICHERUNGEN):
            v.execute(
                text(f"DELETE FROM {tabelle} WHERE tenant_id = ANY(:h)"),
                {"h": [HAUS_A, HAUS_B]},
            )
    yield


@pytest.fixture(scope="module")
def client(engine):
    from fastapi.testclient import TestClient

    from app.main import app

    return TestClient(app, raise_server_exceptions=False)


def kopf(haus: str) -> dict[str, str]:
    return {"X-Tenant-ID": haus, "Authorization": "Bearer dev-token"}


def zahl(wert) -> float:
    return float(wert)


def versicherung(client, haus: str, **felder):
    nutzlast = {
        "bezeichnung": felder.pop("bezeichnung", "Vereinigte Hagel"),
        "vertragsnummer": felder.pop("vertragsnummer", f"VH-{uuid.uuid4().hex[:8]}"),
        "typ": felder.pop("typ", "hagel"),
        "versicherer": felder.pop("versicherer", "Vereinigte Hagelversicherung VVaG"),
    }
    nutzlast.update(felder)
    return client.post(f"{SCHADEN}/versicherungen", json=nutzlast, headers=kopf(haus))


def meldung(client, haus: str, **felder):
    nutzlast = {
        "art": felder.pop("art", "hagel"),
        "schadendatum": felder.pop("schadendatum", date.today().isoformat()),
        "beschreibung": felder.pop("beschreibung", "Hagelschaden am Winterweizen"),
        "schadenhoehe": felder.pop("schadenhoehe", 12500.0),
    }
    nutzlast.update(felder)
    return client.post(f"{SCHADEN}/meldungen", json=nutzlast, headers=kopf(haus))


def drucker(client, haus: str, **felder):
    nutzlast = {"name": felder.pop("name", f"Zebra ZT230 {uuid.uuid4().hex[:4]}")}
    nutzlast.update(felder)
    return client.post(f"{ETIKETT}/drucker", json=nutzlast, headers=kopf(haus))


def auftrag(client, haus: str, drucker_id: str, **felder):
    nutzlast = {
        "chargen_id": felder.pop("chargen_id", f"CH-{uuid.uuid4().hex[:6]}"),
        "drucker_id": drucker_id,
        "anzahl_etiketten": felder.pop("anzahl_etiketten", 4),
    }
    nutzlast.update(felder)
    return client.post(f"{ETIKETT}/druckauftrag", json=nutzlast, headers=kopf(haus))


# ── 1. Was geschrieben wird, ist auch da ────────────────────────────────────


class TestSchreibenUndWiederfinden:
    def test_schadenmeldung_wird_gespeichert(self, engine, client):
        """Vorher: `201` mit Meldungsnummer, und kein INSERT."""
        from sqlalchemy import text

        antwort = meldung(client, HAUS_A)
        assert antwort.status_code == 201, antwort.text
        daten = antwort.json()
        with engine.connect() as c:
            zeile = c.execute(
                text(f"SELECT meldungsnummer, status, schadenhoehe FROM {MELDUNGEN} WHERE id = :id"),
                {"id": daten["id"]},
            ).first()
        assert zeile is not None
        assert zeile[0] == daten["meldungsnummer"]
        assert zeile[1] == "ENTWURF"
        assert float(zeile[2]) == pytest.approx(12500.0)

    def test_liste_zeigt_genau_das_geschriebene(self, client):
        """Vorher stand hier eine erfundene Meldung ueber 12.500 EUR."""
        leer = client.get(f"{SCHADEN}/meldungen", headers=kopf(HAUS_A))
        assert leer.status_code == 200
        assert leer.json() == []

        angelegt = meldung(client, HAUS_A, beschreibung="Frostschaden Raps").json()
        liste = client.get(f"{SCHADEN}/meldungen", headers=kopf(HAUS_A)).json()
        assert [z["id"] for z in liste] == [angelegt["id"]]
        assert liste[0]["beschreibung"] == "Frostschaden Raps"

    def test_versicherungsliste_ist_leer_statt_erfunden(self, client):
        """Vorher: vier Vertraege mit Vertragsnummern, die es nicht gab."""
        antwort = client.get(f"{SCHADEN}/versicherungen", headers=kopf(HAUS_A))
        assert antwort.status_code == 200
        assert antwort.json() == []

        angelegt = versicherung(client, HAUS_A).json()
        liste = client.get(f"{SCHADEN}/versicherungen", headers=kopf(HAUS_A)).json()
        assert [z["id"] for z in liste] == [angelegt["id"]]

    def test_druckauftrag_wird_gespeichert(self, engine, client):
        from sqlalchemy import text

        drk = drucker(client, HAUS_A).json()
        antwort = auftrag(client, HAUS_A, drk["id"])
        assert antwort.status_code == 201, antwort.text
        daten = antwort.json()
        with engine.connect() as c:
            zeile = c.execute(
                text(f"SELECT auftrags_nr, status, anzahl_etiketten FROM {AUFTRAEGE} WHERE id = :id"),
                {"id": daten["id"]},
            ).first()
        assert zeile is not None
        assert zeile[0] == daten["auftrags_nr"]
        assert zeile[1] == "ANGELEGT"
        assert zeile[2] == 4

    def test_druckerliste_ist_leer_statt_erfunden(self, client):
        """Vorher: drei Drucker mit IP-Adressen und Status "online"."""
        antwort = client.get(f"{ETIKETT}/drucker", headers=kopf(HAUS_A))
        assert antwort.status_code == 200
        assert antwort.json() == []

    def test_kein_weg_antwortet_aus_einer_literalliste(self):
        """Die Bestandsfassung hatte die Antworten im Code stehen."""
        from pathlib import Path

        for pfad in (
            "app/api/v1/endpoints/schaeden.py",
            "app/api/v1/endpoints/etiketten.py",
        ):
            quelle = Path(pfad).read_text(encoding="utf-8")
            # Die Spuren der Literallisten: erfundene Kennungen, erfundene
            # Namen, der Hinweis "Demo data". Der Satz "In production" steht
            # bewusst noch im Docstring, der den alten Weg beschreibt.
            for spur in ("Demo data", "vers-001", "drk-001", "Hans Müller", "VH-2024"):
                assert spur not in quelle, f"{pfad}: {spur}"


# ── 2. Die Meldung behauptet nicht, gemeldet zu haben ───────────────────────


class TestMeldungIstEinSchritt:
    def test_anlegen_erzeugt_einen_entwurf(self, client):
        """Vorher antwortete das Anlegen `status: "gemeldet"`."""
        daten = meldung(client, HAUS_A).json()
        assert daten["status"] == "ENTWURF"
        assert daten["gemeldet_am"] is None

    def test_melden_haelt_wann_wer_und_wie_fest(self, client):
        vers = versicherung(client, HAUS_A, meldefrist_tage=4).json()
        m = meldung(client, HAUS_A, versicherung_id=vers["id"]).json()
        antwort = client.post(
            f"{SCHADEN}/meldungen/{m['id']}/melden",
            json={"meldeweg": "TELEFON", "gemeldet_durch": "J. Weerda"},
            headers=kopf(HAUS_A),
        )
        assert antwort.status_code == 200, antwort.text
        daten = antwort.json()
        assert daten["status"] == "GEMELDET"
        assert daten["gemeldet_am"] is not None
        assert daten["gemeldet_durch"] == "J. Weerda"
        assert daten["meldeweg"] == "TELEFON"

    def test_melden_ohne_vertrag_wird_abgewiesen(self, client):
        """Ohne Vertrag ist nicht feststellbar, wem gemeldet wurde und welche Frist galt."""
        m = meldung(client, HAUS_A).json()
        antwort = client.post(
            f"{SCHADEN}/meldungen/{m['id']}/melden",
            json={"meldeweg": "EMAIL"},
            headers=kopf(HAUS_A),
        )
        assert antwort.status_code == 409
        assert "Versicherungsvertrag" in antwort.text

    def test_unbekannter_meldeweg_wird_abgewiesen(self, client):
        vers = versicherung(client, HAUS_A).json()
        m = meldung(client, HAUS_A, versicherung_id=vers["id"]).json()
        antwort = client.post(
            f"{SCHADEN}/meldungen/{m['id']}/melden",
            json={"meldeweg": "BRIEFTAUBE"},
            headers=kopf(HAUS_A),
        )
        assert antwort.status_code == 422

    def test_doppeltes_melden_wird_abgewiesen(self, client):
        vers = versicherung(client, HAUS_A).json()
        m = meldung(client, HAUS_A, versicherung_id=vers["id"]).json()
        erst = client.post(
            f"{SCHADEN}/meldungen/{m['id']}/melden", json={"meldeweg": "POST"},
            headers=kopf(HAUS_A),
        )
        assert erst.status_code == 200
        zweit = client.post(
            f"{SCHADEN}/meldungen/{m['id']}/melden", json={"meldeweg": "POST"},
            headers=kopf(HAUS_A),
        )
        assert zweit.status_code == 409

    def test_gemeldet_ohne_zeitpunkt_ist_in_der_datenbank_unmoeglich(self, engine, client):
        from sqlalchemy import text
        from sqlalchemy.exc import IntegrityError

        m = meldung(client, HAUS_A).json()
        with pytest.raises(IntegrityError):
            with engine.begin() as v:
                v.execute(
                    text(f"UPDATE {MELDUNGEN} SET status = 'GEMELDET' WHERE id = :id"),
                    {"id": m["id"]},
                )


class TestMeldefrist:
    def test_frist_folgt_dem_vertrag(self, client):
        """Eine Frist im Code wuerde fuer alle Policen gleich gelten."""
        vers = versicherung(client, HAUS_A, meldefrist_tage=4).json()
        schaden_tag = date.today() - timedelta(days=1)
        m = meldung(
            client, HAUS_A, versicherung_id=vers["id"],
            schadendatum=schaden_tag.isoformat(),
        ).json()
        assert m["meldefrist_tage"] == 4
        assert m["melden_bis"] == (schaden_tag + timedelta(days=4)).isoformat()
        assert m["frist_ueberschritten"] is False

    def test_ueberschrittene_frist_wird_benannt(self, client):
        vers = versicherung(client, HAUS_A, meldefrist_tage=2).json()
        alt = date.today() - timedelta(days=30)
        m = meldung(
            client, HAUS_A, versicherung_id=vers["id"], schadendatum=alt.isoformat()
        ).json()
        assert m["frist_ueberschritten"] is True

    def test_ohne_frist_am_vertrag_keine_erfundene_frist(self, client):
        vers = versicherung(client, HAUS_A).json()  # ohne meldefrist_tage
        m = meldung(client, HAUS_A, versicherung_id=vers["id"]).json()
        assert m["meldefrist_tage"] is None
        assert m["melden_bis"] is None
        assert m["frist_ueberschritten"] is False


class TestStaende:
    def _gemeldet(self, client) -> dict:
        vers = versicherung(client, HAUS_A).json()
        m = meldung(client, HAUS_A, versicherung_id=vers["id"]).json()
        return client.post(
            f"{SCHADEN}/meldungen/{m['id']}/melden", json={"meldeweg": "EMAIL"},
            headers=kopf(HAUS_A),
        ).json()

    def test_regulierung_braucht_einen_betrag(self, client):
        m = self._gemeldet(client)
        ohne = client.patch(
            f"{SCHADEN}/meldungen/{m['id']}", json={"status": "REGULIERT"},
            headers=kopf(HAUS_A),
        )
        assert ohne.status_code == 422
        mit = client.patch(
            f"{SCHADEN}/meldungen/{m['id']}",
            json={"status": "REGULIERT", "regulierungsbetrag": 9000.0},
            headers=kopf(HAUS_A),
        )
        assert mit.status_code == 200, mit.text
        assert zahl(mit.json()["regulierungsbetrag"]) == pytest.approx(9000.0)

    def test_ablehnung_braucht_einen_grund(self, client):
        m = self._gemeldet(client)
        ohne = client.patch(
            f"{SCHADEN}/meldungen/{m['id']}", json={"status": "ABGELEHNT"},
            headers=kopf(HAUS_A),
        )
        assert ohne.status_code == 422
        mit = client.patch(
            f"{SCHADEN}/meldungen/{m['id']}",
            json={"status": "ABGELEHNT", "abgelehnt_grund": "Nicht versichertes Ereignis"},
            headers=kopf(HAUS_A),
        )
        assert mit.status_code == 200, mit.text

    def test_abgeschlossene_akte_wird_nicht_geoeffnet(self, client):
        m = self._gemeldet(client)
        client.patch(
            f"{SCHADEN}/meldungen/{m['id']}",
            json={"status": "REGULIERT", "regulierungsbetrag": 1.0},
            headers=kopf(HAUS_A),
        )
        antwort = client.patch(
            f"{SCHADEN}/meldungen/{m['id']}", json={"status": "IN_BEARBEITUNG"},
            headers=kopf(HAUS_A),
        )
        assert antwort.status_code == 409
        assert "abgeschlossen" in antwort.text

    def test_entwurf_geht_nicht_direkt_in_bearbeitung(self, client):
        m = meldung(client, HAUS_A).json()
        antwort = client.patch(
            f"{SCHADEN}/meldungen/{m['id']}", json={"status": "IN_BEARBEITUNG"},
            headers=kopf(HAUS_A),
        )
        assert antwort.status_code == 409

    def test_uebergangstabelle_ist_die_einzige_quelle(self):
        from app.services import schaden_service as dienst

        assert set(dienst.UEBERGAENGE) == set(dienst.STAENDE)
        assert dienst.UEBERGAENGE["ENTWURF"] == ("GEMELDET",)
        assert dienst.UEBERGAENGE["REGULIERT"] == ()
        assert dienst.UEBERGAENGE["ABGELEHNT"] == ()


# ── 3. Der Druckauftrag behauptet keinen Druck ──────────────────────────────


class TestDruckauftrag:
    def test_auftrag_nennt_den_versandstand(self, client):
        """Vorher: `status: "erstellt"` — und nichts war unterwegs."""
        drk = drucker(client, HAUS_A).json()
        daten = auftrag(client, HAUS_A, drk["id"]).json()
        assert daten["status"] == "ANGELEGT"
        assert daten["uebermittlung"] == "NICHT_ANGEBUNDEN"
        assert daten["uebermittelt_am"] is None
        assert daten["gedruckt_am"] is None
        assert daten["drucker_name"] == drk["name"]

    def test_unbekannter_drucker_wird_abgewiesen(self, client):
        """Vorher ging jede Kennung durch, weil die Liste aus Literalen bestand."""
        antwort = auftrag(client, HAUS_A, str(uuid.uuid4()))
        assert antwort.status_code == 422
        assert "Drucker" in antwort.text

    def test_fremder_drucker_wird_abgewiesen(self, client):
        fremd = drucker(client, HAUS_B).json()
        assert auftrag(client, HAUS_A, fremd["id"]).status_code == 422

    def test_gedruckt_ohne_zeitpunkt_ist_in_der_datenbank_unmoeglich(self, engine, client):
        from sqlalchemy import text
        from sqlalchemy.exc import IntegrityError

        drk = drucker(client, HAUS_A).json()
        a = auftrag(client, HAUS_A, drk["id"]).json()
        with pytest.raises(IntegrityError):
            with engine.begin() as v:
                v.execute(
                    text(f"UPDATE {AUFTRAEGE} SET status = 'GEDRUCKT' WHERE id = :id"),
                    {"id": a["id"]},
                )

    def test_abbruch_braucht_einen_grund(self, client):
        drk = drucker(client, HAUS_A).json()
        a = auftrag(client, HAUS_A, drk["id"]).json()
        ohne = client.request(
            "DELETE", f"{ETIKETT}/druckauftrag/{a['id']}", json={}, headers=kopf(HAUS_A)
        )
        assert ohne.status_code == 422
        mit = client.request(
            "DELETE", f"{ETIKETT}/druckauftrag/{a['id']}",
            json={"grund": "Charge storniert"}, headers=kopf(HAUS_A),
        )
        assert mit.status_code == 200, mit.text
        assert mit.json()["status"] == "ABGEBROCHEN"

    def test_gedruckter_auftrag_wird_nicht_abgebrochen(self, engine, client):
        from sqlalchemy import text

        drk = drucker(client, HAUS_A).json()
        a = auftrag(client, HAUS_A, drk["id"]).json()
        with engine.begin() as v:
            v.execute(
                text(
                    f"UPDATE {AUFTRAEGE} SET status = 'GEDRUCKT', gedruckt_am = NOW() "
                    "WHERE id = :id"
                ),
                {"id": a["id"]},
            )
        antwort = client.request(
            "DELETE", f"{ETIKETT}/druckauftrag/{a['id']}",
            json={"grund": "zu spaet"}, headers=kopf(HAUS_A),
        )
        assert antwort.status_code == 409
        assert "Umlauf" in antwort.text

    def test_drucker_mit_auftrag_ist_nicht_loeschbar(self, engine, client):
        from sqlalchemy import text
        from sqlalchemy.exc import IntegrityError

        drk = drucker(client, HAUS_A).json()
        auftrag(client, HAUS_A, drk["id"])
        with pytest.raises(IntegrityError):
            with engine.begin() as v:
                v.execute(text(f"DELETE FROM {DRUCKER} WHERE id = :id"), {"id": drk["id"]})


# ── 4. Die Erinnerung behauptet keinen Versand ──────────────────────────────


class TestErinnerung:
    def _bestaetigung(self, engine, haus: str) -> str:
        from sqlalchemy import text

        eid = str(uuid.uuid4())
        # Die Lieferscheinnummer ist je Mandant eindeutig
        # (`ux_gelangensbestaetigung_tenant_lieferschein` aus dem Slice
        # STEUERNACHWEIS-MANDANT-20261001) — also je Aufruf eine eigene.
        kennung = uuid.uuid4().hex[:8].upper()
        with engine.begin() as v:
            v.execute(
                text(
                    f"INSERT INTO {BESTAETIGUNGEN} (id, tenant_id, lieferschein_nr, "
                    " rechnung_nr, kunde_nr, bestimmungsland_code, warenwert_eur, "
                    " versanddatum, empfaenger_name, empfaenger_ust_id_nr, status, token, "
                    " erinnerung_am) "
                    "VALUES (:id, :tid, :ls, :re, 'K-1', 'FR', 1000, CURRENT_DATE, "
                    "        'Dupont SAS', 'FR12345678901', 'AUSSTEHEND', :token, CURRENT_DATE)"
                ),
                {
                    "id": eid,
                    "tid": haus,
                    "ls": f"LS-{kennung}",
                    "re": f"RE-{kennung}",
                    "token": kennung,
                },
            )
        return eid

    def test_erinnerung_wird_vermerkt_nicht_versendet(self, engine, client):
        """Vorher: `erinnerung_gesendet: true` — und nichts wurde versendet."""
        eid = self._bestaetigung(engine, HAUS_A)
        antwort = client.post(
            f"{GELANGEN}/{eid}/mahnung", json={"angefordert_durch": "Innendienst"},
            headers=kopf(HAUS_A),
        )
        assert antwort.status_code == 200, antwort.text
        daten = antwort.json()
        assert daten["erinnerung_vermerkt"] is True
        assert daten["versand"] == "NICHT_KONFIGURIERT"
        assert daten["versuche"] == 1
        assert daten["angefordert_am"] is not None
        assert "kein Versandweg" in daten["hinweis"]
        assert "erinnerung_gesendet" not in daten

    def test_versuche_werden_gezaehlt(self, engine, client):
        eid = self._bestaetigung(engine, HAUS_A)
        client.post(f"{GELANGEN}/{eid}/mahnung", json={}, headers=kopf(HAUS_A))
        zweite = client.post(f"{GELANGEN}/{eid}/mahnung", json={}, headers=kopf(HAUS_A))
        assert zweite.json()["versuche"] == 2

    def test_fremde_bestaetigung_wird_nicht_erinnert(self, engine, client):
        eid = self._bestaetigung(engine, HAUS_B)
        antwort = client.post(f"{GELANGEN}/{eid}/mahnung", json={}, headers=kopf(HAUS_A))
        assert antwort.status_code == 404

    def test_der_versuch_steht_in_der_datenbank(self, engine, client):
        from sqlalchemy import text

        eid = self._bestaetigung(engine, HAUS_A)
        client.post(f"{GELANGEN}/{eid}/mahnung", json={}, headers=kopf(HAUS_A))
        with engine.connect() as c:
            zeile = c.execute(
                text(
                    f"SELECT erinnerung_versuche, erinnerung_angefordert_am FROM {BESTAETIGUNGEN} "
                    "WHERE id = :id"
                ),
                {"id": eid},
            ).first()
        assert zeile[0] == 1
        assert zeile[1] is not None


# ── 5. Der Mandant ──────────────────────────────────────────────────────────


class TestMandantentrennung:
    def test_fremde_meldungen_sind_nicht_sichtbar(self, client):
        meldung(client, HAUS_B, beschreibung="Nur Haus B")
        liste = client.get(f"{SCHADEN}/meldungen", headers=kopf(HAUS_A)).json()
        assert liste == []

    def test_fremde_meldung_ist_nicht_lesbar(self, client):
        fremd = meldung(client, HAUS_B).json()
        assert client.get(
            f"{SCHADEN}/meldungen/{fremd['id']}", headers=kopf(HAUS_A)
        ).status_code == 404

    def test_fremder_vertrag_wird_nicht_zugeordnet(self, client):
        fremd = versicherung(client, HAUS_B).json()
        antwort = meldung(client, HAUS_A, versicherung_id=fremd["id"])
        assert antwort.status_code == 409 or antwort.status_code == 422

    def test_fremde_druckauftraege_sind_nicht_sichtbar(self, client):
        drk = drucker(client, HAUS_B).json()
        auftrag(client, HAUS_B, drk["id"])
        liste = client.get(f"{ETIKETT}/druckauftrag", headers=kopf(HAUS_A)).json()
        assert liste == []

    def test_nummern_laufen_je_mandant(self, client):
        erste = meldung(client, HAUS_A).json()["meldungsnummer"]
        zweite = meldung(client, HAUS_A).json()["meldungsnummer"]
        assert int(erste.rsplit("-", 1)[1]) + 1 == int(zweite.rsplit("-", 1)[1])
