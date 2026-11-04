"""Kein Rueckfall auf 'default': Mandant aus dem Token, jede Abfrage im eigenen Mandanten.

Bis 27.10.2026 lasen Tankstelle, Wartung, Versicherungen, Projekte, Verladung, Ernteplanung und EDI **ohne jeden
Mandantenfilter** und schrieben den Mandanten aus dem Rumpf mit ``"default"`` als Vorgabe; eine Zapfung minderte den
Tankbestand des ersten Treffers zu diesem Artikel, gleich welchen Mandanten. Controlling- und Finanzaktionen nahmen
``x_tenant_id or "default"``, die Service-Anfragen hielten ihre Daten in einem Woerterbuch des Prozesses.

Pruefstand ``valeo_probe``: ausstehende Migrationen und eigene Zeilen in einer Transaktion, die zurueckgerollt wird.
"""
from __future__ import annotations

import asyncio
import inspect
import os
import sys
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

import pytest
import sqlalchemy as sa
from fastapi import HTTPException
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

import rls_domain_support as support
from app.api.v1.endpoints import (
    controlling_actions, edi_api, ernte_planung, external_agent_integrations, finance_actions, projekte,
    service_anfragen, tankstelle, verladung, versicherungen, wartung,
)
from app.core.tenant import get_tenant_id

pytestmark = pytest.mark.integration
ROOT = Path(__file__).resolve().parents[1]
A, B = support.A, support.B
SERVICE = ("domain_ops.service_anfragen", "domain_ops.service_anfrage_rueckmeldungen")


def _anfrage(sub: str = "service-bearbeiter"):
    return SimpleNamespace(state=SimpleNamespace(token_claims={"sub": sub}))


@pytest.fixture
def db():
    url = os.environ.get("TEST_DATABASE_URL")
    if not url:
        pytest.skip("TEST_DATABASE_URL (valeo_probe) erforderlich")
    assert make_url(url).database == "valeo_probe" or os.environ.get("GITHUB_ACTIONS") == "true"
    sys.path.insert(0, str(ROOT / "scripts"))
    import rls_inventory

    engine = sa.create_engine(url)
    with engine.connect() as conn:
        tx = conn.begin()
        rls_inventory._pending_upgrade(conn)
        support.ensure_tenants(conn, A, B)
        session = Session(bind=conn, join_transaction_mode="create_savepoint")
        try:
            yield session
        finally:
            session.close()
            tx.rollback()
    engine.dispose()


def _404(aufruf):
    with pytest.raises(HTTPException) as info:
        aufruf()
    assert info.value.status_code == 404


def test_zapfung_mindert_nur_den_eigenen_tankbestand(db):
    for t, liter in ((A, 1000), (B, 500)):
        db.execute(sa.text("INSERT INTO domain_ops.ops_tank_bestand (id, artikel, tenant_id, bestand_liter) "
                           "VALUES (:id, :artikel, :t, :l)"), {"id": f"TB-{t}", "artikel": f"Diesel-{t}", "t": t, "l": liter})
    # Der Artikel heisst bei beiden gleich (eindeutig ist er heute systemweit, darum zwei Namen und ein Umbenennen).
    db.execute(sa.text("UPDATE domain_ops.ops_tank_bestand SET artikel = 'Diesel' WHERE id = :id"), {"id": f"TB-{A}"})
    zapfung = tankstelle.create_zapfung(
        tankstelle.ZapfungPayload(kennzeichen="LER-AB 1", artikel="Diesel", menge=100, zeitstempel="2026-10-27T08:00:00"),
        _anfrage("tankwart"), tenant_id=A, db=db)
    assert (zapfung["tenant_id"], zapfung["created_by"]) == (A, "tankwart")
    bestand = dict(db.execute(sa.text("SELECT tenant_id, bestand_liter FROM domain_ops.ops_tank_bestand "
                                      "WHERE tenant_id IN (:a, :b)"), {"a": A, "b": B}).all())
    assert (float(bestand[A]), float(bestand[B])) == (900.0, 500.0)
    assert tankstelle.list_zapfungen(kennzeichen=None, artikel=None, skip=0, limit=100, tenant_id=B, db=db) == []
    assert [z["id"] for z in tankstelle.list_zapfungen(kennzeichen=None, artikel=None, skip=0, limit=100, tenant_id=A, db=db)] == [zapfung["id"]]
    assert [b["tenant_id"] for b in tankstelle.list_bestand(tenant_id=B, db=db)] == [B]
    _404(lambda: tankstelle.get_zapfung(zapfung["id"], tenant_id=B, db=db))
    _404(lambda: tankstelle.delete_zapfung(zapfung["id"], tenant_id=B, db=db))


@pytest.mark.parametrize("fall", ["wartung", "projekte", "versicherungen", "ernte"])
def test_crud_nur_im_eigenen_mandanten(db, fall):
    if fall == "wartung":
        neu = wartung.create_anlage(wartung.AnlagePayload(name="Trockner", typ="Trockner", standort="Hof"), _anfrage(), tenant_id=A, db=db)
        liste, holen, loeschen = wartung.list_anlagen, wartung.get_anlage, wartung.delete_anlage
        _404(lambda: wartung.create_protokoll(neu["id"], wartung.ProtokollPayload(datum="2026-10-27T08:00:00", art="Inspektion"),
                                              _anfrage(), tenant_id=B, db=db))
        proto = wartung.create_protokoll(neu["id"], wartung.ProtokollPayload(datum="2026-10-27T08:00:00", art="Inspektion"),
                                         _anfrage(), tenant_id=A, db=db)
        assert proto["tenant_id"] == A and wartung.list_protokolle(neu["id"], tenant_id=B, db=db) == []
    elif fall == "projekte":
        neu = projekte.create_projekt(projekte.ProjektPayload(name="Hallenbau"), _anfrage(), tenant_id=A, db=db)
        liste, holen, loeschen = projekte.list_projekte, projekte.get_projekt, projekte.delete_projekt
        _404(lambda: projekte.create_aufgabe(neu["id"], projekte.AufgabePayload(titel="Statik"), tenant_id=B, db=db))
        aufgabe = projekte.create_aufgabe(neu["id"], projekte.AufgabePayload(titel="Statik"), tenant_id=A, db=db)
        assert aufgabe["tenant_id"] == A and projekte.list_aufgaben(neu["id"], tenant_id=B, db=db) == []
    elif fall == "versicherungen":
        felder = {n: ("x" * 3) for n, f in versicherungen.VersicherungPayload.model_fields.items()
                  if f.is_required() and f.annotation is str}
        felder["vertragsnummer"] = f"VS-{uuid4().hex[:8]}"
        andere = {n: 1 for n, f in versicherungen.VersicherungPayload.model_fields.items()
                  if f.is_required() and n not in felder}
        neu = versicherungen.create_versicherung(versicherungen.VersicherungPayload(**felder, **andere), _anfrage(), tenant_id=A, db=db)
        liste, holen, loeschen = versicherungen.list_versicherungen, versicherungen.get_versicherung, versicherungen.delete_versicherung
    else:
        neu = ernte_planung.create_ernte(ernte_planung.ErntePayload(schlag="S1", kultur="Weizen", datum="2026-08-01"),
                                         tenant_id=A, db=db)
        liste, holen, loeschen = ernte_planung.list_ernten, ernte_planung.get_ernte, ernte_planung.delete_ernte
    assert neu["tenant_id"] == A
    if fall != "ernte":
        assert neu["created_by"] == "service-bearbeiter"
    seite = {"status": None, "skip": 0, "limit": 100}
    assert liste(tenant_id=B, db=db, **seite) == []
    assert neu["id"] in [r["id"] for r in liste(tenant_id=A, db=db, **seite)]
    _404(lambda: holen(neu["id"], tenant_id=B, db=db))
    _404(lambda: loeschen(neu["id"], tenant_id=B, db=db))
    loeschen(neu["id"], tenant_id=A, db=db)


def test_edi_nachricht_und_partner_im_mandanten_des_tokens(db):
    partner = edi_api.create_partner(edi_api.EdiPartnerCreateRequest(gln=f"40{uuid4().int % 10**11:011d}", name="Muehle",
                                                                     aktive_nachrichtentypen=["ORDERS"]), tenant_id=A, db=db)
    assert [p["partner_id"] for p in edi_api.list_partner(tenant_id=A, db=db)] == [partner["partner_id"]]
    assert edi_api.list_partner(tenant_id=B, db=db) == []


@pytest.fixture
def service(db):
    """Service-Tabellen unter RLS: geprueft wird als valeo_app, angelegt ueber die Wege als Eigentuemer."""
    return db


def test_service_anfragen_liegen_in_der_datenbank(service):
    db = service
    erste = asyncio.run(service_anfragen.create_anfrage(
        service_anfragen.ServiceAnfrageCreate(kunde="Landhandel Nord", betreff="Lieferverzug"), _anfrage(), tenant_id=A, db=db))
    zweite = asyncio.run(service_anfragen.create_anfrage(
        service_anfragen.ServiceAnfrageCreate(kunde="Agrar Mueller", betreff="Feuchte"), _anfrage(), tenant_id=A, db=db))
    jahr = erste["nummer"][3:7]
    assert (erste["nummer"], zweite["nummer"]) == (f"SR-{jahr}-001", f"SR-{jahr}-002")
    assert (erste["tenant_id"], erste["erstellt_von"], erste["status"]) == (A, "service-bearbeiter", "neu")
    fremd = asyncio.run(service_anfragen.create_anfrage(
        service_anfragen.ServiceAnfrageCreate(kunde="Fremd", betreff="x"), _anfrage(), tenant_id=B, db=db))
    assert fremd["nummer"] == f"SR-{jahr}-001"  # Nummernkreis je Mandant

    liste = asyncio.run(service_anfragen.list_anfragen(status=None, prioritaet=None, skip=0, limit=50, tenant_id=A, db=db))
    assert liste["total"] == 2 and {i["id"] for i in liste["items"]} == {erste["id"], zweite["id"]}
    for aufruf in (
        lambda: service_anfragen.get_anfrage(erste["id"], tenant_id=B, db=db),
        lambda: service_anfragen.delete_anfrage(erste["id"], tenant_id=B, db=db),
        lambda: service_anfragen.create_rueckmeldung(service_anfragen.RueckmeldungCreate(anfrage_id=erste["id"], text="x"),
                                                     _anfrage(), tenant_id=B, db=db),
        lambda: service_anfragen.close_service_case(service_anfragen.AbschlussCreate(anfrage_id=erste["id"]), tenant_id=B, db=db),
    ):
        with pytest.raises(HTTPException) as info:
            asyncio.run(aufruf())
        assert info.value.status_code == 404

    asyncio.run(service_anfragen.create_rueckmeldung(
        service_anfragen.RueckmeldungCreate(anfrage_id=erste["id"], text="Ware ist da", bewertung=4), _anfrage("kundin"),
        tenant_id=A, db=db))
    zu = asyncio.run(service_anfragen.close_service_case(
        service_anfragen.AbschlussCreate(anfrage_id=erste["id"], abschluss_grund="geliefert"), tenant_id=A, db=db))
    assert zu["status"] == "erledigt" and zu["abgeschlossen_am"]
    detail = asyncio.run(service_anfragen.get_anfrage(erste["id"], tenant_id=A, db=db))
    assert [r["erstellt_von"] for r in detail["rueckmeldungen"]] == ["kundin"]
    for aufruf in (
        lambda: service_anfragen.update_anfrage(erste["id"], service_anfragen.ServiceAnfrageUpdate(betreff="neu"), tenant_id=A, db=db),
        lambda: service_anfragen.close_service_case(service_anfragen.AbschlussCreate(anfrage_id=erste["id"]), tenant_id=A, db=db),
    ):
        with pytest.raises(HTTPException) as info:
            asyncio.run(aufruf())
        assert info.value.status_code == 409
    with pytest.raises(HTTPException) as info:
        asyncio.run(service_anfragen.create_anfrage(
            service_anfragen.ServiceAnfrageCreate(nummer=erste["nummer"], kunde="x", betreff="x"), _anfrage(), tenant_id=A, db=db))
    assert info.value.status_code == 409
    with pytest.raises(Exception):
        service_anfragen.ServiceAnfrageUpdate(status="erledigt")


@pytest.mark.parametrize("table", SERVICE)
def test_service_tabellen_unter_getrennten_policies(table):
    with support.probe(SERVICE) as conn:
        support.ensure_tenants(conn, A, B)
        eltern = {t: support.insert_row(conn, SERVICE[0], t, erstellt_von="x", nummer=f"SR-T-{t}") for t in (A, B)}
        if table == SERVICE[0]:
            own, foreign = eltern[A], eltern[B]
            neu = None
        else:
            own, foreign = (support.insert_row(conn, table, t, anfrage_id=eltern[t], erstellt_von="x", text="x") for t in (A, B))

            def neu(t):
                return support.insert_row(conn, table, t, anfrage_id=eltern[A], erstellt_von="x", text="x")
        support.as_app(conn)
        support.assert_tenant_isolation(conn, table, own, foreign, None, new_row=neu,
                                        values={"erstellt_von": "x"} if table == SERVICE[0] else None)


def test_rueckmeldung_haengt_nicht_an_fremder_anfrage():
    with support.probe(SERVICE) as conn:
        support.ensure_tenants(conn, A, B)
        fremde = support.insert_row(conn, SERVICE[0], B, erstellt_von="x", nummer="SR-T-B")
        meldung = support.as_owner_rejected(
            conn, "INSERT INTO domain_ops.service_anfrage_rueckmeldungen (id, tenant_id, anfrage_id, text, erstellt_von) "
                  "VALUES (:id, :t, :a, 'x', 'x')", {"id": str(uuid4()), "t": A, "a": fremde})
        assert "fk_service_rueckmeldung_anfrage" in meldung


def test_kein_platzhalter_mandant():
    with support.probe(SERVICE) as conn:
        support.ensure_tenants(conn, "default")
        meldung = support.as_owner_rejected(
            conn, "INSERT INTO domain_ops.service_anfragen (id, tenant_id, nummer, kunde, betreff, erstellt_von) "
                  "VALUES (:id, 'default', 'SR-X', 'x', 'x', 'x')", {"id": str(uuid4())})
        assert "check" in meldung.lower()


ROUTER = (tankstelle, wartung, versicherungen, projekte, verladung, ernte_planung, edi_api, controlling_actions,
          finance_actions, service_anfragen, external_agent_integrations)


def test_jeder_weg_nimmt_den_mandanten_aus_dem_token():
    funde = []
    for modul in ROUTER:
        for route in modul.router.routes:
            parameter = inspect.signature(route.endpoint).parameters
            if "tenant_id" in parameter:
                vorgabe = parameter["tenant_id"].default
                if getattr(vorgabe, "dependency", None) is not get_tenant_id and not route.path.count("{tenant_id}"):
                    funde.append(f"{modul.__name__}:{route.path}")
            for name in ("x_tenant_id", "x_tenant"):
                if name in parameter:
                    funde.append(f"{modul.__name__}:{route.path}:{name}")
    assert funde == []
    for modul in ROUTER:
        quelle = Path(modul.__file__).read_text(encoding="utf-8")
        assert '"default"' not in quelle or modul is external_agent_integrations, modul.__name__
        assert "_store" not in quelle or modul is not service_anfragen


def test_anlage_setzt_den_mandanten_selbst():
    for modell in (tankstelle.ZapfungPayload, wartung.AnlagePayload, wartung.ProtokollPayload, projekte.ProjektPayload,
                   projekte.AufgabePayload, versicherungen.VersicherungPayload, verladung.VerladungPayload,
                   ernte_planung.ErntePayload, edi_api.EdiNachrichtEmpfangRequest, edi_api.EdiPartnerCreateRequest):
        assert "tenant_id" not in modell.model_fields, modell.__name__
