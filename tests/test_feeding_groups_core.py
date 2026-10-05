from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.api.v1.endpoints import rations_lifecycle
from app.auth.deps import get_current_user
from app.core.database import get_db
from app.core.tenant import get_tenant_id


ROOT = Path(__file__).parents[1]


def test_group_profile_and_cross_field_rules() -> None:
    from app.agrar.rations.groups import GroupProfile, validate_group_parameters

    assert GroupProfile.FRESH_COW.value == "fresh_cow"
    valid = validate_group_parameters(
        profile=GroupProfile.DRY_CLOSE_UP,
        pregnancy_status="pregnant",
        gestation_day=260,
        milk_fat_pct=None,
        milk_protein_pct=None,
        valid_from=date.today(),
        valid_until=date.today() + timedelta(days=14),
    )
    assert valid["gestation_day"] == 260

    with pytest.raises(ValueError, match="Traechtigkeitstag"):
        validate_group_parameters(
            profile=GroupProfile.HIGH_YIELD_COW,
            pregnancy_status="open",
            gestation_day=120,
            milk_fat_pct=4.0,
            milk_protein_pct=3.4,
            valid_from=date.today(),
            valid_until=None,
        )
    with pytest.raises(ValueError, match="Gueltigkeitsende"):
        validate_group_parameters(
            profile=GroupProfile.CUSTOM,
            pregnancy_status="unknown",
            gestation_day=None,
            milk_fat_pct=None,
            milk_protein_pct=None,
            valid_from=date.today(),
            valid_until=date.today() - timedelta(days=1),
        )


def test_group_api_publishes_typed_detail_update_and_history_contracts() -> None:
    from app.api.v1.endpoints.rations_lifecycle import (
        FeedingGroupOut,
        FeedingGroupUpdateIn,
        FeedingGroupRevisionOut,
        router,
    )

    response_models = {
        (route.path, next(iter(route.methods or []))): route.response_model
        for route in router.routes
        if hasattr(route, "response_model")
    }
    assert response_models[("/lifecycle/groups/{group_id}", "GET")] is FeedingGroupOut
    assert response_models[("/lifecycle/groups/{group_id}", "PATCH")] is FeedingGroupOut
    assert response_models[("/lifecycle/groups/{group_id}/history", "GET")] == list[FeedingGroupRevisionOut]

    with pytest.raises(ValidationError):
        FeedingGroupUpdateIn(expected_revision=0, reason="x")
    with pytest.raises(ValidationError, match="Traechtigkeitstag"):
        FeedingGroupUpdateIn(
            expected_revision=1,
            reason="Gruppenwechsel",
            pregnancy_status="open",
            gestation_day=80,
        )


def test_group_migration_is_additive_and_keeps_append_only_revisions() -> None:
    migration = ROOT / "alembic" / "versions" / "feed_core_groups_20260715.py"
    text = migration.read_text(encoding="utf-8")
    assert 'down_revision = "feed_core_business_20260715"' in text
    for field in (
        "profile_code", "pregnancy_status", "gestation_day", "milk_fat_pct",
        "milk_protein_pct", "risk_level", "valid_from", "valid_until", "revision",
    ):
        assert field in text
    assert "feeding_group_revisions" in text
    assert "guard_immutable_feeding_group_revision" in text
    assert "ck_feeding_group_gestation" in text
    assert "ck_feeding_group_validity" in text


def test_group_object_page_is_native_meridian_and_generator_ready() -> None:
    from app.core.screen_definitions import get_screen_definition
    from app.api.v1.endpoints.mask_screen_definition import _check_readiness

    definition = get_screen_definition("agrar/feeding-group")
    assert definition is not None
    assert definition["adapter"] == {
        "type": "native", "sourceId": "agrar/feeding-group", "temporary": False
    }
    assert definition["layout"]["floorplan"] == "objectPage"
    assert definition["layout"]["contextRail"] == "audit"
    readiness = _check_readiness(definition)
    assert readiness["generatorReady"] is True

    lifecycle = get_screen_definition("agrar/rations-lifecycle")
    groups = next(table for table in lifecycle["tables"] if table["key"] == "groups")
    assert groups["rowRouteTemplate"] == "/portal/rationsoptimierung?view=group&group_id={id}"


class _Rows:
    def mappings(self) -> "_Rows":
        return self

    def all(self) -> list[dict]:
        return []


class _CaptureSession:
    def __init__(self) -> None:
        self.sql: list[str] = []

    def execute(self, statement: object, params: dict | None = None) -> _Rows:
        self.sql.append(str(statement))
        return _Rows()


def test_group_list_is_filtered_by_active_business_grants() -> None:
    from app.services.rations_lifecycle_service import RationLifecycleService

    db = _CaptureSession()
    service = RationLifecycleService(db, "tenant-a", "advisor")  # type: ignore[arg-type]
    assert service.list_groups(active_only=True, subject="advisor", unrestricted=False) == []
    query = "\n".join(db.sql)
    assert "feeding_business_grants" in query
    assert "revoked_at IS NULL" in query
    assert "valid_until" in query
    assert "g.created_by=:subject" in query


def test_group_detail_hides_resource_without_business_scope(monkeypatch: pytest.MonkeyPatch) -> None:
    class DeniedService:
        def has_group_access(self, group_id: str, subject: str, scope: str) -> bool:
            return False

        def get_group(self, group_id: str) -> dict:
            raise AssertionError("resource must not be loaded after denied scope")

    app = FastAPI()
    app.include_router(rations_lifecycle.router)
    app.dependency_overrides[get_current_user] = lambda: {
        "sub": "advisor", "roles": ["FUTTERMITTEL_LESEN"]
    }
    app.dependency_overrides[get_tenant_id] = lambda: "tenant-a"
    app.dependency_overrides[get_db] = lambda: object()
    monkeypatch.setattr(rations_lifecycle, "_service", lambda *_args: DeniedService())

    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get("/lifecycle/groups/foreign-group")
    assert response.status_code == 404
