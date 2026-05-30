"""Pydantic schemas for the knowledge api domain."""
from __future__ import annotations

from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict as _ConfigDict


class KnowledgeOut(BaseSchema):
    model_config = _ConfigDict(extra="allow")


class KnowledgeObjectCreate(BaseModel):
    titel: str
    typ: str
    beschreibung: str = ""
    tags: list[str] = []
    zielrollen: list[str] = []
    agentenfreigabe: bool = True
    initiale_version: str = ""
    format: str = "MARKDOWN"


class KnowledgeObjectUpdate(BaseModel):
    titel: Optional[str] = None
    beschreibung: Optional[str] = None
    tags: Optional[list[str]] = None
    zielrollen: Optional[list[str]] = None
    status: Optional[str] = None
    agentenfreigabe: Optional[bool] = None


class KnowledgeVersionCreate(BaseModel):
    inhalt: str
    format: str = "MARKDOWN"
    quelle: str = "api"


class KnowledgeObjectResponse(BaseModel):
    knowledge_id: str
    titel: str
    typ: str
    status: str
    beschreibung: str
    tags: list[str]
    zielrollen: list[str]
    agentenfreigabe: bool
    created_at: str
    updated_at: str
    versionen_count: int
    aktuelle_version: Optional[int]
    vorschau: str


class KnowledgeStatsResponse(BaseModel):
    gesamt: int
    nach_typ: dict[str, int]
    nach_status: dict[str, int]
    nach_format: dict[str, int]
    agentenfreigabe_aktiv: int

