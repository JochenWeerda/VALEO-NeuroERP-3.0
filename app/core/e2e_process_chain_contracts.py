"""
e2e_process_chain_contracts.py — E2E Prozessketten ohne Medienbruch (Wave 85, Gap 001)

KPI: ≥ 95% aller Prozessketten ohne Medienbruch durchlaufen
     KONTRAKT → ANNAHME → QUALITAET → SETTLEMENT ohne manuelle Nebenliste

Medienbruch-Typen:
    FEHLENDE_UEBERGABE   — parent_referenz_id fehlt zwischen Kettengliedern
    MANUELLE_NEBENLISTE  — Glied hat Status UEBERSPRUNGEN (manuelle Erfassung)
    STATUSSPRUNG         — Verbotene Statusübergänge (z.B. KONTRAKT → SETTLEMENT direkt)
    DUPLIKAT_REFERENZ    — Mehrere Glieder zeigen auf dieselbe parent_referenz_id
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class ProzessGliedTyp(str, Enum):
    """Typ eines Glieds in der E2E-Prozesskette."""
    KONTRAKT   = "KONTRAKT"    # Lieferkontrakt
    ANNAHME    = "ANNAHME"     # Wareneingang / Wiegeschein
    QUALITAET  = "QUALITAET"   # Qualitätsprüfung / Protokoll
    SETTLEMENT = "SETTLEMENT"  # Abrechnung / Selbstfaktura


class GliedStatus(str, Enum):
    """Verarbeitungsstatus eines Prozessketten-Glieds."""
    OFFEN        = "OFFEN"
    IN_BEARBEITUNG = "IN_BEARBEITUNG"
    ABGESCHLOSSEN = "ABGESCHLOSSEN"
    UEBERSPRUNGEN = "UEBERSPRUNGEN"   # Manuelle Eingabe — Medienbruch-Signal
    STORNIERT    = "STORNIERT"


class MedienbruchTyp(str, Enum):
    """Klassifikation eines erkannten Medienbruchs."""
    FEHLENDE_UEBERGABE  = "FEHLENDE_UEBERGABE"   # parent_referenz_id == ""
    MANUELLE_NEBENLISTE = "MANUELLE_NEBENLISTE"  # Status UEBERSPRUNGEN
    STATUSSPRUNG        = "STATUSSPRUNG"          # Unzulässige Typenfolge
    DUPLIKAT_REFERENZ   = "DUPLIKAT_REFERENZ"     # Mehrere Kinder an selber Referenz


# Erlaubte Reihenfolge der Glieder in der Kette
ERLAUBTE_REIHENFOLGE: list[ProzessGliedTyp] = [
    ProzessGliedTyp.KONTRAKT,
    ProzessGliedTyp.ANNAHME,
    ProzessGliedTyp.QUALITAET,
    ProzessGliedTyp.SETTLEMENT,
]


# ---------------------------------------------------------------------------
# Datenhaltung
# ---------------------------------------------------------------------------

@dataclass
class ProzessGlied:
    """Ein Glied in der E2E-Prozesskette."""
    glied_id: str
    typ: ProzessGliedTyp
    tenant_id: str
    referenz_id: str          # Eigene Dokument-ID
    parent_referenz_id: str   # Referenz auf Vorgänger ("" = kein Vorgänger)
    status: GliedStatus
    zeitstempel: str          # ISO-8601

    @property
    def hat_eltern_referenz(self) -> bool:
        """True wenn eine Vorgänger-Referenz vorhanden ist."""
        return bool(self.parent_referenz_id)

    @property
    def ist_uebersprungen(self) -> bool:
        """True wenn das Glied manuell ohne digitale Übergabe erfasst wurde."""
        return self.status == GliedStatus.UEBERSPRUNGEN

    def as_dict(self) -> dict:
        return {
            "glied_id": self.glied_id,
            "typ": self.typ.value,
            "tenant_id": self.tenant_id,
            "referenz_id": self.referenz_id,
            "parent_referenz_id": self.parent_referenz_id,
            "status": self.status.value,
            "zeitstempel": self.zeitstempel,
            "hat_eltern_referenz": self.hat_eltern_referenz,
        }


@dataclass
class E2EProzesskette:
    """Eine vollständige E2E-Prozesskette von Kontrakt bis Settlement."""
    kette_id: str
    tenant_id: str
    glieder: list[ProzessGlied] = field(default_factory=list)
    metadaten: dict[str, Any] = field(default_factory=dict)

    @property
    def ist_vollstaendig(self) -> bool:
        """True wenn alle 4 Kettentypen vorhanden sind."""
        vorhandene_typen = {g.typ for g in self.glieder}
        return all(t in vorhandene_typen for t in ERLAUBTE_REIHENFOLGE)

    @property
    def typen_in_kette(self) -> list[ProzessGliedTyp]:
        return [g.typ for g in self.glieder]

    def get_glied(self, typ: ProzessGliedTyp) -> ProzessGlied | None:
        return next((g for g in self.glieder if g.typ == typ), None)

    def as_dict(self) -> dict:
        return {
            "kette_id": self.kette_id,
            "tenant_id": self.tenant_id,
            "ist_vollstaendig": self.ist_vollstaendig,
            "typen_in_kette": [t.value for t in self.typen_in_kette],
            "glieder": [g.as_dict() for g in self.glieder],
        }


# ---------------------------------------------------------------------------
# Medienbruch-Befund
# ---------------------------------------------------------------------------

@dataclass
class MedienbruchBefund:
    """Ein erkannter Medienbruch in einer Prozesskette."""
    kette_id: str
    glied_id: str
    typ: MedienbruchTyp
    beschreibung: str
    schweregrad: str = "HOCH"   # HOCH | MITTEL | NIEDRIG

    def as_dict(self) -> dict:
        return {
            "kette_id": self.kette_id,
            "glied_id": self.glied_id,
            "typ": self.typ.value,
            "beschreibung": self.beschreibung,
            "schweregrad": self.schweregrad,
        }


# ---------------------------------------------------------------------------
# Validierungsergebnis
# ---------------------------------------------------------------------------

@dataclass
class KettenValidierungsResult:
    """Ergebnis der Validierung einer einzelnen Prozesskette."""
    kette_id: str
    hat_medienbruch: bool
    befunde: list[MedienbruchBefund] = field(default_factory=list)

    @property
    def anzahl_brueche(self) -> int:
        return len(self.befunde)

    def as_dict(self) -> dict:
        return {
            "kette_id": self.kette_id,
            "hat_medienbruch": self.hat_medienbruch,
            "anzahl_brueche": self.anzahl_brueche,
            "befunde": [b.as_dict() for b in self.befunde],
        }


# ---------------------------------------------------------------------------
# Validierungslogik
# ---------------------------------------------------------------------------

def validate_e2e_kette(kette: E2EProzesskette) -> KettenValidierungsResult:
    """
    Prüft eine E2E-Prozesskette auf Medienbrüche.

    Erkannte Brüche:
    - UEBERSPRUNGEN-Status → MANUELLE_NEBENLISTE
    - parent_referenz_id fehlt (nicht bei KONTRAKT) → FEHLENDE_UEBERGABE
    """
    befunde: list[MedienbruchBefund] = []

    for glied in kette.glieder:
        # Manuelle Nebenliste: Glied wurde übersprungen
        if glied.ist_uebersprungen:
            befunde.append(MedienbruchBefund(
                kette_id=kette.kette_id,
                glied_id=glied.glied_id,
                typ=MedienbruchTyp.MANUELLE_NEBENLISTE,
                beschreibung=(
                    f"{glied.typ.value} '{glied.referenz_id}' hat Status UEBERSPRUNGEN "
                    f"— manuelle Erfassung ohne digitale Übergabe"
                ),
                schweregrad="HOCH",
            ))

        # Fehlende Übergabe: Kein Vorgänger-Link (ausser bei Kontrakt, der startet die Kette)
        if glied.typ != ProzessGliedTyp.KONTRAKT and not glied.hat_eltern_referenz:
            befunde.append(MedienbruchBefund(
                kette_id=kette.kette_id,
                glied_id=glied.glied_id,
                typ=MedienbruchTyp.FEHLENDE_UEBERGABE,
                beschreibung=(
                    f"{glied.typ.value} '{glied.referenz_id}' hat keine parent_referenz_id "
                    f"— Übergang vom Vorgänger nicht maschinenlesbar verknüpft"
                ),
                schweregrad="HOCH",
            ))

    return KettenValidierungsResult(
        kette_id=kette.kette_id,
        hat_medienbruch=bool(befunde),
        befunde=befunde,
    )


# ---------------------------------------------------------------------------
# KPI-Report
# ---------------------------------------------------------------------------

@dataclass
class E2EKettenKpiReport:
    """KPI-Bericht für die E2E-Prozessketten eines Tenants."""
    tenant_id: str
    gesamt_ketten: int
    ketten_ohne_bruch: int
    ketten_mit_bruch: int
    kpi_pct: float                  # Anteil ohne Bruch in Prozent
    kpi_erfuellt: bool              # Gap 001 KPI: >= 95%
    kpi_ziel_pct: float = 95.0
    bruch_details: list[KettenValidierungsResult] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "tenant_id": self.tenant_id,
            "gesamt_ketten": self.gesamt_ketten,
            "ketten_ohne_bruch": self.ketten_ohne_bruch,
            "ketten_mit_bruch": self.ketten_mit_bruch,
            "kpi_pct": self.kpi_pct,
            "kpi_ziel_pct": self.kpi_ziel_pct,
            "kpi_erfuellt": self.kpi_erfuellt,
        }


def evaluate_e2e_kpi(
    tenant_id: str,
    validierungen: list[KettenValidierungsResult],
    kpi_ziel_pct: float = 95.0,
) -> E2EKettenKpiReport:
    """
    Berechnet den Gap 001 KPI aus den Validierungsergebnissen.

    KPI: Anteil der Prozessketten ohne Medienbruch >= 95%.
    """
    gesamt = len(validierungen)
    ohne_bruch = sum(1 for v in validierungen if not v.hat_medienbruch)
    mit_bruch = gesamt - ohne_bruch

    kpi_pct = round(ohne_bruch / gesamt * 100, 2) if gesamt > 0 else 0.0
    kpi_erfuellt = kpi_pct >= kpi_ziel_pct

    return E2EKettenKpiReport(
        tenant_id=tenant_id,
        gesamt_ketten=gesamt,
        ketten_ohne_bruch=ohne_bruch,
        ketten_mit_bruch=mit_bruch,
        kpi_pct=kpi_pct,
        kpi_erfuellt=kpi_erfuellt,
        kpi_ziel_pct=kpi_ziel_pct,
        bruch_details=[v for v in validierungen if v.hat_medienbruch],
    )
