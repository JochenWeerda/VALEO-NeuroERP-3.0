"""
VAT Tax Codes for Germany/EU
Comprehensive tax rate management with audit trail
"""

from sqlalchemy import Column, String, Float, DateTime, Boolean, Text, Enum as SQLEnum
from sqlalchemy.sql import func
from app.core.database import Base
import enum
from datetime import datetime
from typing import Optional


class VatCodeCategory(str, enum.Enum):
    """VAT code categories"""
    DE_INLAND = "DE_INLAND"           # Domestic German
    DE_AGR_PAUSCHAL = "DE_AGR_PAUSCHAL"  # Agricultural §24
    DE_FORST = "DE_FORST"             # Forestry §24
    EU_IGL = "EU_IGL"                 # Intra-community delivery
    EU_ERWERB = "EU_ERWERB"           # Intra-community acquisition
    EU_OSS = "EU_OSS"                 # OSS B2C
    EXPORT = "EXPORT"                 # Export (third country)
    EXEMPT = "EXEMPT"                 # Exempt


class VatCode(Base):
    """VAT Tax Codes - configurable with audit trail"""
    
    __tablename__ = "vat_codes"
    
    # Primary key
    id = Column(String(50), primary_key=True)  # e.g., "DE_19", "DE_AGR_24_78"
    
    # Core fields
    name = Column(String(200), nullable=False)
    name_long = Column(String(500), nullable=True)  # Long description
    category = Column(SQLEnum(VatCodeCategory), nullable=False)
    
    # Tax rate (percentage)
    rate = Column(Float, nullable=False)  # 19.0, 7.0, 7.8, 5.5, 0.0
    
    # German tax account (SKR03/SKR04)
    skr03_account = Column(String(10), nullable=True)  # German datev account
    skr04_account = Column(String(10), nullable=True)
    
    # Validity
    valid_from = Column(DateTime, nullable=False, default=func.now())
    valid_to = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Legal reference
    legal_basis = Column(String(200), nullable=True)  # §12 UStG, §24 UStG, etc.
    legal_note = Column(Text, nullable=True)  # Full legal text reference
    
    # Classification
    is_standard = Column(Boolean, default=False)  # Standard rate flag
    is_reduced = Column(Boolean, default=False)   # Reduced rate flag
    is_zero = Column(Boolean, default=False)      # Zero rate flag
    is_reverse_charge = Column(Boolean, default=False)  # Reverse charge
    
    # For agricultural Pauschalierung
    is_agricultural = Column(Boolean, default=False)
    paragraph_24 = Column(Boolean, default=False)  # §24 UStG
    
    # Tenant scoping (system-wide codes can have NULL tenant_id)
    tenant_id = Column(String(50), nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=func.now())
    created_by = Column(String(100), nullable=True)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    updated_by = Column(String(100), nullable=True)


class VatCodeAudit(Base):
    """Audit trail for VAT code changes"""
    
    __tablename__ = "vat_codes_audit"
    
    id = Column(String(50), primary_key=True)  # UUID
    vat_code_id = Column(String(50), nullable=False)
    
    # Change tracking
    action = Column(String(20), nullable=False)  # CREATE, UPDATE, DELETE
    change_type = Column(String(50), nullable=True)  # What field changed
    
    # Old/new values (stored as JSON)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    
    # Who changed
    changed_by = Column(String(100), nullable=False)
    changed_at = Column(DateTime, default=func.now())
    
    # Reason for change (e.g., "Gesetzesänderung §24 ab 2025")
    reason = Column(Text, nullable=True)
    legal_reference = Column(String(200), nullable=True)
    
    # Tenant
    tenant_id = Column(String(50), nullable=True)


# Default VAT codes for Germany (seed data)
DEFAULT_VAT_CODES = [
    # Domestic standard
    {"id": "DE_19", "name": "USt 19%", "name_long": "Umsatzsteuer 19% Regelsteuersatz", 
     "category": VatCodeCategory.DE_INLAND, "rate": 19.0, "skr03_account": "1776", "skr04_account": "1776",
     "legal_basis": "§ 12 Abs. 1 UStG", "is_standard": True, "is_active": True},
    
    # Domestic reduced
    {"id": "DE_7", "name": "USt 7%", "name_long": "Umsatzsteuer 7% ermäßigter Steuersatz",
     "category": VatCodeCategory.DE_INLAND, "rate": 7.0, "skr03_account": "1771", "skr04_account": "1771",
     "legal_basis": "§ 12 Abs. 2 UStG Anlage 2", "is_reduced": True, "is_active": True},
    
    # Agricultural §24 - Durchschnittssatz
    {"id": "DE_AGR_24_78", "name": "Durchschnittssatz 7,8%", "name_long": "Landwirtschaftlicher Durchschnittssatz §24 UStG",
     "category": VatCodeCategory.DE_AGR_PAUSCHAL, "rate": 7.8, "skr03_account": "1773", "skr04_account": "1773",
     "legal_basis": "§ 24 Nr. 1 UStG", "is_agricultural": True, "paragraph_24": True, "is_active": True},
    
    # Forestry §24
    {"id": "DE_FORST_24_55", "name": "Forstwirtschaft 5,5%", "name_long": "Forstwirtschaftlicher Durchschnittssatz §24 Nr. 2 UStG",
     "category": VatCodeCategory.DE_FORST, "rate": 5.5, "skr03_account": "1774", "skr04_account": "1774",
     "legal_basis": "§ 24 Nr. 2 UStG", "is_agricultural": True, "paragraph_24": True, "is_active": True},
    
    # §24 certain deliveries
    {"id": "DE_AGR_24_19", "name": "§24 Lieferungen 19%", "name_long": "Bestimmte Lieferungen nach §24 UStG",
     "category": VatCodeCategory.DE_AGR_PAUSCHAL, "rate": 19.0, "skr03_account": "1776", "skr04_account": "1776",
     "legal_basis": "§ 24 Nr. 3 UStG", "is_agricultural": True, "paragraph_24": True, "is_active": True},
    
    # Zero rated
    {"id": "DE_0", "name": "0% USt", "name_long": "Steuerfreie Lieferung (0%)",
     "category": VatCodeCategory.EXEMPT, "rate": 0.0, "skr03_account": None, "skr04_account": None,
     "legal_basis": "§ 4 UStG", "is_zero": True, "is_active": True},
    
    # EU Intra-community delivery (0% - B2B)
    {"id": "EU_IGL_0", "name": "IG Lieferung 0%", "name_long": "Innergemeinschaftliche Lieferung §6a UStG",
     "category": VatCodeCategory.EU_IGL, "rate": 0.0, "skr03_account": None, "skr04_account": None,
     "legal_basis": "§ 6a UStG", "is_zero": True, "is_active": True},
    
    # EU Intra-community acquisition (reverse charge)
    {"id": "EU_ACQ_19", "name": "IG Erwerb 19%", "name_long": "Innergemeinschaftlicher Erwerb §1a UStG (Reverse Charge)",
     "category": VatCodeCategory.EU_ERWERB, "rate": 19.0, "skr03_account": "1776", "skr04_account": "1776",
     "legal_basis": "§ 1a UStG", "is_reverse_charge": True, "is_active": True},
    
    {"id": "EU_ACQ_7", "name": "IG Erwerb 7%", "name_long": "Innergemeinschaftlicher Erwerb §1a UStG (Reverse Charge) 7%",
     "category": VatCodeCategory.EU_ERWERB, "rate": 7.0, "skr03_account": "1771", "skr04_account": "1771",
     "legal_basis": "§ 1a UStG", "is_reverse_charge": True, "is_active": True},
    
    # Export (third country)
    {"id": "EXPORT_0", "name": "Export 0%", "name_long": "Ausfuhrlieferung §4 Nr. 1a UStG",
     "category": VatCodeCategory.EXPORT, "rate": 0.0, "skr03_account": None, "skr04_account": None,
     "legal_basis": "§ 4 Nr. 1a UStG", "is_zero": True, "is_active": True},
]
