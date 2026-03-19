from fastapi import APIRouter, Depends, HTTPException, Header
from typing import Optional
from ...schemas.feed import FeedIngredient
from ...schemas.requirement import NutrientRequirements
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
from ...schemas.common import BaseResponse
import logging

logger = logging.getLogger(__name__)

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
    
    try:
        result = optimization_service.optimize_ration(
            feeds=active_feeds,
            requirements=request.requirements,
            options=request.options
        )
        return result
    except Exception as e:
        logger.error(f"Error during optimization: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")

@router.post("/optimize/demo", response_model=OptimizationResult)
async def demo_optimization(tenant_id: str = Depends(get_tenant_id)):
    """
    Run a demo optimization with sample data
    """
    logger.info(f"Running demo optimization for tenant {tenant_id}")
    
    # Get sample feeds for the tenant
    feeds = feed_service.get_all_feeds(active_only=True, tenant_id=tenant_id)
    
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
    
    # Create request
    request = OptimizationRequest(
        cow_profile=cow_profile,
        requirements=requirements,
        feeds=feeds,
        options=options
    )
    
    try:
        result = optimization_service.optimize_ration(
            feeds=feeds,
            requirements=requirements,
            options=options
        )
        return result
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
    
    # Use default options if none provided
    if options is None:
        options = OptimizationOptions()
    
    try:
        result = optimization_service.optimize_ration(
            feeds=selected_feeds,
            requirements=requirements,
            options=options
        )
        return result
    except Exception as e:
        logger.error(f"Error during optimization from profile: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")