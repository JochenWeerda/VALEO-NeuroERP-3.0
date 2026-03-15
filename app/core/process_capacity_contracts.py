"""
Process Capacity Contracts — Wave 41
Workload- und Kapazitätsmodell für Process-Kernel-Workflows:
Ressourceneinheiten, Auslastungsgrade, Engpass-Erkennung und
Workflow-Kapazitätsprüfung.

Schichtregeln:
- Kein Import aus app/api/ oder app/infrastructure/
- Nur Stdlib + eigene Core-Module
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


# ---------------------------------------------------------------------------
# Enumerationen
# ---------------------------------------------------------------------------

class KapazitaetsTyp(str, Enum):
    ROLLE = "ROLLE"              # Menschliche Rolle (Sachbearbeiter, Leiter …)
    WORKSTATION = "WORKSTATION"  # Physischer Arbeitsplatz / Terminal
    SYSTEM = "SYSTEM"            # Systemressource (OCR, EDI-Hub …)
    QUEUE = "QUEUE"              # Verarbeitungs-Warteschlange


class AuslastungsStatus(str, Enum):
    UNTERAUSGELASTET = "UNTERAUSGELASTET"  # < 30 %
    NORMAL = "NORMAL"                      # 30 – 75 %
    AUSGELASTET = "AUSGELASTET"            # 75 – 90 %
    UEBERLASTET = "UEBERLASTET"            # > 90 %


class EngpassStufe(str, Enum):
    KEIN = "KEIN"          # < 75 %
    GERING = "GERING"      # 75 – 85 %
    MODERAT = "MODERAT"    # 85 – 95 %
    KRITISCH = "KRITISCH"  # >= 95 %


# ---------------------------------------------------------------------------
# Kapazitätseinheit
# ---------------------------------------------------------------------------

@dataclass
class KapazitaetsEinheit:
    """Eine einzelne Ressourceneinheit mit Kapazitätsangaben."""
    einheit_id: str
    ressource_name: str
    kapazitaets_typ: KapazitaetsTyp
    kapazitaet_max: float        # Maximale Kapazität (Einheiten/h, Slots …)
    kapazitaet_aktuell: float    # Aktuell belegte Kapazität
    tenant_id: str
    domain: str = ""             # "" = domainübergreifend

    @property
    def auslastung_pct(self) -> float:
        """Auslastung in Prozent (0 – 100+)."""
        if self.kapazitaet_max <= 0:
            return 0.0
        return round(self.kapazitaet_aktuell / self.kapazitaet_max * 100, 2)

    @property
    def auslastungs_status(self) -> AuslastungsStatus:
        pct = self.auslastung_pct
        if pct > 90:
            return AuslastungsStatus.UEBERLASTET
        if pct > 75:
            return AuslastungsStatus.AUSGELASTET
        if pct >= 30:
            return AuslastungsStatus.NORMAL
        return AuslastungsStatus.UNTERAUSGELASTET

    @property
    def ist_engpass(self) -> bool:
        return self.auslastung_pct >= 90

    def as_dict(self) -> dict[str, Any]:
        return {
            "einheit_id": self.einheit_id,
            "ressource_name": self.ressource_name,
            "kapazitaets_typ": self.kapazitaets_typ.value,
            "kapazitaet_max": self.kapazitaet_max,
            "kapazitaet_aktuell": self.kapazitaet_aktuell,
            "auslastung_pct": self.auslastung_pct,
            "auslastungs_status": self.auslastungs_status.value,
            "ist_engpass": self.ist_engpass,
            "tenant_id": self.tenant_id,
            "domain": self.domain,
        }


# ---------------------------------------------------------------------------
# Workload-Prognose
# ---------------------------------------------------------------------------

@dataclass
class WorkloadPrognose:
    """Geplante Aufgaben vs. verfügbare Kapazität in einem Zeitfenster."""
    prognose_id: str
    ressource_id: str
    zeitfenster_stunden: float   # Betrachteter Zeitraum in Stunden
    geplante_aufgaben: float     # Anforderungen im Zeitfenster
    verfuegbare_kapazitaet: float

    @property
    def deckungsgrad_pct(self) -> float:
        """Anteil der Aufgaben, der durch verfügbare Kapazität gedeckt wird (max 100)."""
        if self.geplante_aufgaben <= 0:
            return 100.0
        return round(
            min(100.0, self.verfuegbare_kapazitaet / self.geplante_aufgaben * 100), 2
        )

    @property
    def engpass_stufe(self) -> EngpassStufe:
        return berechne_engpass_stufe(100 - self.deckungsgrad_pct + 50)
        # Vereinfacht: hoher Undeckungsgrad → höhere Engpass-Stufe

    def as_dict(self) -> dict[str, Any]:
        return {
            "prognose_id": self.prognose_id,
            "ressource_id": self.ressource_id,
            "zeitfenster_stunden": self.zeitfenster_stunden,
            "geplante_aufgaben": self.geplante_aufgaben,
            "verfuegbare_kapazitaet": self.verfuegbare_kapazitaet,
            "deckungsgrad_pct": self.deckungsgrad_pct,
            "engpass_stufe": self.engpass_stufe.value,
        }


# ---------------------------------------------------------------------------
# Kapazitätsprüfungs-Ergebnis
# ---------------------------------------------------------------------------

@dataclass
class KapazitaetsPruefungErgebnis:
    """Ergebnis der Kapazitätsprüfung für einen Workflow-Start."""
    workflow_instanz_id: str
    geprueft_am: datetime
    kann_gestartet_werden: bool
    engpaesse: list[str] = field(default_factory=list)   # einheit_ids mit Engpass
    empfehlungen: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "workflow_instanz_id": self.workflow_instanz_id,
            "geprueft_am": self.geprueft_am.isoformat(),
            "kann_gestartet_werden": self.kann_gestartet_werden,
            "engpaesse": self.engpaesse,
            "empfehlung_anzahl": len(self.empfehlungen),
            "empfehlungen": self.empfehlungen,
        }


# ---------------------------------------------------------------------------
# Logik
# ---------------------------------------------------------------------------

def berechne_engpass_stufe(auslastung_pct: float) -> EngpassStufe:
    """Ermittelt die Engpass-Stufe aus der Auslastung in Prozent."""
    if auslastung_pct >= 95:
        return EngpassStufe.KRITISCH
    if auslastung_pct >= 85:
        return EngpassStufe.MODERAT
    if auslastung_pct >= 75:
        return EngpassStufe.GERING
    return EngpassStufe.KEIN


def pruefe_workflow_kapazitaet(
    workflow_instanz_id: str,
    domain: str,
    verfuegbare_einheiten: list[KapazitaetsEinheit],
    zeitstempel: datetime | None = None,
) -> KapazitaetsPruefungErgebnis:
    """
    Prüft ob für eine Workflow-Instanz ausreichend Kapazität vorhanden ist.

    Logik:
    - Einheiten der Domain (oder domainübergreifend) werden betrachtet
    - UEBERLASTET-Einheit → Engpass, kann_gestartet_werden = False
    - Empfehlungen werden aus Engpass-Anzahl abgeleitet
    """
    if zeitstempel is None:
        zeitstempel = datetime.utcnow()

    relevante = [
        e for e in verfuegbare_einheiten
        if e.domain == domain or e.domain == ""
    ]

    engpaesse = [e.einheit_id for e in relevante if e.ist_engpass]
    kann_starten = len(engpaesse) == 0

    empfehlungen: list[str] = []
    if not kann_starten:
        if len(engpaesse) == 1:
            empfehlungen.append(
                f"Ressource {engpaesse[0]} ist überlastet — Workflow verzögert starten."
            )
        else:
            empfehlungen.append(
                f"{len(engpaesse)} Ressourcen überlastet — Workload-Umverteilung prüfen."
            )
        empfehlungen.append("Alternative Zeitfenster oder Delegation erwägen.")

    return KapazitaetsPruefungErgebnis(
        workflow_instanz_id=workflow_instanz_id,
        geprueft_am=zeitstempel,
        kann_gestartet_werden=kann_starten,
        engpaesse=engpaesse,
        empfehlungen=empfehlungen,
    )


# ---------------------------------------------------------------------------
# Standarddaten
# ---------------------------------------------------------------------------

def get_default_kapazitaets_einheiten(
    tenant_id: str = "TENANT-001",
) -> list[KapazitaetsEinheit]:
    """Gibt 6 Standard-Kapazitätseinheiten zurück."""
    return [
        KapazitaetsEinheit(
            "KE-001", "Sachbearbeiter Agrar",
            KapazitaetsTyp.ROLLE, kapazitaet_max=8.0, kapazitaet_aktuell=5.5,
            tenant_id=tenant_id, domain="agrar",
        ),
        KapazitaetsEinheit(
            "KE-002", "Abteilungsleiter Annahme",
            KapazitaetsTyp.ROLLE, kapazitaet_max=4.0, kapazitaet_aktuell=3.8,
            tenant_id=tenant_id, domain="agrar",
        ),
        KapazitaetsEinheit(
            "KE-003", "OCR-Verarbeitungs-System",
            KapazitaetsTyp.SYSTEM, kapazitaet_max=100.0, kapazitaet_aktuell=42.0,
            tenant_id=tenant_id, domain="dms",
        ),
        KapazitaetsEinheit(
            "KE-004", "Zahlungslauf-Queue",
            KapazitaetsTyp.QUEUE, kapazitaet_max=500.0, kapazitaet_aktuell=470.0,
            tenant_id=tenant_id, domain="finance",
        ),
        KapazitaetsEinheit(
            "KE-005", "Compliance-Analyst",
            KapazitaetsTyp.ROLLE, kapazitaet_max=6.0, kapazitaet_aktuell=2.0,
            tenant_id=tenant_id, domain="compliance",
        ),
        KapazitaetsEinheit(
            "KE-006", "AP-Approval-Queue",
            KapazitaetsTyp.QUEUE, kapazitaet_max=200.0, kapazitaet_aktuell=198.0,
            tenant_id=tenant_id, domain="finance",
        ),
    ]
