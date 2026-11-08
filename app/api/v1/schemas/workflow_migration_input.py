"""Explicit, deterministic input for workflow migration checks."""
import hashlib
import json

from pydantic import BaseModel, ConfigDict, Field, model_validator


class WorkflowMigrationStepIn(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, str_strip_whitespace=True)
    schritt_id: str = Field(min_length=1)
    pflicht: bool = True
    reihenfolge: int = Field(default=0, ge=0)
    terminal: bool = False
    rolle: str = ""
    schema_version: int = Field(default=1, ge=1)


class WorkflowMigrationCheckIn(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, str_strip_whitespace=True)
    prozess_key: str = Field(min_length=1)
    von_version: str = Field(min_length=1)
    zu_version: str = Field(min_length=1)
    alt_schema_version: int = Field(default=1, ge=1)
    neu_schema_version: int = Field(default=1, ge=1)
    alt_schritte: list[WorkflowMigrationStepIn] = Field(min_length=1)
    # An empty target is a real deletion, not a reason to replace it with demo data.
    neu_schritte: list[WorkflowMigrationStepIn]

    @model_validator(mode="after")
    def unique_steps(self):
        for steps in (self.alt_schritte, self.neu_schritte):
            if len({step.schritt_id for step in steps}) != len(steps):
                raise ValueError("Duplicate workflow step IDs")
        return self

    def comparison_revision(self) -> str:
        content = json.dumps(self.model_dump(mode="json"), sort_keys=True,
                             separators=(",", ":"), ensure_ascii=False, allow_nan=False)
        return hashlib.sha256(content.encode("utf-8")).hexdigest()
