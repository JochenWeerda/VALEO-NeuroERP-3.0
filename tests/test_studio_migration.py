"""Real Studio migration compiler and isolated SQL execution of generated artifacts."""
from copy import deepcopy
from uuid import uuid4
import hashlib

import pytest
from pydantic import ValidationError

from app.api.v1.schemas.studio_migration import StudioMigrationIn
from app.services import studio_migration as service


@pytest.fixture(autouse=True)
def _enable_dev_token():
    yield


@pytest.fixture(scope="session", autouse=True)
def _seed_contract_test_tenants():
    yield


def definition():
    return {"schemaVersion": 1, "id": "tenant/migration-probe", "domain": "crm", "mode": "list",
            "title": "Kunden", "adapter": {"type": "native", "sourceId": "tenant/migration-probe", "temporary": True},
            "dataSources": [{"key": "customers"}], "actions": [{"key": "create_activity"}]}


def schema_change(**updates):
    return {"operation": "create_table", "schema_name": "domain_crm", "table": "studio_migration_probe",
            "columns": [{"name": "bezeichnung", "type": "text", "nullable": False}], **updates}


def test_autowiring_uses_server_catalog_without_mutating_input():
    source = definition(); before = deepcopy(source)
    first = service.plan_migration(StudioMigrationIn(definition=source), "t1", "verified")
    second = service.plan_migration(StudioMigrationIn(definition=source), "t1", "verified")
    assert source == before and first == second
    assert first.definition["dataSources"][0]["endpoint"] == "/api/v1/crm/customers"
    assert first.definition["actions"][0]["commandEndpoint"].endswith("/actions/create_activity")
    assert first.can_activate is False and first.migration_source is None
    assert first.channel_status == {"human": "not_verified", "cli": "not_verified", "mcp": "not_verified"}
    assert "tenant_isolation" in first.required_contracts and "domain_roles" in first.required_contracts
    assert first.plan_hash != service.plan_migration(StudioMigrationIn(definition=source), "other", "verified").plan_hash
    assert first.plan_hash != service.plan_migration(StudioMigrationIn(definition=source), "t1", "other").plan_hash


@pytest.mark.parametrize("placement", ["actions", "rowActions", "availableActions"])
def test_all_action_locations_are_wired_and_keep_agent_block(placement):
    source = definition();source["actions"] = []
    source["tabs"] = [{placement: [{"key": "stornieren"}]}]
    plan = service.plan_migration(StudioMigrationIn(definition=source), "t1", "verified")
    action = plan.definition["tabs"][0][placement][0]
    assert action["forbiddenForAgents"] is True and action["requiresConfirmation"] is True
    assert action["dangerLevel"] == "high"


@pytest.mark.parametrize("kind", ["url", "command", "weak_policy"])
def test_autowiring_never_repairs_away_conflicting_or_unknown_contracts(kind):
    source = definition()
    if kind == "url":source["dataSources"][0]["endpoint"] = "https://outside.invalid"
    if kind == "command":source["actions"][0]["key"] = "invented_transfer"
    if kind == "weak_policy":source["actions"] = [{"key": "stornieren", "dangerLevel": "safe", "forbiddenForAgents": False}]
    plan = service.plan_migration(StudioMigrationIn(definition=source), "t1", "verified")
    always = {"studio_revision_simulation_and_independent_release_required",
              "human_cli_mcp_role_tenant_and_replay_contract_tests_required"}
    assert set(plan.blockers) - always and plan.can_activate is False
    if kind == "url":assert plan.definition["dataSources"][0]["endpoint"] == "https://outside.invalid"


@pytest.mark.parametrize("column", ["tenant_id", "id", "version", "created_by", "updated_at", "x); DROP TABLE y;--"])
def test_schema_cannot_override_identity_or_inject_identifiers(column):
    with pytest.raises(ValidationError):
        StudioMigrationIn(definition=definition(), schema_changes=[schema_change(columns=[{"name": column, "type": "text"}])])


@pytest.mark.parametrize("change,error", [
    ({"schema_name": "domain_invented"}, "schema_not_in_canonical_catalog"),
    ({"table": "customers"}, "table_already_exists"),
    ({"operation": "add_columns", "table": "missing_table", "columns": [{"name": "note", "type": "text"}]}, "table_not_in_canonical_catalog"),
])
def test_schema_targets_must_match_canonical_catalog(change, error):
    # Use an actual canonical table rather than a duplicate fixture schema.
    if error == "table_already_exists":change = {"schema_name": "domain_shared", "table": "tenants"}
    with pytest.raises(ValueError, match=error):
        service.plan_migration(StudioMigrationIn(definition=definition(), schema_changes=[schema_change(**change)]), "t1", "verified")


def test_additive_existing_fields_and_table_artifacts_are_hash_bound():
    body = StudioMigrationIn(definition=definition(), schema_changes=[schema_change(), schema_change(
        operation="add_columns", schema_name="domain_shared", table="branches",
        columns=[{"name": "studio_note_probe", "type": "text"}])])
    first = service.plan_migration(body, "t1", "verified")
    assert "op.create_table(" in first.migration_source and "op.add_column(" in first.migration_source
    assert first.migration_hash == hashlib.sha256(first.migration_source.encode()).hexdigest()
    assert first.migration_filename.startswith("studio_")
    compile(first.migration_source, first.migration_filename, "exec")
    assert "schema_artifact_requires_reviewed_deployment" in first.blockers
    changed = body.model_copy(deep=True);changed.schema_changes[0].columns[0].name = "andere_bezeichnung"
    assert service.plan_migration(changed, "t1", "verified").plan_hash != first.plan_hash


def test_required_extension_needs_a_real_backfill_not_invented_defaults():
    with pytest.raises(ValidationError, match="backfill"):
        StudioMigrationIn(definition=definition(), schema_changes=[schema_change(operation="add_columns")])


def test_api_uses_verified_actor_tenant_and_existing_design_role():
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from app.api.v1.endpoints.studio_drafts import router
    from app.auth.deps import get_current_user
    from app.core.tenant import get_tenant_id
    app = FastAPI(); app.include_router(router, prefix="/api/v1")
    user = {"sub": "verified", "roles": ["EINKAUF_BEARBEITEN"]}
    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_tenant_id] = lambda: "own"
    with TestClient(app) as client:
        result = client.post("/api/v1/studio/migration-plan?tenant_id=foreign", json={"definition": definition()})
        assert result.status_code == 200, result.text
        assert result.json()["tenant_id"] == "own" and result.json()["actor"] == "verified"
        assert client.post("/api/v1/studio/migration-plan", json={"definition": definition(), "actor": "forged"}).status_code == 422
        user["roles"] = ["FINANCE_LESEN"]
        assert client.post("/api/v1/studio/migration-plan", json={"definition": definition()}).status_code == 403


def test_generated_table_executes_in_shared_probe_with_tenant_fk_and_composite_key(require_db):
    from sqlalchemy import text
    from sqlalchemy.exc import IntegrityError
    from alembic.migration import MigrationContext
    from alembic.operations import Operations
    from app.core.database import engine
    from testgrenze import pruefstand_erlaubt
    assert pruefstand_erlaubt(engine.url)
    table = "studio_probe_" + uuid4().hex[:12]
    body = StudioMigrationIn(definition=definition(), schema_changes=[schema_change(table=table)])
    plan = service.plan_migration(body, "synthetic", "designer")
    module = {};exec(compile(plan.migration_source, plan.migration_filename, "exec"), module)
    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            with Operations.context(MigrationContext.configure(connection)):
                module["upgrade"]()
            tenants = [str(uuid4()), str(uuid4())]
            for tenant in tenants:
                connection.execute(text("INSERT INTO domain_shared.tenants (id,name,is_active) VALUES (:id,:id,true)"), {"id": tenant})
            same_id = str(uuid4())
            insert = text(f"INSERT INTO domain_crm.{table} (tenant_id,id,version,created_by,created_at,bezeichnung) VALUES (:tenant,:id,1,'designer',NOW(),'synthetic')")
            for tenant in tenants:connection.execute(insert, {"tenant": tenant, "id": same_id})
            assert connection.execute(text(f"SELECT COUNT(*) FROM domain_crm.{table}")).scalar_one() == 2
            with pytest.raises(IntegrityError):
                with connection.begin_nested():
                    connection.execute(insert, {"tenant": "missing-tenant", "id": str(uuid4())})
        finally:
            transaction.rollback()



@pytest.mark.parametrize("changes", [
    [schema_change(), schema_change()],
    [schema_change(columns=[{"name": "x", "type": "text"}, {"name": "x", "type": "text"}])],
    [schema_change(columns=[{"name": "x", "type": "text); DROP TABLE tenants"}])],
    [schema_change(operation="add_columns", schema_name="domain_shared", table="branches",
                   columns=[{"name": "name", "type": "text"}])],
])
def test_duplicate_targets_columns_unsupported_types_and_existing_fields_rejected(changes):
    with pytest.raises((ValidationError, ValueError)):
        service.plan_migration(StudioMigrationIn(definition=definition(), schema_changes=changes), "t1", "verified")
