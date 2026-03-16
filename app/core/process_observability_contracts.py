"""
Process Observability Contracts — Wave 57
Spans, Traces, Health Checks für den Process Kernel.

Schichtregeln:
- Kein Import aus app/api/ oder app/infrastructure/
- Nur Stdlib + eigene Core-Module
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from datetime import datetime, timedelta


class SpanStatus(str, Enum):
    LAUFEND = "LAUFEND"
    ERFOLGREICH = "ERFOLGREICH"
    FEHLER = "FEHLER"
    ABGEBROCHEN = "ABGEBROCHEN"


class HealthStatus(str, Enum):
    GESUND = "GESUND"
    DEGRADIERT = "DEGRADIERT"
    KRANK = "KRANK"
    UNBEKANNT = "UNBEKANNT"


class MetrikEinheit(str, Enum):
    MILLISEKUNDEN = "MILLISEKUNDEN"
    ANFRAGEN_PRO_SEKUNDE = "ANFRAGEN_PRO_SEKUNDE"
    PROZENT = "PROZENT"
    BYTES = "BYTES"
    ANZAHL = "ANZAHL"


@dataclass
class ObservabilitySpan:
    span_id: str
    trace_id: str
    operation_name: str
    status: SpanStatus = SpanStatus.LAUFEND
    beginn_am: datetime = field(default_factory=datetime.utcnow)
    ende_am: Optional[datetime] = None
    parent_span_id: Optional[str] = None
    tags: dict = field(default_factory=dict)
    fehler_nachricht: str = ""

    def dauer_ms(self) -> Optional[float]:
        """Returns duration in milliseconds, None if still running."""
        if self.ende_am is None:
            return None
        return (self.ende_am - self.beginn_am).total_seconds() * 1000

    def ist_root_span(self) -> bool:
        return self.parent_span_id is None


@dataclass
class Trace:
    trace_id: str
    spans: list = field(default_factory=list)  # list[ObservabilitySpan]

    def root_span(self) -> Optional[object]:
        """Returns the span with parent_span_id=None, or None if not found."""
        wurzeln = [s for s in self.spans if s.ist_root_span()]
        return wurzeln[0] if wurzeln else None

    def gesamtdauer_ms(self) -> Optional[float]:
        """Sum of all span durations. None if any span is still running."""
        dauern = [s.dauer_ms() for s in self.spans]
        if any(d is None for d in dauern):
            return None
        return sum(dauern)

    def fehlerhafte_spans(self) -> list:
        """Returns spans with status FEHLER."""
        return [s for s in self.spans if s.status == SpanStatus.FEHLER]

    def erfolgsrate_pct(self) -> float:
        """ERFOLGREICH / total * 100. 100.0 for empty."""
        if not self.spans:
            return 100.0
        erfolgreich = sum(1 for s in self.spans if s.status == SpanStatus.ERFOLGREICH)
        return (erfolgreich / len(self.spans)) * 100


@dataclass
class HealthCheck:
    check_id: str
    komponente: str
    status: HealthStatus
    nachricht: str = ""
    geprueft_am: datetime = field(default_factory=datetime.utcnow)
    antwortzeit_ms: float = 0.0


@dataclass
class SystemHealthReport:
    report_id: str
    checks: list = field(default_factory=list)  # list[HealthCheck]
    erstellt_am: datetime = field(default_factory=datetime.utcnow)

    def gesamtstatus(self) -> HealthStatus:
        """
        KRANK if any check is KRANK.
        DEGRADIERT if any check is DEGRADIERT (and none KRANK).
        UNBEKANNT if any check is UNBEKANNT (and none KRANK/DEGRADIERT).
        GESUND if all are GESUND.
        GESUND for empty.
        """
        if not self.checks:
            return HealthStatus.GESUND
        stati = [c.status for c in self.checks]
        if HealthStatus.KRANK in stati:
            return HealthStatus.KRANK
        if HealthStatus.DEGRADIERT in stati:
            return HealthStatus.DEGRADIERT
        if HealthStatus.UNBEKANNT in stati:
            return HealthStatus.UNBEKANNT
        return HealthStatus.GESUND

    def gesunde_komponenten(self) -> list:
        return [c for c in self.checks if c.status == HealthStatus.GESUND]


def get_default_traces() -> list:
    now = datetime(2026, 3, 16, 10, 0, 0)

    # Trace 1: successful kontrakt workflow
    t1 = Trace("TRACE-001")
    t1.spans = [
        ObservabilitySpan("SP-001", "TRACE-001", "kontrakt.erfassen", SpanStatus.ERFOLGREICH,
                          now, now + timedelta(milliseconds=120), None, {"tenant": "A"}),
        ObservabilitySpan("SP-002", "TRACE-001", "kontrakt.validieren", SpanStatus.ERFOLGREICH,
                          now + timedelta(milliseconds=120), now + timedelta(milliseconds=250),
                          "SP-001", {"tenant": "A"}),
        ObservabilitySpan("SP-003", "TRACE-001", "kontrakt.speichern", SpanStatus.ERFOLGREICH,
                          now + timedelta(milliseconds=250), now + timedelta(milliseconds=400),
                          "SP-002", {"tenant": "A"}),
    ]

    # Trace 2: error trace
    t2 = Trace("TRACE-002")
    t2.spans = [
        ObservabilitySpan("SP-004", "TRACE-002", "settlement.berechnen", SpanStatus.ERFOLGREICH,
                          now, now + timedelta(milliseconds=80), None, {}),
        ObservabilitySpan("SP-005", "TRACE-002", "settlement.buchen", SpanStatus.FEHLER,
                          now + timedelta(milliseconds=80), now + timedelta(milliseconds=200),
                          "SP-004", {}, "DB-Verbindungsfehler"),
    ]

    return [t1, t2]


def get_default_health_report() -> SystemHealthReport:
    now = datetime(2026, 3, 16, 10, 0, 0)
    report = SystemHealthReport("HR-001", erstellt_am=now)
    report.checks = [
        HealthCheck("HC-001", "Datenbank", HealthStatus.GESUND, "OK", now, 12.5),
        HealthCheck("HC-002", "Redis-Cache", HealthStatus.GESUND, "OK", now, 1.2),
        HealthCheck("HC-003", "NATS-JetStream", HealthStatus.DEGRADIERT, "Hohe Latenz", now, 250.0),
        HealthCheck("HC-004", "EDI-Gateway", HealthStatus.UNBEKANNT, "Timeout", now, 5000.0),
        HealthCheck("HC-005", "Keycloak-OIDC", HealthStatus.GESUND, "OK", now, 45.0),
    ]
    return report
