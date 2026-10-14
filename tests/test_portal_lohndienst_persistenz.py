"""Lohndienst-Auftraege, Empfehlungen und Portalrollen (PORTAL-CONTEXT-001) — gegen die echte (frische) Datenbank.

Bis 14.10.2026 lagen Lohndienst-Auftraege und Empfehlungen im Arbeitsspeicher eines Prozesses. Geprueft wird hier,
was die Nutzerentscheidung verlangt: ein Auftrag ueberlebt den Prozess, wird von parallelen Prozessen weder doppelt
angelegt noch doppelt fortgeschrieben, jede Wiederholung ist idempotent, konkurrierende Aenderungen werden abgewiesen,
die Historie ist nur fortschreibbar — und jede Portalrolle sieht nur, was ihr zusteht.

Auftraege und ihre Historie sind nicht loeschbar; die Tests legen deshalb eigene Mandanten an und raeumen sie nicht
ab (Pruefstand ``valeo_probe`` wird neu aufgebaut).
"""

from __future__ import annotations

import os
import subprocess
import sys
import textwrap
import time
import uuid
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

from app.api.v1.endpoints.compat import router as compat_router
from app.api.v1.endpoints.portal_kundenwege import router as kundenwege_router
from app.api.v1.endpoints.portal_feldbuch import router as feldbuch_router
from app.api.v1.endpoints.portal_innendienst import router as innendienst_router
from app.api.v1.endpoints.portal_intelligence import router as empfehlung_router
from app.api.v1.endpoints.portal_kundenzugaenge import router as zugang_router
from app.api.v1.endpoints.portal_lohndienst import router as lohndienst_router
from app.auth.deps import get_current_user
from app.core.database import SessionLocal
from app.core.tenant import get_tenant_id

REPO = Path(__file__).resolve().parents[1]
LD = "/api/v1/portal/lohndienste"


def _id(praefix: str) -> str:
    return f"{praefix}-{uuid.uuid4().hex[:10]}"


def _schluessel() -> dict[str, str]:
    return {"X-Idempotency-Key": str(uuid.uuid4())}


@pytest.fixture
def welt():
    """Zwei Mandanten; in A die Kunden K1 und K2, in B ein Kunde. Kundennummer = Kunden-ID."""
    a, b = _id("ld-a"), _id("ld-b")
    with SessionLocal() as db:
        for t in (a, b):
            db.execute(text("INSERT INTO domain_shared.tenants (id, name, domain, is_active) VALUES (:i, :i, :i, TRUE)"),
                       {"i": t})
        kunden = {}
        for name, t in (("k1", a), ("k2", a), ("kb", b)):
            kid = _id(name.upper())
            db.execute(text("INSERT INTO domain_crm.customers (id, customer_number, company_name, tenant_id) "
                            "VALUES (:k, :k, :k, :t)"), {"k": kid, "t": t})
            kunden[name] = kid
        db.commit()

    def zuordnen(t: str, subject: str, kunde: str, rolle: str = "inhaber", schlaege: list[str] | None = None) -> None:
        import json
        with SessionLocal() as db:
            db.execute(text(
                "INSERT INTO domain_portal.kundenzugaenge (id, tenant_id, subject, customer_id, rolle, schlag_ids, "
                "angelegt_von) VALUES (:id, :t, :s, :c, :r, CAST(:sch AS jsonb), 'test')"),
                {"id": str(uuid.uuid4()), "t": t, "s": subject, "c": kunde, "r": rolle,
                 "sch": json.dumps(schlaege) if schlaege is not None else None})
            db.commit()

    app = FastAPI()
    for r in (compat_router, kundenwege_router, zugang_router, lohndienst_router, empfehlung_router, innendienst_router):
        app.include_router(r, prefix="/api/v1")
    app.include_router(feldbuch_router, prefix="/api/v1/portal")
    client = TestClient(app, raise_server_exceptions=False)

    def als(t: str, subject: str, *rollen: str) -> TestClient:
        app.dependency_overrides[get_tenant_id] = lambda: t
        app.dependency_overrides[get_current_user] = lambda: {"sub": subject, "name": subject, "roles": list(rollen)}
        return client

    yield {"a": a, "b": b, **kunden, "zuordnen": zuordnen, "als": als}


def _anlegen(c: TestClient, **body) -> dict:
    r = c.post(LD, json={"typ": "lohn_spritz", **body}, headers=_schluessel())
    assert r.status_code == 201, r.text
    return r.json()


def _schritt(c: TestClient, auftrag: dict, aktion: str, **extra) -> dict:
    r = c.post(f"{LD}/{auftrag['auftrag_id']}/status", headers=_schluessel(),
               json={"aktion": aktion, "erwartete_version": auftrag["version"], **extra})
    assert r.status_code == 200, r.text
    return r.json()


INNEN = ("innendienst", "SALES_BEARBEITEN")


# ── Persistenz, Prozesse, Idempotenz ─────────────────────────────────────────


class _Prozess:
    """Ein eigener Python-Prozess; Ausgabe in eine Datei (SQL-Protokolle wuerden eine Pipe fuellen und blockieren).

    Das Ergebnis ist die letzte Zeile mit ``ERGEBNIS:``.
    """

    def __init__(self, code: str, ordner: Path) -> None:
        self.datei = ordner / f"prozess-{uuid.uuid4().hex[:8]}.txt"
        self._f = self.datei.open("w", encoding="utf-8")
        self.p = subprocess.Popen([sys.executable, "-c", textwrap.dedent(code)], cwd=REPO, env={**os.environ},
                                  stdout=self._f, stderr=subprocess.STDOUT, text=True)

    def ergebnis(self) -> str:
        self.p.wait(timeout=240)
        self._f.close()
        ausgabe = self.datei.read_text(encoding="utf-8", errors="replace")
        assert self.p.returncode == 0, ausgabe[-3000:]
        return [z for z in ausgabe.splitlines() if z.startswith("ERGEBNIS:")][-1][len("ERGEBNIS:"):].strip()


def _prozess(code: str, ordner: Path) -> _Prozess:
    return _Prozess(code, ordner)


def test_auftrag_ueberlebt_den_prozess(welt, tmp_path):
    welt["zuordnen"](welt["a"], "hof-1", welt["k1"])
    auftrag = _anlegen(welt["als"](welt["a"], "hof-1"), flaeche_ha=12.5, kultur="Winterweizen")
    p = _prozess(f"""
        from app.core.database import SessionLocal
        from app.services.portal_lohndienst_service import LohndienstService
        with SessionLocal() as db:
            a = LohndienstService(db, {welt['a']!r}).get_auftrag({auftrag['auftrag_id']!r})
            print("ERGEBNIS:", a["status"], a["flaeche_ha"], a["kultur"], a["version"])
    """, tmp_path)
    assert p.ergebnis().split() == ["angefragt", "12.5", "Winterweizen", "1"]


def test_parallele_prozesse_legen_mit_demselben_schluessel_genau_einen_auftrag_an(welt, tmp_path):
    start = tmp_path / "los"
    schluessel = str(uuid.uuid4())
    code = f"""
        import time, pathlib
        from app.core.database import SessionLocal
        from app.services.portal_lohndienst_service import LohndienstService, LohndienstTyp
        while not pathlib.Path({str(start)!r}).exists():
            time.sleep(0.01)
        with SessionLocal() as db:
            a = LohndienstService(db, {welt['a']!r}).auftrag_anlegen(
                customer_id={welt['k1']!r}, typ=LohndienstTyp.MAHL_MISCH, akteur="hof-1", kanal="portal",
                idempotenz_schluessel={schluessel!r}, menge_dt=40)
            print("ERGEBNIS:", a["id"])
    """
    prozesse = [_prozess(code, tmp_path) for _ in range(4)]
    time.sleep(8)  # alle Prozesse haben die Anwendung geladen
    start.write_text("x")
    ids = {p.ergebnis() for p in prozesse}
    assert len(ids) == 1
    with SessionLocal() as db:
        assert db.execute(text("SELECT count(*) FROM domain_portal.lohndienst_auftraege WHERE tenant_id = :t"),
                          {"t": welt["a"]}).scalar() == 1
        assert db.execute(text("SELECT count(*) FROM domain_portal.lohndienst_ereignisse WHERE tenant_id = :t"),
                          {"t": welt["a"]}).scalar() == 1


def test_parallele_prozesse_schreiben_denselben_stand_nur_einmal_fort(welt, tmp_path):
    welt["zuordnen"](welt["a"], "hof-1", welt["k1"])
    auftrag = _anlegen(welt["als"](welt["a"], "hof-1"))
    start = tmp_path / "los"
    code = """
        import time, pathlib, uuid
        from app.core.database import SessionLocal
        from app.services.portal_lohndienst_service import Aktion, LohndienstService, VersionsKonflikt
        while not pathlib.Path(START).exists():
            time.sleep(0.01)
        with SessionLocal() as db:
            try:
                LohndienstService(db, TENANT).status_wechsel(
                    auftrag_id=AUFTRAG, aktion=Aktion.BESTAETIGEN, erwartete_version=1, akteur="innendienst",
                    kanal="intern", idempotenz_schluessel=str(uuid.uuid4()))
                print("ERGEBNIS: ok")
            except VersionsKonflikt:
                print("ERGEBNIS: konflikt")
    """.replace("START", repr(str(start))).replace("TENANT", repr(welt["a"])).replace("AUFTRAG", repr(auftrag["auftrag_id"]))
    prozesse = [_prozess(code, tmp_path) for _ in range(4)]
    time.sleep(8)
    start.write_text("x")
    ergebnisse = [p.ergebnis() for p in prozesse]
    assert sorted(ergebnisse) == ["konflikt", "konflikt", "konflikt", "ok"]
    innen = welt["als"](welt["a"], *INNEN)
    stand = innen.get(f"{LD}/disposition").json()["items"]
    assert [(x["status"], x["version"]) for x in stand] == [("bestaetigt", 2)]


def test_wiederholung_ist_idempotent_und_ein_fremder_inhalt_ein_konflikt(welt):
    welt["zuordnen"](welt["a"], "hof-1", welt["k1"])
    c = welt["als"](welt["a"], "hof-1")
    kopf = _schluessel()
    erst = c.post(LD, json={"typ": "lohn_spritz", "flaeche_ha": 3}, headers=kopf)
    noch = c.post(LD, json={"typ": "lohn_spritz", "flaeche_ha": 3}, headers=kopf)
    assert erst.status_code == noch.status_code == 201
    assert erst.json()["auftrag_id"] == noch.json()["auftrag_id"] and noch.json()["wiederholung"] is True
    assert c.post(LD, json={"typ": "lohn_spritz", "flaeche_ha": 4}, headers=kopf).status_code == 409
    assert c.post(LD, json={"typ": "lohn_spritz"}).status_code == 422  # ohne Schluessel
    assert c.get(LD).json()["count"] == 1
    # Statuswechsel: Wiederholung mit demselben Schluessel liefert das Ergebnis, statt zweimal zu wirken
    innen = welt["als"](welt["a"], *INNEN)
    weg, k = f"{LD}/{erst.json()['auftrag_id']}/status", _schluessel()
    r1 = innen.post(weg, headers=k, json={"aktion": "bestaetigen", "erwartete_version": 1})
    r2 = innen.post(weg, headers=k, json={"aktion": "bestaetigen", "erwartete_version": 1})
    assert r1.status_code == r2.status_code == 200 and r2.json()["wiederholung"] is True
    assert r2.json()["version"] == 2


def test_konkurrierende_aenderung_wird_abgewiesen_statt_ueberschrieben(welt):
    welt["zuordnen"](welt["a"], "hof-1", welt["k1"])
    auftrag = _anlegen(welt["als"](welt["a"], "hof-1"))
    innen = welt["als"](welt["a"], *INNEN)
    _schritt(innen, auftrag, "bestaetigen")
    veraltet = innen.post(f"{LD}/{auftrag['auftrag_id']}/status", headers=_schluessel(),
                          json={"aktion": "stornieren", "erwartete_version": 1})
    assert veraltet.status_code == 409 and veraltet.json()["detail"]["aktuelle_version"] == 2


def test_statusmaschine_ist_deterministisch(welt):
    welt["zuordnen"](welt["a"], "hof-1", welt["k1"])
    auftrag = _anlegen(welt["als"](welt["a"], "hof-1"))
    innen = welt["als"](welt["a"], *INNEN)
    weg = f"{LD}/{auftrag['auftrag_id']}/status"
    assert innen.post(weg, headers=_schluessel(), json={"aktion": "einplanen", "erwartete_version": 1}).status_code == 409
    auftrag = _schritt(innen, auftrag, "bestaetigen")
    assert innen.post(weg, headers=_schluessel(), json={"aktion": "einplanen", "erwartete_version": 2}).status_code == 409
    auftrag = _schritt(innen, auftrag, "einplanen", geplant_datum="2026-11-02", preis_indikativ_eur=480)
    auftrag = _schritt(innen, auftrag, "abschliessen")
    assert auftrag["status"] == "abgeschlossen" and auftrag["abgeschlossen"] is True and auftrag["version"] == 4
    for aktion in ("abschliessen", "stornieren"):
        r = innen.post(weg, headers=_schluessel(), json={"aktion": aktion, "erwartete_version": 4})
        assert r.status_code == 409, aktion


def test_historie_ist_vollstaendig_und_nur_fortschreibbar(welt):
    welt["zuordnen"](welt["a"], "hof-1", welt["k1"])
    kunde = welt["als"](welt["a"], "hof-1")
    auftrag = _anlegen(kunde)
    innen = welt["als"](welt["a"], *INNEN)
    _schritt(innen, auftrag, "bestaetigen", innendienst_notiz="Termin folgt")
    hist = welt["als"](welt["a"], *INNEN).get(f"{LD}/{auftrag['auftrag_id']}/historie", headers={
        "X-Kundenkonto": welt["k1"]}).json()
    assert [(h["aktion"], h["von_status"], h["nach_status"], h["version"], h["kanal"], h["akteur"]) for h in hist] == [
        ("anlegen", None, "angefragt", 1, "portal", "hof-1"),
        ("bestaetigen", "angefragt", "bestaetigt", 2, "intern", "innendienst"),
    ]
    portal = welt["als"](welt["a"], "hof-1").get(f"{LD}/{auftrag['auftrag_id']}/historie").json()
    assert [h["akteur"] for h in portal] == ["hof-1", "Innendienst"]
    for sql in ("UPDATE domain_portal.lohndienst_ereignisse SET akteur = 'x' WHERE auftrag_id = :a",
                "DELETE FROM domain_portal.lohndienst_ereignisse WHERE auftrag_id = :a",
                "DELETE FROM domain_portal.lohndienst_auftraege WHERE id = :a"):
        with SessionLocal() as db, pytest.raises(DBAPIError, match="fortgeschrieben"):
            db.execute(text(sql), {"a": auftrag["auftrag_id"]})


# ── Rollen ───────────────────────────────────────────────────────────────────


def test_portalrollen_sehen_nur_ihre_funktionen(welt):
    a, k1 = welt["a"], welt["k1"]
    for subject, rolle in (("leiter", "betriebsleiter"), ("arbeiter", "mitarbeiter"), ("buch", "buchhaltung"),
                           ("berat", "berater")):
        welt["zuordnen"](a, subject, k1, rolle)
    erwartet = {
        # Weg: (betriebsleiter, mitarbeiter, buchhaltung, berater)
        "/api/v1/portal/rechnungen": (403, 403, 200, 403),
        "/api/v1/portal/bestellungen": (200, 403, 403, 403),
        "/api/v1/portal/vertraege": (200, 403, 403, 403),
        "/api/v1/portal/naehrstoffbilanzen": (200, 403, 403, 200),
        "/api/v1/portal/feldbuch/schlaege": (200, 200, 403, 200),
        "/api/v1/portal/feldbuch/duengebilanz": (200, 403, 403, 200),
        LD: (200, 200, 403, 403),
        "/api/v1/portal/empfehlungen": (200, 403, 403, 200),
        "/api/v1/portal/dashboard": (200, 200, 200, 200),
    }
    for weg, codes in erwartet.items():
        for subject, code in zip(("leiter", "arbeiter", "buch", "berat"), codes):
            assert welt["als"](a, subject).get(weg).status_code == code, (weg, subject)
    neu = {"typ": "lohn_spritz"}
    assert welt["als"](a, "leiter").post(LD, json=neu, headers=_schluessel()).status_code == 201
    assert welt["als"](a, "arbeiter").post(LD, json=neu, headers=_schluessel()).status_code == 403
    assert welt["als"](a, "berat").post("/api/v1/portal/feldbuch/schlaege", json={"name": "X", "flaeche": 1}
                                        ).status_code == 403
    kacheln = {k["label"] for k in welt["als"](a, "buch").get("/api/v1/portal/dashboard").json()["kpis"]}
    assert kacheln == {"Rechnungen offen", "Dokumente"}
    assert welt["als"](a, "arbeiter").get("/api/v1/portal/dashboard").json()["kpis"] == []


def test_portal_storniert_nur_angefragte_auftraege_und_gibt_nichts_frei(welt):
    welt["zuordnen"](welt["a"], "hof-1", welt["k1"])
    kunde = welt["als"](welt["a"], "hof-1")
    eins = _anlegen(kunde)
    weg = f"{LD}/{eins['auftrag_id']}/status"
    assert kunde.post(weg, headers=_schluessel(), json={"aktion": "bestaetigen", "erwartete_version": 1}
                      ).status_code == 403
    assert kunde.post(weg, headers=_schluessel(), json={"aktion": "stornieren", "erwartete_version": 1,
                                                        "preis_indikativ_eur": 1}).status_code == 403
    assert _schritt(kunde, eins, "stornieren")["status"] == "storniert"
    zwei = _anlegen(welt["als"](welt["a"], "hof-1"))
    _schritt(welt["als"](welt["a"], *INNEN), zwei, "bestaetigen")
    r = welt["als"](welt["a"], "hof-1").post(f"{LD}/{zwei['auftrag_id']}/status", headers=_schluessel(),
                                             json={"aktion": "stornieren", "erwartete_version": 2})
    assert r.status_code == 409


def test_lohndienstleister_sieht_und_schliesst_nur_zugewiesene_auftraege(welt):
    a, k1 = welt["a"], welt["k1"]
    welt["zuordnen"](a, "hof-1", k1)
    welt["zuordnen"](a, "lohnunternehmer", k1, "lohndienstleister")
    inhaber = welt["als"](a, "hof-1")
    schlag = inhaber.post("/api/v1/portal/feldbuch/schlaege", json={"name": "Am Deich", "flaeche": 7.5})
    assert schlag.status_code == 201, schlag.text
    zugewiesen = _anlegen(inhaber, schlag_ids=[schlag.json()["id"]])
    anderer = _anlegen(welt["als"](a, "hof-1"))
    innen = welt["als"](a, *INNEN)
    zugewiesen = _schritt(innen, zugewiesen, "bestaetigen")
    falsch = innen.post(f"{LD}/{zugewiesen['auftrag_id']}/status", headers=_schluessel(), json={
        "aktion": "einplanen", "erwartete_version": 2, "geplant_datum": "2026-11-03",
        "dienstleister_subject": "irgendwer"})
    assert falsch.status_code == 422
    zugewiesen = _schritt(innen, zugewiesen, "einplanen", geplant_datum="2026-11-03",
                          dienstleister_subject="lohnunternehmer")
    lu = welt["als"](a, "lohnunternehmer")
    liste = lu.get(LD).json()["items"]
    assert [x["auftrag_id"] for x in liste] == [zugewiesen["auftrag_id"]]
    detail = lu.get(f"{LD}/{zugewiesen['auftrag_id']}").json()
    assert [s["name"] for s in detail["schlaege"]] == ["Am Deich"] and detail["dienstleister_subject"] is None
    assert lu.get(f"{LD}/{anderer['auftrag_id']}").status_code == 404
    assert lu.get("/api/v1/portal/feldbuch/schlaege").status_code == 403
    assert lu.post(f"{LD}/{anderer['auftrag_id']}/status", headers=_schluessel(),
                   json={"aktion": "abschliessen", "erwartete_version": 1}).status_code == 404
    assert _schritt(lu, zugewiesen, "abschliessen")["status"] == "abgeschlossen"
    # Fremde Schlaege kann niemand in einen Auftrag schreiben
    r = welt["als"](a, "hof-1").post(LD, json={"typ": "lohn_spritz", "schlag_ids": ["fremd"]}, headers=_schluessel())
    assert r.status_code == 422


def test_aussendienst_nur_mit_interner_fachrolle(welt):
    a, k1 = welt["a"], welt["k1"]
    welt["zuordnen"](a, "vertreter", k1, "aussendienst")
    assert welt["als"](a, "vertreter").get(LD).status_code == 403
    mit = welt["als"](a, "vertreter", "SALES_LESEN")
    assert mit.get(LD).status_code == 200
    assert mit.get("/api/v1/portal/rechnungen").status_code == 403
    konten = mit.get("/api/v1/portal/kundenkonten").json()
    assert [(k["customer_id"], k["rolle"]) for k in konten] == [(k1, "aussendienst")]


def test_inhaber_verwaltet_die_benutzer_seines_betriebs(welt):
    a, k1, k2 = welt["a"], welt["k1"], welt["k2"]
    welt["zuordnen"](a, "hof-1", k1)
    c = welt["als"](a, "hof-1")
    neu = c.post("/api/v1/portal/kundenzugaenge", json={"subject": "azubi", "customer_id": k1, "rolle": "mitarbeiter"})
    assert neu.status_code == 201, neu.text
    assert welt["als"](a, "hof-1").post("/api/v1/portal/kundenzugaenge", json={
        "subject": "x", "customer_id": k1, "rolle": "aussendienst"}).status_code == 403
    assert welt["als"](a, "hof-1").post("/api/v1/portal/kundenzugaenge", json={
        "subject": "x", "customer_id": k2, "rolle": "mitarbeiter"}).status_code == 403
    liste = welt["als"](a, "hof-1").get("/api/v1/portal/kundenzugaenge").json()
    assert {z["customer_id"] for z in liste} == {k1}
    assert welt["als"](a, "azubi").post("/api/v1/portal/kundenzugaenge", json={
        "subject": "y", "customer_id": k1, "rolle": "mitarbeiter"}).status_code == 403
    widerruf = welt["als"](a, "hof-1").post(f"/api/v1/portal/kundenzugaenge/{neu.json()['id']}/widerrufen")
    assert widerruf.status_code == 200
    assert welt["als"](a, "azubi").get("/api/v1/portal/feldbuch/schlaege").status_code == 403


def test_mitarbeiter_sieht_nur_zugewiesene_schlaege(welt):
    a, k1 = welt["a"], welt["k1"]
    welt["zuordnen"](a, "hof-1", k1)
    inhaber = welt["als"](a, "hof-1")
    eigen = inhaber.post("/api/v1/portal/feldbuch/schlaege", json={"name": "Zugewiesen", "flaeche": 2}).json()["id"]
    fremd = welt["als"](a, "hof-1").post("/api/v1/portal/feldbuch/schlaege", json={"name": "Anderer", "flaeche": 3}
                                         ).json()["id"]
    zuweisung = welt["als"](a, "hof-1").post("/api/v1/portal/kundenzugaenge", json={
        "subject": "arbeiter", "customer_id": k1, "rolle": "mitarbeiter", "schlag_ids": [eigen]})
    assert zuweisung.status_code == 201, zuweisung.text
    m = welt["als"](a, "arbeiter")
    assert [s["id"] for s in m.get("/api/v1/portal/feldbuch/schlaege").json()] == [eigen]
    assert m.get(f"/api/v1/portal/feldbuch/schlaege/{fremd}").status_code == 404
    massnahme = {"datum": "2026-10-14T08:00:00", "typ": "bodenbearbeitung"}
    assert m.post("/api/v1/portal/feldbuch/massnahmen", json={**massnahme, "schlag_id": fremd}).status_code == 404
    assert m.post("/api/v1/portal/feldbuch/massnahmen", json={**massnahme, "schlag_id": eigen}).status_code == 201
    welt["als"](a, "hof-1").post("/api/v1/portal/feldbuch/massnahmen", json={**massnahme, "schlag_id": fremd})
    m = welt["als"](a, "arbeiter")
    assert len(m.get("/api/v1/portal/feldbuch/massnahmen").json()) == 1
    stats = m.get("/api/v1/portal/feldbuch/stats").json()
    assert (stats["schlaege"], stats["massnahmen"]) == (1, 1)
    assert m.post("/api/v1/portal/feldbuch/schlaege", json={"name": "Neu", "flaeche": 1}).status_code == 403
    assert m.get("/api/v1/portal/feldbuch/duengebilanz").status_code == 403


# ── Empfehlungen ─────────────────────────────────────────────────────────────


def test_empfehlungen_ohne_dubletten_gekennzeichnet_und_kontogebunden(welt):
    a, k1, k2 = welt["a"], welt["k1"], welt["k2"]
    welt["zuordnen"](a, "hof-1", k1)
    innen = welt["als"](a, *INNEN)
    kontext = {"kunden_nr": k1, "kulturen": ["Winterweizen", "Raps"], "flaeche_ha": 50.0, "ernte_jahr": 2026}
    erst = innen.post("/api/v1/portal/empfehlungen/generieren/schlagkartei", json=kontext)
    assert erst.status_code == 201 and erst.json()["count"] == 4
    assert {e["herkunft"] for e in erst.json()["neue_empfehlungen"]} == {"regel"}
    assert welt["als"](a, *INNEN).post("/api/v1/portal/empfehlungen/generieren/schlagkartei", json=kontext
                                       ).json()["count"] == 0
    assert welt["als"](a, "lesen", "SALES_LESEN").post("/api/v1/portal/empfehlungen/generieren/schlagkartei",
                                                       json=kontext).status_code == 403
    assert welt["als"](a, *INNEN).post("/api/v1/portal/empfehlungen/generieren/schlagkartei",
                                       json={**kontext, "kunden_nr": welt["kb"]}).status_code == 404
    welt["als"](a, *INNEN).post("/api/v1/portal/empfehlungen/generieren/ration", json={
        "kunden_nr": k2, "tiere_anzahl": 80, "tier_kategorie": "Milchkuehe"})
    c = welt["als"](a, "hof-1")
    eigene = c.get("/api/v1/portal/empfehlungen").json()
    assert eigene["count"] == 4 and {e["customer_id"] for e in eigene["items"]} == {k1}
    assert c.get(f"/api/v1/portal/empfehlungen/{k2}").status_code == 404
    eid = eigene["items"][0]["empfehlung_id"]
    for _ in range(2):
        assert welt["als"](a, "hof-1").post(f"/api/v1/portal/empfehlungen/{k1}/gesehen/{eid}").status_code == 200
    with SessionLocal() as db:
        gesehen = db.execute(text("SELECT gesehen_von FROM domain_portal.empfehlungen WHERE id = :i"), {"i": eid}
                             ).scalar()
        assert gesehen == "hof-1"
        with pytest.raises(DBAPIError):
            db.execute(text(
                "INSERT INTO domain_portal.empfehlungen (id, tenant_id, customer_id, typ, prioritaet, titel, "
                "beschreibung, cta_label, cta_ziel, kontext_schluessel, kontext_wert, herkunft, erzeugt_von) VALUES "
                "(:i, :t, :c, 'lohndienst', 'hoch', 't', 'b', 'l', '/z', 'k', 'w', 'ki', 'agent')"),
                {"i": str(uuid.uuid4()), "t": a, "c": k1})


def test_empfehlungen_aus_parallelen_prozessen_ohne_dubletten(welt, tmp_path):
    start = tmp_path / "los"
    code = f"""
        import time, pathlib
        from app.core.database import SessionLocal
        from app.services.portal_intelligence_service import PortalIntelligenceService
        while not pathlib.Path({str(start)!r}).exists():
            time.sleep(0.01)
        with SessionLocal() as db:
            neu = PortalIntelligenceService(db, {welt['a']!r}).generiere_aus_ration(
                customer_id={welt['k1']!r}, akteur="innendienst", tiere_anzahl=80, tier_kategorie="Milchkuehe",
                benoetigt_rohwaren=[])
            print("ERGEBNIS:", len(neu))
    """
    prozesse = [_prozess(code, tmp_path) for _ in range(3)]
    time.sleep(8)
    start.write_text("x")
    assert sum(int(p.ergebnis()) for p in prozesse) == 9
    with SessionLocal() as db:
        assert db.execute(text("SELECT count(*) FROM domain_portal.empfehlungen WHERE tenant_id = :t"),
                          {"t": welt["a"]}).scalar() == 9  # 7 Rohwaren + 2 Lohndienste, je einmal


# ── Mandantengrenze ──────────────────────────────────────────────────────────


def test_lohndienst_bleibt_im_mandanten(welt):
    welt["zuordnen"](welt["a"], "hof-1", welt["k1"])
    auftrag = _anlegen(welt["als"](welt["a"], "hof-1"))
    fremd = welt["als"](welt["b"], "innendienst-b", "SALES_BEARBEITEN")
    assert fremd.get(f"{LD}/disposition").json()["count"] == 0
    assert fremd.post(f"{LD}/{auftrag['auftrag_id']}/status", headers=_schluessel(),
                      json={"aktion": "bestaetigen", "erwartete_version": 1}).status_code == 404
    welt["zuordnen"](welt["b"], "hof-b", welt["kb"])
    assert welt["als"](welt["b"], "hof-b").get(f"{LD}/{auftrag['auftrag_id']}").status_code == 404
    assert welt["als"](welt["a"], "hof-1").get(LD, headers={"X-Kundenkonto": welt["kb"]}).status_code == 403


# ── Innendienst-Sicht (portal_innendienst) ───────────────────────────────────


def test_innendienst_sicht_mit_rolle_im_mandanten_und_echten_spalten(welt):
    a, k1, k2 = welt["a"], welt["k1"], welt["k2"]
    welt["zuordnen"](a, "hof-1", k1)
    inhaber = welt["als"](a, "hof-1")
    schlag = inhaber.post("/api/v1/portal/feldbuch/schlaege", json={"name": "Nordfeld", "flaeche": 12.5,
                                                                     "kultur": "Winterweizen"}).json()["id"]
    r = welt["als"](a, "hof-1").post("/api/v1/portal/feldbuch/massnahmen", json={
        "datum": "2026-04-03T08:00:00", "typ": "psm", "schlag_id": schlag, "mittel": "Muster", "anwender": "MA-1"})
    assert r.status_code == 201, r.text
    innen = welt["als"](a, "innendienst", "SALES_LESEN")
    kopf = {"X-Kundenkonto": k1}
    schlaege = innen.get(f"/api/v1/innendienst/kunden/{k1}/schlaege", headers=kopf)
    assert schlaege.status_code == 200 and [s["name"] for s in schlaege.json()["schlaege"]] == ["Nordfeld"]
    massnahmen = innen.get(f"/api/v1/innendienst/kunden/{k1}/massnahmen", headers=kopf).json()["massnahmen"]
    assert [(m["schlag_name"], m["fahrer"]) for m in massnahmen] == [("Nordfeld", "MA-1")]
    assert innen.get(f"/api/v1/innendienst/kunden/{k2}/schlaege", headers=kopf).status_code == 404
    assert welt["als"](a, "irgendwer", "user").get(f"/api/v1/innendienst/kunden/{k1}/schlaege",
                                                   headers=kopf).status_code == 403
    assert welt["als"](welt["b"], "innendienst-b", "SALES_LESEN").get(
        f"/api/v1/innendienst/kunden/{k1}/schlaege", headers=kopf).status_code == 404
    potential = welt["als"](a, "innendienst", "SALES_LESEN").get("/api/v1/innendienst/potential")
    assert potential.status_code == 200 and potential.json()["schlag_kunden_count"] == 1
    assert welt["als"](a, "hof-1").get("/api/v1/innendienst/potential").status_code == 403
