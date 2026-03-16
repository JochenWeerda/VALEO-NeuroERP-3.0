from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from datetime import datetime, timedelta
import math


class RetryStrategie(str, Enum):
    KEIN_RETRY = "KEIN_RETRY"
    FESTER_INTERVALL = "FESTER_INTERVALL"                 # fixed delay
    LINEARES_BACKOFF = "LINEARES_BACKOFF"                 # delay * versuch_nummer
    EXPONENTIELLES_BACKOFF = "EXPONENTIELLES_BACKOFF"     # basis_sekunden * 2^(versuch-1)
    JITTER = "JITTER"                                     # exponential + random jitter (deterministic: +50%)


class RetryStatus(str, Enum):
    AUSSTEHEND = "AUSSTEHEND"
    LAUFEND = "LAUFEND"
    ERFOLGREICH = "ERFOLGREICH"
    ERSCHOEPFT = "ERSCHOEPFT"     # max retries reached
    AUFGEGEBEN = "AUFGEGEBEN"     # manually cancelled


@dataclass
class RetryRegel:
    regel_id: str
    strategie: RetryStrategie
    max_versuche: int             # total attempts including first (e.g. 3 = 1 original + 2 retries)
    basis_sekunden: float         # base delay in seconds
    max_verzoegerung_sekunden: float = 300.0   # cap for backoff
    beschreibung: str = ""

    def berechne_verzoegerung(self, versuch_nummer: int) -> float:
        """
        versuch_nummer: 1-based (1 = first retry after original failure).
        KEIN_RETRY → 0.0
        FESTER_INTERVALL → basis_sekunden
        LINEARES_BACKOFF → basis_sekunden * versuch_nummer
        EXPONENTIELLES_BACKOFF → min(basis_sekunden * 2^(versuch_nummer-1), max_verzoegerung_sekunden)
        JITTER → min(basis_sekunden * 2^(versuch_nummer-1) * 1.5, max_verzoegerung_sekunden)
        """
        if self.strategie == RetryStrategie.KEIN_RETRY:
            return 0.0
        elif self.strategie == RetryStrategie.FESTER_INTERVALL:
            return self.basis_sekunden
        elif self.strategie == RetryStrategie.LINEARES_BACKOFF:
            return min(self.basis_sekunden * versuch_nummer, self.max_verzoegerung_sekunden)
        elif self.strategie == RetryStrategie.EXPONENTIELLES_BACKOFF:
            return min(self.basis_sekunden * (2 ** (versuch_nummer - 1)), self.max_verzoegerung_sekunden)
        else:  # JITTER
            return min(self.basis_sekunden * (2 ** (versuch_nummer - 1)) * 1.5, self.max_verzoegerung_sekunden)


@dataclass
class RetryZustand:
    zustand_id: str
    regel_id: str
    befehl_typ: str
    status: RetryStatus = RetryStatus.AUSSTEHEND
    aktueller_versuch: int = 0    # 0 = not yet attempted
    letzter_fehler: str = ""
    naechster_versuch_am: Optional[datetime] = None

    def kann_nochmal_versuchen(self, regel: RetryRegel) -> bool:
        """True if aktueller_versuch < max_versuche and status not ERFOLGREICH/ERSCHOEPFT/AUFGEGEBEN."""
        if self.status in (RetryStatus.ERFOLGREICH, RetryStatus.ERSCHOEPFT, RetryStatus.AUFGEGEBEN):
            return False
        return self.aktueller_versuch < regel.max_versuche

    def naechsten_versuch_planen(self, regel: RetryRegel, jetzt: datetime) -> 'RetryZustand':
        """
        Returns new RetryZustand with incremented aktueller_versuch,
        status=LAUFEND, naechster_versuch_am=jetzt + delay.
        If would exceed max_versuche → status=ERSCHOEPFT instead.
        """
        import dataclasses
        neuer_versuch = self.aktueller_versuch + 1
        if neuer_versuch > regel.max_versuche:
            return dataclasses.replace(self, status=RetryStatus.ERSCHOEPFT)
        verzoegerung = regel.berechne_verzoegerung(neuer_versuch)
        naechster = jetzt + timedelta(seconds=verzoegerung)
        return dataclasses.replace(self, aktueller_versuch=neuer_versuch,
                                   status=RetryStatus.LAUFEND, naechster_versuch_am=naechster)


def get_default_retry_regeln() -> list:
    return [
        RetryRegel("RR-001", RetryStrategie.EXPONENTIELLES_BACKOFF, 3, 5.0, 300.0, "Standard API-Retry"),
        RetryRegel("RR-002", RetryStrategie.FESTER_INTERVALL, 5, 10.0, 300.0, "DB-Verbindungs-Retry"),
        RetryRegel("RR-003", RetryStrategie.LINEARES_BACKOFF, 4, 15.0, 300.0, "EDI-Partner-Retry"),
        RetryRegel("RR-004", RetryStrategie.JITTER, 3, 2.0, 60.0, "Concurrent-Write-Retry"),
        RetryRegel("RR-005", RetryStrategie.KEIN_RETRY, 1, 0.0, 0.0, "Kritische Einmal-Aktionen"),
    ]
