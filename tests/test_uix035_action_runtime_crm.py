"""
UIX-035 / UIX-036 — ActionRuntime-Umschlag fuer CRM create_activity am Kunden.

Seit dem Migrationsstand 6ff9d93f4 sucht der Weg den Kunden in jedem Modus, lehnt einen unbekannten Kunden mit
404 und ungueltige Eingaben mit 422 ab und baut die Aktivitaet ueber den kanonischen Aktivitaetsdienst. Hier geht
es nur um den Umschlag: welcher Modus was ausloest. Kundensuche und Aktivitaetsdienst sind ersetzt; das echte
Schreiben pruefen ``tests/test_crm_activity_canonical_sql.py`` und ``tests/test_crm360_kunde_wird_gefunden.py``.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints import crm_360
from app.core.exceptions import register_domain_exception_handlers
from app.services import crm_activity_service
from testgrenze import ersetze_mandant, ersetze_nutzer

MANDANT = "00000000-0000-0000-0000-000000000001"
BASE = "/crm/customers/cust-001/actions/create_activity"


@pytest.fixture
def lauf(monkeypatch):
    aufrufe: list[tuple[str, str]] = []
    bekannt = {"cust-001": {"id": "cust-001"}}
    monkeypatch.setattr(crm_360, "_kunde_finden", lambda _db, kunde, mandant: bekannt.get(kunde))

    def vorschau(_db, mandant, aktion, command, activity_id=None):
        aufrufe.append(("preview", mandant))
        return {"title": command.title, "type": command.type, "customer_id": command.customer_id}

    def ausfuehren(_db, mandant, aktion, command, activity_id=None):
        aufrufe.append(("execute", mandant))
        return {"activity_id": "act-1", "auditEntryId": "audit-1"}

    monkeypatch.setattr(crm_activity_service, "preview_activity", vorschau)
    monkeypatch.setattr(crm_activity_service, "execute_activity", ausfuehren)
    app = FastAPI()
    register_domain_exception_handlers(app)
    app.include_router(crm_360.router, prefix="/crm/customers")
    app.dependency_overrides[crm_360.get_db] = lambda: None
    ersetze_mandant(app, MANDANT)
    ersetze_nutzer(app, "CRM_BEARBEITEN")
    with TestClient(app, raise_server_exceptions=False) as client:
        yield client, aufrufe


@pytest.mark.parametrize("mode", ["validate", "dryRun", "propose"])
def test_vorschau_modi_schreiben_nicht(lauf, mode):
    client, aufrufe = lauf
    antwort = client.post(BASE, json={"betreff": "Test-Anruf", "typ": "Anruf", "_mode": mode})
    assert antwort.status_code == 200, antwort.text
    daten = antwort.json()
    assert (daten["mode"], daten["success"]) == (mode, True)
    assert daten["proposedChanges"] == [{"title": "Test-Anruf", "type": "call", "customer_id": "cust-001"}]
    assert aufrufe == [("preview", MANDANT)]


def test_execute_legt_ueber_den_aktivitaetsdienst_an(lauf):
    client, aufrufe = lauf
    antwort = client.post(BASE, json={"betreff": "Jahresgespraech", "typ": "Meeting", "_mode": "execute",
                                      "_auditReason": "Kundentermin Q4", "_idempotencyKey": "ikey-abc-123"})
    assert antwort.status_code == 200, antwort.text
    daten = antwort.json()
    assert (daten["success"], daten["affectedIds"], daten["auditEntryId"]) == (True, ["act-1"], "audit-1")
    assert aufrufe == [("execute", MANDANT)]


def test_unbekannter_kunde_wird_abgelehnt_und_nichts_simuliert(lauf):
    client, aufrufe = lauf
    for mode in ("validate", "execute"):
        antwort = client.post("/crm/customers/unbekannt/actions/create_activity",
                              json={"betreff": "X", "typ": "Anruf", "_mode": mode})
        assert antwort.status_code == 404, antwort.text
    assert aufrufe == []


@pytest.mark.parametrize("rumpf", [
    {"betreff": "OK", "typ": "NichtExistent", "_mode": "validate"},
    {"betreff": "OK", "typ": "Anruf", "_mode": "unbekannt"},
    {"betreff": "OK", "typ": "Anruf", "_mode": "validate", "fremdfeld": 1},
])
def test_ungueltige_eingaben_werden_abgelehnt(lauf, rumpf):
    client, aufrufe = lauf
    assert client.post(BASE, json=rumpf).status_code == 422
    assert aufrufe == []


def test_agent_kette_propose_dryrun_validate_fuehrt_nie_aus(lauf):
    """UIX-036: Der Agent geht propose -> dryRun -> validate, ohne execute."""
    client, aufrufe = lauf
    for mode in ("propose", "dryRun", "validate"):
        assert client.post(BASE, json={"betreff": "Besuch geplant", "typ": "Besuch", "_mode": mode}).json()["success"]
    assert [art for art, _ in aufrufe] == ["preview", "preview", "preview"]
