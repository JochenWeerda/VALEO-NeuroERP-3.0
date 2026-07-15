from __future__ import annotations

from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints import feeding_feed_analyses
from app.auth.deps import get_current_user
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.main import app


BASE = "/api/v1/agrar/rations-optimization"
TENANT = "00000000-0000-0000-0000-000000000001"
HEADERS = {"Authorization": "Bearer dev-token", "X-Tenant-Id": TENANT}
client = TestClient(app, raise_server_exceptions=False)


def _feed(suffix: str) -> str:
    response = client.post(f"{BASE}/feed-catalog/feeds", headers=HEADERS, json={
        "artikel_nummer": f"ANA-{suffix}", "name": f"Analysenfutter {suffix}",
        "art": "Grundfutter", "feed_kind": "forage", "approval_status": "approved",
        "trockensubstanz": "35",
    })
    assert response.status_code == 201, response.text
    return response.json()["id"]


def _analysis(feed_id: str, suffix: str) -> dict:
    response = client.post(f"{BASE}/feed-analyses", headers=HEADERS, json={
        "feed_id": feed_id, "bezeichnung": f"Maissilage Probe {suffix}",
        "probe_nr": f"P-{suffix}", "labor": "Testlabor", "method": "VDLUFA",
        "status": "draft", "values": [
            {"nutrient_code": "dry_matter", "original_value": "35",
             "original_unit_code": "percent", "canonical_unit_code": "g_per_kg",
             "basis": "fresh_matter", "value_status": "measured"},
            {"nutrient_code": "crude_protein", "original_value": "8.1",
             "original_unit_code": "percent", "canonical_unit_code": "g_per_kg",
             "basis": "dry_matter", "value_status": "measured"},
            {"nutrient_code": "metabolizable_energy", "original_value": "10.7",
             "original_unit_code": "MJ_per_kg", "canonical_unit_code": "MJ_per_kg",
             "basis": "dry_matter", "value_status": "estimated"},
        ],
    })
    assert response.status_code == 201, response.text
    return response.json()


def test_feed_analysis_full_release_replacement_history_and_tenant_isolation() -> None:
    suffix = str(uuid4())[:8]
    feed_id = _feed(suffix)
    first = _analysis(feed_id, suffix)
    assert first["revision"] == 1
    assert first["values"][2]["estimated"] is True

    validated = client.post(f"{BASE}/feed-analyses/{first['id']}/validate", headers=HEADERS,
                            json={"expected_revision": 1})
    assert validated.status_code == 200, validated.text
    assert validated.json()["status"] == "validated"
    assert not validated.json()["findings"]

    released = client.post(f"{BASE}/feed-analyses/{first['id']}/transition", headers=HEADERS, json={
        "target_status": "released", "expected_revision": 2, "reason": "Laborbefund fachlich freigegeben",
    })
    assert released.status_code == 200, released.text
    assert released.json()["is_active"] is True
    assert released.json()["original_document_id"] is None

    second = _analysis(feed_id, f"{suffix}-2")
    second_valid = client.post(f"{BASE}/feed-analyses/{second['id']}/validate", headers=HEADERS,
                               json={"expected_revision": 1})
    assert second_valid.status_code == 200, second_valid.text
    preview = client.post(f"{BASE}/feed-analyses/{second['id']}/actions/release", headers=HEADERS,
                          json={"_mode": "dryRun", "_auditReason": "Aktuellere Probe freigeben"})
    assert preview.status_code == 200, preview.text
    assert preview.json()["proposedChanges"][0]["after"] == "released"
    assert client.get(f"{BASE}/feed-analyses/{second['id']}", headers=HEADERS).json()["status"] == "validated"
    second_release = client.post(f"{BASE}/feed-analyses/{second['id']}/actions/release", headers=HEADERS, json={
        "_mode": "execute", "_auditReason": "Aktuellere Probe freigegeben",
    })
    assert second_release.status_code == 200, second_release.text
    assert client.get(f"{BASE}/feed-analyses/{first['id']}", headers=HEADERS).json()["status"] == "superseded"

    history = client.get(f"{BASE}/feed-analyses/{second['id']}/history", headers=HEADERS)
    assert history.status_code == 200
    assert [row["revision"] for row in history.json()] == [3, 2, 1]

    stale = client.post(f"{BASE}/feed-analyses/{second['id']}/validate", headers=HEADERS,
                        json={"expected_revision": 1})
    assert stale.status_code == 409
    foreign = client.get(f"{BASE}/feed-analyses/{second['id']}", headers={
        "Authorization": "Bearer dev-token", "X-Tenant-Id": str(uuid4()),
    })
    assert foreign.status_code == 404


def test_feed_analysis_enforces_read_write_and_approval_roles() -> None:
    local = FastAPI()
    local.include_router(feeding_feed_analyses.router)
    local.dependency_overrides[get_tenant_id] = lambda: TENANT
    local.dependency_overrides[get_db] = lambda: object()

    local.dependency_overrides[get_current_user] = lambda: {"sub": "reader", "roles": ["FUTTERMITTEL_LESEN"]}
    with TestClient(local, raise_server_exceptions=False) as local_client:
        assert local_client.post("/feed-analyses", json={"bezeichnung": "X"}).status_code == 403
        assert local_client.post("/feed-analyses/a/transition", json={
            "target_status": "released", "expected_revision": 1, "reason": "Freigabe Test",
        }).status_code == 403

    local.dependency_overrides[get_current_user] = lambda: {
        "sub": "editor", "roles": ["FUTTERMITTEL_BEARBEITEN"],
    }
    with TestClient(local, raise_server_exceptions=False) as local_client:
        assert local_client.post("/feed-analyses/a/transition", json={
            "target_status": "released", "expected_revision": 1, "reason": "Freigabe Test",
        }).status_code == 403


def test_import_preview_requires_revisionssicher_document_before_release() -> None:
    suffix = str(uuid4())[:8]
    feed_id = _feed(f"imp-{suffix}")
    content = (
        "Bezeichnung;Probe-Nr;Probenart;Trockensubstanz;Rohprotein;ME GfE 2023\n"
        f"Importprobe {suffix};IMP-{suffix};Grassilage;35,0;15,2;10,7\n"
    ).encode("utf-8")
    preview = client.post(f"{BASE}/feed-analyses/import-preview", headers=HEADERS,
                          files={"file": ("labor.csv", content, "text/csv")})
    assert preview.status_code == 200, preview.text
    parsed = preview.json()
    assert parsed["quarantine_status"] == "preview_only"
    assert len(parsed["sha256"]) == 64
    assert {item["nutrient_code"] for item in parsed["values"]} >= {"dry_matter", "crude_protein"}

    created = client.post(f"{BASE}/feed-analyses", headers=HEADERS, json={
        "feed_id": feed_id, **parsed["analysis"], "original_sha256": parsed["sha256"],
        "status": "draft", "values": parsed["values"],
    })
    assert created.status_code == 201, created.text
    analysis_id = created.json()["id"]
    validated = client.post(f"{BASE}/feed-analyses/{analysis_id}/validate", headers=HEADERS,
                            json={"expected_revision": 1})
    assert validated.status_code == 200, validated.text
    assert {finding["code"] for finding in validated.json()["findings"]} == {
        "original-document-not-archived",
    }
    blocked = client.post(f"{BASE}/feed-analyses/{analysis_id}/transition", headers=HEADERS, json={
        "target_status": "released", "expected_revision": 2, "reason": "Import fachlich freigeben",
    })
    assert blocked.status_code == 409

    attached = client.post(f"{BASE}/feed-analyses/{analysis_id}/document-reference", headers=HEADERS, json={
        "document_id": f"DMS-{suffix}", "sha256": parsed["sha256"], "expected_revision": 2,
    })
    assert attached.status_code == 200, attached.text
    revalidated = client.post(f"{BASE}/feed-analyses/{analysis_id}/validate", headers=HEADERS,
                              json={"expected_revision": 3})
    assert revalidated.status_code == 200, revalidated.text
    assert revalidated.json()["findings"] == []
    released = client.post(f"{BASE}/feed-analyses/{analysis_id}/transition", headers=HEADERS, json={
        "target_status": "released", "expected_revision": 4, "reason": "DMS-Beleg und Werte geprueft",
    })
    assert released.status_code == 200, released.text


def test_legacy_ground_feed_api_cannot_bypass_revision_and_rejection_history() -> None:
    suffix = str(uuid4())[:8]
    legacy_headers = {"X-Tenant-Id": TENANT, "Authorization": "Bearer dev-token"}
    created = client.post("/api/v1/agrar/grundfutter-analysen", headers=legacy_headers, json={
        "bezeichnung": f"Legacy Probe {suffix}", "probe_nr": f"LEG-{suffix}",
        "trockensubstanz_os": 35, "rohprotein_ts": 15.2,
    })
    assert created.status_code == 201, created.text
    analysis_id = created.json()["id"]
    canonical = client.get(f"{BASE}/feed-analyses/{analysis_id}", headers=HEADERS)
    assert canonical.status_code == 200, canonical.text
    assert canonical.json()["revision"] == 1

    verified = client.patch(f"/api/v1/agrar/grundfutter-analysen/{analysis_id}", headers=legacy_headers,
                            json={"verifiziert": True, "notizen": "Fachlich geprueft"})
    assert verified.status_code == 200, verified.text
    assert client.get(f"{BASE}/feed-analyses/{analysis_id}", headers=HEADERS).json()["status"] == "validated"
    history = client.get(f"{BASE}/feed-analyses/{analysis_id}/history", headers=HEADERS).json()
    assert [row["revision"] for row in history] == [2, 1]

    deleted = client.delete(f"/api/v1/agrar/grundfutter-analysen/{analysis_id}", headers=legacy_headers)
    assert deleted.status_code == 204, deleted.text
    retained = client.get(f"{BASE}/feed-analyses/{analysis_id}", headers=HEADERS)
    assert retained.status_code == 200
    assert retained.json()["status"] == "rejected"
