"""
DLG-merged tenant: optional dataset loaded from dlg_merged_feeds_lp.csv.

This is opt-in via env var so default tests remain stable.
"""

import pytest


def test_get_feeds_dlg_tenant_contains_weizen(client_dlg_tenant):
    r = client_dlg_tenant.get("/api/v1/feeds")
    assert r.status_code == 200
    ids = {x["id"] for x in r.json()}
    assert "weizen" in ids


def test_demo_optimization_dlg_tenant_supplements_forage(client_dlg_tenant):
    """Demo nutzt alle DLG-Mittel: ohne Raufutter im Mandanten → Ergänzung aus default (sonst nur optimal)."""
    r_list = client_dlg_tenant.get("/api/v1/feeds")
    assert r_list.status_code == 200
    dlg_feeds = r_list.json()
    tenant_has_forage = any(x.get("group") == "forage" for x in dlg_feeds)

    r = client_dlg_tenant.post("/api/v1/optimize/demo")
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["status"] == "optimal"
    assert data["metadata"].get("tenant_id") == "dlg"
    if not tenant_has_forage:
        assert data["metadata"].get("forage_supplement_from_default_tenant") is True
        assert data["metadata"].get("supplement_tenant_id") == "default"
        assert any("Grundfutter" in w or "Raufutter" in w for w in data.get("warnings", []))
    else:
        assert data["metadata"].get("forage_supplement_from_default_tenant") is not True
    feed_ids = {item["feed_id"] for item in data["ration_items"]}
    assert "weizen" in feed_ids or "grassilage" in feed_ids or "maissilage" in feed_ids


def test_optimize_dlg_tenant_supplements_forage_from_request_feeds(client_dlg_tenant):
    """POST /optimize mit Korb ohne FORAGE: Raufutter aus default (unabhängig vom vollen DLG-Katalog)."""
    r_feeds = client_dlg_tenant.get("/api/v1/feeds")
    assert r_feeds.status_code == 200
    feeds = [f for f in r_feeds.json() if f.get("group") != "forage"]
    if not feeds:
        pytest.skip("DLG-Katalog ohne Nicht-Raufutter — Ergänzungspfad nicht testbar")

    request = {
        "cow_profile": {
            "breed": "Holstein",
            "body_weight_kg": 650,
            "milk_kg_day": 35,
            "milk_fat_pct": 3.8,
            "milk_protein_pct": 3.2,
            "lactation_stage_days": 150,
            "parity": 2,
            "target_dmi_kg": 22.0,
        },
        "requirements": {
            "dmi_kg": 22.0,
            "me_min_mj": 220.0,
            "sidp_min_g": 3200,
            "andfom_min_g": 5500,
            "andfom_max_g": 7500,
            "starch_max_g": 4000,
            "sugar_max_g": 1000,
            "fat_max_g": 1200,
            "ca_min_g": 100,
            "p_min_g": 60,
            "na_min_g": 8,
            "forage_share_min": 0.4,
        },
        "feeds": feeds,
    }
    r = client_dlg_tenant.post("/api/v1/optimize", json=request)
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["status"] == "optimal"
    assert data["metadata"].get("forage_supplement_from_default_tenant") is True
    assert data["metadata"].get("supplement_tenant_id") == "default"
    assert any("Raufutter" in w or "Grundfutter" in w for w in data.get("warnings", []))
