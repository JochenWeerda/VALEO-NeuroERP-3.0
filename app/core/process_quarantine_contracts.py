"""
Process Quarantine Contracts — Wave 46
Quarantäne-Mechanismus für fehlgeschlagene/suspekte Prozessinstanzen:
Retry-Strategien, Dead-Letter-Management und Freigabeprüfung.

Schichtregeln:
- Kein Import aus app/api/ oder app/infrastructure/
- Nur Stdlib + eigene Core-Module
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any


# ---------------------------------------------------------------------------
# Enumerationen
# ---------------------------------------------------------------------------

class QuarantaeneGrund(str, Enum):
    VALIDIERUNGSFEHLER = "VALIDIERUNGSFEHLER"
    TIMEOUT = "TIMEOUT"
    KAPAZITAET_ERSCHOEPFT = "KAPAZITAET_ERSCHOEPFT"
    SICHERHEITSVERSTOS = "SICHERHEITSVERSTOS"
    DATENFEHLER = "DATENFEHLER"
    MANUELL = "MANUELL"


class RetryStrategie(str, Enum):
    SOFORT = "SOFORT"
    EXPONENTIELL = "EXPONENTIELL"
    FESTER_INTERVALL = "FESTER_INTERVALL"
    KEIN_RETRY = "KEIN_RETRY"


class QuarantaeneStatus(str, Enum):
    IN_QUARANTAENE = "IN_QUARANTAENE"
    FREIGEGEBEN = "FREIGEGEBEN"
    ABGEBROCHEN = "ABGEBROCHEN"
    DEAD_LETTER = "DEAD_LETTER"


# ---------------------------------------------------------------------------
# Quarantäne-Eintrag
# ---------------------------------------------------------------------------

@dataclass
class QuarantaeneEintrag:
    """Eine in Quarantäne befindliche Workflow-Instanz."""
    eintrag_id: str
    workflow_instanz_id: str
    tenant_id: str
    grund: QuarantaeneGrund
    status: QuarantaeneStatus
    retry_strategie: RetryStrategie
    versuch_anzahl: int
    max_versuche: int
    eingestellt_am: datetime
    letzter_versuch: datetime | None = None
    naechster_versuch: datetime | None = None
    fehlermeldung: str = ""

    @property
    def kann_wiederholt_werden(self) -> bool:
        """True wenn Retry möglich: Status IN_QUARANTAENE und Versuche nicht erschöpft."""
        return (
            self.status == QuarantaeneStatus.IN_QUARANTAENE
            and self.versuch_anzahl < self.max_versuche
            and self.retry_strategie != RetryStrategie.KEIN_RETRY
        )

    @property
    def ist_dead_letter(self) -> bool:
        return (
            self.status == QuarantaeneStatus.DEAD_LETTER
            or self.versuch_anzahl >= self.max_versuche
        )

    def berechne_naechsten_versuch(
        self,
        basis_intervall_sekunden: float = 60.0,
        jetzt: datetime | None = None,
    ) -> datetime | None:
        """
        Berechnet den nächsten Retry-Zeitpunkt.

        - SOFORT: jetzt
        - FESTER_INTERVALL: jetzt + basis_intervall_sekunden
        - EXPONENTIELL: jetzt + basis_intervall_sekunden * 2^versuch_anzahl
        - KEIN_RETRY: None
        """
        if self.retry_strategie == RetryStrategie.KEIN_RETRY:
            return None
        ts = jetzt or datetime.utcnow()
        if self.retry_strategie == RetryStrategie.SOFORT:
            return ts
        if self.retry_strategie == RetryStrategie.FESTER_INTERVALL:
            return ts + timedelta(seconds=basis_intervall_sekunden)
        if self.retry_strategie == RetryStrategie.EXPONENTIELL:
            sekunden = basis_intervall_sekunden * (2 ** self.versuch_anzahl)
            return ts + timedelta(seconds=sekunden)
        return None

    def as_dict(self) -> dict[str, Any]:
        return {
            "eintrag_id": self.eintrag_id,
            "workflow_instanz_id": self.workflow_instanz_id,
            "tenant_id": self.tenant_id,
            "grund": self.grund.value,
            "status": self.status.value,
            "retry_strategie": self.retry_strategie.value,
            "versuch_anzahl": self.versuch_anzahl,
            "max_versuche": self.max_versuche,
            "eingestellt_am": self.eingestellt_am.isoformat(),
            "letzter_versuch": self.letzter_versuch.isoformat() if self.letzter_versuch else None,
            "naechster_versuch": self.naechster_versuch.isoformat() if self.naechster_versuch else None,
            "fehlermeldung": self.fehlermeldung,
            "kann_wiederholt_werden": self.kann_wiederholt_werden,
            "ist_dead_letter": self.ist_dead_letter,
        }


# ---------------------------------------------------------------------------
# Quarantäne-Statistik
# ---------------------------------------------------------------------------

@dataclass
class QuarantaeneStatistik:
    """Aggregierte Statistik über Quarantäne-Einträge eines Tenants."""
    tenant_id: str
    in_quarantaene: int
    freigegeben: int
    abgebrochen: int
    dead_letter: int

    @property
    def gesamt(self) -> int:
        return self.in_quarantaene + self.freigegeben + self.abgebrochen + self.dead_letter

    @property
    def dead_letter_rate_pct(self) -> float:
        if self.gesamt == 0:
            return 0.0
        return round(self.dead_letter / self.gesamt * 100, 2)

    def as_dict(self) -> dict[str, Any]:
        return {
            "tenant_id": self.tenant_id,
            "in_quarantaene": self.in_quarantaene,
            "freigegeben": self.freigegeben,
            "abgebrochen": self.abgebrochen,
            "dead_letter": self.dead_letter,
            "gesamt": self.gesamt,
            "dead_letter_rate_pct": self.dead_letter_rate_pct,
        }


# ---------------------------------------------------------------------------
# Logik
# ---------------------------------------------------------------------------

def berechne_quarantaene_statistik(
    eintraege: list[QuarantaeneEintrag],
    tenant_id: str,
) -> QuarantaeneStatistik:
    """Aggregiert Quarantäne-Einträge für einen Tenant."""
    relevant = [e for e in eintraege if e.tenant_id == tenant_id]
    return QuarantaeneStatistik(
        tenant_id=tenant_id,
        in_quarantaene=sum(1 for e in relevant if e.status == QuarantaeneStatus.IN_QUARANTAENE),
        freigegeben=sum(1 for e in relevant if e.status == QuarantaeneStatus.FREIGEGEBEN),
        abgebrochen=sum(1 for e in relevant if e.status == QuarantaeneStatus.ABGEBROCHEN),
        dead_letter=sum(1 for e in relevant if e.status == QuarantaeneStatus.DEAD_LETTER),
    )


# ---------------------------------------------------------------------------
# Standarddaten
# ---------------------------------------------------------------------------

def get_default_quarantaene_eintraege(
    tenant_id: str = "TENANT-001",
) -> list[QuarantaeneEintrag]:
    """Gibt 5 Standard-Quarantäne-Einträge zurück."""
    basis = datetime(2026, 3, 15, 8, 0)
    return [
        QuarantaeneEintrag(
            eintrag_id="QE-001",
            workflow_instanz_id="WF-INST-0091",
            tenant_id=tenant_id,
            grund=QuarantaeneGrund.VALIDIERUNGSFEHLER,
            status=QuarantaeneStatus.IN_QUARANTAENE,
            retry_strategie=RetryStrategie.EXPONENTIELL,
            versuch_anzahl=1,
            max_versuche=5,
            eingestellt_am=basis,
            fehlermeldung="Pflichtfeld 'kontrakt_id' fehlt",
        ),
        QuarantaeneEintrag(
            eintrag_id="QE-002",
            workflow_instanz_id="WF-INST-0087",
            tenant_id=tenant_id,
            grund=QuarantaeneGrund.TIMEOUT,
            status=QuarantaeneStatus.IN_QUARANTAENE,
            retry_strategie=RetryStrategie.FESTER_INTERVALL,
            versuch_anzahl=2,
            max_versuche=3,
            eingestellt_am=basis.replace(hour=9),
            fehlermeldung="Zeitüberschreitung nach 30s",
        ),
        QuarantaeneEintrag(
            eintrag_id="QE-003",
            workflow_instanz_id="WF-INST-0075",
            tenant_id=tenant_id,
            grund=QuarantaeneGrund.DATENFEHLER,
            status=QuarantaeneStatus.DEAD_LETTER,
            retry_strategie=RetryStrategie.EXPONENTIELL,
            versuch_anzahl=5,
            max_versuche=5,
            eingestellt_am=basis.replace(hour=7),
            fehlermeldung="Max. Versuche erreicht — Datenfehler nicht behebbar",
        ),
        QuarantaeneEintrag(
            eintrag_id="QE-004",
            workflow_instanz_id="WF-INST-0062",
            tenant_id=tenant_id,
            grund=QuarantaeneGrund.MANUELL,
            status=QuarantaeneStatus.FREIGEGEBEN,
            retry_strategie=RetryStrategie.SOFORT,
            versuch_anzahl=1,
            max_versuche=3,
            eingestellt_am=basis.replace(day=14),
            fehlermeldung="",
        ),
        QuarantaeneEintrag(
            eintrag_id="QE-005",
            workflow_instanz_id="WF-INST-0055",
            tenant_id=tenant_id,
            grund=QuarantaeneGrund.SICHERHEITSVERSTOS,
            status=QuarantaeneStatus.ABGEBROCHEN,
            retry_strategie=RetryStrategie.KEIN_RETRY,
            versuch_anzahl=0,
            max_versuche=0,
            eingestellt_am=basis.replace(day=13),
            fehlermeldung="Sicherheitsverstoß — manuelle Prüfung erforderlich",
        ),
    ]
