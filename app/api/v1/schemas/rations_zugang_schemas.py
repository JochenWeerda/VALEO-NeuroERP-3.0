"""Pydantic schemas for the rations zugang domain."""
from __future__ import annotations

from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.api.v1.schemas.base import BaseSchema


class ZugangCreate(ZugangBase):
    pass


class ZugangOut(BaseModel):
    id: str
    tenant_id: str
    empfaenger_email: str
    empfaenger_name: Optional[str]
    zugang_typ: str
    gueltig_ab: Optional[datetime]
    gueltig_bis: Optional[datetime]
    darf_lesen: bool
    darf_rationen_anlegen: bool
    darf_grundfutter_anlegen: bool
    darf_zugang_verwalten: bool
    ist_aktiv: bool
    gesperrt_am: Optional[datetime]
    gesperrt_durch: Optional[str]
    sperrgrund: Optional[str]
    erstellt_von_email: str
    erstellt_von_name: Optional[str]
    notizen: Optional[str]
    created_at: Optional[datetime]
    share_token: Optional[str] = None  # nur beim Erstellen eines share_link-Eintrags

    model_config = ConfigDict(from_attributes=True)


class ShareLinkCreate(BaseModel):
    empfaenger_name: Optional[str] = None
    gueltig_bis: Optional[datetime] = None
    notizen: Optional[str] = None


class ShareLinkOut(BaseModel):
    id: str
    share_token: str
    share_url_suffix: str  # /portal/rations/share/{token}
    gueltig_bis: Optional[datetime]

