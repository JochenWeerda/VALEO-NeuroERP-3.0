"""A bounded mask-source read; identity is supplied only by the verified request."""
from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator


class MaskTableFilter(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, allow_inf_nan=False)
    op: Literal["eq", "neq", "contains", "lt", "lte", "gt", "gte", "in", "between"]
    value: str | int | float | bool | None | list[str | int | float | bool | None]

    label: str | None = Field(default=None, max_length=200)

    @model_validator(mode="after")
    def valid_shape(self):
        if self.op == "between" and (not isinstance(self.value, list) or len(self.value) != 2):
            raise ValueError("between_requires_two_bounds")
        if self.op == "in" and (not isinstance(self.value, list) or len(self.value) > 100):
            raise ValueError("in_requires_bounded_values")
        if self.op not in {"in", "between"} and isinstance(self.value, list):
            raise ValueError("scalar_filter_required")
        values = self.value if isinstance(self.value, list) else [self.value]
        if any(isinstance(value, str) and len(value) > 200 for value in values):
            raise ValueError("filter_value_too_long")
        return self


class MaskDataReadIn(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, allow_inf_nan=False)
    screen_id: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9_/-]{0,120}$")
    source_key: str = Field(pattern=r"^[A-Za-z][A-Za-z0-9_-]{0,63}$")
    entity_id: str | None = Field(default=None, pattern=r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,119}$")
    page: int = Field(default=1, ge=1, le=1000000)
    limit: int = Field(default=50, ge=1, le=100)
    q: str | None = Field(default=None, max_length=200)
    table_key: str | None = Field(default=None, pattern=r"^[A-Za-z][A-Za-z0-9_-]{0,63}$")
    sort: str | None = Field(default=None, pattern=r"^[A-Za-z][A-Za-z0-9_.-]{0,100}$")
    sort_dir: Literal["asc", "desc"] = "asc"
    complete: bool = False
    preset_filters: dict[str, str] = Field(default_factory=dict, max_length=8)
    filter_plan: dict[str, MaskTableFilter] = Field(default_factory=dict, max_length=20)

    @model_validator(mode="after")
    def table_contract_required(self):
        if any(not key or len(key) > 200 or not value or len(value) > 200 for key, value in self.preset_filters.items()):
            raise ValueError("invalid_preset_selection")
        if self.complete and self.page != 1:
            raise ValueError("complete_read_requires_first_page")
        if not self.table_key and (self.sort or self.filter_plan or self.preset_filters or self.complete):
            raise ValueError("table_key_required_for_sort_and_filters")
        return self


class MaskDataReadOut(BaseModel):
    screen_id: str
    source_key: str
    page: int
    limit: int
    data: dict[str, Any] | list[Any]
