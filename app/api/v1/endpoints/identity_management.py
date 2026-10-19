"""Server-side session management in the shared identity boundary."""
from fastapi import APIRouter, Depends, Request, Response
from pydantic import BaseModel, Field
from app.auth.deps import get_current_user, require_roles
from app.core import identity_session
from app.auth.bereich_roles import SCHREIBEN  # Schreibrecht je Bereich (WRITE-ROLES)

router=APIRouter(prefix='/identity',tags=['identity'])


class SessionOut(BaseModel):
    subject: str
    tenant_id: str
    idle_seconds: int
    absolute_seconds: int


class RevokeSubject(BaseModel):
    subject: str = Field(min_length=1,max_length=200)


@router.get('/session',response_model=SessionOut,summary='Aktuelle verifizierte Sitzung')
def current_session(request: Request,user: dict=Depends(get_current_user)) -> SessionOut:
    return SessionOut(subject=user['sub'],tenant_id=request.state.tenant_id,
        idle_seconds=identity_session.settings.IDENTITY_SESSION_IDLE_SECONDS,
        absolute_seconds=identity_session.settings.IDENTITY_SESSION_MAX_SECONDS)


@router.post('/session/logout',status_code=204,response_class=Response,response_model=None,summary='Aktuelle Sitzung serverseitig widerrufen', dependencies=SCHREIBEN["PLATTFORM"])
def logout(request: Request,user: dict=Depends(get_current_user)) -> Response:
    identity_session.revoke_session(request.state.token_claims,request.state.authenticated_token)
    return Response(status_code=204)


@router.post('/subjects/revoke',status_code=204,response_class=Response,response_model=None,
             summary='Vorhandene Sitzungen eines Mandantenbenutzers widerrufen',dependencies=[Depends(require_roles('admin'))])
def revoke_subject(payload: RevokeSubject, request: Request) -> Response:
    identity_session.revoke_subject(request.state.token_claims['iss'],request.state.tenant_id,payload.subject,
                                   actor=request.state.token_claims['sub'])
    return Response(status_code=204)


# Token quantities are technical capacity, not monetary accounting entries.
from datetime import datetime
from typing import Literal
from pydantic import ConfigDict
from app.core import identity_quota
from app.core.identity_control_store import human


class BudgetCreate(BaseModel):
    model_config = ConfigDict(extra='forbid')
    tokens: int = Field(gt=0,le=10**12,strict=True)
    max_children: int = Field(ge=0,le=1000,strict=True)


class BudgetAllocate(BudgetCreate):
    request_id: str = Field(min_length=1,max_length=200)
    parent: str = Field(min_length=1,max_length=200)
    owner: str = Field(min_length=1,max_length=200)
    kind: Literal['user','agent']


class BudgetOut(BaseModel):
    id: str
    owner: str
    kind: str
    limit: int
    max_children: int
    children: int
    allocated: int
    reserved: int
    spent: int
    total_spent: int
    depth: int
    parent: str
    available: int | None = None


class LedgerOut(BaseModel):
    id: str
    event: str
    actor: str
    at: datetime
    tokens: int | None = None
    actual_tokens: int | None = None
    job: str | None = None
    budget_id: str | None = None
    reason: str = ''
    detail: dict


@router.get('/budgets',response_model=list[BudgetOut],summary='Wirksame Nutzer- und Agentenkontingente auflisten')
def budgets() -> list[dict]:
    return identity_quota.overview()


@router.post('/budgets/root',response_model=BudgetOut,status_code=201,
             summary='Mandantenkontingent mit ausdrücklicher Plattformberechtigung bereitstellen', dependencies=SCHREIBEN["PLATTFORM"])
def create_budget(payload: BudgetCreate) -> dict:
    return identity_quota.create_root(payload.tokens,payload.max_children)


@router.post('/budgets/allocate',response_model=BudgetOut,status_code=201,
             summary='Elternkontingent an Nutzer oder Agenten verteilen', dependencies=SCHREIBEN["PLATTFORM"])
def allocate_budget(payload: BudgetAllocate) -> dict:
    return identity_quota.allocate(**payload.model_dump())


@router.get('/consumption-ledger',response_model=list[LedgerOut],
             summary='Technisches Token-Verbrauchsnebenbuch des eigenen Mandanten abrufen')
def consumption_ledger(before: str='+', limit: int=50) -> list[dict]:
    return identity_quota.ledger(before=before,limit=limit)


from app.services.mask_action_runtime_service import MaskActionResult
from fastapi import HTTPException


class BudgetCommand(BudgetCreate):
    mode: Literal['execute','dryRun','validate','propose'] = Field(default='execute',alias='_mode')
    audit_reason: str | None = Field(default=None,alias='_auditReason',max_length=500)
    idempotency_key: str | None = Field(default=None,alias='_idempotencyKey',max_length=200)
    parent: str | None = Field(default=None,max_length=200)
    owner: str | None = Field(default=None,max_length=200)
    kind: Literal['user','agent'] | None = None
    request_id: str | None = Field(default=None,max_length=200)


@router.post('/budgets/actions/{action_key}',response_model=MaskActionResult,
             summary='Kontingentvergabe im Maskbuilder prüfen und kontrolliert ausführen', dependencies=SCHREIBEN["PLATTFORM"])
def budget_command(action_key: Literal['root','allocate'],payload: BudgetCommand) -> MaskActionResult:
    human()  # Interactive mask contract; service subdelegation uses the typed API.
    preview=payload.mode!='execute'
    if not preview and (not payload.audit_reason or len(payload.audit_reason.strip())<3):
        raise HTTPException(422,'Begründung für die Kontingentvergabe erforderlich')
    reason=(payload.audit_reason or '').strip()
    if action_key=='root':
        if any((payload.parent,payload.owner,payload.kind,payload.request_id)):
            raise HTTPException(422,'Mandantenbudget enthält keine Unterkontingentfelder')
        record=identity_quota.create_root(payload.tokens,payload.max_children,dry_run=preview,reason=reason)
    else:
        if not all((payload.parent,payload.owner,payload.kind,payload.request_id or payload.idempotency_key)):
            raise HTTPException(422,'Elternbudget, Empfänger, Art und Vergabereferenz erforderlich')
        record=identity_quota.allocate(payload.parent,payload.owner,payload.kind,payload.tokens,
            payload.max_children,payload.request_id or payload.idempotency_key,dry_run=preview,reason=reason)
    return MaskActionResult(actionKey=action_key,mode=payload.mode,success=True,
        summary='Kontingentvergabe geprüft.' if preview else 'Kontingent gespeichert.',
        proposedChanges=[{'description':f"{payload.tokens} Tokens; maximal {payload.max_children} direkte Unterkontingente."}] if preview else None,
        affectedIds=None if preview else [record['id']])
