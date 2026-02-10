"""
PDF Service
Generiert gebrandete PDF-Dokumente aus Belegen mit Logo, QR-Code und Fußzeile
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
    PageBreak,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_CENTER
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF
import logging

logger = logging.getLogger(__name__)

# Branding-Konfiguration aus ENV
COMPANY_NAME = os.environ.get("PDF_COMPANY_NAME", "VALEO NeuroERP")
COMPANY_ADDRESS = os.environ.get("PDF_COMPANY_ADDRESS", "Musterstraße 1, 12345 Musterstadt")
COMPANY_PHONE = os.environ.get("PDF_COMPANY_PHONE", "+49 123 456789")
COMPANY_EMAIL = os.environ.get("PDF_COMPANY_EMAIL", "info@valeo-neuroerp.de")
COMPANY_LOGO = os.environ.get("PDF_COMPANY_LOGO", "")  # Pfad zu Logo-Datei


class PDFGenerator:
    """PDF-Generator für ERP-Belege mit Branding"""

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _get_workflow_status(self, domain: str, number: str) -> str:
        """
        Holt Workflow-Status für PDF-Footer
        
        Args:
            domain: Belegtyp
            number: Belegnummer
        
        Returns:
            Status-String (Draft, Pending, Approved, Posted, etc.)
        """
        try:
            import httpx
            # Synchroner Request für Status
            with httpx.Client(timeout=1.0) as client:
                response = client.get(f"http://localhost:8000/api/workflow/{domain}/{number}")
                if response.status_code == 200:
                    data = response.json()
                    if data.get("ok"):
                        return data.get("state", "unknown").capitalize()
        except Exception as e:
            logger.warning(f"Could not fetch workflow status: {e}")
        return "Unknown"

    def _setup_custom_styles(self):
        """Erstellt custom Styles"""
        self.styles.add(
            ParagraphStyle(
                name="RightAlign",
                parent=self.styles["Normal"],
                alignment=TA_RIGHT,
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="Header",
                parent=self.styles["Heading1"],
                fontSize=18,
                textColor=colors.HexColor("#1e40af"),
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="Footer",
                parent=self.styles["Normal"],
                fontSize=8,
                textColor=colors.grey,
                alignment=TA_CENTER,
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="CompanyInfo",
                parent=self.styles["Normal"],
                fontSize=9,
                textColor=colors.grey,
            )
        )

    def _add_header(self, story: List, doc_type: str, doc_number: str):
        """Fügt Header mit Logo und Firmeninfo hinzu"""
        # Logo (falls vorhanden)
        if COMPANY_LOGO and Path(COMPANY_LOGO).exists():
            try:
                logo = Image(COMPANY_LOGO, width=40 * mm, height=20 * mm)
                story.append(logo)
                story.append(Spacer(1, 5 * mm))
            except Exception as e:
                logger.warning(f"Failed to load logo: {e}")

        # Firmeninfo
        story.append(
            Paragraph(f"<b>{COMPANY_NAME}</b>", self.styles["CompanyInfo"])
        )
        story.append(Paragraph(COMPANY_ADDRESS, self.styles["CompanyInfo"]))
        story.append(
            Paragraph(
                f"Tel: {COMPANY_PHONE} | Email: {COMPANY_EMAIL}",
                self.styles["CompanyInfo"],
            )
        )
        story.append(Spacer(1, 10 * mm))

        # Dokumenten-Titel
        title_map = {
            "sales_order": "Verkaufsauftrag",
            "sales_delivery": "Lieferschein",
            "sales_invoice": "Rechnung",
            "purchase_order": "Bestellung",
            "goods_receipt": "Wareneingang",
            "supplier_invoice": "Lieferantenrechnung",
        }
        title = title_map.get(doc_type, doc_type.upper())

        story.append(Paragraph(f"{title} Nr. {doc_number}", self.styles["Header"]))
        story.append(Spacer(1, 10 * mm))

    def _add_qr_code(self, story: List, data: str):
        """Fügt QR-Code hinzu"""
        try:
            qr = QrCodeWidget(data)
            qr_drawing = Drawing(50, 50)
            qr_drawing.add(qr)
            story.append(qr_drawing)
        except Exception as e:
            logger.warning(f"Failed to generate QR code: {e}")

    def _add_footer(self, story: List, status: str = None):
        """Fügt Fußzeile hinzu"""
        story.append(Spacer(1, 10 * mm))

        footer_text = f"{COMPANY_NAME} | {COMPANY_ADDRESS} | {COMPANY_EMAIL}"
        if status:
            from datetime import datetime
            status_date = datetime.now().strftime("%Y-%m-%d")
            footer_text += f" | Status: {status} · {status_date}"

        story.append(
            Paragraph(footer_text, self.styles["Footer"])
        )

    def render_document(
        self, doc_type: str, payload: Dict[str, Any], output_path: str, status: str = None
    ) -> str:
        """
        Rendert Beleg als PDF mit Branding

        Args:
            doc_type: Belegtyp (z.B. "sales_order")
            payload: Beleg-Daten
            output_path: Ziel-Pfad für PDF

        Returns:
            Pfad zur erstellten PDF-Datei
        """
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        story = []

        # Header mit Logo & Firmeninfo
        doc_number = payload.get("number", "N/A")
        self._add_header(story, doc_type, doc_number)

        # Beleg-Daten
        fields_to_show = [
            ("date", "Datum"),
            ("customerId", "Kunde"),
            ("deliveryAddress", "Lieferadresse"),
            ("paymentTerms", "Zahlungsbedingungen"),
            ("notes", "Notizen"),
        ]

        for field, label in fields_to_show:
            value = payload.get(field)
            if value:
                story.append(
                    Paragraph(f"<b>{label}:</b> {value}", self.styles["Normal"])
                )

        story.append(Spacer(1, 10 * mm))

        # Positionen-Tabelle
        lines = payload.get("lines", [])
        if lines:
            table_data = [["Artikel", "Menge", "Preis", "Summe"]]

            for line in lines:
                article = line.get("article", "")
                qty = line.get("qty", 0)
                price = line.get("price", 0)
                total = round(qty * price, 2)
                table_data.append(
                    [article, str(qty), f"{price:.2f} €", f"{total:.2f} €"]
                )

            # Gesamtsumme
            grand_total = sum(l.get("qty", 0) * l.get("price", 0) for l in lines)
            table_data.append(["", "", "<b>Gesamt:</b>", f"<b>{grand_total:.2f} €</b>"])

            table = Table(table_data, colWidths=[80 * mm, 30 * mm, 30 * mm, 30 * mm])
            table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e40af")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, 0), 10),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                        ("BACKGROUND", (0, -1), (-1, -1), colors.beige),
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                    ]
                )
            )
            story.append(table)

        # QR-Code mit Belegnummer
        story.append(Spacer(1, 10 * mm))
        self._add_qr_code(story, doc_number)

        # Fußzeile
        self._add_footer(story, status)

        # PDF bauen
        doc.build(story)
        logger.info(f"Generated PDF: {output_path}")
        return output_path


# Global Generator Instance
generator = PDFGenerator()

