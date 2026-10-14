"""Canonical bounded data-quality request shared by REST and MCP."""
from typing import Any
from pydantic import BaseModel, ConfigDict, Field, field_validator


class DataQualityCheckIn(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, str_strip_whitespace=True)
    entity_typ: str = Field(min_length=1)
    datensatz: dict[str, Any] = Field(max_length=50)
    # FastAPI omits null defaults in OpenAPI. Export the same schema from MCP;
    # keep default comparisons strict for values that affect execution.
    kontext_datensaetze: list[dict[str, Any]] | None = Field(
        default=None, max_length=100, json_schema_extra=lambda schema: schema.pop("default", None)
    )

    @field_validator("datensatz")
    @classmethod
    def bounded_strings(cls, value):
        if any(isinstance(item, str) and len(item) > 1000 for item in value.values()):
            raise ValueError("Dataset string exceeds maximum length")
        return value
