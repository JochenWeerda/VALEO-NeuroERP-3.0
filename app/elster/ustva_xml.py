"""
ELSTER UStVA XML — Aufbau gemäß offiziellem Schema.
Schema: http://finkonsens.de/elster/elsteranmeldung/ustva/v2023
Encoding: ISO-8859-15 (Pflicht für ELSTER-Upload).
Referenz: https://www.elster.de/eportal/helpGlobal?themaGlobal=ustva_upload
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

# ELSTER UStVA Kennziffern (Zeilen des Formulars)
# https://forum.elster.de, ERiC-Schnittstellenbeschreibung
KZ_STEUER_UMSAETZE_19 = "Kz35"   # Zeile 35 Steuerpflichtige Umsätze 19%
KZ_STEUER_UMSAETZE_7 = "Kz36"    # Zeile 36 Steuerpflichtige Umsätze 7%
KZ_VORSTEUER = "Kz66"            # Zeile 66 Vorsteuerbeträge
KZ_UMSAETZE_19 = "Kz81"          # Zeile 81 Umsätze 19%
KZ_UMSAETZE_7 = "Kz86"           # Zeile 86 Umsätze 7%
KZ_VERBLEIBENDE = "Kz83"         # Zeile 49 Verbleibende USt-Vorauszahlung

# Mapping position_code (aus tax_keys.ustva_position) → ELSTER-Kennziffer
POSITION_TO_KZ: Dict[str, str] = {
    "35": KZ_STEUER_UMSAETZE_19,
    "36": KZ_STEUER_UMSAETZE_7,
    "66": KZ_VORSTEUER,
    "81": KZ_UMSAETZE_19,
    "86": KZ_UMSAETZE_7,
    "83": KZ_VERBLEIBENDE,
}


def _format_amount(val: Any) -> str:
    """Betrag auf 2 Nachkommastellen, Punkt als Dezimaltrennzeichen."""
    if val is None:
        return "0.00"
    d = Decimal(str(val))
    return f"{float(d):.2f}".replace(",", ".")


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
    total_sales_net: Optional[Decimal] = None,
    total_input_tax: Optional[Decimal] = None,
    total_output_tax: Optional[Decimal] = None,
    vat_payable: Optional[Decimal] = None,
    data_lieferant: str = "VALEO NeuroERP",
) -> bytes:
    """
    Erzeugt ELSTER-konforme UStVA-XML (Anmeldungssteuern).
    Encoding: ISO-8859-15.
    """
    ns = "http://finkonsens.de/elster/elsteranmeldung/ustva/v2023"
    ET: Any
    import xml.etree.ElementTree as ET

    root = ET.Element("Anmeldungssteuern", attrib={"version": "2023", "xmlns": ns})

    # Erstellungsdatum YYYYMMDD
    heute = datetime.now().strftime("%Y%m%d")
    erstell = ET.SubElement(root, "Erstellungsdatum")
    erstell.text = heute

    dl = ET.SubElement(root, "DatenLieferant")
    dl.text = _elster_escape(data_lieferant)

    steuerfall = ET.SubElement(root, "Steuerfall")

    # Mandant (Steuernummer erforderlich)
    mandant = ET.SubElement(steuerfall, "Mandant")
    if tax_id:
        mnr = ET.SubElement(mandant, "Steuernummer")
        mnr.text = _elster_escape(tax_id)

    # Unternehmer (Name, Adresse)
    unternehmer = ET.SubElement(steuerfall, "Unternehmer")
    name = ET.SubElement(unternehmer, "Name")
    name.text = _elster_escape(taxpayer_name)
    if strasse:
        s = ET.SubElement(unternehmer, "Strasse")
        s.text = _elster_escape(strasse)
    if hausnummer:
        h = ET.SubElement(unternehmer, "Hausnummer")
        h.text = _elster_escape(hausnummer)
    if plz:
        p = ET.SubElement(unternehmer, "Postleitzahl")
        p.text = _elster_escape(plz)
    if ort:
        o = ET.SubElement(unternehmer, "Ort")
        o.text = _elster_escape(ort)

    # Umsatzsteuervoranmeldung
    ustva = ET.SubElement(steuerfall, "Umsatzsteuervoranmeldung")

    # Jahr und Zeitraum (Monat 1-12)
    year, month = period.split("-")[0], period.split("-")[1] if "-" in period else "01"
    jahr = ET.SubElement(ustva, "Jahr")
    jahr.text = year
    zeitraum = ET.SubElement(ustva, "Zeitraum")
    zeitraum.text = str(int(month))

    # Kennziffern aus positions
    pos_map: Dict[str, Decimal] = {}
    if positions:
        for p in positions:
            pc = str(p.get("position_code", ""))
            kz = POSITION_TO_KZ.get(pc, f"Kz{pc}" if pc.isdigit() else pc)
            net = Decimal(str(p.get("net_amount", 0)))
            tax = Decimal(str(p.get("tax_amount", 0)))
            # Umsätze: Netto; Vorsteuer (Kz66): Steuerbetrag
            if kz == KZ_VORSTEUER:
                pos_map[kz] = pos_map.get(kz, Decimal("0")) + tax
            elif kz != KZ_VERBLEIBENDE:  # Kz83 kommt immer aus vat_payable
                pos_map[kz] = pos_map.get(kz, Decimal("0")) + net

    # Fallback auf Summen wenn keine positions
    if not pos_map and total_sales_net is not None:
        # Vereinfacht: Kz81 = Umsätze 19%, Kz66 = Vorsteuer
        kz81 = ET.SubElement(ustva, KZ_UMSAETZE_19)
        kz81.text = _format_amount(total_sales_net)
        if total_input_tax is not None:
            kz66 = ET.SubElement(ustva, KZ_VORSTEUER)
            kz66.text = _format_amount(total_input_tax)
        if vat_payable is not None:
            kz83 = ET.SubElement(ustva, KZ_VERBLEIBENDE)
            kz83.text = _format_amount(vat_payable)
    else:
        for kz, betrag in pos_map.items():
            elem = ET.SubElement(ustva, kz)
            elem.text = _format_amount(betrag)

        if vat_payable is not None and KZ_VERBLEIBENDE not in pos_map:
            kz83 = ET.SubElement(ustva, KZ_VERBLEIBENDE)
            kz83.text = _format_amount(vat_payable)

    # XML serialisieren (ELSTER: ISO-8859-15)
    rough = ET.tostring(root, encoding="utf-8", method="xml")
    # Declaration + Content; ELSTER verlangt ISO-8859-15
    decl = b'<?xml version="1.0" encoding="ISO-8859-15" standalone="no"?>\n'
    return decl + rough.decode("utf-8").encode("iso-8859-15", errors="replace")
