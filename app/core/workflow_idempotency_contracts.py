from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Any
from datetime import datetime, timedelta

class IdempotenzStatus(str, Enum):
    NEU = "NEU"                     # First time seen
    DUPLIKAT = "DUPLIKAT"           # Already processed successfully
    VERARBEITUNG = "VERARBEITUNG"   # Currently being processed
    FEHLGESCHLAGEN = "FEHLGESCHLAGEN"  # Previous attempt failed (may retry)
    ABGELAUFEN = "ABGELAUFEN"       # TTL expired

class DeduplizierungsStrategie(str, Enum):
    STRIKTE_EINMALIGKEIT = "STRIKTE_EINMALIGKEIT"   # Never re-process
    WIEDERHOLUNG_BEI_FEHLER = "WIEDERHOLUNG_BEI_FEHLER"  # Retry on FEHLGESCHLAGEN
    ZEITFENSTER = "ZEITFENSTER"     # Deduplicate within TTL window only

@dataclass
class IdempotenzEintrag:
    schluessel: str                 # Idempotency key
    befehl_typ: str                 # e.g. "kontrakt_erstellen"
    tenant_id: str
    status: IdempotenzStatus = IdempotenzStatus.NEU
    ergebnis_nutzlast: dict = field(default_factory=dict)
    erstellt_am: datetime = field(default_factory=datetime.utcnow)
    verarbeitet_am: Optional[datetime] = None
    ttl_sekunden: int = 86400       # 24 hours default

    def ist_abgelaufen(self, jetzt: datetime) -> bool:
        return (jetzt - self.erstellt_am).total_seconds() > self.ttl_sekunden

    def aktueller_status(self, jetzt: datetime) -> IdempotenzStatus:
        """Returns ABGELAUFEN if TTL exceeded, else current status."""
        if self.ist_abgelaufen(jetzt):
            return IdempotenzStatus.ABGELAUFEN
        return self.status

@dataclass
class IdempotenzPruefung:
    """Result of checking whether a command should be processed."""
    schluessel: str
    soll_verarbeiten: bool          # True if command should be processed
    status: IdempotenzStatus
    gespeichertes_ergebnis: Optional[dict] = None   # Set if DUPLIKAT

def pruefe_idempotenz(
    schluessel: str,
    bekannte_eintraege: list,       # list[IdempotenzEintrag]
    strategie: DeduplizierungsStrategie,
    jetzt: datetime,
) -> IdempotenzPruefung:
    """
    Looks up schluessel in bekannte_eintraege.
    If not found → NEU, soll_verarbeiten=True.
    If found:
      - STRIKTE_EINMALIGKEIT + DUPLIKAT → soll_verarbeiten=False, return stored result
      - STRIKTE_EINMALIGKEIT + VERARBEITUNG → soll_verarbeiten=False
      - STRIKTE_EINMALIGKEIT + FEHLGESCHLAGEN → soll_verarbeiten=False
      - WIEDERHOLUNG_BEI_FEHLER + FEHLGESCHLAGEN → soll_verarbeiten=True
      - WIEDERHOLUNG_BEI_FEHLER + DUPLIKAT → soll_verarbeiten=False
      - ZEITFENSTER + ABGELAUFEN → soll_verarbeiten=True (treat as new)
      - ZEITFENSTER + DUPLIKAT → soll_verarbeiten=False
      - ABGELAUFEN (any strategy) → soll_verarbeiten=True
    """
    eintrag = next((e for e in bekannte_eintraege if e.schluessel == schluessel), None)
    if eintrag is None:
        return IdempotenzPruefung(schluessel, True, IdempotenzStatus.NEU)

    aktuell = eintrag.aktueller_status(jetzt)

    if aktuell == IdempotenzStatus.ABGELAUFEN:
        return IdempotenzPruefung(schluessel, True, IdempotenzStatus.ABGELAUFEN)

    if strategie == DeduplizierungsStrategie.STRIKTE_EINMALIGKEIT:
        if aktuell == IdempotenzStatus.DUPLIKAT:
            return IdempotenzPruefung(schluessel, False, IdempotenzStatus.DUPLIKAT, eintrag.ergebnis_nutzlast)
        return IdempotenzPruefung(schluessel, False, aktuell)

    elif strategie == DeduplizierungsStrategie.WIEDERHOLUNG_BEI_FEHLER:
        if aktuell == IdempotenzStatus.FEHLGESCHLAGEN:
            return IdempotenzPruefung(schluessel, True, IdempotenzStatus.FEHLGESCHLAGEN)
        if aktuell == IdempotenzStatus.DUPLIKAT:
            return IdempotenzPruefung(schluessel, False, IdempotenzStatus.DUPLIKAT, eintrag.ergebnis_nutzlast)
        return IdempotenzPruefung(schluessel, False, aktuell)

    else:  # ZEITFENSTER
        if aktuell == IdempotenzStatus.DUPLIKAT:
            return IdempotenzPruefung(schluessel, False, IdempotenzStatus.DUPLIKAT, eintrag.ergebnis_nutzlast)
        return IdempotenzPruefung(schluessel, True, aktuell)

def get_default_idempotenz_eintraege() -> list:
    """Returns 5 default IdempotenzEintrag instances."""
    now = datetime(2026, 3, 16, 10, 0, 0)
    return [
        IdempotenzEintrag("KEY-001", "kontrakt_erstellen", "TENANT-A", IdempotenzStatus.DUPLIKAT,
                          {"kontrakt_id": "K-001"}, now, now, 86400),
        IdempotenzEintrag("KEY-002", "settlement_ausfuehren", "TENANT-A", IdempotenzStatus.VERARBEITUNG,
                          {}, now, None, 3600),
        IdempotenzEintrag("KEY-003", "rechnung_buchen", "TENANT-B", IdempotenzStatus.FEHLGESCHLAGEN,
                          {"fehler": "DB-Fehler"}, now, now, 86400),
        IdempotenzEintrag("KEY-004", "zahlung_anweisen", "TENANT-B", IdempotenzStatus.NEU,
                          {}, now, None, 86400),
        IdempotenzEintrag("KEY-005-ALT", "alte_aktion", "TENANT-A", IdempotenzStatus.DUPLIKAT,
                          {"alt": True}, now - timedelta(days=2), None, 86400),  # expired
    ]
