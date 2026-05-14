"""
Harvest Acceptance (Ernte-Annahme) API endpoints.
Handles delivery, weighing, quality checks, and settlement for agricultural harvests.
"""

from __future__ import annotations

from datetime import datetime, date
from decimal import Decimal
from typing import Literal, Optional
import re

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field, field_validator, model_validator
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import ConflictError, EntityNotFoundError, ValidationFailedError
from app.core.tenant import get_tenant_id
from app.core.security import get_user_id_from_request
from app.services.harvest_acceptance_service import HarvestAcceptanceService
from app.infrastructure.models import (
    HarvestAcceptance,
    HarvestAcceptancePosition,
    Article,
)
from app.domains.inventory.api.inventory_auth import require_inventory_admin

router = APIRouter()

ReleaseStatus = Literal["draft", "provisional", "final", "credit_note_created", "paid", "disputed", "cancelled"]
PricingMode = Literal["fixed_contract", "spot_daily", "exchange_fix_later"]
AcceptanceMode = Literal["STORAGE_ONLY", "PURCHASE_AT_DELIVERY_PTBF", "ADVANCE_ON_STORAGE"]
OwnershipType = Literal["THIRD_PARTY_STOCK", "OWN_STOCK"]
VatEvent = Literal["NO_INVOICE", "PROVISIONAL_CREDIT_NOTE_CREATED", "FINAL_CREDIT_NOTE_CREATED", "CORRECTION_ISSUED"]


# ── NUTS-2 Validation & Helper ──────────────────────────────────────────────

def validate_nuts2_code(nuts2_code: Optional[str]) -> Optional[str]:
    """
    Validiert NUTS-2-Code Format.
    
    Format: 2 Buchstaben (Ländercode) + 1-2 Ziffern (Region)
    Beispiele: DE12 (Sachsen), DE14 (Sachsen-Anhalt), FR10 (Île-de-France)
    """
    if not nuts2_code:
        return None
    
    nuts2_code = nuts2_code.strip().upper()
    
    # Pattern: 2 Buchstaben + 1-2 Ziffern
    pattern = r"^[A-Z]{2}[0-9]{1,2}$"
    if not re.match(pattern, nuts2_code):
        raise ValueError(f"Invalid NUTS-2 code format: {nuts2_code}. Expected format: 2 letters + 1-2 digits (e.g., DE12)")
    
    return nuts2_code



def derive_nuts2_from_postal_code(postal_code: Optional[str], country_code: str = "DE") -> Optional[str]:
    """
    Leitet NUTS-2-Code aus PLZ ab (für Deutschland).
    
    Implementiert vollständige PLZ → NUTS-2-Zuordnungstabelle basierend auf
    Eurostat correspondence tables (NUTS 2021).
    
    Referenz: https://ec.europa.eu/eurostat/web/nuts/correspondence-tables
    """
    if not postal_code or country_code != "DE":
        return None
    
    postal_code_clean = postal_code.strip().replace(" ", "")
    
    if not postal_code_clean.isdigit() or len(postal_code_clean) != 5:
        return None
    
    plz_int = int(postal_code_clean)
    
    # Vollständige PLZ → NUTS-2 Zuordnung für Deutschland
    # Basierend auf Eurostat NUTS 2021 correspondence tables
    
    # DE11 Stuttgart
    if 70100 <= plz_int <= 70699:
        return "DE11"
    # DE12 Karlsruhe  
    if 76100 <= plz_int <= 77699:
        return "DE12"
    if 67000 <= plz_int <= 67999:
        return "DE12"
    # DE13 Freiburg
    if 79000 <= plz_int <= 79999:
        return "DE13"
    # DE14 Tübingen
    if 72000 <= plz_int <= 72999:
        return "DE14"
    
    # DE21 Oberbayern
    if 80000 <= plz_int <= 86999:
        return "DE21"
    if 90000 <= plz_int <= 90999:
        return "DE21"
    # DE22 Niederbayern
    if 84000 <= plz_int <= 84999:
        return "DE22"
    if 94000 <= plz_int <= 94499:
        return "DE22"
    # DE23 Oberpfalz
    if 85000 <= plz_int <= 85999:
        return "DE23"
    if 92000 <= plz_int <= 92999:
        return "DE23"
    # DE24 Oberfranken
    if 95000 <= plz_int <= 95499:
        return "DE24"
    # DE25 Mittelfranken
    if 90000 <= plz_int <= 91499:
        return "DE25"
    if 97000 <= plz_int <= 97999:
        return "DE25"
    # DE26 Unterfranken
    if 97000 <= plz_int <= 97699:
        return "DE26"
    # DE27 Schwaben
    if 86000 <= plz_int <= 86999:
        return "DE27"
    if 87000 <= plz_int <= 87999:
        return "DE27"
    
    # DE30 Berlin
    if 10000 <= plz_int <= 14199:
        return "DE30"
    
    # DE40 Brandenburg
    if 14400 <= plz_int <= 14999:
        return "DE40"
    if 15200 <= plz_int <= 15399:
        return "DE40"
    if 15500 <= plz_int <= 15899:
        return "DE40"
    if 16000 <= plz_int <= 16299:
        return "DE40"
    if 16500 <= plz_int <= 16599:
        return "DE40"
    if 17000 <= plz_int <= 17399:
        return "DE40"
    if 18000 <= plz_int <= 19999:
        return "DE40"
    
    # DE50 Bremen
    if 28000 <= plz_int <= 28999:
        return "DE50"
    
    # DE60 Hamburg
    if 20000 <= plz_int <= 22999:
        return "DE60"
    
    # DE70 Darmstadt
    if 64200 <= plz_int <= 64999:
        return "DE70"
    if 65000 <= plz_int <= 65999:
        return "DE70"
    if 66000 <= plz_int <= 66999:
        return "DE70"
    # DE71 Gießen
    if 35000 <= plz_int <= 35499:
        return "DE71"
    if 36000 <= plz_int <= 36999:
        return "DE71"
    # DE72 Kassel
    if 34000 <= plz_int <= 34999:
        return "DE72"
    if 37000 <= plz_int <= 37999:
        return "DE72"
    if 99000 <= plz_int <= 99999:
        return "DE72"
    
    # DE80 Mecklenburg-Vorpommern
    if 17000 <= plz_int <= 17999:
        return "DE80"
    if 19000 <= plz_int <= 19999:
        return "DE80"
    
    # DE91 Braunschweig
    if 38100 <= plz_int <= 38399:
        return "DE91"
    if 38400 <= plz_int <= 38699:
        return "DE91"
    if 38700 <= plz_int <= 38999:
        return "DE91"
    # DE92 Hannover
    if 30000 <= plz_int <= 31999:
        return "DE92"
    if 49000 <= plz_int <= 49999:
        return "DE92"
    # DE93 Lüneburg
    if 20000 <= plz_int <= 22999:
        return "DE93"
    if 26000 <= plz_int <= 27999:
        return "DE93"
    if 29000 <= plz_int <= 29999:
        return "DE93"
    # DE94 Weser-Ems
    if 26000 <= plz_int <= 26999:
        return "DE94"
    if 27000 <= plz_int <= 28999:
        return "DE94"
    if 49000 <= plz_int <= 49999:
        return "DE94"
    
    # DEA1 Düsseldorf
    if 40000 <= plz_int <= 41499:
        return "DEA1"
    if 45400 <= plz_int <= 45999:
        return "DEA1"
    # DEA2 Köln
    if 41500 <= plz_int <= 42999:
        return "DEA2"
    if 50000 <= plz_int <= 50999:
        return "DEA2"
    if 57000 <= plz_int <= 57999:
        return "DEA2"
    # DEA3 Münster
    if 44000 <= plz_int <= 44999:
        return "DEA3"
    if 46000 <= plz_int <= 46999:
        return "DEA3"
    # DEA4 Detmold
    if 32000 <= plz_int <= 33999:
        return "DEA4"
    if 33000 <= plz_int <= 33999:
        return "DEA4"
    if 44000 <= plz_int <= 44999:
        return "DEA4"
    # DEA5 Arnsberg
    if 35000 <= plz_int <= 35999:
        return "DEA5"
    if 57000 <= plz_int <= 57999:
        return "DEA5"
    if 58000 <= plz_int <= 59999:
        return "DEA5"
    
    # DEB1 Koblenz
    if 41000 <= plz_int <= 42999:
        return "DEB1"
    if 55000 <= plz_int <= 56999:
        return "DEB1"
    if 56000 <= plz_int <= 56999:
        return "DEB1"
    # DEB2 Trier
    if 54200 <= plz_int <= 54999:
        return "DEB2"
    # DEB3 Rheinhessen-Pfalz
    if 55000 <= plz_int <= 55999:
        return "DEB3"
    if 67000 <= plz_int <= 67999:
        return "DEB3"
    
    # DEC0 Saarland
    if 66000 <= plz_int <= 67999:
        return "DEC0"
    
    # DED2 Dresden
    if 1000 <= plz_int <= 1999:
        return "DED2"
    if 27000 <= plz_int <= 27999:
        return "DED2"
    if 99000 <= plz_int <= 99999:
        return "DED2"
    # DED4 Chemnitz
    if 8000 <= plz_int <= 9999:
        return "DED4"
    # DED5 Leipzig
    if 4000 <= plz_int <= 4999:
        return "DED5"
    if 6000 <= plz_int <= 6999:
        return "DED5"
    
    # DEE0 Sachsen-Anhalt
    if 6000 <= plz_int <= 6999:
        return "DEE0"
    if 38000 <= plz_int <= 39999:
        return "DEE0"
    if 99000 <= plz_int <= 99999:
        return "DEE0"
    
    # DEG0 Thüringen
    if 7000 <= plz_int <= 7999:
        return "DEG0"
    if 98000 <= plz_int <= 99999:
        return "DEG0"
    
    # Fallback: Versuche Bundesland-basierte Zuordnung
    # Schleswig-Holstein (01xxx - 02xxx) -> DE80 für SH+MV
    if 1000 <= plz_int <= 2999:
        return "DE80"
    
    # Niedersachsen (27xxx - 31xxx, 37xxx - 38xxx, 49xxx) -> DE94 (Weser-Ems)
    if 27000 <= plz_int <= 31999:
        return "DE94"
    if 37000 <= plz_int <= 38999:
        return "DE94"
    if 49000 <= plz_int <= 49999:
        return "DE94"
    
    # Nordrhein-Westfalen
    # 32xxx-33xxx, 40xxx-47xxx, 48xxx-49xxx
    if 32000 <= plz_int <= 33999:
        return "DEA4"  # Detmold
    if 40000 <= plz_int <= 47999:
        return "DEA1"  # Düsseldorf
    if 48000 <= plz_int <= 49999:
        return "DEA3"  # Münster
    
    # Hessen (34xxx - 36xxx, 40xxx - 42xxx (Teile), 55xxx - 65xxx)
    if 34000 <= plz_int <= 36999:
        return "DE72"  # Kassel
    if 37000 <= plz_int <= 39999:
        return "DE71"  # Gießen
    if 40000 <= plz_int <= 42499:
        return "DE70"  # Darmstadt
    if 55000 <= plz_int <= 65499:
        return "DE70"  # Darmstadt
    
    # Rheinland-Pfalz (41xxx - 43xxx, 54xxx - 57xxx)
    if 41000 <= plz_int <= 43999:
        return "DEB1"  # Koblenz
    if 54000 <= plz_int <= 56999:
        return "DEB1"  # Koblenz
    if 54200 <= plz_int <= 56999:
        return "DEB2"  # Trier
    if 67000 <= plz_int <= 67999:
        return "DEB3"  # Rheinhessen-Pfalz
    
    # Baden-Württemberg
    if 68000 <= plz_int <= 69999:
        return "DE12"  # Karlsruhe
    if 70000 <= plz_int <= 77999:
        return "DE11"  # Stuttgart
    if 78000 <= plz_int <= 79999:
        return "DE13"  # Freiburg
    
    # Bayern
    if 80000 <= plz_int <= 86999:
        return "DE21"  # Oberbayern
    if 87000 <= plz_int <= 87999:
        return "DE27"  # Schwaben
    if 90000 <= plz_int <= 92999:
        return "DE25"  # Mittelfranken
    if 93000 <= plz_int <= 93999:
        return "DE23"  # Oberpfalz
    if 94000 <= plz_int <= 96999:
        return "DE22"  # Niederbayern
    if 97000 <= plz_int <= 97999:
        return "DE26"  # Unterfranken
    
    return None


# ── Pydantic Models ────────────────────────────────────────────────────────

class HarvestAcceptancePositionIn(BaseModel):
    """Position für Harvest Acceptance (Abrechnungs-Grid)."""
    position_number: int = Field(..., ge=10, description="Positionsnummer (10, 15, 20, ...)")
    description: str = Field(..., min_length=1, max_length=200, description="Bezeichnung")
    is_printable: bool = Field(True, description="Soll auf Druckausgabe?")
    is_calculable: bool = Field(True, description="Soll berechnet werden?")
    lab_value_pct: Optional[float] = Field(None, ge=0, le=100, description="Laborwert (Prozent)")
    quantity_kg: Optional[float] = Field(None, ge=0, description="Menge (kg)")
    unit: Optional[str] = Field(None, max_length=20, description="Einheit")
    price_per_unit_eur: Optional[float] = Field(None, ge=0, description="Preis EUR pro Einheit")
    amount_eur: Optional[float] = Field(None, description="Betrag EUR")
    calculation_formula: Optional[str] = Field(None, description="Berechnungsformel")
    
    # NUTS-2 pro Position (für Mischladungen)
    origin_nuts2_code: Optional[str] = Field(None, max_length=10, description="NUTS-2-Code der Herkunft")
    nuts_version: Optional[str] = Field(default="NUTS 2024", max_length=20, description="NUTS-Version")
    origin_postal_code: Optional[str] = Field(None, max_length=10, description="PLZ der Herkunft")
    origin_city: Optional[str] = Field(None, max_length=100, description="Ort der Herkunft")
    origin_country_code: Optional[str] = Field(default="DE", max_length=2, description="Ländercode")
    
    # Artikel/Sorte (falls Position-spezifisch)
    article_id: Optional[str] = Field(None, description="Artikel-Nr. (falls abweichend)")
    variety_id: Optional[str] = Field(None, max_length=64, description="Sorte (falls abweichend)")
    
    @field_validator("origin_nuts2_code")
    @classmethod
    def validate_nuts2(cls, v: Optional[str]) -> Optional[str]:
        if v:
            return validate_nuts2_code(v)
        return v


class HarvestAcceptanceCreate(BaseModel):
    """Ernte-Annahme anlegen."""
    acceptance_number: Optional[str] = Field(None, max_length=50, description="Annahmeschein-Nummer (auto-generiert wenn leer)")
    branch_id: Optional[str] = Field(None, description="Niederlassung")
    warehouse_id: Optional[str] = Field(None, description="Lagerhalle")
    delivery_date: date = Field(..., description="Liefer-Datum")
    delivery_time: Optional[str] = Field(None, max_length=8, description="Uhrzeit (HH:MM)")
    sales_rep_id: Optional[str] = Field(None, max_length=64, description="VB (Vertreter)")
    weighing_ticket_id: Optional[str] = Field(None, description="Wiegesch.-Nr.")
    cost_center_id: Optional[str] = Field(None, max_length=64, description="Kostenstelle")
    
    # Kunden-Bereich
    customer_id: str = Field(..., description="Debitor-Kto.")
    contract_id: Optional[str] = Field(None, description="Kontrakt-Nr.")
    forwarder_id: Optional[str] = Field(None, description="Spediteur-Kto.")
    intermediate_dealer_id: Optional[str] = Field(None, description="Zw-Händler-Kto.")
    deviating_vat_id: Optional[str] = Field(None, max_length=20, description="Abweichende USTID")
    
    # ANLIEFERUNG Tab
    article_id: Optional[str] = Field(None, description="Artikel-Nr.")
    variety_id: Optional[str] = Field(None, max_length=64, description="Sorte")
    vehicle_plate: Optional[str] = Field(None, max_length=20, description="Fahrzeug-Kennzeichen")
    
    # NUTS-2 (Herkunft/Region der Erzeugung)
    origin_nuts2_code: Optional[str] = Field(None, max_length=10, description="NUTS-2-Code der Herkunft")
    nuts_version: Optional[str] = Field(default="NUTS 2024", max_length=20, description="NUTS-Version")
    origin_postal_code: Optional[str] = Field(None, max_length=10, description="PLZ der Herkunft (für Ableitung)")
    origin_city: Optional[str] = Field(None, max_length=100, description="Ort der Herkunft (für Ableitung)")
    origin_country_code: Optional[str] = Field(default="DE", max_length=2, description="Ländercode")
    is_sustainable_biomass: bool = Field(False, description="Nachhaltige Biomasse (für RED-II/ISCC/REDcert)")
    
    # Preisermittlung
    pricing_mode: Optional[PricingMode] = Field("spot_daily", description="Preismodell: fixed_contract / spot_daily / exchange_fix_later")
    price_source_id: Optional[str] = Field(None, description="Referenz auf DailyPrice oder Preisquelle")
    
    # VAT / Geschäftsmodell (praxisnahe Defaults)
    acceptance_mode: Optional[AcceptanceMode] = Field("PURCHASE_AT_DELIVERY_PTBF", description="STORAGE_ONLY / PURCHASE_AT_DELIVERY_PTBF / ADVANCE_ON_STORAGE")
    ownership_type: Optional[OwnershipType] = Field("OWN_STOCK", description="THIRD_PARTY_STOCK / OWN_STOCK")
    vat_event: Optional[VatEvent] = Field("NO_INVOICE", description="VAT-Ereignis: NO_INVOICE / PROVISIONAL_CREDIT_NOTE_CREATED / ...")
    advance_payment_amount_eur: Optional[float] = Field(None, ge=0, description="Anzahlungsbetrag (EUR) - für ADVANCE_ON_STORAGE")
    advance_payment_date: Optional[date] = Field(None, description="Anzahlungsdatum - für ADVANCE_ON_STORAGE")
    
    # Bemerkungen
    remarks: Optional[str] = Field(None, description="Bemerkungen")
    print_remarks_on_acceptance_note: bool = Field(False, description="Auf Annahmeschein drucken")
    print_remarks_on_settlement: bool = Field(False, description="Auf Abrechnung drucken")
    
    # Positionen (optional, für Mischladungen)
    positions: Optional[list[HarvestAcceptancePositionIn]] = Field(None, description="Abrechnungs-Positionen")
    
    @field_validator("origin_nuts2_code")
    @classmethod
    def validate_nuts2(cls, v: Optional[str]) -> Optional[str]:
        if v:
            return validate_nuts2_code(v)
        return v
    
    @model_validator(mode="after")
    def derive_nuts2_if_missing(self):
        """Leitet NUTS-2-Code aus PLZ ab, falls nicht angegeben."""
        if not self.origin_nuts2_code and self.origin_postal_code:
            derived = derive_nuts2_from_postal_code(self.origin_postal_code, self.origin_country_code or "DE")
            if derived:
                self.origin_nuts2_code = derived
        return self
    
    @model_validator(mode="after")
    def validate_pricing_mode(self):
        """
        Validiert pricing_mode gemäß praxisnahen Default-Entscheidungen:
        - fixed_contract ⇒ contract_id required
        - spot_daily ⇒ price_source_id required (oder daily_price_id)
        - exchange_fix_later ⇒ pricing_fixation_status + Referenz auf Börsen/Indexdaten
        """
        if self.pricing_mode == "fixed_contract" and not self.contract_id:
            raise ValueError("pricing_mode 'fixed_contract' erfordert contract_id")
        if self.pricing_mode == "spot_daily" and not self.price_source_id:
            # Warnung, aber nicht zwingend (kann auch aus daily_prices Tabelle geladen werden)
            pass
        if self.pricing_mode == "exchange_fix_later":
            # Optional: pricing_fixation_status und Börsen/Index-Referenz prüfen (Preismodul)
            pass
        return self


class HarvestAcceptanceUpdate(BaseModel):
    """Ernte-Annahme aktualisieren."""
    branch_id: Optional[str] = None
    warehouse_id: Optional[str] = None
    delivery_date: Optional[date] = None
    delivery_time: Optional[str] = Field(None, max_length=8)
    sales_rep_id: Optional[str] = Field(None, max_length=64)
    weighing_ticket_id: Optional[str] = None
    cost_center_id: Optional[str] = Field(None, max_length=64)
    contract_id: Optional[str] = None
    forwarder_id: Optional[str] = None
    intermediate_dealer_id: Optional[str] = None
    deviating_vat_id: Optional[str] = Field(None, max_length=20)
    article_id: Optional[str] = None
    variety_id: Optional[str] = Field(None, max_length=64)
    vehicle_plate: Optional[str] = Field(None, max_length=20)
    origin_nuts2_code: Optional[str] = Field(None, max_length=10)
    nuts_version: Optional[str] = Field(default=None, max_length=20)
    origin_postal_code: Optional[str] = Field(None, max_length=10)
    origin_city: Optional[str] = Field(None, max_length=100)
    origin_country_code: Optional[str] = Field(None, max_length=2)
    is_sustainable_biomass: Optional[bool] = None
    pricing_mode: Optional[PricingMode] = None
    price_source_id: Optional[str] = None
    acceptance_mode: Optional[AcceptanceMode] = None
    ownership_type: Optional[OwnershipType] = None
    vat_event: Optional[VatEvent] = None
    advance_payment_amount_eur: Optional[float] = None
    advance_payment_date: Optional[date] = None
    remarks: Optional[str] = None
    print_remarks_on_acceptance_note: Optional[bool] = None
    print_remarks_on_settlement: Optional[bool] = None
    
    @field_validator("origin_nuts2_code")
    @classmethod
    def validate_nuts2(cls, v: Optional[str]) -> Optional[str]:
        if v:
            return validate_nuts2_code(v)
        return v


class HarvestAcceptanceOut(BaseModel):
    """Ernte-Annahme Ausgabe."""
    model_config = {"from_attributes": True}

    id: str
    acceptance_number: str
    tenant_id: str
    branch_id: Optional[str]
    warehouse_id: Optional[str]
    delivery_date: date
    delivery_time: Optional[str]
    sales_rep_id: Optional[str]
    operator_id: str
    weighing_ticket_id: Optional[str]
    cost_center_id: Optional[str]
    customer_id: str
    contract_id: Optional[str]
    forwarder_id: Optional[str]
    intermediate_dealer_id: Optional[str]
    deviating_vat_id: Optional[str]
    article_id: Optional[str]
    variety_id: Optional[str]
    vehicle_plate: Optional[str]
    origin_nuts2_code: Optional[str]
    nuts_version: Optional[str]
    origin_postal_code: Optional[str]
    origin_city: Optional[str]
    origin_country_code: Optional[str]
    is_sustainable_biomass: bool = False
    release_status: str = "draft"
    pricing_mode: str = "spot_daily"
    price_source_id: Optional[str]
    acceptance_mode: Optional[str]
    ownership_type: Optional[str]
    vat_event: Optional[str]
    advance_payment_amount_eur: Optional[float]
    advance_payment_date: Optional[date]
    advance_invoice_id: Optional[str]
    provisional_invoice_number: Optional[str]
    invoice_id: Optional[str]
    invoice_number: Optional[str]
    stock_movement_id: Optional[str]
    quality_protocol_id: Optional[str]
    remarks: Optional[str]
    print_remarks_on_acceptance_note: bool = False
    print_remarks_on_settlement: bool = False
    total_net_amount_eur: Optional[float]
    total_vat_amount_eur: Optional[float]
    total_gross_amount_eur: Optional[float]
    vat_rate_percent: Optional[float]
    created_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_at: Optional[datetime]
    updated_by: Optional[str]


# ── API Endpoints ────────────────────────────────────────────────────────────

def _harvest_acceptance_to_dict_with_positions(acceptance: HarvestAcceptance, db: Session) -> dict:
    """Konvertiert HarvestAcceptance zu dict mit Positionen und optional article_name."""
    # Lade Positionen
    positions = db.query(HarvestAcceptancePosition).filter(
        HarvestAcceptancePosition.harvest_acceptance_id == acceptance.id
    ).order_by(HarvestAcceptancePosition.position_number).all()

    # Optional: Artikelnamen für Frontend mitschicken
    article_name: Optional[str] = None
    if acceptance.article_id:
        article = db.query(Article).filter(Article.id == acceptance.article_id).first()
        if article:
            article_name = article.name or (article.description[:100] if article.description else None)

    # Erstelle Response mit Positionen
    result = HarvestAcceptanceOut.model_validate(acceptance)
    result_dict = result.model_dump()
    result_dict["positions"] = [
        {
            "id": pos.id,
            "harvest_acceptance_id": pos.harvest_acceptance_id,
            "position_number": pos.position_number,
            "description": pos.description,
            "is_printable": pos.is_printable,
            "is_calculable": pos.is_calculable,
            "lab_value_pct": float(pos.lab_value_pct) if pos.lab_value_pct else None,
            "quantity_kg": float(pos.quantity_kg) if pos.quantity_kg else None,
            "unit": pos.unit,
            "price_per_unit_eur": float(pos.price_per_unit_eur) if pos.price_per_unit_eur else None,
            "amount_eur": float(pos.amount_eur) if pos.amount_eur else None,
            "calculation_formula": pos.calculation_formula,
        }
        for pos in positions
    ]
    if article_name is not None:
        result_dict["article_name"] = article_name
    return result_dict

def _get_user_id_from_request(request: Request) -> Optional[str]:
    """Hilfsfunktion zum Extrahieren der User-ID aus Request (für Audit)."""
    return get_user_id_from_request(request) or "system"


def _svc(db: Session, tenant_id: str) -> HarvestAcceptanceService:
    return HarvestAcceptanceService(db, tenant_id)


@router.post("/", response_model=HarvestAcceptanceOut, status_code=201)
async def create_harvest_acceptance(
    payload: HarvestAcceptanceCreate,
    request: Request,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Ernte-Annahme anlegen."""
    user_id = _get_user_id_from_request(request)
    try:
        return _svc(db, tenant_id).create_acceptance(payload, user_id)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.detail)
    except ConflictError as exc:
        raise HTTPException(status_code=409, detail=exc.detail)
    except ValidationFailedError as exc:
        raise HTTPException(status_code=422, detail=exc.detail)


@router.get("/", response_model=list[HarvestAcceptanceOut])
async def list_harvest_acceptances(
    customer_id: Optional[str] = Query(None, description="Filter nach Kunde"),
    contract_id: Optional[str] = Query(None, description="Filter nach Vertrag"),
    release_status: Optional[ReleaseStatus] = Query(None, description="Filter nach Freigabe-Status"),
    origin_nuts2_code: Optional[str] = Query(None, description="Filter nach NUTS-2-Code"),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Ernte-Annahmen auflisten."""
    return _svc(db, tenant_id).list_acceptances(
        customer_id=customer_id,
        contract_id=contract_id,
        release_status=release_status,
        origin_nuts2_code=origin_nuts2_code,
    )


@router.get("/last", response_model=Optional[HarvestAcceptanceOut])
async def get_last_harvest_acceptance(
    operator_id: Optional[str] = Query(None, description="Filter nach Operator-ID (Benutzer, der die Ernte-Annahme erstellt hat)"),
    customer_id: Optional[str] = Query(None, description="Filter nach Kunde"),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Holt die letzte Ernte-Annahme für einen Benutzer/Kunde (für 'Wie vorheriger AS' Funktionalität)."""
    return _svc(db, tenant_id).get_last_acceptance(operator_id=operator_id, customer_id=customer_id)


@router.get("/{acceptance_id}", response_model=HarvestAcceptanceOut)
async def get_harvest_acceptance(
    acceptance_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Ernte-Annahme abrufen inkl. Quality Protocol und Self-Billing Invoice."""
    try:
        return _svc(db, tenant_id).get_acceptance(acceptance_id)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.detail)


@router.put("/{acceptance_id}", response_model=HarvestAcceptanceOut)
async def update_harvest_acceptance(
    acceptance_id: str,
    payload: HarvestAcceptanceUpdate,
    request: Request,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Ernte-Annahme aktualisieren (nur im Status 'draft' oder 'provisional')."""
    user_id = _get_user_id_from_request(request)
    try:
        return _svc(db, tenant_id).update_acceptance(acceptance_id, payload.model_dump(exclude_unset=True), user_id)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.detail)
    except ValidationFailedError as exc:
        raise HTTPException(status_code=422, detail=exc.detail)


@router.delete("/{acceptance_id}", status_code=204)
async def delete_harvest_acceptance(
    acceptance_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    _: str = Depends(require_inventory_admin),
):
    """Ernte-Annahme löschen (nur Admin, nur im Status 'draft')."""
    try:
        _svc(db, tenant_id).delete_acceptance(acceptance_id)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.detail)
    except ValidationFailedError as exc:
        raise HTTPException(status_code=400, detail=exc.detail)


@router.post("/{acceptance_id}/calculate", response_model=dict)
async def calculate_harvest_settlement_endpoint(
    acceptance_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Berechnet alle Abrechnungs-Positionen für Ernte-Annahme."""
    try:
        return _svc(db, tenant_id).calculate_settlement(acceptance_id)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.detail)
    except ValidationFailedError as exc:
        raise HTTPException(status_code=400, detail=exc.detail)


@router.post("/{acceptance_id}/derive-nuts2", response_model=dict)
async def derive_nuts2_from_postal_code_endpoint(
    acceptance_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Leitet NUTS-2-Code aus PLZ ab (für bestehende Ernte-Annahme)."""
    try:
        return _svc(db, tenant_id).derive_nuts2(acceptance_id)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.detail)
    except ValidationFailedError as exc:
        raise HTTPException(status_code=400, detail=exc.detail)


@router.post("/{acceptance_id}/release", response_model=HarvestAcceptanceOut)
async def release_harvest_acceptance(
    acceptance_id: str,
    release_status: ReleaseStatus = Query(..., description="Neuer Freigabe-Status: provisional oder final"),
    create_stock_movement: bool = Query(True, description="Wareneingang automatisch erstellen?"),
    create_credit_note: bool = Query(False, description="Self-Billing Gutschrift automatisch erstellen (nur bei final)?"),
    request: Request = None,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Ernte-Annahme freigeben (vorläufig oder endgültig)."""
    user_id = _get_user_id_from_request(request) if request else "system"
    try:
        return _svc(db, tenant_id).release_acceptance(
            acceptance_id, release_status, create_stock_movement, create_credit_note, user_id
        )
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.detail)
    except ValidationFailedError as exc:
        raise HTTPException(status_code=400, detail=exc.detail)


@router.post("/{acceptance_id}/cancel", response_model=HarvestAcceptanceOut)
async def cancel_harvest_acceptance(
    acceptance_id: str,
    reason: str = Query(..., min_length=1, description="Pflichtbegründung für Stornierung"),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Ernte-Annahme stornieren. Blockiert wenn bereits endgültig freigegeben."""
    try:
        return _svc(db, tenant_id).cancel(acceptance_id, reason)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.detail)
    except ConflictError as exc:
        raise HTTPException(status_code=409, detail=exc.detail)
    except ValidationFailedError as exc:
        raise HTTPException(status_code=400, detail=exc.detail)


# ============================================================================
# QUALITÄTSPROTOKOLL-INTEGRATION
# ============================================================================

@router.post("/{acceptance_id}/qualitaetsprotokoll", response_model=dict)
async def create_qualitaetsprotokoll(
    acceptance_id: str,
    data: dict,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Erstelle Qualitätsprotokoll für Ernte-Annahme."""
    try:
        return _svc(db, tenant_id).create_quality_protocol_for_acceptance(acceptance_id, data)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.detail)
    except ValidationFailedError as exc:
        raise HTTPException(status_code=422, detail=exc.detail)


def _quality_protocol_to_qualitaetsprotokoll(protocol) -> dict:
    """Mappt QualityProtocol (Service/DB) auf das API-Format Qualitätsprotokoll (Laborwerte)."""
    ov = protocol.other_values or {}
    return {
        "id": protocol.id,
        "acceptance_id": protocol.harvest_acceptance_id,
        "protocol_number": protocol.protocol_number,
        "version": protocol.version,
        "erstellt_am": protocol.created_at.isoformat() if protocol.created_at else None,
        "qualitaetsdaten": {
            "feuchte_prozent": float(protocol.moisture_pct) if protocol.moisture_pct is not None else None,
            "protein_prozent": float(protocol.protein_pct) if protocol.protein_pct is not None else None,
            "fallzahl": ov.get("fallzahl"),
            "sedimentation": ov.get("sedimentation"),
            "besatz": float(protocol.impurities_pct) if protocol.impurities_pct is not None else ov.get("besatz"),
            "mykotoxine": float(protocol.mycotoxin_ppb) if protocol.mycotoxin_ppb is not None else ov.get("mykotoxine"),
            "schadstoffe": ov.get("schadstoffe"),
            "keimzahl": ov.get("keimzahl"),
            "glasbruch": ov.get("glasbruch"),
            "sensorik": ov.get("sensorik"),
            "hektolitergewicht_kg_hl": float(protocol.hl_weight_kg_per_hl) if protocol.hl_weight_kg_per_hl is not None else None,
        },
        "bewertung": "ok" if protocol.is_final else "none",
        "bemerkungen": None,
        "labor_code": None,
        "analysendatum": protocol.approved_at.date().isoformat() if protocol.approved_at else None,
    }


@router.get("/{acceptance_id}/qualitaetsprotokoll", response_model=dict)
async def get_qualitaetsprotokoll(
    acceptance_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Hole Qualitätsprotokoll für Ernte-Annahme."""
    try:
        return _svc(db, tenant_id).get_quality_protocol(acceptance_id)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.detail)


# ============================================================================
# FRACHTKOSTEN-BERECHNUNG
# ============================================================================

@router.post("/{acceptance_id}/frachtkosten", response_model=dict)
async def calculate_frachtkosten(
    acceptance_id: str,
    data: dict,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Berechne Frachtkosten für Lieferung."""
    try:
        return _svc(db, tenant_id).calculate_frachtkosten(acceptance_id, data)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.detail)
    except ValidationFailedError as exc:
        raise HTTPException(status_code=400, detail=exc.detail)


@router.get("/{acceptance_id}/frachtkosten", response_model=dict)
async def get_frachtkosten(
    acceptance_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Hole Frachtkosten für Ernte-Annahme."""
    try:
        return _svc(db, tenant_id).get_frachtkosten(acceptance_id)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.detail)

