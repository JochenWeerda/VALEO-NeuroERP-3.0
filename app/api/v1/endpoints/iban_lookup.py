"""
IBAN Lookup Service
Uses openiban.com to validate IBAN and retrieve bank information (bank name, BIC)
Includes caching to reduce API calls
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query
import httpx
from pydantic import BaseModel
from datetime import datetime, timedelta
import hashlib
import json

router = APIRouter(prefix="/iban-lookup", tags=["finance", "iban"])

# In-memory cache for IBAN lookups (in production, use Redis or similar)
_iban_cache: dict[str, tuple[dict, datetime]] = {}
CACHE_TTL_HOURS = 24  # Cache for 24 hours


def _get_cache_key(iban: str) -> str:
    """Generate cache key from normalized IBAN"""
    normalized = iban.replace(" ", "").replace("-", "").upper()
    return hashlib.md5(normalized.encode()).hexdigest()


def _get_cached(iban: str) -> Optional[dict]:
    """Get cached IBAN lookup result if available and not expired"""
    cache_key = _get_cache_key(iban)
    if cache_key in _iban_cache:
        cached_data, cached_time = _iban_cache[cache_key]
        if datetime.now() - cached_time < timedelta(hours=CACHE_TTL_HOURS):
            return cached_data
        else:
            # Remove expired entry
            del _iban_cache[cache_key]
    return None


def _set_cache(iban: str, data: dict):
    """Cache IBAN lookup result"""
    cache_key = _get_cache_key(iban)
    _iban_cache[cache_key] = (data, datetime.now())
    # Limit cache size (keep last 1000 entries)
    if len(_iban_cache) > 1000:
        # Remove oldest entries
        sorted_entries = sorted(_iban_cache.items(), key=lambda x: x[1][1])
        for key, _ in sorted_entries[:100]:
            del _iban_cache[key]


class IBANLookupResponse(BaseModel):
    """Response model for IBAN lookup"""
    valid: bool
    iban: str
    bank_name: Optional[str] = None
    bic: Optional[str] = None
    bank_code: Optional[str] = None
    city: Optional[str] = None
    zip: Optional[str] = None
    country: Optional[str] = None
    message: Optional[str] = None


@router.get("/validate/{iban}", response_model=IBANLookupResponse)
async def lookup_iban(
    iban: str,
    get_bic: bool = Query(True, description="Include BIC in response"),
    validate_bank_code: bool = Query(True, description="Validate bank code")
):
    """
    Validate IBAN and retrieve bank information using openiban.com
    
    Args:
        iban: The IBAN to validate (will be normalized - spaces removed, uppercase)
        get_bic: Whether to include BIC in response
        validate_bank_code: Whether to validate bank code
    
    Returns:
        IBANLookupResponse with validation result and bank information
    """
    # Normalize IBAN: remove spaces and convert to uppercase
    normalized_iban = iban.replace(" ", "").replace("-", "").upper()
    
    # Basic format validation
    if not normalized_iban or len(normalized_iban) < 15 or len(normalized_iban) > 34:
        raise HTTPException(
            status_code=400,
            detail="Invalid IBAN format: must be between 15 and 34 characters"
        )
    
    # Check cache first
    cached_result = _get_cached(normalized_iban)
    if cached_result:
        return IBANLookupResponse(**cached_result)
    
    # Build openiban.com URL
    base_url = "https://openiban.com/validate"
    params = {
        "getBIC": "true" if get_bic else "false",
        "validateBankCode": "true" if validate_bank_code else "false"
    }
    url = f"{base_url}/{normalized_iban}"
    
    try:
        # Make request to openiban.com
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
        
        # Extract bank data if available
        bank_data = data.get("bankData", {})
        
        result = IBANLookupResponse(
            valid=data.get("valid", False),
            iban=normalized_iban,
            bank_name=bank_data.get("name"),
            bic=bank_data.get("bic"),
            bank_code=bank_data.get("bankCode"),
            city=bank_data.get("city"),
            zip=bank_data.get("zip"),
            country=normalized_iban[:2] if len(normalized_iban) >= 2 else None,
            message=data.get("message")
        )
        
        # Cache the result (only if valid to save space)
        if result.valid:
            _set_cache(normalized_iban, result.model_dump())
        
        return result
    
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="IBAN lookup service timeout. Please try again later."
        )
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            # IBAN not found or invalid
            return IBANLookupResponse(
                valid=False,
                iban=normalized_iban,
                message="IBAN not found or invalid"
            )
        raise HTTPException(
            status_code=502,
            detail=f"IBAN lookup service error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to lookup IBAN: {str(e)}"
        )

