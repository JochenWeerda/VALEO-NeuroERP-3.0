from fastapi import APIRouter, Depends, HTTPException, Header
from typing import Optional
from ...schemas.requirement import NutrientRequirements
from ...schemas.optimization import OptimizationRequest
from ...domain.models import CowProfile
from ...services.requirement_service import RequirementService
from ...schemas.common import BaseResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
requirement_service = RequirementService()

def get_tenant_id(x_tenant_id: Optional[str] = Header(None)) -> str:
    """Extract tenant ID from header, default to 'default'"""
    return x_tenant_id if x_tenant_id else "default"

@router.post("/requirements/calculate", response_model=NutrientRequirements)
async def calculate_requirements(cow_profile: CowProfile, tenant_id: str = Depends(get_tenant_id)):
    """
    Calculate nutrient requirements for a cow based on her profile
    """
    logger.debug(f"Calculating requirements for tenant {tenant_id}: cow {cow_profile.breed}, {cow_profile.milk_kg_day} kg milk/day")
    
    try:
        requirements = requirement_service.calculate_requirements(cow_profile)
        return requirements
    except Exception as e:
        logger.error(f"Error calculating requirements: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to calculate requirements: {str(e)}")

@router.post("/requirements/maintenance", response_model=NutrientRequirements)
async def calculate_maintenance_requirements(body_weight_kg: float, tenant_id: str = Depends(get_tenant_id)):
    """
    Calculate maintenance-only nutrient requirements for a dry cow
    """
    logger.debug(f"Calculating maintenance requirements for tenant {tenant_id}: cow weighing {body_weight_kg} kg")
    
    if body_weight_kg <= 0:
        raise HTTPException(status_code=400, detail="Body weight must be positive")
    
    try:
        requirements = requirement_service.get_maintenance_requirements(body_weight_kg)
        return requirements
    except Exception as e:
        logger.error(f"Error calculating maintenance requirements: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to calculate maintenance requirements: {str(e)}")