"""Kaufmaennischer Rechenkern fuer Belegpositionen - eine Quelle fuer alle Belege (24.11.2026).

Vorher stand die Rechnung als ``_line_amounts`` nur in ``app/services/docflow_service.py``; sie lebt jetzt hier und
DocFlow ruft sie auf. Durchgaengig ``Decimal``, kaufmaennisch gerundet (ROUND_HALF_UP) **je Position**; der Beleg
summiert die gerundeten Positionen. Diese Reihenfolge ist fachlich gewollt: ein Beleg ueber neun Dieselpositionen
ergibt 660,10 EUR (Summe der gerundeten Positionen), nicht 660,11 EUR (gerundete Summe von 660,108 EUR) - Golden
Master ``tests/golden_master/diesel_220050.json``.

Getrennte Groessen, nicht vermischt:
- **Menge** in der Mengeneinheit der Position (z. B. Liter) - wird nicht in die Preiseinheit umgerechnet,
- **Preis** je **Preisbezugsmenge** (z. B. 140,00 EUR je 100 Liter; Preisbezugsmenge 100, Standard 1),
- Gebinderechnung (``app/core/gebinde_rechnung.py``) und Bestandseinheit sind eigene Kerne.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from typing import Iterable

CENT = Decimal("0.01")
EINS = Decimal("1")
HUNDERT = Decimal("100")


def geld(betrag: Decimal) -> Decimal:
    """Kaufmaennisch auf den Cent."""
    return Decimal(betrag).quantize(CENT, rounding=ROUND_HALF_UP)


@dataclass(frozen=True)
class Positionsbetraege:
    netto: Decimal
    steuer: Decimal
    brutto: Decimal


def positionsbetraege(menge: Decimal, preis: Decimal, rabatt_prozent: Decimal = Decimal("0"),
                      steuersatz: Decimal = Decimal("0"), preisbezug: Decimal = EINS) -> Positionsbetraege:
    """Netto = Menge x Preis / Preisbezugsmenge x (100 - Rabatt) / 100, je Position auf den Cent gerundet."""
    for name, wert in (("menge", menge), ("preis", preis), ("rabatt_prozent", rabatt_prozent),
                       ("steuersatz", steuersatz), ("preisbezug", preisbezug)):
        if not isinstance(wert, Decimal):
            raise TypeError(f"{name} muss Decimal sein, nicht {type(wert).__name__} (keine Gleitkommarechnung).")
    if preisbezug <= 0:
        raise ValueError("Preisbezugsmenge muss positiv sein.")
    netto = geld(menge * preis / preisbezug * (HUNDERT - rabatt_prozent) / HUNDERT)
    steuer = geld(netto * steuersatz / HUNDERT)
    return Positionsbetraege(netto=netto, steuer=steuer, brutto=geld(netto + steuer))


def belegsumme(betraege: Iterable[Decimal]) -> Decimal:
    """Summe der bereits gerundeten Positionsbetraege (keine zweite Rundung der ungerundeten Summe)."""
    return geld(sum(betraege, Decimal("0")))


def durchschnittspreis(netto_summe: Decimal, mengen_summe: Decimal, preisbezug: Decimal = EINS) -> Decimal:
    """Gewichteter Durchschnittspreis je Preisbezugsmenge (z. B. EUR je 100 Liter), auf den Cent."""
    if mengen_summe == 0:
        raise ValueError("Ohne Menge kein Durchschnittspreis.")
    return geld(netto_summe / mengen_summe * preisbezug)
