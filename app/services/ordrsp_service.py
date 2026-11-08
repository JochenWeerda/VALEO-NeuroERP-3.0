"""EDIFACT ORDRSP (Bestellantwort, D.96A) lesen und gegen die Bestellung abgleichen.

Reiner Dienst ohne Datenbank: ``parse_ordrsp`` liest die Nachricht, ``abgleich`` vergleicht ihre Positionen mit
denen der Bestellung. Der Erfassungsweg (``einkauf_ab_erfassung``) legt daraus die Auftragsbestaetigung an.

Gelesene Segmente: UNA (Trennzeichen), BGM (Nummer, Funktion), DTM+137 (Datum), DTM+2 (Liefertermin), RFF+ON
(Bestellnummer), CUX (Waehrung), LIN (Position, Aktion, Artikel), PIA (Artikelnummern), QTY+21/113 (Menge), PRI
(Preis), MOA+79/86/128 (Summe). Unbekannte Segmente werden uebergangen, nicht erfunden.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any, Optional

#: LIN-Aktionscode (DE 1229): 3 geaendert, 5 angenommen ohne Aenderung, 7 nicht angenommen.
AKTION = {"3": "geaendert", "5": "angenommen", "7": "abgelehnt"}
#: BGM-Funktion (DE 1225): 27 nicht angenommen, 29 angenommen ohne Aenderung, 4 Aenderung.
FUNKTION = {"27": "abgelehnt", "29": "angenommen", "4": "geaendert"}


class OrdrspFehler(ValueError):
    """Die Nachricht ist keine lesbare ORDRSP."""


@dataclass
class AbPosition:
    pos: str
    artikel: Optional[str] = None
    lieferanten_artnr: Optional[str] = None
    menge: Optional[Decimal] = None
    preis: Optional[Decimal] = None
    lieferdatum: Optional[date] = None
    aktion: Optional[str] = None


@dataclass
class Ordrsp:
    ab_nummer: str
    bestellnummer: str
    funktion: Optional[str] = None
    datum: Optional[date] = None
    lieferdatum: Optional[date] = None
    waehrung: Optional[str] = None
    gesamtbetrag: Optional[Decimal] = None
    positionen: list[AbPosition] = field(default_factory=list)


def _segmente(raw: str) -> tuple[list[list[list[str]]], str]:
    text = raw.replace("\r", "").replace("\n", "")
    komponente, element, dezimal, freigabe, segment = ":", "+", ".", "?", "'"
    if text.startswith("UNA"):
        komponente, element, dezimal, freigabe, segment = text[3], text[4], text[5], text[6], text[8]
        text = text[9:]
    teile, aktuell, i = [], "", 0
    while i < len(text):
        zeichen = text[i]
        if zeichen == freigabe and i + 1 < len(text):
            aktuell += freigabe + text[i + 1]  # maskiertes Zeichen bleibt bis zur Feldtrennung markiert
            i += 2
            continue
        if zeichen == segment:
            if aktuell.strip():
                teile.append(aktuell.strip())
            aktuell = ""
        else:
            aktuell += zeichen
        i += 1
    if aktuell.strip():
        teile.append(aktuell.strip())

    def trenne(wert: str, zeichen: str) -> list[str]:
        stuecke, stueck, j = [], "", 0
        while j < len(wert):
            if wert[j] == freigabe and j + 1 < len(wert):
                stueck += wert[j:j + 2]
                j += 2
                continue
            if wert[j] == zeichen:
                stuecke.append(stueck)
                stueck = ""
            else:
                stueck += wert[j]
            j += 1
        stuecke.append(stueck)
        return stuecke

    def entmaske(wert: str) -> str:
        klar, k = "", 0
        while k < len(wert):
            if wert[k] == freigabe and k + 1 < len(wert):
                klar += wert[k + 1]
                k += 2
            else:
                klar += wert[k]
                k += 1
        return klar

    ergebnis = [[[entmaske(c) for c in trenne(el, komponente)] for el in trenne(s, element)] for s in teile]
    return ergebnis, dezimal


def _zahl(wert: str, dezimal: str) -> Optional[Decimal]:
    if not wert:
        return None
    try:
        return Decimal(wert.replace(dezimal, "."))
    except InvalidOperation as exc:
        raise OrdrspFehler(f"Keine Zahl: {wert}") from exc


def _datum(wert: str, format_code: str) -> Optional[date]:
    if not wert:
        return None
    formate = {"102": "%Y%m%d", "203": "%Y%m%d%H%M", "101": "%y%m%d"}
    try:
        return datetime.strptime(wert, formate.get(format_code or "102", "%Y%m%d")).date()
    except ValueError as exc:
        raise OrdrspFehler(f"Kein Datum: {wert}") from exc


def _feld(segment: list[list[str]], element: int, komponente: int = 0) -> str:
    if element < len(segment) and komponente < len(segment[element]):
        return segment[element][komponente].strip()
    return ""


def parse_ordrsp(raw: str) -> Ordrsp:
    if not raw or not raw.strip():
        raise OrdrspFehler("Nachricht ist leer.")
    segmente, dezimal = _segmente(raw)
    namen = [s[0][0] if s and s[0] else "" for s in segmente]
    unh = next((s for s in segmente if _feld(s, 0) == "UNH"), None)
    if unh is None or _feld(unh, 2, 0) != "ORDRSP":
        raise OrdrspFehler("Keine ORDRSP-Nachricht (UNH mit Typ ORDRSP fehlt).")
    ab_nummer = bestellnummer = ""
    kopf: dict[str, Any] = {}
    positionen: list[AbPosition] = []
    pos: Optional[AbPosition] = None
    for segment, name in zip(segmente, namen):
        if name == "BGM":
            ab_nummer = _feld(segment, 2)
            kopf["funktion"] = FUNKTION.get(_feld(segment, 3), _feld(segment, 3) or None)
        elif name == "DTM":
            qualifier, wert, fmt = _feld(segment, 1, 0), _feld(segment, 1, 1), _feld(segment, 1, 2)
            if qualifier == "137" and pos is None:
                kopf["datum"] = _datum(wert, fmt)
            elif qualifier in ("2", "69", "67"):
                if pos is None:
                    kopf["lieferdatum"] = _datum(wert, fmt)
                else:
                    pos.lieferdatum = _datum(wert, fmt)
        elif name == "RFF" and _feld(segment, 1, 0) == "ON":
            bestellnummer = _feld(segment, 1, 1)
        elif name == "CUX":
            kopf["waehrung"] = _feld(segment, 1, 1) or None
        elif name == "LIN":
            pos = AbPosition(pos=_feld(segment, 1) or str(len(positionen) + 1),
                             aktion=AKTION.get(_feld(segment, 2), _feld(segment, 2) or None),
                             artikel=_feld(segment, 3, 0) or None)
            positionen.append(pos)
        elif name == "PIA" and pos is not None:
            for element in segment[2:]:
                nummer, art = (element + ["", ""])[0], (element + ["", ""])[1]
                if art == "SA" and nummer:
                    pos.lieferanten_artnr = nummer
                elif art in ("BP", "IN") and nummer:
                    pos.artikel = nummer
        elif name == "QTY" and pos is not None and _feld(segment, 1, 0) in ("21", "113", "12"):
            pos.menge = _zahl(_feld(segment, 1, 1), dezimal)
        elif name == "PRI" and pos is not None:
            pos.preis = _zahl(_feld(segment, 1, 1), dezimal)
        elif name == "MOA" and _feld(segment, 1, 0) in ("79", "86", "128"):
            kopf["gesamtbetrag"] = _zahl(_feld(segment, 1, 1), dezimal)
    if not ab_nummer:
        raise OrdrspFehler("BGM ohne Nummer der Bestellantwort.")
    if not bestellnummer:
        raise OrdrspFehler("RFF+ON (Bestellnummer) fehlt.")
    return Ordrsp(ab_nummer=ab_nummer, bestellnummer=bestellnummer, positionen=positionen, **kopf)


def _gleich(a: Optional[Decimal], b: Any) -> bool:
    if a is None or b is None:
        return True  # fehlende Angabe ist keine Abweichung
    return abs(Decimal(str(a)) - Decimal(str(b))) <= Decimal("0.005")


def abgleich(bestellpositionen: list[dict[str, Any]], antwort: Ordrsp) -> list[dict[str, Any]]:
    """Abweichungen der Bestellantwort zur Bestellung, je Position.

    ``bestellpositionen``: Zeilen mit ``pos_nr``, ``artikel_nr``, ``lieferanten_artnr``, ``menge``, ``einzelpreis``,
    ``lieferdatum``. Zuordnung ueber Artikel- oder Lieferanten-Artikelnummer, sonst ueber die Positionsnummer.
    """
    offen = list(bestellpositionen)
    abweichungen: list[dict[str, Any]] = []

    def finde(p: AbPosition) -> Optional[dict[str, Any]]:
        for kandidat in offen:
            if (p.artikel and p.artikel in (kandidat.get("artikel_nr"), kandidat.get("lieferanten_artnr"))) or \
                    (p.lieferanten_artnr and p.lieferanten_artnr == kandidat.get("lieferanten_artnr")):
                return kandidat
        return next((k for k in offen if str(k.get("pos_nr")) == p.pos), None)

    for p in antwort.positionen:
        bestellt = finde(p)
        bezug = p.artikel or p.lieferanten_artnr or f"Pos. {p.pos}"
        if bestellt is None:
            abweichungen.append({"art": "zusaetzlich", "position": bezug, "bestaetigt": str(p.menge or "")})
            continue
        offen.remove(bestellt)
        if p.aktion == "abgelehnt":
            abweichungen.append({"art": "abgelehnt", "position": bezug})
            continue
        if not _gleich(p.menge, bestellt.get("menge")):
            abweichungen.append({"art": "menge", "position": bezug, "bestellt": str(bestellt.get("menge")),
                                 "bestaetigt": str(p.menge)})
        if not _gleich(p.preis, bestellt.get("einzelpreis")):
            abweichungen.append({"art": "preis", "position": bezug, "bestellt": str(bestellt.get("einzelpreis")),
                                 "bestaetigt": str(p.preis)})
        termin = bestellt.get("lieferdatum")
        if p.lieferdatum and termin and p.lieferdatum != termin:
            abweichungen.append({"art": "termin", "position": bezug, "bestellt": str(termin),
                                 "bestaetigt": str(p.lieferdatum)})
    for rest in offen:
        abweichungen.append({"art": "nicht_bestaetigt", "position": rest.get("artikel_nr") or f"Pos. {rest.get('pos_nr')}"})
    return abweichungen


def abweichungstext(abweichungen: list[dict[str, Any]]) -> Optional[str]:
    if not abweichungen:
        return None
    texte = {"menge": "Menge", "preis": "Preis", "termin": "Termin"}
    zeilen = []
    for a in abweichungen:
        if a["art"] in texte:
            zeilen.append(f"{a['position']}: {texte[a['art']]} bestellt {a['bestellt']}, bestaetigt {a['bestaetigt']}")
        elif a["art"] == "zusaetzlich":
            zeilen.append(f"{a['position']}: nicht bestellt, bestaetigt {a['bestaetigt']}")
        elif a["art"] == "abgelehnt":
            zeilen.append(f"{a['position']}: vom Lieferanten abgelehnt")
        else:
            zeilen.append(f"{a['position']}: nicht bestaetigt")
    return "\n".join(zeilen)
