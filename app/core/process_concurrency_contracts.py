from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from datetime import datetime, timedelta


class KonkurrenzModus(str, Enum):
    MUTEX = "MUTEX"                 # Only 1 at a time
    SEMAPHORE = "SEMAPHORE"         # Up to N concurrent
    READ_WRITE = "READ_WRITE"       # Multiple reads OR one write
    SINGLE_WRITER = "SINGLE_WRITER" # Only 1 writer, multiple readers


class AusfuehrungsSlotStatus(str, Enum):
    FREI = "FREI"
    BELEGT = "BELEGT"
    RESERVIERT = "RESERVIERT"


@dataclass
class KonkurrenzRegel:
    regel_id: str
    ressource_typ: str          # e.g. "settlement_run", "batch_import"
    modus: KonkurrenzModus
    max_gleichzeitig: int       # ignored for MUTEX (always 1)
    timeout_sekunden: int = 300

    def effektives_limit(self) -> int:
        """MUTEX → 1; others → max_gleichzeitig."""
        return 1 if self.modus == KonkurrenzModus.MUTEX else self.max_gleichzeitig


@dataclass
class AusfuehrungsSlot:
    slot_id: str
    regel_id: str
    inhaber_id: str
    status: AusfuehrungsSlotStatus = AusfuehrungsSlotStatus.FREI
    belegt_seit: Optional[datetime] = None
    ablauf_am: Optional[datetime] = None

    def ist_abgelaufen(self, jetzt: datetime) -> bool:
        """True if ablauf_am is set and jetzt >= ablauf_am."""
        return self.ablauf_am is not None and jetzt >= self.ablauf_am

    def ist_verfuegbar(self, jetzt: datetime) -> bool:
        """FREI or (BELEGT but expired)."""
        return self.status == AusfuehrungsSlotStatus.FREI or (
            self.status == AusfuehrungsSlotStatus.BELEGT and self.ist_abgelaufen(jetzt)
        )


@dataclass
class KonkurrenzWaechter:
    waechter_id: str
    regel: KonkurrenzRegel
    slots: list = field(default_factory=list)   # list[AusfuehrungsSlot]

    def belegte_slots(self, jetzt: datetime) -> list:
        """Non-expired BELEGT slots."""
        return [s for s in self.slots
                if s.status == AusfuehrungsSlotStatus.BELEGT and not s.ist_abgelaufen(jetzt)]

    def kann_ausfuehren(self, jetzt: datetime) -> bool:
        """True if len(belegte_slots) < effektives_limit."""
        return len(self.belegte_slots(jetzt)) < self.regel.effektives_limit()

    def auslastung_pct(self, jetzt: datetime) -> float:
        """belegte_slots / effektives_limit * 100."""
        limit = self.regel.effektives_limit()
        if limit == 0:
            return 0.0
        return (len(self.belegte_slots(jetzt)) / limit) * 100


def get_default_konkurrenz_waechter() -> list:
    now = datetime(2026, 3, 16, 10, 0, 0)

    # Waechter 1: MUTEX settlement_run — 1 slot belegt, 1 slot frei → cannot execute
    w1 = KonkurrenzWaechter("KW-001", KonkurrenzRegel("KR-001", "settlement_run", KonkurrenzModus.MUTEX, 1, 300))
    w1.slots = [
        AusfuehrungsSlot("AS-001", "KR-001", "WI-S-001", AusfuehrungsSlotStatus.BELEGT,
                          now - timedelta(minutes=5), now + timedelta(minutes=295)),
    ]

    # Waechter 2: SEMAPHORE batch_import max=3 — 2 belegt → kann ausführen
    w2 = KonkurrenzWaechter("KW-002", KonkurrenzRegel("KR-002", "batch_import", KonkurrenzModus.SEMAPHORE, 3, 600))
    w2.slots = [
        AusfuehrungsSlot("AS-002", "KR-002", "WI-B-001", AusfuehrungsSlotStatus.BELEGT,
                          now - timedelta(minutes=10), now + timedelta(minutes=590)),
        AusfuehrungsSlot("AS-003", "KR-002", "WI-B-002", AusfuehrungsSlotStatus.BELEGT,
                          now - timedelta(minutes=5), now + timedelta(minutes=595)),
        AusfuehrungsSlot("AS-004", "KR-002", "WI-B-003", AusfuehrungsSlotStatus.BELEGT,
                          now - timedelta(hours=2), now - timedelta(minutes=10)),  # expired
    ]

    return [w1, w2]
