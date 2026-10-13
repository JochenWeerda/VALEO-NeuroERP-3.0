"""Tenant lifecycle with explicit platform authority and journal preservation."""
from fastapi import Response, APIRouter, Depends, Query
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.tenant_lifecycle_service import TenantLifecycleService
from app.api.v1.schemas.shared import TenantCreate, TenantUpdate, Tenant
from app.api.v1.schemas.base import PaginatedResponse

router=APIRouter(tags=['tenants'],dependencies=[Depends(get_tenant_id)])


class LifecycleReason(BaseModel):
    model_config=ConfigDict(extra='forbid')
    reason: str=Field(min_length=3,max_length=500)


@router.post('/',response_model=Tenant,status_code=201,summary='Mandanten mit Plattformberechtigung anlegen')
def create_tenant(payload: TenantCreate,db: Session=Depends(get_db)) -> Tenant:
    return Tenant.model_validate(TenantLifecycleService(db).create(payload.model_dump()))


@router.get('/',response_model=PaginatedResponse[Tenant],summary='Berechtigte Mandanten auflisten')
def list_tenants(skip: int=Query(0,ge=0),limit: int=Query(100,ge=1,le=100),db: Session=Depends(get_db)) -> PaginatedResponse[Tenant]:
    rows,total=TenantLifecycleService(db).list(skip,limit)
    return PaginatedResponse[Tenant](items=[Tenant.model_validate(row) for row in rows],total=total,
        page=skip//limit+1,size=limit,pages=(total+limit-1)//limit,has_next=skip+limit<total,has_prev=skip>0)


# target_id is an administrative object selector, not an active tenant switch.
# Cross-tenant access requires the explicit platform scope in the service.
@router.get('/{target_id}',response_model=Tenant,summary='Eigenen oder ausdrücklich administrierten Mandanten abrufen')
def get_tenant(target_id: str,db: Session=Depends(get_db)) -> Tenant:
    return Tenant.model_validate(TenantLifecycleService(db).get(target_id))


@router.put('/{target_id}',response_model=Tenant,summary='Mandantenstammdaten administrieren')
def update_tenant(target_id: str,payload: TenantUpdate,db: Session=Depends(get_db)) -> Tenant:
    return Tenant.model_validate(TenantLifecycleService(db).update(target_id,payload.model_dump(exclude_unset=True)))


@router.post('/{target_id}/block',response_model=Tenant,summary='Mandanten unter Erhalt sämtlicher Buchungen sperren')
def block_tenant(target_id: str,payload: LifecycleReason,db: Session=Depends(get_db)) -> Tenant:
    return Tenant.model_validate(TenantLifecycleService(db).block(target_id,payload.reason))


@router.delete('/{target_id}',status_code=204,response_class=Response,response_model=None,
               summary='Mandanten ausschließlich ohne Buchungen und geschützte Referenzen löschen')
def delete_tenant(target_id: str,payload: LifecycleReason,db: Session=Depends(get_db)) -> Response:
    TenantLifecycleService(db).delete(target_id,payload.reason)
    return Response(status_code=204)
