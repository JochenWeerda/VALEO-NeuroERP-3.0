"""Betriebsprofile aus crm-core nur fuer den eigenen Mandanten (21.10.2026).

crm-core fuehrt den Mandanten am Betriebsprofil; der Proxy ``app/api/v1/endpoints/farm_profiles.py`` wertete ihn nicht
aus — Liste, Abruf, Aendern, Loeschen und Unterlisten (Kulturen, Tierbestand, Zertifikate) reichten Profile aller
Mandanten durch.
"""
from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints import farm_profiles
from app.integrations.crm_core_client import CRMCoreFarmProfile
from testgrenze import ersetze_mandant, ersetze_nutzer

EIGEN, FREMD = "11111111-1111-4111-8111-111111111111", "22222222-2222-4222-8222-222222222222"
A1, B1 = "a1a1a1a1-0000-4000-8000-00000000000a", "b1b1b1b1-0000-4000-8000-00000000000b"


def _profil(kennung: str, haus: str) -> CRMCoreFarmProfile:
    return CRMCoreFarmProfile(id=kennung, tenant_id=haus, farm_name="Hof", owner="Janssen", total_area=120.0,
                              crops=[{"crop": "Weizen", "area": 40.0}], livestock=[], certifications=[], location=None,
                              notes="", created_at="2026-10-21T08:00:00",
                              updated_at="2026-10-21T08:00:00")


@pytest.fixture()
def client():
    app = FastAPI()
    app.include_router(farm_profiles.router, prefix="/api/v1/crm/farm-profiles")
    ersetze_mandant(app, EIGEN)
    ersetze_nutzer(app, "CRM_BEARBEITEN")
    return TestClient(app)


def test_liste_zeigt_nur_eigene(client):
    daten = ([_profil(A1, EIGEN), _profil(B1, FREMD)], 2)
    with patch.object(farm_profiles.crm_core_client, "list_farm_profiles", AsyncMock(return_value=daten)):
        antwort = client.get("/api/v1/crm/farm-profiles/")
    assert antwort.status_code == 200, antwort.text
    assert [z["id"] for z in antwort.json()["items"]] == [A1] and antwort.json()["total"] == 1


@pytest.mark.parametrize("methode,pfad", [("get", ""), ("put", ""), ("delete", ""), ("get", "/crops"),
                                          ("get", "/certifications")])
def test_fremdes_profil_ist_nicht_gefunden(client, methode, pfad):
    aendern, loeschen = AsyncMock(), AsyncMock()
    with patch.object(farm_profiles.crm_core_client, "get_farm_profile", AsyncMock(return_value=_profil(B1, FREMD))), \
         patch.object(farm_profiles.crm_core_client, "update_farm_profile", aendern), \
         patch.object(farm_profiles.crm_core_client, "delete_farm_profile", loeschen):
        kwargs = {"json": {"farm_name": "Uebernahme"}} if methode == "put" else {}
        antwort = getattr(client, methode)(f"/api/v1/crm/farm-profiles/{B1}{pfad}", **kwargs)
    assert antwort.status_code == 404
    aendern.assert_not_awaited()
    loeschen.assert_not_awaited()


def test_eigenes_profil_wird_geliefert(client):
    with patch.object(farm_profiles.crm_core_client, "get_farm_profile", AsyncMock(return_value=_profil(A1, EIGEN))):
        assert client.get(f"/api/v1/crm/farm-profiles/{A1}").status_code == 200
