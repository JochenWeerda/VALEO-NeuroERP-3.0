from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Any
from datetime import datetime


class EreignisTyp(str, Enum):
    ERSTELLT = "ERSTELLT"
    ZUSTAND_GEAENDERT = "ZUSTAND_GEAENDERT"
    AKTION_AUSGEFUEHRT = "AKTION_AUSGEFUEHRT"
    KOMPENSIERT = "KOMPENSIERT"
    ABGESCHLOSSEN = "ABGESCHLOSSEN"
    FEHLER_AUFGETRETEN = "FEHLER_AUFGETRETEN"


class ReplayModus(str, Enum):
    VOLLSTAENDIG = "VOLLSTAENDIG"     # Replay all events
    BIS_ZEITPUNKT = "BIS_ZEITPUNKT"  # Replay up to a timestamp
    AB_VERSION = "AB_VERSION"         # Replay from a specific version


@dataclass
class WorkflowEreignis:
    ereignis_id: str
    workflow_instanz_id: str
    ereignis_typ: EreignisTyp
    version: int                      # monotonically increasing per instance
    nutzlast: dict = field(default_factory=dict)
    ausgefuehrt_von: str = ""
    erstellt_am: datetime = field(default_factory=datetime.utcnow)
    tenant_id: str = ""


@dataclass
class EreignisStream:
    stream_id: str                    # == workflow_instanz_id
    ereignisse: list = field(default_factory=list)  # list[WorkflowEreignis], ordered by version

    def aktuelle_version(self) -> int:
        """Returns max version or 0 if empty."""
        if not self.ereignisse:
            return 0
        return max(e.version for e in self.ereignisse)

    def fuege_ereignis_hinzu(self, ereignis: WorkflowEreignis) -> 'EreignisStream':
        """Returns new stream with event appended. Event version must be aktuelle_version + 1."""
        import dataclasses
        neue_ereignisse = list(self.ereignisse) + [ereignis]
        return dataclasses.replace(self, ereignisse=neue_ereignisse)

    def replay(self, modus: ReplayModus, bis_zeitpunkt: Optional[datetime] = None, ab_version: int = 1) -> list:
        """
        VOLLSTAENDIG: returns all events sorted by version
        BIS_ZEITPUNKT: returns events where erstellt_am <= bis_zeitpunkt, sorted by version
        AB_VERSION: returns events where version >= ab_version, sorted by version
        """
        sortiert = sorted(self.ereignisse, key=lambda e: e.version)
        if modus == ReplayModus.VOLLSTAENDIG:
            return sortiert
        elif modus == ReplayModus.BIS_ZEITPUNKT:
            if bis_zeitpunkt is None:
                return sortiert
            return [e for e in sortiert if e.erstellt_am <= bis_zeitpunkt]
        else:  # AB_VERSION
            return [e for e in sortiert if e.version >= ab_version]


def rekonstruiere_zustand(ereignisse: list) -> dict:
    """
    Folds events into a state dict.
    - ERSTELLT: sets {"workflow_instanz_id": ..., "zustand": "ERSTELLT", "version": n}
    - ZUSTAND_GEAENDERT: updates "zustand" from nutzlast["neuer_zustand"]
    - AKTION_AUSGEFUEHRT: adds "letzte_aktion" from nutzlast["aktion"]
    - KOMPENSIERT: sets "zustand" to "KOMPENSIERT"
    - ABGESCHLOSSEN: sets "zustand" to "ABGESCHLOSSEN"
    - FEHLER_AUFGETRETEN: sets "fehler" from nutzlast.get("fehler", "unbekannt")
    Always updates "version" to current event version.
    Returns {} for empty list.
    """
    if not ereignisse:
        return {}
    zustand = {}
    for e in sorted(ereignisse, key=lambda x: x.version):
        zustand["version"] = e.version
        if e.ereignis_typ == EreignisTyp.ERSTELLT:
            zustand["workflow_instanz_id"] = e.workflow_instanz_id
            zustand["zustand"] = "ERSTELLT"
        elif e.ereignis_typ == EreignisTyp.ZUSTAND_GEAENDERT:
            zustand["zustand"] = e.nutzlast.get("neuer_zustand", zustand.get("zustand"))
        elif e.ereignis_typ == EreignisTyp.AKTION_AUSGEFUEHRT:
            zustand["letzte_aktion"] = e.nutzlast.get("aktion", "")
        elif e.ereignis_typ == EreignisTyp.KOMPENSIERT:
            zustand["zustand"] = "KOMPENSIERT"
        elif e.ereignis_typ == EreignisTyp.ABGESCHLOSSEN:
            zustand["zustand"] = "ABGESCHLOSSEN"
        elif e.ereignis_typ == EreignisTyp.FEHLER_AUFGETRETEN:
            zustand["fehler"] = e.nutzlast.get("fehler", "unbekannt")
    return zustand


def get_default_ereignis_streams() -> list:
    """Returns 4 default EreignisStream examples."""
    from datetime import timedelta
    now = datetime(2026, 3, 16, 10, 0, 0)

    # Stream 1: Completed kontrakt workflow (4 events)
    s1 = EreignisStream("WI-KONTRAKT-001")
    for i, (typ, nutzlast) in enumerate([
        (EreignisTyp.ERSTELLT, {}),
        (EreignisTyp.ZUSTAND_GEAENDERT, {"neuer_zustand": "PRUEFUNG"}),
        (EreignisTyp.AKTION_AUSGEFUEHRT, {"aktion": "freigabe_erteilt"}),
        (EreignisTyp.ABGESCHLOSSEN, {}),
    ], start=1):
        s1.ereignisse.append(WorkflowEreignis(
            f"EVT-{i:03d}", "WI-KONTRAKT-001", typ, i, nutzlast,
            "user-001", now + timedelta(minutes=i), "TENANT-A"
        ))

    # Stream 2: Compensated settlement (3 events)
    s2 = EreignisStream("WI-SETTLEMENT-002")
    for i, (typ, nutzlast) in enumerate([
        (EreignisTyp.ERSTELLT, {}),
        (EreignisTyp.FEHLER_AUFGETRETEN, {"fehler": "Buchungsfehler"}),
        (EreignisTyp.KOMPENSIERT, {}),
    ], start=1):
        s2.ereignisse.append(WorkflowEreignis(
            f"EVT-S{i:03d}", "WI-SETTLEMENT-002", typ, i, nutzlast,
            "system", now + timedelta(minutes=i), "TENANT-A"
        ))

    # Stream 3: Running invoice approval (2 events)
    s3 = EreignisStream("WI-RECHNUNG-003")
    for i, (typ, nutzlast) in enumerate([
        (EreignisTyp.ERSTELLT, {}),
        (EreignisTyp.ZUSTAND_GEAENDERT, {"neuer_zustand": "FREIGABE_AUSSTEHEND"}),
    ], start=1):
        s3.ereignisse.append(WorkflowEreignis(
            f"EVT-R{i:03d}", "WI-RECHNUNG-003", typ, i, nutzlast,
            "user-002", now + timedelta(minutes=i), "TENANT-B"
        ))

    # Stream 4: Empty stream
    s4 = EreignisStream("WI-LEER-004")

    return [s1, s2, s3, s4]
