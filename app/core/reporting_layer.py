from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from app.core.read_model_persistence import ReadModelSnapshotStore


class DataProduct(BaseModel):
    product_id: str
    product_name: str
    tenant_id: str
    wirtschaftsjahr: str | None = None
    snapshot_ids: list[str] = Field(default_factory=list)
    source_models: list[str] = Field(default_factory=list)
    schema_version: int = 1


class DataProductCatalog(BaseModel):
    products: list[DataProduct] = Field(default_factory=list)
    schema_version: int = 1

    def get_by_tenant(self, tenant_id: str) -> list[DataProduct]:
        return [product for product in self.products if product.tenant_id == tenant_id]

    def get(self, product_id: str, tenant_id: str) -> DataProduct | None:
        return next(
            (
                product
                for product in self.products
                if product.product_id == product_id and product.tenant_id == tenant_id
            ),
            None,
        )


class ReportDefinition(BaseModel):
    report_id: str
    titel: str
    datenprodukt_id: str
    filter_spec: dict[str, Any] = Field(default_factory=dict)
    aggregationen: list[str] = Field(default_factory=list)
    schema_version: int = 1


class ReportResult(BaseModel):
    result_id: str
    report_id: str
    rows: list[dict[str, Any]] = Field(default_factory=list)
    total_rows: int
    generated_at: datetime
    schema_version: int = 1


def build_default_data_products(
    store: ReadModelSnapshotStore,
    tenant_id: str,
    wirtschaftsjahr: str | None = None,
) -> DataProductCatalog:
    product_specs = (
        ("finance-ap-invoice-cockpit", "AP-Invoice-Cockpit", ["ap-invoice-cockpit"]),
        ("finance-payment-run-cockpit", "Payment-Run-Cockpit", ["payment-run-cockpit"]),
        ("finance-process-observation", "Process-Observation", ["process-observation"]),
    )
    products: list[DataProduct] = []
    for product_id, product_name, source_models in product_specs:
        snapshot_ids: list[str] = []
        for model_name in source_models:
            snapshot = store.get_latest(model_name=model_name, tenant_id=tenant_id)
            if snapshot is not None:
                snapshot_ids.append(snapshot.snapshot_id)
        products.append(
            DataProduct(
                product_id=product_id,
                product_name=product_name,
                tenant_id=tenant_id,
                wirtschaftsjahr=wirtschaftsjahr,
                snapshot_ids=snapshot_ids,
                source_models=list(source_models),
            )
        )
    return DataProductCatalog(products=products)


def run_report(
    report_definition: ReportDefinition,
    data_product: DataProduct,
    store: ReadModelSnapshotStore,
) -> ReportResult:
    rows: list[dict[str, Any]] = []
    for snapshot_id in data_product.snapshot_ids:
        snapshot = store.get(snapshot_id)
        if snapshot is None:
            continue
        rows.extend(_snapshot_rows(snapshot.get_payload()))

    filtered_rows = _apply_filters(rows, report_definition.filter_spec)
    if report_definition.aggregationen:
        filtered_rows = _apply_aggregations(filtered_rows, report_definition.aggregationen)

    return ReportResult(
        result_id=str(uuid4()),
        report_id=report_definition.report_id,
        rows=filtered_rows,
        total_rows=len(filtered_rows),
        generated_at=datetime.utcnow(),
    )


def _snapshot_rows(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, dict):
        if isinstance(payload.get("items"), list):
            return [item for item in payload["items"] if isinstance(item, dict)]
        return [payload]
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    return [{"value": payload}]


def _apply_filters(rows: list[dict[str, Any]], filter_spec: dict[str, Any]) -> list[dict[str, Any]]:
    if not filter_spec:
        return rows
    filtered = rows
    for key, expected in filter_spec.items():
        filtered = [row for row in filtered if row.get(key) == expected]
    return filtered


def _apply_aggregations(rows: list[dict[str, Any]], aggregationen: list[str]) -> list[dict[str, Any]]:
    aggregated_row: dict[str, Any] = {}
    for aggregation in aggregationen:
        if aggregation == "count":
            aggregated_row["count"] = len(rows)
            continue
        if aggregation.startswith("sum:"):
            field_name = aggregation.split(":", 1)[1]
            aggregated_row[f"sum_{field_name}"] = sum(
                value for value in (row.get(field_name) for row in rows) if isinstance(value, (int, float))
            )
    return [aggregated_row] if aggregated_row else rows
