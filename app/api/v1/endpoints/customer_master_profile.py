"""Staff-only customer master profile and audited update command."""
from __future__ import annotations

import hashlib
import json
from typing import Any, Literal
from copy import deepcopy
from pydantic import ConfigDict, Field, create_model

from fastapi import APIRouter, Body, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.auth.bereich_roles import SCHREIBEN
from app.auth.deps import require_roles
from app.core.akteur import gepruefter_akteur_aus_request
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.core.customer_master_profile import master_catalog
from app.api.v1.schemas.crm import Customer as CustomerOut
from app.api.v1.endpoints import business_partners as partner_dto
from app.services.customer_master_profile_service import check_profile, read_profile, update_profile, validate_changes, field_specs
from app.services.mask_action_runtime_service import MaskActionResult, run_delegated_mask_action

router = APIRouter(tags=['customer-master-profile'])
read_role = require_roles('CRM_LESEN', 'CRM_BEARBEITEN', 'CRM_ADMIN', 'SALES_LESEN', 'SALES_BEARBEITEN', 'SALES_ADMIN', 'FINANCE_LESEN', 'FINANCE_BEARBEITEN', 'FINANCE_ADMIN', 'admin')

# Preserve the existing customer response and publish every added scalar's type.
CustomerMasterProfileOut = create_model(
    'CustomerMasterProfileOut', __base__=CustomerOut,
    version=(int | None, None),
    **{'partner_' + field['key']: (
        getattr(partner_dto, group['model']).model_fields[field['key']].annotation | None, None)
       for group in master_catalog()['groups'] for field in group['fields']
       if field['key'] in getattr(partner_dto, group['model']).model_fields},
)


def command_schema() -> dict[str, Any]:
    """Describe the same partial fields validated by the domain service, without
    exposing rejected bank values through Pydantic's default error rendering.
    """
    fields = {}
    for key, specification in field_specs().items():
        field = deepcopy(specification)
        field.default = None
        fields['partner_' + key] = (field.annotation, field)
    model = create_model(
        'CustomerMasterProfileCommandV1', __config__=ConfigDict(extra='forbid'),
        expected_version=(int, Field(..., ge=1, le=9007199254740991)),
        mode=(Literal['execute', 'dryRun', 'validate', 'propose'], Field('execute', alias='_mode')),
        reason=(str | None, Field(None, alias='_auditReason', pattern=r'\S')),
        idempotency=(str | None, Field(None, alias='_idempotencyKey', min_length=1, max_length=200, pattern=r'^\S(?:.*\S)?$')),
        **fields,
    )
    schema = model.model_json_schema(by_alias=True)
    schema['allOf'] = [{'if': {'properties': {'_mode': {'const': 'execute'}}},
                        'then': {'required': ['_idempotencyKey', '_auditReason']}}]
    return schema


@router.get('/crm/customers/{customer_id}/master-profile', summary='Interne Kundenstammdaten abrufen', response_model=CustomerMasterProfileOut, dependencies=[Depends(read_role)])
def customer_master_profile(customer_id: str, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)) -> dict[str, Any]:
    return read_profile(db, tenant_id, customer_id)


@router.post('/crm/customers/{customer_id}/master-profile/actions/bearbeiten', summary='Kundenstammdaten versionsgebunden pflegen', response_model=MaskActionResult, dependencies=SCHREIBEN['CRM'])
async def edit_customer_master_profile(customer_id: str, request: Request, body: dict[str, Any] = Body(..., json_schema_extra=command_schema()),
                                       db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)) -> MaskActionResult:
    actor = gepruefter_akteur_aus_request(request)
    execute = body.get('_mode', 'execute') == 'execute'
    key = body.get('_idempotencyKey')
    reason = body.get('_auditReason')
    if execute and (not isinstance(key, str) or not key.strip() or key != key.strip() or len(key) > 200):
        raise HTTPException(422, 'Ein gültiger Idempotenzschlüssel ist erforderlich.')
    if execute and (not isinstance(reason, str) or not reason.strip()):
        raise HTTPException(422, 'Eine Auditbegründung ist erforderlich.')
    payload = {k: v for k, v in body.items() if k not in {'_mode', '_auditReason', '_idempotencyKey'}}
    try:
        validate_changes(payload)
        canonical = json.dumps({'tenant': tenant_id, 'actor': actor, 'entity': customer_id,
                                'body': body}, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False)
    except (ValueError, TypeError) as exc:
        raise HTTPException(422, str(exc)) from exc
    fingerprint = hashlib.sha256(canonical.encode('utf-8')).hexdigest()

    def check(session: Session, values: dict, eid: str, tid: str) -> list[dict]:
        try:
            check_profile(session, values, eid, tid)
        except (ValueError, HTTPException) as exc:
            return [{'field': '_entity', 'message': str(getattr(exc, 'detail', exc)), 'severity': 'blocking'}]
        return []

    def update(session: Session, values: dict, eid: str, tid: str) -> str:
        return update_profile(session, values, eid, tid, actor=actor)

    return await run_delegated_mask_action(
        db, action_key='stammdaten_pflegen', entity_type='customer_master_profile', entity_id=customer_id,
        tenant_id=tenant_id, body=body, check_fn=check, delegate_fn=update,
        outbox_event_type='crm.customer.master_profile.updated', require_audit_reason=True,
        performed_by=actor, request_fingerprint=fingerprint)
