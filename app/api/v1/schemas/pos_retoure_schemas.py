"""Pydantic schemas for the pos retoure domain."""
from __future__ import annotations

from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict as _ConfigDict


class PosRetourOut(BaseSchema):
    model_config = _ConfigDict(extra="allow")


class RetourRequest(BaseModel):
    original_bon_nr: Optional[str] = None
    kassierer: str
    positionen: List[RetourPosition]
    zahlungsrueckerstattung: str = "bar"  # bar | ec | gift_card
    gesamt: float
    tenant_id: Optional[str] = None


class RetourResponse(BaseModel):
    retoure_id: str
    retoure_bon_nr: str
    gesamt: float
    status: str
    message: str

