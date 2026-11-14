"""Price-free, version-bound position selection for canonical conversions."""
from pydantic import BaseModel, ConfigDict, Field


class ConversionItem(BaseModel):
    model_config = ConfigDict(extra="forbid")
    source_item_id: str
    line_number: int
    article_number: str
    description: str | None = None
    unit: str | None = None
    quantity: float = Field(ge=0, allow_inf_nan=False)
    remaining_quantity: float = Field(ge=0, allow_inf_nan=False)


class ConversionOptions(BaseModel):
    model_config = ConfigDict(extra="forbid")
    source_doc_id: str
    source_doc_type: str
    target_doc_type: str
    version: int = Field(ge=1)
    items: list[ConversionItem]
