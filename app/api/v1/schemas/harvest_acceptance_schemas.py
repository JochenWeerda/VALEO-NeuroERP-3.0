"""Pydantic schemas for the harvest acceptance domain."""
from __future__ import annotations

from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.api.v1.schemas.base import BaseSchema


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

