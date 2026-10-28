"""Kein Rueckfall auf den Standardmandanten ueber settings.DEFAULT_TENANT_ID oder eine feste UUID.

Bis 28.10.2026 nahmen CRM-Kunden, Leads, Kundenberichte und -erweiterungen, Duenger, Saatgut und Naehrstoffe den
Mandanten aus ``?tenant_id=`` mit dem Standardmandanten als Rueckfall; ueber 30 Dienste setzten ``tenant_id or
_DEFAULT_TENANT``. Die Lead-Umwandlung las Leads ohne Mandantenfilter. Kanal-Wege nahmen den Mandanten aus Rumpf,
Query oder Slack-/Teams-Metadaten, Freigabeentscheidungen Entscheider und Rolle aus dem Rumpf.
"""
from __future__ import annotations

import asyncio
import importlib
import inspect
import os
import pkgutil
from types import SimpleNamespace
from uuid import uuid4

import pytest
import sqlalchemy as sa
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from app.api.v1.endpoints import (
    channel_work_surfaces, crm_reports, customer_extensions, customers, nutrient_compositions,
)
from app.core.tenant import get_tenant_id
from app.domains.agrar.api import duenger, saatgut
from app.domains.crm.api import customers as crm_customers, leads as crm_leads

ROUTER = (crm_reports, customer_extensions, customers, nutrient_compositions, duenger, saatgut, crm_customers, crm_leads,
          channel_work_surfaces)


def test_jeder_weg_nimmt_den_mandanten_aus_dem_token():
    funde = []
    for modul in ROUTER:
        for route in modul.router.routes:
            parameter = inspect.signature(route.endpoint).parameters
            vorgabe = parameter.get("tenant_id")
            if vorgabe is not None and getattr(vorgabe.default, "dependency", None) is not get_tenant_id:
                funde.append(f"{modul.__name__}:{route.path}")
    assert funde == []


def _dienste_mit_mandant():
    import app.services as paket

    for info in pkgutil.iter_modules(paket.__path__):
        modul = importlib.import_module(f"app.services.{info.name}")
        try:
            quelle = inspect.getsource(modul)
        except (OSError, TypeError):  # Paket ohne Quelltext (z. B. Namensraum)
            continue
        if 'raise ValueError("Mandant fehlt")' not in quelle:
            continue
        for _, klasse in inspect.getmembers(modul, inspect.isclass):
            if klasse.__module__ != modul.__name__:
                continue
            init = klasse.__dict__.get("__init__")
            try:
                if init is not None and 'raise ValueError("Mandant fehlt")' in inspect.getsource(init):
                    yield klasse
            except (OSError, TypeError):  # eingebautes oder erzeugtes __init__
                continue


def test_dienste_ohne_mandant_verweigern():
    klassen = list(_dienste_mit_mandant())
    assert len(klassen) >= 30
    for klasse in klassen:
        parameter = inspect.signature(klasse.__init__).parameters
        argumente = {n: None for n, p in parameter.items() if n != "self" and p.default is inspect.Parameter.empty}
        argumente["tenant_id"] = None
        with pytest.raises(ValueError, match="Mandant fehlt"):
            klasse(**argumente)


def test_inventar_ohne_mandant_403():
    from app.domains.inventory.api.inventory_auth import get_current_tenant_id

    anfrage = SimpleNamespace(state=SimpleNamespace(token_claims={}), headers={})
    with pytest.raises(HTTPException) as info:
        get_current_tenant_id(anfrage)
    assert info.value.status_code == 403


@pytest.fixture
def probe():
    url = os.environ.get("TEST_DATABASE_URL")
    if not url:
        pytest.skip("TEST_DATABASE_URL (valeo_probe) erforderlich")
    assert make_url(url).database == "valeo_probe" or os.environ.get("GITHUB_ACTIONS") == "true"
    engine = sa.create_engine(url)
    import sys
    sys.path.insert(0, "scripts")
    import rls_inventory

    with engine.connect() as conn:
        tx = conn.begin()
        rls_inventory._pending_upgrade(conn)  # u. a. crm_leads_spalten_20261028
        session = Session(bind=conn, join_transaction_mode="create_savepoint")
        try:
            yield session
        finally:
            session.close()
            tx.rollback()
    engine.dispose()


def test_fremder_lead_wird_nicht_zum_eigenen_kunden(probe):
    db = probe
    a, b = f"sm-a-{uuid4().hex[:8]}", f"sm-b-{uuid4().hex[:8]}"
    for t in (a, b):
        db.execute(sa.text("INSERT INTO domain_shared.tenants(id, name) VALUES (:t, :t)"), {"t": t})
    import rls_domain_support as support

    lead_id = support.insert_row(db.connection(), "domain_crm.leads", b)
    vorher = db.execute(sa.text("SELECT status FROM domain_crm.leads WHERE id = :id"), {"id": lead_id}).scalar()
    with pytest.raises(HTTPException) as info:
        asyncio.run(customer_extensions.convert_lead_to_customer(
            customer_extensions.ConvertLeadRequest(lead_id=lead_id), tenant_id=a, db=db))
    assert info.value.status_code == 404
    assert db.execute(sa.text("SELECT status FROM domain_crm.leads WHERE id = :id"), {"id": lead_id}).scalar() == vorher


# --- Kanal-Wege --------------------------------------------------------------------------------------------------

def _kanal(rollen=("teamleiter",), mandant="t1"):
    from app.auth.deps import get_current_user
    from app.core.database import get_db

    app = FastAPI()
    app.include_router(channel_work_surfaces.router)
    app.dependency_overrides[get_tenant_id] = lambda: mandant
    app.dependency_overrides[get_current_user] = lambda: {"sub": "geprueft-1", "roles": list(rollen)}
    app.dependency_overrides[get_db] = lambda: None
    return TestClient(app, raise_server_exceptions=False)


def test_freigabe_braucht_die_rolle_und_den_eigenen_thread(monkeypatch):
    thread = SimpleNamespace(tenant_id="t1", status="pending", as_dict=lambda: {"status": "approved"})
    store = SimpleNamespace(get=lambda tid: thread if tid == "th-1" else None)
    entschieden = {}

    def entscheide(**kw):
        entschieden.update(kw)
        return thread

    monkeypatch.setattr(channel_work_surfaces, "get_channel_process_thread_store", lambda db=None: store)
    monkeypatch.setattr(channel_work_surfaces, "decide_channel_process_action", entscheide)
    monkeypatch.setattr("app.core.blockchain_anchor_runtime.anchor_channel_process_thread",
                        lambda db, thread: SimpleNamespace(as_dict=lambda: {}))
    rumpf = {"decision": "GENEHMIGT", "approver_role": "teamleiter", "begruendung": "ok", "entschieden_von": "jemand"}

    assert _kanal(rollen=("sachbearbeiter",)).post("/channels/slack/process-actions/th-1/decision", json=rumpf).status_code == 403
    assert _kanal(mandant="t2").post("/channels/slack/process-actions/th-1/decision", json=rumpf).status_code == 404
    assert entschieden == {}
    antwort = _kanal().post("/channels/slack/process-actions/th-1/decision", json=rumpf)
    assert antwort.status_code == 200, antwort.text
    assert entschieden["entschieden_von"] == "geprueft-1"


def test_freigabe_ueber_kanal_eingang_ist_gesperrt():
    from app.core.channel_ingress import ChannelIngressEnvelope, dispatch_channel_ingress
    from app.core.knowledge_core_contracts import KnowledgeChannel

    umschlag = ChannelIngressEnvelope(kanal=KnowledgeChannel.SLACK, intent="approval_decision", tenant_id="t1",
                                      rolle="teamleiter", query="ok", payload={"thread_id": "th-1", "decision": "GENEHMIGT",
                                                                               "approver_role": "teamleiter"})
    with pytest.raises(PermissionError):
        dispatch_channel_ingress(None, umschlag)


def test_kanal_eingang_nimmt_den_mandanten_der_anmeldung():
    from app.core.channel_ingress import normalize_slack_event, normalize_teams_event

    slack = normalize_slack_event({"event": {"text": "hilfe", "metadata": {"tenant_id": "fremd"}}}, tenant_id="t1")
    teams = normalize_teams_event({"text": "hilfe", "channelData": {"metadata": {"tenant_id": "fremd"}}}, tenant_id="t1")
    assert (slack.tenant_id, teams.tenant_id) == ("t1", "t1")


# --- Naehrstoffgehalte unter RLS (rls_nutrient_compositions_20261028) ------------------------------------------

NAEHRSTOFFE = "domain_agrar.nutrient_compositions"


def test_naehrstoffe_mandantengrenze():
    import rls_domain_support as support

    with support.probe((NAEHRSTOFFE, "domain_inventory.articles")) as conn:
        support.ensure_tenants(conn, support.A, support.B)
        eigen, fremd = (support.insert_row(conn, NAEHRSTOFFE, t) for t in (support.A, support.B))
        support.as_app(conn)
        assert support.shape(conn, NAEHRSTOFFE) == ("getrennt", "")
        support.assert_tenant_isolation(conn, NAEHRSTOFFE, eigen, fremd, None)


def test_artikel_verweist_nicht_auf_fremde_naehrstoffe():
    import rls_domain_support as support

    with support.probe((NAEHRSTOFFE, "domain_inventory.articles")) as conn:
        support.ensure_tenants(conn, support.A, support.B)
        fremd = support.insert_row(conn, NAEHRSTOFFE, support.B)
        meldung = support.as_owner_rejected(
            conn, "INSERT INTO domain_inventory.articles (id, article_number, name, tenant_id, duengemittel_inhalte_id) "
                  "VALUES (:id, :id, 'Duenger', :a, :n)", {"id": str(uuid4()), "a": support.A, "n": fremd})
        assert "fk_articles_duengemittel_inhalte_id_tenant" in meldung
