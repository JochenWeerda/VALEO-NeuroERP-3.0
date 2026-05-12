"""
Lieferschein PDF Generator
Spezialisierter PDF-Generator für Lieferscheine (DIN A4)
"""

from __future__ import annotations
import os
from typing import Dict, Any, List
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Table,
    TableStyle,
    Spacer,
    Image,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing
import logging

logger = logging.getLogger(__name__)

# Branding-Konfiguration aus ENV
COMPANY_NAME = os.environ.get("PDF_COMPANY_NAME", "VALEO NeuroERP")
COMPANY_ADDRESS = os.environ.get("PDF_COMPANY_ADDRESS", "Musterstraße 1")
COMPANY_CITY = os.environ.get("PDF_COMPANY_CITY", "12345 Musterstadt")
COMPANY_COUNTRY = os.environ.get("PDF_COMPANY_COUNTRY", "Deutschland")
COMPANY_PHONE = os.environ.get("PDF_COMPANY_PHONE", "+49 123 456789")
COMPANY_EMAIL = os.environ.get("PDF_COMPANY_EMAIL", "info@valeo-neuroerp.de")
COMPANY_TAX_ID = os.environ.get("COMPANY_TAX_ID", "DE123456789")
COMPANY_LOGO = os.environ.get("PDF_COMPANY_LOGO", "")


class LieferscheinPDFGenerator:
    """PDF-Generator für Lieferscheine (DIN A4)"""

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Erstellt custom Styles für Lieferschein"""
        # Header Style
        self.styles.add(
            ParagraphStyle(
                name="LieferscheinHeader",
                parent=self.styles["Heading1"],
                fontSize=24,
                textColor=colors.HexColor("#1e40af"),
                alignment=TA_CENTER,
                spaceAfter=10*mm,
            )
        )
        
        # Company Info Style
        self.styles.add(
            ParagraphStyle(
                name="CompanyInfo",
                parent=self.styles["Normal"],
                fontSize=9,
                leading=12,
            )
        )
        
        # Customer Info Style
        self.styles.add(
            ParagraphStyle(
                name="CustomerInfo",
                parent=self.styles["Normal"],
                fontSize=10,
                leading=14,
            )
        )
        
        # Footer Style
        self.styles.add(
            ParagraphStyle(
                name="Footer",
                parent=self.styles["Normal"],
                fontSize=8,
                textColor=colors.grey,
                alignment=TA_CENTER,
            )
        )
        
        # Table Header Style
        self.styles.add(
            ParagraphStyle(
                name="TableHeader",
                parent=self.styles["Normal"],
                fontSize=9,
                textColor=colors.white,
                alignment=TA_CENTER,
            )
        )

    def _add_header(self, story: List, lieferschein_nr: str, liefer_datum: str):
        """Fügt Header mit Logo und Firmeninfo hinzu"""
        # Logo (falls vorhanden)
        if COMPANY_LOGO and Path(COMPANY_LOGO).exists():
            try:
                logo_img = Image(COMPANY_LOGO, width=60*mm, height=30*mm)
                story.append(logo_img)
                story.append(Spacer(1, 5*mm))
            except Exception as e:
                logger.warning(f"Failed to load logo: {e}")
        
        # Firmeninfo (rechts oben)
        company_info = f"""
        <b>{COMPANY_NAME}</b><br/>
        {COMPANY_ADDRESS}<br/>
        {COMPANY_CITY}<br/>
        {COMPANY_COUNTRY}<br/>
        Tel: {COMPANY_PHONE}<br/>
        E-Mail: {COMPANY_EMAIL}<br/>
        USt-IdNr: {COMPANY_TAX_ID}
        """
        story.append(Paragraph(company_info, self.styles["CompanyInfo"]))
        story.append(Spacer(1, 10*mm))
        
        # Lieferschein Titel
        story.append(Paragraph("LIEFERSCHEIN", self.styles["LieferscheinHeader"]))
        
        # Lieferschein-Nummer und Datum
        info_table = Table([
            ["Lieferschein-Nr.:", lieferschein_nr],
            ["Liefer-Datum:", liefer_datum],
        ], colWidths=[50*mm, 100*mm])
        
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        
        story.append(info_table)
        story.append(Spacer(1, 10*mm))

    def _add_customer_info(self, story: List, customer: Dict[str, Any]):
        """Fügt Kundeninformationen hinzu"""
        customer_name = customer.get("name", customer.get("company_name", "N/A"))
        customer_address = customer.get("address", customer.get("street", ""))
        customer_city = customer.get("city", "")
        customer_postal_code = customer.get("postal_code", "")
        customer_country = customer.get("country", "Deutschland")
        
        customer_info = f"""
        <b>Lieferadresse:</b><br/>
        {customer_name}<br/>
        {customer_address}<br/>
        {customer_postal_code} {customer_city}<br/>
        {customer_country}
        """
        
        if customer.get("phone"):
            customer_info += f"<br/>Tel: {customer.get('phone')}"
        if customer.get("email"):
            customer_info += f"<br/>E-Mail: {customer.get('email')}"
        
        story.append(Paragraph(customer_info, self.styles["CustomerInfo"]))
        story.append(Spacer(1, 10*mm))

    def _add_positions_table(self, story: List, positions: List[Dict[str, Any]]):
        """Fügt Positionen-Tabelle hinzu"""
        if not positions:
            return
        
        # Tabellen-Header
        table_data = [[
            "Pos.",
            "Artikel-Nr.",
            "Bezeichnung",
            "Menge",
            "Einheit",
            "Listenpreis",
            "Rabatt %",
            "Netto-Preis",
            "Netto-Betrag",
        ]]
        
        # Positionen
        for pos in positions:
            table_data.append([
                str(pos.get("posNr", "")),
                pos.get("artikelNr", ""),
                pos.get("bezeichnung", ""),
                f"{pos.get('menge', 0):.2f}",
                pos.get("einheit", ""),
                f"{pos.get('listenpreis', 0):.2f} €",
                f"{pos.get('rabatt', 0):.2f} %",
                f"{pos.get('nettoPreis', 0):.2f} €",
                f"{pos.get('nettoBetrag', 0):.2f} €",
            ])
        
        # Summen-Zeile
        netto_gesamt = sum(pos.get("nettoBetrag", 0) for pos in positions)
        mwst_prozent = positions[0].get("mwstProzent", 19) if positions else 19
        mwst_betrag = netto_gesamt * (mwst_prozent / 100)
        brutto_gesamt = netto_gesamt + mwst_betrag
        
        table_data.append([
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "<b>Netto Gesamt:</b>",
            f"<b>{netto_gesamt:.2f} €</b>",
        ])
        table_data.append([
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            f"MwSt. ({mwst_prozent}%):",
            f"{mwst_betrag:.2f} €",
        ])
        table_data.append([
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "<b>Brutto Gesamt:</b>",
            f"<b>{brutto_gesamt:.2f} €</b>",
        ])
        
        # Tabelle erstellen
        table = Table(table_data, colWidths=[
            15*mm,  # Pos.
            30*mm,  # Artikel-Nr.
            60*mm,  # Bezeichnung
            20*mm,  # Menge
            20*mm,  # Einheit
            25*mm,  # Listenpreis
            20*mm,  # Rabatt
            25*mm,  # Netto-Preis
            30*mm,  # Netto-Betrag
        ])
        
        # Tabellen-Style
        table.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1e40af")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (2, 0), (2, -1), 'LEFT'),  # Bezeichnung links
            ('ALIGN', (7, 0), (-1, -1), 'RIGHT'),  # Preise rechts
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # Daten-Zeilen
            ('FONTNAME', (0, 1), (-1, -4), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -4), 9),
            ('GRID', (0, 0), (-1, -4), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -4), [colors.white, colors.HexColor("#f3f4f6")]),
            
            # Summen-Zeilen
            ('FONTNAME', (7, -3), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (7, -3), (-1, -1), 10),
            ('LINEABOVE', (7, -3), (-1, -3), 1, colors.black),
            ('LINEABOVE', (7, -1), (-1, -1), 2, colors.black),
            ('TOPPADDING', (7, -3), (-1, -1), 5),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 10*mm))

    def _add_footer(self, story: List):
        """Fügt Fußzeile hinzu"""
        story.append(Spacer(1, 10*mm))
        
        footer_text = f"{COMPANY_NAME} | {COMPANY_ADDRESS}, {COMPANY_CITY} | {COMPANY_EMAIL} | {COMPANY_PHONE}"
        story.append(Paragraph(footer_text, self.styles["Footer"]))
        
        # QR-Code (optional)
        try:
            qr = QrCodeWidget(f"{COMPANY_NAME}|{COMPANY_EMAIL}")
            qr.barWidth = 30
            qr.barHeight = 30
            drawing = Drawing(30, 30)
            drawing.add(qr)
            story.append(Spacer(1, 5*mm))
            story.append(drawing)
        except Exception as e:
            logger.warning(f"Failed to generate QR code: {e}")

    def generate_lieferschein_pdf(
        self,
        lieferschein_nr: str,
        liefer_datum: str,
        customer: Dict[str, Any],
        positions: List[Dict[str, Any]],
        output_path: str,
    ) -> str:
        """
        Generiert Lieferschein-PDF (DIN A4)
        
        Args:
            lieferschein_nr: Lieferschein-Nummer
            liefer_datum: Liefer-Datum (Format: DD.MM.YYYY)
            customer: Kunden-Daten
            positions: Liste der Positionen
            output_path: Ziel-Pfad für PDF
        
        Returns:
            Pfad zur erstellten PDF-Datei
        """
        doc = SimpleDocTemplate(output_path, pagesize=A4, topMargin=20*mm, bottomMargin=20*mm)
        story = []
        
        # Header
        self._add_header(story, lieferschein_nr, liefer_datum)
        
        # Kundeninfo
        self._add_customer_info(story, customer)
        
        # Positionen-Tabelle
        self._add_positions_table(story, positions)
        
        # Footer
        self._add_footer(story)
        
        # PDF generieren
        doc.build(story)
        
        logger.info(f"Lieferschein PDF generated: {output_path}")
        return output_path


# Singleton
_lieferschein_generator: LieferscheinPDFGenerator | None = None


def get_lieferschein_generator() -> LieferscheinPDFGenerator:
    """Get global LieferscheinPDFGenerator instance"""
    global _lieferschein_generator
    if _lieferschein_generator is None:
        _lieferschein_generator = LieferscheinPDFGenerator()
    return _lieferschein_generator


