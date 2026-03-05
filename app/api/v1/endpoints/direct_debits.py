"""
Direct debit endpoints used by finance UI masks.
Provides lightweight defaults so form routes can load without 404s.
"""

from datetime import date
from fastapi import APIRouter, Depends

from ....core.tenant import get_tenant_id

router = APIRouter(prefix="/direct-debits", tags=["finance", "direct-debits"])


@router.get("", response_model=list[dict])
async def list_direct_debits(tenant_id: str = Depends(get_tenant_id)):
    """Return an empty list if no direct debit backend is configured yet."""
    _ = tenant_id
    return []


@router.get("/new", response_model=dict)
async def get_new_direct_debit_template(tenant_id: str = Depends(get_tenant_id)):
    """Return default values for direct debit create forms."""
    return {
        "id": None,
        "tenant_id": tenant_id,
        "laufnummer": "",
        "faelligkeitsdatum": date.today().isoformat(),
        "ausfuehrungsdatum": date.today().isoformat(),
        "sepaSchema": "CORE",
        "sequenzTyp": "RCUR",
        "glaeubigerId": "",
        "abbucherName": "",
        "anzahlLastschriften": 0,
        "gesamtbetrag": 0,
        "status": "draft",
        "lastschriften": [],
    }
