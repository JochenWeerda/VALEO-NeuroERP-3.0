"""
VIES Service
VAT Information Exchange System validation for EU VAT numbers
"""

import logging
import httpx
from typing import Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ViesResult:
    """VIES validation result"""
    valid: bool
    vat_number: str
    country_code: str
    name: Optional[str] = None
    address: Optional[str] = None
    request_date: Optional[str] = None
    error: Optional[str] = None


class ViesService:
    """Service for VIES VAT validation"""

    VIES_URL = "https://ec.europa.eu/taxation_customs/vies/rest-api/ms/{country_code}/vat/{vat_number}"

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=10.0)

    async def validate_vat(self, vat_number: str, country_code: Optional[str] = None) -> ViesResult:
        """
        Validate VAT number using VIES

        Args:
            vat_number: VAT number (with or without country code)
            country_code: Optional country code override

        Returns:
            ViesResult with validation details
        """
        try:
            # Extract country code from VAT number if not provided
            if not country_code:
                if len(vat_number) < 2:
                    return ViesResult(
                        valid=False,
                        vat_number=vat_number,
                        country_code="",
                        error="VAT number too short"
                    )
                country_code = vat_number[:2].upper()
                vat_number = vat_number[2:]

            # Clean VAT number (remove spaces, dashes, etc.)
            vat_number = "".join(c for c in vat_number if c.isalnum())

            logger.info(f"Validating VAT: {country_code}{vat_number}")

            # Call VIES API
            url = self.VIES_URL.format(country_code=country_code, vat_number=vat_number)
            response = await self.client.get(url)

            if response.status_code == 200:
                data = response.json()

                if data.get("valid", False):
                    return ViesResult(
                        valid=True,
                        vat_number=f"{country_code}{vat_number}",
                        country_code=country_code,
                        name=data.get("name"),
                        address=data.get("address"),
                        request_date=data.get("requestDate")
                    )
                else:
                    return ViesResult(
                        valid=False,
                        vat_number=f"{country_code}{vat_number}",
                        country_code=country_code,
                        error="VAT number not valid according to VIES"
                    )
            else:
                logger.warning(f"VIES API error: {response.status_code} - {response.text}")
                return ViesResult(
                    valid=False,
                    vat_number=f"{country_code}{vat_number}",
                    country_code=country_code,
                    error=f"VIES API error: {response.status_code}"
                )

        except Exception as e:
            logger.error(f"VIES validation failed: {e}")
            return ViesResult(
                valid=False,
                vat_number=vat_number,
                country_code=country_code or "",
                error=f"Validation failed: {str(e)}"
            )

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


# Global service instance
vies_service = ViesService()


async def validate_eu_vat(vat_number: str) -> ViesResult:
    """
    Convenience function for VAT validation

    Args:
        vat_number: Full VAT number with country code

    Returns:
        ViesResult
    """
    return await vies_service.validate_vat(vat_number)