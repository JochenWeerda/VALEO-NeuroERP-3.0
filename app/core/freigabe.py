"""Freigabematrix (APPROVAL-001): welche Freigabe ein Vorgang braucht.

Entscheidung des Auftraggebers vom 13.10.2026: Buchen und Stornieren unterliegen einer risikobasierten Freigabe —
kein generelles Vier-Augen-Prinzip, sondern Betragsgrenzen, Risikoklassen und Funktionstrennung. Hier steht nur
die Regel, ohne Datenbank; durchgesetzt wird sie in ``app/services/docflow_freigabe.py``.

Die Betraege sind Startwerte der ERP-Governance, **keine gesetzlichen Schwellen**, und vor produktiver Anwendung
fachlich abzunehmen. Ein Mandant kann sie fuer sich enger setzen, nicht weiter (restriktive Systemvorgabe).

| Vorgang | Freigabe |
|---|---|
| Ausgangsrechnung buchen bis 10.000 EUR brutto | R2 — Rollenrecht |
| Ausgangsrechnung buchen darueber | R3 — zweite Person |
| Eingangsrechnung buchen bis 5.000 EUR brutto, Rechnungsabgleich in Ordnung | R2 — Rollenrecht |
| Eingangsrechnung darueber, mit Abweichung oder ohne Abgleich | R3 — zweite Person |
| Gutschrift buchen bis 1.000 EUR brutto | R3 — zweite Person |
| Gutschrift darueber | R4 — zweite Person mit erhoehter Berechtigung |
| Nicht gebuchten Beleg zuruecknehmen | R2 — Rollenrecht und Begruendung |
| Gebuchten Beleg stornieren | R4 — zweite Person mit erhoehter Berechtigung, gleich welcher Betrag |

Eine Stueckelung unter die Grenze (mehrere Belege aus demselben Vorgang) zaehlt wie der Gesamtbetrag.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from app.core.belegvertrag import BELEGARTEN

GUELTIGKEIT_STUNDEN = 24

# Grenze je Gruppe in EUR brutto; bis einschliesslich genuegt die niedrigere Stufe.
STANDARDGRENZEN: dict[str, Decimal] = {
    "ausgangsrechnung": Decimal("10000"),
    "eingangsrechnung": Decimal("5000"),
    "gutschrift": Decimal("1000"),
}

GRUPPE: dict[str, str] = {
    "sales_invoice": "ausgangsrechnung",
    "purchase_invoice": "eingangsrechnung",
    "sales_credit_memo": "gutschrift",
    "purchase_credit_memo": "gutschrift",
}

AKTIONEN: tuple[str, ...] = ("post", "reverse")


@dataclass(frozen=True)
class Anforderung:
    risiko: str  # R2, R3 oder R4
    grund: str

    @property
    def zweitfreigabe(self) -> bool:
        return self.risiko in {"R3", "R4"}

    @property
    def erhoeht(self) -> bool:
        return self.risiko == "R4"


def wirksame_grenze(gruppe: str, mandantenwert: Decimal | None) -> Decimal:
    """Der Mandant kann die Grenze enger setzen, nicht weiter."""
    standard = STANDARDGRENZEN[gruppe]
    if mandantenwert is None or mandantenwert < 0:
        return standard
    return min(standard, mandantenwert)


def anforderung(
    belegart: str,
    aktion: str,
    *,
    brutto: Decimal,
    gebucht: bool,
    grenze: Decimal | None = None,
    abgleich_in_ordnung: bool = True,
    abgleich_hinweis: str = "",
    brutto_des_vorgangs: Decimal | None = None,
) -> Anforderung:
    """Die Freigabe, die dieser Vorgang braucht.

    ``brutto_des_vorgangs`` ist die Summe aller Belege derselben Art aus demselben Vorgang (Stueckelung);
    ``abgleich_in_ordnung`` gilt nur fuer die Eingangsrechnung.
    """
    variante = BELEGARTEN.get(belegart)
    if variante is None or aktion not in AKTIONEN:
        return Anforderung("R2", "Rollenrecht genügt.")
    if aktion == "reverse":
        if variante.bucht and gebucht:
            return Anforderung("R4", "Storno eines gebuchten Belegs: zweite Person mit erhöhter Berechtigung.")
        return Anforderung("R2", "Rollenrecht und Begründung genügen.")
    gruppe = GRUPPE.get(belegart)
    if gruppe is None:
        return Anforderung("R2", "Rollenrecht genügt.")
    g = grenze if grenze is not None else STANDARDGRENZEN[gruppe]
    gestueckelt = brutto <= g and brutto_des_vorgangs is not None and brutto_des_vorgangs > g
    ueber = brutto > g or gestueckelt
    warum = (
        f"mehrere Belege desselben Vorgangs ergeben zusammen {brutto_des_vorgangs} EUR und überschreiten {g} EUR"
        if gestueckelt else f"Betrag {brutto} EUR über {g} EUR"
    )
    if gruppe == "gutschrift":
        if ueber:
            return Anforderung("R4", f"Gutschrift, {warum}: zweite Person mit erhöhter Berechtigung.")
        return Anforderung("R3", "Gutschrift: Freigabe durch eine zweite Person (Funktionstrennung).")
    if ueber:
        return Anforderung("R3", f"{variante.bezeichnung}, {warum}: zweite Person.")
    if gruppe == "eingangsrechnung" and not abgleich_in_ordnung:
        return Anforderung("R3", f"Eingangsrechnung ohne erfolgreichen Rechnungsabgleich ({abgleich_hinweis}): zweite Person.")
    return Anforderung("R2", "Rollenrecht genügt.")
