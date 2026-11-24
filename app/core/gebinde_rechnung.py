"""Gebinderechnung nach den Gebindetypen von a.eins (Nutzerauftrag 24.11.2026).

Fachgrundlage: ``docs/design/mengeneinheiten-aeins-uebernahme.md`` Abschnitt 3. Eine Gebinde-Mengeneinheit rechnet
eine Anzahl Gebinde mit bis zu vier Gebindefaktoren in die Ergebnismenge um (10 Sack a 25 kg = 250 kg) und - wenn die
effektive Menge eingegeben wird - zurueck in die Anzahl.

Reine Rechnung ohne Datenbank. Die Faktoren kommen nach der Faktorherkunft aus Mengeneinheit, Artikelstamm, Artikel
oder Artikel-Auspraegung (``faktoren_nach_herkunft``). Fehlt ein benoetigter Faktor, wird nicht gerechnet: dieselbe
Disziplin wie ``app/core/agrar_units.py``, keine Umrechnung ohne belegten Faktor.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_CEILING, ROUND_FLOOR, ROUND_HALF_UP, Decimal, InvalidOperation
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


class FaktorFehlt(GebindeNichtRechenbar):
    """Auf keiner zugelassenen Stufe ist ein Faktor hinterlegt. Ein fehlender Faktor wird nie durch 1 ersetzt."""


class FaktorsatzUnvollstaendig(FaktorFehlt):
    """Die gefundene Stufe hat Faktoren, aber nicht alle, die der Gebindetyp braucht."""


class FaktorUngueltig(GebindeNichtRechenbar):
    """Ein Faktor ist hinterlegt, aber nicht verwendbar (keine Zahl, null oder negativ)."""


class FaktorpflegeNichtZulaessig(GebindeNichtRechenbar):
    """Faktoren auf einer Stufe, die die Faktorherkunft der Mengeneinheit nicht zulaesst."""


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
        raise FaktorsatzUnvollstaendig(f"Gebindetyp {int(gt)} braucht {n} Faktor(en), hinterlegt: {list(faktoren)}.")
    try:
        werte = [Decimal(str(f)) for f in benutzt]
    except (InvalidOperation, ValueError) as fehler:
        raise FaktorUngueltig(f"Gebindefaktor ist keine Zahl: {list(benutzt)}.") from fehler
    if any(not w.is_finite() for w in werte):
        raise FaktorUngueltig(f"Gebindefaktor ist keine endliche Zahl: {list(benutzt)}.")
    # Subtraktion (Zaehlerstaende): die Staende duerfen 0 sein, aber nicht negativ.
    if gt == Gebindetyp.SUBTRAKTION:
        if any(w < 0 for w in werte):
            raise FaktorUngueltig("Zaehlerstaende duerfen nicht negativ sein.")
    elif any(w <= 0 for w in werte):
        raise FaktorUngueltig("Gebindefaktoren muessen positiv sein.")
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


def suchpfad(herkunft: int | Faktorherkunft) -> tuple[Faktorherkunft, ...]:
    """Stufen, die die Faktorherkunft zulaesst, in Suchreihenfolge (a.eins: auf der eingestellten Stufe beginnen,
    bei "nicht gefunden" weiter unten suchen; bestaetigt 24.11.2026):

    1 Mengeneinheit | 2 Artikelstamm -> Mengeneinheit | 3 Artikel -> Artikelstamm -> Mengeneinheit |
    4 Auspraegung -> Artikel -> Artikelstamm -> Mengeneinheit.
    Speziellere Stufen oberhalb der eingestellten werden nie beruecksichtigt.
    """
    try:
        start = Faktorherkunft(int(herkunft))
    except ValueError as fehler:
        raise GebindeNichtRechenbar(f"Unbekannte Faktorherkunft {herkunft!r}.") from fehler
    return tuple(sorted((s for s in Faktorherkunft if s <= start), reverse=True))


def pruefe_faktorpflege(herkunft: int | Faktorherkunft, stufe: int | Faktorherkunft) -> None:
    """Faktoren duerfen nur auf Stufen gepflegt werden, die im Suchpfad liegen (a.eins: bei Faktorherkunft
    Mengeneinheit sind die Faktoren im Artikel nicht aenderbar). Fuer die serverseitige Pruefung der Stammpflege."""
    if Faktorherkunft(int(stufe)) not in suchpfad(herkunft):
        raise FaktorpflegeNichtZulaessig(
            f"Faktorherkunft {Faktorherkunft(int(herkunft)).name.lower()} laesst keine Faktoren auf Stufe "
            f"{Faktorherkunft(int(stufe)).name.lower()} zu.")


def faktoren_nach_herkunft(herkunft: int | Faktorherkunft,
                           stufen: Mapping[Faktorherkunft, Optional[Sequence[Optional[Decimal]]]]
                           ) -> tuple[Faktorherkunft, Sequence[Optional[Decimal]]]:
    """Erste Stufe im Suchpfad, auf der mindestens ein Faktor hinterlegt ist, mit ihrem Faktorsatz.

    Der Satz wird als Ganzes von einer Stufe genommen; Faktoren verschiedener Stufen werden nicht gemischt. Ist der
    Satz der gefundenen Stufe fuer den Gebindetyp unvollstaendig, meldet ``berechne_gebinde`` das, statt auf der
    naechsten Stufe weiterzusuchen oder Faktoren einzeln zusammenzusetzen: Ob a.eins einzeln oder satzweise aufloest,
    ist nicht belegt (offen, s. docs/design/mengeneinheiten-aeins-uebernahme.md).
    """
    pfad = suchpfad(herkunft)
    for stufe in pfad:
        werte = stufen.get(stufe)
        if werte and any(f is not None for f in werte):
            return stufe, werte
    raise FaktorFehlt(f"Keine Gebindefaktoren im Suchpfad {[s.name.lower() for s in pfad]} hinterlegt.")


@dataclass(frozen=True)
class Gebindeberechnung:
    """Ergebnis mit allem, was der Beleg zur Nachvollziehbarkeit festhaelt: Typ, eingestellte und tatsaechlich
    verwendete Herkunft, die verwendeten Faktoren, Anzahl, Rundung, Ergebnis. Ein Beleg rechnet spaeter aus diesem
    Abbild, nicht aus dem dann geaenderten Stamm."""

    gebindetyp: int
    faktorherkunft: int
    herkunft_verwendet: Optional[int]
    faktoren: tuple[str, ...]
    anzahl: str
    rundung: int
    ergebnis: str

    def als_dict(self) -> dict:
        return {"gebindetyp": self.gebindetyp, "faktorherkunft": self.faktorherkunft,
                "herkunft_verwendet": self.herkunft_verwendet, "faktoren": list(self.faktoren),
                "anzahl": self.anzahl, "rundung": self.rundung, "ergebnis": self.ergebnis}


def berechne_gebinde(typ: int | Gebindetyp, anzahl: Decimal, herkunft: int | Faktorherkunft,
                     stufen: Mapping[Faktorherkunft, Optional[Sequence[Optional[Decimal]]]],
                     rundung: int = 3) -> Gebindeberechnung:
    """Der eine Einstieg fuer Einkauf, Verkauf, Lager, Waage, Fakturierung und Bewertung."""
    gt = _typ(typ)
    if BENOETIGTE_FAKTOREN[gt] == 0:
        verwendet, faktoren = None, []
    else:
        verwendet, roh = faktoren_nach_herkunft(herkunft, stufen)
        faktoren = _faktoren(gt, roh)
    ergebnis = ergebnismenge(gt, anzahl, faktoren, rundung)
    return Gebindeberechnung(gebindetyp=int(gt), faktorherkunft=int(Faktorherkunft(int(herkunft))),
                             herkunft_verwendet=None if verwendet is None else int(verwendet),
                             faktoren=tuple(str(f) for f in faktoren), anzahl=str(Decimal(str(anzahl))),
                             rundung=rundung, ergebnis=str(ergebnis))
