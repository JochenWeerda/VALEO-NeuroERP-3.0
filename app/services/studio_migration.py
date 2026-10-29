"""Studio migration compiler: catalog wiring and reviewable additive Alembic artifacts.

Compilation never connects to a database, registers a command, or activates a mask.
"""
from copy import deepcopy
import ast
import hashlib
import json
from pathlib import Path

from app.api.v1.schemas.studio_migration import StudioMigrationIn, StudioMigrationOut
from app.core.studio_release import definition_hash
from app.core.screen_definitions import SCREEN_DEFINITION_BUILDERS
from app.services.studio_validation import load_studio_catalog, validate_studio_draft, _iter_actions

ROOT = Path(__file__).resolve().parents[2]
_TYPES = {"text": "sa.Text()", "integer": "sa.Integer()", "boolean": "sa.Boolean()",
          "date": "sa.Date()", "datetime": "sa.DateTime(timezone=True)",
          "decimal": "sa.Numeric(18, 4)", "uuid": "sa.Uuid()"}


def _hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=False, allow_nan=False).encode()).hexdigest()


def _nodes(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _nodes(child)
    elif isinstance(value, list):
        for child in value:
            yield from _nodes(child)


def _head():
    """Inspect literal revision metadata only; never execute migration modules."""
    revisions, parents = set(), set()
    for path in (ROOT / "alembic/versions").glob("*.py"):
        for node in ast.parse(path.read_text(encoding="utf-8-sig")).body:
            if not isinstance(node, (ast.Assign, ast.AnnAssign)):
                continue
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for target in targets:
                if not isinstance(target, ast.Name) or target.id not in {"revision", "down_revision"}:
                    continue
                value = ast.literal_eval(node.value)
                if target.id == "revision":
                    revisions.add(value)
                elif isinstance(value, str):
                    parents.add(value)
                elif isinstance(value, (tuple, list)):
                    parents.update(value)
    heads = revisions - parents
    if len(heads) != 1:
        raise ValueError("schema_migration_requires_single_alembic_head")
    return heads.pop()


def _schema_artifact(changes, schemas, plan_hash, head):
    operations = []
    seen = set()
    for change in changes:
        target = (change.schema_name, change.table)
        if target in seen:
            raise ValueError("duplicate_schema_target")
        seen.add(target)
        if change.schema_name not in schemas:
            raise ValueError("schema_not_in_canonical_catalog")
        existing = schemas[change.schema_name]["tables"].get(change.table)
        if change.operation == "create_table":
            if existing:
                raise ValueError("table_already_exists")
            columns = ["sa.Column('tenant_id', sa.String(), sa.ForeignKey('domain_shared.tenants.id'), nullable=False)",
                       "sa.Column('id', sa.Uuid(), nullable=False)",
                       "sa.Column('version', sa.Integer(), nullable=False)",
                       "sa.Column('created_by', sa.Text(), nullable=False)",
                       "sa.Column('created_at', sa.DateTime(timezone=True), nullable=False)"]
            columns.extend(f"sa.Column({c.name!r}, {_TYPES[c.type]}, nullable={c.nullable})" for c in change.columns)
            columns.append("sa.PrimaryKeyConstraint('tenant_id', 'id')")
            operations.append(f"    op.create_table({change.table!r}, " + ", ".join(columns) + f", schema={change.schema_name!r})")
        else:
            if not existing:
                raise ValueError("table_not_in_canonical_catalog")
            known = {column["name"] for column in existing["columns"]}
            if "tenant_id" not in known:
                raise ValueError("schema_extension_requires_tenant_owned_table")
            for column in change.columns:
                if column.name in known:
                    raise ValueError("column_already_exists")
                operations.append(f"    op.add_column({change.table!r}, sa.Column({column.name!r}, {_TYPES[column.type]}, nullable=True), schema={change.schema_name!r})")
    revision = "studio_" + plan_hash[:24]
    source = ('"""Studio additive schema proposal; requires reviewed deployment and isolation tests."""\n'
              'from alembic import op\nimport sqlalchemy as sa\n\n'
              f'revision = {revision!r}\ndown_revision = {head!r}\nbranch_labels = None\ndepends_on = None\n\n'
              'def upgrade():\n' + '\n'.join(operations) + '\n\n'
              'def downgrade():\n    raise RuntimeError("Studio schema rollback requires a reviewed compensating migration")\n')
    compile(source, revision + ".py", "exec")
    return revision + ".py", source


def plan_migration(body: StudioMigrationIn, tenant_id: str, actor: str) -> StudioMigrationOut:
    if not tenant_id or not actor:
        raise ValueError("verified_tenant_and_actor_required")
    catalog = load_studio_catalog()
    definition = deepcopy(body.definition)
    bindings = []
    sources = {source["key"]: source for source in catalog["data_sources"]}
    for node in _nodes(definition):
        for source in node.get("dataSources", []) if isinstance(node.get("dataSources"), list) else []:
            if isinstance(source, dict) and source.get("key") in sources and "endpoint" not in source:
                source["endpoint"] = sources[source["key"]]["endpoint"]
                bindings.append("data_source:" + source["key"])
    for action in _iter_actions(definition):
        if not isinstance(action, dict) or action.get("key") not in catalog["actions"]:
            continue
        approved = catalog["actions"][action["key"]]
        # Fill absent values only. Conflicting or weakened policy remains visible to validation.
        for key in ("commandEndpoint", "dangerLevel", "forbiddenForAgents"):
            if key not in action and key in approved:
                action[key] = approved[key]
                bindings.append("action:" + action["key"] + ":" + key)
        if "requiresConfirmation" not in action:
            action["requiresConfirmation"] = approved["dangerLevel"] != "safe"
    blockers = validate_studio_draft(definition, native_screen_ids=set(SCREEN_DEFINITION_BUILDERS))
    schemas = json.loads((ROOT / "docs/admin/table-catalog.json").read_text(encoding="utf-8"))["schemas"]
    catalog_hash = _hash({"version": catalog["version"], "sources": catalog["data_sources"], "actions": catalog["command_actions"]})
    schema_hash = _hash({key: {table: {"columns": data["columns"], "primary_key": data.get("primary_key"),
                                    "foreign_keys": data.get("foreign_keys")} for table, data in value["tables"].items()}
                         for key, value in schemas.items()})
    head = _head() if body.schema_changes else None
    generator_hash = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    digest = _hash({"version": 1, "generator_hash": generator_hash, "tenant": tenant_id, "actor": actor, "definition": definition,
                    "catalog_hash": catalog_hash, "schema_catalog_hash": schema_hash, "head": head,
                    "schema_changes": [change.model_dump() for change in body.schema_changes]})
    filename, source = _schema_artifact(body.schema_changes, schemas, digest, head) if body.schema_changes else (None, None)
    if body.schema_changes:
        blockers.extend(["schema_artifact_requires_reviewed_deployment", "schema_commands_and_tenant_isolation_tests_required"])
    blockers.extend(["studio_revision_simulation_and_independent_release_required",
                     "human_cli_mcp_role_tenant_and_replay_contract_tests_required"])
    return StudioMigrationOut(tenant_id=tenant_id, actor=actor, plan_hash=digest,
        definition_hash=definition_hash(definition), catalog_hash=catalog_hash, schema_catalog_hash=schema_hash,
        definition=definition, bindings=bindings, blockers=sorted(set(blockers)),
        migration_filename=filename, migration_source=source,
        migration_hash=hashlib.sha256(source.encode()).hexdigest() if source else None)
