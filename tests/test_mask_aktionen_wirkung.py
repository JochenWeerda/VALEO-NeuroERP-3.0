"""Mask-Aktionen melden nur Erfolg, wenn etwas geschehen ist.

Bis zum 07.10.2026 schrieb keine der neun ``execute``-Funktionen in
``mask_actions.py`` fachlich: Sie bauten ein Ergebnis-Dict, schrieben Audit und
Outbox und antworteten ``success: true``. Das Ereignis
``finance.payment_run.approved`` speiste die Projektion ``payment_run_cockpit`` —
ein nicht freigegebener Zahlungslauf erschien im Lesemodell als freigegeben.

Was diese Vertraege festhalten:

* Eine Aktion mit Fachweg **delegiert** an ihn. Mutation, Audit und Ereignis
  entstehen in **einem** Commit; scheitert der Fachweg, entsteht nichts davon, und
  die Antwort nennt den fachlichen Grund.
* ``dryRun`` prueft gegen die Datenbank (Objekt da, Zustand passt) und schreibt
  nichts.
* Eine Aktion **ohne** Fachweg hat keinen Endpunkt, sondern einen ``stubReason``
  — die Maske sagt "nicht verfuegbar" statt "erledigt".

Geprueft gegen die gemeinsame, vorhandene Pruefstand-Datenbank.
"""

from __future__ import annotations

import os
import uuid
from datetime import date

import pytest

pytestmark = pytest.mark.integration

DB_URL = os.environ.get(
    "TEST_DATABASE_URL",
    os.environ.get("DATABASE_URL", "postgresql://valeo_dev:valeo_dev_2024@127.0.0.1:5432/valeo_probe"),
)
os.environ.setdefault("DATABASE_URL", DB_URL)
os.environ.setdefault("API_DEV_TOKEN", "dev-token")

HAUS_A = f"mak-a-{uuid.uuid4().hex[:6]}"
HAUS_B = f"mak-b-{uuid.uuid4().hex[:6]}"

ZAHLUNGSLAUF = "/api/v1/finance/payment-runs/{}/actions/freigeben"
LIEFERSCHEIN = "/api/v1/sales/delivery-notes/{}/actions/drucken"
REKLAMATION = "/api/v1/reklamationen/{}/actions/abschliessen"
MAHNEN = "/api/v1/finance/open-items/{}/actions/mahnen"
AP_FREIGABE = "/api/v1/finance/ap/invoices/{}/actions/freigeben"

#: Aktionen ohne Fachweg — Pfad und warum.
OHNE_FACHWEG = {
    "/api/v1/crm/leads/{entity_id}/actions/qualifizieren": "crm/lead",
    "/api/v1/crm/opportunities/{entity_id}/actions/create_activity": "crm/opportunity",
    "/api/v1/einkauf/bestellungen/{entity_id}/actions/bestellen": "einkauf/angebot",
    "/api/v1/lager/artikel/{entity_id}/actions/wareneingang": "einkauf/anlieferavis",
    "/api/v1/lager/stock-movements/{entity_id}/actions/stornieren": "lager/stock-movement",
    "/api/v1/agrar/harvest-settlements/{entity_id}/actions/drucken": "agrar/harvest-settlement",
}


@pytest.fixture(scope="module")
def engine():
    from sqlalchemy import create_engine, text

    try:
        motor = create_engine(DB_URL)
        with motor.connect() as conn:
            conn.execute(text("SELECT 1 FROM domain_crm.crm_action_audit_log LIMIT 0"))
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank nicht erreichbar: {fehler}")
    return motor


def aufraeumen(engine):
    from sqlalchemy import text

    with engine.begin() as v:
        for tabelle in (
            "domain_crm.crm_action_audit_log",
            "public.outbox_events",
            "domain_audit.attestations",
            "domain_erp.payment_runs",
            "domain_sales.delivery_notes",
            "domain_ops.reklamationen",
            "domain_finance.finance_mahnstufen_audit",
            "public.offene_posten",
        ):
            v.execute(text(f"DELETE FROM {tabelle} WHERE tenant_id = ANY(:h)"), {"h": [HAUS_A, HAUS_B]})  # nosec B608


@pytest.fixture(scope="module", autouse=True)
def haeuser(engine):
    from sqlalchemy import text

    with engine.begin() as v:
        for haus in (HAUS_A, HAUS_B):
            v.execute(
                text("INSERT INTO domain_shared.tenants (id, name) VALUES (:id, :n) ON CONFLICT (id) DO NOTHING"),
                {"id": haus, "n": f"Pruefbetrieb {haus}"},
            )
    yield
    aufraeumen(engine)
    with engine.begin() as v:
        v.execute(text("DELETE FROM domain_shared.tenants WHERE id = ANY(:h)"), {"h": [HAUS_A, HAUS_B]})


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


def wert(engine, sql: str, **parameter):
    from sqlalchemy import text

    with engine.connect() as v:
        return v.execute(text(sql), parameter).scalar()


def spuren(engine, haus: str, aktion: str) -> tuple[int, int]:
    """Audit-Zeilen und Ereignisse dieser Aktion im Mandanten."""
    audit = wert(
        engine,
        "SELECT COUNT(*) FROM domain_crm.crm_action_audit_log WHERE tenant_id = :h AND action_key = :a",
        h=haus, a=aktion,
    )
    ereignisse = wert(
        engine,
        "SELECT COUNT(*) FROM public.outbox_events WHERE tenant_id = :h AND payload LIKE :a",
        h=haus, a=f'%"action_key": "{aktion}"%',
    )
    return audit, ereignisse


def zahlungslauf(engine, haus: str, status: str = "draft") -> str:
    from sqlalchemy import text

    kennung = str(uuid.uuid4())
    with engine.begin() as v:
        v.execute(
            text(
                "INSERT INTO domain_erp.payment_runs (id, tenant_id, run_number, execution_date, "
                " initiator_name, initiator_iban, status) "
                "VALUES (:id, :h, :nr, :d, 'Pruefbetrieb', 'DE02120300000000202051', :s)"
            ),
            {"id": kennung, "h": haus, "nr": f"ZL-{kennung[:8]}", "d": date.today(), "s": status},
        )
    return kennung


def lieferschein(engine, haus: str, status: str = "draft") -> str:
    from sqlalchemy import text

    kennung = str(uuid.uuid4())
    with engine.begin() as v:
        v.execute(
            text(
                "INSERT INTO domain_sales.delivery_notes (id, tenant_id, delivery_note_number, delivery_date, status) "
                "VALUES (:id, :h, :nr, :d, :s)"
            ),
            {"id": kennung, "h": haus, "nr": f"LS-{kennung[:8]}", "d": date.today(), "s": status},
        )
    return kennung


def reklamation(engine, haus: str, status: str = "anerkannt") -> str:
    from sqlalchemy import text

    kennung = f"REK-{uuid.uuid4().hex[:10]}"
    with engine.begin() as v:
        v.execute(
            text(
                "INSERT INTO domain_ops.reklamationen (id, reklamation_id, reklamation_nr, tenant_id, "
                " lieferant_id, typ, zustaendiger, frist_datum, status) "
                "VALUES (:id, :rid, :nr, :h, 'L-1', 'qualitaet', 'Pruefer', :d, :s)"
            ),
            {"id": str(uuid.uuid4()), "rid": kennung, "nr": kennung, "h": haus, "d": date.today(), "s": status},
        )
    return kennung


def offener_posten(engine, haus: str, rechnungsnr: str | None = "RE-1") -> str:
    from sqlalchemy import text

    kennung = str(uuid.uuid4())
    with engine.begin() as v:
        v.execute(
            text(
                "INSERT INTO public.offene_posten (id, tenant_id, rechnungsnr, datum, faelligkeit, betrag, offen, konto_typ) "
                "VALUES (:id, :h, :nr, :d, :d, 100, 100, 'debitoren')"
            ),
            {"id": kennung, "h": haus, "nr": rechnungsnr if rechnungsnr else "", "d": date.today()},
        )
    return kennung


# ── 1. Zahlungslauf freigeben ───────────────────────────────────────────────


class TestZahlungslauf:
    def test_freigabe_aendert_den_lauf_und_hinterlaesst_spuren(self, client, engine):
        lauf = zahlungslauf(engine, HAUS_A)
        antwort = client.post(
            ZAHLUNGSLAUF.format(lauf),
            json={"_mode": "execute", "_auditReason": "Vier-Augen geprueft", "freigegeben_von": "Kasse"},
            headers=kopf(HAUS_A),
        ).json()
        assert antwort["success"] is True, antwort
        assert wert(engine, "SELECT status FROM domain_erp.payment_runs WHERE id = :i", i=lauf) == "approved"
        assert wert(engine, "SELECT approved_by FROM domain_erp.payment_runs WHERE id = :i", i=lauf) == "Kasse"
        assert spuren(engine, HAUS_A, "freigeben") == (1, 1)

    def test_ein_freigegebener_lauf_wird_nicht_nochmals_freigegeben(self, client, engine):
        lauf = zahlungslauf(engine, HAUS_A, status="approved")
        antwort = client.post(
            ZAHLUNGSLAUF.format(lauf), json={"_mode": "execute", "_auditReason": "x"}, headers=kopf(HAUS_A)
        ).json()
        assert antwort["success"] is False
        # Der fachliche Grund, nicht "Aktion konnte nicht gespeichert werden".
        assert "cannot be approved" in antwort["error"] or "nicht" in antwort["error"]
        assert spuren(engine, HAUS_A, "freigeben") == (0, 0)

    def test_ohne_begruendung_geschieht_nichts(self, client, engine):
        lauf = zahlungslauf(engine, HAUS_A)
        antwort = client.post(ZAHLUNGSLAUF.format(lauf), json={"_mode": "execute"}, headers=kopf(HAUS_A)).json()
        assert antwort["success"] is False
        assert wert(engine, "SELECT status FROM domain_erp.payment_runs WHERE id = :i", i=lauf) == "draft"
        assert spuren(engine, HAUS_A, "freigeben") == (0, 0)

    def test_ein_fremder_mandant_gibt_nichts_frei(self, client, engine):
        lauf = zahlungslauf(engine, HAUS_A)
        antwort = client.post(
            ZAHLUNGSLAUF.format(lauf), json={"_mode": "execute", "_auditReason": "x"}, headers=kopf(HAUS_B)
        ).json()
        assert antwort["success"] is False
        assert wert(engine, "SELECT status FROM domain_erp.payment_runs WHERE id = :i", i=lauf) == "draft"
        assert spuren(engine, HAUS_B, "freigeben") == (0, 0)

    def test_trockenlauf_prueft_und_schreibt_nichts(self, client, engine):
        lauf = zahlungslauf(engine, HAUS_A)
        gut = client.post(ZAHLUNGSLAUF.format(lauf), json={"_mode": "dryRun"}, headers=kopf(HAUS_A)).json()
        assert gut["success"] is True
        fehlt = client.post(
            ZAHLUNGSLAUF.format(str(uuid.uuid4())), json={"_mode": "dryRun"}, headers=kopf(HAUS_A)
        ).json()
        # Vorher meldete der Trockenlauf "Validierung erfolgreich" auch fuer einen
        # Lauf, den es nicht gibt.
        assert fehlt["success"] is False
        assert wert(engine, "SELECT status FROM domain_erp.payment_runs WHERE id = :i", i=lauf) == "draft"
        assert spuren(engine, HAUS_A, "freigeben") == (0, 0)


# ── 2. Lieferschein drucken ─────────────────────────────────────────────────


class TestLieferschein:
    def test_druck_markiert_den_lieferschein(self, client, engine):
        schein = lieferschein(engine, HAUS_A)
        antwort = client.post(LIEFERSCHEIN.format(schein), json={"_mode": "execute"}, headers=kopf(HAUS_A)).json()
        assert antwort["success"] is True, antwort
        assert wert(engine, "SELECT status FROM domain_sales.delivery_notes WHERE id = :i", i=schein) == "printed"
        assert wert(engine, "SELECT is_printed FROM domain_sales.delivery_notes WHERE id = :i", i=schein) is True
        assert spuren(engine, HAUS_A, "drucken") == (1, 1)

    def test_nachdruck_braucht_eine_begruendung(self, client, engine):
        schein = lieferschein(engine, HAUS_A, status="posted")
        ohne = client.post(LIEFERSCHEIN.format(schein), json={"_mode": "execute"}, headers=kopf(HAUS_A)).json()
        assert ohne["success"] is False
        assert "Attestation" in ohne["error"]
        assert spuren(engine, HAUS_A, "drucken") == (0, 0)
        mit = client.post(
            LIEFERSCHEIN.format(schein), json={"_mode": "execute", "attestation": "Kunde braucht Kopie"},
            headers=kopf(HAUS_A),
        ).json()
        assert mit["success"] is True
        assert wert(
            engine, "SELECT COUNT(*) FROM domain_audit.attestations WHERE entity_id = :i", i=schein
        ) == 1

    def test_fremder_lieferschein_nicht_druckbar(self, client, engine):
        schein = lieferschein(engine, HAUS_A)
        antwort = client.post(LIEFERSCHEIN.format(schein), json={"_mode": "execute"}, headers=kopf(HAUS_B)).json()
        assert antwort["success"] is False
        assert wert(engine, "SELECT status FROM domain_sales.delivery_notes WHERE id = :i", i=schein) == "draft"


# ── 3. Reklamation abschliessen ─────────────────────────────────────────────


class TestReklamation:
    def test_abschluss_setzt_den_status(self, client, engine):
        rek = reklamation(engine, HAUS_A, status="anerkannt")
        antwort = client.post(REKLAMATION.format(rek), json={"_mode": "execute"}, headers=kopf(HAUS_A)).json()
        assert antwort["success"] is True, antwort
        assert wert(engine, "SELECT status FROM domain_ops.reklamationen WHERE reklamation_id = :i", i=rek) == "geschlossen"
        assert spuren(engine, HAUS_A, "abschliessen") == (1, 1)

    def test_die_zustandsmaschine_gilt(self, client, engine):
        # Eine offene Reklamation ist nicht geprueft — sie darf nicht geschlossen werden.
        rek = reklamation(engine, HAUS_A, status="offen")
        antwort = client.post(REKLAMATION.format(rek), json={"_mode": "execute"}, headers=kopf(HAUS_A)).json()
        assert antwort["success"] is False
        assert "Erlaubt" in antwort["error"]
        assert wert(engine, "SELECT status FROM domain_ops.reklamationen WHERE reklamation_id = :i", i=rek) == "offen"
        assert spuren(engine, HAUS_A, "abschliessen") == (0, 0)

    def test_trockenlauf_kennt_die_zustandsmaschine(self, client, engine):
        rek = reklamation(engine, HAUS_A, status="offen")
        antwort = client.post(REKLAMATION.format(rek), json={"_mode": "dryRun"}, headers=kopf(HAUS_A)).json()
        assert antwort["success"] is False


# ── 3b. Mahnen und Eingangsrechnung ─────────────────────────────────────────


class TestMahnen:
    def test_mahnen_setzt_eine_mahnstufe(self, client, engine):
        nummer = f"RE-{uuid.uuid4().hex[:8]}"
        posten = offener_posten(engine, HAUS_A, nummer)
        antwort = client.post(MAHNEN.format(posten), json={"_mode": "execute"}, headers=kopf(HAUS_A)).json()
        assert antwort["success"] is True, antwort
        assert wert(
            engine,
            "SELECT COUNT(*) FROM domain_finance.finance_mahnstufen_audit WHERE tenant_id = :h AND rechnungsnr = :n",
            h=HAUS_A, n=nummer,
        ) == 1
        assert spuren(engine, HAUS_A, "mahnen") == (1, 1)

    def test_fremder_posten_wird_nicht_gemahnt(self, client, engine):
        posten = offener_posten(engine, HAUS_A, f"RE-{uuid.uuid4().hex[:8]}")
        antwort = client.post(MAHNEN.format(posten), json={"_mode": "execute"}, headers=kopf(HAUS_B)).json()
        assert antwort["success"] is False
        assert spuren(engine, HAUS_B, "mahnen") == (0, 0)
        assert wert(
            engine, "SELECT COUNT(*) FROM domain_finance.finance_mahnstufen_audit WHERE tenant_id = ANY(:h)",
            h=[HAUS_A, HAUS_B],
        ) == 0


class TestEingangsrechnung:
    def test_unbekannte_rechnung_wird_nicht_freigegeben(self, client, engine):
        antwort = client.post(
            AP_FREIGABE.format(str(uuid.uuid4())), json={"_mode": "execute"}, headers=kopf(HAUS_A)
        ).json()
        # Vorher: "Eingangsrechnung freigegeben." fuer eine Rechnung, die es nicht gibt.
        assert antwort["success"] is False
        assert spuren(engine, HAUS_A, "freigeben") == (0, 0)


# ── 4. Keine Aktion ohne Fachweg ────────────────────────────────────────────


class TestOhneFachweg:
    @pytest.mark.parametrize("pfad", sorted(OHNE_FACHWEG))
    def test_kein_endpunkt_mehr(self, pfad):
        from app.main import app

        treffer = [r for r in app.routes if getattr(r, "path", "") == pfad]
        assert treffer == [], f"{pfad} meldete Erfolg ohne Wirkung und darf nicht mehr montiert sein"

    @pytest.mark.parametrize("pfad,screen_id", sorted(OHNE_FACHWEG.items()))
    def test_die_maske_sagt_nicht_verfuegbar(self, pfad, screen_id):
        from app.core.screen_definitions import get_screen_definition

        sd = get_screen_definition(screen_id)
        endpunkte = [a.get("commandEndpoint") for a in sd.get("actions", [])]
        assert pfad not in endpunkte
        aktion = pfad.rsplit("/", 1)[-1]
        eintrag = next(a for a in sd["actions"] if a["key"] == aktion)
        assert eintrag.get("stubReason"), f"{screen_id}/{aktion}: stubReason fehlt"


class TestNeueBestellung:
    def test_ein_sprung_statt_eines_vorgetaeuschten_befehls(self):
        from app.core.screen_definitions import get_screen_definition
        from app.main import app

        aktion = next(
            a for a in get_screen_definition("einkauf/supplier")["actions"] if a["key"] == "neue_bestellung"
        )
        assert aktion.get("navigationRoute") == "/einkauf/bestellungen/neu"
        assert "commandEndpoint" not in aktion
        pfad = "/api/v1/einkauf/lieferanten/{entity_id}/actions/neue_bestellung"
        assert [r for r in app.routes if getattr(r, "path", "") == pfad] == []


# ── 5. Statisch: jeder Endpunkt einer Maske existiert ───────────────────────


class TestStatisch:
    def test_jeder_command_endpoint_ist_montiert(self):
        import re

        from app.core.screen_definitions import SCREEN_DEFINITION_BUILDERS, get_screen_definition
        from app.main import app

        # Ein Routen-Parameter passt auf jedes Segment: `/actions/{action_key}`
        # bedient `/actions/approve`.
        muster = [
            re.compile("^" + re.sub(r"\\{[^}]+\\}", "[^/]+", re.escape(r.path)) + "$")
            for r in app.routes
            if hasattr(r, "path") and getattr(r, "methods", None)
        ]
        fehlend = []
        for screen_id in SCREEN_DEFINITION_BUILDERS:
            for aktion in get_screen_definition(screen_id).get("actions", []):
                ziel = aktion.get("commandEndpoint")
                if not ziel:
                    continue
                konkret = re.sub(r"\{[^}]+\}", "X", ziel)
                if not any(m.match(konkret) for m in muster):
                    fehlend.append(f"{screen_id}/{aktion['key']}: {ziel}")
        assert fehlend == []

    def test_kein_handler_meldet_erfolg_ohne_fachaufruf(self):
        from pathlib import Path

        quelle = Path("app/api/v1/endpoints/mask_actions.py").read_text(encoding="utf-8")
        # Der alte Baustein baute nur ein Ergebnis-Dict.
        assert "_status_mutation" not in quelle
        assert quelle.count("delegate_fn=") == quelle.count("@router.post(")
