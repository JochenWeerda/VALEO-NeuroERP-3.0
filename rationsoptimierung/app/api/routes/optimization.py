from fastapi import APIRouter, Depends, HTTPException, Header
from typing import Optional
from ...schemas.optimization import (
    OptimizationRequest,
    OptimizationOptions,
    OptimizationResult,
    OptimizeFromProfileRequest,
)
from ...domain.models import CowProfile
from ...services.feed_service import FeedService
from ...services.requirement_service import RequirementService
from ...optimization.solver import OptimizationService
from ...utils.tenant_feeds import ensure_forage_feeds_for_lp
import logging

logger = logging.getLogger(__name__)


def _merge_forage_supplement_into_result(result, supplemented: bool, extra_warnings: list[str]):
    if not supplemented:
        return result
    meta = dict(result.metadata or {})
    meta["forage_supplement_from_default_tenant"] = True
    meta["supplement_tenant_id"] = "default"
    return result.model_copy(
        update={
            "warnings": list(result.warnings) + extra_warnings,
            "metadata": meta,
        }
    )

router = APIRouter()
feed_service = FeedService()
requirement_service = RequirementService()
optimization_service = OptimizationService()

def get_tenant_id(x_tenant_id: Optional[str] = Header(None)) -> str:
    """Extract tenant ID from header, default to 'default'"""
    return x_tenant_id if x_tenant_id else "default"

@router.post("/optimize", response_model=OptimizationResult)
async def optimize_ration(request: OptimizationRequest, tenant_id: str = Depends(get_tenant_id)):
    """
    Optimize a ration for a cow based on her profile, requirements, and available feeds
    """
    logger.info(f"Optimizing ration for tenant {tenant_id}: {request.cow_profile.breed} cow")
    
    # Validate feeds
    feed_errors = feed_service.validate_feeds(request.feeds)
    if feed_errors:
        raise HTTPException(status_code=400, detail=f"Feed validation errors: {', '.join(feed_errors)}")
    
    # Filter to active feeds only
    active_feeds = [f for f in request.feeds if f.active]
    if not active_feeds:
        raise HTTPException(status_code=400, detail="No active feeds provided")

    active_feeds, supplemented, extra_warnings = ensure_forage_feeds_for_lp(
        active_feeds, tenant_id, feed_service
    )

    try:
        result = optimization_service.optimize_ration(
            feeds=active_feeds,
            requirements=request.requirements,
            options=request.options
        )
        return _merge_forage_supplement_into_result(result, supplemented, extra_warnings)
    except Exception as e:
        logger.error(f"Error during optimization: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")

@router.post("/optimize/demo", response_model=OptimizationResult)
async def demo_optimization(tenant_id: str = Depends(get_tenant_id)):
    """
    Demo-Optimierung mit festem Kuhprofil (22 kg TM).

    - **Standard** (`X-Tenant-Id` weglassen → `default`): die 8 Demo-Futtermittel.
    - **DLG-Merge** (`X-Tenant-Id: dlg` + `RATIONS_DLG_MERGED_ENABLE=1`): gemergte Futtermittel inkl. Raufutter
      (Silagen/Heu über Overlay im Merge); **ohne** Raufutter im Korb werden wie bei anderen Mandanten
      **Grassilage + Maissilage** aus `default` ergänzt (Mindest-Raufutteranteil).

    Siehe `docs/futterwerte_dlg_2025_gfe2023.md`.
    """
    logger.info(f"Running demo optimization for tenant {tenant_id}")
    
    # Get sample feeds for the tenant
    feeds = feed_service.get_all_feeds(active_only=True, tenant_id=tenant_id)
    if not feeds:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Keine aktiven Futtermittel für Mandant '{tenant_id}'. "
                "Für Mandant 'dlg': Umgebungsvariable RATIONS_DLG_MERGED_ENABLE=1 setzen "
                "und dlg_merged_feeds_lp.csv vorhanden lassen, oder ohne X-Tenant-Id den Demo-Mandanten nutzen."
            ),
        )
    feeds, supplemented, extra_warnings = ensure_forage_feeds_for_lp(
        feeds, tenant_id, feed_service
    )
    
    # Create a sample cow profile
    cow_profile = CowProfile(
        breed="Holstein",
        body_weight_kg=650,
        milk_kg_day=35,
        milk_fat_pct=3.8,
        milk_protein_pct=3.2,
        lactation_stage_days=150,
        parity=2,
        target_dmi_kg=22.0
    )
    
    # Calculate requirements
    requirements = requirement_service.calculate_requirements(cow_profile)
    
    # Create default options
    options = OptimizationOptions()

    try:
        result = optimization_service.optimize_ration(
            feeds=feeds,
            requirements=requirements,
            options=options
        )
        meta = dict(result.metadata or {})
        meta["tenant_id"] = tenant_id
        result = result.model_copy(update={"metadata": meta})
        return _merge_forage_supplement_into_result(result, supplemented, extra_warnings)
    except Exception as e:
        logger.error(f"Error during demo optimization: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Demo optimization failed: {str(e)}")

@router.post("/optimize/from-profile", response_model=OptimizationResult)
async def optimize_from_cow_profile(
    body: OptimizeFromProfileRequest,
    tenant_id: str = Depends(get_tenant_id),
):
    """
    Optimize a ration based only on a cow profile (requirements calculated automatically)
    """
    cow_profile = body.cow_profile
    feeds = body.feeds
    options = body.options
    logger.info(f"Optimizing ration from cow profile for tenant {tenant_id}: {cow_profile.breed}")
    
    # Calculate requirements
    requirements = requirement_service.calculate_requirements(cow_profile)
    
    # Get feeds
    if feeds:
        # Get specific feeds by ID
        selected_feeds = []
        for feed_id in feeds:
            feed = feed_service.get_feed_by_id(feed_id, tenant_id)
            if feed:
                selected_feeds.append(feed)
            else:
                logger.warning(f"Feed with ID '{feed_id}' not found for tenant '{tenant_id}'")
        
        if not selected_feeds:
            raise HTTPException(status_code=400, detail=f"No valid feeds found for the provided IDs for tenant '{tenant_id}'")
        
        selected_feeds = [f for f in selected_feeds if f.active]
    else:
        # Use all active feeds for the tenant
        selected_feeds = feed_service.get_all_feeds(active_only=True, tenant_id=tenant_id)
    
    if not selected_feeds:
        raise HTTPException(status_code=400, detail=f"No active feeds available for tenant '{tenant_id}'")

    selected_feeds, supplemented, extra_warnings = ensure_forage_feeds_for_lp(
        selected_feeds, tenant_id, feed_service
    )

    # Use default options if none provided
    if options is None:
        options = OptimizationOptions()
    
    try:
        result = optimization_service.optimize_ration(
            feeds=selected_feeds,
            requirements=requirements,
            options=options
        )
        return _merge_forage_supplement_into_result(result, supplemented, extra_warnings)
    except Exception as e:
        logger.error(f"Error during optimization from profile: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")