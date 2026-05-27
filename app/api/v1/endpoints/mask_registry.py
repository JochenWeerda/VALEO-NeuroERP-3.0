"""
Mask Registry API — Wave 3 AP1

Liefert das klassifizierte Masken-Register (A/B/C) fuer das UI-Framework.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from ....core.tenant import get_tenant_id
from ....core.mask_classification import (
    MaskRegistry,
    MaskClass,
    MaskDomain,
    build_mask_registry,
)

router = APIRouter(prefix="/ui/mask-registry", tags=["ui", "masks"])

_REGISTRY: MaskRegistry = build_mask_registry()


@router.get("", response_model=dict, summary="Mask registry abrufen")
async def get_mask_registry(tenant_id: str = Depends(get_tenant_id)):
    """Liefert das vollstaendige Masken-Register mit A/B/C-Klassifizierung."""
    _ = tenant_id
    return _REGISTRY.model_dump(mode="json")


@router.get("/class/{mask_class}", response_model=list[dict], summary="Masks by class abrufen")
async def get_masks_by_class(
    mask_class: MaskClass,
    tenant_id: str = Depends(get_tenant_id),
):
    """Liefert alle Masken einer Klasse (A=Kernprozess, B=Unterstuetzend, C=Reporting)."""
    _ = tenant_id
    return [m.model_dump(mode="json") for m in _REGISTRY.get_by_class(mask_class)]


@router.get("/domain/{domain}", response_model=list[dict], summary="Masks by domain abrufen")
async def get_masks_by_domain(
    domain: MaskDomain,
    tenant_id: str = Depends(get_tenant_id),
):
    """Liefert alle Masken einer fachlichen Domain."""
    _ = tenant_id
    return [m.model_dump(mode="json") for m in _REGISTRY.get_by_domain(domain)]


@router.get("/gap-report", response_model=dict, summary="Class a gap report abrufen")
async def get_class_a_gap_report(tenant_id: str = Depends(get_tenant_id)):
    """
    Liefert Klasse-A-Masken ohne Wave-1-Contract (technische Schulden).
    Nuetzlich fuer Sprint-Planung und Architektur-Reviews.
    """
    _ = tenant_id
    gaps = _REGISTRY.class_a_without_wave1_contract()
    all_a = _REGISTRY.get_by_class(MaskClass.A)
    return {
        "class_a_total": len(all_a),
        "class_a_with_wave1_contract": len(all_a) - len(gaps),
        "class_a_gap_count": len(gaps),
        "gaps": [m.model_dump(mode="json") for m in gaps],
    }
