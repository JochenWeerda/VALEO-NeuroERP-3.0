"""Consent Engine — REST API (NC-004)."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.consent_engine import check_consent, grant_consent, revoke_consent, get_consent_status

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.base import CompatFlexOut


router = APIRouter(prefix="/neuro/consent", tags=["neuro-core", "consent", "dsgvo"])


class ConsentCheckRequest(BaseModel):
    entity_id: str
    consent_type: str


class ConsentGrantRequest(BaseModel):
    entity_id: str
    consent_type: str
    purpose: str = Field("", description="Zweckbindung")


class ConsentRevokeRequest(BaseModel):
    entity_id: str
    consent_type: str


@router.post("/check", summary="Check do",
    response_model=CompatFlexOut
)
async def do_check(req: ConsentCheckRequest, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    return check_consent(req.entity_id, req.consent_type, tenant_id, db)


@router.post("/grant", summary="Grant do",
    response_model=CompatFlexOut
)
async def do_grant(req: ConsentGrantRequest, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    return grant_consent(req.entity_id, req.consent_type, req.purpose, tenant_id, db)


@router.post("/revoke", summary="Revoke do",
    response_model=CompatFlexOut
)
async def do_revoke(req: ConsentRevokeRequest, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    return revoke_consent(req.entity_id, req.consent_type, tenant_id, db)


@router.get("/{entity_id}", summary="Status abrufen",
    response_model=CompatFlexOut
)
async def get_status(entity_id: str, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    return {"entity_id": entity_id, "consents": get_consent_status(entity_id, tenant_id, db)}
