"""Kontrollregel der Finanzbuchhaltung (FIN-CONTROL-001): was auffaellt und was sperrt.

Entscheidung des Auftraggebers vom 13.10.2026 (abends), sie korrigiert die Freigabematrix vom selben Tag:
„Der Finanzbuchhalter hat den Hut auf. Der Controller ueberwacht die Ausnahmen – nicht jede einzelne
Routinebuchung." Nicht der Betrag allein entscheidet, sondern das Risiko, die Abweichung vom Standardprozess und die
finanzielle Auswirkung.

Zwei Stufen:

* **Warnung** — der Vorgang bleibt zulaessig und wird ausgefuehrt; der Befund geht in den Pruefkorb des Controllers.
* **Kritischer Befund** — der Vorgang ist gesperrt, bis der Controller oder eine andere unabhaengige berechtigte
  Person ihn freigibt.

Hier steht nur die Regel, ohne Datenbank. Befunde, die Daten brauchen (Dublette, Abweichung vom Vorgaenger,
geschuetzte Konten, Haeufung), liefert der Bereich; die Betragsschwellen stehen hier. Durchgesetzt wird in
``app/services/freigabe_engine.py``.

| Vorgang | Regel |
|---|---|
| Routine: Rechnung, Gutschrift, manuelle Hauptbuchbuchung, regelkonformer Storno | Rollenrecht |
| Betrag ueber der Schwelle, Stueckelung | Warnung |
| Moegliche Dublette, Abweichung vom Vorgaenger, geschuetztes Konto, Gutschrift ohne Bezug ueber der Schwelle | kritisch |
| Zahlungslauf ausfuehren | immer unabhaengige Freigabe (Zahlungsberechtigung) |

Die Schwellen sind Startwerte fuer Tests, **keine gesetzlichen Schwellen und keine endgueltige Risikopolitik**; sie
sind je Mandant einstellbar. Ein kritischer Befund gilt unabhaengig vom Betrag.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable, Literal

from app.core.belegvertrag import BELEGARTEN

GUELTIGKEIT_STUNDEN = 24

# Schwelle je Gruppe in EUR; darueber eine Warnung.
STANDARDGRENZEN: dict[str, Decimal] = {
    "ausgangsrechnung": Decimal("10000"),
    "eingangsrechnung": Decimal("5000"),
    "gutschrift": Decimal("1000"),
    "hauptbuch": Decimal("10000"),
    "agrar_korrektur": Decimal("250"),
}

AKTIONEN: tuple[str, ...] = ("post", "reverse")

# Vorgaenge der Finanzbuchhaltung, die keine Belegart des Belegvertrags sind.
HAUPTBUCHBUCHUNG = "manual_journal"
ZAHLUNGSLAUF = "payment_run"

GRUPPE: dict[str, str] = {
    "sales_invoice": "ausgangsrechnung",
    "purchase_invoice": "eingangsrechnung",
    "sales_credit_memo": "gutschrift",
    "purchase_credit_memo": "gutschrift",
    HAUPTBUCHBUCHUNG: "hauptbuch",
}


@dataclass(frozen=True)
class Befund:
    """Was die Kontrolle an einem Vorgang findet."""

    code: str
    schwere: Literal["warnung", "kritisch"]
    text: str


@dataclass(frozen=True)
class Anforderung:
    risiko: str  # R2 Rollenrecht, R3 unabhaengige Freigabe, R4 Zahlungsberechtigung
    grund: str
    befunde: tuple[Befund, ...] = ()

    @property
    def zweitfreigabe(self) -> bool:
        return self.risiko in {"R3", "R4"}

    @property
    def erhoeht(self) -> bool:
        return self.risiko == "R4"

    @property
    def warnungen(self) -> tuple[Befund, ...]:
        return tuple(b for b in self.befunde if b.schwere == "warnung")


def wirksame_grenze(gruppe: str, mandantenwert: Decimal | None) -> Decimal:
    """Die Schwelle des Mandanten, sonst der Startwert."""
    if mandantenwert is None or mandantenwert < 0:
        return STANDARDGRENZEN[gruppe]
    return mandantenwert


def anforderung(
    belegart: str,
    aktion: str,
    *,
    brutto: Decimal,
    gebucht: bool,
    grenze: Decimal | None = None,
    befunde: Iterable[Befund] = (),
    brutto_des_vorgangs: Decimal | None = None,
) -> Anforderung:
    """Was dieser Vorgang braucht — und was an ihm auffaellt.

    ``befunde`` liefert der Bereich. ``brutto_des_vorgangs`` ist die Summe aller Belege derselben Art aus demselben
    Vorgang (Stueckelung). ``gebucht`` bleibt Teil der Auskunft, entscheidet aber nichts mehr: Ein regelkonformer
    Storno braucht Rollenrecht und Begruendung.
    """
    liste = list(befunde)
    if aktion not in AKTIONEN:
        return Anforderung("R2", "Rollenrecht genügt.", tuple(liste))
    if belegart == ZAHLUNGSLAUF and aktion == "post":
        return Anforderung("R4", "Zahlungsfreigabe: unabhängige Person mit Zahlungsberechtigung.", tuple(liste))
    gruppe = GRUPPE.get(belegart)
    if aktion == "post" and gruppe is not None:
        g = grenze if grenze is not None else STANDARDGRENZEN[gruppe]
        name = "Manuelle Hauptbuchbuchung" if belegart == HAUPTBUCHBUCHUNG else BELEGARTEN[belegart].bezeichnung
        # Hauptbuch: „ab" der Schwelle; Belege: darueber.
        if brutto >= g if belegart == HAUPTBUCHBUCHUNG else brutto > g:
            liste.append(Befund("betrag", "warnung", f"{name}: Betrag {brutto} EUR, Schwelle {g} EUR."))
        elif brutto_des_vorgangs is not None and brutto_des_vorgangs > g:
            liste.append(Befund(
                "stueckelung", "warnung",
                f"{name}: mehrere Belege desselben Vorgangs ergeben zusammen {brutto_des_vorgangs} EUR und "
                f"überschreiten {g} EUR."))
    kritisch = [b for b in liste if b.schwere == "kritisch"]
    if kritisch:
        return Anforderung("R3", f"{kritisch[0].text} Unabhängige Freigabe erforderlich.", tuple(liste))
    return Anforderung("R2", "Rollenrecht genügt.", tuple(liste))
