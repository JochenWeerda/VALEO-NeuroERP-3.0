"""
Agrar Sorten/Varieties API für Ernte-Annahme.
Liefert Standard-Sorten; kann später durch DB-Stammdaten ergänzt werden.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class VarietyOut(BaseModel):
    id: str
    variety_number: str
    name: str
    description: Optional[str] = None
    crop_type: Optional[str] = None


# Standard-Sorten (kann später aus DB/Stammdaten geladen werden)
STANDARD_VARIETIES: list[VarietyOut] = [
    VarietyOut(id="1", variety_number="245", name="Weizen", description="Standard-Weizen", crop_type="WHEAT"),
    VarietyOut(id="2", variety_number="100", name="Mais", description="Standard-Mais", crop_type="MAIZE"),
    VarietyOut(id="3", variety_number="200", name="Gerste", description="Standard-Gerste", crop_type="BARLEY"),
    VarietyOut(id="4", variety_number="300", name="Hafer", description="Standard-Hafer", crop_type="OATS"),
    VarietyOut(id="5", variety_number="400", name="Raps", description="Standard-Raps", crop_type="RAPESEED"),
]


@router.get("/", response_model=list[VarietyOut])
async def list_varieties():
    """Liste der Sorten für Ernte-Annahme (Ernte-Annahme Auswahlfelder)."""
    return STANDARD_VARIETIES
