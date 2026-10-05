from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app, raise_server_exceptions=False)
BASE = "/api/v1/agrar/rations-optimization"
TENANT = "00000000-0000-0000-0000-000000000001"
HEADERS = {"Authorization": "Bearer dev-token", "X-Tenant-Id": TENANT}


def _business() -> dict:
    response = client.post(f"{BASE}/feeding/businesses", headers=HEADERS, json={"name": f"Vorlagenbetrieb {uuid4()}"})
    assert response.status_code == 201, response.text
    return response.json()


def _group(business_id: str, name: str) -> dict:
    response = client.post(f"{BASE}/lifecycle/groups", headers=HEADERS, json={
        "external_ref": f"template-{uuid4()}", "name": name, "animal_count": 42, "business_id": business_id,
    })
    assert response.status_code == 201, response.text
    return response.json()


def _ration(group_id: str, name: str, feed_id: str) -> dict:
    response = client.post(f"{BASE}/lifecycle/rations", headers=HEADERS, json={
        "group_id": group_id, "name": name, "source": "editor", "comment": "Ausgangsversion",
        "snapshot": {"ration": [{"feed_id": feed_id, "kg_fm": 12.5}], "readiness": {"status": "ready", "blocker_count": 0}},
    })
    assert response.status_code == 201, response.text
    return response.json()


def test_template_create_list_apply_and_business_file() -> None:
    business = _business()
    group = _group(business["id"], "Frischmelker")
    source = _ration(group["id"], "Quelle", "mais")
    target = _ration(group["id"], "Ziel", "gras")
    source_version = source["versions"][0]

    created = client.post(f"{BASE}/feeding/ration-templates", headers=HEADERS, json={
        "name": "  Sommer   Frischmelker ", "description": "Freigegebene Ausgangsbasis",
        "source_ration_version_id": source_version["id"],
    })
    assert created.status_code == 201, created.text
    template = created.json()
    assert template["name"] == "Sommer Frischmelker"
    assert template["source_ration_version_id"] == source_version["id"]

    listed = client.get(f"{BASE}/feeding/businesses/{business['id']}/ration-templates", headers=HEADERS)
    assert listed.status_code == 200
    assert any(item["id"] == template["id"] for item in listed.json())

    applied = client.post(f"{BASE}/feeding/ration-templates/{template['id']}/apply", headers=HEADERS, json={
        "target_ration_id": target["id"], "expected_latest_version_no": 1,
        "reason": "Neue Beratung auf Vorlagenbasis",
    })
    assert applied.status_code == 201, applied.text
    copy = applied.json()
    assert copy["version_no"] == 2
    assert copy["source"] == "template"
    assert copy["based_on_version_id"] == source_version["id"]

    detail = client.get(f"{BASE}/lifecycle/rations/{target['id']}", headers=HEADERS).json()
    assert detail["versions"][0]["snapshot"]["ration"][0]["feed_id"] == "mais"
    overview = client.get(f"{BASE}/feeding/businesses/{business['id']}/overview", headers=HEADERS)
    assert overview.status_code == 200, overview.text
    assert overview.json()["group_count"] == 1
    assert overview.json()["ration_count"] == 2
    assert overview.json()["template_count"] == 1
    assert overview.json()["data_status"] == "available"


def test_template_rejects_cross_group_copy_and_stale_version() -> None:
    business = _business()
    first_group = _group(business["id"], "Gruppe A")
    second_group = _group(business["id"], "Gruppe B")
    source = _ration(first_group["id"], "Quelle", "mais")
    other = _ration(second_group["id"], "Fremdes Ziel", "gras")
    created = client.post(f"{BASE}/feeding/ration-templates", headers=HEADERS, json={
        "name": f"Grenze {uuid4()}", "source_ration_version_id": source["versions"][0]["id"],
    }).json()
    cross_group = client.post(f"{BASE}/feeding/ration-templates/{created['id']}/apply", headers=HEADERS, json={
        "target_ration_id": other["id"], "expected_latest_version_no": 1,
        "reason": "Nicht erlaubter Gruppenwechsel",
    })
    assert cross_group.status_code == 409
    assert "derselben Fuetterungsgruppe" in cross_group.json()["detail"]


def test_template_endpoints_enforce_roles() -> None:
    denied = client.get(
        f"{BASE}/feeding/businesses/unknown/ration-templates",
        headers={"Authorization": "Bearer dev-token-no-roles", "X-Tenant-Id": TENANT},
    )
    assert denied.status_code in {401, 403}
