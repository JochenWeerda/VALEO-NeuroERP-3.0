from datetime import date
from uuid import uuid4
from fastapi.testclient import TestClient
from app.agrar.rations.controlling import deviation, energy_corrected_milk, nitrogen_efficiency
from app.main import app

client = TestClient(app, raise_server_exceptions=False)
ROOT = "/api/v1/agrar/rations-optimization"
TENANT = "00000000-0000-0000-0000-000000000001"
HEADERS = {"Authorization": "Bearer dev-token", "X-Tenant-Id": TENANT}

def test_controlling_calculations_keep_missing_values_unknown() -> None:
    assert energy_corrected_milk(35, 4.0, 3.4) == 35.043
    assert energy_corrected_milk(35, None, 3.4) is None
    assert nitrogen_efficiency(35, 3.4, 0.42) == 44.41
    assert deviation(None, 23) is None
    assert deviation(22.4, 23) == -0.6

def test_daily_observation_is_idempotent_tenant_isolated_and_has_variances() -> None:
    suffix = str(uuid4())[:8]
    group = client.post(f"{ROOT}/lifecycle/groups", headers=HEADERS, json={
        "external_ref": f"ctrl-{suffix}", "name": f"Controlling {suffix}", "animal_count": 50, "feeding_system": "TMR"
    })
    assert group.status_code == 201, group.text
    group_id = group.json()["id"]
    ration = client.post(f"{ROOT}/lifecycle/rations", headers=HEADERS, json={
        "group_id": group_id, "name": f"Ctrl ration {suffix}", "source": "solver",
        "snapshot": {"wizard": {"milkYield": 36}, "optimization_result": {"total_dm_kg": 23, "total_cost_eur_day": 4.8}}
    })
    assert ration.status_code == 201, ration.text
    version = ration.json()["latest_version_id"]
    for current, target in (("draft", "in_review"), ("in_review", "approved"), ("approved", "active")):
        transition = client.post(f"{ROOT}/lifecycle/versions/{version}/transitions", headers=HEADERS,
            json={"expected_status": current, "target_status": target, "reason": "Controlling-Test"})
        assert transition.status_code == 200, transition.text
    body = {"group_id": group_id, "observation_date": date.today().isoformat(), "source": "manual",
        "source_ref": "stable-day", "cow_count": 50, "actual_dmi_kg_cow": 22.4,
        "actual_cost_eur_cow": 4.95, "actual_milk_kg_cow": 35, "actual_fat_pct": 4.0,
        "actual_protein_pct": 3.4, "feed_n_kg_cow": 0.42}
    first = client.post(f"{ROOT}/controlling/observations", headers=HEADERS, json=body)
    assert first.status_code == 201, first.text
    second = client.post(f"{ROOT}/controlling/observations", headers=HEADERS, json={**body, "actual_dmi_kg_cow": 22.6})
    assert second.status_code == 201, second.text
    assert second.json()["id"] == first.json()["id"]
    assert second.json()["dmi_deviation_kg"] == -0.4
    assert second.json()["actual_ecm_kg_cow"] == 35.043
    series = client.get(f"{ROOT}/controlling/series?group_id={group_id}", headers=HEADERS)
    assert series.status_code == 200
    assert len(series.json()) == 1
    other = client.get(f"{ROOT}/controlling/series?group_id={group_id}", headers={**HEADERS, "X-Tenant-Id": str(uuid4())})
    assert other.status_code == 200 and other.json() == []
