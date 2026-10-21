"""One authenticated HTTP command adapter for generated master-data contracts."""
from uuid import UUID
from typing import Any, Union
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.auth.deps import require_roles
from app.services.studio_entity_contracts import EntitySpec, EntityCommand, POLICIES, normalized_command, contract_hash, response_models
from app.services.studio_entity_commands import execute, read


def build_router(spec: EntitySpec, *, writes_enabled=False, agent_roles=()):
    """Called from reviewed generated deployment code, never a caller-supplied target."""
    loaded_contract = contract_hash(spec)
    roles = POLICIES[spec.domain][1]
    if set(agent_roles) - set(roles): raise ValueError('agent_roles_must_use_domain_policy')
    read_roles = (*roles, *(role.replace('_BEARBEITEN', '_LESEN') for role in roles if role.endswith('_BEARBEITEN')))
    reader, writer = require_roles(*read_roles), require_roles(*roles)
    router = APIRouter(prefix='/entities/' + spec.name, tags=['studio-generated'])
    WriteBody = Union[EntityCommand, spec.flat_command_model()]
    RowOut, PageOut, CommandOut = response_models(spec)

    def deployment(db):
        from app.services.studio_entity_commands import verify_deployment
        verify_deployment(db, spec, expected_contract=loaded_contract)

    def actor(user):
        from fastapi import HTTPException
        subject = user.get('sub')
        if not isinstance(subject, str) or not subject.strip():
            raise HTTPException(401, 'verified_subject_required')
        return subject

    @router.get('', response_model=PageOut, summary='Generierte Stammdaten mandantengenau lesen')
    def collection(limit: int = Query(50, ge=1, le=100), skip: int = Query(0, ge=0, le=1000000),
                   tenant: str = Depends(get_tenant_id), user: dict = Depends(reader), db: Session = Depends(get_db)):
        actor(user)
        deployment(db)
        import sqlalchemy as sa
        from app.services.studio_entity_commands import tables
        rows, _ = tables(spec)
        total = db.scalar(sa.select(sa.func.count()).select_from(rows).where(
            rows.c.tenant_id == tenant, rows.c.deleted.is_(False)))
        return {'items': read(db, spec, tenant, limit=limit, offset=skip), 'total': total, 'limit': limit, 'skip': skip}

    @router.get('/{entity_id}', response_model=RowOut, summary='Generierten Stammdatensatz lesen')
    def detail(entity_id: UUID, tenant: str = Depends(get_tenant_id),
               user: dict = Depends(reader), db: Session = Depends(get_db)):
        actor(user)
        deployment(db)
        return read(db, spec, tenant, entity_id)

    def command(operation, body, tenant, user, db, entity_id=None):
        if not writes_enabled:
            from fastapi import HTTPException
            raise HTTPException(403, 'generated_capability_not_enabled')
        if (user.get('raw') or {}).get('identity_type') == 'agent':
            if not set(user.get('roles') or []) & set(agent_roles):
                from fastapi import HTTPException
                raise HTTPException(403, 'agent_capability_not_enabled_for_role')
        deployment(db)
        kind = 'agent' if (user.get('raw') or {}).get('identity_type') == 'agent' else 'human'
        result = execute(db, spec, operation, tenant, actor(user), normalized_command(body), entity_id, actor_kind=kind)
        db.commit()
        return {'success': True, 'actionKey': f'{spec.name}_{operation}', 'mode': body.mode, 'result': result}

    @router.post('/actions/create', response_model=CommandOut, summary='Generierten Stammdatensatz anlegen')
    def create(body: WriteBody, tenant: str = Depends(get_tenant_id),
               user: dict = Depends(writer), db: Session = Depends(get_db)):
        return command('create', body, tenant, user, db)

    @router.post('/{entity_id}/actions/update', response_model=CommandOut, summary='Generierten Stammdatensatz versioniert ersetzen')
    def update(entity_id: UUID, body: WriteBody, tenant: str = Depends(get_tenant_id),
               user: dict = Depends(writer), db: Session = Depends(get_db)):
        return command('update', body, tenant, user, db, entity_id)

    @router.post('/{entity_id}/actions/delete', response_model=CommandOut, summary='Generierten Stammdatensatz nachvollziehbar deaktivieren')
    def delete(entity_id: UUID, body: EntityCommand, tenant: str = Depends(get_tenant_id),
               user: dict = Depends(writer), db: Session = Depends(get_db)):
        return command('delete', body, tenant, user, db, entity_id)

    return router


def install_registered_entities(router):
    import yaml
    from app.services.studio_validation import _CONFIG_PATH
    from app.services.studio_entity_contracts import registrations
    data = yaml.safe_load(_CONFIG_PATH.read_text(encoding='utf-8')) or {}
    for entry in registrations(data):
        router.include_router(build_router(entry.spec, writes_enabled=entry.writes_enabled,
                                          agent_roles=entry.agent_roles))
