from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from datetime import datetime

class SignalTyp(str, Enum):
    EXTERN = "EXTERN"          # From external system
    INTERN = "INTERN"          # From another workflow
    ZEITPLAN = "ZEITPLAN"      # Scheduled/timer signal
    BENUTZER = "BENUTZER"      # Manual user action
    SYSTEM = "SYSTEM"          # Platform-generated

class SignalStatus(str, Enum):
    AUSSTEHEND = "AUSSTEHEND"
    ZUGESTELLT = "ZUGESTELLT"
    VERARBEITET = "VERARBEITET"
    ABGELAUFEN = "ABGELAUFEN"
    ABGEWIESEN = "ABGEWIESEN"

class TriggerAktion(str, Enum):
    FORTSETZEN = "FORTSETZEN"      # Resume waiting workflow
    ABBRECHEN = "ABBRECHEN"        # Cancel workflow
    ESKALIEREN = "ESKALIEREN"      # Escalate to supervisor
    BENACHRICHTIGEN = "BENACHRICHTIGEN"  # Notify only, no state change

@dataclass
class WorkflowSignal:
    signal_id: str
    workflow_instanz_id: str
    signal_typ: SignalTyp
    nutzlast: dict = field(default_factory=dict)
    status: SignalStatus = SignalStatus.AUSSTEHEND
    erstellt_am: datetime = field(default_factory=datetime.utcnow)
    zugestellt_am: Optional[datetime] = None
    ablauf_am: Optional[datetime] = None
    quelle: str = ""

    def ist_abgelaufen(self, jetzt: datetime) -> bool:
        if self.ablauf_am is None:
            return False
        return jetzt >= self.ablauf_am

    def aktueller_status(self, jetzt: datetime) -> SignalStatus:
        if self.status == SignalStatus.AUSSTEHEND and self.ist_abgelaufen(jetzt):
            return SignalStatus.ABGELAUFEN
        return self.status

@dataclass
class SignalRegel:
    regel_id: str
    signal_typ: SignalTyp
    trigger_aktion: TriggerAktion
    workflow_typ: str            # which workflow type this applies to
    bedingung: str = ""          # optional condition description
    ist_aktiv: bool = True

@dataclass
class SignalVerarbeitungsErgebnis:
    signal_id: str
    workflow_instanz_id: str
    trigger_aktion: TriggerAktion
    erfolgreich: bool
    nachricht: str = ""

def verarbeite_signal(signal: WorkflowSignal, regeln: list, jetzt: datetime) -> SignalVerarbeitungsErgebnis:
    """
    Finds first matching active SignalRegel by signal_typ.
    If signal is abgelaufen -> erfolgreich=False, nachricht="Signal abgelaufen"
    If no matching rule -> erfolgreich=False, nachricht="Keine passende Regel"
    Otherwise -> erfolgreich=True, trigger_aktion from rule
    """
    if signal.ist_abgelaufen(jetzt):
        return SignalVerarbeitungsErgebnis(signal.signal_id, signal.workflow_instanz_id,
                                           TriggerAktion.BENACHRICHTIGEN, False, "Signal abgelaufen")
    passende = [r for r in regeln if r.signal_typ == signal.signal_typ and r.ist_aktiv]
    if not passende:
        return SignalVerarbeitungsErgebnis(signal.signal_id, signal.workflow_instanz_id,
                                           TriggerAktion.BENACHRICHTIGEN, False, "Keine passende Regel")
    regel = passende[0]
    return SignalVerarbeitungsErgebnis(signal.signal_id, signal.workflow_instanz_id,
                                       regel.trigger_aktion, True, f"Regel {regel.regel_id} angewendet")

def get_default_signal_regeln() -> list:
    return [
        SignalRegel("SR-001", SignalTyp.EXTERN, TriggerAktion.FORTSETZEN, "kontrakt_freigabe", "EDI-Bestaetigung"),
        SignalRegel("SR-002", SignalTyp.BENUTZER, TriggerAktion.FORTSETZEN, "ap_rechnung", "Manuelle Freigabe"),
        SignalRegel("SR-003", SignalTyp.ZEITPLAN, TriggerAktion.ESKALIEREN, "settlement", "SLA-Timeout"),
        SignalRegel("SR-004", SignalTyp.INTERN, TriggerAktion.FORTSETZEN, "qualitaet", "Qualitaetsfreigabe"),
        SignalRegel("SR-005", SignalTyp.SYSTEM, TriggerAktion.ABBRECHEN, "fehler_workflow", "Systemfehler"),
    ]

def get_default_signale() -> list:
    now = datetime(2026, 3, 16, 10, 0, 0)
    from datetime import timedelta
    return [
        WorkflowSignal("SIG-001", "WI-K-001", SignalTyp.EXTERN, {"bestaetigung": "EDI-OK"}, SignalStatus.AUSSTEHEND, now, None, now + timedelta(hours=1), "EDI-Gateway"),
        WorkflowSignal("SIG-002", "WI-AP-002", SignalTyp.BENUTZER, {"freigabe": True}, SignalStatus.VERARBEITET, now, now, None, "user-001"),
        WorkflowSignal("SIG-003", "WI-S-003", SignalTyp.ZEITPLAN, {}, SignalStatus.AUSSTEHEND, now - timedelta(hours=2), None, now - timedelta(hours=1), "scheduler"),
        WorkflowSignal("SIG-004", "WI-Q-004", SignalTyp.INTERN, {"lot_id": "LOT-001"}, SignalStatus.ZUGESTELLT, now, now, None, "quality-service"),
    ]
