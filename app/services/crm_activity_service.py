"""Canonical CRM activity commands v1; transports never own business writes."""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.auth.bereich_roles import CRM
from app.core.business_time import business_now
from app.core.identity_context import current_identity
from app.domains.crm.activity_contracts import ActivityCreateCommand, ActivityUpdateCommand, ActivityDeleteCommand, ActivityRead
from app.domains.shared.events import IntegrationEvent
from app.infrastructure.eventbus.outbox import OutboxEvent
from app.infrastructure.models import Activity
from app.services.mask_action_runtime_service import _write_audit

_CONTROL = {"idempotency_key", "audit_reason", "correlation_id", "expected_version"}
_READ = set(ActivityRead.model_fields)


def read_activity(row) -> ActivityRead:
    return ActivityRead.model_validate({key:getattr(row,key) for key in _READ})


def activity_or_404(db: Session, tenant: str, activity_id: str, *, lock=False):
    statement=select(Activity).where(Activity.id==activity_id,Activity.tenant_id==tenant)
    if lock:
        statement=statement.with_for_update().execution_options(populate_existing=True)
    row=db.execute(statement).scalar_one_or_none()
    if row is None:
        raise HTTPException(404,"Activity not found")
    return row


def _references(db, tenant, values):
    if values.get("customer_id") and values.get("opportunity_id"):
        raise HTTPException(422,"Customer and opportunity references require an authoritative shared customer mapping")
    for field, statement in (("customer_id", "SELECT company_name AS name FROM domain_crm.customers WHERE id=:id AND tenant_id=:tenant AND deleted_at IS NULL FOR SHARE"),
                             ("contact_id", "SELECT name FROM public.crm_contacts WHERE id=:id AND tenant_id=:tenant FOR SHARE")):
        reference=values.get(field)
        if reference:
            row=db.execute(text(statement),{"id":reference,"tenant":tenant}).mappings().first()
            if row is None:
                raise HTTPException(404,"Referenced CRM record not found")
            name=str(row["name"] or "")
            if len(name)>100:
                raise HTTPException(422,"Referenced CRM display name exceeds the activity contract")
            values["customer" if field=="customer_id" else "contact_person"]=name
    if values.get("opportunity_id"):
        from app.services.crm_opportunity_reference import require_opportunity_sync
        opportunity=require_opportunity_sync(db,values["opportunity_id"],tenant)
        name=opportunity.get("customer_name")
        if name is not None and not values.get("customer_id"):
            if len(str(name))>100:raise HTTPException(422,"Opportunity customer name exceeds the activity contract")
            values["customer"]=str(name)


def activity_principal(tenant, *, write=True):
    principal=current_identity()
    if principal.tenant_id != tenant:
        raise HTTPException(403,"Activity tenant disagrees with verified identity")
    if write and (principal.claims.get("identity_type") != "human" or principal.claims.get("act") or principal.claims.get("agent_id")):
        raise HTTPException(403,"Activity writes require an explicitly authorized human identity")
    if not principal.roles.intersection(CRM):
        raise HTTPException(403,"CRM write role required")
    return principal


def preview_activity(db,tenant,action,command,activity_id=None):
    activity_principal(tenant,write=False)
    values=command.model_dump(exclude_unset=action=="update",exclude=_CONTROL)
    if action!="create":
        row=activity_or_404(db,tenant,activity_id)
        if row.version!=command.expected_version:raise HTTPException(409,"Activity version changed; reload before editing")
        if action=="delete":return {"activity_id":row.id,"expected_version":row.version}
        references={field:values.get(field,getattr(row,field)) for field in ("customer_id","contact_id","opportunity_id")}
        _references(db,tenant,references)
        values.update({key:value for key,value in references.items() if key in {"customer","contact_person"}})
    else:
        _references(db,tenant,values)
        if not values["assigned_to"]:values["assigned_to"]=current_identity().subject
    return values


def execute_activity(db: Session, tenant: str, action: str, command, activity_id: str|None=None):
    """Authorize, lock/replay, validate, mutate and record outcome in one transaction."""
    principal=activity_principal(tenant)
    expected={"create":ActivityCreateCommand,"update":ActivityUpdateCommand,"delete":ActivityDeleteCommand}
    if action not in expected or not isinstance(command,expected[action]):
        raise HTTPException(422,"Invalid activity command")
    if (action=="create") != (activity_id is None):
        raise HTTPException(422,"Invalid activity command target")
    actor=principal.subject
    tool="crm.activity."+action+".v1"
    payload=command.model_dump(mode="json",exclude_unset=action=="update",exclude={"correlation_id"})
    fingerprint=hashlib.sha256(json.dumps([activity_id,payload],sort_keys=True,ensure_ascii=False).encode()).hexdigest()
    key=command.idempotency_key
    lock=int.from_bytes(hashlib.sha256(json.dumps([tenant,tool,key]).encode()).digest()[:8],"big",signed=True)
    try:
        db.execute(text("SELECT pg_advisory_xact_lock(:key)"),{"key":lock})
        previous=db.execute(text("SELECT actor_id,payload_hash,result FROM public.mcp_tool_executions WHERE tenant_id=:tenant AND tool_name=:tool AND idempotency_key=:key"),
                            {"tenant":tenant,"tool":tool,"key":key}).mappings().first()
        if previous:
            if previous["actor_id"]!=actor or previous["payload_hash"]!=fingerprint:
                raise HTTPException(409,"Idempotency key is bound to another activity command")
            result=previous["result"]
            if isinstance(result,str):result=json.loads(result)
            db.commit()
            return {**result,"replayed":True}
        now=business_now()
        values=command.model_dump(exclude_unset=action=="update",exclude=_CONTROL)
        before=None
        if action=="create":
            _references(db,tenant,values)
            if not values["assigned_to"]:values["assigned_to"]=actor
            row=Activity(id=str(uuid4()),tenant_id=tenant,version=1,created_at=now,updated_at=now,
                         created_by=actor,updated_by=actor,origin={},**values)
            db.add(row)
        else:
            row=activity_or_404(db,tenant,activity_id,lock=True)
            before=read_activity(row).model_dump(mode="json")
            if row.version!=command.expected_version:
                raise HTTPException(409,"Activity version changed; reload before editing")
            if action=="update":
                references={field:values.get(field,getattr(row,field)) for field in ("customer_id","contact_id","opportunity_id")}
                _references(db,tenant,references)
                values.update({key:value for key,value in references.items() if key in {"customer","contact_person"}})
                for field,value in values.items():setattr(row,field,value)
                row.version+=1;row.updated_at=now;row.updated_by=actor
        entity_id=row.id
        version=row.version if action!="delete" else row.version+1
        db.flush()
        output=read_activity(row).model_dump(mode="json")
        if action=="delete":db.delete(row)
        audit_id=_write_audit(db,tenant_id=tenant,action_key=tool,entity_type="crm_activity",entity_id=entity_id,
                             audit_reason=command.audit_reason,idempotency_key=key,summary="CRM activity "+action+" v"+str(version),performed_by=actor)
        correlation=command.correlation_id or str(uuid4())
        event=IntegrationEvent(aggregate_id=entity_id,timestamp=now,event_type=tool,tenant_id=tenant,
            payload={"activity_id":entity_id,"version":version,"actor_id":actor,"correlation_id":correlation,"audit_id":audit_id})
        db.add(OutboxEvent(id=event.event_id,event_type=event.event_type,aggregate_id=entity_id,tenant_id=tenant,
                          timestamp=now,payload=json.dumps(asdict(event),default=str),published=False))
        result={"success":True,"activity_id":entity_id,"activity":output,"auditEntryId":audit_id,"version":version,"previous_activity":before,"correlation_id":correlation,"event_id":event.event_id}
        db.execute(text("INSERT INTO public.mcp_tool_executions (tenant_id,tool_name,idempotency_key,actor_id,payload_hash,result) VALUES (:tenant,:tool,:key,:actor,:hash,CAST(:result AS jsonb))"),
            {"tenant":tenant,"tool":tool,"key":key,"actor":actor,"hash":fingerprint,"result":json.dumps(result)})
        db.commit()
        return result
    except HTTPException:
        db.rollback();raise
    except Exception as error:
        db.rollback()
        raise HTTPException(503,"Activity command failed; no changes confirmed") from error
