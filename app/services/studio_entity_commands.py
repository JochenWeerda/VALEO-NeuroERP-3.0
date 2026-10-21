"""Generated domain-command implementation. Only deployment-owned EntitySpec selects tables."""
import json
from datetime import datetime, timezone
from uuid import UUID, uuid4
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from fastapi import HTTPException
from pydantic import ValidationError
from app.core.studio_release import definition_hash
from app.infrastructure.eventbus.outbox import OutboxEvent
from app.services.studio_entity_contracts import EntitySpec, EntityCommand, POLICIES


def tables(spec: EntitySpec):
    metadata = sa.MetaData()
    schema = POLICIES[spec.domain][0]
    sa.Table('tenants', metadata, sa.Column('id', sa.String, primary_key=True), schema='domain_shared')
    types = {'text': sa.Text, 'integer': sa.Integer, 'boolean': sa.Boolean,
             'date': sa.Date, 'datetime': lambda: sa.DateTime(timezone=True),
             'decimal': lambda: sa.Numeric(18, 4), 'uuid': sa.Uuid}
    rows = sa.Table(spec.name, metadata,
        sa.Column('tenant_id', sa.String, sa.ForeignKey('domain_shared.tenants.id'), primary_key=True),
        sa.Column('id', sa.Uuid, primary_key=True),
        sa.Column('version', sa.Integer, nullable=False),
        sa.Column('deleted', sa.Boolean, nullable=False),
        sa.Column('created_by', sa.Text, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        *(sa.Column(c.name, types[c.type](), nullable=c.nullable) for c in spec.columns), schema=schema)
    events = sa.Table(spec.name + '_events', metadata,
        sa.Column('tenant_id', sa.String, sa.ForeignKey('domain_shared.tenants.id'), primary_key=True),
        sa.Column('id', sa.Uuid, primary_key=True),
        sa.Column('actor', sa.Text, nullable=False),
        sa.Column('request_hash', sa.String(64), nullable=False),
        sa.Column('result', JSONB, nullable=False),
        sa.Column('audit', JSONB, nullable=False),
        sa.Column('recorded_at', sa.DateTime(timezone=True), nullable=False), schema=schema)
    return rows, events


def public_row(row):
    return json.loads(json.dumps(dict(row), default=str, allow_nan=False))


def execute(session, spec, operation, tenant, actor, body: EntityCommand, entity_id=None, *, actor_kind='human'):
    """Caller supplies trusted context. Router applies existing roles before this command.

    No commit here: row, immutable receipt and outbox share the caller transaction.
    Rejected operations roll back their own savepoint and never partially mutate.
    """
    if not tenant or not actor or actor_kind not in {'human', 'agent'}:
        raise HTTPException(401, 'verified_identity_required')
    if operation not in {'create', 'update', 'delete'}:
        raise HTTPException(422, 'unknown_domain_command')
    try:
        key = UUID(body.idempotency_key)
        identifier = UUID(str(entity_id)) if entity_id else None
        if operation == 'create':
            if identifier or body.expected_version is not None:
                raise ValueError('create_identity_is_server_owned')
        elif not identifier or body.expected_version is None:
            raise ValueError('expected_version_required')
        if operation == 'delete':
            if body.data: raise ValueError('delete_payload_forbidden')
            values = {}
        else:
            values = spec.payload_model().model_validate_json(json.dumps(body.data, allow_nan=False)).model_dump()
    except (ValidationError, ValueError, TypeError) as error:
        raise HTTPException(422, 'invalid_entity_command') from error
    rows, events = tables(spec)
    fingerprint = definition_hash({'contract': spec.model_dump(), 'operation': operation,
        'entity_id': str(identifier) if identifier else None, 'actor': actor, 'actor_kind': actor_kind,
        'version': body.expected_version, 'data': body.data, 'reason': body.audit_reason})
    with session.begin_nested():
        session.execute(sa.text('SELECT pg_advisory_xact_lock(hashtextextended(:key, 0))'),
                        {'key': tenant + ':' + spec.name + ':' + str(key)})
        receipt = session.execute(sa.select(events).where(events.c.tenant_id == tenant, events.c.id == key)).mappings().first()
        if receipt:
            if receipt['actor'] != actor or receipt['request_hash'] != fingerprint:
                raise HTTPException(409, 'idempotency_conflict')
            return receipt['result']
        before = None
        if operation != 'create':
            before = session.execute(sa.select(rows).where(rows.c.tenant_id == tenant,
                rows.c.id == identifier, rows.c.deleted.is_(False)).with_for_update()).mappings().first()
            if before is None: raise HTTPException(404, 'entity_not_found')
            if before['version'] != body.expected_version: raise HTTPException(409, 'version_conflict')
        if body.mode != 'execute':
            return {'validated': True, 'persisted': False, 'mode': body.mode}
        now = datetime.now(timezone.utc)
        if operation == 'create':
            identifier = uuid4()
            result = session.execute(rows.insert().values(**values, tenant_id=tenant, id=identifier,
                version=1, deleted=False, created_by=actor, created_at=now).returning(rows)).mappings().one()
        else:
            result = session.execute(rows.update().where(rows.c.tenant_id == tenant, rows.c.id == identifier,
                rows.c.version == body.expected_version).values(**values, version=body.expected_version + 1,
                deleted=operation == 'delete').returning(rows)).mappings().one()
        result = public_row(result)
        event_id = str(uuid4())
        payload = {'event_id': event_id, 'tenant_id': tenant, 'actor': actor, 'actor_kind': actor_kind,
            'agent_id': actor if actor_kind == 'agent' else None,
            'command': f'{spec.name}.{operation}.v1', 'correlation_id': str(key),
            'reason': body.audit_reason, 'before': public_row(before) if before else None, 'after': result}
        session.execute(events.insert().values(tenant_id=tenant, id=key, actor=actor,
            request_hash=fingerprint, result=result, audit=payload, recorded_at=now))
        session.add(OutboxEvent(id=event_id, event_type='StudioEntityChanged', aggregate_id=str(identifier),
            tenant_id=tenant, payload=json.dumps(payload, allow_nan=False), timestamp=now.replace(tzinfo=None), published=False))
        session.flush()
        return result


def read(session, spec, tenant, entity_id=None, *, limit=50, offset=0):
    if not tenant: raise HTTPException(401, 'verified_tenant_required')
    if not 1 <= limit <= 100 or not 0 <= offset <= 1000000:
        raise HTTPException(422, 'invalid_pagination')
    rows, _ = tables(spec)
    query = sa.select(rows).where(rows.c.tenant_id == tenant, rows.c.deleted.is_(False))
    if entity_id is not None:
        row = session.execute(query.where(rows.c.id == UUID(str(entity_id)))).mappings().first()
        if row is None: raise HTTPException(404, 'entity_not_found')
        return public_row(row)
    return [public_row(row) for row in session.execute(query.order_by(rows.c.id).limit(limit).offset(offset)).mappings()]
