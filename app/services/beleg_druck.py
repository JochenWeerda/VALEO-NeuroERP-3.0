"""Belegdruck: ein PDF je DocFlow-Beleg aus dem Belegvertrag (BELEG-052 Stufe 2b, 09.11.2026).

Die abgeloesten Belegseiten druckten je Speicher anders (Lieferschein-Druck des Einkaufs, Browserdruck im Verkauf).
Gedruckt wird jetzt der Beleg in Vertragsform: Kopf, Partner, Positionen und - nur mit Preisrecht und nur bei
Belegen mit Preisen - Einzelpreise, Steuergruppen und Summen. Der Leseweg schreibt nichts.
"""
from __future__ import annotations

import base64
from decimal import Decimal
from io import BytesIO
from typing import Any

from app.core.belegvertrag import BELEGARTEN, Beleg


def _betrag(wert: Any, waehrung: str) -> str:
    if wert is None:
        return ""
    zahl = Decimal(str(wert)).quantize(Decimal("0.01"))
    text = f"{zahl:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{text} {waehrung}"


def _menge(wert: Any) -> str:
    if wert is None:
        return ""
    zahl = Decimal(str(wert)).normalize()
    return format(zahl, "f").replace(".", ",")


def belegtitel(beleg: Beleg) -> str:
    """Ueberschrift des Drucks: Ein bestaetigter Auftrag geht als Auftragsbestaetigung hinaus."""
    if beleg.belegart == "sales_order" and beleg.status == "confirmed":
        return "Auftragsbestätigung"
    return BELEGARTEN[beleg.belegart].bezeichnung


def beleg_pdf(beleg: Beleg) -> bytes:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    variante = BELEGARTEN[beleg.belegart]
    titel = belegtitel(beleg)
    preise = beleg.summen is not None and variante.mit_preisen
    stile = getSampleStyleSheet()
    puffer = BytesIO()
    dokument = SimpleDocTemplate(puffer, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm,
                                 topMargin=18 * mm, bottomMargin=18 * mm,
                                 title=f"{titel} {beleg.beleg_nr}")
    partner = beleg.partner
    rolle = "Lieferant" if variante.partnerrolle == "lieferant" else "Kunde"
    teile: list[Any] = [
        Paragraph(f"{titel} {beleg.beleg_nr}", stile["Title"]),
        *([Paragraph(f"NACHDRUCK – Druck {beleg.druck_anzahl}", stile["Heading3"])] if beleg.druck_anzahl > 1 else []),
        Paragraph(f"Belegdatum: {beleg.belegdatum.strftime('%d.%m.%Y')} &nbsp;&nbsp; Status: {beleg.status}",
                  stile["Normal"]),
        Paragraph(f"{rolle}: {(partner.name or '') if partner else ''} "
                  f"({(partner.nummer or '') if partner else ''})", stile["Normal"]),
        Spacer(1, 6 * mm),
    ]
    kopf = ["Pos.", "Artikel", "Bezeichnung", "Menge", "Einheit"]
    if preise:
        kopf += ["Einzelpreis", "Netto"]
    zeilen = [kopf]
    for p in beleg.positionen:
        zeile = [str(p.pos_nr), p.artikel_nr, p.bezeichnung or "", _menge(p.menge), p.einheit or ""]
        if preise:
            zeile += [_betrag(p.einzelpreis, beleg.waehrung), _betrag(p.netto, beleg.waehrung)]
        zeilen.append(zeile)
    tabelle = Table(zeilen, repeatRows=1)
    tabelle.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("LINEBELOW", (0, 0), (-1, 0), 0.6, colors.black),
        ("ALIGN", (3, 1), (3, -1), "RIGHT"),
        *([("ALIGN", (5, 1), (-1, -1), "RIGHT")] if preise else []),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
    ]))
    teile.append(tabelle)
    if preise and beleg.summen is not None:
        teile.append(Spacer(1, 6 * mm))
        summen = [[f"Steuer {g.steuerschluessel or ''} {_menge(g.steuersatz)} %", _betrag(g.steuer, beleg.waehrung)]
                  for g in beleg.summen.steuergruppen]
        summen = [["Netto", _betrag(beleg.summen.netto, beleg.waehrung)], *summen,
                  ["Brutto", _betrag(beleg.summen.brutto, beleg.waehrung)]]
        block = Table(summen, hAlign="RIGHT")
        block.setStyle(TableStyle([("ALIGN", (1, 0), (1, -1), "RIGHT"),
                                   ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                                   ("LINEABOVE", (0, -1), (-1, -1), 0.6, colors.black)]))
        teile.append(block)
    dokument.build(teile)
    return puffer.getvalue()


def beleg_druck(beleg: Beleg) -> dict[str, str]:
    """Antwort des Downloadwegs: Dateiname und PDF (base64) fuer den Download-Vertrag des Mask Builders."""
    return {"dateiname": f"{beleg.belegart}_{beleg.beleg_nr}.pdf".replace("/", "-").replace("\\", "-"),
            "pdf": base64.b64encode(beleg_pdf(beleg)).decode("ascii")}
