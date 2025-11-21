"""
VIES Router
API endpoints for VAT validation using VIES service
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import logging

from app.services.vies_service import validate_eu_vat, ViesResult

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/vies", tags=["vies"])


class VatValidationRequest(BaseModel):
    """VAT validation request"""
    vat_number: str
    country_code: str = None


class VatValidationResponse(BaseModel):
    """VAT validation response"""
    valid: bool
    vat_number: str
    country_code: str
    name: str = None
    address: str = None
    request_date: str = None
    error: str = None


@router.post("/validate", response_model=VatValidationResponse)
async def validate_vat(request: VatValidationRequest):
    """
    Validate VAT number using VIES

    Args:
        request: VatValidationRequest with VAT number and optional country code

    Returns:
        VatValidationResponse with validation result
    """
    try:
        result: ViesResult = await validate_eu_vat(request.vat_number)

        return VatValidationResponse(
            valid=result.valid,
            vat_number=result.vat_number,
            country_code=result.country_code,
            name=result.name,
            address=result.address,
            request_date=result.request_date,
            error=result.error
        )

    except Exception as e:
        logger.error(f"VAT validation endpoint failed: {e}")
        raise HTTPException(status_code=500, detail=f"VAT validation failed: {str(e)}")


@router.get("/validate/{vat_number}", response_model=VatValidationResponse)
async def validate_vat_simple(vat_number: str):
    """
    Simple VAT validation endpoint

    Args:
        vat_number: VAT number to validate

    Returns:
        VatValidationResponse with validation result
    """
    try:
        result: ViesResult = await validate_eu_vat(vat_number)

        return VatValidationResponse(
            valid=result.valid,
            vat_number=result.vat_number,
            country_code=result.country_code,
            name=result.name,
            address=result.address,
            request_date=result.request_date,
            error=result.error
        )

    except Exception as e:
        logger.error(f"Simple VAT validation endpoint failed: {e}")
        raise HTTPException(status_code=500, detail=f"VAT validation failed: {str(e)}")