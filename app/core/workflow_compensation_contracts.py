"""
Wave 51 – Workflow Compensation Contracts (Saga-Pattern)
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from datetime import datetime


class KompensationsTyp(str, Enum):
    RUECKGAENGIG = "RUECKGAENGIG"
    AUSGLEICH = "AUSGLEICH"
    NEUSTART = "NEUSTART"
    UEBERSPRINGEN = "UEBERSPRINGEN"
    ABBRECHEN = "ABBRECHEN"


class KompensationsStatus(str, Enum):
    AUSSTEHEND = "AUSSTEHEND"
    LAUFEND = "LAUFEND"
    ABGESCHLOSSEN = "ABGESCHLOSSEN"
    FEHLGESCHLAGEN = "FEHLGESCHLAGEN"
    NICHT_NOTWENDIG = "NICHT_NOTWENDIG"


class SagaStatus(str, Enum):
    LAUFEND = "LAUFEND"
    ABGESCHLOSSEN = "ABGESCHLOSSEN"
    KOMPENSIERT = "KOMPENSIERT"
    FEHLGESCHLAGEN = "FEHLGESCHLAGEN"


@dataclass
class KompensationsSchritt:
    schritt_id: str
    saga_id: str
    schritt_name: str
    kompensations_typ: KompensationsTyp
    status: KompensationsStatus = KompensationsStatus.AUSSTEHEND
    ausgefuehrt_von: str = ""
    erstellt_am: datetime = field(default_factory=datetime.utcnow)
    abgeschlossen_am: Optional[datetime] = None
    fehler_nachricht: str = ""

    @property
    def ist_abgeschlossen(self) -> bool:
        return self.status in (
            KompensationsStatus.ABGESCHLOSSEN,
            KompensationsStatus.FEHLGESCHLAGEN,
            KompensationsStatus.NICHT_NOTWENDIG,
        )


@dataclass
class SagaInstanz:
    saga_id: str
    saga_typ: str
    tenant_id: str
    schritte: list = field(default_factory=list)  # list[KompensationsSchritt]
    status: SagaStatus = SagaStatus.LAUFEND
    ausgeloest_von: str = ""
    erstellt_am: datetime = field(default_factory=datetime.utcnow)
    abgeschlossen_am: Optional[datetime] = None

    def offene_kompensationen(self) -> list:
        """Returns steps with status AUSSTEHEND."""
        return [s for s in self.schritte if s.status == KompensationsStatus.AUSSTEHEND]

    def berechne_saga_status(self) -> SagaStatus:
        """
        Derives SagaStatus from steps:
        - Any LAUFEND → LAUFEND
        - Any FEHLGESCHLAGEN → FEHLGESCHLAGEN
        - All done, any ABGESCHLOSSEN → KOMPENSIERT
        - All NICHT_NOTWENDIG or empty → ABGESCHLOSSEN
        """
        if not self.schritte:
            return SagaStatus.ABGESCHLOSSEN
        stati = [s.status for s in self.schritte]
        if any(s == KompensationsStatus.LAUFEND for s in stati):
            return SagaStatus.LAUFEND
        if any(s == KompensationsStatus.FEHLGESCHLAGEN for s in stati):
            return SagaStatus.FEHLGESCHLAGEN
        if all(s == KompensationsStatus.NICHT_NOTWENDIG for s in stati):
            return SagaStatus.ABGESCHLOSSEN
        return SagaStatus.KOMPENSIERT


def erstelle_kompensations_plan(saga_id: str, saga_typ: str, tenant_id: str, schritt_definitionen: list) -> SagaInstanz:
    """
    Creates a SagaInstanz with KompensationsSchritt instances from definitions.
    schritt_definitionen: list of dicts with keys: schritt_id, schritt_name, kompensations_typ
    """
    schritte = []
    for d in schritt_definitionen:
        schritte.append(KompensationsSchritt(
            schritt_id=d["schritt_id"],
            saga_id=saga_id,
            schritt_name=d["schritt_name"],
            kompensations_typ=KompensationsTyp(d["kompensations_typ"]),
        ))
    return SagaInstanz(
        saga_id=saga_id,
        saga_typ=saga_typ,
        tenant_id=tenant_id,
        schritte=schritte,
    )


def get_default_saga_instanzen() -> list:
    """Returns 4 default SagaInstanz examples."""
    now = datetime(2026, 3, 16, 10, 0, 0)

    si1 = SagaInstanz("SI-001", "kontrakt_storno", "TENANT-A", status=SagaStatus.ABGESCHLOSSEN, erstellt_am=now)
    si1.schritte = [
        KompensationsSchritt("SK-001", "SI-001", "Bestand freigeben", KompensationsTyp.RUECKGAENGIG, KompensationsStatus.NICHT_NOTWENDIG),
        KompensationsSchritt("SK-002", "SI-001", "Zahlung stornieren", KompensationsTyp.AUSGLEICH, KompensationsStatus.NICHT_NOTWENDIG),
    ]

    si2 = SagaInstanz("SI-002", "settlement_rollback", "TENANT-A", status=SagaStatus.KOMPENSIERT, erstellt_am=now)
    si2.schritte = [
        KompensationsSchritt("SK-003", "SI-002", "Journal-Eintrag rückgängig", KompensationsTyp.RUECKGAENGIG, KompensationsStatus.ABGESCHLOSSEN),
        KompensationsSchritt("SK-004", "SI-002", "Bestand korrigieren", KompensationsTyp.AUSGLEICH, KompensationsStatus.ABGESCHLOSSEN),
    ]

    si3 = SagaInstanz("SI-003", "rechnungs_storno", "TENANT-B", status=SagaStatus.LAUFEND, erstellt_am=now)
    si3.schritte = [
        KompensationsSchritt("SK-005", "SI-003", "Rechnung stornieren", KompensationsTyp.RUECKGAENGIG, KompensationsStatus.LAUFEND),
        KompensationsSchritt("SK-006", "SI-003", "Zahlung zurückbuchen", KompensationsTyp.AUSGLEICH, KompensationsStatus.AUSSTEHEND),
    ]

    si4 = SagaInstanz("SI-004", "bestellung_abbruch", "TENANT-B", status=SagaStatus.FEHLGESCHLAGEN, erstellt_am=now)
    si4.schritte = [
        KompensationsSchritt("SK-007", "SI-004", "Lieferung stornieren", KompensationsTyp.ABBRECHEN, KompensationsStatus.FEHLGESCHLAGEN, fehler_nachricht="Lieferant nicht erreichbar"),
        KompensationsSchritt("SK-008", "SI-004", "Bestand freigeben", KompensationsTyp.RUECKGAENGIG, KompensationsStatus.AUSSTEHEND),
    ]

    return [si1, si2, si3, si4]
