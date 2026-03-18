from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from datetime import datetime


class SimulationsTyp(str, Enum):
    LAST_TEST = "LAST_TEST"               # Load simulation
    PFAD_ANALYSE = "PFAD_ANALYSE"         # Critical path analysis
    ENGPASS_ANALYSE = "ENGPASS_ANALYSE"   # Bottleneck detection
    WHAT_IF = "WHAT_IF"                   # Parameter variation


class SimulationsStatus(str, Enum):
    AUSSTEHEND = "AUSSTEHEND"
    LAUFEND = "LAUFEND"
    ABGESCHLOSSEN = "ABGESCHLOSSEN"
    FEHLGESCHLAGEN = "FEHLGESCHLAGEN"


@dataclass
class SimulationsParameter:
    parameter_id: str
    name: str
    basis_wert: float
    simulierter_wert: float
    einheit: str = ""

    @property
    def abweichung_pct(self) -> float:
        """(simulierter_wert - basis_wert) / basis_wert * 100. 0.0 if basis_wert==0."""
        if self.basis_wert == 0:
            return 0.0
        return ((self.simulierter_wert - self.basis_wert) / self.basis_wert) * 100


@dataclass
class SimulationsErgebnis:
    ergebnis_id: str
    simulations_typ: SimulationsTyp
    parameter: list = field(default_factory=list)  # list[SimulationsParameter]
    prognostizierte_dauer_minuten: float = 0.0
    engpass_schritt: Optional[str] = None
    empfehlung: str = ""
    konfidenz_pct: float = 0.0

    @property
    def groesste_abweichung(self) -> Optional[object]:
        """Returns SimulationsParameter with highest abs(abweichung_pct). None if empty."""
        if not self.parameter:
            return None
        return max(self.parameter, key=lambda p: abs(p.abweichung_pct))


@dataclass
class SimulationsLauf:
    lauf_id: str
    workflow_typ: str
    simulations_typ: SimulationsTyp
    status: SimulationsStatus = SimulationsStatus.AUSSTEHEND
    ergebnis: Optional[SimulationsErgebnis] = None
    gestartet_am: Optional[datetime] = None
    beendet_am: Optional[datetime] = None

    def laufzeit_sekunden(self) -> Optional[float]:
        """None if not finished. Seconds between start and end."""
        if self.gestartet_am is None or self.beendet_am is None:
            return None
        return (self.beendet_am - self.gestartet_am).total_seconds()


def get_default_simulations_laeufe() -> list:
    now = datetime(2026, 3, 16, 10, 0, 0)
    from datetime import timedelta

    # Lauf 1: completed WHAT_IF
    l1 = SimulationsLauf("SL-001", "kontrakt_freigabe", SimulationsTyp.WHAT_IF,
                          SimulationsStatus.ABGESCHLOSSEN,
                          gestartet_am=now - timedelta(minutes=10),
                          beendet_am=now - timedelta(minutes=8))
    l1.ergebnis = SimulationsErgebnis("SE-001", SimulationsTyp.WHAT_IF,
        parameter=[
            SimulationsParameter("SP-001", "Menge", 100.0, 150.0, "t"),       # +50%
            SimulationsParameter("SP-002", "Preis", 200.0, 190.0, "EUR/t"),   # -5%
        ],
        prognostizierte_dauer_minuten=45.0,
        engpass_schritt="Preisfreigabe",
        empfehlung="Menge unter 120t halten für optimale Durchlaufzeit",
        konfidenz_pct=78.0,
    )

    # Lauf 2: running ENGPASS
    l2 = SimulationsLauf("SL-002", "settlement_ausfuehren", SimulationsTyp.ENGPASS_ANALYSE,
                          SimulationsStatus.LAUFEND,
                          gestartet_am=now - timedelta(minutes=2))

    # Lauf 3: pending LAST_TEST
    l3 = SimulationsLauf("SL-003", "ap_rechnung", SimulationsTyp.LAST_TEST,
                          SimulationsStatus.AUSSTEHEND)

    return [l1, l2, l3]
