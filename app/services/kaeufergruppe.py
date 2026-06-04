"""Käufergruppen-Modell + realistisch gewinnbare Bedarfslücke (Durchdringungs-CRM).

Kernidee: Nicht jede rechnerische Bedarfslücke ist eine realistische Vertriebschance.
Ein Betriebsleiter streut bewusst auf mehrere Lieferanten (Preisvergleich, Risiko,
Unabhängigkeit) — die letzten Prozentpunkte bis zum Alleinlieferanten haben oft
abnehmenden Grenzertrag und sind teils bewusst verteidigte Einkaufsfreiheit.

Daher drei Lücken-Begriffe je Produktgruppe:
    theoretische Lücke          = Bedarf − Ist
    realistisch gewinnbare Lücke = max(0, Bedarf × Zielanteil − Ist)
    geschützte Restlücke         = Bedarf × (1 − Zielanteil)   (bewusst woanders)

Priorität = realistisch gewinnbare Lücke × Marge × Abschlusswahrscheinlichkeit
            ÷ Grenzaufwand   (Grenzaufwand steigt nahe Sättigung).

Reine Berechnungs-/Klassifikationslogik ohne DB — vollständig unit-testbar.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class BuyingGroup(str, Enum):
    PREISABFRAGER = "preisabfrager_ohne_abschluss"
    PREISVERHANDLER = "preisverhandler_mit_abschluss"
    BEZIEHUNGSKAEUFER = "beziehungskaeufer"
    LEISTUNGSKAEUFER = "leistungskaeufer"
    BEQUEMLICHKEITSKAEUFER = "bequemlichkeitskaeufer"
    RISIKO_STREUER = "risiko_streuer"
    OPPORTUNIST = "opportunist"
    SAISON_ERGAENZER = "saison_ergaenzer"
    STRATEGISCHER_STAMMKUNDE = "strategischer_stammkunde"
    SCHLAFENDER_POTENZIALKUNDE = "schlafender_potenzialkunde"
    UNBEKANNT = "unbekannt"


@dataclass(frozen=True)
class GruppenProfil:
    label: str
    # realistischer Zielanteil am Kundenbedarf (Share of Wallet), Korridor
    ziel_anteil_min: float
    ziel_anteil_max: float
    abschluss_faktor: float   # Abschlusswahrscheinlichkeits-Gewicht (0..1)
    grenzaufwand: float       # relativer Vertriebsaufwand je Chance (>1 = teuer)
    ansatz: str               # empfohlener Vertriebsansatz


# Alleinlieferant (100 %) ist bewusst NICHT das Standardziel.
GRUPPEN: dict[BuyingGroup, GruppenProfil] = {
    BuyingGroup.PREISABFRAGER: GruppenProfil(
        "Preisabfrager o. Abschluss", 0.40, 0.55, 0.25, 1.8,
        "Nicht jeden Preis blind nachtelefonieren — nur bei hoher Marge, strategischem Produkt oder klarer Abschlusschance priorisieren.",
    ),
    BuyingGroup.PREISVERHANDLER: GruppenProfil(
        "Preisverhandler m. Abschluss", 0.55, 0.75, 0.60, 1.2,
        "Gezielt Paketangebote, Staffelpreise und zeitlich begrenzte Aktionen nutzen; Rabatt diszipliniert führen.",
    ),
    BuyingGroup.BEZIEHUNGSKAEUFER: GruppenProfil(
        "Beziehungskäufer", 0.80, 0.92, 0.80, 0.8,
        "Frühzeitig betreuen, Service halten, Cross-Sell über Vertrauen.",
    ),
    BuyingGroup.LEISTUNGSKAEUFER: GruppenProfil(
        "Leistungs-/Beratungskäufer", 0.70, 0.88, 0.70, 1.0,
        "Mit fachlichem Nutzen, Versuchsdaten, Wirtschaftlichkeit und Beratung argumentieren.",
    ),
    BuyingGroup.BEQUEMLICHKEITSKAEUFER: GruppenProfil(
        "Bequemlichkeits-/Servicekäufer", 0.80, 0.93, 0.80, 0.7,
        "Einfache Bestellung, zuverlässige Lieferung, Abo/Standardbelieferung anbieten.",
    ),
    BuyingGroup.RISIKO_STREUER: GruppenProfil(
        "Risiko-Streuer / Mehrlieferant", 0.55, 0.75, 0.55, 1.3,
        "Nicht auf 100 % drängen. Zielanteil realistisch begrenzen, wichtigste Produktgruppen absichern.",
    ),
    BuyingGroup.OPPORTUNIST: GruppenProfil(
        "Opportunist. Wechselkäufer", 0.40, 0.60, 0.35, 1.7,
        "Nur bei passender Aktion/Verfügbarkeit; kein dauerhaftes Bindungsziel, geringe Vorhaltekosten.",
    ),
    BuyingGroup.SAISON_ERGAENZER: GruppenProfil(
        "Saisonaler Ergänzungskäufer", 0.50, 0.70, 0.50, 1.2,
        "Cross-Sell saisonal timen (Silofolie/Saatgut/PSM/Dünger-Aktion); außerhalb der Fenster nicht überbearbeiten.",
    ),
    BuyingGroup.STRATEGISCHER_STAMMKUNDE: GruppenProfil(
        "Strategischer Stammkunde", 0.85, 0.95, 0.85, 0.6,
        "Halten, Servicequalität, rechtzeitige Angebote — nicht überbearbeiten, Abwanderung früh erkennen.",
    ),
    BuyingGroup.SCHLAFENDER_POTENZIALKUNDE: GruppenProfil(
        "Schlafender Potenzialkunde", 0.50, 0.75, 0.40, 1.4,
        "Ersteinstieg mit niedrigschwelligem Produkt oder konkretem Problem lösen; nicht mit 100-%-Ziel rechnen.",
    ),
    BuyingGroup.UNBEKANNT: GruppenProfil(
        "Noch nicht eingestuft", 0.65, 0.80, 0.50, 1.2,
        "Kaufmuster beobachten; Einordnung über Zeit verfeinern.",
    ),
}

# Produktgruppen-Modifikator auf den Zielanteil (Sättigung/Preisvergleich je Sparte).
# Standardware sättigt früh + wird stark verglichen → niedrigerer erreichbarer Anteil;
# beratungsintensive Gruppen → höher.
PRODUKTGRUPPEN_ZIEL_MOD: dict[str, float] = {
    "kraftfutter": -0.08,
    "duenger_marktfrucht": -0.10,
    "grundfutterbau": -0.05,
    "stallbedarf_hygiene": -0.05,
    "mineral_spezial": +0.05,
    "kaelber": +0.05,
    "pflanzenschutz": +0.04,
    "beratung_analyse": +0.05,
    "saatgut_marktfrucht": 0.0,
}

ZIEL_ANTEIL_MIN = 0.30
ZIEL_ANTEIL_MAX = 0.97
# Ab dieser Deckung beginnt der überproportionale Grenzaufwand (abnehmender Grenzertrag).
SAETTIGUNG_SCHWELLE = 0.70


def profil(group: BuyingGroup | str) -> GruppenProfil:
    if isinstance(group, str):
        try:
            group = BuyingGroup(group)
        except ValueError:
            group = BuyingGroup.UNBEKANNT
    return GRUPPEN.get(group, GRUPPEN[BuyingGroup.UNBEKANNT])


def ziel_anteil(group: BuyingGroup | str, produktgruppe_key: Optional[str] = None) -> float:
    """Realistischer Ziel-Share-of-Wallet (Mitte des Korridors) inkl. Produktgruppen-Modifikator."""
    p = profil(group)
    base = (p.ziel_anteil_min + p.ziel_anteil_max) / 2
    mod = PRODUKTGRUPPEN_ZIEL_MOD.get(produktgruppe_key or "", 0.0)
    return max(ZIEL_ANTEIL_MIN, min(ZIEL_ANTEIL_MAX, base + mod))


def grenzaufwand_faktor(group: BuyingGroup | str, deckung_pct: float) -> float:
    """Grenzaufwand steigt überproportional, je näher der Ist-Deckungsgrad an die
    Sättigung kommt (die letzten Prozentpunkte sind am teuersten/teils verteidigt)."""
    base = profil(group).grenzaufwand
    d = max(0.0, min(1.0, deckung_pct / 100.0))
    if d <= SAETTIGUNG_SCHWELLE:
        return base
    over = (d - SAETTIGUNG_SCHWELLE) / (1.0 - SAETTIGUNG_SCHWELLE)  # 0..1
    return base * (1.0 + over * 1.5)


@dataclass(frozen=True)
class LueckenBewertung:
    bedarf_eur: int
    ist_eur: int
    theoretische_luecke_eur: int
    ziel_anteil: float
    ziel_umsatz_eur: int
    realistische_luecke_eur: int
    geschuetzte_luecke_eur: int
    deckung_pct: int
    abschluss_faktor: float
    grenzaufwand: float
    prioritaet: float


def bewerte_luecke(
    bedarf_eur: float,
    ist_eur: float,
    group: BuyingGroup | str,
    produktgruppe_key: str,
    marge_faktor: float = 1.0,
) -> LueckenBewertung:
    """Bewertet eine Produktgruppen-Lücke realistisch (Käufergruppe + Sättigung)."""
    bedarf = max(0.0, bedarf_eur)
    ist = max(0.0, ist_eur)
    theo = max(0.0, bedarf - ist)
    za = ziel_anteil(group, produktgruppe_key)
    ziel_umsatz = bedarf * za
    realistisch = max(0.0, ziel_umsatz - ist)
    geschuetzt = max(0.0, bedarf - ziel_umsatz)
    deckung = (ist / bedarf * 100.0) if bedarf > 0 else 0.0
    p = profil(group)
    aufwand = grenzaufwand_faktor(group, deckung)
    prioritaet = (realistisch * marge_faktor * p.abschluss_faktor / aufwand) if aufwand > 0 else 0.0
    return LueckenBewertung(
        bedarf_eur=round(bedarf), ist_eur=round(ist),
        theoretische_luecke_eur=round(theo),
        ziel_anteil=round(za, 3), ziel_umsatz_eur=round(ziel_umsatz),
        realistische_luecke_eur=round(realistisch),
        geschuetzte_luecke_eur=round(geschuetzt),
        deckung_pct=min(round(deckung), 100),
        abschluss_faktor=p.abschluss_faktor, grenzaufwand=round(aufwand, 2),
        prioritaet=round(prioritaet),
    )


# ── Regelbasierte Käufergruppen-Klassifikation ────────────────────────────────
@dataclass(frozen=True)
class Verhaltenssignale:
    """Beobachtbare Einkaufssignale (rollierend 12 M). In DEV modelliert, später
    aus echten Angebots-/Preisabfrage-/Belegdaten aggregiert."""
    angebote_12m: int = 0
    preisabfragen_12m: int = 0
    abschlussquote: float = 0.0       # 0..1
    rabatt_schnitt: float = 0.0       # 0..1
    kauffrequenz_12m: int = 0
    deckung_gesamt_pct: float = 0.0   # 0..100
    multi_lieferant_wahrsch: float = 0.5  # 0..1
    saison_konzentration: float = 0.0     # 0..1 (Anteil Umsatz in Saisonfenstern)
    bedarf_gesamt_eur: float = 0.0


@dataclass(frozen=True)
class Klassifikation:
    gruppe: BuyingGroup
    confidence: float   # 0..1
    begruendung: str


def klassifiziere(s: Verhaltenssignale) -> Klassifikation:
    """Regelbasierte Erstklassifikation aus beobachtbaren Signalen. Liefert immer
    eine Begründung (keine Blackbox). Reihenfolge = Spezifität (spezifisch zuerst)."""
    # Schlafender Potenzialkunde: hoher Bedarf, kaum Bezug, wenig Aktivität.
    if s.bedarf_gesamt_eur >= 20000 and s.deckung_gesamt_pct < 12 and s.angebote_12m <= 2:
        return Klassifikation(
            BuyingGroup.SCHLAFENDER_POTENZIALKUNDE, 0.7,
            f"Hoher Bedarf (~{round(s.bedarf_gesamt_eur):,} €) bei nur {round(s.deckung_gesamt_pct)} % Deckung und kaum Angebotsaktivität ({s.angebote_12m}).".replace(",", "."),
        )
    # Preisabfrager ohne Abschluss: viele Anfragen, niedrige Abschlussquote.
    if s.preisabfragen_12m >= 8 and s.abschlussquote < 0.30:
        return Klassifikation(
            BuyingGroup.PREISABFRAGER, 0.75,
            f"{s.preisabfragen_12m} Preisabfragen, aber nur {round(s.abschlussquote*100)} % Abschlussquote — nutzt uns vermutlich als Preisanker.",
        )
    # Preisverhandler mit Abschluss: viele Angebote, solide Abschlussquote, hoher Rabatt.
    if s.angebote_12m >= 6 and s.abschlussquote >= 0.45 and s.rabatt_schnitt >= 0.03:
        return Klassifikation(
            BuyingGroup.PREISVERHANDLER, 0.75,
            f"{s.angebote_12m} Angebote, {round(s.abschlussquote*100)} % Abschluss, Ø Rabatt {round(s.rabatt_schnitt*100,1)} % — preissensibel, aber gewinnbar.",
        )
    # Strategischer Stammkunde: hohe Deckung, regelmäßig, wenig Rabatt.
    if s.deckung_gesamt_pct >= 75 and s.kauffrequenz_12m >= 10 and s.rabatt_schnitt < 0.04:
        return Klassifikation(
            BuyingGroup.STRATEGISCHER_STAMMKUNDE, 0.8,
            f"Hohe Deckung ({round(s.deckung_gesamt_pct)} %), {s.kauffrequenz_12m} Käufe/Jahr, geringer Rabatt — halten statt überbearbeiten.",
        )
    # Beziehungskäufer: regelmäßig, kaum Preisverhandlung, mittlere/hohe Deckung.
    if s.kauffrequenz_12m >= 8 and s.preisabfragen_12m <= 3 and s.deckung_gesamt_pct >= 50:
        return Klassifikation(
            BuyingGroup.BEZIEHUNGSKAEUFER, 0.7,
            f"{s.kauffrequenz_12m} regelmäßige Käufe bei nur {s.preisabfragen_12m} Preisabfragen — reagiert auf Betreuung/Verlässlichkeit.",
        )
    # Saisonaler Ergänzungskäufer: Umsatz stark in Saisonfenstern konzentriert.
    if s.saison_konzentration >= 0.6 and s.kauffrequenz_12m <= 6:
        return Klassifikation(
            BuyingGroup.SAISON_ERGAENZER, 0.65,
            f"{round(s.saison_konzentration*100)} % des Bezugs in Saisonfenstern, wenige Käufe — saisonal timen.",
        )
    # Risiko-Streuer: bewusst mehrere Lieferanten, mittlere Deckung, nie hoch.
    if s.multi_lieferant_wahrsch >= 0.6 and 25 <= s.deckung_gesamt_pct < 70:
        return Klassifikation(
            BuyingGroup.RISIKO_STREUER, 0.65,
            f"Hohe Mehrlieferanten-Wahrscheinlichkeit ({round(s.multi_lieferant_wahrsch*100)} %) bei {round(s.deckung_gesamt_pct)} % Deckung — Zielanteil begrenzen.",
        )
    # Opportunist: niedrige Abschlussquote + niedrige (aber vorhandene) Frequenz + Mehrlieferant.
    if s.abschlussquote < 0.4 and 1 <= s.kauffrequenz_12m <= 4 and s.multi_lieferant_wahrsch >= 0.5:
        return Klassifikation(
            BuyingGroup.OPPORTUNIST, 0.55,
            "Geringe Loyalität (niedrige Abschlussquote, wenige Käufe, Mehrlieferant) — nur bei passender Aktion.",
        )
    return Klassifikation(
        BuyingGroup.UNBEKANNT, 0.3,
        "Datenlage für eine klare Einordnung noch zu dünn — Kaufmuster weiter beobachten.",
    )
