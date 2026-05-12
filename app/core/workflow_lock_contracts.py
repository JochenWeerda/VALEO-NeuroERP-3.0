"""
Workflow Lock Contracts — Wave 49
Optimistisches Sperren und Konkurrenzkontrolle fuer Workflow-Ressourcen:
Lock-Akquisition, Konflikterkennung und automatischer Ablauf.

Schichtregeln:
- Kein Import aus app/api/ oder app/infrastructure/
- Nur Stdlib + eigene Core-Module
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any


class LockTyp(str, Enum):
    LESEN = "LESEN"          # Shared Lock — mehrere Leser erlaubt
    SCHREIBEN = "SCHREIBEN"  # Exclusive Lock — nur ein Schreiber
    OPTIMISTISCH = "OPTIMISTISCH"  # Version-basiert, kein echter Lock


class LockStatus(str, Enum):
    AKTIV = "AKTIV"
    ABGELAUFEN = "ABGELAUFEN"
    FREIGEGEBEN = "FREIGEGEBEN"
    KONFLIKT = "KONFLIKT"


class KonfliktTyp(str, Enum):
    SCHREIB_SCHREIB = "SCHREIB_SCHREIB"   # Zwei Schreiber auf gleicher Ressource
    LESE_SCHREIB = "LESE_SCHREIB"         # Schreiber blockiert Leser
    VERSION_KONFLIKT = "VERSION_KONFLIKT"  # Optimistischer Lock: Version veraltet
    DEADLOCK = "DEADLOCK"                  # Zyklische Abhaengigkeit


@dataclass
class WorkflowLock:
    """Ein aktiver Lock auf einer Workflow-Ressource."""
    lock_id: str
    ressource_id: str
    inhaber_id: str       # User/Prozess-ID des Lock-Inhabers
    lock_typ: LockTyp
    status: LockStatus
    version: int          # Ressourcen-Version zum Lock-Zeitpunkt
    ttl_sekunden: int     # Time-to-live in Sekunden
    erstellt_am: datetime
    ablauf_am: datetime = field(init=False)

    def __post_init__(self) -> None:
        self.ablauf_am = self.erstellt_am + timedelta(seconds=self.ttl_sekunden)

    @property
    def ist_aktiv(self) -> bool:
        return self.status == LockStatus.AKTIV

    def ist_abgelaufen(self, jetzt: datetime) -> bool:
        """True wenn TTL ueberschritten."""
        return jetzt >= self.ablauf_am

    def pruefe_konflikt(self, anderer: "WorkflowLock") -> KonfliktTyp | None:
        """
        Prueft ob dieser Lock mit einem anderen Lock konfliktiert.

        Regeln:
        - Gleiche Ressource + beide SCHREIBEN -> SCHREIB_SCHREIB
        - Gleiche Ressource + einer SCHREIBEN, anderer LESEN -> LESE_SCHREIB
        - Gleiche Ressource + OPTIMISTISCH + verschiedene Versionen -> VERSION_KONFLIKT
        - Sonst kein Konflikt (None)
        """
        if self.ressource_id != anderer.ressource_id:
            return None
        if not (self.ist_aktiv and anderer.ist_aktiv):
            return None
        if self.inhaber_id == anderer.inhaber_id:
            return None

        if self.lock_typ == LockTyp.SCHREIBEN and anderer.lock_typ == LockTyp.SCHREIBEN:
            return KonfliktTyp.SCHREIB_SCHREIB
        if (self.lock_typ == LockTyp.SCHREIBEN) != (anderer.lock_typ == LockTyp.SCHREIBEN):
            # einer ist SCHREIBEN, der andere nicht
            if LockTyp.OPTIMISTISCH not in (self.lock_typ, anderer.lock_typ):
                return KonfliktTyp.LESE_SCHREIB
        if self.lock_typ == LockTyp.OPTIMISTISCH and anderer.lock_typ == LockTyp.OPTIMISTISCH:
            if self.version != anderer.version:
                return KonfliktTyp.VERSION_KONFLIKT
        return None

    def as_dict(self) -> dict[str, Any]:
        return {
            "lock_id": self.lock_id,
            "ressource_id": self.ressource_id,
            "inhaber_id": self.inhaber_id,
            "lock_typ": self.lock_typ.value,
            "status": self.status.value,
            "version": self.version,
            "ttl_sekunden": self.ttl_sekunden,
            "erstellt_am": self.erstellt_am.isoformat(),
            "ablauf_am": self.ablauf_am.isoformat(),
            "ist_aktiv": self.ist_aktiv,
        }


@dataclass
class LockAkquisitionsErgebnis:
    """Ergebnis eines Lock-Akquisitionsversuchs."""
    lock_id: str
    ressource_id: str
    inhaber_id: str
    lock_typ: LockTyp
    erfolg: bool
    konflikt_typ: KonfliktTyp | None = None
    konflikt_lock_id: str = ""
    begruendung: str = ""
    versucht_am: datetime = field(default_factory=datetime.utcnow)

    def as_dict(self) -> dict[str, Any]:
        return {
            "lock_id": self.lock_id,
            "ressource_id": self.ressource_id,
            "inhaber_id": self.inhaber_id,
            "lock_typ": self.lock_typ.value,
            "erfolg": self.erfolg,
            "konflikt_typ": self.konflikt_typ.value if self.konflikt_typ else None,
            "konflikt_lock_id": self.konflikt_lock_id,
            "begruendung": self.begruendung,
            "versucht_am": self.versucht_am.isoformat(),
        }


def akquiriere_lock(
    lock_id: str,
    ressource_id: str,
    inhaber_id: str,
    lock_typ: LockTyp,
    version: int,
    ttl_sekunden: int,
    bestehende_locks: list[WorkflowLock],
    jetzt: datetime | None = None,
) -> LockAkquisitionsErgebnis:
    """
    Versucht einen Lock zu akquirieren.

    Logik:
    1. Bestehende aktive (nicht abgelaufene) Locks auf der Ressource pruefen
    2. Bei Konflikt -> erfolg=False mit Konflikttyp
    3. LESEN-Locks blockieren sich gegenseitig nicht
    4. Kein Konflikt -> erfolg=True
    """
    ts = jetzt or datetime.utcnow()

    neuer_lock = WorkflowLock(
        lock_id=lock_id,
        ressource_id=ressource_id,
        inhaber_id=inhaber_id,
        lock_typ=lock_typ,
        status=LockStatus.AKTIV,
        version=version,
        ttl_sekunden=ttl_sekunden,
        erstellt_am=ts,
    )

    aktive = [
        line_item for line_item in bestehende_locks
        if line_item.ressource_id == ressource_id
        and line_item.ist_aktiv
        and not line_item.ist_abgelaufen(ts)
        and line_item.inhaber_id != inhaber_id
    ]

    # LESEN-Locks blockieren sich nicht gegenseitig
    if lock_typ == LockTyp.LESEN:
        aktive = [line_item for line_item in aktive if line_item.lock_typ != LockTyp.LESEN]

    for bestehend in aktive:
        konflikt = neuer_lock.pruefe_konflikt(bestehend)
        if konflikt is not None:
            return LockAkquisitionsErgebnis(
                lock_id=lock_id,
                ressource_id=ressource_id,
                inhaber_id=inhaber_id,
                lock_typ=lock_typ,
                erfolg=False,
                konflikt_typ=konflikt,
                konflikt_lock_id=bestehend.lock_id,
                begruendung=f"Konflikt mit Lock {bestehend.lock_id} ({konflikt.value})",
                versucht_am=ts,
            )

    return LockAkquisitionsErgebnis(
        lock_id=lock_id,
        ressource_id=ressource_id,
        inhaber_id=inhaber_id,
        lock_typ=lock_typ,
        erfolg=True,
        begruendung="Lock erfolgreich akquiriert.",
        versucht_am=ts,
    )


def get_default_locks(jetzt: datetime | None = None) -> list[WorkflowLock]:
    """Gibt 5 Standard-Locks zurueck."""
    ts = jetzt or datetime(2026, 3, 15, 10, 0)
    return [
        WorkflowLock(
            lock_id="LK-001",
            ressource_id="kontrakt:K-2026-001",
            inhaber_id="mueller",
            lock_typ=LockTyp.SCHREIBEN,
            status=LockStatus.AKTIV,
            version=3,
            ttl_sekunden=300,
            erstellt_am=ts,
        ),
        WorkflowLock(
            lock_id="LK-002",
            ressource_id="settlement:S-2026-042",
            inhaber_id="schneider",
            lock_typ=LockTyp.LESEN,
            status=LockStatus.AKTIV,
            version=1,
            ttl_sekunden=600,
            erstellt_am=ts,
        ),
        WorkflowLock(
            lock_id="LK-003",
            ressource_id="settlement:S-2026-042",
            inhaber_id="fischer",
            lock_typ=LockTyp.LESEN,
            status=LockStatus.AKTIV,
            version=1,
            ttl_sekunden=600,
            erstellt_am=ts,
        ),
        WorkflowLock(
            lock_id="LK-004",
            ressource_id="ap-rechnung:R-2026-099",
            inhaber_id="weber",
            lock_typ=LockTyp.OPTIMISTISCH,
            status=LockStatus.FREIGEGEBEN,
            version=2,
            ttl_sekunden=120,
            erstellt_am=ts,
        ),
        WorkflowLock(
            lock_id="LK-005",
            ressource_id="kontrakt:K-2026-007",
            inhaber_id="mueller",
            lock_typ=LockTyp.SCHREIBEN,
            status=LockStatus.ABGELAUFEN,
            version=1,
            ttl_sekunden=60,
            erstellt_am=ts,
        ),
    ]
