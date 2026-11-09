"""Partnerstamm-Pflege in der Kundenakte crm/customer-360 (09.11.2026).

Bis dahin pflegte nur der handgebaute Kundenstamm ``verkauf/kunden-stamm`` Anschriften, Ansprechpartner, CPD-Konten,
Rabatte, Preise und Chef-Anweisungen. Jetzt sind es Kommandowege der Studio-Maske (Maske, CLI, MCP): Trockenlauf
ohne Wirkung, mandantengebunden, Entfernen nur mit Begruendung.
"""
from __future__ import annotations

import os
import uuid

import pytest

pytestmark = pytest.mark.integration

DB_URL = os.environ.get("TEST_DATABASE_URL", os.environ.get(
    "DATABASE_URL", "postgresql://valeo_dev:valeo_dev_2024@127.0.0.1:5432/valeo_probe"))
os.environ.setdefault("DATABASE_URL", DB_URL)

_NUTZER = {"sub": "pruefer-ks", "roles": ["CRM_BEARBEITEN", "CRM_LESEN"]}


@pytest.fixture(scope="module")
def stamm():
    from sqlalchemy import create_engine, text

    from test_crm360_kunde_wird_gefunden import _BP_FLAGS

    try:
        engine = create_engine(DB_URL, connect_args={"connect_timeout": 5})
        engine.connect().close()
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank nicht erreichbar: {fehler}")
    mandant, kunde, partner = str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4())
    with engine.begin() as v:
        v.execute(text("INSERT INTO domain_shared.tenants (id, name, domain, is_active) "
                       "VALUES (:id, :id, :d, true) ON CONFLICT (id) DO NOTHING"), {"id": mandant, "d": f"{mandant}.test"})
        spalten = ", ".join(_BP_FLAGS)
        werte = ", ".join("true" if s == "is_customer" else "false" for s in _BP_FLAGS)
        v.execute(text(f"INSERT INTO domain_crm.business_partners (partner_id, tenant_id, partner_number, name_1, status, "
                       f"{spalten}) VALUES (:id, :t, :nr, 'Hof Pflege', 'active', {werte})"),
                  {"id": partner, "t": mandant, "nr": f"BP-{uuid.uuid4().hex[:5]}"})
        v.execute(text("INSERT INTO domain_crm.customers (id, tenant_id, customer_number, company_name, business_partner_id) "
                       "VALUES (:id, :t, :nr, 'Hof Pflege', :p)"),
                  {"id": kunde, "t": mandant, "nr": f"KD-{uuid.uuid4().hex[:5]}", "p": partner})
    yield {"mandant": mandant, "kunde": kunde, "partner": partner, "engine": engine}
    with engine.begin() as v:
        for t in ("business_partner_addresses", "business_partner_contacts", "business_partner_discount_items"):
            v.execute(text(f"DELETE FROM domain_crm.{t} WHERE tenant_id = :t"), {"t": mandant})
        v.execute(text("DELETE FROM domain_crm.crm_action_audit_log WHERE tenant_id = :t"), {"t": mandant})
        v.execute(text("DELETE FROM outbox_events WHERE tenant_id = :t"), {"t": mandant})
        v.execute(text("DELETE FROM domain_crm.customers WHERE tenant_id = :t"), {"t": mandant})
        v.execute(text("DELETE FROM domain_crm.business_partners WHERE tenant_id = :t"), {"t": mandant})
        v.execute(text("DELETE FROM domain_shared.tenants WHERE id = :t"), {"t": mandant})


@pytest.fixture()
def client(stamm):
    from fastapi.testclient import TestClient

    from app.auth.deps import get_current_user
    from app.main import app

    vorher = app.dependency_overrides.get(get_current_user)
    app.dependency_overrides[get_current_user] = lambda: dict(_NUTZER)
    yield TestClient(app, raise_server_exceptions=False)
    if vorher is None:
        app.dependency_overrides.pop(get_current_user, None)
    else:
        app.dependency_overrides[get_current_user] = vorher


def _post(client, stamm, pfad: str, mandant: str | None = None, **rumpf):
    return client.post(f"/api/v1{pfad}", json=rumpf,
                       headers={"X-Tenant-Id": mandant or stamm["mandant"], "Authorization": "Bearer dev-token"}).json()


def _anschriften(stamm) -> list[dict]:
    from sqlalchemy import text

    with stamm["engine"].connect() as c:
        return [dict(r) for r in c.execute(text(
            "SELECT id::text AS id, city, partner_id::text AS partner FROM domain_crm.business_partner_addresses "
            "WHERE tenant_id = :t"), {"t": stamm["mandant"]}).mappings()]


def test_trockenlauf_legt_nichts_an(client, stamm):
    antwort = _post(client, stamm, f"/crm/customers/{stamm['kunde']}/actions/anschrift_anlegen", _mode="dryRun",
                    address_type="shipping", city="Leer")
    assert antwort["success"] is True, antwort
    assert _anschriften(stamm) == []


def test_anschrift_anlegen_aendern_entfernen(client, stamm):
    neu = _post(client, stamm, f"/crm/customers/{stamm['kunde']}/actions/anschrift_anlegen",
                address_type="shipping", name_1="Hof Pflege Lager", city="Leer", unbekannt="x")
    assert neu["success"] is True, neu
    [zeile] = _anschriften(stamm)
    assert zeile["partner"] == stamm["partner"] and zeile["city"] == "Leer"
    geaendert = _post(client, stamm, f"/crm/kunden-stamm/anschrift/{zeile['id']}/actions/aendern", city="Aurich")
    assert geaendert["success"] is True, geaendert
    assert _anschriften(stamm)[0]["city"] == "Aurich"
    ohne_grund = _post(client, stamm, f"/crm/kunden-stamm/anschrift/{zeile['id']}/actions/entfernen")
    assert ohne_grund["success"] is False
    entfernt = _post(client, stamm, f"/crm/kunden-stamm/anschrift/{zeile['id']}/actions/entfernen",
                     _auditReason="Anschrift doppelt")
    assert entfernt["success"] is True, entfernt
    assert _anschriften(stamm) == []


def test_rabatt_mit_ungueltigem_prozentsatz_abgelehnt(client, stamm):
    antwort = _post(client, stamm, f"/crm/customers/{stamm['kunde']}/actions/rabatt_anlegen",
                    article_number="SAAT-1", discount_percent="viel")
    assert antwort["success"] is False


def test_fremder_mandant_sieht_die_zeile_nicht(client, stamm):
    _post(client, stamm, f"/crm/customers/{stamm['kunde']}/actions/ansprechpartner_anlegen",
          first_name="Jan", last_name="Jansen")
    fremd = str(uuid.uuid4())
    antwort = _post(client, stamm, f"/crm/customers/{stamm['kunde']}/actions/ansprechpartner_anlegen",
                    mandant=fremd, first_name="X", last_name="Y")
    assert antwort.get("success") is not True


def test_pflegeaktionen_nur_in_der_kundenakte():
    """Die Partnerstamm-Pflege gehoert genau einer Maske. Ein Ersetzen ohne Anzahl haengte sie am 09.11.2026 an
    zwoelf Builder (Auftrag, Lieferschein ...): dort fehlte danach "edit" und es erschienen Kundenstamm-Aktionen."""
    from app.core.screen_definitions import SCREEN_DEFINITION_BUILDERS, get_screen_definition

    traeger = set()
    for sid in list(SCREEN_DEFINITION_BUILDERS):
        definition = get_screen_definition(sid)
        wege = [a.get("commandEndpoint") or "" for a in definition.get("actions") or []]
        wege += [r.get("commandEndpoint") or "" for t in definition.get("tabs") or []
                 for tab in (t.get("tables") or []) for r in (tab.get("rowActions") or [])]
        if any("/crm/kunden-stamm/" in w or w.endswith("/actions/anschrift_anlegen") for w in wege):
            traeger.add(sid)
    from app.core.native_screen_aliases import NATIVE_SCREEN_ALIASES

    akte = {"crm/customer-360"} | {alias for alias, ziel in NATIVE_SCREEN_ALIASES.items() if ziel == "crm/customer-360"}
    assert traeger == akte
