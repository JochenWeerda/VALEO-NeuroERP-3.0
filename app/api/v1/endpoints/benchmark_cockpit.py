from __future__ import annotations

from fastapi import APIRouter

from app.core.benchmark_cockpit import (
    build_benchmark_catalog,
    build_benchmark_read_model,
    get_example_benchmark_report,
)

router = APIRouter(prefix="/benchmark", tags=["benchmark", "analytics", "catalog"])


@router.get("/catalog", summary="Benchmark Catalog",
    response_model=dict
)
def get_benchmark_catalog(
    tenant_id: str = "TENANT-001",
    genossenschaft_name: str = "Agrargenossenschaft Muster eG",
) -> dict:
    report = get_example_benchmark_report(
        tenant_id=tenant_id,
        genossenschaft_name=genossenschaft_name,
    )
    return build_benchmark_catalog(report).as_dict()


@router.get("/read-model", summary="Benchmark Read Model",
    response_model=dict
)
def get_benchmark_read_model(
    tenant_id: str = "TENANT-001",
    genossenschaft_name: str = "Agrargenossenschaft Muster eG",
) -> dict:
    report = get_example_benchmark_report(
        tenant_id=tenant_id,
        genossenschaft_name=genossenschaft_name,
    )
    return build_benchmark_read_model(report).as_dict()
