"""
Wave 51 – Process Capacity Planning Contracts
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from datetime import datetime


class KapazitaetsTyp(str, Enum):
    CPU = "CPU"
    SPEICHER = "SPEICHER"
    DATENBANKVERBINDUNGEN = "DATENBANKVERBINDUNGEN"
    NACHRICHTENWARTESCHLANGE = "NACHRICHTENWARTESCHLANGE"
    EXTERNE_API = "EXTERNE_API"


class KapazitaetsStatus(str, Enum):
    NORMAL = "NORMAL"
    ERHOET = "ERHOET"
    KRITISCH = "KRITISCH"
    UEBERLASTET = "UEBERLASTET"


class SkalierungsStrategie(str, Enum):
    MANUELL = "MANUELL"
    AUTOMATISCH = "AUTOMATISCH"
    KEIN_SKALIEREN = "KEIN_SKALIEREN"


@dataclass
class KapazitaetsRegel:
    regel_id: str
    kapazitaets_typ: KapazitaetsTyp
    max_kapazitaet: float
    warnschwelle_pct: float
    kritisch_schwelle_pct: float
    skalierungs_strategie: SkalierungsStrategie
    beschreibung: str = ""

    def berechne_status(self, aktuelle_auslastung: float) -> KapazitaetsStatus:
        """Calculate status from current utilization (0–max_kapazitaet scale)."""
        if self.max_kapazitaet <= 0:
            return KapazitaetsStatus.NORMAL
        pct = (aktuelle_auslastung / self.max_kapazitaet) * 100
        if pct >= 100:
            return KapazitaetsStatus.UEBERLASTET
        elif pct >= self.kritisch_schwelle_pct:
            return KapazitaetsStatus.KRITISCH
        elif pct >= self.warnschwelle_pct:
            return KapazitaetsStatus.ERHOET
        return KapazitaetsStatus.NORMAL


@dataclass
class KapazitaetsMessung:
    messung_id: str
    regel_id: str
    kapazitaets_typ: KapazitaetsTyp
    aktuelle_auslastung: float
    gemessen_am: datetime
    status: KapazitaetsStatus = KapazitaetsStatus.NORMAL


@dataclass
class KapazitaetsPlan:
    plan_id: str
    tenant_id: str
    messungen: list = field(default_factory=list)  # list[KapazitaetsMessung]
    erstellt_am: datetime = field(default_factory=datetime.utcnow)

    def kritische_messungen(self) -> list:
        return [m for m in self.messungen if m.status in (KapazitaetsStatus.KRITISCH, KapazitaetsStatus.UEBERLASTET)]

    def auslastungs_zusammenfassung(self) -> dict:
        """Returns {KapazitaetsStatus: count}"""
        result = {s: 0 for s in KapazitaetsStatus}
        for m in self.messungen:
            result[m.status] += 1
        return result


def get_default_kapazitaets_regeln() -> list:
    """Returns 5 default KapazitaetsRegel instances."""
    return [
        KapazitaetsRegel("KR-001", KapazitaetsTyp.CPU, 100.0, 70.0, 90.0, SkalierungsStrategie.AUTOMATISCH, "CPU-Auslastung"),
        KapazitaetsRegel("KR-002", KapazitaetsTyp.SPEICHER, 16384.0, 70.0, 90.0, SkalierungsStrategie.AUTOMATISCH, "Arbeitsspeicher MB"),
        KapazitaetsRegel("KR-003", KapazitaetsTyp.DATENBANKVERBINDUNGEN, 100.0, 70.0, 90.0, SkalierungsStrategie.MANUELL, "DB Connection Pool"),
        KapazitaetsRegel("KR-004", KapazitaetsTyp.NACHRICHTENWARTESCHLANGE, 10000.0, 70.0, 90.0, SkalierungsStrategie.AUTOMATISCH, "NATS Queue Depth"),
        KapazitaetsRegel("KR-005", KapazitaetsTyp.EXTERNE_API, 1000.0, 70.0, 90.0, SkalierungsStrategie.KEIN_SKALIEREN, "API Rate Limit RPM"),
    ]
