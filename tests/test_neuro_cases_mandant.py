"""Freigabefaelle (/neuro/cases): nur der eigene Mandant, Entscheider aus dem Token (20.10.2026).

Vorher lieferten Abruf, Zuweisen, Entscheiden, Eskalieren und Schliessen jeden Fall jeder Kennung, der
Entscheider stand frei im Body (``decided_by``), und ``escalate-overdue`` eskalierte die Faelle aller Mandanten.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from app.api.v1.endpoints import case_management_api
from app.services import case_management
from testgrenze import ALLE_FACHROLLEN, ersetze_bearer, ersetze_mandant, ersetze_nutzer

app = FastAPI()
app.include_router(case_management_api.router, prefix="/api/v1")
ersetze_bearer(app, *ALLE_FACHROLLEN)
ersetze_mandant(app)
ersetze_nutzer(app, *ALLE_FACHROLLEN)
client = TestClient(app, raise_server_exceptions=False)


def fall(tenant: str, ueberfaellig: bool = False) -> str:
    case = case_management.ApprovalCase(
        priority=case_management.CasePriority.MEDIUM, aktions_typ="buchung", instanz_id="I-1", agent_id="agent",
        risiko_stufe="MITTEL", begruendung="Pruefen", freigabe_rolle="controller", context={},
        due_at=(datetime.now(timezone.utc) + timedelta(hours=-1 if ueberfaellig else 24)).isoformat(),
        tenant_id=tenant,
    )
    case_management._CASE_STORE[case.case_id] = case
    return case.case_id


def test_fremde_faelle_sind_nicht_sichtbar_und_nicht_entscheidbar():
    fremd = fall("haus-b")
    kopf = {"X-Tenant-ID": "haus-a"}
    assert client.get(f"/api/v1/neuro/cases/{fremd}", headers=kopf).status_code == 404
    antwort = client.post(f"/api/v1/neuro/cases/{fremd}/decide", headers=kopf,
                          json={"decision": "GENEHMIGT", "decided_by": "jemand"})
    assert antwort.status_code == 404
    assert case_management._CASE_STORE[fremd].status == case_management.CaseStatus.OPEN


def test_entscheider_kommt_aus_dem_token_nicht_aus_dem_body(monkeypatch):
    eigen = fall("haus-a")
    monkeypatch.setattr(case_management_api, "gepruefter_akteur_aus_request", lambda request: "token-nutzer")
    antwort = client.post(f"/api/v1/neuro/cases/{eigen}/decide", headers={"X-Tenant-ID": "haus-a"},
                          json={"decision": "GENEHMIGT", "decided_by": "im-body-behauptet"})
    assert antwort.status_code == 200, antwort.text
    assert case_management._CASE_STORE[eigen].decided_by == "token-nutzer"


def test_eskalation_nur_fuer_den_eigenen_mandanten():
    eigen, fremd = fall("haus-a", ueberfaellig=True), fall("haus-b", ueberfaellig=True)
    antwort = client.post("/api/v1/neuro/cases/escalate-overdue", headers={"X-Tenant-ID": "haus-a"})
    assert antwort.status_code == 200, antwort.text
    assert case_management._CASE_STORE[eigen].status == case_management.CaseStatus.ESCALATED
    assert case_management._CASE_STORE[fremd].status == case_management.CaseStatus.OPEN
