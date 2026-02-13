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

            if doc_type == "sales_delivery":
                story.append(Spacer(1, 6 * mm))
                story.append(Paragraph("<b>Bilanzrelevante NÃ¤hrstoff- und CO2-Werte</b>", self.styles["Normal"]))
                story.append(Spacer(1, 2 * mm))

                total_n = payload.get("totalNutrientNKg")
                total_p2o5 = payload.get("totalNutrientP2o5Kg")
                total_co2e = payload.get("totalCo2eKg")

                if total_n is None:
                    total_n = sum(
                        float(line.get("nutrientNTotalKg") or (line.get("qty", 0) * (line.get("nutrientNKgPerUnit", 0) or 0)))
                        for line in lines
                    )
                if total_p2o5 is None:
                    total_p2o5 = sum(
                        float(line.get("nutrientP2o5TotalKg") or (line.get("qty", 0) * (line.get("nutrientP2o5KgPerUnit", 0) or 0)))
                        for line in lines
                    )
                if total_co2e is None:
                    total_co2e = sum(
                        float(line.get("co2eTotalKg") or (line.get("qty", 0) * (line.get("co2eKgPerUnit", 0) or 0)))
                        for line in lines
                    )

                sustainability_summary = [
                    ["Kennzahl", "Wert"],
                    ["Gesamt N", f"{float(total_n):.3f} kg"],
                    ["Gesamt P2O5", f"{float(total_p2o5):.3f} kg"],
                    ["Gesamt CO2e", f"{float(total_co2e):.3f} kg"],
                ]

                summary_table = Table(sustainability_summary, colWidths=[80 * mm, 40 * mm])
                summary_table.setStyle(
                    TableStyle(
                        [
                            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e5e7eb")),
                            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                            ("ALIGN", (1, 1), (1, -1), "RIGHT"),
                            ("GRID", (0, 0), (-1, -1), 1, colors.black),
                        ]
                    )
                )
                story.append(summary_table)

                position_sustainability = [["Artikel", "N kg", "P2O5 kg", "CO2e kg"]]
                for line in lines:
                    qty = float(line.get("qty", 0) or 0)
                    line_n = float(line.get("nutrientNTotalKg") or (qty * (line.get("nutrientNKgPerUnit", 0) or 0)))
                    line_p2o5 = float(line.get("nutrientP2o5TotalKg") or (qty * (line.get("nutrientP2o5KgPerUnit", 0) or 0)))
                    line_co2e = float(line.get("co2eTotalKg") or (qty * (line.get("co2eKgPerUnit", 0) or 0)))
                    position_sustainability.append(
                        [
                            str(line.get("article", "")),
                            f"{line_n:.3f}",
                            f"{line_p2o5:.3f}",
                            f"{line_co2e:.3f}",
                        ]
                    )

                story.append(Spacer(1, 3 * mm))
                detail_table = Table(position_sustainability, colWidths=[70 * mm, 25 * mm, 25 * mm, 25 * mm])
                detail_table.setStyle(
                    TableStyle(
                        [
                            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f3f4f6")),
                            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                            ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
                            ("GRID", (0, 0), (-1, -1), 1, colors.black),
                        ]
                    )
                )
                story.append(detail_table)

                psm_lines = [
                    line for line in lines
                    if line.get("bvlZulassungsnummer") or line.get("sdsReference") or line.get("hazardHinweise")
                ]
                if psm_lines:
                    story.append(Spacer(1, 5 * mm))
                    story.append(Paragraph("<b>PSM Pflichtangaben und Gefahrenhinweise</b>", self.styles["Normal"]))

                    compliance = payload.get("psmCompliance", {}) or {}
                    status_label = "konform" if compliance.get("compliant") else "nicht konform"
                    supplier_name = payload.get("supplierName") or compliance.get("supplierName") or "-"
                    sachkunde = payload.get("sachkundeStatus") or compliance.get("sachkundeStatus") or "-"
                    sds_mitgeliefert = payload.get("sdsMitgeliefert") or compliance.get("sdsMitgeliefert") or "-"
                    adr_punkte = float(payload.get("adrPunkte") or compliance.get("adrPunkte") or 0.0)

                    psm_header = [
                        ["Lieferant", "Sachkunde", "SDB", "ADR Punkte", "Status"],
                        [str(supplier_name), str(sachkunde), str(sds_mitgeliefert), f"{adr_punkte:.1f}", status_label],
                    ]
                    psm_header_table = Table(psm_header, colWidths=[45 * mm, 30 * mm, 20 * mm, 25 * mm, 30 * mm])
                    psm_header_table.setStyle(
                        TableStyle(
                            [
                                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f3f4f6")),
                                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                                ("ALIGN", (3, 1), (3, 1), "RIGHT"),
                                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                            ]
                        )
                    )
                    story.append(psm_header_table)

                    psm_table = [["Produkt", "BVL-Zulassung", "SDB-Ref.", "Gefahrenhinweise"]]
                    for line in psm_lines:
                        psm_table.append(
                            [
                                str(line.get("article", "")),
                                str(line.get("bvlZulassungsnummer", "")),
                                str(line.get("sdsReference", "")),
                                str(line.get("hazardHinweise", "")),
                            ]
                        )

                    story.append(Spacer(1, 3 * mm))
                    psm_detail_table = Table(psm_table, colWidths=[45 * mm, 35 * mm, 30 * mm, 40 * mm])
                    psm_detail_table.setStyle(
                        TableStyle(
                            [
                                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e5e7eb")),
                                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                            ]
                        )
                    )
                    story.append(psm_detail_table)

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

