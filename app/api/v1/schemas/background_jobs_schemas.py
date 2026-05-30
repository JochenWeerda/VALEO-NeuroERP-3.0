"""Pydantic schemas for the background jobs domain."""
from __future__ import annotations

from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict as _ConfigDict


class BackgroundJobOut(BaseSchema):
    model_config = _ConfigDict(extra="allow")


class BackgroundJobEnqueueIn(BaseModel):
    typ: JobTyp
    angefordert_von: str = Field(min_length=1)
    parameter: dict[str, Any] = Field(default_factory=dict)
    prioritaet_override: JobPrioritaet | None = None
    tenant_id: str = Field(default="")


class BackgroundJobMutationIn(BaseModel):
    ergebnis_summary: str = ""
    fehler_meldung: str = ""

