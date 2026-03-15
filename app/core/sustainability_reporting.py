"""
Nachhaltigkeit / CO2-Reporting — Wave 38, Gap 046
ESG-Kennzahlen, CO2-Bilanz, Scope-1/2/3-Emissionen, Nachhaltigkeitsberichte.

Schichtregeln:
- Kein Import aus app/api/ oder app/infrastructure/
- Nur Stdlib + eigene Core-Module
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Any

# ---------------------------------------------------------------------------
# Enumerationen
# ---------------------------------------------------------------------------

class EmissionsScope(str, Enum):
    SCOPE_1 = "SCOPE_1"   # Direkte Emissionen (eigene Fahrzeuge, Heizung)
    SCOPE_2 = "SCOPE_2"   # Indirekte Energie (Strom, Fernwärme)
    SCOPE_3 = "SCOPE_3"   # Vorgelagerte/nachgelagerte Emissionen (Lieferkette)


class EmissionsKategorie(str, Enum):
    TRANSPORT_LKW = "TRANSPORT_LKW"
    TRANSPORT_BAHN = "TRANSPORT_BAHN"
    TRANSPORT_SCHIFF = "TRANSPORT_SCHIFF"
    ENERGIE_STROM = "ENERGIE_STROM"
    ENERGIE_WAERME = "ENERGIE_WAERME"
    LANDWIRTSCHAFT = "LANDWIRTSCHAFT"
    DUENGUNG = "DUENGUNG"
    PFLANZENSCHUTZ = "PFLANZENSCHUTZ"
    TROCKNUNG = "TROCKNUNG"
    VERWALTUNG = "VERWALTUNG"


class ESGBewertung(str, Enum):
    SEHR_GUT = "SEHR_GUT"     # >= 80 Punkte
    GUT = "GUT"               # 60–79
    AUSREICHEND = "AUSREICHEND"  # 40–59
    MANGELHAFT = "MANGELHAFT"    # < 40


class BerichtsTyp(str, Enum):
    JAHRLICH = "JAEHRLICH"
    QUARTAL = "QUARTAL"
    KAMPAGNE = "KAMPAGNE"
    AD_HOC = "AD_HOC"


class NachhaltigkeitsZiel(str, Enum):
    CO2_REDUKTION = "CO2_REDUKTION"
    ENERGIE_EFFIZIENZ = "ENERGIE_EFFIZIENZ"
    BIODIVERSITAET = "BIODIVERSITAET"
    WASSERVERBRAUCH = "WASSERVERBRAUCH"
    ABFALL_REDUKTION = "ABFALL_REDUKTION"
    LIEFERKETTEN_TRANSPARENZ = "LIEFERKETTEN_TRANSPARENZ"


# ---------------------------------------------------------------------------
# Emissionsfaktoren (kg CO2e pro Einheit)
# ---------------------------------------------------------------------------

# kg CO2e pro Tonnen-Kilometer
_EMISSIONSFAKTOR_TONNE_KM: dict[EmissionsKategorie, float] = {
    EmissionsKategorie.TRANSPORT_LKW: 0.062,    # DSLV-Faktor
    EmissionsKategorie.TRANSPORT_BAHN: 0.018,
    EmissionsKategorie.TRANSPORT_SCHIFF: 0.010,
}

# kg CO2e pro kWh
_EMISSIONSFAKTOR_KWH: dict[EmissionsKategorie, float] = {
    EmissionsKategorie.ENERGIE_STROM: 0.380,    # Bundesdurchschnitt 2026
    EmissionsKategorie.ENERGIE_WAERME: 0.210,
}

# kg CO2e pro Tonne Ware
_EMISSIONSFAKTOR_TONNE_WARE: dict[EmissionsKategorie, float] = {
    EmissionsKategorie.LANDWIRTSCHAFT: 180.0,   # Getreide-Durchschnitt
    EmissionsKategorie.DUENGUNG: 4.5,           # pro kg N-Äquivalent
    EmissionsKategorie.PFLANZENSCHUTZ: 12.0,
    EmissionsKategorie.TROCKNUNG: 8.5,          # pro % Feuchteabzug/t
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class EmissionsPosition:
    """Eine einzelne Emissionsposition."""
    positions_id: str
    scope: EmissionsScope
    kategorie: EmissionsKategorie
    menge: float          # Einheit abhängig von Kategorie
    einheit: str          # "t*km", "kWh", "t"
    co2e_kg: float        # berechnete CO2-Äquivalente
    beschreibung: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "positions_id": self.positions_id,
            "scope": self.scope.value,
            "kategorie": self.kategorie.value,
            "menge": round(self.menge, 4),
            "einheit": self.einheit,
            "co2e_kg": round(self.co2e_kg, 4),
            "co2e_t": round(self.co2e_kg / 1000, 6),
            "beschreibung": self.beschreibung,
        }


@dataclass
class CO2Bilanz:
    """Vollständige CO2-Bilanz für einen Betrieb/Zeitraum."""
    bilanz_id: str
    tenant_id: str
    zeitraum_von: date
    zeitraum_bis: date
    positionen: list[EmissionsPosition]
    bericht_typ: BerichtsTyp = BerichtsTyp.JAHRLICH

    @property
    def gesamt_co2e_kg(self) -> float:
        return sum(p.co2e_kg for p in self.positionen)

    @property
    def gesamt_co2e_t(self) -> float:
        return self.gesamt_co2e_kg / 1000.0

    @property
    def scope1_co2e_kg(self) -> float:
        return sum(p.co2e_kg for p in self.positionen if p.scope == EmissionsScope.SCOPE_1)

    @property
    def scope2_co2e_kg(self) -> float:
        return sum(p.co2e_kg for p in self.positionen if p.scope == EmissionsScope.SCOPE_2)

    @property
    def scope3_co2e_kg(self) -> float:
        return sum(p.co2e_kg for p in self.positionen if p.scope == EmissionsScope.SCOPE_3)

    def as_dict(self) -> dict[str, Any]:
        return {
            "bilanz_id": self.bilanz_id,
            "tenant_id": self.tenant_id,
            "zeitraum_von": self.zeitraum_von.isoformat(),
            "zeitraum_bis": self.zeitraum_bis.isoformat(),
            "bericht_typ": self.bericht_typ.value,
            "positionen_anzahl": len(self.positionen),
            "gesamt_co2e_kg": round(self.gesamt_co2e_kg, 2),
            "gesamt_co2e_t": round(self.gesamt_co2e_t, 4),
            "scope1_co2e_kg": round(self.scope1_co2e_kg, 2),
            "scope2_co2e_kg": round(self.scope2_co2e_kg, 2),
            "scope3_co2e_kg": round(self.scope3_co2e_kg, 2),
            "positionen": [p.as_dict() for p in self.positionen],
        }


@dataclass
class ESGKennzahl:
    """Eine einzelne ESG-Kennzahl mit Zielwert und Ist-Wert."""
    kennzahl_id: str
    ziel: NachhaltigkeitsZiel
    bezeichnung: str
    ist_wert: float
    ziel_wert: float
    einheit: str
    gewichtung: float = 1.0   # für ESG-Score-Berechnung

    @property
    def zielerreichung_pct(self) -> float:
        """Zielerreichungsgrad in Prozent (100 % = Ziel erreicht, niedriger = schlechter)."""
        if self.ziel_wert == 0:
            return 100.0 if self.ist_wert == 0 else 0.0
        # Für Reduktionsziele: niedrigerer Ist-Wert = besser
        return min(100.0, (self.ziel_wert / self.ist_wert) * 100.0) if self.ist_wert > 0 else 100.0

    def as_dict(self) -> dict[str, Any]:
        return {
            "kennzahl_id": self.kennzahl_id,
            "ziel": self.ziel.value,
            "bezeichnung": self.bezeichnung,
            "ist_wert": round(self.ist_wert, 4),
            "ziel_wert": round(self.ziel_wert, 4),
            "einheit": self.einheit,
            "gewichtung": self.gewichtung,
            "zielerreichung_pct": round(self.zielerreichung_pct, 2),
        }


@dataclass
class ESGBericht:
    """Vollständiger ESG-Bericht mit Score und Bewertung."""
    bericht_id: str
    tenant_id: str
    zeitraum_von: date
    zeitraum_bis: date
    kennzahlen: list[ESGKennzahl]
    co2_bilanz: CO2Bilanz | None = None
    hinweise: list[str] = field(default_factory=list)

    @property
    def esg_score(self) -> float:
        """Gewichteter ESG-Score [0–100]."""
        if not self.kennzahlen:
            return 0.0
        gesamt_gewicht = sum(k.gewichtung for k in self.kennzahlen)
        if gesamt_gewicht == 0:
            return 0.0
        return sum(k.zielerreichung_pct * k.gewichtung for k in self.kennzahlen) / gesamt_gewicht

    @property
    def bewertung(self) -> ESGBewertung:
        score = self.esg_score
        if score >= 80.0:
            return ESGBewertung.SEHR_GUT
        if score >= 60.0:
            return ESGBewertung.GUT
        if score >= 40.0:
            return ESGBewertung.AUSREICHEND
        return ESGBewertung.MANGELHAFT

    def as_dict(self) -> dict[str, Any]:
        return {
            "bericht_id": self.bericht_id,
            "tenant_id": self.tenant_id,
            "zeitraum_von": self.zeitraum_von.isoformat(),
            "zeitraum_bis": self.zeitraum_bis.isoformat(),
            "esg_score": round(self.esg_score, 2),
            "bewertung": self.bewertung.value,
            "kennzahlen_anzahl": len(self.kennzahlen),
            "kennzahlen": [k.as_dict() for k in self.kennzahlen],
            "co2_bilanz": self.co2_bilanz.as_dict() if self.co2_bilanz else None,
            "hinweise": self.hinweise,
        }


# ---------------------------------------------------------------------------
# Berechnungsfunktionen
# ---------------------------------------------------------------------------

def berechne_transport_co2e(
    positions_id: str,
    kategorie: EmissionsKategorie,
    menge_t: float,
    distanz_km: float,
    scope: EmissionsScope = EmissionsScope.SCOPE_3,
) -> EmissionsPosition:
    """
    Berechnet CO2e für eine Transportposition.

    co2e_kg = menge_t * distanz_km * emissionsfaktor [kg CO2e / (t*km)]
    """
    if menge_t <= 0 or math.isnan(menge_t) or math.isinf(menge_t):
        raise ValueError("menge_t muss positiv und endlich sein")
    if distanz_km <= 0 or math.isnan(distanz_km) or math.isinf(distanz_km):
        raise ValueError("distanz_km muss positiv und endlich sein")
    if kategorie not in _EMISSIONSFAKTOR_TONNE_KM:
        raise ValueError(f"Kein Transportfaktor für {kategorie}")

    faktor = _EMISSIONSFAKTOR_TONNE_KM[kategorie]
    co2e = menge_t * distanz_km * faktor

    return EmissionsPosition(
        positions_id=positions_id,
        scope=scope,
        kategorie=kategorie,
        menge=menge_t * distanz_km,
        einheit="t*km",
        co2e_kg=co2e,
    )


def berechne_energie_co2e(
    positions_id: str,
    kategorie: EmissionsKategorie,
    kwh: float,
    scope: EmissionsScope = EmissionsScope.SCOPE_2,
) -> EmissionsPosition:
    """Berechnet CO2e für eine Energieposition (Strom/Wärme)."""
    if kwh <= 0 or math.isnan(kwh) or math.isinf(kwh):
        raise ValueError("kwh muss positiv und endlich sein")
    if kategorie not in _EMISSIONSFAKTOR_KWH:
        raise ValueError(f"Kein Energiefaktor für {kategorie}")

    faktor = _EMISSIONSFAKTOR_KWH[kategorie]
    co2e = kwh * faktor

    return EmissionsPosition(
        positions_id=positions_id,
        scope=scope,
        kategorie=kategorie,
        menge=kwh,
        einheit="kWh",
        co2e_kg=co2e,
    )


def erstelle_beispiel_co2_bilanz(
    tenant_id: str = "TENANT-001",
    jahr: int = 2026,
) -> CO2Bilanz:
    """Erstellt eine Beispiel-CO2-Bilanz für Demo und Tests."""
    positionen = [
        EmissionsPosition("P-001", EmissionsScope.SCOPE_1, EmissionsKategorie.TRANSPORT_LKW,
                          125_000.0, "t*km", 125_000 * 0.062, "Eigene LKW-Flotte"),
        EmissionsPosition("P-002", EmissionsScope.SCOPE_2, EmissionsKategorie.ENERGIE_STROM,
                          480_000.0, "kWh", 480_000 * 0.380, "Stromverbrauch Standorte"),
        EmissionsPosition("P-003", EmissionsScope.SCOPE_2, EmissionsKategorie.ENERGIE_WAERME,
                          120_000.0, "kWh", 120_000 * 0.210, "Fernwärme Trocknung"),
        EmissionsPosition("P-004", EmissionsScope.SCOPE_3, EmissionsKategorie.LANDWIRTSCHAFT,
                          50_000.0, "t", 50_000 * 180.0, "Zugekauftes Getreide"),
        EmissionsPosition("P-005", EmissionsScope.SCOPE_3, EmissionsKategorie.TRANSPORT_LKW,
                          200_000.0, "t*km", 200_000 * 0.062, "Zulieferer-Transporte"),
    ]
    return CO2Bilanz(
        bilanz_id=f"CO2-{tenant_id}-{jahr}",
        tenant_id=tenant_id,
        zeitraum_von=date(jahr, 1, 1),
        zeitraum_bis=date(jahr, 12, 31),
        positionen=positionen,
    )


def erstelle_beispiel_esg_bericht(
    tenant_id: str = "TENANT-001",
    jahr: int = 2026,
) -> ESGBericht:
    """Erstellt einen Beispiel-ESG-Bericht für Demo und Tests."""
    bilanz = erstelle_beispiel_co2_bilanz(tenant_id, jahr)
    kennzahlen = [
        ESGKennzahl("KZ-001", NachhaltigkeitsZiel.CO2_REDUKTION,
                    "CO2e-Gesamtemissionen", bilanz.gesamt_co2e_t, 9_200.0, "t CO2e", 2.0),
        ESGKennzahl("KZ-002", NachhaltigkeitsZiel.ENERGIE_EFFIZIENZ,
                    "Stromverbrauch je Tonne Durchsatz", 9.6, 8.0, "kWh/t", 1.5),
        ESGKennzahl("KZ-003", NachhaltigkeitsZiel.WASSERVERBRAUCH,
                    "Wasserverbrauch Standorte", 4_200.0, 4_000.0, "m³", 1.0),
        ESGKennzahl("KZ-004", NachhaltigkeitsZiel.ABFALL_REDUKTION,
                    "Restabfallquote", 3.2, 2.5, "%", 1.0),
        ESGKennzahl("KZ-005", NachhaltigkeitsZiel.LIEFERKETTEN_TRANSPARENZ,
                    "Lieferanten mit Nachhaltigkeitsaudit", 68.0, 80.0, "%", 1.5),
    ]
    return ESGBericht(
        bericht_id=f"ESG-{tenant_id}-{jahr}",
        tenant_id=tenant_id,
        zeitraum_von=date(jahr, 1, 1),
        zeitraum_bis=date(jahr, 12, 31),
        kennzahlen=kennzahlen,
        co2_bilanz=bilanz,
        hinweise=[
            "Scope-3-Daten basieren auf Einkaufsmengen, nicht auf gemessenen Werten.",
            "Zielwerte gemäß internem Nachhaltigkeitspfad 2025–2030.",
        ],
    )
