"""WM-AGRI-SILO-001 — Agrar-Siloanlagen und Materialfluss (additiv zu /lager/wms)."""

from __future__ import annotations

from decimal import Decimal
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.api.v1.schemas.base import BaseSchema
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.agri_silo_material_flow_service import AgriSiloMaterialFlowService


class AgriJsonOut(BaseSchema):
    model_config = ConfigDict(extra="allow")


router = APIRouter()


def _svc(db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)) -> AgriSiloMaterialFlowService:
    return AgriSiloMaterialFlowService(db, tenant_id)


# ── Schemas ────────────────────────────────────────────────────────────────


class SiloSystemIn(BaseModel):
    system_code: str
    name: str
    description: Optional[str] = None


class SiloCellIn(BaseModel):
    cell_code: str
    name: str
    capacity_kg: Optional[Decimal] = None
    zone_id: Optional[str] = None
    aisle_id: Optional[str] = None
    bin_id: Optional[str] = None
    current_material_id: Optional[str] = None
    current_lot_id: Optional[str] = None
    qs_status: str = "frei"
    contamination_risk_class: Optional[str] = None


class SiloCellPatch(BaseModel):
    qs_status: Optional[str] = None
    name: Optional[str] = None
    capacity_kg: Optional[Decimal] = None
    current_material_id: Optional[str] = None
    current_lot_id: Optional[str] = None
    contamination_risk_class: Optional[str] = None
    layout_x: Optional[Decimal] = None
    layout_y: Optional[Decimal] = None
    legacy_silo_id: Optional[str] = None


class MaterialFlowNodeIn(BaseModel):
    node_type: str
    code: str
    name: str
    ref_type: Optional[str] = None
    ref_id: Optional[str] = None
    status: str = "active"
    geo_lat: Optional[Decimal] = None
    geo_lng: Optional[Decimal] = None
    layout_x: Optional[Decimal] = None
    layout_y: Optional[Decimal] = None


class MaterialFlowNodePatch(BaseModel):
    status: Optional[str] = None
    name: Optional[str] = None
    ref_type: Optional[str] = None
    ref_id: Optional[str] = None
    geo_lat: Optional[Decimal] = None
    geo_lng: Optional[Decimal] = None
    layout_x: Optional[Decimal] = None
    layout_y: Optional[Decimal] = None


class MaterialFlowEdgeIn(BaseModel):
    from_node_id: str
    to_node_id: str
    conveyor_type: str = "generic"
    status: str = "open"
    contamination_guard_enabled: bool = True
    flush_required: bool = False
    max_capacity_kg_h: Optional[Decimal] = None


class MaterialFlowEdgePatch(BaseModel):
    status: Optional[str] = None
    conveyor_type: Optional[str] = None
    contamination_guard_enabled: Optional[bool] = None
    flush_required: Optional[bool] = None
    max_capacity_kg_h: Optional[Decimal] = None


class ValidateRouteIn(BaseModel):
    warehouse_id: str
    from_node_id: str
    to_node_id: str
    material_id: Optional[str] = None
    previous_material_id: Optional[str] = None


# ── Siloanlagen ────────────────────────────────────────────────────────────


@router.get("/silo-systems", summary="GET /silo-systems")
def list_silo_systems(
    warehouse_id: Optional[str] = Query(None),
    svc: AgriSiloMaterialFlowService = Depends(_svc),
) -> Any:
    return svc.list_silo_systems(warehouse_id)


@router.post("/silo-systems", status_code=status.HTTP_201_CREATED, response_model=AgriJsonOut, summary="POST /silo-systems")
def create_silo_system(
    warehouse_id: str = Query(...),
    payload: SiloSystemIn = ...,
    svc: AgriSiloMaterialFlowService = Depends(_svc),
) -> Any:
    try:
        return svc.create_silo_system(warehouse_id, payload.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


# ── Silozellen ──────────────────────────────────────────────────────────────


@router.get("/silo-cells", summary="GET /silo-cells")
def list_silo_cells(
    warehouse_id: Optional[str] = Query(None),
    silo_system_id: Optional[str] = Query(None),
    svc: AgriSiloMaterialFlowService = Depends(_svc),
) -> Any:
    return svc.list_silo_cells(warehouse_id, silo_system_id)


@router.post("/silo-cells", status_code=status.HTTP_201_CREATED, response_model=AgriJsonOut, summary="POST /silo-cells")
def create_silo_cell(
    silo_system_id: str = Query(...),
    warehouse_id: str = Query(...),
    payload: SiloCellIn = ...,
    svc: AgriSiloMaterialFlowService = Depends(_svc),
) -> Any:
    try:
        return svc.create_silo_cell(silo_system_id, warehouse_id, payload.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.patch("/silo-cells/{cell_id}", response_model=AgriJsonOut, summary="PATCH /silo-cells/{cell_id}")
def patch_silo_cell(
    cell_id: str,
    warehouse_id: str = Query(...),
    payload: SiloCellPatch = ...,
    svc: AgriSiloMaterialFlowService = Depends(_svc),
) -> Any:
    body = payload.model_dump(exclude_unset=True)
    try:
        return svc.patch_silo_cell(cell_id, warehouse_id, body)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


# ── Materialfluss ───────────────────────────────────────────────────────────


@router.get("/material-flow/nodes", summary="GET /material-flow/nodes")
def list_flow_nodes(
    warehouse_id: Optional[str] = Query(None),
    svc: AgriSiloMaterialFlowService = Depends(_svc),
) -> Any:
    return svc.list_material_flow_nodes(warehouse_id)


@router.post("/material-flow/nodes", status_code=status.HTTP_201_CREATED, response_model=AgriJsonOut, summary="POST /material-flow/nodes")
def create_flow_node(
    warehouse_id: str = Query(...),
    payload: MaterialFlowNodeIn = ...,
    svc: AgriSiloMaterialFlowService = Depends(_svc),
) -> Any:
    try:
        return svc.create_material_flow_node(warehouse_id, payload.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.patch("/material-flow/nodes/{node_id}", response_model=AgriJsonOut, summary="PATCH /material-flow/nodes/{node_id}")
def patch_flow_node(
    node_id: str,
    warehouse_id: str = Query(...),
    payload: MaterialFlowNodePatch = ...,
    svc: AgriSiloMaterialFlowService = Depends(_svc),
) -> Any:
    body = payload.model_dump(exclude_unset=True)
    try:
        return svc.patch_material_flow_node(node_id, warehouse_id, body)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/material-flow/edges", summary="GET /material-flow/edges")
def list_flow_edges(
    warehouse_id: Optional[str] = Query(None),
    svc: AgriSiloMaterialFlowService = Depends(_svc),
) -> Any:
    return svc.list_material_flow_edges(warehouse_id)


@router.post("/material-flow/edges", status_code=status.HTTP_201_CREATED, response_model=AgriJsonOut, summary="POST /material-flow/edges")
def create_flow_edge(
    warehouse_id: str = Query(...),
    payload: MaterialFlowEdgeIn = ...,
    svc: AgriSiloMaterialFlowService = Depends(_svc),
) -> Any:
    try:
        return svc.create_material_flow_edge(warehouse_id, payload.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.patch("/material-flow/edges/{edge_id}", response_model=AgriJsonOut, summary="PATCH /material-flow/edges/{edge_id}")
def patch_flow_edge(
    edge_id: str,
    warehouse_id: str = Query(...),
    payload: MaterialFlowEdgePatch = ...,
    svc: AgriSiloMaterialFlowService = Depends(_svc),
) -> Any:
    body = payload.model_dump(exclude_unset=True)
    try:
        return svc.patch_material_flow_edge(edge_id, warehouse_id, body)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/material-flow/validate-route", response_model=AgriJsonOut, summary="POST /material-flow/validate-route")
def validate_route(
    payload: ValidateRouteIn = ...,
    svc: AgriSiloMaterialFlowService = Depends(_svc),
) -> Any:
    return svc.validate_route(
        payload.warehouse_id,
        payload.from_node_id,
        payload.to_node_id,
        payload.material_id,
        payload.previous_material_id,
    )


class MaterialTransferIn(BaseModel):
    warehouse_id: str
    from_cell_id: str
    to_cell_id: str
    quantity_kg: Decimal
    article_id: str
    lot_id: Optional[str] = None
    booked_by: Optional[str] = None
    reference: Optional[str] = None


@router.post("/material-flow/transfer", response_model=AgriJsonOut, status_code=200, summary="POST /material-flow/transfer")
def book_material_transfer(
    payload: MaterialTransferIn,
    svc: AgriSiloMaterialFlowService = Depends(_svc),
) -> Any:
    """WMS-FLOW-001: Materialtransfer zwischen Silozellen mit Lagerbuchung."""
    try:
        return svc.book_material_transfer(
            warehouse_id=payload.warehouse_id,
            from_cell_id=payload.from_cell_id,
            to_cell_id=payload.to_cell_id,
            quantity_kg=payload.quantity_kg,
            article_id=payload.article_id,
            lot_id=payload.lot_id,
            booked_by=payload.booked_by or "system",
            reference=payload.reference,
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post(
    "/silo-cells/{cell_id}/sync-from-lots",
    response_model=AgriJsonOut,
    status_code=200,
    summary="POST /silo-cells/{cell_id}/sync-from-lots",
)
def sync_silo_cell_from_lots(
    cell_id: str,
    warehouse_id: str = Query(...),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> Any:
    """WM-AGRI-LOT-LINK: Aggregiert aktive silo_lots des verknüpften Legacy-Silos auf die Silozelle."""
    from app.services.agri_silo_lot_link_service import AgriSiloLotLinkService

    try:
        return AgriSiloLotLinkService(db, tenant_id).sync_cell_from_lots(cell_id, warehouse_id)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
