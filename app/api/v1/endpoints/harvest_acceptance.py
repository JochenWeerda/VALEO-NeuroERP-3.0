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
from sqlalchemy import desc

from app.core.data_quality_enforcement import build_dq_error_detail, evaluate_harvest_acceptance_datensatz
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.core.security import get_user_id_from_request
from app.infrastructure.models import (
    HarvestAcceptance,
    HarvestAcceptancePosition,
    HarvestAcceptanceLine,
    SupplierTaxProfile,
    PriceAdjustmentRule,
    WeighingTicket,
    Customer,
    Article,
    AgrarContract,
    Warehouse,
    StockMovement,
)
from app.domains.inventory.api.inventory_auth import require_inventory_admin
from modules.agrar.services.harvest_calculator import (
    HarvestCalculationInput,
    HarvestCalculationResult,
    calculate_harvest_settlement,
)
from modules.agrar.services.drying_rule_engine import (
    DryingRuleRepository as _DryingRuleRepository,
)
from app.api.v1.endpoints.agrar_settlements import _DbDryingRuleRepo
from modules.agrar.services.quality_protocol_service import (
    get_latest_protocol,
    create_quality_protocol,
    QualityProtocolCreate,
)
from modules.agrar.repositories.quality_protocol_repo import QualityProtocolRepositoryImpl
from modules.agrar.services.daily_price_service import (
    get_price_for_date,
    DailyPriceFilter,
)
from modules.agrar.repositories.daily_price_repo import DailyPriceRepositoryImpl
from modules.agrar.services.self_billing_service import (
    create_credit_note,
    CreditNoteCreate,
)
from modules.agrar.repositories.self_billing_repo import SelfBillingRepositoryImpl
from modules.agrar.services.tax_profile_service import get_taxation_type_for_supplier
from modules.agrar.services.partie_service import generate_lot_number
from app.core.uuid7 import uuid7, uuid7_short_suffix

router = APIRouter()

ReleaseStatus = Literal["draft", "provisional", "final", "credit_note_created", "paid", "disputed", "cancelled"]
PricingMode = Literal["fixed_contract", "spot_daily", "exchange_fix_later"]
AcceptanceMode = Literal["STORAGE_ONLY", "PURCHASE_AT_DELIVERY_PTBF", "ADVANCE_ON_STORAGE"]
OwnershipType = Literal["THIRD_PARTY_STOCK", "OWN_STOCK"]
VatEvent = Literal["NO_INVOICE", "PROVISIONAL_CREDIT_NOTE_CREATED", "FINAL_CREDIT_NOTE_CREATED", "CORRECTION_ISSUED"]


def _build_harvest_acceptance_dq_datensatz(data: dict[str, object]) -> dict[str, object]:
    return {
        "annahme_nr": data.get("acceptance_number"),
        "kunde_id": data.get("customer_id"),
        "lieferdatum": str(data.get("delivery_date") or ""),
        "preismodell": data.get("pricing_mode") or "spot_daily",
        "annahmemodus": data.get("acceptance_mode") or "PURCHASE_AT_DELIVERY_PTBF",
        "land": data.get("origin_country_code") or "DE",
    }


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


@router.post("/", response_model=HarvestAcceptanceOut, status_code=201)
async def create_harvest_acceptance(
    payload: HarvestAcceptanceCreate,
    request: Request,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Ernte-Annahme anlegen."""
    acceptance_number = payload.acceptance_number
    if not acceptance_number:
        timestamp = datetime.utcnow()
        acceptance_number = f"HA-{timestamp.strftime('%Y%m%d')}-{uuid7_short_suffix()}"

    dq_result = evaluate_harvest_acceptance_datensatz(
        _build_harvest_acceptance_dq_datensatz(
            {
                "acceptance_number": acceptance_number,
                "customer_id": payload.customer_id,
                "delivery_date": payload.delivery_date,
                "pricing_mode": payload.pricing_mode,
                "acceptance_mode": payload.acceptance_mode,
                "origin_country_code": payload.origin_country_code,
            }
        )
    )
    if not dq_result.bestanden:
        raise HTTPException(status_code=422, detail=build_dq_error_detail("ErnteAnnahme", dq_result))
    # Prüfe Kunde
    customer = db.query(Customer).filter(Customer.id == payload.customer_id, Customer.tenant_id == tenant_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Prüfe Wiegeschein (falls angegeben)
    if payload.weighing_ticket_id:
        ticket = db.query(WeighingTicket).filter(WeighingTicket.id == payload.weighing_ticket_id, WeighingTicket.tenant_id == tenant_id).first()
        if not ticket:
            raise HTTPException(status_code=404, detail="Weighing ticket not found")
    
    # Prüfe Artikel (falls angegeben)
    if payload.article_id:
        article = db.query(Article).filter(Article.id == payload.article_id, Article.tenant_id == tenant_id).first()
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
    
    # Prüfe Vertrag (falls angegeben)
    if payload.contract_id:
        contract = db.query(AgrarContract).filter(AgrarContract.id == payload.contract_id, AgrarContract.tenant_id == tenant_id).first()
        if not contract:
            raise HTTPException(status_code=404, detail="Contract not found")
    
    # Prüfe Lagerhalle (falls angegeben)
    if payload.warehouse_id:
        warehouse = db.query(Warehouse).filter(Warehouse.id == payload.warehouse_id, Warehouse.tenant_id == tenant_id).first()
        if not warehouse:
            raise HTTPException(status_code=404, detail="Warehouse not found")
    
    # Generiere Annahmeschein-Nummer (falls nicht angegeben)
    acceptance_number = payload.acceptance_number
    if not acceptance_number:
        # Format: HA-YYYY-MMDD-HHMMSS oder HA-YYYY-XXXXX
        timestamp = datetime.utcnow()
        acceptance_number = f"HA-{timestamp.strftime('%Y%m%d')}-{uuid7_short_suffix()}"

    dq_result = evaluate_harvest_acceptance_datensatz(
        _build_harvest_acceptance_dq_datensatz(
            {
                "acceptance_number": acceptance_number,
                "customer_id": payload.customer_id,
                "delivery_date": payload.delivery_date,
                "pricing_mode": payload.pricing_mode,
                "acceptance_mode": payload.acceptance_mode,
                "origin_country_code": payload.origin_country_code,
            }
        )
    )
    if not dq_result.bestanden:
        raise HTTPException(status_code=422, detail=build_dq_error_detail("ErnteAnnahme", dq_result))
    
    # Prüfe auf Duplikat
    duplicate = (
        db.query(HarvestAcceptance)
        .filter(HarvestAcceptance.tenant_id == tenant_id, HarvestAcceptance.acceptance_number == acceptance_number)
        .first()
    )
    if duplicate:
        raise HTTPException(status_code=409, detail=f"Acceptance number {acceptance_number} already exists")
    
    user_id = _get_user_id_from_request(request)
    
    # Erstelle Harvest Acceptance
    acceptance = HarvestAcceptance(
        id=uuid7(),
        tenant_id=tenant_id,
        acceptance_number=acceptance_number,
        branch_id=payload.branch_id,
        warehouse_id=payload.warehouse_id,
        delivery_date=payload.delivery_date,
        delivery_time=payload.delivery_time,
        sales_rep_id=payload.sales_rep_id,
        operator_id=user_id,
        weighing_ticket_id=payload.weighing_ticket_id,
        cost_center_id=payload.cost_center_id,
        customer_id=payload.customer_id,
        contract_id=payload.contract_id,
        forwarder_id=payload.forwarder_id,
        intermediate_dealer_id=payload.intermediate_dealer_id,
        deviating_vat_id=payload.deviating_vat_id,
        article_id=payload.article_id,
        variety_id=payload.variety_id,
        vehicle_plate=payload.vehicle_plate,
        origin_nuts2_code=payload.origin_nuts2_code,
        nuts_version=payload.nuts_version or "NUTS 2024",
        origin_postal_code=payload.origin_postal_code,
        origin_city=payload.origin_city,
        origin_country_code=payload.origin_country_code or "DE",
        is_sustainable_biomass=payload.is_sustainable_biomass,
        pricing_mode=payload.pricing_mode or "spot_daily",
        price_source_id=payload.price_source_id,
        acceptance_mode=payload.acceptance_mode or "PURCHASE_AT_DELIVERY_PTBF",
        ownership_type=payload.ownership_type or "OWN_STOCK",
        vat_event=payload.vat_event or "NO_INVOICE",
        advance_payment_amount_eur=Decimal(str(payload.advance_payment_amount_eur)) if payload.advance_payment_amount_eur is not None else None,
        advance_payment_date=payload.advance_payment_date,
        release_status="draft",
        remarks=payload.remarks,
        print_remarks_on_acceptance_note=payload.print_remarks_on_acceptance_note,
        print_remarks_on_settlement=payload.print_remarks_on_settlement,
        created_by=user_id,
    )
    
    db.add(acceptance)
    db.flush()
    
    # Erstelle Positionen (falls vorhanden)
    if payload.positions:
        for pos_in in payload.positions:
            pos = HarvestAcceptancePosition(
                id=uuid7(),
                harvest_acceptance_id=acceptance.id,
                position_number=pos_in.position_number,
                description=pos_in.description,
                is_printable=pos_in.is_printable,
                is_calculable=pos_in.is_calculable,
                lab_value_pct=Decimal(str(pos_in.lab_value_pct)) if pos_in.lab_value_pct is not None else None,
                quantity_kg=Decimal(str(pos_in.quantity_kg)) if pos_in.quantity_kg is not None else None,
                unit=pos_in.unit,
                price_per_unit_eur=Decimal(str(pos_in.price_per_unit_eur)) if pos_in.price_per_unit_eur is not None else None,
                amount_eur=Decimal(str(pos_in.amount_eur)) if pos_in.amount_eur is not None else None,
                calculation_formula=pos_in.calculation_formula,
                origin_nuts2_code=pos_in.origin_nuts2_code,
                nuts_version=pos_in.nuts_version or "NUTS 2024",
                origin_postal_code=pos_in.origin_postal_code,
                origin_city=pos_in.origin_city,
                origin_country_code=pos_in.origin_country_code or "DE",
                article_id=pos_in.article_id,
                variety_id=pos_in.variety_id,
            )
            db.add(pos)
    
    db.commit()
    db.refresh(acceptance)
    
    return _harvest_acceptance_to_dict_with_positions(acceptance, db)


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
    query = db.query(HarvestAcceptance).filter(HarvestAcceptance.tenant_id == tenant_id)
    
    if customer_id:
        query = query.filter(HarvestAcceptance.customer_id == customer_id)
    if contract_id:
        query = query.filter(HarvestAcceptance.contract_id == contract_id)
    if release_status:
        query = query.filter(HarvestAcceptance.release_status == release_status)
    if origin_nuts2_code:
        query = query.filter(HarvestAcceptance.origin_nuts2_code == origin_nuts2_code.upper())
    
    items = query.order_by(HarvestAcceptance.delivery_date.desc(), HarvestAcceptance.acceptance_number.desc()).limit(500).all()
    return [HarvestAcceptanceOut.model_validate(item) for item in items]


@router.get("/last", response_model=Optional[HarvestAcceptanceOut])
async def get_last_harvest_acceptance(
    operator_id: Optional[str] = Query(None, description="Filter nach Operator-ID (Benutzer, der die Ernte-Annahme erstellt hat)"),
    customer_id: Optional[str] = Query(None, description="Filter nach Kunde"),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Holt die letzte Ernte-Annahme für einen Benutzer/Kunde (für 'Wie vorheriger AS' Funktionalität)."""
    query = db.query(HarvestAcceptance).filter(HarvestAcceptance.tenant_id == tenant_id)
    
    if operator_id:
        query = query.filter(HarvestAcceptance.operator_id == operator_id)
    
    if customer_id:
        query = query.filter(HarvestAcceptance.customer_id == customer_id)
    
    acceptance = query.order_by(HarvestAcceptance.created_at.desc()).first()
    
    if not acceptance:
        return None
    
    return _harvest_acceptance_to_dict_with_positions(acceptance, db)


@router.get("/{acceptance_id}", response_model=HarvestAcceptanceOut)
async def get_harvest_acceptance(
    acceptance_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """
    Ernte-Annahme abrufen.
    
    Lädt automatisch:
    - Quality Protocol (falls vorhanden)
    - Self-Billing Invoice (falls vorhanden)
    """
    acceptance = db.query(HarvestAcceptance).filter(HarvestAcceptance.id == acceptance_id, HarvestAcceptance.tenant_id == tenant_id).first()
    if not acceptance:
        raise HTTPException(status_code=404, detail="Harvest acceptance not found")
    
    # Lade Quality Protocol (falls vorhanden)
    if not acceptance.quality_protocol_id:
        quality_repo = QualityProtocolRepositoryImpl(db)
        try:
            protocol = get_latest_protocol(quality_repo, acceptance_id)
            if protocol:
                acceptance.quality_protocol_id = protocol.id
                db.commit()
        except:
            pass  # Kein Protokoll vorhanden, kein Fehler
    
    result = _harvest_acceptance_to_dict_with_positions(acceptance, db)
    
    # Lade Self-Billing Invoice (falls vorhanden)
    if acceptance.invoice_id:
        billing_repo = SelfBillingRepositoryImpl(db)
        invoice = billing_repo.get_invoice_by_id(acceptance.invoice_id)
        if invoice:
            result["invoice"] = {
                "invoice_number": invoice.invoice_number,
                "status": invoice.status,
                "dispute_status": invoice.dispute_status,
                "total_gross_amount_eur": float(invoice.total_gross_amount_eur),
            }
    
    return result


@router.put("/{acceptance_id}", response_model=HarvestAcceptanceOut)
async def update_harvest_acceptance(
    acceptance_id: str,
    payload: HarvestAcceptanceUpdate,
    request: Request,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Ernte-Annahme aktualisieren (nur im Status 'draft' oder 'provisional')."""
    acceptance = db.query(HarvestAcceptance).filter(HarvestAcceptance.id == acceptance_id, HarvestAcceptance.tenant_id == tenant_id).first()
    if not acceptance:
        raise HTTPException(status_code=404, detail="Harvest acceptance not found")
    
    # Prüfe Status (nur Draft/Provisional dürfen geändert werden)
    if acceptance.release_status not in ("draft", "provisional"):
        raise HTTPException(status_code=400, detail=f"Cannot update harvest acceptance in status '{acceptance.release_status}'. Only 'draft' or 'provisional' can be updated.")
    
    update_data = payload.model_dump(exclude_unset=True)
    effective_data = {
        "acceptance_number": acceptance.acceptance_number,
        "customer_id": acceptance.customer_id,
        "delivery_date": update_data.get("delivery_date", acceptance.delivery_date),
        "pricing_mode": update_data.get("pricing_mode", acceptance.pricing_mode),
        "acceptance_mode": update_data.get("acceptance_mode", acceptance.acceptance_mode),
        "origin_country_code": update_data.get("origin_country_code", acceptance.origin_country_code),
    }
    dq_result = evaluate_harvest_acceptance_datensatz(_build_harvest_acceptance_dq_datensatz(effective_data))
    if not dq_result.bestanden:
        raise HTTPException(status_code=422, detail=build_dq_error_detail("ErnteAnnahme", dq_result))

    user_id = _get_user_id_from_request(request)

    # Aktualisiere Felder
    for key, value in update_data.items():
        if hasattr(acceptance, key):
            setattr(acceptance, key, value)
    
    acceptance.updated_by = user_id
    acceptance.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(acceptance)
    
    return HarvestAcceptanceOut.model_validate(acceptance)


@router.delete("/{acceptance_id}", status_code=204)
async def delete_harvest_acceptance(
    acceptance_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    _: str = Depends(require_inventory_admin),  # Nur Admin kann löschen
):
    """Ernte-Annahme löschen (nur Admin, nur im Status 'draft')."""
    acceptance = db.query(HarvestAcceptance).filter(HarvestAcceptance.id == acceptance_id, HarvestAcceptance.tenant_id == tenant_id).first()
    if not acceptance:
        raise HTTPException(status_code=404, detail="Harvest acceptance not found")
    
    if acceptance.release_status != "draft":
        raise HTTPException(status_code=400, detail=f"Cannot delete harvest acceptance in status '{acceptance.release_status}'. Only 'draft' can be deleted.")
    
    db.delete(acceptance)
    db.commit()


@router.post("/{acceptance_id}/calculate", response_model=dict)
async def calculate_harvest_settlement_endpoint(
    acceptance_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """
    Berechnet alle Abrechnungs-Positionen für Ernte-Annahme.
    
    Liest Daten aus:
    - Wiegeschein (Nettogewicht)
    - Laborwerte (Windabgang, Besatz, Feuchte, HL-Gewicht)
    - Eingaben (Lagergeld, Frachtkosten, Wiegegebühren)
    - Vertrag/Artikel (Preis, MWSt-Satz)
    
    Gibt berechnete Positionen und Summen zurück.
    """
    acceptance = db.query(HarvestAcceptance).filter(HarvestAcceptance.id == acceptance_id, HarvestAcceptance.tenant_id == tenant_id).first()
    if not acceptance:
        raise HTTPException(status_code=404, detail="Harvest acceptance not found")
    
    # Hole Nettogewicht aus Wiegeschein
    delivered_quantity_kg = Decimal("0")
    if acceptance.weighing_ticket_id:
        ticket = db.query(WeighingTicket).filter(WeighingTicket.id == acceptance.weighing_ticket_id).first()
        if ticket and ticket.net_weight:
            delivered_quantity_kg = ticket.net_weight
        else:
            raise HTTPException(status_code=400, detail="Weighing ticket has no net weight")
    else:
        raise HTTPException(status_code=400, detail="Weighing ticket is required for calculation")
    
    # Hole Laborwerte aus Positionen, Wiegeschein oder Qualitätsprotokoll
    windage_pct = None
    impurities_pct = None
    moisture_pct = None
    hl_weight_kg_per_hl = None
    
    # Versuche aus Wiegeschein zu laden
    if acceptance.weighing_ticket_id:
        ticket = db.query(WeighingTicket).filter(WeighingTicket.id == acceptance.weighing_ticket_id).first()
        if ticket:
            moisture_pct = ticket.moisture_pct
            impurities_pct = ticket.impurities_pct
            hl_weight_kg_per_hl = ticket.hl_weight
    
    # Hole Eingaben aus Positionen
    positions = db.query(HarvestAcceptancePosition).filter(
        HarvestAcceptancePosition.harvest_acceptance_id == acceptance_id
    ).all()
    
    storage_fee_per_month = None
    storage_months = None
    freight_costs = None
    weighing_fees = None
    storage_shrinkage_pct = None
    
    for pos in positions:
        if pos.position_number == 15 and pos.lab_value_pct:  # Windabgang
            windage_pct = pos.lab_value_pct
        elif pos.position_number == 20 and pos.lab_value_pct:  # Besatz
            impurities_pct = pos.lab_value_pct
        elif pos.position_number == 40 and pos.lab_value_pct:  # Feuchte
            moisture_pct = pos.lab_value_pct
        elif pos.position_number == 60 and pos.quantity_kg:  # HL-Gewicht
            hl_weight_kg_per_hl = pos.quantity_kg
        elif pos.position_number == 63 and pos.lab_value_pct:  # Lagerschwund
            storage_shrinkage_pct = pos.lab_value_pct
        elif pos.position_number == 75 and pos.amount_eur:  # Lagergeld
            storage_fee_per_month = pos.amount_eur
            if storage_months is None:
                storage_months = 1  # Default; kann später aus separatem Feld/Berechnung kommen
        elif pos.position_number == 78 and pos.amount_eur:  # Frachtkosten
            freight_costs = pos.amount_eur
        elif pos.position_number == 80 and pos.amount_eur:  # Wiegegebühren
            weighing_fees = pos.amount_eur
    
    # Warnungen sammeln
    warnings: list[str] = []
    
    # Hole Preis aus Vertrag, Tagespreis oder Artikel
    unit_price_eur_per_ton = None
    crop_code = None
    price_source = "unknown"
    
    if acceptance.contract_id:
        contract = db.query(AgrarContract).filter(AgrarContract.id == acceptance.contract_id).first()
        if contract:
            if contract.pricing_model == "fixed" and contract.fixed_price:
                unit_price_eur_per_ton = contract.fixed_price
                price_source = "contract_fixed"
            elif contract.pricing_model == "follow":
                # Tagespreis aus daily_prices Tabelle ermitteln
                from modules.agrar.services.daily_price_service import DailyPriceFilter
                from modules.agrar.repositories.daily_price_repo import DailyPriceRepositoryImpl
                
                repo = DailyPriceRepositoryImpl(db)
                price_filter = DailyPriceFilter(
                    tenant_id=acceptance.tenant_id,
                    article_id=acceptance.article_id,
                    price_date=acceptance.weighing_date or acceptance.calculated_date
                )
                daily_price = repo.find_price(price_filter)
                
                if daily_price:
                    unit_price_eur_per_ton = float(daily_price.price_eur_per_ton)
                    price_source = "contract_daily_price"
                # Wenn kein Tagespreis gefunden, Fallback auf Artikel-Preis
            elif contract.pricing_model == "pool":
                # Pool-Preis: Durchschnitt der letzten X Tage
                from datetime import timedelta
                pool_days = getattr(contract, 'pool_days', 30) or 30
                pool_start = (acceptance.weighing_date or acceptance.calculated_date) - timedelta(days=pool_days)
                pool_end = acceptance.weighing_date or acceptance.calculated_date
                
                price_filter = DailyPriceFilter(
                    tenant_id=acceptance.tenant_id,
                    article_id=acceptance.article_id,
                )
                prices = repo.get_price_history(
                    tenant_id=acceptance.tenant_id,
                    article_id=acceptance.article_id,
                    from_date=pool_start,
                    to_date=pool_end,
                    limit=100
                )
                if prices:
                    avg_price = sum(float(p.price_eur_per_ton) for p in prices) / len(prices)
                    unit_price_eur_per_ton = avg_price
                    price_source = "contract_pool"
    
    # Fallback: Artikel-Preis
    if not unit_price_eur_per_ton and acceptance.article_id:
        article = db.query(Article).filter(Article.id == acceptance.article_id).first()
        if article:
            # Versuche crop_code aus warengruppe abzuleiten (Mapping)
            if article.warengruppe:
                # Einfaches Mapping: warengruppe → crop_code
                warengruppe_upper = article.warengruppe.upper()
                crop_mapping = {
                    "MAIS": "MAIZE",
                    "WEIZEN": "WHEAT",
                    "GERSTE": "BARLEY",
                    "HAFER": "OATS",
                    "RAPS": "RAPESEED",
                    "ACKERBOHNE": "FIELD_BEANS",
                    "ERBSE": "PEAS",
                    "LUPINE": "LUPINS",
                }
                crop_code = crop_mapping.get(warengruppe_upper)
            
            # Fallback: Artikel-Verkaufspreis (wenn kein Vertragspreis)
            if not unit_price_eur_per_ton and article.sales_price:
                unit_price_eur_per_ton = article.sales_price
                price_source = "article_sales_price"
    
    # Hole MWSt-Satz aus Artikel oder Kunde
    vat_rate_percent = None
    if acceptance.article_id:
        article = db.query(Article).filter(Article.id == acceptance.article_id).first()
        if article and article.mehrwertsteuer_prozent:
            vat_rate_percent = article.mehrwertsteuer_prozent
    
    # Erstelle Drying Rule Repository (falls crop_code vorhanden)
    drying_repo = None
    use_drying_rule_engine = False
    if crop_code and moisture_pct:
        try:
            drying_repo = _DbDryingRuleRepo(db, tenant_id=tenant_id)
            use_drying_rule_engine = True
        except Exception:
            pass  # Fallback auf vereinfachte Berechnung
    
    # Erstelle Berechnungs-Input
    calc_input = HarvestCalculationInput(
        delivered_quantity_kg=delivered_quantity_kg,
        windage_pct=Decimal(str(windage_pct)) if windage_pct else None,
        impurities_pct=Decimal(str(impurities_pct)) if impurities_pct else None,
        moisture_pct=Decimal(str(moisture_pct)) if moisture_pct else None,
        hl_weight_kg_per_hl=Decimal(str(hl_weight_kg_per_hl)) if hl_weight_kg_per_hl else None,
        storage_shrinkage_pct=Decimal(str(storage_shrinkage_pct)) if storage_shrinkage_pct else None,
        storage_fee_per_month=Decimal(str(storage_fee_per_month)) if storage_fee_per_month else None,
        storage_months=storage_months,
        freight_costs=Decimal(str(freight_costs)) if freight_costs else None,
        weighing_fees=Decimal(str(weighing_fees)) if weighing_fees else None,
        unit_price_eur_per_ton=Decimal(str(unit_price_eur_per_ton)) if unit_price_eur_per_ton else None,
        use_drying_rule_engine=use_drying_rule_engine,
        crop_code=crop_code,
        site_id=acceptance.warehouse_id,  # Standort aus Lagerhalle
        contract_id=acceptance.contract_id,
        customer_id=acceptance.customer_id,
        calc_date=acceptance.delivery_date,
        drying_repo=drying_repo,
    )
    
    # Warnung, wenn kein Preis gefunden
    if not unit_price_eur_per_ton:
        warnings.append("Kein Preis gefunden. Bitte manuell eingeben oder Vertrag/Artikel prüfen.")
    
    # Berechne
    result = calculate_harvest_settlement(calc_input, vat_rate_percent=Decimal(str(vat_rate_percent)) if vat_rate_percent else None)
    
    # Füge Warnungen hinzu
    if warnings:
        result.warnings.extend(warnings)
    
    # Aktualisiere Summen in HarvestAcceptance
    acceptance.total_net_amount_eur = result.total_net_amount_eur
    acceptance.total_vat_amount_eur = result.total_vat_amount_eur
    acceptance.total_gross_amount_eur = result.total_gross_amount_eur
    acceptance.vat_rate_percent = result.vat_rate_percent
    
    # Aktualisiere Positionen mit berechneten Werten
    for pos_result in result.positions:
        existing_pos = next(
            (p for p in positions if p.position_number == pos_result.position_number),
            None
        )
        if existing_pos:
            if pos_result.quantity_kg is not None:
                existing_pos.quantity_kg = pos_result.quantity_kg
            if pos_result.quantity_pct is not None:
                existing_pos.lab_value_pct = pos_result.quantity_pct
            if pos_result.amount_eur is not None:
                existing_pos.amount_eur = pos_result.amount_eur
            if pos_result.calculation_formula:
                existing_pos.calculation_formula = pos_result.calculation_formula
        else:
            # Erstelle neue Position
            new_pos = HarvestAcceptancePosition(
                id=uuid7(),
                harvest_acceptance_id=acceptance_id,
                position_number=pos_result.position_number,
                description=pos_result.description,
                quantity_kg=pos_result.quantity_kg,
                lab_value_pct=pos_result.quantity_pct,
                amount_eur=pos_result.amount_eur,
                unit=pos_result.unit,
                calculation_formula=pos_result.calculation_formula,
                is_calculable=True,
                is_printable=True,
            )
            db.add(new_pos)
    
    db.commit()
    db.refresh(acceptance)
    
    # Rückgabe als JSON
    return {
        "acceptance_id": acceptance_id,
        "positions": [
            {
                "position_number": p.position_number,
                "description": p.description,
                "quantity_kg": float(p.quantity_kg) if p.quantity_kg else None,
                "quantity_pct": float(p.quantity_pct) if p.quantity_pct else None,
                "amount_eur": float(p.amount_eur) if p.amount_eur else None,
                "unit": p.unit,
                "calculation_formula": p.calculation_formula,
            }
            for p in result.positions
        ],
        "total_net_amount_eur": float(result.total_net_amount_eur),
        "total_vat_amount_eur": float(result.total_vat_amount_eur),
        "total_gross_amount_eur": float(result.total_gross_amount_eur),
        "vat_rate_percent": float(result.vat_rate_percent) if result.vat_rate_percent else None,
        "warnings": result.warnings,
        "price_source": price_source if 'price_source' in locals() else "unknown",
    }


@router.post("/{acceptance_id}/derive-nuts2", response_model=dict)
async def derive_nuts2_from_postal_code_endpoint(
    acceptance_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """
    Leitet NUTS-2-Code aus PLZ ab (für bestehende Ernte-Annahme).
    Nützlich, wenn PLZ nachträglich eingegeben wird.
    """
    acceptance = db.query(HarvestAcceptance).filter(HarvestAcceptance.id == acceptance_id, HarvestAcceptance.tenant_id == tenant_id).first()
    if not acceptance:
        raise HTTPException(status_code=404, detail="Harvest acceptance not found")
    
    if not acceptance.origin_postal_code:
        raise HTTPException(status_code=400, detail="Postal code (origin_postal_code) is required to derive NUTS-2 code")
    
    derived = derive_nuts2_from_postal_code(acceptance.origin_postal_code, acceptance.origin_country_code or "DE")
    
    if derived:
        acceptance.origin_nuts2_code = derived
        db.commit()
        return {"origin_nuts2_code": derived, "nuts_version": acceptance.nuts_version or "NUTS 2024", "message": "NUTS-2 code derived successfully"}
    else:
        return {"origin_nuts2_code": None, "message": "Could not derive NUTS-2 code from postal code. Please enter manually."}


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
    """
    Ernte-Annahme freigeben (vorläufig oder endgültig).
    
    Bei Freigabe wird automatisch:
    - Status aktualisiert
    - Wareneingang (Stock Movement) erstellt (wenn create_stock_movement=true)
    - Ware wird als "Sperrbestand" gebucht, bis Qualitätsfreigabe final ist
    """
    acceptance = db.query(HarvestAcceptance).filter(HarvestAcceptance.id == acceptance_id, HarvestAcceptance.tenant_id == tenant_id).first()
    if not acceptance:
        raise HTTPException(status_code=404, detail="Harvest acceptance not found")
    
    # Prüfe Status-Übergang
    if acceptance.release_status == "final":
        raise HTTPException(status_code=400, detail="Harvest acceptance is already final")
    if acceptance.release_status == "cancelled":
        raise HTTPException(status_code=400, detail="Cannot release cancelled harvest acceptance")
    
    if release_status not in ("provisional", "final"):
        raise HTTPException(status_code=400, detail="release_status must be 'provisional' or 'final'")
    
    user_id = _get_user_id_from_request(request) if request else "system"
    
    # Hole Nettogewicht (für Stock Movement und Partie/Charge)
    net_weight_kg = Decimal("0")
    if acceptance.weighing_ticket_id:
        ticket = db.query(WeighingTicket).filter(WeighingTicket.id == acceptance.weighing_ticket_id).first()
        if ticket and ticket.net_weight:
            net_weight_kg = ticket.net_weight
    else:
        positions = db.query(HarvestAcceptancePosition).filter(
            HarvestAcceptancePosition.harvest_acceptance_id == acceptance_id,
            HarvestAcceptancePosition.position_number == 10,  # Angelieferte Menge
        ).all()
        if positions:
            net_weight_kg = sum(pos.quantity_kg or Decimal("0") for pos in positions)
    
    # Erstelle Wareneingang (Stock Movement), wenn gewünscht und noch nicht vorhanden
    if create_stock_movement and not acceptance.stock_movement_id:
        if not acceptance.article_id:
            raise HTTPException(status_code=400, detail="Article ID is required to create stock movement")
        if not acceptance.warehouse_id:
            raise HTTPException(status_code=400, detail="Warehouse ID is required to create stock movement")
        
        if net_weight_kg <= 0:
            raise HTTPException(status_code=400, detail="Net weight must be > 0 to create stock movement")
        
        # Aktuellen Bestand aus letztem StockMovement für Artikel+Lager ermitteln
        last_movement = (
            db.query(StockMovement)
            .filter(
                StockMovement.article_id == acceptance.article_id,
                StockMovement.warehouse_id == acceptance.warehouse_id,
                StockMovement.tenant_id == tenant_id,
            )
            .order_by(desc(StockMovement.movement_date), desc(StockMovement.created_at))
            .first()
        )
        previous_stock = (last_movement.new_stock if last_movement else Decimal("0")) or Decimal("0")
        new_stock = previous_stock + net_weight_kg

        # Erstelle Stock Movement (Wareneingang in Sperrbestand)
        stock_movement = StockMovement(
            id=uuid7(),
            tenant_id=tenant_id,
            article_id=acceptance.article_id,
            warehouse_id=acceptance.warehouse_id,
            movement_type="in",
            quantity=net_weight_kg,
            unit="kg",
            movement_date=acceptance.delivery_date,
            reference_number=acceptance.acceptance_number,
            movement_number=f"HA-{acceptance.acceptance_number}",
            notes=f"Wareneingang aus Ernte-Annahme {acceptance.acceptance_number}",
            booking_user=user_id,
            auto_created=True,
            weighing_ticket_id=acceptance.weighing_ticket_id,
            agrar_contract_id=acceptance.contract_id,
            # Sperrbestand: ownership_type könnte "quarantine" sein, falls vorhanden
            ownership_type="owned",
            previous_stock=previous_stock,
            new_stock=new_stock,
            storage_fee_relevant=False,  # Wird später bei "endgültig" aktiviert
        )
        db.add(stock_movement)
        db.flush()
        
        acceptance.stock_movement_id = stock_movement.id
    
    # Aktualisiere Status
    acceptance.release_status = release_status
    acceptance.updated_by = user_id
    acceptance.updated_at = datetime.utcnow()
    
    # Erstelle Partie/Charge (wenn final und noch nicht vorhanden)
    if release_status == "final":
        # Prüfe, ob bereits HarvestAcceptanceLines vorhanden
        existing_lines = db.query(HarvestAcceptanceLine).filter(
            HarvestAcceptanceLine.harvest_acceptance_id == acceptance_id
        ).count()
        
        if existing_lines == 0:
            # Erstelle automatisch eine Line mit generierter Partie-Nummer
            lot_id = generate_lot_number(db, acceptance_id, tenant_id)
            line = HarvestAcceptanceLine(
                id=uuid7(),
                tenant_id=tenant_id,
                harvest_acceptance_id=acceptance_id,
                line_number=1,
                lot_id=lot_id,
                qty_kg_allocated=net_weight_kg,
            )
            db.add(line)
    
    # Erstelle Self-Billing Gutschrift (wenn gewünscht und final)
    if create_credit_note and release_status == "final" and not acceptance.invoice_id:
        if not acceptance.total_gross_amount_eur:
            raise HTTPException(status_code=400, detail="Cannot create credit note: total_gross_amount_eur is not set. Please calculate settlement first.")
        
        # Hole MWSt-Satz
        vat_rate_percent = Decimal("0")
        if acceptance.vat_rate_percent:
            vat_rate_percent = acceptance.vat_rate_percent
        else:
            # Fallback: Standard-MWSt
            vat_rate_percent = Decimal("19.0")
        
        # Erstelle Gutschrift
        billing_repo = SelfBillingRepositoryImpl(db)
        credit_note_input = CreditNoteCreate(
            tenant_id=tenant_id,
            harvest_acceptance_id=acceptance_id,
            total_net_amount_eur=acceptance.total_net_amount_eur or Decimal("0"),
            total_vat_amount_eur=acceptance.total_vat_amount_eur or Decimal("0"),
            total_gross_amount_eur=acceptance.total_gross_amount_eur,
            vat_rate_percent=vat_rate_percent,
            created_by=user_id,
        )
        
        # Hole Taxation Type aus Supplier Tax Profile
        taxation_type = "regular"  # Default
        if acceptance.customer_id:
            # Bei Ernte-Annahme ist customer_id der Lieferant (Supplier)
            taxation_type = get_taxation_type_for_supplier(
                db=db,
                supplier_id=acceptance.customer_id,
                tenant_id=tenant_id,
                effective_date=acceptance.delivery_date,
            )
        
        invoice = create_credit_note(billing_repo, credit_note_input, taxation_type=taxation_type)
        acceptance.invoice_id = invoice.id
        acceptance.release_status = "credit_note_created"
    
    db.commit()
    db.refresh(acceptance)
    
    return _harvest_acceptance_to_dict_with_positions(acceptance, db)


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
    """
    Erstelle Qualitätsprotokoll für Ernte-Annahme.
    Speichert Laborwerte in domain_inventory.quality_protocols und setzt quality_protocol_id.
    """
    from datetime import datetime
    
    acceptance = db.query(HarvestAcceptance).filter(
        HarvestAcceptance.id == acceptance_id,
        HarvestAcceptance.tenant_id == tenant_id
    ).first()
    
    if not acceptance:
        raise HTTPException(status_code=404, detail="Ernte-Annahme nicht gefunden")
    
    qd = data.get("qualitaetsdaten") or data
    create_input = QualityProtocolCreate(
        tenant_id=tenant_id,
        harvest_acceptance_id=acceptance_id,
        moisture_pct=Decimal(str(qd["feuchte_prozent"])) if qd.get("feuchte_prozent") is not None else None,
        protein_pct=Decimal(str(qd["protein_prozent"])) if qd.get("protein_prozent") is not None else None,
        impurities_pct=Decimal(str(qd["besatz"])) if qd.get("besatz") is not None else None,
        mycotoxin_ppb=Decimal(str(qd["mykotoxine"])) if qd.get("mykotoxine") is not None else None,
        hl_weight_kg_per_hl=Decimal(str(qd["hektolitergewicht_kg_hl"])) if qd.get("hektolitergewicht_kg_hl") is not None else None,
        other_values={
            "fallzahl": qd.get("fallzahl"),
            "sedimentation": qd.get("sedimentation"),
            "schadstoffe": qd.get("schadstoffe"),
            "keimzahl": qd.get("keimzahl"),
            "glasbruch": qd.get("glasbruch"),
            "sensorik": qd.get("sensorik"),
        } if any(qd.get(k) is not None for k in ("fallzahl", "sedimentation", "schadstoffe", "keimzahl", "glasbruch", "sensorik")) else None,
        source_type="manual",
        created_by=None,
    )
    quality_repo = QualityProtocolRepositoryImpl(db)
    protocol = create_quality_protocol(quality_repo, create_input)
    acceptance.quality_protocol_id = protocol.id
    bewertung = data.get("bewertung", "none")
    if bewertung == "ok":
        acceptance.quality_status = "approved"
    elif bewertung == "warning":
        acceptance.quality_status = "conditional"
    elif bewertung == "critical":
        acceptance.quality_status = "rejected"
    db.commit()
    
    qualitaetsprotokoll = _quality_protocol_to_qualitaetsprotokoll(protocol)
    qualitaetsprotokoll["bewertung"] = bewertung
    qualitaetsprotokoll["bemerkungen"] = data.get("bemerkungen")
    qualitaetsprotokoll["labor_code"] = data.get("labor_code")
    qualitaetsprotokoll["analysendatum"] = data.get("analysendatum")
    return {
        "message": "Qualitätsprotokoll erstellt",
        "qualitaetsprotokoll": qualitaetsprotokoll,
        "quality_status": getattr(acceptance, "quality_status", None),
    }


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
    """Hole Qualitätsprotokoll für Ernte-Annahme. Laborwerte aus quality_protocol_id (QualityProtocol) oder Legacy-JSON."""
    acceptance = db.query(HarvestAcceptance).filter(
        HarvestAcceptance.id == acceptance_id,
        HarvestAcceptance.tenant_id == tenant_id
    ).first()
    
    if not acceptance:
        raise HTTPException(status_code=404, detail="Ernte-Annahme nicht gefunden")
    
    if acceptance.quality_protocol_id:
        quality_repo = QualityProtocolRepositoryImpl(db)
        protocol = quality_repo.get_by_id(acceptance.quality_protocol_id)
        if protocol:
            return _quality_protocol_to_qualitaetsprotokoll(protocol)
    
    legacy = getattr(acceptance, "quality_protocol", None)
    if legacy:
        return legacy
    
    raise HTTPException(status_code=404, detail="Kein Qualitätsprotokoll vorhanden")


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
    """
    Berechne Frachtkosten für Lieferung.
    
    Parameter:
    - entfernung_km: Entfernung in Kilometer
    - gewicht_kg: Gewicht der Lieferung
    - tariff_id: Tarif-ID (optional)
    """
    from decimal import Decimal
    
    acceptance = db.query(HarvestAcceptance).filter(
        HarvestAcceptance.id == acceptance_id,
        HarvestAcceptance.tenant_id == tenant_id
    ).first()
    
    if not acceptance:
        raise HTTPException(status_code=404, detail="Ernte-Annahme nicht gefunden")
    
    # Hole Parameter
    entfernung_km = data.get("entfernung_km", 0)
    gewicht_kg = data.get("gewicht_kg")
    tariff_id = data.get("tariff_id")
    
    # Fallback: Nimm Gewicht aus Acceptance
    if not gewicht_kg:
        if acceptance.weighing_ticket_id:
            ticket = db.query(WeighingTicket).filter(
                WeighingTicket.id == acceptance.weighing_ticket_id
            ).first()
            if ticket and ticket.net_weight:
                gewicht_kg = float(ticket.net_weight)
        if not gewicht_kg:
            positions = db.query(HarvestAcceptancePosition).filter(
                HarvestAcceptancePosition.harvest_acceptance_id == acceptance_id,
                HarvestAcceptancePosition.position_number == 10,
            ).all()
            if positions:
                gewicht_kg = sum(float(pos.quantity_kg or 0) for pos in positions)
    
    if not gewicht_kg or gewicht_kg <= 0:
        raise HTTPException(status_code=400, detail="Gewicht konnte nicht ermittelt werden")
    
    # Standard-Frachttarif (pro km + pro Tonne)
    grundpreis_eur = 50.0
    preis_pro_km_eur = 1.50
    preis_pro_tonne_eur = 25.0
    
    # Berechnung
    gewicht_tonnen = gewicht_kg / 1000
    frachtkosten_eur = grundpreis_eur + (entfernung_km * preis_pro_km_eur) + (gewicht_tonnen * preis_pro_tonne_eur)
    frachtkosten_eur = round(frachtkosten_eur, 2)
    
    # Speichere Frachtkosten
    acceptance.logistics_freight_costs_eur = Decimal(str(frachtkosten_eur))
    db.commit()
    
    return {
        "acceptance_id": acceptance_id,
        "entfernung_km": entfernung_km,
        "gewicht_kg": gewicht_kg,
        "gewicht_tonnen": round(gewicht_tonnen, 3),
        "frachtkosten_eur": frachtkosten_eur,
    }


@router.get("/{acceptance_id}/frachtkosten", response_model=dict)
async def get_frachtkosten(
    acceptance_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Hole Frachtkosten für Ernte-Annahme."""
    acceptance = db.query(HarvestAcceptance).filter(
        HarvestAcceptance.id == acceptance_id,
        HarvestAcceptance.tenant_id == tenant_id
    ).first()
    
    if not acceptance:
        raise HTTPException(status_code=404, detail="Ernte-Annahme nicht gefunden")
    
    return {
        "acceptance_id": acceptance_id,
        "frachtkosten_eur": float(acceptance.logistics_freight_costs_eur or 0),
    }

