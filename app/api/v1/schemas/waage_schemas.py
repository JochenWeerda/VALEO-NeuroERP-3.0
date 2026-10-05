"""Antwortmodelle der Doppelwiegung.

Beide Wege hingen an `WaageOut` — einem Modell mit ``extra="allow"``, das an
jedem Weg des Moduls haengt. Ein Modell, das alles erlaubt, beschreibt nichts:
Das Anlegen gab `{id, netto, gosse, zielschein_typ, status}` zurueck, das Lesen
eine ganz andere Form, und beides galt als dasselbe.
"""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

#: Deckungsgleich mit ``wiegung_service.RICHTUNG_JE_ZIELSCHEIN``.
#: EL = Eingangslieferschein (Zugang), VL = Verkaufslieferschein (Abgang).
Zielscheintyp = Literal["EL", "VL"]


class WiegungErweitert(BaseModel):
    """Die zwei Waegungen und was die Waage dazu weiss.

    ``brutto_kg`` und ``tara_kg`` sind benannt, nicht ``wiegung1``/``wiegung2``:
    Der Weg rechnete vorher ``abs(wiegung1 - wiegung2)``, und der Absolutbetrag
    verdeckte, dass die Reihenfolge eine fachliche Bedeutung hat.
    """

    model_config = ConfigDict(extra="forbid")

    waage_id: Optional[str] = None
    ident_nr: Optional[str] = None
    brutto_kg: Optional[float] = Field(default=None, ge=0)
    tara_kg: Optional[float] = Field(default=None, ge=0)
    netto_kg: Optional[float] = Field(
        default=None,
        gt=0,
        description="Nur bei Handwiegung oder Fremdwaage — sonst aus Brutto minus Tara",
    )
    gosse: Optional[int] = Field(default=None, ge=0)
    muster_nr: Optional[str] = None
    #: Nach MessEG ist eine von Hand eingetragene Masse keine geeichte Messung.
    handwiegung: bool = False
    zielschein_typ: Optional[Zielscheintyp] = None


class WiegescheinMitDoppelwiegung(BaseModel):
    model_config = ConfigDict(extra="forbid")

    waage_id: Optional[str] = None
    lieferant_id: Optional[str] = None
    artikel_id: Optional[str] = None
    partie_id: Optional[str] = None
    wiegung_erweitert: Optional[WiegungErweitert] = None
    disponr: Optional[str] = None
    charge_nr: Optional[str] = None
    kfz_kennzeichen: Optional[str] = None
    bemerkung: Optional[str] = None


class WiegungAngelegt(BaseModel):
    id: str
    ticket_number: str
    brutto_kg: Optional[float] = None
    tara_kg: Optional[float] = None
    netto_kg: float
    richtung: str
    gosse: Optional[int] = None
    handwiegung: bool
    status: str = "gebucht"


class WiegescheinOut(BaseModel):
    id: str
    ticket_number: str
    tenant_id: str
    scale_id: Optional[str] = None
    vehicle_plate: Optional[str] = None
    gross_weight: Optional[float] = None
    tare_weight: Optional[float] = None
    net_weight: Optional[float] = None
    weighing_date: Optional[str] = None
    status: Optional[str] = None
    direction: Optional[str] = None
    reference_doc: Optional[str] = None
    first_weighing_at: Optional[str] = None
    second_weighing_at: Optional[str] = None
    gosse: Optional[int] = None
    muster_nr: Optional[str] = None
    handwiegung: Optional[bool] = None
    ident_nr: Optional[str] = None
    disposition_nr: Optional[str] = None
    charge_nr: Optional[str] = None
    article_id: Optional[str] = None
    contract_id: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[str] = None
