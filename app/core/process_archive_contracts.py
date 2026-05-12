"""
Process Archive Contracts — Wave 50
GoBD-konforme Archivierung von Workflow-Instanzen:
Archivierungsregeln, Aufbewahrungsfristen und Abrufprotokolle.

Schichtregeln:
- Kein Import aus app/api/ oder app/infrastructure/
- Nur Stdlib + eigene Core-Module
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any


class ArchivierungsGrund(str, Enum):
    ABGESCHLOSSEN = "ABGESCHLOSSEN"
    GOBD_PFLICHT = "GOBD_PFLICHT"
    MANUELL = "MANUELL"
    INAKTIVITAET = "INAKTIVITAET"


class ArchivStatus(str, Enum):
    AKTIV = "AKTIV"           # Noch in Produktion
    ARCHIVIERT = "ARCHIVIERT"
    GESPERRT = "GESPERRT"     # Aufbewahrungspflicht läuft noch
    GELOESCHT = "GELOESCHT"   # Nach Ablauf der Aufbewahrungsfrist


class AufbewahrungsKlasse(str, Enum):
    KLASSE_A = "KLASSE_A"   # 10 Jahre (GoBD steuerrelevant)
    KLASSE_B = "KLASSE_B"   # 6 Jahre (GoBD handelsrechtlich)
    KLASSE_C = "KLASSE_C"   # 3 Jahre (operativ)
    KLASSE_D = "KLASSE_D"   # 1 Jahr (temporär)


# Aufbewahrungsfristen in Jahren
AUFBEWAHRUNGSFRISTEN: dict[AufbewahrungsKlasse, int] = {
    AufbewahrungsKlasse.KLASSE_A: 10,
    AufbewahrungsKlasse.KLASSE_B: 6,
    AufbewahrungsKlasse.KLASSE_C: 3,
    AufbewahrungsKlasse.KLASSE_D: 1,
}


@dataclass
class ArchivEintrag:
    """Archivierter Workflow-Instanz-Eintrag."""
    eintrag_id: str
    workflow_instanz_id: str
    tenant_id: str
    grund: ArchivierungsGrund
    status: ArchivStatus
    aufbewahrungsklasse: AufbewahrungsKlasse
    archiviert_am: datetime
    beschreibung: str = ""

    @property
    def aufbewahrungsfrist_jahre(self) -> int:
        return AUFBEWAHRUNGSFRISTEN[self.aufbewahrungsklasse]

    @property
    def loeschen_ab(self) -> datetime:
        """Frühester Löschzeitpunkt (Ende der Aufbewahrungsfrist)."""
        return self.archiviert_am.replace(
            year=self.archiviert_am.year + self.aufbewahrungsfrist_jahre
        )

    @property
    def ist_loeschbar(self) -> bool:
        """True wenn Aufbewahrungsfrist abgelaufen (status != GESPERRT)."""
        return (
            self.status != ArchivStatus.GESPERRT
            and datetime.utcnow() >= self.loeschen_ab
        )

    def ist_loeschbar_am(self, jetzt: datetime) -> bool:
        """Prüft Löschbarkeit zu einem bestimmten Zeitpunkt."""
        return (
            self.status != ArchivStatus.GESPERRT
            and jetzt >= self.loeschen_ab
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "eintrag_id": self.eintrag_id,
            "workflow_instanz_id": self.workflow_instanz_id,
            "tenant_id": self.tenant_id,
            "grund": self.grund.value,
            "status": self.status.value,
            "aufbewahrungsklasse": self.aufbewahrungsklasse.value,
            "aufbewahrungsfrist_jahre": self.aufbewahrungsfrist_jahre,
            "archiviert_am": self.archiviert_am.isoformat(),
            "loeschen_ab": self.loeschen_ab.isoformat(),
            "beschreibung": self.beschreibung,
        }


@dataclass
class ArchivStatistik:
    """Aggregierte Archivstatistik für einen Tenant."""
    tenant_id: str
    aktiv: int
    archiviert: int
    gesperrt: int
    geloescht: int

    @property
    def gesamt(self) -> int:
        return self.aktiv + self.archiviert + self.gesperrt + self.geloescht

    @property
    def archivierungsrate_pct(self) -> float:
        if self.gesamt == 0:
            return 0.0
        return round((self.archiviert + self.gesperrt + self.geloescht) / self.gesamt * 100, 2)

    def as_dict(self) -> dict[str, Any]:
        return {
            "tenant_id": self.tenant_id,
            "aktiv": self.aktiv,
            "archiviert": self.archiviert,
            "gesperrt": self.gesperrt,
            "geloescht": self.geloescht,
            "gesamt": self.gesamt,
            "archivierungsrate_pct": self.archivierungsrate_pct,
        }


def berechne_archiv_statistik(
    eintraege: list[ArchivEintrag],
    tenant_id: str,
) -> ArchivStatistik:
    """Aggregiert Archiv-Einträge für einen Tenant."""
    relevant = [e for e in eintraege if e.tenant_id == tenant_id]
    return ArchivStatistik(
        tenant_id=tenant_id,
        aktiv=sum(1 for e in relevant if e.status == ArchivStatus.AKTIV),
        archiviert=sum(1 for e in relevant if e.status == ArchivStatus.ARCHIVIERT),
        gesperrt=sum(1 for e in relevant if e.status == ArchivStatus.GESPERRT),
        geloescht=sum(1 for e in relevant if e.status == ArchivStatus.GELOESCHT),
    )


def get_default_archiv_eintraege(tenant_id: str = "TENANT-001") -> list[ArchivEintrag]:
    """Gibt 5 Standard-Archiv-Einträge zurück."""
    basis = datetime(2026, 1, 1, 0, 0)
    return [
        ArchivEintrag(
            eintrag_id="AE-001",
            workflow_instanz_id="WF-INST-1001",
            tenant_id=tenant_id,
            grund=ArchivierungsGrund.GOBD_PFLICHT,
            status=ArchivStatus.GESPERRT,
            aufbewahrungsklasse=AufbewahrungsKlasse.KLASSE_A,
            archiviert_am=basis,
            beschreibung="Jahreskontrakt 2025 — steuerrelevant 10 Jahre",
        ),
        ArchivEintrag(
            eintrag_id="AE-002",
            workflow_instanz_id="WF-INST-0987",
            tenant_id=tenant_id,
            grund=ArchivierungsGrund.ABGESCHLOSSEN,
            status=ArchivStatus.ARCHIVIERT,
            aufbewahrungsklasse=AufbewahrungsKlasse.KLASSE_B,
            archiviert_am=basis,
            beschreibung="Settlement Q4 2025 — handelsrechtlich 6 Jahre",
        ),
        ArchivEintrag(
            eintrag_id="AE-003",
            workflow_instanz_id="WF-INST-0850",
            tenant_id=tenant_id,
            grund=ArchivierungsGrund.INAKTIVITAET,
            status=ArchivStatus.ARCHIVIERT,
            aufbewahrungsklasse=AufbewahrungsKlasse.KLASSE_C,
            archiviert_am=basis,
            beschreibung="Operativer Vorgang — 3 Jahre Aufbewahrung",
        ),
        ArchivEintrag(
            eintrag_id="AE-004",
            workflow_instanz_id="WF-INST-0720",
            tenant_id=tenant_id,
            grund=ArchivierungsGrund.MANUELL,
            status=ArchivStatus.GELOESCHT,
            aufbewahrungsklasse=AufbewahrungsKlasse.KLASSE_D,
            archiviert_am=datetime(2024, 1, 1, 0, 0),
            beschreibung="Temporaerer Vorgang — bereits geloescht",
        ),
        ArchivEintrag(
            eintrag_id="AE-005",
            workflow_instanz_id="WF-INST-1100",
            tenant_id=tenant_id,
            grund=ArchivierungsGrund.ABGESCHLOSSEN,
            status=ArchivStatus.AKTIV,
            aufbewahrungsklasse=AufbewahrungsKlasse.KLASSE_B,
            archiviert_am=basis,
            beschreibung="Laufender Vorgang noch aktiv",
        ),
    ]
