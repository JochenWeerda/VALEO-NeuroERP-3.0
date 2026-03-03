"""
VIES (VAT Information Exchange System) – EU-USt-ID-Prüfung.

Prüft USt-IDs gegen den EU-Service (ec.europa.eu/taxation_customs/vies).
Optional: Paket `zeep` oder `vatnumber` für robuste SOAP-Anbindung;
ohne zusätzliche Abhängigkeit: HTTP/SOAP mit requests (WSDL-Endpunkt kann zeitweise 500 liefern).
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)

# EU-Ländercodes (ISO 3166-1 alpha-2) für USt-ID
VIES_COUNTRY_CODES = frozenset([
    "AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", "GR", "HU",
    "IE", "IT", "LV", "LT", "LU", "MT", "NL", "PL", "PT", "RO", "SK", "SI", "ES", "SE",
    "XI",  # Nordirland (post-Brexit)
])

# Bekannter VIES SOAP-Endpunkt (Production)
VIES_CHECK_VAT_URL = "https://ec.europa.eu/taxation_customs/vies/services/checkVatService"
# Fallback (manche Umgebungen nutzen checkVatTestService für Tests)
VIES_CHECK_VAT_TEST_URL = "https://ec.europa.eu/taxation_customs/vies/services/checkVatTestService"


@dataclass
class VIESResult:
    """Ergebnis einer VIES-Anfrage."""
    valid: bool
    country_code: str
    vat_number: str
    request_identifier: Optional[str] = None
    name: Optional[str] = None
    address: Optional[str] = None
    raw_response: Optional[str] = None
    error_message: Optional[str] = None
    service_unavailable: bool = False


def normalize_vat_number(vat_id: str) -> tuple[str, str]:
    """
    Extrahiert Ländercode (2 Zeichen) und Nummer aus USt-ID.
    z. B. 'DE 123 456 789' -> ('DE', '123456789')
    """
    s = (vat_id or "").strip().upper().replace(" ", "")
    if len(s) < 3:
        return ("", s)
    if s[:2].isalpha():
        return (s[:2], s[2:].replace(" ", ""))
    return ("", s)


def check_vat_format(vat_id: str) -> Optional[str]:
    """
    Prüft nur das Format (Ländercode + Ziffern).
    Returns: None wenn plausibel, sonst Fehlermeldung.
    """
    country, number = normalize_vat_number(vat_id)
    if not country or country not in VIES_COUNTRY_CODES:
        return "Ungültiger oder fehlender EU-Ländercode"
    if not number or not re.match(r"^[A-Z0-9]+$", number):
        return "USt-Nummer darf nur Ziffern/Buchstaben enthalten"
    if len(number) < 4:
        return "USt-Nummer zu kurz"
    return None


def check_vat_vies(vat_id: str, use_test_service: bool = False) -> VIESResult:
    """
    Prüft USt-ID gegen den EU-VIES-SOAP-Service.

    Bei Netzwerkfehlern oder 500 des Dienstes: service_unavailable=True,
    valid=False, error_message gesetzt. Formatprüfung erfolgt vorab.
    """
    country, number = normalize_vat_number(vat_id)
    format_err = check_vat_format(vat_id)
    if format_err:
        return VIESResult(
            valid=False,
            country_code=country or "",
            vat_number=number or vat_id,
            error_message=format_err,
        )

    url = VIES_CHECK_VAT_TEST_URL if use_test_service else VIES_CHECK_VAT_URL
    soap_body = f"""<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:urn="urn:ec.europa.eu:taxud:vies:services:checkVat:types">
  <soap:Body>
    <urn:checkVat>
      <urn:countryCode>{country}</urn:countryCode>
      <urn:vatNumber>{number}</urn:vatNumber>
    </urn:checkVat>
  </soap:Body>
</soap:Envelope>"""

    try:
        import requests
        resp = requests.post(
            url,
            data=soap_body.encode("utf-8"),
            headers={
                "Content-Type": "text/xml; charset=utf-8",
                "SOAPAction": "",
            },
            timeout=10,
        )
    except Exception as e:
        logger.warning("VIES request failed: %s", e)
        return VIESResult(
            valid=False,
            country_code=country,
            vat_number=number,
            error_message=str(e),
            service_unavailable=True,
        )

    if resp.status_code != 200:
        return VIESResult(
            valid=False,
            country_code=country,
            vat_number=number,
            error_message=f"VIES HTTP {resp.status_code}",
            raw_response=resp.text[:500] if resp.text else None,
            service_unavailable=resp.status_code >= 500,
        )

    # Einfaches Parsing der SOAP-Antwort (valid, name, address)
    text = resp.text or ""
    valid = "<valid>true</valid>" in text.lower()
    name = None
    address = None
    req_id = None
    fault = None
    if "<soap:Fault>" in text or "<faultstring>" in text:
        import re as re_mod
        m = re_mod.search(r"<faultstring[^>]*>([^<]+)</faultstring>", text, re_mod.IGNORECASE | re_mod.DOTALL)
        if m:
            fault = m.group(1).strip()
    if not fault:
        m = re.search(r"<name>([^<]*)</name>", text, re.IGNORECASE)
        if m:
            name = m.group(1).strip() or None
        m = re.search(r"<address>([^<]*)</address>", text, re.IGNORECASE)
        if m:
            address = m.group(1).strip() or None
        m = re.search(r"<requestIdentifier>([^<]*)</requestIdentifier>", text, re.IGNORECASE)
        if m:
            req_id = m.group(1).strip() or None

    return VIESResult(
        valid=valid and not fault,
        country_code=country,
        vat_number=number,
        request_identifier=req_id,
        name=name,
        address=address,
        raw_response=text[:1000] if logger.isEnabledFor(logging.DEBUG) else None,
        error_message=fault,
        service_unavailable=False,
    )
