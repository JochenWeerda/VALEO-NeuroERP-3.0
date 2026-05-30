"""Pydantic schemas for the compat domain."""
from __future__ import annotations

from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict as _ConfigDict


class CsvImportResponse(BaseSchema):
    created: int = 0
    updated: int = 0
    errors: list[str] = []


class PurchaseOrderListOut(BaseSchema):
    data: list[dict] = []
    page: int = 1
    pageSize: int = 50
    total: int = 0
    totalPages: int = 1


class PurchaseOrderOut(BaseSchema):
    model_config = _ConfigDict(extra="allow")
    id: str = ""
    status: Optional[str] = None


class EinkaufDocOut(BaseSchema):
    model_config = _ConfigDict(extra="allow")
    id: str = ""


class InventoryOut(BaseSchema):
    model_config = _ConfigDict(extra="allow")


class AnnahmeEntryOut(BaseSchema):
    model_config = _ConfigDict(extra="allow")
    id: str = ""


class PortalOut(BaseSchema):
    model_config = _ConfigDict(extra="allow")


class SetupFirmaOut(BaseSchema):
    model_config = _ConfigDict(extra="allow")


class FieldServiceTaskOut(BaseSchema):
    model_config = _ConfigDict(extra="allow")
    id: str = ""
    status: Optional[str] = None


class CrmOut(BaseSchema):
    model_config = _ConfigDict(extra="allow")


class SanktionsPruefungOut(BaseSchema):
    geprueft: bool
    treffer: bool
    name: str
    land: str
    listen: list[str] = []
    ergebnis: str = ""
    geprueft_am: str = ""
    hinweis: str = ""


class NewsletterOut(BaseSchema):
    initiiert: bool = True
    empfaenger_gesamt: int = 0
    empfaenger_gueltig: int = 0
    empfaenger_ungueltig: int = 0
    betreff: str = ""
    typ: str = ""
    status: str = ""
    hinweis: str = ""


class FutterBulkDeleteIn(BaseModel):
    ids: list[str] = Field(default_factory=list, min_length=1, max_length=100)


class FutterBulkDeleteErrorOut(BaseModel):
    id: str
    detail: str


class FutterBulkDeleteOut(BaseModel):
    requested: int
    deleted: int
    missing_ids: list[str] = Field(default_factory=list)
    errors: list[FutterBulkDeleteErrorOut] = Field(default_factory=list)


class NaehrwertBerechnungRequest(BaseModel):
    komponenten: list[NaehrwertKomponente] = Field(default_factory=list)
    fan: float = Field(default=2.5, description="Futteraufnahmeniveau (Vielfaches Erhaltung)")
    modus: str = Field(default="beratung", description="beratung | deklaration")


class SanktionsPruefungRequest(BaseModel):
    name: str = Field(..., min_length=1)
    land: str = Field(default="DE")


class NewsletterRequest(BaseModel):
    empfaenger: list[str] = Field(..., description="E-Mail-Adressen der EmpfÃ¤nger")
    typ: str = Field(default="allgemein")
    betreff: str = Field(default="Information von VALEO")
    text: Optional[str] = None


class AnnahmeStatusUpdate(BaseModel):
    status: Optional[str] = Field(default=None, description="in-bearbeitung | abgeschlossen | gesperrt")
    klaerung: Optional[dict[str, Any]] = Field(default=None, description="Klaerungsdaten fuer gesperrte Ware")


class LKWRegistrierungIn(BaseModel):
    kennzeichen: str = Field(..., min_length=1)
    lieferant: str = Field(..., min_length=1)
    lieferschein_nr: str = Field(default="")
    article_id: str | None = Field(default=None)
    artikel: str = Field(default="")
    ankunftszeit: str = Field(default="")
    prioritaet: str = Field(default="normal", description="hoch | normal | niedrig")
    attachment_ids: List[str] = Field(default_factory=list, description="IDs von hochgeladenen AnhÃ¤ngen (Kennzeichen/Lieferschein-Fotos)")


class LKWRegistrierungOut(BaseModel):
    id: str
    kennzeichen: str
    article_id: str | None = None
    artikel: str = ""
    status: str = "warteschlange"


class AnnahmeUploadOut(BaseModel):
    id: str
    filename: str


class EinlagerungIn(BaseModel):
    chargen_id: str = Field(..., description="Chargen-ID der einzulagernden Ware")
    artikel: str = Field(..., description="Artikel-Bezeichnung")
    menge: float = Field(..., gt=0, description="Menge in Tonnen")
    lagerort: str = Field(..., description="Lagerort-Code (z.B. silo-1, halle-a)")
    lagerplatz: Optional[str] = Field(default=None, description="Optionaler Lagerplatz / Bin-Location")


class EinlagerungOut(BaseModel):
    id: str
    batch_number: str
    artikel: str
    menge: float
    lagerort: str
    lagerplatz: Optional[str]
    datum: date
    status: str


class AuslagerungIn(BaseModel):
    artikel: str = Field(..., description="Artikel-Bezeichnung")
    menge: float = Field(..., gt=0, description="Menge (z.B. Tonnen)")
    strategie: str = Field(default="fifo", description="fifo | fefo | manuell")
    chargen_id: Optional[str] = Field(default=None, description="Charge bei manuell")
    verwendungszweck: Optional[str] = Field(default=None)


class AuslagerungOut(BaseModel):
    id: str
    artikel: str
    menge: float
    strategie: str
    chargen_id: Optional[str]
    datum: date
    status: str


class TagesabschlussIn(BaseModel):
    datum: date
    kassierer: str = ""
    tse_transaktionen: int = 0
    umsatz_bar: float = 0.0
    umsatz_ec: float = 0.0
    umsatz_paypal: float = 0.0
    umsatz_b2b: float = 0.0
    umsatz_gesamt: float = 0.0
    bargeld_gezaehlt: float = 0.0
    ec_abrechnung: float = 0.0
    paypal_abrechnung: float = 0.0
    differenz_bar: float = 0.0


class TagesabschlussOut(BaseModel):
    id: str
    datum: date
    kassierer: str
    umsatz_gesamt: float
    status: str
    belegnummer: str

