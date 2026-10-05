"""FEED-WIZ-051 (TDD-Red-Welle 1, Backend-Anteil):

(a) /feeds reicht die DLG-PRIMARYID und Nomenklatur als fachliche Nummern
    durch (Artikel-/Rationsnummern-Spalte im Wizard).
(b) optimize/from-profile normalisiert Katalog-custom_feeds (_source='catalog')
    auf das LP-Format — unvollstaendige Solver-Koeffizienten fuehren nicht zu
    einem 500 (042-Befund: KeyError 'bst').
Vor der Implementierung geschrieben.
"""
from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app as main_app

ROOT = "/api/v1/agrar/rations-optimization"
TENANT = "00000000-0000-0000-0000-000000000001"
HEADERS = {"Authorization": "Bearer dev-token", "X-Tenant-Id": TENANT}
client = TestClient(main_app, raise_server_exceptions=False)


def test_feeds_expose_dlg_primaryid_and_nomenklatur() -> None:
    response = client.get(f"{ROOT}/feeds", headers=HEADERS)
    assert response.status_code == 200, response.text
    feeds = response.json()
    dlg = [feed for feed in feeds if str(feed["id"]).startswith("dlg_")]
    assert len(dlg) >= 150, "DLG-Pool geladen"

    with_primaryid = [feed for feed in dlg if feed.get("dlg_primaryid")]
    assert len(with_primaryid) == len(dlg), \
        "jede DLG-Position traegt ihre PRIMARYID als fachliche Nummer"
    sample = next(feed for feed in dlg if feed["id"] == "dlg_10010010")
    assert sample["dlg_primaryid"] == "10010010"
    assert sample.get("nomenklatur"), "DLG-Nomenklatur wird durchgereicht"


def test_from_profile_normalizes_catalog_custom_feeds() -> None:
    # Katalog-solver_feed OHNE bst/st/zu/nfc/minerals — vor dem Fix: KeyError
    catalog_feed = {
        "_source": "catalog",
        "id": f"catalog-{uuid4().hex[:8]}",
        "name": "Katalog Energiefutter",
        "group": "Kraftfutter",
        "futterart": "concentrate",
        "forage": False,
        "dm_frac": 0.88,
        "price": 0.32,
        "me": 13.0,
        "cp": 150.0,
        "artikel_nummer": "KF-0815",
    }
    response = client.post(f"{ROOT}/optimize/from-profile", headers=HEADERS, json={
        "cow_profile": {"body_weight_kg": 650, "milk_kg_day": 30,
                        "milk_fat_pct": 4.0, "milk_protein_pct": 3.4,
                        "feeding_type": "TMR"},
        "custom_feeds": [catalog_feed],
    })
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload.get("status") in {"optimal", "infeasible"}, payload.get("status")
