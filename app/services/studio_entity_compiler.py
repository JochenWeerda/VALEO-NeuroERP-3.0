"""Deterministic deployable entity bundle. Does not execute DDL or activate writes."""
import json
from app.core.studio_release import definition_hash
from app.services.studio_entity_contracts import EntitySpec, contract_hash
from app.services.studio_entity_commands import tables
from app.services.studio_migration import _head


def compile_entity(spec: EntitySpec, *, catalog_only=False):
    from sqlalchemy.schema import CreateTable
    from sqlalchemy.dialects import postgresql
    spec_hash = contract_hash(spec)
    rows, events = tables(spec)
    schema = rows.schema
    from app.services.studio_migration import ROOT
    catalog = json.loads((ROOT / 'docs/admin/table-catalog.json').read_text(encoding='utf-8'))['schemas']
    if schema not in catalog:
        raise ValueError('schema_not_in_canonical_catalog')
    if not catalog_only and any(table.name in catalog[schema]['tables'] for table in (rows, events)):
        raise ValueError('existing_domain_table_must_use_its_domain_commands')
    ddl = [str(CreateTable(table).compile(dialect=postgresql.dialect())) for table in (rows, events)]
    ddl.extend(f'COMMENT ON TABLE "{schema}"."{table.name}" IS \'studio-entity:{spec_hash}\'' for table in (rows, events))
    # Receipts remain the immutable audit/replay source after outbox delivery/cleanup.
    function = f'"{schema}"."{spec.name}_immutable"'
    ddl.extend([
        f"CREATE FUNCTION {function}() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN RAISE EXCEPTION 'immutable_studio_history'; END; $$",
        f'CREATE TRIGGER immutable_history BEFORE UPDATE OR DELETE ON "{schema}"."{events.name}" FOR EACH ROW EXECUTE FUNCTION {function}()',
    ])
    source = ('"""Generated Studio master-data deployment. Review before applying."""\n'
        'from alembic import op\n\n' + f'revision = {("studio_entity_" + spec_hash[:18])!r}\n'
        + f'down_revision = {_head()!r}\nbranch_labels = None\ndepends_on = None\n\n'
        + 'def upgrade():\n' + ''.join(f'    op.execute({statement!r})\n' for statement in ddl)
        + '\ndef downgrade():\n    raise RuntimeError("reviewed_compensating_migration_required")\n')
    endpoint = '/api/v1/studio/entities/' + spec.name
    input_fields = [{'key': c.name, 'label': c.label or c.name,
        'type': 'text' if c.type in {'uuid', 'decimal'} else 'number' if c.type == 'integer' else c.type,
        'required': not c.nullable} for c in spec.columns]
    actions = []
    for operation, label in [('create', 'Anlegen'), ('update', 'Ändern'), ('delete', 'Deaktivieren')]:
        actions.append({'key': f'{spec.name}_{operation}', 'label': label,
            'commandEndpoint': endpoint + ('' if operation == 'create' else '/{entity_id}') + '/actions/' + operation,
            'dangerLevel': 'moderate', 'requiresConfirmation': True, 'auditReasonRequired': True,
            'forbiddenForAgents': True, 'disabled': True,
            'command': f'{spec.name}.{operation}.v1',
            'permission': f'studio.entity.{spec.domain}.write',
            'inputFields': input_fields if operation != 'delete' else []})
    screen_id = 'tenant/' + spec.name
    definition = {'schemaVersion': 1, 'id': screen_id, 'domain': spec.domain, 'mode': 'list', 'title': spec.label,
        'processSimulation': {'profile':'studio.entity.v1','entity':spec.name,'contractHash':spec_hash},
        'adapter': {'type': 'native', 'sourceId': screen_id, 'temporary': True},
        'layout': {'floorplan': 'worklist', 'density': 'compact', 'contextRail': 'audit',
                   'tableProfile': 'inventory' if spec.domain == 'inventory' else 'standard'},
        'dataSources': [{'key': spec.name, 'endpoint': endpoint, 'pageSize': 50}],
        'tables': [{'key': 'list', 'label': spec.label, 'dataSourceKey': spec.name, 'serverPagination': True,
                    'columns': [{'key': c.name, 'label': c.label or c.name, 'sortable':False, 'filterable':False,
                                 'numeric': c.type in {'integer','decimal'},
                                 'renderKind': 'number' if c.type in {'integer','decimal'} else 'text' if c.type == 'uuid' else c.type}
                                for c in spec.columns] + [
                        {'key':'version','label':'Version','sortable':False,'filterable':False},
                        {'key':'created_at','label':'Erstellt am','renderKind':'datetime','sortable':False,'filterable':False}],
                    'rowActions': actions[1:]}],
        'fields': [{'key': c.name, 'label': c.label or c.name, 'type': 'number' if c.type in {'integer','decimal'} else 'text' if c.type == 'uuid' else c.type,
                    'required': not c.nullable} for c in spec.columns], 'actions': actions[:1],
        'agentContract': {'schemaVersion': 1, 'domain': spec.domain, 'availableActions': actions,
                          'editableFields': [c.name for c in spec.columns]}}
    module = ('"""Generated entity router; include only after migration and acceptance."""\n'
        'from app.services.studio_entity_contracts import EntitySpec\n'
        'from app.services.studio_entity_router import build_router\n'
        f'router = build_router(EntitySpec.model_validate_json({spec.model_dump_json()!r}))\n')
    files = {'migration.py': source, 'router.py': module,
             'screen.json': json.dumps(definition, ensure_ascii=False, sort_keys=True, indent=2),
             'schema.json': json.dumps(spec.payload_model().model_json_schema(), sort_keys=True, indent=2),
             'command-schema.json': json.dumps(spec.flat_command_model().model_json_schema(), sort_keys=True, indent=2),
             'registration.json': json.dumps({'generated_entities':[{'spec':spec.model_dump(),'writes_enabled':False,'agent_roles':[]}]}, sort_keys=True, indent=2),
             'catalog.json': json.dumps({'data_sources': definition['dataSources'], 'command_actions': actions}, ensure_ascii=False, sort_keys=True, indent=2)}
    from fastapi import FastAPI
    from app.services.studio_entity_router import build_router
    api = FastAPI(); api.include_router(build_router(spec), prefix='/api/v1/studio')
    files['openapi.json'] = json.dumps(api.openapi(), ensure_ascii=False, sort_keys=True, indent=2)
    for name in ('migration.py', 'router.py'): compile(files[name], name, 'exec')
    return {'version': 1, 'contract_hash': spec_hash, 'spec': spec.model_dump(),
            'files': files, 'file_hashes': {name: definition_hash(text) for name, text in files.items()},
            'required_checks': ['migration', 'roles', 'two_tenants', 'replay', 'concurrency', 'rollback', 'ui_cli_mcp'],
            'enabled': False}


def registered_definition(entry):
    """Projection of reviewed deployment switches; authoring bundles remain disabled."""
    from app.services.studio_validation import _nodes
    definition = json.loads(compile_entity(entry.spec, catalog_only=True)['files']['screen.json'])
    for node in _nodes(definition):
        if node.get('command', '').startswith(entry.spec.name + '.'):
            node['disabled'] = not entry.writes_enabled
            node['forbiddenForAgents'] = not bool(entry.agent_roles)
    return definition
