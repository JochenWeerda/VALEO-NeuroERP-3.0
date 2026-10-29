"""Bounded metadata for the registered Flow Spine catalog cockpit."""
from typing import Literal

from pydantic import BaseModel, ConfigDict, StrictBool, ValidationError


class FlowSpineCatalog(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    enabled: Literal[True]
    warmWorkspaces: StrictBool


def validate_flow_spine_catalog(definition: dict) -> list[str]:
    if "flowSpineCatalog" not in definition:
        return []
    try:
        metadata = definition["flowSpineCatalog"]
        if not isinstance(metadata, dict) or metadata.get("enabled") is not True:
            return ["flow_spine_katalog_ungueltig"]
        FlowSpineCatalog.model_validate(metadata)
    except (ValidationError, TypeError, ValueError):
        return ["flow_spine_katalog_ungueltig"]
    if definition.get("id") != "workflow/flow-spine-studio" or definition.get("mode") != "cockpit":
        return ["flow_spine_katalog_maske_ungueltig"]
    return []
