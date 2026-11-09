"""Bestellvorschlag -> Bestellentwurf in DocFlow (BELEG-052 Stufe 3, 09.11.2026).

Vorher legte "zu Bestellung" eine EinkaufBestellung an: fester Steuersatz 7 %, Preis "je 100 kg" gegen eine Menge
in t geteilt durch 100. Jetzt entsteht je Lieferant ein DocFlow-Bestellentwurf; die Menge steht in der Einheit des
Preises (dt bei Preis je 100 kg), ohne Steuervorgabe, mit dem Bearbeiter aus dem Token.
"""
from __future__ import annotations

import os
import uuid

import pytest

pytestmark = pytest.mark.integration

DB_URL = os.environ.get("TEST_DATABASE_URL", os.environ.get(
    "DATABASE_URL", "postgresql://valeo_dev:valeo_dev_2024@127.0.0.1:5432/valeo_probe"))
os.environ.setdefault("DATABASE_URL", DB_URL)


@pytest.fixture(scope="module")
def umgebung():
    from sqlalchemy import create_engine, text

    try:
        engine = create_engine(DB_URL, connect_args={"connect_timeout": 5})
        engine.connect().close()
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank nicht erreichbar: {fehler}")
    mandant, lieferant = f"bv-{uuid.uuid4().hex[:8]}", str(uuid.uuid4())
    with engine.begin() as v:
        v.execute(text("INSERT INTO domain_shared.tenants (id, name) VALUES (:id, :id) ON CONFLICT (id) DO NOTHING"),
                  {"id": mandant})
        v.execute(text("INSERT INTO domain_einkauf.lieferanten (id, tenant_id, lieferantennummer, firmenname) "
                       "VALUES (:id, :t, 'L-BV', 'Landhandel Nord')"), {"id": lieferant, "t": mandant})
    yield {"mandant": mandant, "lieferant": lieferant, "engine": engine}
    from test_belege_lesen import AUFRAEUMEN

    with engine.begin() as v:
        v.execute(text("SELECT set_config('valeo.docflow_wartung', 'loeschen', true)"))
        v.execute(text("DELETE FROM domain_einkauf.bestellvorschlag_positionen WHERE vorschlag_id IN "
                       "(SELECT id FROM domain_einkauf.bestellvorschlaege WHERE tenant_id = :t)"), {"t": mandant})
        v.execute(text("DELETE FROM domain_einkauf.bestellvorschlaege WHERE tenant_id = :t"), {"t": mandant})
        v.execute(text("DELETE FROM domain_einkauf.lieferanten WHERE tenant_id = :t"), {"t": mandant})
        for sql in AUFRAEUMEN:
            v.execute(text(sql), {"t": mandant})


@pytest.fixture()
def client(umgebung):
    from fastapi.testclient import TestClient

    from app.auth.deps import get_current_user
    from app.main import app

    vorher = app.dependency_overrides.get(get_current_user)
    app.dependency_overrides[get_current_user] = lambda: {"sub": "einkaeufer-1", "roles": ["EINKAUF_BEARBEITEN",
                                                                                            "EINKAUF_LESEN"]}
    yield TestClient(app, raise_server_exceptions=False)
    if vorher is None:
        app.dependency_overrides.pop(get_current_user, None)
    else:
        app.dependency_overrides[get_current_user] = vorher


def test_vorschlag_wird_docflow_bestellentwurf_in_dt(client, umgebung):
    from sqlalchemy import text

    kopf = {"X-Tenant-Id": umgebung["mandant"], "Authorization": "Bearer dev-token"}
    angelegt = client.post("/api/v1/einkauf/bestellvorschlaege", headers=kopf, json={
        "vorschlag_typ": "lager", "bezeichnung": "Test", "positionen": [{
            "article_id": str(uuid.uuid4()), "artikel_nr": "WEIZEN", "artikel_bezeichnung": "Weizen B",
            "einheit": "t", "vorschlag_menge": 5, "lieferant_id": umgebung["lieferant"],
            "letzter_preis": 21.5, "preis_einheit": "100kg"}]})
    assert angelegt.status_code == 201, angelegt.text
    antwort = client.post(f"/api/v1/einkauf/bestellvorschlaege/{angelegt.json()['id']}/zu-bestellung", headers=kopf)
    assert antwort.status_code == 201, antwort.text
    [bestellung] = antwort.json()["bestellungen"]
    with umgebung["engine"].connect() as c:
        beleg = c.execute(text("SELECT doc_type, status, supplier_id, source_system, created_by "
                               "FROM domain_docflow.document_headers WHERE id = :id AND tenant_id = :t"),
                          {"id": bestellung["bestellung_id"], "t": umgebung["mandant"]}).mappings().one()
        position = c.execute(text("SELECT quantity, unit, unit_price, tax_rate FROM domain_docflow.document_items "
                                  "WHERE header_id = :id"), {"id": bestellung["bestellung_id"]}).mappings().one()
        alt = c.execute(text("SELECT count(*) FROM domain_einkauf.bestellungen WHERE tenant_id = :t"),
                        {"t": umgebung["mandant"]}).scalar()
    assert (beleg["doc_type"], beleg["status"], beleg["supplier_id"]) == ("purchase_order", "draft",
                                                                         umgebung["lieferant"])
    assert beleg["source_system"] == "bestellvorschlag"
    assert (float(position["quantity"]), position["unit"], float(position["unit_price"])) == (50.0, "dt", 21.5)
    assert float(bestellung["netto_summe"]) == pytest.approx(1075.0)  # 50 dt x 21,50 EUR
    assert alt == 0


def test_berechnung_speichern_und_zu_bestellung_als_kommando(client, umgebung):
    """Familie bestellvorschlag: Speichern rechnet auf dem Server, "Zu Bestellung" legt den DocFlow-Entwurf an."""
    kopf = {"X-Tenant-Id": umgebung["mandant"], "Authorization": "Bearer dev-token"}
    leer = client.post("/api/v1/einkauf/bestellvorschlaege/berechnung/lager/actions/speichern", headers=kopf,
                       json={"_mode": "dryRun"}).json()
    assert leer["success"] is False and "Kein Bedarf" in leer["error"]  # leerer Mandant: nichts zu bestellen
    angelegt = client.post("/api/v1/einkauf/bestellvorschlaege", headers=kopf, json={
        "vorschlag_typ": "lager", "positionen": [{
            "article_id": str(uuid.uuid4()), "artikel_nr": "GERSTE", "einheit": "dt", "vorschlag_menge": 10,
            "lieferant_id": umgebung["lieferant"], "letzter_preis": 18.0, "preis_einheit": "100kg"}]}).json()
    erst = client.post(f"/api/v1/einkauf/bestellvorschlaege/{angelegt['id']}/actions/zu_bestellung",
                       headers=kopf, json={}).json()
    assert erst["success"] is True, erst
    zweit = client.post(f"/api/v1/einkauf/bestellvorschlaege/{angelegt['id']}/actions/zu_bestellung",
                        headers=kopf, json={}).json()
    assert zweit["success"] is False and "bereits bestellt" in zweit["error"]


def test_neuroassist_workflow_legt_docflow_entwurf_an(umgebung):
    """Agenten-Workflow Bestellvorschlag (09.11.2026): derselbe DocFlow-Weg, Menge in der Preiseinheit, wiederholbar."""
    from sqlalchemy import text

    from app.agents.workflows import bestellvorschlag as workflow

    korrelation = str(uuid.uuid4())
    posten = [{"article_id": str(uuid.uuid4()), "artikel_nr": "RAPS", "artikel_bezeichnung": "Raps", "menge": 2,
               "einheit": "t", "einzelpreis": 45.0, "preis_einheit": "100kg"}]
    erst = workflow._persist_purchase_order(tenant_id=umgebung["mandant"], supplier_id=umgebung["lieferant"],
                                            items=posten, correlation_id=korrelation, ai_recommendations=[])
    nochmal = workflow._persist_purchase_order(tenant_id=umgebung["mandant"], supplier_id=umgebung["lieferant"],
                                               items=posten, correlation_id=korrelation, ai_recommendations=[])
    assert erst == nochmal
    with umgebung["engine"].connect() as c:
        kopf = c.execute(text("SELECT doc_type, status, source_system, created_by FROM domain_docflow.document_headers "
                              "WHERE id = :id"), {"id": erst}).mappings().one()
        position = c.execute(text("SELECT quantity, unit FROM domain_docflow.document_items WHERE header_id = :id"),
                             {"id": erst}).mappings().one()
    assert (kopf["doc_type"], kopf["status"], kopf["source_system"]) == ("purchase_order", "draft", "neuroassist")
    assert (float(position["quantity"]), position["unit"]) == (20.0, "dt")
