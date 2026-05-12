from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from datetime import datetime


class CircuitBreakerZustand(str, Enum):
    GESCHLOSSEN = "GESCHLOSSEN"    # Normal operation, requests pass through
    OFFEN = "OFFEN"                # Failing, requests blocked
    HALB_OFFEN = "HALB_OFFEN"      # Testing recovery, limited requests


class AufrufErgebnis(str, Enum):
    ERFOLG = "ERFOLG"
    FEHLER = "FEHLER"
    ZEITUEBERSCHREITUNG = "ZEITUEBERSCHREITUNG"


@dataclass
class CircuitBreakerKonfiguration:
    breaker_id: str
    service_name: str
    fehler_schwellwert: int        # Number of failures before opening (e.g. 5)
    wiederherstellungs_timeout_sekunden: int  # Time before trying HALB_OFFEN (e.g. 60)
    halb_offen_max_anfragen: int   # Max requests in HALB_OFFEN state (e.g. 3)
    beschreibung: str = ""


@dataclass
class CircuitBreakerZustandsRecord:
    breaker_id: str
    zustand: CircuitBreakerZustand = CircuitBreakerZustand.GESCHLOSSEN
    fehler_zaehler: int = 0
    erfolg_zaehler_halb_offen: int = 0
    letzter_fehler_am: Optional[datetime] = None
    zustand_geaendert_am: datetime = field(default_factory=datetime.utcnow)

    def kann_anfrage_durchlassen(self, config: CircuitBreakerKonfiguration, jetzt: datetime) -> bool:
        """
        GESCHLOSSEN -> True always.
        OFFEN -> True only if wiederherstellungs_timeout expired (-> transitions to HALB_OFFEN logic externally).
        HALB_OFFEN -> True only if erfolg_zaehler_halb_offen < halb_offen_max_anfragen.
        """
        if self.zustand == CircuitBreakerZustand.GESCHLOSSEN:
            return True
        elif self.zustand == CircuitBreakerZustand.OFFEN:
            if self.letzter_fehler_am is None:
                return False
            elapsed = (jetzt - self.letzter_fehler_am).total_seconds()
            return elapsed >= config.wiederherstellungs_timeout_sekunden
        else:  # HALB_OFFEN
            return self.erfolg_zaehler_halb_offen < config.halb_offen_max_anfragen

    def verarbeite_ergebnis(self, ergebnis: AufrufErgebnis, config: CircuitBreakerKonfiguration, jetzt: datetime) -> 'CircuitBreakerZustandsRecord':
        """
        Returns new state record (immutable update pattern).
        GESCHLOSSEN + FEHLER/ZEITUEBERSCHREITUNG: increment fehler_zaehler; if >= schwellwert -> OFFEN
        GESCHLOSSEN + ERFOLG: reset fehler_zaehler to 0
        OFFEN + any: stays OFFEN (use kann_anfrage_durchlassen to check transition)
        HALB_OFFEN + ERFOLG: increment erfolg_zaehler; if >= halb_offen_max -> GESCHLOSSEN
        HALB_OFFEN + FEHLER/ZEITUEBERSCHREITUNG: -> OFFEN, reset erfolg_zaehler
        """
        import dataclasses
        rec = dataclasses.replace(self)

        if self.zustand == CircuitBreakerZustand.GESCHLOSSEN:
            if ergebnis in (AufrufErgebnis.FEHLER, AufrufErgebnis.ZEITUEBERSCHREITUNG):
                rec.fehler_zaehler += 1
                rec.letzter_fehler_am = jetzt
                if rec.fehler_zaehler >= config.fehler_schwellwert:
                    rec.zustand = CircuitBreakerZustand.OFFEN
                    rec.zustand_geaendert_am = jetzt
            else:  # ERFOLG
                rec.fehler_zaehler = 0
        elif self.zustand == CircuitBreakerZustand.HALB_OFFEN:
            if ergebnis == AufrufErgebnis.ERFOLG:
                rec.erfolg_zaehler_halb_offen += 1
                if rec.erfolg_zaehler_halb_offen >= config.halb_offen_max_anfragen:
                    rec.zustand = CircuitBreakerZustand.GESCHLOSSEN
                    rec.fehler_zaehler = 0
                    rec.erfolg_zaehler_halb_offen = 0
                    rec.zustand_geaendert_am = jetzt
            else:
                rec.zustand = CircuitBreakerZustand.OFFEN
                rec.letzter_fehler_am = jetzt
                rec.erfolg_zaehler_halb_offen = 0
                rec.zustand_geaendert_am = jetzt
        # OFFEN: no state change from results
        return rec


def get_default_circuit_breaker_konfigurationen() -> list:
    """Returns 5 default configurations."""
    return [
        CircuitBreakerKonfiguration("CB-001", "ERP-Settlement-API", 5, 60, 3, "Settlement-Service"),
        CircuitBreakerKonfiguration("CB-002", "EDI-Partner-Gateway", 3, 120, 2, "EDI Gateway"),
        CircuitBreakerKonfiguration("CB-003", "Marktdaten-Feed", 10, 30, 5, "Market data feed"),
        CircuitBreakerKonfiguration("CB-004", "OIDC-Token-Endpoint", 3, 30, 2, "Auth service"),
        CircuitBreakerKonfiguration("CB-005", "Lager-Datenbank", 5, 10, 3, "Database connection"),
    ]
