"""FEED-CORE-015: Fuetterungsbetriebe, Standorte, Herden, Grants.

Teil 1: Rollenregression ohne DB (isolierte Router-App, Muster test_rations_authz).
Teil 2: DB-Integration ueber die volle Hierarchie inkl. CRM-Aktivierung ohne
Doppelerfassung, Backfill und Grant-Gueltigkeit (Dev-DB, Muster
test_rations_controlling).
"""
from datetime import datetime, timedelta, timezone
import os
from typing import Any
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints import feeding_core
from app.auth.deps import get_current_user
from app.core.database import get_db
from app.core.tenant import get_tenant_id

# ── Teil 1: Rollenregression (ohne DB) ─────────────────────────────────────

_CONTEXT: dict[str, Any] = {"roles": []}
_APP = FastAPI()
_APP.include_router(feeding_core.router)
_APP.dependency_overrides[get_current_user] = lambda: {"sub": "role-test", "roles": _CONTEXT["roles"]}
_APP.dependency_overrides[get_tenant_id] = lambda: "tenant-role-test"
_APP.dependency_overrides[get_db] = lambda: object()


@pytest.fixture(scope="module")
def role_client() -> TestClient:
    with TestClient(_APP) as value:
        yield value


REQUESTS = [
    ("post", "/feeding/businesses", {"name": "Hof A"}),
    ("post", "/feeding/businesses/activate-from-partner", {"business_partner_id": "bp-1", "name": "Hof A"}),
    ("get", "/feeding/businesses", None),
    ("get", "/feeding/businesses/b-1", None),
    ("post", "/feeding/businesses/b-1/sites", {"name": "Standort Nord"}),
    ("post", "/feeding/businesses/b-1/herds", {"name": "Herde 1"}),
    ("post", "/feeding/businesses/b-1/groups", {"group_id": "g-1"}),
    ("post", "/feeding/businesses/backfill-default", None),
    ("post", "/feeding/businesses/b-1/grants", {"subject": "berater@example", "scope": "read"}),
    ("get", "/feeding/businesses/b-1/grants", None),
    ("delete", "/feeding/businesses/b-1/grants?subject=x&scope=read", None),
]


@pytest.mark.parametrize(("method", "path", "body"), REQUESTS)
def test_feeding_core_rejects_user_without_domain_role(role_client: TestClient, method: str, path: str, body: dict | None) -> None:
    _CONTEXT["roles"] = []
    response = getattr(role_client, method)(path, **({"json": body} if body is not None else {}))
    assert response.status_code == 403, (method, path, response.text)


def test_grant_management_requires_admin_level(role_client: TestClient) -> None:
    _CONTEXT["roles"] = ["FUTTERMITTEL_BEARBEITEN"]
    response = role_client.post("/feeding/businesses/b-1/grants", json={"subject": "s", "scope": "read"})
    assert response.status_code == 403
    response = role_client.post("/feeding/businesses/backfill-default")
    assert response.status_code == 403


def test_feeding_core_routes_publish_typed_response_models() -> None:
    from app.api.v1.endpoints.feeding_core import BusinessStructureOut, FeedingBusinessOut

    response_models = {
        route.path: route.response_model
        for route in feeding_core.router.routes
        if hasattr(route, "response_model")
    }
    assert response_models["/feeding/businesses"] == list[FeedingBusinessOut]
    assert response_models["/feeding/businesses/{business_id}"] is BusinessStructureOut


def test_business_endpoint_requires_business_grant(role_client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    class DeniedService:
        def has_business_access(self, business_id: str, subject: str, scope: str) -> bool:
            return False

        def upsert_site(self, business_id: str, payload: dict[str, Any]) -> dict[str, Any]:
            return {"id": "must-not-be-created"}

    _CONTEXT["roles"] = ["FUTTERMITTEL_BEARBEITEN"]
    monkeypatch.setattr(feeding_core, "_service", lambda *_args, **_kwargs: DeniedService())
    response = role_client.post("/feeding/businesses/b-1/sites", json={"name": "Nicht erlaubt"})
    assert response.status_code == 403


def test_business_list_is_filtered_for_non_admin(role_client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    class FilterAwareService:
        def list_businesses(self, *, include_inactive: bool, subject: str | None = None,
                            unrestricted: bool = False) -> list[dict[str, Any]]:
            if subject == "role-test" and not unrestricted:
                return []
            return [{"id": "foreign-business"}]

    _CONTEXT["roles"] = ["FUTTERMITTEL_LESEN"]
    monkeypatch.setattr(feeding_core, "_service", lambda *_args, **_kwargs: FilterAwareService())
    response = role_client.get("/feeding/businesses")
    assert response.status_code == 200
    assert response.json() == []


class _Mappings:
    def __init__(self, row: dict[str, Any] | None):
        self.row = row

    def first(self) -> dict[str, Any] | None:
        return self.row

    def one(self) -> dict[str, Any]:
        assert self.row is not None
        return self.row


class _Result:
    def __init__(self, row: dict[str, Any] | None = None, *, scalar_exists: bool = False, rowcount: int = 0):
        self.row = row
        self.scalar_exists = scalar_exists
        self.rowcount = rowcount

    def mappings(self) -> _Mappings:
        return _Mappings(self.row)

    def first(self) -> tuple[int] | None:
        return (1,) if self.scalar_exists else None


class _GuardSession:
    def __init__(self, *, foreign_business_id: bool = False, site_belongs: bool = True,
                 herd_belongs: bool = True, creator_access: bool = False):
        self.foreign_business_id = foreign_business_id
        self.site_belongs = site_belongs
        self.herd_belongs = herd_belongs
        self.creator_access = creator_access
        self.statements: list[str] = []

    def execute(self, statement: Any, params: dict[str, Any] | None = None) -> _Result:
        sql = str(statement)
        self.statements.append(sql)
        if "tenant_id<>" in sql or "tenant_id !=" in sql:
            return _Result(scalar_exists=self.foreign_business_id)
        if "FROM domain_agrar.feeding_businesses" in sql and "created_by=:subject" in sql:
            return _Result(scalar_exists=self.creator_access)
        if "FROM domain_agrar.feeding_businesses" in sql:
            return _Result({"id": (params or {}).get("id") or (params or {}).get("business_id"), "tenant_id": "tenant-a"})
        if "FROM domain_agrar.farm_sites" in sql:
            return _Result({"id": (params or {}).get("site_id")}) if self.site_belongs else _Result()
        if "FROM domain_agrar.herds" in sql:
            return _Result({"id": (params or {}).get("herd_id")}) if self.herd_belongs else _Result()
        if "SELECT 1 FROM domain_agrar.feeding_business_grants" in sql:
            return _Result(scalar_exists=self.creator_access and "created_by=:subject" in sql)
        if "INSERT INTO domain_agrar.feeding_businesses" in sql:
            return _Result({"id": (params or {})["id"], "tenant_id": (params or {})["tenant_id"]})
        if "INSERT INTO domain_agrar.herds" in sql:
            return _Result({"id": (params or {})["id"], "business_id": (params or {})["business_id"]})
        if "UPDATE domain_agrar.feeding_groups" in sql:
            return _Result({"id": (params or {})["group_id"], "business_id": (params or {})["business_id"]})
        if "INSERT INTO domain_agrar.feeding_business_grants" in sql:
            return _Result({"id": "grant-1", "business_id": (params or {})["business_id"]})
        if "UPDATE domain_agrar.feeding_business_grants" in sql:
            return _Result(rowcount=1)
        if "DELETE FROM domain_agrar.feeding_business_grants" in sql:
            return _Result(rowcount=1)
        raise AssertionError(f"Unerwartetes SQL: {sql}")

    def commit(self) -> None:
        return None


def test_business_upsert_rejects_id_owned_by_other_tenant() -> None:
    from app.services.feeding_business_service import FeedingBusinessConflict, FeedingBusinessService

    service = FeedingBusinessService(_GuardSession(foreign_business_id=True), "tenant-a", "tester")  # type: ignore[arg-type]
    with pytest.raises(FeedingBusinessConflict):
        service.upsert_business({"id": "shared-id", "name": "Hof A"})


def test_herd_rejects_site_from_other_business() -> None:
    from app.services.feeding_business_service import FeedingBusinessNotFound, FeedingBusinessService

    db = _GuardSession(site_belongs=False)
    service = FeedingBusinessService(db, "tenant-a", "tester")  # type: ignore[arg-type]
    with pytest.raises(FeedingBusinessNotFound):
        service.upsert_herd("business-a", {"name": "Herde", "site_id": "foreign-site"})
    assert not any("INSERT INTO domain_agrar.herds" in sql for sql in db.statements)


def test_group_rejects_herd_from_other_business() -> None:
    from app.services.feeding_business_service import FeedingBusinessNotFound, FeedingBusinessService

    db = _GuardSession(herd_belongs=False)
    service = FeedingBusinessService(db, "tenant-a", "tester")  # type: ignore[arg-type]
    with pytest.raises(FeedingBusinessNotFound):
        service.assign_group("business-a", "group-a", "foreign-herd")
    assert not any("UPDATE domain_agrar.feeding_groups" in sql for sql in db.statements)


def test_grant_revoke_is_append_only() -> None:
    from app.services.feeding_business_service import FeedingBusinessService

    db = _GuardSession()
    service = FeedingBusinessService(db, "tenant-a", "tester")  # type: ignore[arg-type]
    assert service.revoke_access("business-a", "advisor", "read") == 1
    assert any("UPDATE domain_agrar.feeding_business_grants" in sql for sql in db.statements)
    assert not any("DELETE FROM domain_agrar.feeding_business_grants" in sql for sql in db.statements)


def test_regrant_preserves_revoked_grant_history() -> None:
    from app.services.feeding_business_service import FeedingBusinessService

    db = _GuardSession()
    service = FeedingBusinessService(db, "tenant-a", "tester")  # type: ignore[arg-type]
    service.grant_access("business-a", "advisor", "read")
    grant_sql = next(sql for sql in db.statements if "INSERT INTO domain_agrar.feeding_business_grants" in sql)
    assert "WHERE revoked_at IS NULL" in grant_sql
    assert "revoked_by=NULL" not in grant_sql


def test_business_creator_has_implicit_owner_access() -> None:
    from app.services.feeding_business_service import FeedingBusinessService

    db = _GuardSession(creator_access=True)
    service = FeedingBusinessService(db, "tenant-a", "creator")  # type: ignore[arg-type]
    assert service.has_business_access("business-a", "creator", "write") is True


# ── Teil 2: DB-Integration (Dev-DB) ────────────────────────────────────────

ROOT = "/api/v1/agrar/rations-optimization/feeding"
TENANT = "00000000-0000-0000-0000-000000000001"
HEADERS = {"Authorization": "Bearer dev-token", "X-Tenant-Id": TENANT}


@pytest.mark.skipif(not os.getenv("RUN_FEEDING_DB_TESTS"), reason="expliziter Dev-DB-Integrationstest")
def test_business_hierarchy_partner_activation_backfill_and_grants() -> None:
    from app.main import app

    client = TestClient(app, raise_server_exceptions=True)
    suffix = str(uuid4())[:8]
    partner_id = f"bp-{suffix}"

    # CRM-Aktivierung ist idempotent (FEED-BUS-001: keine Doppelerfassung)
    first = client.post(f"{ROOT}/businesses/activate-from-partner", headers=HEADERS,
                        json={"business_partner_id": partner_id, "name": f"Hof {suffix}"})
    assert first.status_code == 201, first.text
    business_id = first.json()["id"]
    second = client.post(f"{ROOT}/businesses/activate-from-partner", headers=HEADERS,
                         json={"business_partner_id": partner_id, "name": "anders"})
    assert second.status_code == 201
    assert second.json()["id"] == business_id

    # Standort + Herde + Gruppenzuordnung
    site = client.post(f"{ROOT}/businesses/{business_id}/sites", headers=HEADERS,
                       json={"name": f"Standort {suffix}"})
    assert site.status_code == 201, site.text
    herd = client.post(f"{ROOT}/businesses/{business_id}/herds", headers=HEADERS,
                       json={"name": f"Herde {suffix}", "site_id": site.json()["id"]})
    assert herd.status_code == 201, herd.text

    group = client.post("/api/v1/agrar/rations-optimization/lifecycle/groups", headers=HEADERS,
                        json={"name": f"Gruppe {suffix}", "animal_count": 42, "feeding_system": "TMR"})
    assert group.status_code == 201, group.text
    group_id = group.json()["id"]
    assigned = client.post(f"{ROOT}/businesses/{business_id}/groups", headers=HEADERS,
                           json={"group_id": group_id, "herd_id": herd.json()["id"]})
    assert assigned.status_code == 200, assigned.text
    assert assigned.json()["business_id"] == business_id

    # Struktur zeigt die volle Hierarchie
    structure = client.get(f"{ROOT}/businesses/{business_id}", headers=HEADERS)
    assert structure.status_code == 200
    payload = structure.json()
    assert payload["business"]["business_partner_id"] == partner_id
    assert any(g["id"] == group_id for g in payload["groups"])

    # Backfill haengt betriebslose Gruppen an den Default-Betrieb
    orphan = client.post("/api/v1/agrar/rations-optimization/lifecycle/groups", headers=HEADERS,
                         json={"name": f"Waise {suffix}", "animal_count": 5, "feeding_system": "TMR"})
    assert orphan.status_code == 201
    backfill = client.post(f"{ROOT}/businesses/backfill-default", headers=HEADERS)
    assert backfill.status_code == 200, backfill.text
    assert backfill.json()["assigned_groups"] >= 1

    # Grants: zeitlich abgelaufener Grant zaehlt nicht
    expired_until = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    expired = client.post(f"{ROOT}/businesses/{business_id}/grants", headers=HEADERS,
                          json={"subject": f"berater-{suffix}", "scope": "read", "valid_until": expired_until})
    assert expired.status_code == 201, expired.text
    grants = client.get(f"{ROOT}/businesses/{business_id}/grants", headers=HEADERS)
    assert grants.status_code == 200
    assert any(g["subject"] == f"berater-{suffix}" for g in grants.json())

    from app.core.database import SessionLocal
    from app.services.feeding_business_service import FeedingBusinessService
    db = SessionLocal()
    try:
        service = FeedingBusinessService(db, TENANT, "test")
        assert service.has_business_access(business_id, f"berater-{suffix}", "read") is False
        service.grant_access(business_id, f"berater-{suffix}", "write")
        assert service.has_business_access(business_id, f"berater-{suffix}", "read") is True
        assert service.has_business_access(business_id, f"berater-{suffix}", "admin") is False
    finally:
        db.close()

    # Tenant-Isolation: fremder Mandant sieht den Betrieb nicht
    other = client.get(f"{ROOT}/businesses/{business_id}", headers={**HEADERS, "X-Tenant-Id": str(uuid4())})
    assert other.status_code in (404, 403)
