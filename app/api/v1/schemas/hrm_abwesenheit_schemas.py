"""Response-Schemas fuer Abwesenheitsantraege und Urlaubskonto.

SPEC-P1-06 Welle 5: ersetzt ``response_model=dict[str, Any]`` in
``app/api/v1/endpoints/hrm_abwesenheit.py``.

Feldliste aus ``Abwesenheitsantrag.to_dict`` und
``HrmAbwesenheitService.urlaubskonto``.
"""

from __future__ import annotations

from typing import Optional

from pydantic import Field

from app.api.v1.schemas.base import BaseSchema


class AbwesenheitsantragOut(BaseSchema):
    """Ein Abwesenheitsantrag samt abgeleiteter Kennzeichen."""

    antrag_id: Optional[str] = None
    tenant_id: Optional[str] = None
    mitarbeiter_nr: Optional[str] = None
    typ: Optional[str] = None
    von_datum: Optional[str] = Field(default=None, description="ISO-Datum")
    bis_datum: Optional[str] = Field(default=None, description="ISO-Datum")
    arbeitstage: Optional[float] = None
    status: Optional[str] = None
    beantragt_von: Optional[str] = None
    beantragt_am: Optional[str] = None
    kommentar: Optional[str] = None
    genehmigt_von: Optional[str] = None
    genehmigt_am: Optional[str] = None
    ablehnung_grund: Optional[str] = None
    eau_nachweis_id: Optional[str] = Field(
        default=None, description="Nachweis der elektronischen Arbeitsunfaehigkeit"
    )
    vertretung_durch: Optional[str] = None
    eau_pflicht: Optional[bool] = Field(
        default=None, description="True bei Typen, die einen eAU-Nachweis verlangen"
    )
    abgeschlossen: Optional[bool] = Field(
        default=None, description="True bei Endstatus (genehmigt/abgelehnt/zurueckgezogen)"
    )


class AbwesenheitsantragListeOut(BaseSchema):
    """``GET /antraege``"""

    items: list[AbwesenheitsantragOut] = Field(default_factory=list)
    count: Optional[int] = None


class UrlaubskontoOut(BaseSchema):
    """``GET /urlaubskonto/{mitarbeiter_nr}``"""

    mitarbeiter_nr: Optional[str] = None
    jahr: Optional[int] = None
    anspruch_tage: Optional[float] = None
    verbraucht_tage: Optional[float] = None
    resturlaub_tage: Optional[float] = None
    genehmigte_antraege: Optional[int] = None
