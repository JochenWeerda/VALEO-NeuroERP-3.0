"""
PDF Template Service
Multi-Language (DE/EN) & Multi-Size (A4/Letter) Support
"""

import os
import logging
from typing import Literal
from pathlib import Path
from reportlab.lib.pagesizes import A4, LETTER
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image

logger = logging.getLogger(__name__)

PageSize = Literal["A4", "LETTER"]
Language = Literal["de", "en"]


class PDFTemplateConfig:
    """PDF-Template-Konfiguration aus ENV"""
    
    def __init__(self):
        self.language: Language = os.environ.get("PDF_TEMPLATE_LANG", "de").lower()  # type: ignore
        self.page_size: PageSize = os.environ.get("PDF_PAGE_SIZE", "A4").upper()  # type: ignore
        self.logo_path = os.environ.get("PDF_LOGO_PATH", "data/branding/logo.png")
        self.primary_color = os.environ.get("PDF_PRIMARY_COLOR", "#003366")
        self.secondary_color = os.environ.get("PDF_SECONDARY_COLOR", "#0066CC")
        
        # Company Info
        self.company_name = os.environ.get("COMPANY_NAME", "VALEO GmbH")
        self.company_address = os.environ.get("COMPANY_ADDRESS", "Musterstraße 123")
        self.company_city = os.environ.get("COMPANY_CITY", "12345 Musterstadt")
        self.company_country = os.environ.get("COMPANY_COUNTRY", "Deutschland")
        self.company_tax_id = os.environ.get("COMPANY_TAX_ID", "DE123456789")
        self.company_phone = os.environ.get("COMPANY_PHONE", "+49 123 456789")
        self.company_email = os.environ.get("COMPANY_EMAIL", "info@example.com")
        self.company_website = os.environ.get("COMPANY_WEBSITE", "www.example.com")
    
    def get_page_size(self):
        """Returns ReportLab page size"""
        return A4 if self.page_size == "A4" else LETTER
    
    def get_logo(self):
        """Returns logo ImageReader or None"""
        logo_path = Path(self.logo_path)
        if logo_path.exists():
            try:
                return ImageReader(str(logo_path))
            except Exception as e:
                logger.warning(f"Failed to load logo: {e}")
        return None


class PDFTemplateService:
    """Service für PDF-Template-Rendering"""
    
    def __init__(self, config: PDFTemplateConfig = None):
        self.config = config or PDFTemplateConfig()
        self.translations = self._load_translations()
    
    def _load_translations(self) -> dict:
        """Lädt Übersetzungen für Templates"""
        return {
            "de": {
                "invoice": "Rechnung",
                "sales_order": "Kundenauftrag",
                "delivery": "Lieferschein",
                "purchase_order": "Bestellung",
                "date": "Datum",
                "number": "Nummer",
                "customer": "Kunde",
                "supplier": "Lieferant",
                "item": "Artikel",
                "description": "Beschreibung",
                "quantity": "Menge",
                "unit_price": "Einzelpreis",
                "total": "Gesamt",
                "subtotal": "Zwischensumme",
                "tax": "MwSt.",
                "grand_total": "Gesamtsumme",
                "page": "Seite",
                "of": "von",
                "thank_you": "Vielen Dank für Ihr Vertrauen",
                "payment_terms": "Zahlbar innerhalb 14 Tagen ohne Abzug",
            },
            "en": {
                "invoice": "Invoice",
                "sales_order": "Sales Order",
                "delivery": "Delivery Note",
                "purchase_order": "Purchase Order",
                "date": "Date",
                "number": "Number",
                "customer": "Customer",
                "supplier": "Supplier",
                "item": "Item",
                "description": "Description",
                "quantity": "Quantity",
                "unit_price": "Unit Price",
                "total": "Total",
                "subtotal": "Subtotal",
                "tax": "VAT",
                "grand_total": "Grand Total",
                "page": "Page",
                "of": "of",
                "thank_you": "Thank you for your business",
                "payment_terms": "Payment due within 14 days",
            }
        }
    
    def t(self, key: str) -> str:
        """Translate key to configured language"""
        return self.translations[self.config.language].get(key, key)
    
    def render_header(self, c: canvas.Canvas, doc_type: str, doc_number: str, doc_date: str):
        """Rendert PDF-Header mit Logo und Company-Info"""
        page_width, page_height = self.config.get_page_size()
        
        # Logo
        logo = self.config.get_logo()
        if logo:
            c.drawImage(logo, 20*mm, page_height - 40*mm, width=40*mm, height=20*mm, preserveAspectRatio=True)
        
        # Company Info (rechts)
        c.setFont("Helvetica", 8)
        x = page_width - 70*mm
        y = page_height - 25*mm
        
        c.drawString(x, y, self.config.company_name)
        c.drawString(x, y - 3*mm, self.config.company_address)
        c.drawString(x, y - 6*mm, self.config.company_city)
        c.drawString(x, y - 9*mm, self.config.company_country)
        c.drawString(x, y - 12*mm, f"Tax ID: {self.config.company_tax_id}")
        c.drawString(x, y - 15*mm, self.config.company_phone)
        c.drawString(x, y - 18*mm, self.config.company_email)
        
        # Document Title
        c.setFont("Helvetica-Bold", 16)
        c.setFillColorRGB(0, 0.2, 0.4)  # Primary color
        c.drawString(20*mm, page_height - 50*mm, self.t(doc_type))
        
        # Document Info
        c.setFont("Helvetica", 10)
        c.setFillColorRGB(0, 0, 0)
        c.drawString(20*mm, page_height - 60*mm, f"{self.t('number')}: {doc_number}")
        c.drawString(20*mm, page_height - 65*mm, f"{self.t('date')}: {doc_date}")
    
    def render_footer(self, c: canvas.Canvas, page_num: int, total_pages: int):
        """Rendert PDF-Footer"""
        page_width, page_height = self.config.get_page_size()
        
        c.setFont("Helvetica", 8)
        c.setFillColorRGB(0.5, 0.5, 0.5)
        
        # Page number
        c.drawString(
            page_width / 2 - 10*mm,
            15*mm,
            f"{self.t('page')} {page_num} {self.t('of')} {total_pages}"
        )
        
        # Company footer
        footer_text = f"{self.config.company_name} | {self.config.company_website} | {self.config.company_email}"
        c.drawCentredString(page_width / 2, 10*mm, footer_text)


# Singleton
_template_service: PDFTemplateService | None = None


def get_pdf_template_service() -> PDFTemplateService:
    """Get global PDFTemplateService instance"""
    global _template_service
    if _template_service is None:
        _template_service = PDFTemplateService()
    return _template_service

