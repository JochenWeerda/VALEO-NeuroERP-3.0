"""Masken-Commands: ein Idempotenzschluessel wird durchgesetzt, nicht nur notiert.

Befund vom 11.10.2026: Jeder Masken-Command las ``_idempotencyKey`` und schrieb ihn ins
Audit; keiner pruefte ihn. Wer einen Auftrag nach einem Zeitlimit mit demselben Schluessel
wiederholte, fuehrte ihn ein zweites Mal aus — eine zweite Sanktionspruefung im Protokoll,
ein zweiter Bonuslauf, eine zweite Tour.

Der Waechter steht in ``mask_action_runtime_service``. Die Vertraege laufen gegen
``valeo_probe``; nichts an der Datenbank ist nachgestellt.
"""

from __future__ import annotations

import asyncio
import os
import pathlib
import re
import threading
import time
import uuid

import pytest

pytestmark = pytest.mark.integration

DB_URL = os.environ.get(
    "TEST_DATABASE_URL",
    os.environ.get("DATABASE_URL", "postgresql://valeo_dev:valeo_dev_2024@127.0.0.1:5432/valeo_probe"),
)
os.environ.setdefault("DATABASE_URL", DB_URL)
os.environ.setdefault("API_DEV_TOKEN", "dev-token")

HAUS = f"ik-{uuid.uuid4().hex[:8]}"
NACHBAR = f"ik-{uuid.uuid4().hex[:8]}"
WURZEL = pathlib.Path(__file__).resolve().parent.parent
PRUEFEN = "/api/v1/compliance/sanctions/actions/pruefen/manual"


def _aufraeumen(v) -> None:
    from sqlalchemy import text

    for haus in (HAUS, NACHBAR):
        for anweisung in (
            "DELETE FROM domain_crm.crm_action_audit_log WHERE tenant_id = :h",
            "DELETE FROM public.outbox_events WHERE tenant_id = :h",
            "DELETE FROM domain_compliance.sanctions_checks WHERE tenant_id = :h",
        ):
            v.execute(text(anweisung), {"h": haus})


@pytest.fixture(scope="module")
def engine():
    from sqlalchemy import create_engine, text

    try:
        motor = create_engine(DB_URL)
        with motor.connect() as v:
            v.execute(text("SELECT idempotency_key FROM domain_crm.crm_action_audit_log LIMIT 0"))
            v.execute(text("SELECT 1 FROM domain_compliance.sanctions_checks LIMIT 0"))
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank/Migration nicht bereit: {fehler}")
    yield motor
    with motor.begin() as v:
        _aufraeumen(v)


@pytest.fixture(scope="module")
def client(engine):
    from fastapi.testclient import TestClient

    from app.main import app

    with TestClient(app) as c:
        yield c


def kopf(haus: str = HAUS) -> dict:
    return {"Authorization": "Bearer dev-token", "X-Tenant-Id": haus}


def schluessel() -> str:
    return f"auftrag-{uuid.uuid4().hex[:10]}"


class Fachweg:
    """Ein Fachweg, der mitzaehlt, wie oft er gelaufen ist."""

    def __init__(self, *, dauer: float = 0.0, scheitert_einmal: bool = False):
        self.laeufe = 0
        self.dauer = dauer
        self.scheitert = scheitert_einmal
        self.pruefungen = 0
        self.ablehnen_ab = None

    async def pruefen(self, _db, _payload, _entity, _tenant):
        self.pruefungen += 1
        if self.ablehnen_ab is not None and self.pruefungen >= self.ablehnen_ab:
            return [{"field": "status", "message": "Schon freigegeben.", "severity": "blocking"}]
        return []

    async def ausfuehren(self, _db, _payload, _entity, _tenant):
        if self.dauer:
            time.sleep(self.dauer)
        if self.scheitert:
            self.scheitert = False
            from fastapi import HTTPException

            raise HTTPException(409, "Der Fachweg lehnt ab.")
        self.laeufe += 1
        return "freigegeben"


def lauf(engine, weg: Fachweg, *, key: str | None, objekt: str = "beleg-1", haus: str = HAUS,
         modus: str = "execute"):
    from sqlalchemy.orm import Session

    from app.services import mask_action_runtime_service as runtime

    rumpf: dict = {"_mode": modus}
    if key is not None:
        rumpf["_idempotencyKey"] = key
    with Session(engine) as db:
        return asyncio.run(runtime.run_delegated_mask_action(
            db, action_key="freigeben", entity_type="ik_beleg", entity_id=objekt, tenant_id=haus,
            body=rumpf, check_fn=weg.pruefen, delegate_fn=weg.ausfuehren,
            outbox_event_type="ik.beleg.freigegeben",
        ))


def audit_zeilen(engine, key: str, haus: str = HAUS) -> int:
    from sqlalchemy import text

    with engine.connect() as v:
        return v.execute(
            text("SELECT count(*) FROM domain_crm.crm_action_audit_log "
                 "WHERE tenant_id = :h AND idempotency_key = :k"),
            {"h": haus, "k": key},
        ).scalar_one()


# ── Der Standardweg (run_delegated_mask_action) ──────────────────────────────


class TestStandardweg:
    def test_derselbe_schluessel_laeuft_einmal(self, engine):
        weg, key = Fachweg(), schluessel()
        erster = lauf(engine, weg, key=key)
        zweiter = lauf(engine, weg, key=key)
        assert (erster.success, zweiter.success) == (True, True)
        assert weg.laeufe == 1
        assert zweiter.auditEntryId == erster.auditEntryId
        assert zweiter.affectedIds == ["beleg-1"]
        assert "bereits ausgefuehrt" in zweiter.summary
        assert zweiter.outboxEventId is None, "eine Wiederholung loest kein zweites Ereignis aus"
        assert audit_zeilen(engine, key) == 1

    def test_ohne_schluessel_bleibt_alles_wie_es_war(self, engine):
        weg = Fachweg()
        lauf(engine, weg, key=None)
        lauf(engine, weg, key=None)
        assert weg.laeufe == 2

    def test_leerer_schluessel_ist_kein_schluessel(self, engine):
        weg = Fachweg()
        lauf(engine, weg, key="   ")
        lauf(engine, weg, key="   ")
        assert weg.laeufe == 2

    def test_die_wiederholung_wird_vor_der_zustandspruefung_beantwortet(self, engine):
        """Nach dem ersten Lauf passt der Zustand nicht mehr. „Schon freigegeben" waere die
        falsche Antwort auf die Wiederholung desselben Auftrags."""
        weg, key = Fachweg(), schluessel()
        weg.ablehnen_ab = 2
        lauf(engine, weg, key=key)
        zweiter = lauf(engine, weg, key=key)
        assert zweiter.success is True, zweiter.error
        assert weg.laeufe == 1

    def test_derselbe_schluessel_fuer_ein_anderes_objekt_ist_ein_fehler(self, engine):
        weg, key = Fachweg(), schluessel()
        lauf(engine, weg, key=key, objekt="beleg-1")
        anderer = lauf(engine, weg, key=key, objekt="beleg-2")
        assert anderer.success is False
        assert anderer.validationErrors[0]["field"] == "_idempotencyKey"
        assert weg.laeufe == 1

    def test_ein_gescheiterter_lauf_verbraucht_den_schluessel_nicht(self, engine):
        weg, key = Fachweg(scheitert_einmal=True), schluessel()
        erster = lauf(engine, weg, key=key)
        assert erster.success is False
        assert audit_zeilen(engine, key) == 0
        zweiter = lauf(engine, weg, key=key)
        assert zweiter.success is True
        assert weg.laeufe == 1

    @pytest.mark.parametrize("modus", ["validate", "dryRun", "propose"])
    def test_ein_trockenlauf_verbraucht_den_schluessel_nicht(self, engine, modus):
        weg, key = Fachweg(), schluessel()
        assert lauf(engine, weg, key=key, modus=modus).success is True
        assert audit_zeilen(engine, key) == 0
        assert lauf(engine, weg, key=key).success is True
        assert weg.laeufe == 1

    def test_der_schluessel_gilt_je_mandant(self, engine):
        weg, key = Fachweg(), schluessel()
        lauf(engine, weg, key=key, haus=HAUS)
        nachbar = lauf(engine, weg, key=key, haus=NACHBAR)
        assert nachbar.success is True
        assert weg.laeufe == 2
        assert (audit_zeilen(engine, key, HAUS), audit_zeilen(engine, key, NACHBAR)) == (1, 1)

    def test_zwei_gleichzeitige_laeufe_fuehren_einmal_aus(self, engine):
        weg, key = Fachweg(dauer=0.6), schluessel()
        ergebnisse: list = []

        def einer():
            ergebnisse.append(lauf(engine, weg, key=key))

        faeden = [threading.Thread(target=einer) for _ in range(2)]
        for faden in faeden:
            faden.start()
        for faden in faeden:
            faden.join(timeout=30)
        assert [e.success for e in ergebnisse] == [True, True], [e.error for e in ergebnisse]
        assert weg.laeufe == 1
        assert audit_zeilen(engine, key) == 1
        assert len({e.auditEntryId for e in ergebnisse}) == 1


# ── Ein Einzelweg ueber HTTP: die Sanktionspruefung ──────────────────────────


def protokollzeilen(engine, name: str) -> int:
    from sqlalchemy import text

    with engine.connect() as v:
        return v.execute(
            text("SELECT count(*) FROM domain_compliance.sanctions_checks WHERE tenant_id = :h AND geprueft_name = :n"),
            {"h": HAUS, "n": name},
        ).scalar_one()


class TestEinzelweg:
    def test_wiederholte_sanktionspruefung_schreibt_ein_protokoll(self, client, engine):
        name = f"Hof Idempotenz {uuid.uuid4().hex[:6]}"
        rumpf = {"name": name, "_idempotencyKey": schluessel()}
        erste = client.post(PRUEFEN, headers=kopf(), json=rumpf).json()
        zweite = client.post(PRUEFEN, headers=kopf(), json=rumpf).json()
        assert erste["success"] is True, erste
        assert zweite["success"] is True, zweite
        assert protokollzeilen(engine, name) == 1
        assert zweite["auditEntryId"] == erste["auditEntryId"]
        assert zweite["affectedIds"] == erste["affectedIds"]

    def test_ohne_schluessel_ist_jede_pruefung_eine_pruefung(self, client, engine):
        name = f"Hof ohne Schluessel {uuid.uuid4().hex[:6]}"
        for _ in range(2):
            assert client.post(PRUEFEN, headers=kopf(), json={"name": name}).json()["success"] is True
        assert protokollzeilen(engine, name) == 2


# ── Kein Weg ohne Waechter ───────────────────────────────────────────────────

# Wege, die den Schluessel lesen und bewusst nicht pruefen — mit Grund.
AUSNAHMEN = {
    # Zustandsmaschine: Ein zweites "approve" lehnt der Lebenszyklus ab; ein Audit mit
    # Schluessel schreibt dieser Weg nicht.
    "app/api/v1/endpoints/rations_lifecycle.py",
}


def _schreibwege() -> dict[str, tuple[int, int]]:
    """Je Datei: Zahl der Audit-Schreibstellen und Zahl der Waechter davor."""
    gefunden = {}
    for datei in sorted((WURZEL / "app").rglob("*.py")):
        quelle = datei.read_text(encoding="utf-8")
        if "parse_action_body(" not in quelle:
            continue
        pfad = datei.relative_to(WURZEL).as_posix()
        if pfad == "app/services/mask_action_runtime_service.py":
            continue
        schreibt = len(re.findall(r"(?<![\w.])_write_audit\(", quelle))
        waechter = len(re.findall(r"(?<![\w.])(?:wiederholter_auftrag|_frueherer_lauf)\(", quelle))
        waechter -= len(re.findall(r"def _frueherer_lauf\(", quelle))
        gefunden[pfad] = (schreibt, waechter)
    return gefunden


def test_jeder_schreibweg_hat_einen_waechter():
    wege = _schreibwege()
    assert len(wege) >= 10, "die Suche findet die Command-Dateien nicht mehr"
    ohne = {pfad: zahlen for pfad, zahlen in wege.items()
            if zahlen[1] < zahlen[0] and pfad not in AUSNAHMEN}
    assert ohne == {}, (
        "Masken-Commands schreiben ein Audit mit Schluessel, ohne ihn zu pruefen "
        f"(Schreibstellen, Waechter): {ohne}"
    )


def test_die_ausnahmen_gibt_es_noch():
    wege = _schreibwege()
    assert {pfad for pfad in AUSNAHMEN if pfad not in wege} == set()
    assert {pfad for pfad in AUSNAHMEN if wege[pfad][0] > 0} == set(), (
        "eine Ausnahme schreibt inzwischen ein Audit — dann braucht sie den Waechter"
    )


def test_der_standardweg_prueft_vor_der_zustandspruefung_und_in_der_schreibtransaktion():
    quelle = (WURZEL / "app/services/mask_action_runtime_service.py").read_text(encoding="utf-8")
    rumpf = quelle[quelle.index("async def run_delegated_mask_action("):]
    erster = rumpf.index("wiederholter_auftrag(")
    pruefung = rumpf.index("await check_fn(")
    zweiter = rumpf.index("wiederholter_auftrag(", pruefung)
    assert erster < pruefung < zweiter < rumpf.index("audit_id = _write_audit(")
