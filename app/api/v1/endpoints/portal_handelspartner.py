"""Own trade-partner discovery; never changes the active tenant or issues credentials."""
from typing import Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.auth.deps import get_current_user
from app.services.portal_tenant_directory import eigene_handelspartner

router = APIRouter(prefix="/portal", tags=["portal", "identity"])


class PortalHandelspartner(BaseModel):
    id: str = Field(..., description="Berechtigter Handelsmandant aus eigener Zuordnung")
    name: str = Field(..., description="Name des berechtigten Handelspartners")
    customer_count: int = Field(..., ge=1, description="Anzahl eigener aktiver Kundenkonten dort")
    active: bool = Field(..., description="Entspricht dem bereits verifizierten Token-Mandanten")


class PortalHandelspartnerVerzeichnis(BaseModel):
    items: list[PortalHandelspartner]
    stage: Literal["discovery_only"] = "discovery_only"
    context_switch_available: Literal[False] = False


@router.get(
    "/handelspartner",
    response_model=PortalHandelspartnerVerzeichnis,
    summary="Eigene freigegebene Handelspartner ermitteln",
    description=("Liefert ausschliesslich Metadaten eigener gueltiger Portal-Zuordnungen. "
                 "Waehlt keinen Mandanten, erweitert keine Rolle und gibt keine Geschaeftsdaten zurueck. "
                 "Ein fremder Subject- oder Tenant-Selektor ist kein Eingabeparameter. "
                 "Ohne gepruefte System-Leseverbindung bleibt der Weg gesperrt."),
    responses={403: {"description": "Gepruefte Identitaet fehlt"},
               503: {"description": "Sicheres Zuordnungsverzeichnis nicht verfuegbar"}},
)
def meine_handelspartner(user: dict = Depends(get_current_user)) -> PortalHandelspartnerVerzeichnis:
    return PortalHandelspartnerVerzeichnis(items=eigene_handelspartner(user))
