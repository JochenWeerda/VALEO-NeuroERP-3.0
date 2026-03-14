from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator


DeductionType = Literal["drying", "cleaning", "freight", "other"]
DeductionMode = Literal["per_ton", "fixed"]


class DeductionInput(BaseModel):
    deduction_type: DeductionType
    mode: DeductionMode
    rate_per_ton_eur: float | None = Field(default=None, ge=0)
    fixed_amount_eur: float | None = Field(default=None, ge=0)
    basis_quantity_tons: float | None = Field(default=None, ge=0)
    note: str | None = None

    @model_validator(mode="after")
    def validate_mode_fields(self):
        if self.mode == "per_ton" and self.rate_per_ton_eur is None:
            raise ValueError("rate_per_ton_eur is required for mode=per_ton")
        if self.mode == "fixed" and self.fixed_amount_eur is None:
            raise ValueError("fixed_amount_eur is required for mode=fixed")
        return self
