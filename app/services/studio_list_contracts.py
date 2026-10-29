"""Bounded declarative list behavior; no commands or executable expressions."""
from typing import Annotated, Literal
from pydantic import AfterValidator, BaseModel, ConfigDict, Field, ValidationError, model_validator

Text = Annotated[str, Field(min_length=1, max_length=200)]

def _safe_key(value: str) -> str:
    if value.casefold() in {"__proto__", "prototype", "constructor"}:
        raise ValueError("reserved key")
    return value

Key = Annotated[Text, AfterValidator(_safe_key)]

class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, allow_inf_nan=False)

class Condition(Contract):
    field: Key
    op: Literal["eq", "neq"]
    value: Annotated[str, Field(max_length=200)]

class Aggregate(Contract):
    key: Key
    label: Text
    conditions: list[Condition] = Field(max_length=100)
    kind: Literal["count", "sum"] = "count"
    field: Key | None = None
    format: Literal["currency"] | None = None
    currencyField: Key | None = None

    @model_validator(mode="after")
    def aggregate_shape(self):
        if (self.kind == "sum") != (self.field is not None) or (self.format is not None and self.kind != "sum") or (self.currencyField is not None and self.kind != "sum"):
            raise ValueError("invalid aggregate shape")
        return self

class ExportColumn(Contract):
    key: Key
    label: Text

class Export(Contract):
    filenamePrefix: Text
    delimiter: Literal[";"]
    columns: list[ExportColumn] = Field(min_length=1, max_length=100)

class Resume(Contract):
    resumeNodeId: Text
    businessStatus: Text
    actionLabelPrefix: Text
    createScreen: Text
    detailScreen: Text

class Notice(Contract):
    aggregate: Key
    text: Text

class When(Contract):
    aggregate: Key
    op: Literal["gt"]
    value: int | float

class Variant(Contract):
    when: When | None = None
    text: Text

class Insight(Contract):
    label: Text
    variants: list[Variant] = Field(max_length=100)

class ListExperience(Contract):
    searchFields: list[Key] = Field(min_length=1, max_length=100)
    aggregates: list[Aggregate] = Field(max_length=100)
    export: Export
    workflowResume: Resume | None = None
    notice: Notice | None = None
    insightLines: list[Insight] = Field(default_factory=list, max_length=100)

    @model_validator(mode="after")
    def references(self):
        keys = [entry.key for entry in self.aggregates]
        exports = [entry.key for entry in self.export.columns]
        if len(set(keys)) != len(keys) or len(set(exports)) != len(exports) or len(set(self.searchFields)) != len(self.searchFields):
            raise ValueError("duplicate list keys")
        references = ([self.notice.aggregate] if self.notice else []) + [
            variant.when.aggregate for line in self.insightLines for variant in line.variants if variant.when]
        if any(key not in keys for key in references):
            raise ValueError("unknown aggregate reference")
        return self


def validate_list_experience(definition: dict) -> list[str]:
    if "listExperience" not in definition:
        return []
    try:
        metadata = definition["listExperience"]
        if isinstance(metadata, dict) and "workflowResume" in metadata and metadata["workflowResume"] is None:
            return ["listenvertrag_ungueltig"]
        if isinstance(metadata, dict) and any(isinstance(aggregate, dict) and any(
                key in aggregate and aggregate[key] is None for key in ("kind", "field", "format", "currencyField"))
                for aggregate in metadata.get("aggregates", []) if isinstance(metadata.get("aggregates"), list)):
            return ["listenvertrag_ungueltig"]
        experience = ListExperience.model_validate(metadata)
        tables = definition.get("tables") or []
        if definition.get("mode") != "list" or not tables or not isinstance(tables[0], dict):
            return ["listenvertrag_benoetigt_listenmaske_mit_tabelle"]
        columns = {column.get("key") for column in tables[0].get("columns", []) if isinstance(column, dict)}
        used = set(experience.searchFields) | {column.key for column in experience.export.columns} | {
            condition.field for aggregate in experience.aggregates for condition in aggregate.conditions} | {
            aggregate.field for aggregate in experience.aggregates if aggregate.field is not None} | {
            aggregate.currencyField for aggregate in experience.aggregates if aggregate.currencyField is not None}
        if not used <= columns:
            return ["listenvertrag_feld_nicht_deklariert"]
        return []
    except (ValidationError, TypeError, ValueError):
        return ["listenvertrag_ungueltig"]
