from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from datetime import datetime, timedelta


class RessourceLockTyp(str, Enum):
    EXKLUSIV = "EXKLUSIV"           # One owner only
    GETEILT = "GETEILT"             # Multiple readers OK
    UPGRADE = "UPGRADE"             # Shared → Exclusive upgrade intent


class DeadlockStatus(str, Enum):
    KEIN_DEADLOCK = "KEIN_DEADLOCK"
    DEADLOCK_ERKANNT = "DEADLOCK_ERKANNT"
    DEADLOCK_AUFGELOEST = "DEADLOCK_AUFGELOEST"


@dataclass
class RessourceLock:
    lock_id: str
    ressource_id: str
    inhaber_id: str
    lock_typ: RessourceLockTyp
    erstellt_am: datetime = field(default_factory=datetime.utcnow)
    ttl_sekunden: int = 300
    ablauf_am: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        self.ablauf_am = self.erstellt_am + timedelta(seconds=self.ttl_sekunden)

    def ist_aktiv(self, jetzt: datetime) -> bool:
        return jetzt < self.ablauf_am


@dataclass
class WarteschlangenEintrag:
    eintrag_id: str
    inhaber_id: str
    ressource_id: str
    benoetigt_lock_typ: RessourceLockTyp
    wartet_seit: datetime


@dataclass
class DeadlockAnalyse:
    analyse_id: str
    status: DeadlockStatus
    beteiligte_inhaber: list = field(default_factory=list)  # list[str]
    aufloesungs_vorschlag: str = ""


def pruefe_lock_kompatibilitaet(bestehend: RessourceLockTyp, neu: RessourceLockTyp) -> bool:
    """
    GETEILT + GETEILT → True (multiple readers OK)
    GETEILT + EXKLUSIV → False
    EXKLUSIV + GETEILT → False
    EXKLUSIV + EXKLUSIV → False
    UPGRADE + GETEILT → True (upgrade intent compatible with shared)
    UPGRADE + EXKLUSIV → False
    UPGRADE + UPGRADE → False
    """
    if bestehend == RessourceLockTyp.GETEILT and neu == RessourceLockTyp.GETEILT:
        return True
    if bestehend == RessourceLockTyp.UPGRADE and neu == RessourceLockTyp.GETEILT:
        return True
    return False


def erkenne_deadlock(warte_relationen: list) -> DeadlockAnalyse:
    """
    warte_relationen: list of {"wartet": str, "auf": str} dicts.
    Detects cycle using DFS.
    Returns DeadlockAnalyse with DEADLOCK_ERKANNT if cycle found, else KEIN_DEADLOCK.
    beteiligte_inhaber: all nodes in the cycle (empty if no deadlock).
    """
    # Build adjacency: wartet → auf
    graph = {}
    alle_knoten = set()
    for r in warte_relationen:
        w, a = r["wartet"], r["auf"]
        graph.setdefault(w, []).append(a)
        alle_knoten.add(w)
        alle_knoten.add(a)

    besucht = set()
    im_stack = set()

    def dfs(knoten, pfad):
        besucht.add(knoten)
        im_stack.add(knoten)
        pfad.append(knoten)
        for nachbar in graph.get(knoten, []):
            if nachbar not in besucht:
                result = dfs(nachbar, pfad)
                if result:
                    return result
            elif nachbar in im_stack:
                # Found cycle — extract cycle members
                zyklus_start = pfad.index(nachbar)
                return pfad[zyklus_start:]
        pfad.pop()
        im_stack.discard(knoten)
        return None

    for knoten in alle_knoten:
        if knoten not in besucht:
            zyklus = dfs(knoten, [])
            if zyklus:
                return DeadlockAnalyse(
                    "DA-AUTO", DeadlockStatus.DEADLOCK_ERKANNT,
                    beteiligte_inhaber=zyklus,
                    aufloesungs_vorschlag=f"Abbreche Prozess {zyklus[0]} zur Deadlock-Auflösung"
                )
    return DeadlockAnalyse("DA-AUTO", DeadlockStatus.KEIN_DEADLOCK)


def get_default_resource_locks() -> list:
    now = datetime(2026, 3, 16, 10, 0, 0)
    return [
        RessourceLock("RL-001", "KONTRAKT-001", "WI-K-001", RessourceLockTyp.EXKLUSIV, now, 300),
        RessourceLock("RL-002", "SETTLEMENT-001", "WI-S-001", RessourceLockTyp.GETEILT, now, 600),
        RessourceLock("RL-003", "SETTLEMENT-001", "WI-S-002", RessourceLockTyp.GETEILT, now, 600),
        RessourceLock("RL-004", "BATCH-001", "WI-B-001", RessourceLockTyp.EXKLUSIV,
                      now - timedelta(hours=1), 60),  # expired
    ]
