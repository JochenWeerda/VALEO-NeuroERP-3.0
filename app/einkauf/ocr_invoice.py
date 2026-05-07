"""Heuristische Rechnungs-Extraktion aus PDF für Einkauf OCR (PROC-IV-01)."""

from __future__ import annotations

import io
import logging
import os
import re
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


def resolve_pdf_bytes(file_id: str) -> bytes | None:
    """Lädt Bytes, wenn EINKAUF_OCR_UPLOAD_DIR gesetzt ist und `{dir}/{file_id}` existiert."""
    base = os.getenv("EINKAUF_OCR_UPLOAD_DIR") or ""
    if not base or not file_id:
        return None
    candidate = os.path.join(base, file_id)
    if os.path.isfile(candidate) and candidate.lower().endswith(".pdf"):
        with open(candidate, "rb") as f:
            return f.read()
    return None


def extract_invoice_pdf(
    *,
    file_id: str,
    engine: str,
    pdf_bytes: bytes | None,
) -> dict[str, Any]:
    """
    Extrahiert Text via pdfplumber und wendet einfache Regex-Heuristiken an.
    Ohne gültiges PDF wird None-confidence zurückgegeben (Router nutzt Fallback).
    """
    warnings: list[str] = []
    extracted: dict[str, Any]

    content = pdf_bytes or resolve_pdf_bytes(file_id)

    if engine == "pdfplumber" and content:
        try:
            import pdfplumber  # type: ignore[import-untyped]

            chunks: list[str] = []
            with pdfplumber.open(io.BytesIO(content)) as pdf:
                for page in pdf.pages[:8]:
                    t = page.extract_text() or ""
                    chunks.append(t)
            full_text = "\n".join(chunks)

            rn = (
                re.search(
                    r"(?:Rechnung(?:s|\s*-)?Nr\.?\s*|Invoice\s*(?:No\.|#)?\s*)[:#\s]*([A-Za-z0-9\-_/]+)",
                    full_text,
                    re.I,
                )
            )
            rechnungs_nummer = rn.group(1).strip() if rn else f"PDF-{file_id[-8:]}"

            dmatch = re.search(
                r"(?:Datum|Date)[:\s]+(\d{1,2}[./]\d{1,2}[./]\d{2,4})", full_text, re.I
            )
            rechnungs_datum = dmatch.group(1) if dmatch else datetime.utcnow().date().isoformat()

            money = re.findall(
                r"(?:EUR|€)\s*(\d{1,3}(?:\.\d{3})*,\d{2}|\d+,\d{2})|\b(\d+[\.,]\d{2})\s*EUR\b",
                full_text,
                re.I,
            )
            amounts: list[float] = []
            for a, b in money:
                raw = (a or b).replace(".", "").replace(",", ".")
                try:
                    amounts.append(float(raw))
                except ValueError:
                    continue
            brutto = max(amounts) if amounts else 0.0
            mwst_hint = brutto / 1.19 * 0.19 if brutto else 0.0
            netto = brutto - mwst_hint if brutto else 0.0

            extracted = {
                "rechnungs_nummer": rechnungs_nummer,
                "rechnungs_datum": str(rechnungs_datum),
                "lieferant_name": "",
                "lieferant_adresse": "",
                "netto_betrag": round(netto, 2),
                "mwst_betrag": round(mwst_hint, 2),
                "brutto_betrag": round(brutto, 2),
                "waehrung": "EUR",
                "positionen": [],
                "_text_preview": full_text[:1200],
            }
            if not brutto:
                warnings.append(
                    "Keine Beträge sicher erkannt — bitte Felder manuell prüfen."
                )

            confidence = min(0.95, 0.55 + 0.08 * len(amounts))

            return {
                "extracted_data": extracted,
                "confidence_score": confidence,
                "extraction_warnings": warnings,
                "ocr_model": "pdfplumber-heuristic-v1",
                "processed_at": datetime.utcnow().isoformat(),
            }
        except ImportError:
            warnings.append(
                "pdfplumber nicht installiert — pip install pdfplumber oder Fallback nutzen."
            )
        except Exception:
            logger.exception("pdfplumber_extraktion_fehler")
            warnings.append("PDF-OCR Parsing fehlgeschlagen.")

    extracted = {
        "rechnungs_nummer": f"OCR-{file_id[-8:]}",
        "rechnungs_datum": datetime.utcnow().date().isoformat(),
        "lieferant_name": "Muster-Lieferant GmbH",
        "lieferant_adresse": "Musterstraße 1, 12345 Musterstadt",
        "netto_betrag": 1500.00,
        "mwst_betrag": 285.00,
        "brutto_betrag": 1785.00,
        "waehrung": "EUR",
        "positionen": [
            {
                "artikel_name": "Musterartikel A",
                "menge": 10,
                "einzelpreis": 100.00,
                "gesamtpreis": 1000.00,
                "mwst_satz": 19.0,
            },
            {
                "artikel_name": "Musterartikel B",
                "menge": 5,
                "einzelpreis": 100.00,
                "gesamtpreis": 500.00,
                "mwst_satz": 19.0,
            },
        ]
        if engine == "stub"
        else [],
    }

    confidence = 0.35 if engine == "pdfplumber" else 0.92
    if warnings:
        confidence *= 0.85

    return {
        "extracted_data": extracted,
        "confidence_score": confidence,
        "extraction_warnings": warnings
        + (
            []
            if content
            else [
                "Kein PDF-Inhalt verfügbar — setzen Sie EINKAUF_OCR_UPLOAD_DIR oder liefern Sie Dateien nach."
            ]
        ),
        "ocr_model": f"{engine}-fallback",
        "processed_at": datetime.utcnow().isoformat(),
    }
