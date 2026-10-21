"""CRM-Aktivitaeten aus crm-core nur fuer den eigenen Mandanten (21.10.2026).

crm-core fuehrt den Mandanten an der Aktivitaet; der Proxy ``app/api/v1/endpoints/activities.py`` wertete ihn nicht
aus. Produktiv beschattet er fuer ``/api/v1/crm/activities/{id}`` die mandantengebundenen Wege von ``app.crm.router``:
Abruf, Aendern und Loeschen fremder Aktivitaeten waren moeglich, die Anlage trug den Standardmandanten ein.
"""
from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints import activities
from app.integrations.crm_core_client import CRMCoreActivity
from testgrenze import ersetze_mandant, ersetze_nutzer

# Das Ausgabeschema fuehrt Kennung und Mandant als UUID.
EIGEN, FREMD = "11111111-1111-4111-8111-111111111111", "22222222-2222-4222-8222-222222222222"
A1, B1, N1 = ("a1a1a1a1-0000-4000-8000-00000000000a", "b1b1b1b1-0000-4000-8000-00000000000b",
              "c1c1c1c1-0000-4000-8000-00000000000c")


def _aktivitaet(kennung: str, haus: str) -> CRMCoreActivity:
    return CRMCoreActivity(id=kennung, tenant_id=haus, type="call", title=f"Anruf {kennung}", status="planned",
                           scheduled_at="2026-10-21T09:00:00", created_at="2026-10-21T08:00:00",
                           updated_at="2026-10-21T08:00:00")


@pytest.fixture()
def client():
    app = FastAPI()
    app.include_router(activities.router, prefix="/api/v1/crm/activities")
    ersetze_mandant(app, EIGEN)
    ersetze_nutzer(app, "CRM_BEARBEITEN")
    return TestClient(app)


def test_liste_zeigt_nur_eigene(client):
    daten = ([_aktivitaet(A1, EIGEN), _aktivitaet(B1, FREMD)], 2)
    with patch.object(activities.crm_core_client, "list_activities", AsyncMock(return_value=daten)):
        antwort = client.get("/api/v1/crm/activities/")
    assert antwort.status_code == 200, antwort.text
    assert [z["id"] for z in antwort.json()["items"]] == [A1]
    assert antwort.json()["total"] == 1


@pytest.mark.parametrize("methode", ["get", "put", "delete"])
def test_fremde_aktivitaet_ist_nicht_gefunden(client, methode):
    aendern, loeschen = AsyncMock(), AsyncMock()
    with patch.object(activities.crm_core_client, "get_activity", AsyncMock(return_value=_aktivitaet(B1, FREMD))), \
         patch.object(activities.crm_core_client, "update_activity", aendern), \
         patch.object(activities.crm_core_client, "delete_activity", loeschen):
        kwargs = {"json": {"title": "Uebernahme"}} if methode == "put" else {}
        antwort = getattr(client, methode)(f"/api/v1/crm/activities/{B1}", **kwargs)
    assert antwort.status_code == 404
    aendern.assert_not_awaited()
    loeschen.assert_not_awaited()


def test_unterlisten_fremder_aktivitaeten_sind_nicht_gefunden(client):
    with patch.object(activities.crm_core_client, "get_activity", AsyncMock(return_value=_aktivitaet(B1, FREMD))):
        assert client.get(f"/api/v1/crm/activities/{B1}/main-topics").status_code == 404


def test_anlage_traegt_den_kontextmandanten_ein(client):
    anlegen = AsyncMock(return_value=_aktivitaet(N1, EIGEN))
    with patch.object(activities.crm_core_client, "create_activity", anlegen):
        antwort = client.post("/api/v1/crm/activities/", json={
            "type": "call", "title": "Rueckruf", "customer": "Hof", "contact_person": "Jan",
            "date": "2026-10-21T09:00:00", "status": "planned", "assigned_to": "vertrieb"})
    assert antwort.status_code == 201, antwort.text
    assert anlegen.await_args.args[0]["tenant_id"] == EIGEN
