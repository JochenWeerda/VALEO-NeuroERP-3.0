"""Revision-bound plans in the existing append-only Studio history, never DDL."""
from copy import deepcopy

from sqlalchemy import text

from app.api.v1.schemas.studio_migration import StudioMigrationIn, StudioSavedMigrationIn
from app.core.studio_release import definition_hash
from app.services import studio_draft_store as store
from app.services.studio_migration import plan_migration


def _request_hash(body):
    return definition_hash([change.model_dump(mode="json") for change in body.schema_changes])


def _replay(snapshot, body):
    if snapshot is None:
        return None
    if snapshot.get("migration_input_hash") != _request_hash(body):
        raise ValueError("idempotenzschluessel_anderer_inhalt")
    return deepcopy(snapshot["saved_migration"])


def _compile(item, tenant, actor, body):
    if item["revision"] != body.expected_revision:
        raise ValueError("entwurf_seit_anzeige_geaendert")
    if item["status"] not in {"draft", "review"}:
        raise ValueError("migrationsplan_erfordert_entwurf_oder_review")
    candidate_hash = definition_hash(item["definition"])
    plan = plan_migration(StudioMigrationIn(definition=item["definition"], schema_changes=body.schema_changes), tenant, actor)
    binding = {"tenant_id": tenant, "actor": actor, "draft_id": item["id"],
               "candidate_revision": item["revision"], "candidate_definition_hash": candidate_hash,
               "plan_hash": plan.plan_hash, "schema_request_hash": _request_hash(body)}
    result = {"event_id": str(body.idempotency_key), "draft_id": item["id"],
              "candidate_revision": item["revision"], "candidate_definition_hash": candidate_hash,
              "binding_hash": definition_hash(binding),
              "schema_changes": [change.model_dump(mode="json") for change in body.schema_changes],
              "requires_definition_update": candidate_hash != plan.definition_hash,
              "plan": plan.model_dump(mode="json")}
    return {**item, "migration_input_hash": _request_hash(body), "saved_migration": result}


@store._durable_operation
def save_migration_plan(tenant: str, draft_id: str, actor: str, body: StudioSavedMigrationIn):
    """Compile while holding the same draft lock as edits; commit only one history event."""
    key = str(body.idempotency_key)
    if store._prefer_memory:
        with store._memory_lock:
            replay = _replay(store.get_status_replay(tenant, draft_id, actor, "migration_plan", body.expected_revision, key), body)
            if replay is not None:
                return replay
            item = store.get_draft(tenant, draft_id)
            if item is None:
                raise KeyError(draft_id)
            snapshot = _compile(item, tenant, actor, body)
            store._HISTORY.append(store._history_entry(snapshot, actor, "migration_plan", body.expected_revision, key))
            return deepcopy(snapshot["saved_migration"])
    from app.infrastructure.models.studio_models import ScreenDefinitionDraft
    session = store._sql_session()
    try:
        session.execute(text("SELECT pg_advisory_xact_lock(hashtextextended(:key, 0))"), {"key": key})
        replay = _replay(store._sql_replay(session, key, tenant, draft_id, actor, "migration_plan", body.expected_revision), body)
        if replay is not None:
            return replay
        row = session.query(ScreenDefinitionDraft).filter_by(id=draft_id, tenant_id=tenant).with_for_update().one_or_none()
        if row is None:
            raise KeyError(draft_id)
        snapshot = _compile(store._with_revision(store._row_to_dict(row)), tenant, actor, body)
        store._append_sql_history(session, snapshot, actor, "migration_plan", body.expected_revision, key)
        session.commit()
        return deepcopy(snapshot["saved_migration"])
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def verify_saved_plan(item, saved, actor):
    """Recompute against current compiler/catalog; stored evidence is never self-authorizing."""
    from app.api.v1.schemas.studio_migration import StudioSavedMigrationOut
    from pydantic import ValidationError
    try:
        checked = StudioSavedMigrationOut.model_validate(saved).model_dump(mode="json")
        body = StudioSavedMigrationIn(expected_revision=item["revision"], idempotency_key=checked["event_id"],
                                      schema_changes=checked["schema_changes"])
        current = _compile(item, item["tenant_id"], actor, body)["saved_migration"]
    except (ValidationError, KeyError, TypeError) as error:
        raise ValueError("migrationsplan_nachweis_ungueltig") from error
    if checked != current:
        raise ValueError("migrationsplan_nachweis_veraltet_oder_veraendert")
    if checked["requires_definition_update"]:
        raise ValueError("migrationsplan_vorschlaege_zuerst_speichern")
    if checked["schema_changes"]:
        raise ValueError("schema_deployment_nachweis_fehlt")
    expected = {"studio_revision_simulation_and_independent_release_required",
                "human_cli_mcp_role_tenant_and_replay_contract_tests_required"}
    if set(checked["plan"]["blockers"]) - expected:
        raise ValueError("migrationsplan_fachvertrag_nicht_freigabefaehig")
    return {**checked, "actor": actor, "tenant_id": item["tenant_id"]}


def require_saved_plan(item, entries):
    for entry in reversed(entries):
        if entry.get("action") != "migration_plan":
            continue
        saved = entry.get("snapshot", {}).get("saved_migration")
        if not isinstance(saved, dict) or saved.get("candidate_revision") != item["revision"]:
            continue
        if (entry.get("tenant_id") != item["tenant_id"] or entry.get("draft_id") != item["id"]
                or entry.get("id") != saved.get("event_id")):
            raise ValueError("migrationsplan_nachweis_ungueltig")
        return verify_saved_plan(item, saved, entry["actor"])
    raise ValueError("migrationsplan_fuer_diese_revision_fehlt")


def published_plan_valid(record, proof):
    try:
        saved = proof["migration_plan"]
        candidate = {**record, "status": "review", "revision": proof["candidate_revision"]}
        if saved["tenant_id"] != record["tenant_id"]:
            return False
        expected = verify_saved_plan(candidate, {key:value for key,value in saved.items() if key not in {"actor","tenant_id"}}, saved["actor"])
        return saved == expected
    except (ValueError, KeyError, TypeError):
        return False
