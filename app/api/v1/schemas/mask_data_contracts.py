"""A bounded mask-source read; identity is supplied only by the verified request."""
from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class MaskDataReadIn(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    screen_id: str = Field(pattern=r"^[a-z0-9][a-z0-9_/-]{0,120}$")
    source_key: str = Field(pattern=r"^[A-Za-z][A-Za-z0-9_-]{0,63}$")
    entity_id: str | None = Field(default=None, pattern=r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,119}$")
    page: int = Field(default=1, ge=1, le=1000000)
    limit: int = Field(default=50, ge=1, le=100)
    q: str | None = Field(default=None, max_length=200)


class MaskDataReadOut(BaseModel):
    screen_id: str
    source_key: str
    page: int
    limit: int
    data: dict[str, Any] | list[Any]
