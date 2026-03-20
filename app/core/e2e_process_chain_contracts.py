"""
e2e_process_chain_contracts.py — E2E Prozesskette ohne Medienbruch (Wave 85, Gap 001)

Modelliert die vollständige Kette Kontrakt → Annahme → Qualität → Settlement
und erkennt Medienbrüche (manuelle Nebenlisten, fehlende Übergaben).

Gap 001: ≥95% Vorgänge ohne manuelle Nebenliste
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
    KONTRAKT    = "KONTRAKT"    # Handelskontrakt mit Preislogik
    ANNAHME     = "ANNAHME"     # Warenannahme / Wiegeschein
    QUALITAET   = "QUALITAET"   # Qualitätsprüfung / Laborwerte
    SETTLEMENT  = "SETTLEMENT"  # Abrechnung / Gutschrift


class GliedStatus(str, Enum):
    """Status eines Kettenglieds."""
    AUSSTEHEND  = "AUSSTEHEND"  # Noch nicht gestartet
    AKTIV       = "AKTIV"       # In Bearbeitung
    ABGESCHLOSSEN = "ABGESCHLOSSEN"
    FEHLGESCHLAGEN = "FEHLGESCHLAGEN"
    UEBERSPRUNGEN = "UEBERSPRUNGEN"  # Medienbruch: manuell außerhalb erfasst


class MedienbruchTyp(str, Enum):
    """Art des Medienbruchs."""
    MANUELLE_NEBENLISTE  = "MANUELLE_NEBENLISTE"   # Excel/Paper außerhalb System
    FEHLENDE_UEBERGABE   = "FEHLENDE_UEBERGABE"    # Kein automatischer Trigger
    DATEN_INKONSISTENZ   = "DATEN_INKONSISTENZ"    # IDs stimmen nicht überein
    ZEITLICHER_BRUCH     = "ZEITLICHER_BRUCH"      # Zu lange Lücke zwischen Gliedern


class KettenStatus(str, Enum):
    """Gesamtstatus der E2E-Kette."""
    VOLLSTAENDIG   = "VOLLSTAENDIG"   # Alle Glieder abgeschlossen, kein Bruch
    TEILWEISE      = "TEILWEISE"      # Kette läuft, noch nicht vollständig
    UNTERBROCHEN   = "UNTERBROCHEN"   # Medienbruch erkannt
    FEHLERHAFT     = "FEHLERHAFT"     # Kritischer Fehler in Kette


# ---------------------------------------------------------------------------
# Prozessketten-Glied
# ---------------------------------------------------------------------------

@dataclass
class ProzessGlied:
    """
    Ein einzelnes Glied der E2E-Prozesskette.

    Jedes Glied hat eine Referenz auf das vorherige (parent_referenz_id)
    — fehlt diese bei ANNAHME/QUALITAET/SETTLEMENT, ist es ein Medienbruch.
    """
    glied_id: str
    typ: ProzessGliedTyp
    tenant_id: str
    referenz_id: str            # z.B. Kontrakt-Nr, Annahme-Nr, etc.
    parent_referenz_id: str     # Referenz auf vorheriges Glied — "" = Medienbruch-Risiko
    status: GliedStatus
    zeitstempel: str            # ISO-Timestamp
    metadaten: dict[str, Any] = field(default_factory=dict)

    @property
    def hat_eltern_referenz(self) -> bool:
        """True wenn das Glied auf ein vorheriges Glied verweist."""
        return bool(self.parent_referenz_id)

    @property
    def ist_abgeschlossen(self) -> bool:
        return self.status == GliedStatus.ABGESCHLOSSEN

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
            "ist_abgeschlossen": self.ist_abgeschlossen,
        }


# ---------------------------------------------------------------------------
# Medienbruch-Befund
# ---------------------------------------------------------------------------

@dataclass
class MedienbruchBefund:
    """Ein erkannter Medienbruch in der Prozesskette."""
    bruch_typ: MedienbruchTyp
    betroffenes_glied: ProzessGliedTyp
    beschreibung: str
    schwere: str = "HOCH"       # "HOCH" | "MITTEL" | "NIEDRIG"
    empfehlung: str = ""

    def as_dict(self) -> dict:
        return {
            "bruch_typ": self.bruch_typ.value,
            "betroffenes_glied": self.betroffenes_glied.value,
            "beschreibung": self.beschreibung,
            "schwere": self.schwere,
            "empfehlung": self.empfehlung,
        }


# ---------------------------------------------------------------------------
# E2E Prozesskette
# ---------------------------------------------------------------------------

@dataclass
class E2EProzesskette:
    """
    Vollständige E2E-Prozesskette für einen Landhandel-Vorgang.

    Reihenfolge: KONTRAKT → ANNAHME → QUALITAET → SETTLEMENT
    Jedes Glied muss auf das vorherige verweisen (parent_referenz_id).
    """
    ketten_id: str
    tenant_id: str
    glieder: list[ProzessGlied] = field(default_factory=list)

    _ERWARTETE_REIHENFOLGE: list[ProzessGliedTyp] = field(
        default_factory=lambda: [
            ProzessGliedTyp.KONTRAKT,
            ProzessGliedTyp.ANNAHME,
            ProzessGliedTyp.QUALITAET,
            ProzessGliedTyp.SETTLEMENT,
        ],
        repr=False,
    )

    def get_glied(self, typ: ProzessGliedTyp) -> ProzessGlied | None:
        return next((g for g in self.glieder if g.typ == typ), None)

    @property
    def vorhandene_typen(self) -> list[ProzessGliedTyp]:
        return [g.typ for g in self.glieder]

    @property
    def abgeschlossene_glieder(self) -> int:
        return sum(1 for g in self.glieder if g.ist_abgeschlossen)

    @property
    def fortschritt_pct(self) -> float:
        """Anteil abgeschlossener Pflicht-Glieder (0–100)."""
        gesamt = len(self._ERWARTETE_REIHENFOLGE)
        vorhanden = sum(
            1 for typ in self._ERWARTETE_REIHENFOLGE
            if self.get_glied(typ) is not None
        )
        return round(vorhanden / gesamt * 100, 1)

    @property
    def ist_vollstaendig(self) -> bool:
        """Alle 4 Pflicht-Glieder vorhanden und abgeschlossen."""
        return all(
            (g := self.get_glied(typ)) is not None and g.ist_abgeschlossen
            for typ in self._ERWARTETE_REIHENFOLGE
        )

    def as_dict(self) -> dict:
        return {
            "ketten_id": self.ketten_id,
            "tenant_id": self.tenant_id,
            "glieder": [g.as_dict() for g in self.glieder],
            "abgeschlossene_glieder": self.abgeschlossene_glieder,
            "fortschritt_pct": self.fortschritt_pct,
            "ist_vollstaendig": self.ist_vollstaendig,
        }


# ---------------------------------------------------------------------------
# Kettenvalidierung
# ---------------------------------------------------------------------------

@dataclass
class KettenValidierungsResult:
    """Ergebnis der Medienbruch-Prüfung für eine E2E-Kette."""
    ketten_id: str
    status: KettenStatus
    medienbrueche: list[MedienbruchBefund] = field(default_factory=list)
    warnungen: list[str] = field(default_factory=list)

    @property
    def hat_medienbruch(self) -> bool:
        return len(self.medienbrueche) > 0

    @property
    def kpi_erfuellt(self) -> bool:
        """KPI: kein Medienbruch (Vorgang ohne manuelle Nebenliste)."""
        return not self.hat_medienbruch

    def as_dict(self) -> dict:
        return {
            "ketten_id": self.ketten_id,
            "status": self.status.value,
            "hat_medienbruch": self.hat_medienbruch,
            "kpi_erfuellt": self.kpi_erfuellt,
            "medienbrueche": [b.as_dict() for b in self.medienbrueche],
            "warnungen": self.warnungen,
        }


def validate_e2e_kette(kette: E2EProzesskette) -> KettenValidierungsResult:
    """
    Prüft eine E2E-Prozesskette auf Medienbrüche.

    Regeln:
    1. ANNAHME muss auf KONTRAKT verweisen (parent_referenz_id)
    2. QUALITAET muss auf ANNAHME verweisen
    3. SETTLEMENT muss auf QUALITAET verweisen
    4. Übersprungene Glieder (UEBERSPRUNGEN) → Medienbruch
    """
    brueche: list[MedienbruchBefund] = []
    warnungen: list[str] = []

    typen = [ProzessGliedTyp.KONTRAKT, ProzessGliedTyp.ANNAHME,
             ProzessGliedTyp.QUALITAET, ProzessGliedTyp.SETTLEMENT]

    for i, typ in enumerate(typen):
        glied = kette.get_glied(typ)

        if glied is None:
            if typ in (ProzessGliedTyp.SETTLEMENT,):
                warnungen.append(f"{typ.value} noch nicht vorhanden — Kette unvollständig")
            continue

        # Übersprungene Glieder = Medienbruch
        if glied.status == GliedStatus.UEBERSPRUNGEN:
            brueche.append(MedienbruchBefund(
                bruch_typ=MedienbruchTyp.MANUELLE_NEBENLISTE,
                betroffenes_glied=typ,
                beschreibung=f"{typ.value} wurde außerhalb des Systems erfasst",
                empfehlung=f"{typ.value} direkt im System anlegen statt manuelle Nebenliste",
            ))

        # Fehlende Elternreferenz (außer bei KONTRAKT, das ist der Anfang)
        if i > 0 and glied.status != GliedStatus.UEBERSPRUNGEN:
            if not glied.hat_eltern_referenz:
                brueche.append(MedienbruchBefund(
                    bruch_typ=MedienbruchTyp.FEHLENDE_UEBERGABE,
                    betroffenes_glied=typ,
                    beschreibung=(
                        f"{typ.value} hat keine Referenz auf {typen[i-1].value} — "
                        f"automatische Übergabe fehlt"
                    ),
                    empfehlung=f"Event-Trigger von {typen[i-1].value} nach {typ.value} einrichten",
                ))

    if brueche:
        status = KettenStatus.UNTERBROCHEN
    elif kette.ist_vollstaendig:
        status = KettenStatus.VOLLSTAENDIG
    else:
        status = KettenStatus.TEILWEISE

    return KettenValidierungsResult(
        ketten_id=kette.ketten_id,
        status=status,
        medienbrueche=brueche,
        warnungen=warnungen,
    )


# ---------------------------------------------------------------------------
# KPI-Aggregation über mehrere Ketten
# ---------------------------------------------------------------------------

@dataclass
class E2EKettenKpiReport:
    """
    Aggregierter KPI-Report über alle E2E-Ketten eines Tenants.

    KPI: ≥95% Vorgänge ohne manuelle Nebenliste.
    """
    tenant_id: str
    gesamt_ketten: int
    ketten_ohne_bruch: int
    ketten_mit_bruch: int

    @property
    def kpi_pct(self) -> float:
        if self.gesamt_ketten == 0:
            return 100.0
        return round(self.ketten_ohne_bruch / self.gesamt_ketten * 100, 1)

    @property
    def kpi_erfuellt(self) -> bool:
        """KPI: ≥95% Vorgänge ohne Medienbruch."""
        return self.kpi_pct >= 95.0 and self.gesamt_ketten > 0

    def as_dict(self) -> dict:
        return {
            "tenant_id": self.tenant_id,
            "gesamt_ketten": self.gesamt_ketten,
            "ketten_ohne_bruch": self.ketten_ohne_bruch,
            "ketten_mit_bruch": self.ketten_mit_bruch,
            "kpi_pct": self.kpi_pct,
            "kpi_erfuellt": self.kpi_erfuellt,
        }


def evaluate_e2e_kpi(
    tenant_id: str,
    validierungen: list[KettenValidierungsResult],
) -> E2EKettenKpiReport:
    """Aggregiert Validierungsergebnisse zum KPI-Report."""
    ohne_bruch = sum(1 for v in validierungen if not v.hat_medienbruch)
    mit_bruch = sum(1 for v in validierungen if v.hat_medienbruch)
    return E2EKettenKpiReport(
        tenant_id=tenant_id,
        gesamt_ketten=len(validierungen),
        ketten_ohne_bruch=ohne_bruch,
        ketten_mit_bruch=mit_bruch,
    )
