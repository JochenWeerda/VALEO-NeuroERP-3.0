"""Antwortvertrag von ``POST /finance/mahnstufe/{rechnungsnr}/eskalieren`` ueber den einen Mahnweg (23.11.2026).

Die Eskalation erzeugt eine Mahnung (``FinanceDunningService.run_dunning``); die Stufen kommen dort als Zahl und
werden als Text ausgeliefert. Ist der Posten nicht mahnfaellig, antwortet der Weg 422 und schreibt nichts.
Der Mahnweg selbst ist gegen die echte Datenbank in tests/test_ein_mahnweg.py geprueft.
"""
from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints.finance_actions import router
from app.core.database import get_db
from app.services.finance_dunning_service import FinanceDunningService
from testgrenze import ersetze_mandant, ersetze_nutzer


def _client(db):
    app = FastAPI()
    ersetze_mandant(app)
    ersetze_nutzer(app, "FINANCE_BEARBEITEN")
    app.include_router(router, prefix="/finance")
    app.dependency_overrides[get_db] = lambda: db
    return TestClient(app)


@pytest.mark.parametrize("vorher,stufe", [(0, "1"), (1, "2"), (2, "3")])
def test_eskalation_liefert_die_stufen_als_text(monkeypatch, vorher, stufe):
    monkeypatch.setattr(FinanceDunningService, "run_dunning", lambda self, **_: {
        "ok": True, "erzeugt": 1,
        "mahnungen": [{"id": "n-1", "stufe": int(stufe), "vorherige_stufe": vorher, "gebuehr": 5.0}]})
    with _client(MagicMock()) as client:
        antwort = client.post("/finance/mahnstufe/RE-CONTRACT/eskalieren", json={"operator": "contract-test"})
    assert antwort.status_code == 201, antwort.text
    assert antwort.json()["stufe"] == stufe
    assert antwort.json()["vorherige_stufe"] == (str(vorher) if vorher else None)
    assert antwort.json()["id"] == "n-1"


def test_nicht_mahnfaellig_wird_abgelehnt_ohne_schreibzugriff(monkeypatch):
    monkeypatch.setattr(FinanceDunningService, "run_dunning",
                        lambda self, **_: {"ok": True, "erzeugt": 0, "mahnungen": []})
    db = MagicMock()
    with _client(db) as client:
        antwort = client.post("/finance/mahnstufe/RE-CONTRACT/eskalieren", json={"operator": "test"})
    assert antwort.status_code == 422
    assert "nicht mahnfällig" in antwort.json()["detail"]
    db.commit.assert_not_called()
