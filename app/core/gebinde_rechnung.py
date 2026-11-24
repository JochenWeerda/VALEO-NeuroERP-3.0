"""Gebinderechnung nach den Gebindetypen von a.eins (Nutzerauftrag 24.11.2026).

Fachgrundlage: ``docs/design/mengeneinheiten-aeins-uebernahme.md`` Abschnitt 3. Eine Gebinde-Mengeneinheit rechnet
eine Anzahl Gebinde mit bis zu vier Gebindefaktoren in die Ergebnismenge um (10 Sack a 25 kg = 250 kg) und - wenn die
effektive Menge eingegeben wird - zurueck in die Anzahl.

Reine Rechnung ohne Datenbank. Die Faktoren kommen nach der Faktorherkunft aus Mengeneinheit, Artikelstamm, Artikel
oder Artikel-Auspraegung (``faktoren_nach_herkunft``). Fehlt ein benoetigter Faktor, wird nicht gerechnet: dieselbe
Disziplin wie ``app/core/agrar_units.py``, keine Umrechnung ohne belegten Faktor.
"""
from __future__ import annotations

from decimal import ROUND_CEILING, ROUND_FLOOR, ROUND_HALF_UP, Decimal
from enum import Enum, IntEnum
from typing import Mapping, Optional, Sequence


class Gebindetyp(IntEnum):
    KEIN_GEBINDE = 0
    LINEAR = 1              # Anzahl x F1
    STUFE_2 = 2             # Anzahl x F1 x F2 (Flaeche)
    STUFE_3 = 3             # Anzahl x F1 x F2 x F3 (Volumen)
    ADDITION = 4            # Anzahl x (F1 + F2)
    SUBTRAKTION = 5         # Anzahl x (F1 - F2), z. B. Zaehlerstaende
    ANBRUCH_AUFGERUNDET = 6  # in a.eins deaktiv
    ANBRUCH_ABGERUNDET = 7   # in a.eins deaktiv
    F1_MAL_F2_DURCH_F3 = 8   # Anzahl x F1 x F2 / F3
    F1_BIS_F4 = 9            # Anzahl x F1 x F2 x F3 x F4 (Palette/Lagen/Kartons/Dosen)


#: Wie viele Faktoren ein Typ braucht.
BENOETIGTE_FAKTOREN = {
    Gebindetyp.KEIN_GEBINDE: 0, Gebindetyp.LINEAR: 1, Gebindetyp.STUFE_2: 2, Gebindetyp.STUFE_3: 3,
    Gebindetyp.ADDITION: 2, Gebindetyp.SUBTRAKTION: 2, Gebindetyp.F1_MAL_F2_DURCH_F3: 3, Gebindetyp.F1_BIS_F4: 4,
}


class Faktorherkunft(IntEnum):
    MENGENEINHEIT = 1
    ARTIKELSTAMM = 2
    ARTIKEL = 3
    AUSPRAEGUNG = 4


class Anbruch(str, Enum):
    """Behandlung einer nicht ganzzahligen Gebindeanzahl bei Eingabe der effektiven Menge."""

    NORMAL = "normal"        # Anzahl bleibt gebrochen
    ABRUNDEN = "abrunden"
    AUFRUNDEN = "aufrunden"


class GebindeNichtRechenbar(ValueError):
    """Typ deaktiv oder unbekannt, Faktor fehlt oder ungueltig - die Menge wird nicht geraten."""


def _typ(typ: int | Gebindetyp) -> Gebindetyp:
    try:
        gt = Gebindetyp(int(typ))
    except ValueError as fehler:
        raise GebindeNichtRechenbar(f"Unbekannter Gebindetyp {typ!r}.") from fehler
    if gt in (Gebindetyp.ANBRUCH_AUFGERUNDET, Gebindetyp.ANBRUCH_ABGERUNDET):
        raise GebindeNichtRechenbar(f"Gebindetyp {int(gt)} ist deaktiv.")
    return gt


def _faktoren(gt: Gebindetyp, faktoren: Sequence[Optional[Decimal]]) -> list[Decimal]:
    n = BENOETIGTE_FAKTOREN[gt]
    benutzt = list(faktoren[:n])
    if len(benutzt) < n or any(f is None for f in benutzt):
        raise GebindeNichtRechenbar(f"Gebindetyp {int(gt)} braucht {n} Faktor(en), hinterlegt: {list(faktoren)}.")
    werte = [Decimal(str(f)) for f in benutzt]
    if gt != Gebindetyp.SUBTRAKTION and any(f <= 0 for f in werte):
        raise GebindeNichtRechenbar("Gebindefaktoren muessen positiv sein.")
    return werte


def menge_je_gebinde(typ: int | Gebindetyp, faktoren: Sequence[Optional[Decimal]]) -> Decimal:
    """Ergebnismenge eines einzelnen Gebindes (Anzahl 1)."""
    gt = _typ(typ)
    f = _faktoren(gt, faktoren)
    if gt == Gebindetyp.KEIN_GEBINDE:
        return Decimal(1)
    if gt == Gebindetyp.ADDITION:
        return f[0] + f[1]
    if gt == Gebindetyp.SUBTRAKTION:
        return f[0] - f[1]
    if gt == Gebindetyp.F1_MAL_F2_DURCH_F3:
        return f[0] * f[1] / f[2]
    ergebnis = Decimal(1)
    for faktor in f:
        ergebnis *= faktor
    return ergebnis


def ergebnismenge(typ: int | Gebindetyp, anzahl: Decimal, faktoren: Sequence[Optional[Decimal]],
                  rundung: int = 3) -> Decimal:
    """Anzahl Gebinde -> Ergebnismenge, gerundet auf ``rundung`` Stellen (Rundung bei Umrechnung, 0-4)."""
    menge = Decimal(str(anzahl)) * menge_je_gebinde(typ, faktoren)
    return menge.quantize(Decimal(1).scaleb(-rundung), rounding=ROUND_HALF_UP)


def anzahl_aus_menge(typ: int | Gebindetyp, menge: Decimal, faktoren: Sequence[Optional[Decimal]],
                     anbruch: Anbruch = Anbruch.NORMAL, rundung: int = 3) -> Decimal:
    """Effektive Menge eingegeben -> Anzahl Gebinde (a.eins: "Effektive Menge eingebbar")."""
    je = menge_je_gebinde(typ, faktoren)
    if je == 0:
        raise GebindeNichtRechenbar("Ein Gebinde ergibt die Menge 0 - Anzahl nicht bestimmbar.")
    anzahl = Decimal(str(menge)) / je
    if anbruch == Anbruch.AUFRUNDEN:
        return anzahl.to_integral_value(rounding=ROUND_CEILING)
    if anbruch == Anbruch.ABRUNDEN:
        return anzahl.to_integral_value(rounding=ROUND_FLOOR)
    return anzahl.quantize(Decimal(1).scaleb(-rundung), rounding=ROUND_HALF_UP)


def faktoren_nach_herkunft(herkunft: int | Faktorherkunft,
                           stufen: Mapping[Faktorherkunft, Optional[Sequence[Optional[Decimal]]]]
                           ) -> tuple[Faktorherkunft, Sequence[Optional[Decimal]]]:
    """Faktoren suchen: auf der Stufe ``herkunft`` beginnen, bei "nicht gefunden" zur allgemeineren Stufe.

    Auslegung (a.eins: "bei nicht gefunden wird stets weiter unten weitergesucht"): die speziellere Stufe ueberstimmt
    die allgemeinere, die Mengeneinheit ist die Grundlage. Beginnt die Suche beim Artikel, gilt Artikel ->
    Artikelstamm -> Mengeneinheit. Gefunden heisst: mindestens ein Faktor hinterlegt.
    """
    start = Faktorherkunft(int(herkunft))
    for stufe in sorted((s for s in Faktorherkunft if s <= start), reverse=True):
        werte = stufen.get(stufe)
        if werte and any(f is not None for f in werte):
            return stufe, werte
    raise GebindeNichtRechenbar(f"Keine Gebindefaktoren ab Stufe {start.name.lower()} hinterlegt.")
