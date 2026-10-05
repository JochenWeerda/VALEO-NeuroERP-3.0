"""Sendung: die gemeinsamen Beförderungsdaten.

Lieferschein und Frachtbrief sind zwei Belege. Sie lesen dieselbe Sendung
und bleiben eigene Dokumenttypen.

Führend ist nicht der Ausdruck, sondern der Satz, der die Tatsache zuerst kennt:

- Handelsgeschäft (Käufer, Auftrag, Artikel, Handelsmenge, Charge, Kontrakt): Lieferschein
- Transportauftrag: Tour
- Fahrzeug, Fahrer, Ladeort, Ablieferstelle, Lademenge: Verladung
- Brutto, Tara, Netto: Wägung
- Frachtführer, Anhänger, Verpackung, besondere Transportbedingungen: Sendung
- Produktrechtliche Kennzeichnung: Begleitdokument, nicht der Frachtbrief
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Any


class Belegart(str, Enum):
    LIEFERSCHEIN = "lieferschein"
    FRACHTBRIEF = "frachtbrief"
    BEGLEITDOKUMENT = "begleitdokument"


class FuehrenderSatz(str, Enum):
    AUFTRAG = "auftrag"
    LIEFERSCHEIN = "lieferschein"
    TOUR = "tour"
    SENDUNG = "sendung"
    VERLADUNG = "verladung"
    WIEGUNG = "wiegung"
    BEGLEITDOKUMENT = "begleitdokument"


FUEHREND: dict[str, FuehrenderSatz] = {
    "kaeufer": FuehrenderSatz.LIEFERSCHEIN,
    "auftrag": FuehrenderSatz.AUFTRAG,
    "artikel": FuehrenderSatz.LIEFERSCHEIN,
    "handelsmenge": FuehrenderSatz.LIEFERSCHEIN,
    "charge": FuehrenderSatz.LIEFERSCHEIN,
    "kontrakt": FuehrenderSatz.LIEFERSCHEIN,
    "transportauftrag": FuehrenderSatz.TOUR,
    "fahrzeug": FuehrenderSatz.VERLADUNG,
    "fahrer": FuehrenderSatz.VERLADUNG,
    "ladeort": FuehrenderSatz.VERLADUNG,
    "ablieferstelle": FuehrenderSatz.VERLADUNG,
    "lademenge": FuehrenderSatz.VERLADUNG,
    "brutto": FuehrenderSatz.WIEGUNG,
    "tara": FuehrenderSatz.WIEGUNG,
    "netto": FuehrenderSatz.WIEGUNG,
    "frachtfuehrer": FuehrenderSatz.SENDUNG,
    "anhaenger": FuehrenderSatz.SENDUNG,
    "verpackung": FuehrenderSatz.SENDUNG,
    "produktrecht": FuehrenderSatz.BEGLEITDOKUMENT,
}


@dataclass(frozen=True)
class Sendung:
    """Beförderung. Der Lieferschein hängt nur als Referenz daran."""

    absender: str
    empfaenger: str
    ladeort: str
    ablieferstelle: str
    kennzeichen: str
    artikel: str
    menge: Decimal
    einheit: str
    frachtfuehrer: str | None = None
    fahrer: str | None = None
    anhaenger_kennzeichen: str | None = None
    verpackung: str | None = None
    brutto: Decimal | None = None
    tara: Decimal | None = None
    netto: Decimal | None = None
    charge: str | None = None
    lieferschein_nr: str | None = None
    auftrag_nr: str | None = None


@dataclass(frozen=True)
class LieferscheinSicht:
    """Warenbeleg: was der Verkäufer dem Käufer aufgrund des Auftrags liefert."""

    belegart: Belegart
    kunde: str
    artikel: str
    menge: Decimal
    einheit: str
    auftrag_nr: str | None
    charge: str | None
    lieferschein_nr: str | None


@dataclass(frozen=True)
class FrachtbriefSicht:
    """Transportbeleg: wer welche Ware von wo nach wo befördert."""

    belegart: Belegart
    absender: str
    empfaenger: str
    ladeort: str
    ablieferstelle: str
    kennzeichen: str
    anhaenger_kennzeichen: str | None
    frachtfuehrer: str | None
    fahrer: str | None
    artikel: str
    verpackung: str | None
    menge: Decimal
    brutto: Decimal | None
    tara: Decimal | None
    netto: Decimal | None
    lieferschein_nr: str | None


def lieferschein_sicht(sendung: Sendung) -> LieferscheinSicht:
    return LieferscheinSicht(
        belegart=Belegart.LIEFERSCHEIN,
        kunde=sendung.empfaenger,
        artikel=sendung.artikel,
        menge=sendung.netto if sendung.netto is not None else sendung.menge,
        einheit=sendung.einheit,
        auftrag_nr=sendung.auftrag_nr,
        charge=sendung.charge,
        lieferschein_nr=sendung.lieferschein_nr,
    )


def frachtbrief_sicht(sendung: Sendung) -> FrachtbriefSicht:
    return FrachtbriefSicht(
        belegart=Belegart.FRACHTBRIEF,
        absender=sendung.absender,
        empfaenger=sendung.empfaenger,
        ladeort=sendung.ladeort,
        ablieferstelle=sendung.ablieferstelle,
        kennzeichen=sendung.kennzeichen,
        anhaenger_kennzeichen=sendung.anhaenger_kennzeichen,
        frachtfuehrer=sendung.frachtfuehrer,
        fahrer=sendung.fahrer,
        artikel=sendung.artikel,
        verpackung=sendung.verpackung,
        menge=sendung.netto if sendung.netto is not None else sendung.menge,
        brutto=sendung.brutto,
        tara=sendung.tara,
        netto=sendung.netto,
        lieferschein_nr=sendung.lieferschein_nr,
    )


def _text(value: Any) -> str:
    return str(value or "").strip()


def sendung_aus_verladung(verladung: Any) -> Sendung | None:
    """Baut die Sendung aus der Verladung. Unvollständig → kein Beleg."""
    kennzeichen = _text(getattr(verladung, "kennzeichen", None))
    artikel = _text(getattr(verladung, "artikel", None))
    ladeort = _text(getattr(verladung, "ladeort", None))
    empfaenger = _text(getattr(verladung, "kunde", None)) or _text(getattr(verladung, "zielort", None))
    ablieferstelle = _text(getattr(verladung, "zielort", None)) or empfaenger
    menge = getattr(verladung, "menge", None)
    if str(getattr(verladung, "status", "") or "") != "verladen":
        return None
    if not kennzeichen or not artikel or not ladeort or not empfaenger or menge is None:
        return None
    menge_dec = Decimal(str(menge))
    if menge_dec <= 0:
        return None
    return Sendung(
        absender=ladeort,
        empfaenger=empfaenger,
        ladeort=ladeort,
        ablieferstelle=ablieferstelle,
        kennzeichen=kennzeichen,
        fahrer=_text(getattr(verladung, "fahrer", None)) or None,
        artikel=artikel,
        menge=menge_dec,
        einheit=_text(getattr(verladung, "einheit", None)) or "t",
        lieferschein_nr=_text(getattr(verladung, "lieferschein_nr", None)) or None,
    )
