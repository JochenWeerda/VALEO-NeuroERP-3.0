"""Canonical advisory evaluations; results never grant command authorization."""
from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class PolicyEvaluationIn(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, str_strip_whitespace=True)
    prozess_key: str = Field(min_length=1)
    kontext: dict[str, Any]
    policy_set_id: str | None = Field(default=None, json_schema_extra=lambda schema: schema.pop("default", None))


class ApprovalEvaluationIn(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, str_strip_whitespace=True)
    aktions_typ: str = Field(min_length=1)
    kontext: dict[str, Any]
