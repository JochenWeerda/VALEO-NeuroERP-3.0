"""
Wave 68 — Process Health Dashboard Contracts.
Pure domain layer: NO imports from app/api/.
"""
from enum import Enum
from dataclasses import dataclass, field, replace
from datetime import datetime
from typing import Optional, List, Dict


class KomponentenStatus(Enum):
    GESUND = "GESUND"
    DEGRADIERT = "DEGRADIERT"
    KRITISCH = "KRITISCH"
    AUSGEFALLEN = "AUSGEFALLEN"
    UNBEKANNT = "UNBEKANNT"


class MetrikTyp(Enum):
    DURCHSATZ = "DURCHSATZ"            # transactions/sec
    LATENZ = "LATENZ"                  # milliseconds
    FEHLERRATE = "FEHLERRATE"          # percent
    VERFUEGBARKEIT = "VERFUEGBARKEIT"  # percent uptime
    AUSLASTUNG = "AUSLASTUNG"          # percent capacity used


@dataclass
class MetrikSchwellwert:
    metrik_typ: MetrikTyp
    warnung_ab: float   # threshold for DEGRADIERT
    kritisch_ab: float  # threshold for KRITISCH
    einheit: str        # "ms", "%", "req/s"

    def bewerte(self, wert: float) -> KomponentenStatus:
        if wert >= self.kritisch_ab:
            return KomponentenStatus.KRITISCH
        if wert >= self.warnung_ab:
            return KomponentenStatus.DEGRADIERT
        return KomponentenStatus.GESUND


@dataclass
class KomponentenMetrik:
    komponente_id: str
    metrik_typ: MetrikTyp
    wert: float
    erfasst_am: datetime
    einheit: str


@dataclass
class DashboardKomponente:
    komponente_id: str
    name: str
    typ: str  # "api", "worker", "database", "queue"
    metriken: List[KomponentenMetrik] = field(default_factory=list)
    status_override: Optional[KomponentenStatus] = None

    def berechne_status(self, schwellwerte: List[MetrikSchwellwert]) -> KomponentenStatus:
        if self.status_override:
            return self.status_override
        if not self.metriken:
            return KomponentenStatus.UNBEKANNT

        rang = [
            KomponentenStatus.GESUND,
            KomponentenStatus.DEGRADIERT,
            KomponentenStatus.KRITISCH,
            KomponentenStatus.AUSGEFALLEN,
        ]

        schlechtester = KomponentenStatus.GESUND
        for metrik in self.metriken:
            for sw in schwellwerte:
                if sw.metrik_typ == metrik.metrik_typ:
                    status = sw.bewerte(metrik.wert)
                    if rang.index(status) > rang.index(schlechtester):
                        schlechtester = status
        return schlechtester

    def letzte_metrik(self, typ: MetrikTyp) -> Optional[KomponentenMetrik]:
        treffer = [m for m in self.metriken if m.metrik_typ == typ]
        if not treffer:
            return None
        return max(treffer, key=lambda m: m.erfasst_am)


@dataclass
class HealthDashboard:
    dashboard_id: str
    name: str
    komponenten: List[DashboardKomponente] = field(default_factory=list)
    schwellwerte: List[MetrikSchwellwert] = field(default_factory=list)
    erstellt_am: datetime = field(default_factory=datetime.now)

    def gesamtstatus(self) -> KomponentenStatus:
        if not self.komponenten:
            return KomponentenStatus.UNBEKANNT
        rang = [
            KomponentenStatus.GESUND,
            KomponentenStatus.UNBEKANNT,
            KomponentenStatus.DEGRADIERT,
            KomponentenStatus.KRITISCH,
            KomponentenStatus.AUSGEFALLEN,
        ]
        schlechtester = KomponentenStatus.GESUND
        for k in self.komponenten:
            s = k.berechne_status(self.schwellwerte)
            if rang.index(s) > rang.index(schlechtester):
                schlechtester = s
        return schlechtester

    def kritische_komponenten(self) -> List[DashboardKomponente]:
        return [
            k for k in self.komponenten
            if k.berechne_status(self.schwellwerte) in
            (KomponentenStatus.KRITISCH, KomponentenStatus.AUSGEFALLEN)
        ]

    def verfuegbarkeits_pct(self) -> float:
        if not self.komponenten:
            return 0.0
        gesund = sum(
            1 for k in self.komponenten
            if k.berechne_status(self.schwellwerte) == KomponentenStatus.GESUND
        )
        return round(gesund / len(self.komponenten) * 100, 2)


# 5 default Schwellwerte (above threshold = worse semantics)
STANDARD_SCHWELLWERTE = [
    MetrikSchwellwert(MetrikTyp.LATENZ, warnung_ab=500.0, kritisch_ab=2000.0, einheit="ms"),
    MetrikSchwellwert(MetrikTyp.FEHLERRATE, warnung_ab=1.0, kritisch_ab=5.0, einheit="%"),
    MetrikSchwellwert(MetrikTyp.AUSLASTUNG, warnung_ab=70.0, kritisch_ab=90.0, einheit="%"),
    MetrikSchwellwert(MetrikTyp.DURCHSATZ, warnung_ab=100.0, kritisch_ab=10.0, einheit="req/s"),
    MetrikSchwellwert(MetrikTyp.VERFUEGBARKEIT, warnung_ab=99.0, kritisch_ab=95.0, einheit="%"),
]
