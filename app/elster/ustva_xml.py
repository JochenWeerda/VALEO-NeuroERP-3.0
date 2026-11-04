"""
UStVA als XML: die Kennzahlen einer Anmeldung zum Datenaustausch (z. B. mit der Steuerberatung).

Das ist **keine** ELSTER-Uebermittlung. ELSTER nimmt eine Voranmeldung nur signiert ueber ERiC an; ERiC ist nicht
angebunden. Uebermittelt wird im ELSTER-Portal, die Anmeldung haelt danach das Transferticket fest.

Bis 27.10.2026 behauptete diese Datei „gemaess offiziellem Schema“ und ordnete Kennziffern falsch zu (Kz35/36 als
Umsaetze 19 %/7 %; tatsaechlich sind das Bemessungsgrundlage und Steuer zu anderen Steuersaetzen) und schrieb
Bemessungsgrundlagen mit Cent. Jetzt gilt wie im Formular: Bemessungsgrundlagen in vollen Euro (Cent entfallen),
Steuerbetraege mit Cent; Zeitraum ``01``–``12`` fuer Monate, ``41``–``44`` fuer Quartale.

Encoding: ISO-8859-15.
"""

from datetime import datetime
from decimal import ROUND_DOWN, Decimal
from typing import Any, Dict, List, Optional

#: Kennzahl der Steuer zu einer Bemessungsgrundlage, wo das Formular beide fuehrt (andere Steuersaetze).
STEUER_ZUR_KENNZAHL = {"35": "36"}


def _euro(val: Any) -> str:
    """Volle Euro, Cent entfallen (Bemessungsgrundlagen)."""
    return str(Decimal(str(val or 0)).to_integral_value(rounding=ROUND_DOWN))


def _cent(val: Any) -> str:
    """Betrag mit zwei Nachkommastellen, Punkt als Dezimaltrennzeichen (Steuerbetraege)."""
    return f"{Decimal(str(val or 0)).quantize(Decimal('0.01')):f}"


def _elster_escape(text: Optional[str]) -> str:
    """Text für XML escapen (ISO-8859-15)."""
    if not text:
        return ""
    s = str(text)
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def zeitraum_code(period: str) -> tuple[str, str]:
    """``2026-03`` -> (``2026``, ``03``); ``2026-Q2`` -> (``2026``, ``42``)."""
    jahr, teil = period.split("-", 1)
    if teil.startswith("Q"):
        return jahr, f"4{int(teil[1:])}"
    return jahr, f"{int(teil):02d}"


def build_ustva_elster_xml(
    period: str,
    taxpayer_name: str,
    tax_id: Optional[str] = None,
    vat_id: Optional[str] = None,
    strasse: Optional[str] = None,
    hausnummer: Optional[str] = None,
    plz: Optional[str] = None,
    ort: Optional[str] = None,
    positions: Optional[List[Dict[str, Any]]] = None,
    vat_payable: Optional[Decimal] = None,
    data_lieferant: str = "VALEO NeuroERP",
) -> bytes:
    """Kennzahlen der Anmeldung (``app.finance.ustva.Kennzahl`` als dict) als XML."""
    ns = "http://finkonsens.de/elster/elsteranmeldung/ustva/v2023"  # NOSONAR - XML-Namensraum ist eine feste Kennung des Standards, kein Netzzugriff
    ET: Any
    import xml.etree.ElementTree as ET

    root = ET.Element("Anmeldungssteuern", attrib={"version": "2023", "xmlns": ns})
    ET.SubElement(root, "Erstellungsdatum").text = datetime.now().strftime("%Y%m%d")
    ET.SubElement(root, "DatenLieferant").text = _elster_escape(data_lieferant)

    steuerfall = ET.SubElement(root, "Steuerfall")
    mandant = ET.SubElement(steuerfall, "Mandant")
    if tax_id:
        ET.SubElement(mandant, "Steuernummer").text = _elster_escape(tax_id)

    unternehmer = ET.SubElement(steuerfall, "Unternehmer")
    ET.SubElement(unternehmer, "Name").text = _elster_escape(taxpayer_name)
    for tag, wert in (("Strasse", strasse), ("Hausnummer", hausnummer), ("Postleitzahl", plz), ("Ort", ort)):
        if wert:
            ET.SubElement(unternehmer, tag).text = _elster_escape(wert)

    ustva = ET.SubElement(steuerfall, "Umsatzsteuervoranmeldung")
    jahr, zeitraum = zeitraum_code(period)
    ET.SubElement(ustva, "Jahr").text = jahr
    ET.SubElement(ustva, "Zeitraum").text = zeitraum

    for p in positions or []:
        kz = str(p.get("kennzahl") or "")
        if not kz.isdigit():
            raise ValueError(f"Position ohne gültige Kennzahl: {p!r}")
        if p.get("seite") == "vorsteuer":
            ET.SubElement(ustva, f"Kz{kz}").text = _cent(p.get("steuer"))
            continue
        ET.SubElement(ustva, f"Kz{kz}").text = _euro(p.get("bemessungsgrundlage"))
        if kz in STEUER_ZUR_KENNZAHL:
            ET.SubElement(ustva, f"Kz{STEUER_ZUR_KENNZAHL[kz]}").text = _cent(p.get("steuer"))

    if vat_payable is not None:
        ET.SubElement(ustva, "Kz83").text = _cent(vat_payable)

    rough = ET.tostring(root, encoding="utf-8", method="xml")
    decl = b'<?xml version="1.0" encoding="ISO-8859-15" standalone="no"?>\n'
    return decl + rough.decode("utf-8").encode("iso-8859-15", errors="replace")
