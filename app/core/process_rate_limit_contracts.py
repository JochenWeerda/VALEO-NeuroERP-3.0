from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

class RateLimitFenster(str, Enum):
    SEKUNDE = "SEKUNDE"
    MINUTE = "MINUTE"
    STUNDE = "STUNDE"
    TAG = "TAG"

class RateLimitErgebnis(str, Enum):
    ERLAUBT = "ERLAUBT"
    GEDROSSELT = "GEDROSSELT"       # Soft limit: allowed but throttled
    BLOCKIERT = "BLOCKIERT"         # Hard limit: rejected

class RateLimitGranularitaet(str, Enum):
    TENANT = "TENANT"
    BENUTZER = "BENUTZER"
    ENDPUNKT = "ENDPUNKT"
    GLOBAL = "GLOBAL"

@dataclass
class RateLimitRegel:
    regel_id: str
    granularitaet: RateLimitGranularitaet
    fenster: RateLimitFenster
    max_anfragen: int           # Hard limit → BLOCKIERT
    weich_limit: int            # Soft limit → GEDROSSELT (must be <= max_anfragen)
    beschreibung: str = ""

    def fenster_sekunden(self) -> int:
        """Returns window size in seconds."""
        return {
            RateLimitFenster.SEKUNDE: 1,
            RateLimitFenster.MINUTE: 60,
            RateLimitFenster.STUNDE: 3600,
            RateLimitFenster.TAG: 86400,
        }[self.fenster]

@dataclass
class RateLimitZaehler:
    zaehler_id: str             # e.g. "{regel_id}:{tenant_id}:{benutzer_id}"
    regel_id: str
    anfragen_im_fenster: int = 0
    fenster_beginn: datetime = field(default_factory=datetime.utcnow)

    def ist_fenster_abgelaufen(self, jetzt: datetime, fenster_sekunden: int) -> bool:
        return (jetzt - self.fenster_beginn).total_seconds() >= fenster_sekunden

    def pruefe_und_inkrementiere(self, regel: RateLimitRegel, jetzt: datetime) -> tuple:
        """
        Returns (RateLimitErgebnis, updated_zaehler).
        If window expired: reset counter to 1, new window starts at jetzt.
        If anfragen_im_fenster + 1 > max_anfragen → BLOCKIERT (do not increment).
        If anfragen_im_fenster + 1 > weich_limit → GEDROSSELT (increment).
        Otherwise → ERLAUBT (increment).
        """
        import dataclasses
        fenster_sek = regel.fenster_sekunden()
        if self.ist_fenster_abgelaufen(jetzt, fenster_sek):
            neuer = dataclasses.replace(self, anfragen_im_fenster=1, fenster_beginn=jetzt)
            return (RateLimitErgebnis.ERLAUBT, neuer)
        neue_anzahl = self.anfragen_im_fenster + 1
        if neue_anzahl > regel.max_anfragen:
            return (RateLimitErgebnis.BLOCKIERT, self)
        ergebnis = RateLimitErgebnis.GEDROSSELT if neue_anzahl > regel.weich_limit else RateLimitErgebnis.ERLAUBT
        neuer = dataclasses.replace(self, anfragen_im_fenster=neue_anzahl)
        return (ergebnis, neuer)

def get_default_rate_limit_regeln() -> list:
    """Returns 5 default RateLimitRegel instances."""
    return [
        RateLimitRegel("RL-001", RateLimitGranularitaet.TENANT, RateLimitFenster.MINUTE, 1000, 800, "API-Anfragen pro Tenant/Minute"),
        RateLimitRegel("RL-002", RateLimitGranularitaet.BENUTZER, RateLimitFenster.MINUTE, 100, 80, "API-Anfragen pro Benutzer/Minute"),
        RateLimitRegel("RL-003", RateLimitGranularitaet.ENDPUNKT, RateLimitFenster.SEKUNDE, 50, 40, "Burst-Schutz pro Endpunkt/Sekunde"),
        RateLimitRegel("RL-004", RateLimitGranularitaet.GLOBAL, RateLimitFenster.STUNDE, 100000, 80000, "Globales Stundenlimit"),
        RateLimitRegel("RL-005", RateLimitGranularitaet.TENANT, RateLimitFenster.TAG, 50000, 40000, "Tageslimit pro Tenant"),
    ]
