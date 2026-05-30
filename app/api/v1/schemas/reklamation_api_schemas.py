"""Pydantic schemas for the reklamation api domain."""
from __future__ import annotations

from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict as _ConfigDict


class ReklamationOut(BaseSchema):
    """Typed response schema for ReklamationOut endpoints (extra fields forwarded)."""
    model_config = _ConfigDict(extra="allow")


class ReklamationsCRMReferenzRequest(BaseModel):
    crm_system: str
    crm_case_id: str
    crm_ticket_id: Optional[str] = None
    crm_status: Optional[str] = None
    crm_url: Optional[str] = None


class ReklamationsDMSReferenzRequest(BaseModel):
    dokument_id: str
    dokument_typ: Optional[str] = None
    dateiname: Optional[str] = None
    checksum: Optional[str] = None
    source_uri: Optional[str] = None


class ReklamationCreateRequest(BaseModel):
    tenant_id: str
    lieferant_id: str
    typ: str
    positionen: list[dict]
    zustaendiger: str
    frist_datum: str
    kontrakt_id: Optional[str] = None
    crm_referenz: Optional[ReklamationsCRMReferenzRequest] = None
    dms_referenzen: list[ReklamationsDMSReferenzRequest] = Field(default_factory=list)
    gobd_beleg_id: Optional[str] = None
    aktor_id: str = "system"


class ReklamationTransitionRequest(BaseModel):
    neuer_status: str
    aktor_id: str = "system"
    kommentar: Optional[str] = None


class ReklamationReferenzUpdateRequest(BaseModel):
    aktor_id: str = "system"
    crm_referenz: Optional[ReklamationsCRMReferenzRequest] = None
    dms_referenzen: list[ReklamationsDMSReferenzRequest] = Field(default_factory=list)

