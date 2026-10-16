"""Versioned input and read-only output for document screen provenance."""
from pydantic import BaseModel, ConfigDict, Field


class DocflowScreenContextIn(BaseModel):
    model_config = ConfigDict(extra='forbid')
    screen_id: str = Field(min_length=1, max_length=160)
    definition_hash: str = Field(pattern=r'^[0-9a-f]{64}$')


class DocflowScreenContextOut(DocflowScreenContextIn):
    document_variant: dict[str, str] | None = None
    studio_release: dict[str, str] | None = None
