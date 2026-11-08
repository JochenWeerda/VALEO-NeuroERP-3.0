"""Service-Faelle nur fuer den eigenen Mandanten, Eskalierender aus dem Token (21.10.2026).

Vorher lasen und aenderten Abruf, Aendern, Loeschen, Eskalieren und SLA-Status Faelle aller Mandanten; der
Eskalierende kam aus einem frei setzbaren Anfrageparameter; Liste und Dashboard filterten nur auf Wunsch.
"""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints import cases
from app.core.database import get_db
from testgrenze import ersetze_mandant, ersetze_nutzer

EIGEN, FREMD = "haus-a", "haus-b"


def _fall(kennung: str, haus: str) -> dict:
    return {"id": kennung, "case_number": "C-1", "tenant_id": haus, "subject": "Reklamation", "description": "Bruch",
            "status": "open",
            "priority": "MEDIUM", "created_at": "2026-10-21T08:00:00", "updated_at": "2026-10-21T08:00:00"}


@pytest.fixture()
def umgebung():
    app = FastAPI()
    app.include_router(cases.router, prefix="/api/v1/crm/cases")
    db = MagicMock()
    db.execute.return_value.fetchone.return_value = None  # kein lokaler Fall
    db.execute.return_value.fetchall.return_value = []
    app.dependency_overrides[get_db] = lambda: db
    ersetze_mandant(app, EIGEN)
    ersetze_nutzer(app, "CRM_BEARBEITEN")
    return TestClient(app), db


@pytest.mark.parametrize("methode,pfad", [("get", ""), ("put", ""), ("delete", ""), ("get", "/sla-status")])
def test_fremder_fall_ist_nicht_gefunden(umgebung, methode, pfad):
    client, _ = umgebung
    aendern, loeschen = AsyncMock(), AsyncMock()
    with patch.object(cases, "crm_get_case", AsyncMock(return_value=_fall("f1", FREMD))), \
         patch.object(cases, "crm_update_case", aendern), patch.object(cases, "crm_delete_case", loeschen):
        kwargs = {"json": {"status": "closed"}} if methode == "put" else {}
        antwort = getattr(client, methode)(f"/api/v1/crm/cases/f1{pfad}", **kwargs)
    assert antwort.status_code == 404
    aendern.assert_not_awaited()
    loeschen.assert_not_awaited()


def test_eskalation_fremder_faelle_nein_eskalierender_aus_dem_token(umgebung):
    client, db = umgebung
    eskalieren = AsyncMock(return_value={"case_id": "e1", "escalated": True})
    with patch.object(cases, "crm_get_case", AsyncMock(return_value=_fall("f1", FREMD))), \
         patch.object(cases, "crm_escalate_case", eskalieren):
        assert client.post("/api/v1/crm/cases/f1/escalate?reason=dringend&escalated_by=chef").status_code == 404
    eskalieren.assert_not_awaited()
    with patch.object(cases, "crm_get_case", AsyncMock(return_value=_fall("e1", EIGEN))), \
         patch.object(cases, "crm_escalate_case", eskalieren):
        assert client.post("/api/v1/crm/cases/e1/escalate?reason=dringend&escalated_by=chef").status_code == 200
    # Der Anfrageparameter zaehlt nicht mehr; eskaliert hat die gepruefte Person.
    assert eskalieren.await_args.args[2] == "5f0c2a9e"
    lokale_suche = db.execute.call_args_list[0]
    assert "tenant_id = :tid" in str(lokale_suche.args[0]) and lokale_suche.args[1]["tid"] == EIGEN


def test_liste_und_anlage_nutzen_den_kontextmandanten(umgebung):
    client, _ = umgebung
    auflisten = AsyncMock(return_value=([], 0))
    anlegen = AsyncMock(return_value=_fall("c1c1c1c1-0000-4000-8000-00000000000c", EIGEN))
    with patch.object(cases, "crm_list_cases", auflisten), patch.object(cases, "crm_create_case", anlegen):
        assert client.get("/api/v1/crm/cases/?tenant_id=").status_code == 200
        angelegt = client.post("/api/v1/crm/cases/", json={"subject": "Reklamation", "description": "Bruch",
                                                           "tenant_id": EIGEN})
    assert auflisten.await_args.kwargs["tenant_id"] == EIGEN
    assert angelegt.status_code == 201, angelegt.text
    assert anlegen.await_args.args[0]["tenant_id"] == EIGEN
