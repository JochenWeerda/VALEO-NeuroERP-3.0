"""Explicit finite SLO measurement; null means unknown, omission is invalid."""
from pydantic import BaseModel, ConfigDict, Field
from fastapi import Request


class SloCheckIn(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, str_strip_whitespace=True, allow_inf_nan=False)
    slo_id: str = Field(min_length=1)
    ist_wert: float | None


async def reject_nonfinite_slo_json(request: Request):
    # JSON's nonstandard NaN/Infinity values must not enter validation errors:
    # serializing those raw error inputs can otherwise itself fail with 500.
    import math
    from json import JSONDecodeError
    from fastapi import HTTPException
    try:
        value = await request.json()
    except JSONDecodeError:
        return
    pending = [value]
    while pending:
        item = pending.pop()
        if isinstance(item, float) and not math.isfinite(item):
            raise HTTPException(422, "Non-finite JSON numbers are not allowed")
        if isinstance(item, dict): pending.extend(item.values())
        elif isinstance(item, list): pending.extend(item)
