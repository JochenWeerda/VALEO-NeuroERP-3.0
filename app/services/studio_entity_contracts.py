"""Compile-time contracts for new Studio-owned master data, never existing ledgers."""
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator, create_model
from app.api.v1.schemas.studio_migration import StudioColumnIn
from app.auth import bereich_roles

POLICIES = {'crm': ('domain_crm', bereich_roles.CRM),
            'agrar': ('domain_agrar', bereich_roles.AGRAR),
            'inventory': ('domain_inventory', bereich_roles.LAGER)}
RESERVED = {'id', 'tenant_id', 'version', 'created_by', 'created_at', 'deleted',
            'mode', 'idempotency_key', 'audit_reason', 'expected_version', 'data'}


class EntityColumn(StudioColumnIn):
    label: str | None = Field(None, min_length=1, max_length=100)


class EntitySpec(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    version: Literal[1] = 1
    name: str = Field(pattern=r'^studio_[a-z][a-z0-9_]{0,27}$')
    domain: Literal['crm', 'agrar', 'inventory']
    label: str = Field(min_length=1, max_length=100)
    columns: list[EntityColumn] = Field(min_length=1, max_length=30)

    @model_validator(mode='after')
    def fields_unique(self):
        names = [column.name for column in self.columns]
        if len(names) != len(set(names)) or set(names) & RESERVED:
            raise ValueError('duplicate_or_reserved_field')
        return self

    def payload_model(self):
        from datetime import date
        from decimal import Decimal
        from uuid import UUID
        from typing import Annotated
        from pydantic import AwareDatetime
        types = {'text': Annotated[str, Field(max_length=4096)],
                 'integer': Annotated[int, Field(ge=-2147483648, le=2147483647)],
                 'boolean': bool, 'date': date, 'datetime': AwareDatetime,
                 'decimal': Annotated[Decimal, Field(max_digits=18, decimal_places=4)], 'uuid': UUID}
        return create_model(self.name + '_v1', __config__=ConfigDict(extra='forbid', strict=True),
            **{column.name: (types[column.type] | None, None) if column.nullable
               else (Annotated[str, Field(min_length=1, max_length=4096, pattern=r'\S')]
                     if column.type == 'text' else types[column.type], ...) for column in self.columns})

    def flat_command_model(self):
        """The native action dialog sends fields flat; OpenAPI declares that shape too."""
        from copy import deepcopy
        fields = {name: (field.annotation, deepcopy(field))
                  for name, field in self.payload_model().model_fields.items()}
        fields.update({name: (field.annotation, deepcopy(field)) for name, field in EntityCommand.model_fields.items()
                       if name != 'data'})
        return create_model(self.name + '_command_v1', __config__=ConfigDict(extra='forbid'), **fields)


def normalized_command(body):
    if isinstance(body, EntityCommand): return body
    raw = body.model_dump(by_alias=True, mode='json')
    controls = {key: raw.pop(key) for key in ('_mode', '_idempotencyKey', '_auditReason', 'expected_version')}
    return EntityCommand.model_validate({**controls, 'data': raw})


class EntityCommand(BaseModel):
    model_config = ConfigDict(extra='forbid', populate_by_name=False)
    mode: Literal['execute', 'dryRun', 'validate', 'propose'] = Field('execute', alias='_mode')
    idempotency_key: str = Field(alias='_idempotencyKey', pattern=r'^[0-9a-fA-F-]{36}$')
    audit_reason: str = Field(alias='_auditReason', min_length=3, max_length=500, pattern=r'\S')
    expected_version: int | None = Field(None, ge=1, strict=True)
    data: dict = Field(default_factory=dict)


class EntityRegistration(BaseModel):
    """Trusted deployment configuration in the existing Studio catalog; never request input."""
    model_config = ConfigDict(extra='forbid', strict=True)
    spec: EntitySpec
    writes_enabled: bool = False
    agent_roles: list[str] = Field(default_factory=list, max_length=20)

    @model_validator(mode='after')
    def existing_domain_roles(self):
        if set(self.agent_roles) - set(POLICIES[self.spec.domain][1]):
            raise ValueError('agent_role_not_in_existing_domain_policy')
        return self


def registrations(data):
    entries = [EntityRegistration.model_validate(item) for item in data.get('generated_entities', [])]
    names = [entry.spec.name for entry in entries]
    targets = [(POLICIES[entry.spec.domain][0], table) for entry in entries
               for table in (entry.spec.name, entry.spec.name + '_events')]
    if len(names) > 64 or len(names) != len(set(names)) or len(targets) != len(set(targets)):
        raise ValueError('duplicate_or_excessive_generated_entities')
    return entries


def contract_hash(spec):
    from pathlib import Path
    from hashlib import sha256
    from app.core.studio_release import definition_hash
    root = Path(__file__).parent
    return definition_hash({'spec': spec.model_dump(), 'runtime': {
        name: sha256((root / name).read_bytes().replace(b'\r\n', b'\n')).hexdigest() for name in (
            'studio_entity_contracts.py', 'studio_entity_commands.py', 'studio_entity_router.py')}})


class EntityBundleOut(BaseModel):
    version: Literal[1]
    contract_hash: str
    spec: EntitySpec
    files: dict[str, str]
    file_hashes: dict[str, str]
    required_checks: list[str]
    enabled: Literal[False]


def response_models(spec):
    """REST and exported artifacts share the exact generated business-field schemas."""
    from datetime import datetime
    from uuid import UUID
    from copy import deepcopy
    fields = {name: (field.annotation, deepcopy(field))
              for name, field in spec.payload_model().model_fields.items()}
    fields.update({'id':(UUID,...),'tenant_id':(str,...),'version':(int,...),
                   'deleted':(bool,...),'created_by':(str,...),'created_at':(datetime,...)})
    row = create_model(spec.name + '_record_v1', __config__=ConfigDict(extra='forbid'), **fields)
    page = create_model(spec.name + '_page_v1',items=(list[row],...),total=(int,...),limit=(int,...),skip=(int,...))
    preview = create_model(spec.name + '_preview_v1',validated=(Literal[True],...),
                           persisted=(Literal[False],...),mode=(Literal['dryRun','validate','propose'],...))
    result = create_model(spec.name + '_result_v1',success=(Literal[True],...),actionKey=(str,...),
                          mode=(Literal['execute','dryRun','validate','propose'],...),result=(row | preview,...))
    return row, page, result


class EntityExtensionIn(BaseModel):
    """Only the trusted registration supplies the previous schema and permissions."""
    model_config = ConfigDict(extra='forbid', strict=True)
    name: str = Field(pattern=r'^studio_[a-z][a-z0-9_]{0,27}$')
    expected_contract_hash: str = Field(pattern=r'^[0-9a-f]{64}$')
    columns: list[EntityColumn] = Field(min_length=1, max_length=30)


class EntityExtensionOut(BaseModel):
    base_contract_hash: str
    bundle: EntityBundleOut
