"""Reviewable additive evolution from trusted registered Studio master-data contracts."""
from sqlalchemy.schema import CreateColumn
from sqlalchemy.dialects import postgresql
from app.services.studio_entity_contracts import EntityExtensionIn, EntitySpec, contract_hash, registrations, POLICIES
from app.services.studio_entity_compiler import compile_entity
from app.services.studio_entity_commands import tables
from app.services.studio_migration import _head


def compile_extension(body: EntityExtensionIn):
    """Never apply SQL or accept a caller-asserted old schema. Writes stay disabled."""
    import yaml
    from app.services.studio_validation import _CONFIG_PATH
    entries = registrations(yaml.safe_load(_CONFIG_PATH.read_text(encoding='utf-8')) or {})
    entry = next((item for item in entries if item.spec.name == body.name), None)
    if entry is None:
        raise ValueError('registered_studio_entity_required')
    old = entry.spec
    base = contract_hash(old)
    if body.expected_contract_hash != base:
        raise ValueError('entity_base_contract_changed')
    if any(not column.nullable for column in body.columns):
        raise ValueError('existing_rows_require_nullable_additions')
    # EntitySpec checks duplicates, reserved fields and the total column budget.
    new = EntitySpec.model_validate({**old.model_dump(),
        'columns': [column.model_dump() for column in old.columns + body.columns]})
    bundle = compile_entity(new, catalog_only=True)
    schema = POLICIES[old.domain][0]
    row, event = tables(new)
    targets = [f'"{schema}"."{table.name}"' for table in (row, event)]
    statements = ['LOCK TABLE ' + ', '.join(targets) + ' IN ACCESS EXCLUSIVE MODE']
    for target in targets:
        statements.append("DO $$ BEGIN IF obj_description('" + target + "'::regclass, 'pg_class') IS DISTINCT FROM 'studio-entity:" + base + "' THEN RAISE EXCEPTION 'studio_entity_base_deployment_changed'; END IF; END; $$")
    for column in body.columns:
        definition = str(CreateColumn(row.c[column.name]).compile(dialect=postgresql.dialect()))
        statements.append(f'ALTER TABLE {targets[0]} ADD COLUMN {definition}')
    for target in targets:
        statements.append(f"COMMENT ON TABLE {target} IS 'studio-entity:{bundle['contract_hash']}'")
    migration = ('"""Generated additive Studio entity evolution; reviewed deployment required."""\n'
        'from alembic import op\n\n' + f"revision = {('studio_entity_' + bundle['contract_hash'][:18])!r}\n"
        + f'down_revision = {_head()!r}\nbranch_labels = None\ndepends_on = None\n\n'
        + 'def upgrade():\n' + ''.join(f'    op.execute({statement!r})\n' for statement in statements)
        + '\ndef downgrade():\n    raise RuntimeError("reviewed_compensating_migration_required")\n')
    compile(migration, 'migration.py', 'exec')
    bundle['files']['migration.py'] = migration
    from app.core.studio_release import definition_hash
    bundle['file_hashes']['migration.py'] = definition_hash(migration)
    return {'base_contract_hash': base, 'bundle': bundle}
