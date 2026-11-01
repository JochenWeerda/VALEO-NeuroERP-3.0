"""Canonical tenant-bound CRM activity resources and versioned commands."""
from __future__ import annotations
from typing import Literal
from fastapi import APIRouter, Depends, Header, HTTPException, Query, Response
from pydantic import AliasChoices, BaseModel, Field
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.auth.bereich_roles import SCHREIBEN
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.domains.crm.activity_contracts import ActivityRead, ActivityCreateCommand, ActivityUpdateCommand, ActivityDeleteCommand
from app.infrastructure.models import Activity
from app.services.crm_activity_service import activity_or_404, execute_activity, read_activity, preview_activity
from app.api.v1.schemas.base import PaginatedResponse

router=APIRouter()


class ActivityCommandResult(BaseModel):
    actionKey: str
    mode: Literal["execute","dryRun","validate","propose"] = "execute"
    success: bool
    activity_id: str | None = None
    activity: ActivityRead | None = None
    auditEntryId: str | None = None
    version: int | None = None
    replayed: bool = False
    proposedChanges: list[dict] | None = None


class ActivityCreateAction(ActivityCreateCommand):
    mode: Literal["execute","dryRun","validate","propose"] = Field(default="execute",validation_alias=AliasChoices("mode","_mode"))


class ActivityUpdateAction(ActivityUpdateCommand):
    mode: Literal["execute","dryRun","validate","propose"] = Field(default="execute",validation_alias=AliasChoices("mode","_mode"))


class ActivityDeleteAction(ActivityDeleteCommand):
    mode: Literal["execute","dryRun","validate","propose"] = Field(default="execute",validation_alias=AliasChoices("mode","_mode"))


def _action(db,tenant,action,envelope,entity=None):
    cls={"create":ActivityCreateCommand,"update":ActivityUpdateCommand,"delete":ActivityDeleteCommand}[action]
    command=cls.model_validate(envelope.model_dump(exclude={"mode"},exclude_unset=action=="update"))
    if envelope.mode!="execute":
        proposed=preview_activity(db,tenant,action,command,entity)
        return {"actionKey":action,"mode":envelope.mode,"success":True,"proposedChanges":[proposed]}
    return {**execute_activity(db,tenant,action,command,entity),"actionKey":action}


@router.get("",response_model=PaginatedResponse[ActivityRead],summary="Aktivitaeten auflisten")
def list_activities(type_filter:str|None=Query(None,alias="type"),status_filter:str|None=Query(None,alias="status"),
                    search:str|None=Query(None,max_length=200),contact_id:str|None=Query(None,max_length=64),
                    skip:int=Query(0,ge=0),limit:int=Query(100,ge=1,le=200),
                    db:Session=Depends(get_db),tenant_id:str=Depends(get_tenant_id)) -> PaginatedResponse[ActivityRead]:
    conditions=[Activity.tenant_id==tenant_id]
    if type_filter is not None:conditions.append(Activity.type==type_filter)
    if status_filter is not None:conditions.append(Activity.status==status_filter)
    if contact_id is not None:conditions.append(Activity.contact_id==contact_id)
    if search:
        term="%"+search+"%"
        conditions.append(or_(Activity.title.ilike(term),Activity.customer.ilike(term),Activity.contact_person.ilike(term),Activity.assigned_to.ilike(term)))
    total=db.execute(select(func.count()).select_from(Activity).where(*conditions)).scalar_one()
    rows=db.execute(select(Activity).where(*conditions).order_by(Activity.date.desc().nullslast(),Activity.id).offset(skip).limit(limit)).scalars()
    return PaginatedResponse(items=[read_activity(row) for row in rows],total=total,page=skip//limit+1,size=limit,
                             pages=(total+limit-1)//limit,has_next=skip+limit<total,has_prev=skip>0)


@router.get("/{activity_id}",response_model=ActivityRead,summary="Aktivitaet abrufen")
def get_activity(activity_id:str,response:Response,db:Session=Depends(get_db),tenant_id:str=Depends(get_tenant_id)) -> ActivityRead:
    result=read_activity(activity_or_404(db,tenant_id,activity_id))
    response.headers["ETag"]='"'+str(result.version)+'"'
    return result


@router.post("",response_model=ActivityRead,status_code=201,summary="Aktivitaet anlegen",dependencies=SCHREIBEN["CRM"])
def create_activity(payload:ActivityCreateCommand,db:Session=Depends(get_db),tenant_id:str=Depends(get_tenant_id)) -> ActivityRead:
    return ActivityRead.model_validate(execute_activity(db,tenant_id,"create",payload)["activity"])


@router.put("/{activity_id}",response_model=ActivityRead,summary="Aktivitaet aendern",dependencies=SCHREIBEN["CRM"])
def update_activity(activity_id:str,payload:ActivityUpdateCommand,db:Session=Depends(get_db),tenant_id:str=Depends(get_tenant_id)) -> ActivityRead:
    return ActivityRead.model_validate(execute_activity(db,tenant_id,"update",payload,activity_id)["activity"])


@router.delete("/{activity_id}",status_code=204,response_model=None,summary="Aktivitaet loeschen",dependencies=SCHREIBEN["CRM"])
def delete_activity(activity_id:str,
                    if_match:str|None=Header(None,alias="If-Match",pattern=r'^"[1-9][0-9]{0,9}"$'),
                    idempotency_key:str=Header(...,alias="Idempotency-Key",min_length=1,max_length=200),
                    db:Session=Depends(get_db),tenant_id:str=Depends(get_tenant_id)) -> None:
    if if_match is None:raise HTTPException(428,"If-Match is required for activity deletion")
    command=ActivityDeleteCommand(expected_version=int(if_match[1:-1]),idempotency_key=idempotency_key)
    try:execute_activity(db,tenant_id,"delete",command,activity_id)
    except HTTPException as error:
        if error.status_code==409 and error.detail=="Activity version changed; reload before editing":
            raise HTTPException(412,"Activity precondition failed; reload before deleting") from error
        raise


@router.post("/actions/create",response_model=ActivityCommandResult,summary="Aktivitaet erstellen v1",dependencies=SCHREIBEN["CRM"])
def create_activity_action(payload:ActivityCreateAction,db:Session=Depends(get_db),tenant_id:str=Depends(get_tenant_id)) -> ActivityCommandResult:
    return ActivityCommandResult.model_validate(_action(db,tenant_id,"create",payload))


@router.post("/{activity_id}/actions/update",response_model=ActivityCommandResult,summary="Aktivitaet bearbeiten v1",dependencies=SCHREIBEN["CRM"])
def update_activity_action(activity_id:str,payload:ActivityUpdateAction,db:Session=Depends(get_db),tenant_id:str=Depends(get_tenant_id)) -> ActivityCommandResult:
    return ActivityCommandResult.model_validate(_action(db,tenant_id,"update",payload,activity_id))


@router.post("/{activity_id}/actions/delete",response_model=ActivityCommandResult,summary="Aktivitaet entfernen v1",dependencies=SCHREIBEN["CRM"])
def delete_activity_action(activity_id:str,payload:ActivityDeleteAction,db:Session=Depends(get_db),tenant_id:str=Depends(get_tenant_id)) -> ActivityCommandResult:
    return ActivityCommandResult.model_validate(_action(db,tenant_id,"delete",payload,activity_id))


# Child reads remain available; writes update the aggregate atomically with a version and idempotency key.
_COLLECTIONS={"main-topics":"main_topics","orders-placed":"orders_placed","follow-up-actions":"follow_up_actions"}


def _collection(collection):
    if collection not in _COLLECTIONS:raise HTTPException(404,"Activity collection not found")
    return _COLLECTIONS[collection]


@router.get("/{activity_id}/{collection}",response_model=list[str],summary="Aktivitaeten-Unterliste lesen")
def list_collection(activity_id:str,collection:Literal["main-topics","orders-placed","follow-up-actions"],
                    db:Session=Depends(get_db),tenant_id:str=Depends(get_tenant_id)) -> list[str]:
    return getattr(activity_or_404(db,tenant_id,activity_id),_collection(collection))
