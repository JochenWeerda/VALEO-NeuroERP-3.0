"""Atomic tenant/user/agent budgets and a technical token consumption ledger.

Budgets are immutable allocations. Children consume an allocation of their parent,
not additional capacity. Provider calls must reserve before spending.
"""
from __future__ import annotations
import hashlib
import json
import time
from uuid import uuid4
from fastapi import HTTPException
from app.core.identity_context import current_identity
from app.core import identity_session
from app.core.identity_control_store import human, storage_boundary

PREFIX = 'valeo:identity:quota:v1:'
MAX_DEPTH = 3

# A single document and stream per tenant keep all invariants in one Redis script.
_MUTATE = r"""
local raw=redis.call('GET',KEYS[1])
local data=raw and cjson.decode(raw) or {budgets={},reservations={}}
local req=cjson.decode(ARGV[1])
local event=nil
if req.op=='root' then
 if next(data.budgets) then return {'conflict'} end
 data.budgets[req.id]={id=req.id,owner=req.owner,kind='tenant',limit=req.tokens,
  max_children=req.children,children=0,allocated=0,reserved=0,spent=0,total_spent=0,depth=0,parent=''}
 event='budget_created'
elseif req.op=='allocate' then
 local prior=data.budgets[req.id]
 if prior then
  if prior.owner~=req.owner or prior.kind~=req.kind or prior.limit~=req.tokens or prior.max_children~=req.children or prior.parent~=req.parent or prior.created_by~=req.actor or (not req.dry_run and (prior.allocation_reason or '')~=req.reason) then return {'conflict'} end
  return {'ok',cjson.encode(prior)}
 end
 local p=data.budgets[req.parent]
 if not p then return {'missing'} end
 if not req.admin and p.owner~=req.actor then return {'forbidden'} end
 if p.depth>=tonumber(ARGV[2]) then return {'depth'} end
 if p.children>=p.max_children or req.tokens>p.limit-p.allocated-p.reserved-p.spent then return {'exhausted'} end
 p.allocated=p.allocated+req.tokens; p.children=p.children+1
 data.budgets[req.id]={id=req.id,owner=req.owner,kind=req.kind,limit=req.tokens,
  max_children=req.children,children=0,allocated=0,reserved=0,spent=0,total_spent=0,depth=p.depth+1,parent=req.parent,created_by=req.actor,allocation_reason=req.reason}
 event='budget_allocated'
elseif req.op=='reserve' then
 local p=data.budgets[req.budget]
 if not p then return {'missing'} end
 if p.owner~=req.actor then return {'forbidden'} end
 local prior=data.reservations[req.id]
 if prior then
  if prior.budget~=req.budget or prior.tokens~=req.tokens or prior.job~=req.job then return {'conflict'} end
  return {'ok',cjson.encode(prior)}
 end
 if req.tokens>p.limit-p.allocated-p.reserved-p.spent then return {'exhausted'} end
 p.reserved=p.reserved+req.tokens
 data.reservations[req.id]={id=req.id,budget=req.budget,tokens=req.tokens,job=req.job,
  actor=req.actor,status='reserved',at=req.at}
 event='tokens_reserved'
elseif req.op=='settle' then
 local r=data.reservations[req.id]
 if not r then return {'missing'} end
 if r.actor~=req.actor then return {'forbidden'} end
 if r.status~='reserved' then
  if r.actual~=req.actual or r.outcome~=req.outcome then return {'conflict'} end
  return {'ok',cjson.encode(r)}
 end
 if req.actual>r.tokens then return {'overrun'} end
 local p=data.budgets[r.budget]
 p.reserved=p.reserved-r.tokens; p.spent=p.spent+req.actual
 local cursor=p
 while cursor do
  cursor.total_spent=cursor.total_spent+req.actual
  cursor=data.budgets[cursor.parent]
 end
 r.status='settled'; r.actual=req.actual; r.outcome=req.outcome; r.settled_at=req.at
 req.budget=r.budget; req.tokens=r.tokens; req.job=r.job
 event='tokens_settled'
end
if not event then return {'invalid'} end
if req.dry_run then
 if req.op=='reserve' or req.op=='settle' then return {'ok',cjson.encode(data.reservations[req.id])} end
 return {'ok',cjson.encode(data.budgets[req.id])}
end
redis.call('SET',KEYS[1],cjson.encode(data))
redis.call('XADD',KEYS[2],'*','event',event,'actor',req.actor,'at',tostring(req.at),'detail',cjson.encode(req))
if req.op=='reserve' or req.op=='settle' then return {'ok',cjson.encode(data.reservations[req.id])} end
return {'ok',cjson.encode(data.budgets[req.id])}
"""


def locations(tenant: str) -> tuple[str,str]:
    tag=hashlib.sha256(tenant.encode()).hexdigest()
    return PREFIX+'{'+tag+'}:state', PREFIX+'{'+tag+'}:ledger'


def amount(value: int, *, positive: bool=False) -> int:
    # Lua/cjson uses doubles: keep counters below the exact integer limit.
    if isinstance(value,bool) or not isinstance(value,int) or not (int(positive)<=value<=10**12):
        raise HTTPException(422,'Kontingente erfordern ganze, begrenzte Mengen')
    return value


@storage_boundary
def mutate(request: dict) -> dict:
    principal=current_identity()
    request.update(actor=principal.subject,at=time.time())
    response=identity_session.store().eval(_MUTATE,2,*locations(principal.tenant_id),
                                            json.dumps(request),MAX_DEPTH)
    code=response[0].decode() if isinstance(response[0],bytes) else response[0]
    if code!='ok':
        statuses={'missing':404,'forbidden':403,'conflict':409,'exhausted':429,'depth':409,'overrun':409}
        messages={'exhausted':'Kontingent ausgeschöpft','overrun':'Verbrauch überschreitet Reservierung',
                  'conflict':'Wiederholung widerspricht dem gespeicherten Vorgang','depth':'Delegationstiefe erreicht'}
        raise HTTPException(statuses.get(code,422),messages.get(code,'Kontingentvorgang nicht zulässig'))
    return json.loads(response[1])


def create_root(tokens: int, max_children: int, *, dry_run: bool=False, reason: str='') -> dict:
    if amount(max_children)>1000: raise HTTPException(422,'Maximal 1000 direkte Unterkontingente')
    principal=human()
    if 'platform:quota:manage' not in principal.scopes:
        raise HTTPException(403,'Plattformfreigabe für das Mandantenkontingent erforderlich')
    return mutate(dict(op='root',id=uuid4().hex,owner=principal.subject,
                       tokens=amount(tokens,positive=True),children=amount(max_children),dry_run=dry_run,reason=reason))


def allocate(parent: str, owner: str, kind: str, tokens: int, max_children: int, request_id: str, *, dry_run: bool=False, reason: str='') -> dict:
    if amount(max_children)>1000: raise HTTPException(422,'Maximal 1000 direkte Unterkontingente')
    principal=current_identity()
    service=principal.claims.get('identity_type')=='service'
    if service:
        if kind!='agent' or 'agent:delegate' not in principal.scopes:
            raise HTTPException(403,'Agent darf nur autorisierte Unteragenten begrenzen')
    elif principal.claims.get('identity_type')!='human':
        raise HTTPException(403,'Verifizierte Identitätsart erforderlich')
    elif 'admin' not in principal.roles and 'identity:quota:allocate' not in principal.scopes:
        raise HTTPException(403,'Kontingentvergaberecht erforderlich')
    if kind not in ('user','agent') or not owner.strip() or len(owner)>200:
        raise HTTPException(422,'Ungültiger Kontingentempfänger')
    if not request_id or len(request_id)>200: raise HTTPException(422,'Wiederholungsschlüssel erforderlich')
    identifier=hashlib.sha256(json.dumps([principal.issuer,principal.tenant_id,principal.subject,request_id]).encode()).hexdigest()
    return mutate(dict(op='allocate',id=identifier,parent=parent,owner=owner,kind=kind,
        tokens=amount(tokens,positive=True),children=amount(max_children),
        admin=not service and 'admin' in principal.roles,dry_run=dry_run,reason=reason))


def reserve(budget: str, request_id: str, job: str, tokens: int) -> dict:
    if not request_id or len(request_id)>200 or not job or len(job)>200:
        raise HTTPException(422,'Auftrag und Wiederholungsschlüssel erforderlich')
    return mutate(dict(op='reserve',id=request_id,budget=budget,job=job,tokens=amount(tokens,positive=True)))


def settle(request_id: str, actual_tokens: int, outcome: str) -> dict:
    if outcome not in ('completed','failed','cancelled'):
        raise HTTPException(422,'Ungültiger Abschlussstatus')
    return mutate(dict(op='settle',id=request_id,actual=amount(actual_tokens),outcome=outcome))


@storage_boundary
def overview() -> list[dict]:
    principal=current_identity()
    raw=identity_session.store().get(locations(principal.tenant_id)[0])
    if raw is None: return []
    data=json.loads(raw)
    administrative=principal.claims.get('identity_type')=='human' and 'admin' in principal.roles
    return [dict(row,available=row['limit']-row['allocated']-row['reserved']-row['spent'])
            for row in data['budgets'].values() if administrative or row['owner']==principal.subject]


@storage_boundary
def ledger(*, before: str='+', limit: int=50) -> list[dict]:
    principal=human(administrative=True)
    if not 1<=limit<=100: raise HTTPException(422,'Maximal 100 Verbrauchseinträge je Seite')
    rows=identity_session.store().xrevrange(locations(principal.tenant_id)[1],max=before,count=limit)
    result=[]
    for identifier,fields in rows:
        decoded={(k.decode() if isinstance(k,bytes) else k):(v.decode() if isinstance(v,bytes) else v)
                 for k,v in fields.items()}
        detail=json.loads(decoded['detail'])
        result.append(dict(tokens=detail.get('tokens'),actual_tokens=detail.get('actual'),
                           job=detail.get('job'),budget_id=detail.get('budget',detail.get('id')),reason=detail.get('reason',''),
                           id=identifier.decode() if isinstance(identifier,bytes) else identifier,
                           event=decoded['event'],actor=decoded['actor'],at=float(decoded['at']),
                           detail=detail))
    return result
