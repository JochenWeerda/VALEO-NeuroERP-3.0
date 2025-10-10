"""
DMS OCR-Parser
Extrahiert Beleg-Felder aus OCR-Text (Mayan → VALEO)
"""

import re
import logging
from typing import Dict, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class DMSParser:
    """
    OCR-Text-Parser für Eingangsbelege
    Extrahiert: Rechnungsnummer, Lieferant, Datum, Betrag, Positionen
    """
    
    # Regex-Patterns für deutsche Belege
    PATTERNS = {
        # Rechnungsnummer
        "invoice_number": [
            r"Rechnungsnr\.?\s*:?\s*([A-Z0-9\-]+)",
            r"Rechnung\s+Nr\.?\s*:?\s*([A-Z0-9\-]+)",
            r"Invoice\s+No\.?\s*:?\s*([A-Z0-9\-]+)",
            r"R-Nr\.?\s*:?\s*([A-Z0-9\-]+)",
        ],
        
        # Datum
        "date": [
            r"Datum\s*:?\s*(\d{1,2}\.\d{1,2}\.\d{2,4})",
            r"Date\s*:?\s*(\d{1,2}\.\d{1,2}\.\d{2,4})",
            r"(\d{1,2}\.\d{1,2}\.\d{4})",
        ],
        
        # Lieferant
        "supplier": [
            r"(?:Lieferant|Absender|Von)\s*:?\s*([^\n]+)",
            r"^([A-ZÄÖÜ][a-zäöüß]+(?:\s+[A-ZÄÖÜ][a-zäöüß]+){1,3})\s+GmbH",
        ],
        
        # Gesamtbetrag
        "total": [
            r"Gesamtbetrag\s*:?\s*€?\s*([0-9.,]+)",
            r"Summe\s*:?\s*€?\s*([0-9.,]+)",
            r"Total\s*:?\s*€?\s*([0-9.,]+)",
            r"Endbetrag\s*:?\s*€?\s*([0-9.,]+)",
        ],
        
        # MwSt-Betrag
        "tax": [
            r"MwSt\.?\s*(?:19%|7%)?\s*:?\s*€?\s*([0-9.,]+)",
            r"VAT\s*(?:19%|7%)?\s*:?\s*€?\s*([0-9.,]+)",
            r"Umsatzsteuer\s*:?\s*€?\s*([0-9.,]+)",
        ],
        
        # Lieferanten-ID
        "supplier_id": [
            r"Lieferantennr\.?\s*:?\s*([A-Z0-9\-]+)",
            r"Kreditor\s*:?\s*([A-Z0-9\-]+)",
        ],
    }
    
    def parse(self, ocr_text: str) -> Dict[str, Any]:
        """
        Parst OCR-Text und extrahiert Beleg-Felder
        
        Args:
            ocr_text: OCR-Text aus Mayan
        
        Returns:
            Dict mit extrahierten Feldern
        """
        result = {
            "confidence": 0.0,
            "fields": {},
            "raw_text": ocr_text[:500],  # Erste 500 Zeichen
        }
        
        matches = 0
        total_patterns = 0
        
        for field, patterns in self.PATTERNS.items():
            total_patterns += len(patterns)
            
            for pattern in patterns:
                match = re.search(pattern, ocr_text, re.MULTILINE | re.IGNORECASE)
                if match:
                    value = match.group(1).strip()
                    result["fields"][field] = self._clean_value(field, value)
                    matches += 1
                    break  # Erste Match gewinnt
        
        # Confidence-Score
        result["confidence"] = matches / len(self.PATTERNS) if self.PATTERNS else 0.0
        
        # Post-Processing
        result["fields"] = self._post_process(result["fields"])
        
        logger.info(f"Parsed OCR: {matches} fields, confidence: {result['confidence']:.2f}")
        
        return result
    
    def _clean_value(self, field: str, value: str) -> str:
        """Bereinigt extrahierte Werte"""
        value = value.strip()
        
        # Datum normalisieren
        if field == "date":
            value = self._normalize_date(value)
        
        # Betrag normalisieren (deutsch → float)
        elif field in ("total", "tax"):
            value = value.replace(".", "").replace(",", ".")
            try:
                value = f"{float(value):.2f}"
            except ValueError:
                pass
        
        return value
    
    def _normalize_date(self, date_str: str) -> str:
        """Normalisiert Datum zu ISO-Format"""
        try:
            # DD.MM.YYYY → YYYY-MM-DD
            if re.match(r"\d{1,2}\.\d{1,2}\.\d{4}", date_str):
                parts = date_str.split(".")
                return f"{parts[2]}-{parts[1]:0>2}-{parts[0]:0>2}"
            
            # DD.MM.YY → YYYY-MM-DD
            elif re.match(r"\d{1,2}\.\d{1,2}\.\d{2}", date_str):
                parts = date_str.split(".")
                year = f"20{parts[2]}" if int(parts[2]) < 50 else f"19{parts[2]}"
                return f"{year}-{parts[1]:0>2}-{parts[0]:0>2}"
        except Exception:
            pass
        
        return date_str
    
    def _post_process(self, fields: Dict[str, str]) -> Dict[str, str]:
        """Post-Processing: Validierung, Defaults"""
        
        # Datum-Fallback
        if "date" not in fields or not fields["date"]:
            fields["date"] = datetime.now().strftime("%Y-%m-%d")
        
        # Domain-Detection
        if "invoice_number" in fields and "domain" not in fields:
            # Heuristik: Lieferantenrechnung oder Kundenrechnung?
            if "supplier" in fields or "supplier_id" in fields:
                fields["domain"] = "purchase"
            else:
                fields["domain"] = "sales"
        
        return fields


# Singleton
parser = DMSParser()

