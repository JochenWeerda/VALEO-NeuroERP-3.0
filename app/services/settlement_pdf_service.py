"""PDF generation and GoBD archiving for Agrar settlement self-billing documents."""

from __future__ import annotations

import hashlib
import io
import logging
from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from sqlalchemy.orm import Session

from app.core.gobd_artifact import register_artifact

logger = logging.getLogger(__name__)

_VALEO_BLUE = colors.HexColor("#1a3a5c")
_LIGHT_GREY = colors.HexColor("#f2f2f2")


class SettlementPdfService:
    """Generates self-billing PDF (Gutschrift/Selbstabrechnung) for Agrar settlements
    and archives it via GoBD-compliant artifact store."""

    def __init__(self, db: Session, tenant_id: str) -> None:
        self.db = db
        self.tenant_id = tenant_id

    # ── Public API ────────────────────────────────────────────────────────────

    def generate_and_archive(
        self,
        settlement: Any,
        deductions: list[Any],
        supplier: Optional[Any],
        article: Optional[Any],
    ) -> dict:
        """Generate PDF bytes, compute SHA-256, register GoBD artifact.

        Returns dict with keys: filename, content_type, size_bytes, artifact_path, sha256.
        """
        pdf_bytes = self._build_pdf(settlement, deductions, supplier, article)
        sha256 = hashlib.sha256(pdf_bytes).hexdigest()
        filename = f"abrechnung_{settlement.settlement_number or settlement.id}.pdf"
        artifact_path = f"agrar/settlements/{settlement.id}/{filename}"

        try:
            register_artifact(
                self.db,
                self.tenant_id,
                str(settlement.id),
                "settlement_pdf",
                sha256,
                artifact_path,
                file_name=filename,
                created_by=None,
            )
        except Exception:
            logger.warning("GoBD artifact registration failed for settlement %s", settlement.id)

        return {
            "filename": filename,
            "content_type": "application/pdf",
            "size_bytes": len(pdf_bytes),
            "artifact_path": artifact_path,
            "sha256": sha256,
            "pdf_bytes": pdf_bytes,
        }

    def generate_bytes(
        self,
        settlement: Any,
        deductions: list[Any],
        supplier: Optional[Any],
        article: Optional[Any],
    ) -> bytes:
        return self._build_pdf(settlement, deductions, supplier, article)

    # ── PDF construction ──────────────────────────────────────────────────────

    def _build_pdf(self, settlement: Any, deductions: list, supplier: Optional[Any], article: Optional[Any]) -> bytes:
        buf = io.BytesIO()
        doc = SimpleDocTemplate(
            buf,
            pagesize=A4,
            leftMargin=2 * cm,
            rightMargin=2 * cm,
            topMargin=2.5 * cm,
            bottomMargin=2 * cm,
        )

        styles = getSampleStyleSheet()
        h1 = ParagraphStyle("H1", parent=styles["Heading1"], textColor=_VALEO_BLUE, fontSize=16, spaceAfter=6)
        h2 = ParagraphStyle("H2", parent=styles["Heading2"], textColor=_VALEO_BLUE, fontSize=11, spaceBefore=10, spaceAfter=4)
        body = ParagraphStyle("Body", parent=styles["Normal"], fontSize=9, leading=14)
        small = ParagraphStyle("Small", parent=styles["Normal"], fontSize=8, textColor=colors.grey)

        story = []

        # ── Header ────────────────────────────────────────────────────────────
        story.append(Paragraph("SELBSTABRECHNUNG", h1))
        story.append(Paragraph("Agrar-Lieferanten-Gutschrift gemäß §14 Abs. 2 UStG", body))
        story.append(HRFlowable(width="100%", thickness=1.5, color=_VALEO_BLUE, spaceAfter=8))

        # ── Metadaten-Block ───────────────────────────────────────────────────
        abrechnungs_datum = _fmt_date(settlement.posted_at or settlement.created_at)
        meta_data = [
            ["Abrechnungsnummer:", str(settlement.settlement_number or settlement.id)],
            ["Datum:", abrechnungs_datum],
            ["Status:", str(settlement.status or "").upper()],
            ["Mandant:", self.tenant_id],
        ]
        meta_table = Table(meta_data, colWidths=[5 * cm, 10 * cm])
        meta_table.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        story.append(meta_table)
        story.append(Spacer(1, 0.4 * cm))

        # ── Lieferant ─────────────────────────────────────────────────────────
        story.append(Paragraph("Lieferant", h2))
        if supplier:
            sup_data = [
                ["Name:", supplier.name or ""],
                ["Nummer:", getattr(supplier, "partner_number", "") or ""],
                ["Adresse:", _fmt_address(supplier)],
            ]
        else:
            sup_data = [["Lieferant-ID:", str(settlement.supplier_id or "")]]
        sup_table = Table(sup_data, colWidths=[4 * cm, 11 * cm])
        sup_table.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        story.append(sup_table)
        story.append(Spacer(1, 0.4 * cm))

        # ── Warenangaben ──────────────────────────────────────────────────────
        story.append(Paragraph("Warenangaben", h2))
        artikel_name = (article.name if article else None) or str(settlement.article_id or "")
        artikel_nr = getattr(article, "item_number", None) or getattr(article, "article_number", None) or ""
        ware_data = [
            ["Artikel:", artikel_name],
            ["Artikelnummer:", artikel_nr],
            ["Bruttogewicht:", f"{_d(settlement.gross_quantity_kg):,.3f} kg"],
            ["Abrechnungsgewicht:", f"{_d(settlement.billing_quantity_kg):,.3f} kg"],
            ["Preis:", f"{_d(settlement.unit_price_eur_per_ton):,.4f} EUR/t"],
        ]
        ware_table = Table(ware_data, colWidths=[5 * cm, 10 * cm])
        ware_table.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        story.append(ware_table)
        story.append(Spacer(1, 0.4 * cm))

        # ── Abzüge ────────────────────────────────────────────────────────────
        if deductions:
            story.append(Paragraph("Abzüge", h2))
            ded_rows = [["Abzugsart", "Betrag (EUR)", "Notiz"]]
            for d in deductions:
                ded_rows.append([
                    str(getattr(d, "deduction_type", "") or "").upper(),
                    f"-{_d(d.amount_eur):,.2f}",
                    str(getattr(d, "note", "") or ""),
                ])
            ded_table = Table(ded_rows, colWidths=[5 * cm, 3.5 * cm, 6.5 * cm])
            ded_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), _VALEO_BLUE),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, _LIGHT_GREY]),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]))
            story.append(ded_table)
            story.append(Spacer(1, 0.3 * cm))

        # ── Betragsübersicht ──────────────────────────────────────────────────
        story.append(Paragraph("Rechnungsbetrag", h2))
        gross = _d(settlement.gross_amount_eur)
        total_ded = sum(_d(getattr(d, "amount_eur", 0)) for d in deductions)
        net = _d(settlement.net_amount_eur)

        totals = [
            ["Abrechnungsbetrag (brutto):", f"{gross:,.2f} EUR"],
            ["Summe Abzüge:", f"-{total_ded:,.2f} EUR"],
            ["", ""],
            ["ZAHLBAR:", f"{net:,.2f} EUR"],
        ]
        totals_table = Table(totals, colWidths=[9 * cm, 6 * cm])
        totals_table.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, -1), (-1, -1), 11),
            ("LINEABOVE", (0, -1), (-1, -1), 1, _VALEO_BLUE),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(totals_table)
        story.append(Spacer(1, 0.6 * cm))

        # ── Notiz ─────────────────────────────────────────────────────────────
        if getattr(settlement, "note", None):
            story.append(Paragraph("Notiz", h2))
            story.append(Paragraph(settlement.note, body))
            story.append(Spacer(1, 0.3 * cm))

        # ── GoBD-Footer ───────────────────────────────────────────────────────
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey, spaceBefore=8))
        story.append(Paragraph(
            f"Erstellt am: {datetime.utcnow().strftime('%d.%m.%Y %H:%M:%S')} UTC  |  "
            f"GoBD-konforme Dokumentation gemäß §147 AO  |  "
            f"Settlement-ID: {settlement.id}",
            small,
        ))
        story.append(Paragraph(
            "Dieses Dokument ist maschinell erstellt und revisionssicher archiviert.",
            small,
        ))

        doc.build(story)
        return buf.getvalue()


# ── helpers ───────────────────────────────────────────────────────────────────

def _fmt_date(dt: Any) -> str:
    if dt is None:
        return "N/A"
    try:
        return dt.strftime("%d.%m.%Y")
    except Exception:
        return str(dt)[:10]


def _fmt_address(partner: Any) -> str:
    parts = []
    if getattr(partner, "street", None):
        parts.append(partner.street)
    city_part = " ".join(filter(None, [
        getattr(partner, "zip", None) or getattr(partner, "postal_code", None) or "",
        getattr(partner, "city", None) or "",
    ])).strip()
    if city_part:
        parts.append(city_part)
    return ", ".join(parts) or "N/A"


def _d(value: Any) -> Decimal:
    try:
        return Decimal(str(value or 0))
    except Exception:
        return Decimal("0")
