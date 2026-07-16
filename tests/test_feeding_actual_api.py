from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
import json
from typing import Any
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

from app.api.v1.endpoints.feeding_actual import router
from app.auth.deps import get_current_user
from app.core.database import SessionLocal, get_db
from app.core.tenant import get_tenant_id
from app.main import app

BASE = "/api/v1/agrar/rations-optimization"
TENANT = "00000000-0000-0000-0000-000000000001"
HEADERS = {"Authorization": "Bearer dev-token", "X-Tenant-Id": TENANT}
client = TestClient(app, raise_server_exceptions=False)


def _plan() -> tuple[dict[str, Any], str]:
    suffix = uuid4().hex[:8]
    feed = client.post(
        f"{BASE}/feed-catalog/feeds",
        headers=HEADERS,
        json={
            "artikel_nummer": f"ACT-{suffix}",
            "name": f"Ist-Futter {suffix}",
            "art": "Grundfutter",
            "feed_kind": "forage",
            "approval_status": "approved",
        },
    )
    assert feed.status_code == 201, feed.text
    feed_id = feed.json()["id"]
    assert (
        client.post(
            f"{BASE}/feed-catalog/feeds/{feed_id}/products",
            headers=HEADERS,
            json={
                "sku": f"ACT-P-{suffix}",
                "display_name": "Lose Ware",
                "price_eur_t": "50",
                "freight_eur_t": "5",
                "packaging_unit": "t",
                "package_size": 1,
            },
        ).status_code
        == 201
    )
    assert (
        client.post(
            f"{BASE}/feed-catalog/feeds/{feed_id}/reference-values",
            headers=HEADERS,
            json={
                "nutrient_code": "crude_protein",
                "value": "80",
                "unit_code": "g_per_kg",
                "basis": "fresh_matter",
                "source_type": "analysis",
                "source_ref": "ACT golden",
            },
        ).status_code
        == 201
    )
    business = client.post(
        f"{BASE}/feeding/businesses",
        headers=HEADERS,
        json={"name": f"Ist-Betrieb {suffix}"},
    )
    group = client.post(
        f"{BASE}/lifecycle/groups",
        headers=HEADERS,
        json={
            "name": f"Ist-Gruppe {suffix}",
            "external_ref": f"actual-{suffix}",
            "animal_count": 10,
            "business_id": business.json()["id"],
        },
    )
    ration = client.post(
        f"{BASE}/lifecycle/rations",
        headers=HEADERS,
        json={
            "group_id": group.json()["id"],
            "name": f"Ist-Ration {suffix}",
            "source": "editor",
            "snapshot": {
                "ration": [
                    {
                        "feed_id": feed_id,
                        "feed_name": feed.json()["name"],
                        "kg_fm": 10,
                        "mixing_sequence": 1,
                    }
                ]
            },
        },
    )
    version_id = ration.json()["versions"][0]["id"]
    for current, target, reason in (
        ("draft", "in_review", None),
        ("in_review", "approved", "Ist-Erfassung geprueft"),
    ):
        assert (
            client.post(
                f"{BASE}/lifecycle/versions/{version_id}/transitions",
                headers=HEADERS,
                json={
                    "expected_status": current,
                    "target_status": target,
                    "reason": reason,
                },
            ).status_code
            == 200
        )
    plan = client.post(
        f"{BASE}/feeding/plans/publish",
        headers=HEADERS,
        json={
            "source_ration_version_id": version_id,
            "animal_count": 10,
            "dosing_step_kg": "0.1",
            "rounding_mode": "nearest",
            "valid_from": "2026-07-16",
            "valid_until": "2026-08-31",
            "reason": "Plan fuer Ist-Fuetterungs-Abnahme publizieren",
            "idempotency_key": f"actual-plan-{uuid4()}",
        },
    )
    assert plan.status_code == 201, plan.text
    return plan.json(), feed_id


def test_actual_feeding_is_plan_bound_idempotent_audited_and_csv_exportable() -> None:
    plan, feed_id = _plan()
    key = f"actual-{uuid4()}"
    payload = {
        "plan_version_id": plan["id"],
        "feeding_at": datetime.now(timezone.utc).isoformat(),
        "source": "manual",
        "source_ref": f"mobile-{uuid4()}",
        "cause_class": "dosing_error",
        "comment": "Waage wurde nachdosiert",
        "idempotency_key": key,
        "context": {"rest_feed_kg": 12, "dry_matter_pct": 40},
        "components": [{"feed_id": feed_id, "actual_kg": "108"}],
    }
    created = client.post(f"{BASE}/feeding/actuals", headers=HEADERS, json=payload)
    assert created.status_code == 201, created.text
    record = created.json()
    assert record["context"] == {"rest_feed_kg": 12, "dry_matter_pct": 40}
    component = record["components"][0]
    assert Decimal(str(component["target_kg"])) == Decimal("100")
    assert Decimal(str(component["delta_kg"])) == Decimal("8")
    assert Decimal(str(component["delta_pct"])) == Decimal("8")
    consequence = component["value_consequences"]
    assert Decimal(consequence["cost"]["delta_eur"]) == Decimal("0.44")
    assert Decimal(consequence["nutrients"][0]["delta"]) == Decimal("640")
    repeated = client.post(f"{BASE}/feeding/actuals", headers=HEADERS, json=payload)
    assert repeated.status_code == 201 and repeated.json()["id"] == record["id"]
    conflict = client.post(
        f"{BASE}/feeding/actuals",
        headers=HEADERS,
        json={
            **payload,
            "components": [{"feed_id": feed_id, "actual_kg": "109"}],
        },
    )
    assert conflict.status_code == 409
    exported = client.get(f"{BASE}/feeding/actuals/export.csv", headers=HEADERS)
    assert exported.status_code == 200
    assert record["id"] in exported.text and "dosing_error" in exported.text
    component_rows = client.get(f"{BASE}/feeding/actuals/components", headers=HEADERS)
    assert component_rows.status_code == 200
    projected = next(
        row for row in component_rows.json() if row["actual_record_id"] == record["id"]
    )
    assert projected["feed_id"] == feed_id
    assert Decimal(str(projected["cost_delta_eur"])) == Decimal("0.44")
    assert "crude_protein" in projected["nutrient_delta_summary"]

    db = SessionLocal()
    try:
        events = (
            db.execute(
                text("""SELECT payload FROM public.outbox_events WHERE tenant_id=:tenant_id
          AND event_type='feeding.actual.recorded' AND aggregate_id=:id"""),
                {"tenant_id": TENANT, "id": record["id"]},
            )
            .scalars()
            .all()
        )
        assert len(events) == 1
        assert json.loads(events[0])["payload"]["plan_version_id"] == plan["id"]
        with pytest.raises(DBAPIError):
            db.execute(
                text(
                    "UPDATE domain_agrar.feeding_actual_records SET comment='x' WHERE id=:id"
                ),
                {"id": record["id"]},
            )
            db.commit()
    finally:
        db.rollback()
        db.close()


def test_actual_feeding_rejects_unknown_component_other_without_comment_and_roles() -> (
    None
):
    plan, feed_id = _plan()
    common = {
        "plan_version_id": plan["id"],
        "feeding_at": datetime.now(timezone.utc).isoformat(),
        "source": "manual",
        "source_ref": f"mobile-{uuid4()}",
        "idempotency_key": f"actual-{uuid4()}",
    }
    unknown = client.post(
        f"{BASE}/feeding/actuals",
        headers=HEADERS,
        json={
            **common,
            "cause_class": "normal",
            "components": [{"feed_id": "not-planned", "actual_kg": 1}],
        },
    )
    assert unknown.status_code == 409 and "nicht im Plan" in unknown.json()["detail"]
    other = client.post(
        f"{BASE}/feeding/actuals",
        headers=HEADERS,
        json={
            **common,
            "idempotency_key": f"actual-{uuid4()}",
            "cause_class": "other",
            "components": [{"feed_id": feed_id, "actual_kg": 100}],
        },
    )
    assert other.status_code == 409 and "Kommentar" in other.json()["detail"]

    local = FastAPI()
    local.include_router(router)
    local.dependency_overrides[get_current_user] = lambda: {
        "sub": "crm",
        "roles": ["CRM_LESEN"],
    }
    local.dependency_overrides[get_tenant_id] = lambda: TENANT
    local.dependency_overrides[get_db] = lambda: object()
    with TestClient(local, raise_server_exceptions=False) as role_client:
        assert role_client.get("/feeding/actuals").status_code == 403
        assert role_client.get("/feeding/actuals/export.csv").status_code == 403
        assert role_client.get("/feeding/actuals/findings").status_code == 403
        assert role_client.get("/feeding/actuals/measures").status_code == 403
        assert role_client.get("/feeding/actuals/deviation-policies").status_code == 403


def test_actual_feeding_is_tenant_and_business_grant_safe() -> None:
    plan, feed_id = _plan()
    foreign = client.get(
        f"{BASE}/feeding/actuals",
        headers={
            "Authorization": "Bearer dev-token",
            "X-Tenant-Id": str(uuid4()),
        },
    )
    assert foreign.status_code == 200 and foreign.json() == []

    reader_app = FastAPI()
    reader_app.include_router(router)
    reader_app.dependency_overrides[get_current_user] = lambda: {
        "sub": f"external-reader-{uuid4()}",
        "roles": ["FUTTERMITTEL_LESEN"],
    }
    reader_app.dependency_overrides[get_tenant_id] = lambda: TENANT
    with TestClient(reader_app, raise_server_exceptions=False) as reader:
        assert reader.get("/feeding/actuals").json() == []
        assert reader.get("/feeding/actuals/components").json() == []
        assert reader.get("/feeding/actuals/findings").json() == []
        assert reader.get("/feeding/actuals/measures").json() == []

    writer_app = FastAPI()
    writer_app.include_router(router)
    writer_app.dependency_overrides[get_current_user] = lambda: {
        "sub": f"external-writer-{uuid4()}",
        "roles": ["FUTTERMITTEL_BEARBEITEN"],
    }
    writer_app.dependency_overrides[get_tenant_id] = lambda: TENANT
    with TestClient(writer_app, raise_server_exceptions=False) as writer:
        denied = writer.post(
            "/feeding/actuals",
            json={
                "plan_version_id": plan["id"],
                "feeding_at": datetime.now(timezone.utc).isoformat(),
                "source": "manual",
                "source_ref": "denied",
                "cause_class": "normal",
                "idempotency_key": f"denied-{uuid4()}",
                "components": [{"feed_id": feed_id, "actual_kg": 100}],
            },
        )
        assert denied.status_code == 404


def test_deviation_policy_finding_and_human_measure_journey() -> None:
    plan, feed_id = _plan()
    policy = client.post(
        f"{BASE}/feeding/actuals/deviation-policies",
        headers=HEADERS,
        json={
            "feed_class": "forage",
            "warning_pct": "5",
            "critical_pct": "10",
            "valid_from": "2026-01-01",
            "reason": "Betriebliche Toleranz fuer Grundfutter festlegen",
        },
    )
    assert policy.status_code == 201, policy.text
    future_policy = client.post(
        f"{BASE}/feeding/actuals/deviation-policies",
        headers=HEADERS,
        json={
            "feed_class": "forage",
            "warning_pct": "1",
            "critical_pct": "2",
            "valid_from": (date.today() + timedelta(days=1)).isoformat(),
            "reason": "Kuenftige betriebliche Toleranz kontrolliert vormerken",
        },
    )
    assert future_policy.status_code == 201, future_policy.text
    assert future_policy.json()["version"] == policy.json()["version"] + 1
    actual = client.post(
        f"{BASE}/feeding/actuals",
        headers=HEADERS,
        json={
            "plan_version_id": plan["id"],
            "feeding_at": datetime.now(timezone.utc).isoformat(),
            "source": "manual",
            "source_ref": f"measure-{uuid4()}",
            "cause_class": "dosing_error",
            "comment": "Deutliche Ueberdosierung",
            "idempotency_key": f"measure-actual-{uuid4()}",
            "components": [{"feed_id": feed_id, "actual_kg": 115}],
        },
    )
    assert actual.status_code == 201, actual.text
    component_id = actual.json()["components"][0]["id"]
    findings = client.get(f"{BASE}/feeding/actuals/findings", headers=HEADERS)
    assert findings.status_code == 200
    finding = next(
        item for item in findings.json() if item["actual_component_id"] == component_id
    )
    assert finding["severity"] == "critical"
    assert Decimal(str(finding["delta_pct"])) == Decimal("15")
    assert finding["policy_version"] == policy.json()["version"]

    key = f"measure-{uuid4()}"
    payload = {
        "actual_component_id": component_id,
        "title": "Mischwagenwaage pruefen",
        "owner_subject": "stall-team",
        "due_date": (date.today() + timedelta(days=3)).isoformat(),
        "reason": "Kritische Grundfutterabweichung fachlich nachverfolgen",
        "idempotency_key": key,
    }
    created = client.post(
        f"{BASE}/feeding/actuals/measures", headers=HEADERS, json=payload
    )
    assert created.status_code == 201, created.text
    assert created.json()["finding"]["plan_version_id"] == plan["id"]
    repeated = client.post(
        f"{BASE}/feeding/actuals/measures", headers=HEADERS, json=payload
    )
    assert repeated.status_code == 201 and repeated.json()["id"] == created.json()["id"]
    conflict = client.post(
        f"{BASE}/feeding/actuals/measures",
        headers=HEADERS,
        json={**payload, "title": "Andere Massnahme"},
    )
    assert conflict.status_code == 409
    listed = client.get(f"{BASE}/feeding/actuals/measures", headers=HEADERS)
    assert any(item["id"] == created.json()["id"] for item in listed.json())

    db = SessionLocal()
    try:
        measure_events = (
            db.execute(
                text(
                    """SELECT event_type,payload FROM public.outbox_events
                WHERE tenant_id=:tenant_id AND (
                  (event_type='feeding.measure.created' AND aggregate_id=:measure_id) OR
                  (event_type='feeding.deviation.exceeded' AND aggregate_id=:component_id)
                ) ORDER BY event_type"""
                ),
                {
                    "tenant_id": TENANT,
                    "measure_id": created.json()["id"],
                    "component_id": component_id,
                },
            )
            .mappings()
            .all()
        )
        assert [event["event_type"] for event in measure_events] == [
            "feeding.deviation.exceeded",
            "feeding.measure.created",
        ]
        assert all(
            (
                event["payload"]
                if isinstance(event["payload"], dict)
                else json.loads(event["payload"])
            )["schema_version"]
            == "1.0"
            for event in measure_events
        )
        with pytest.raises(DBAPIError):
            db.execute(
                text(
                    "UPDATE domain_agrar.feeding_actual_measures SET title='x' WHERE id=:id"
                ),
                {"id": created.json()["id"]},
            )
            db.commit()
    finally:
        db.rollback()
        db.close()
