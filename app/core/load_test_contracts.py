"""
load_test_contracts.py — Lasttest-SLA-Contracts Erntepeak (Wave 87, Gap 037)

WICHTIG: Diese Datei definiert NUR das Datenmodell und die SLA-Schwellwerte.
Sie führt KEINE echten Lasttests durch. Die tatsächliche Lastgenerierung
erfolgt durch:
  - load-tests/erntepeak-load-test.js  (k6, echter HTTP-Traffic)
  - load-tests/locustfile.py           (Locust, Python-basiert)

Workflow:
  1. k6/Locust generiert realen HTTP-Traffic gegen den laufenden Stack
  2. Messwerte werden als LasttestErgebnis-Objekte instanziiert
  3. evaluate_erntepeak_sla() prüft gegen ErntepeakSLAContract
  4. Ergebnis: kpi_erfuellt = True/False

Gap 037: 500 gleichzeitige User stabil — p95 Response < 2s, Error Rate < 1%
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class LasttestSzenario(str, Enum):
    """Vordefinierte Lasttest-Szenarien."""
    NORMALBETRIEB   = "NORMALBETRIEB"    # 50 User, Basislast
    ERNTEPEAK       = "ERNTEPEAK"        # 500 User, Kampagnenbetrieb
    STRESSTEST      = "STRESSTEST"       # 1000+ User, Überlasttest
    SOAK_TEST       = "SOAK_TEST"        # 200 User, 4h Dauerlauf
    SPIKE_TEST      = "SPIKE_TEST"       # Plötzlicher Lastanstieg 50→500


class LasttestStatus(str, Enum):
    """Status eines Lasttests."""
    GEPLANT      = "GEPLANT"
    LAEUFT       = "LAEUFT"
    ABGESCHLOSSEN = "ABGESCHLOSSEN"
    ABGEBROCHEN  = "ABGEBROCHEN"
    FEHLGESCHLAGEN = "FEHLGESCHLAGEN"


class SLAErfuellungsGrad(str, Enum):
    """Erfüllungsgrad eines SLA-Vertrags."""
    ERFUELLT     = "ERFUELLT"
    GRENZWERTIG  = "GRENZWERTIG"   # Innerhalb ±10% des Ziels
    VERLETZT     = "VERLETZT"
    NICHT_MESSBAR = "NICHT_MESSBAR"  # Zu wenige Stichproben


class EndpointKategorie(str, Enum):
    """Kategorie eines zu testenden Endpoints."""
    DASHBOARD    = "DASHBOARD"     # p95 < 250ms (Gap 033)
    ANNAHME      = "ANNAHME"       # Wareneingang, Wiegeschein
    CONTROLLING  = "CONTROLLING"   # KPIs, Timeseries
    SETTLEMENT   = "SETTLEMENT"    # Abrechnung
    SEARCH       = "SEARCH"        # Volltextsuche
    AUTH         = "AUTH"          # Login, Token-Refresh


# ---------------------------------------------------------------------------
# Lasttest-Konfiguration
# ---------------------------------------------------------------------------

@dataclass
class LasttestKonfiguration:
    """
    Konfiguration eines Lasttests.

    Definiert Szenario, Nutzeranzahl, Dauer und Ramp-Up.
    """
    szenario: LasttestSzenario
    gleichzeitige_user: int
    dauer_sekunden: int
    ramp_up_sekunden: int = 60      # Zeit bis zur Volllast
    think_time_ms: int = 1000       # Pause zwischen Requests pro User
    tenant_count: int = 1           # Anzahl simultaner Tenants

    def __post_init__(self) -> None:
        if self.gleichzeitige_user <= 0:
            raise ValueError("gleichzeitige_user muss > 0 sein")
        if self.dauer_sekunden <= 0:
            raise ValueError("dauer_sekunden muss > 0 sein")
        if self.ramp_up_sekunden < 0:
            raise ValueError("ramp_up_sekunden darf nicht negativ sein")

    @property
    def requests_pro_sekunde_theoretisch(self) -> float:
        """Theoretischer Durchsatz ohne Think-Time."""
        if self.think_time_ms <= 0:
            return float(self.gleichzeitige_user)
        return self.gleichzeitige_user / (self.think_time_ms / 1000)

    def as_dict(self) -> dict:
        return {
            "szenario": self.szenario.value,
            "gleichzeitige_user": self.gleichzeitige_user,
            "dauer_sekunden": self.dauer_sekunden,
            "ramp_up_sekunden": self.ramp_up_sekunden,
            "think_time_ms": self.think_time_ms,
            "tenant_count": self.tenant_count,
            "requests_pro_sekunde_theoretisch": round(self.requests_pro_sekunde_theoretisch, 1),
        }


# ---------------------------------------------------------------------------
# Lasttest-Ergebnis
# ---------------------------------------------------------------------------

@dataclass
class EndpointLasttestErgebnis:
    """Messergebnis für einen einzelnen Endpoint."""
    endpoint: str
    kategorie: EndpointKategorie
    anfragen_gesamt: int
    fehler_anzahl: int
    p50_ms: float
    p95_ms: float
    p99_ms: float
    throughput_rps: float       # Requests per Second

    @property
    def fehler_rate_pct(self) -> float:
        if self.anfragen_gesamt == 0:
            return 0.0
        return round(self.fehler_anzahl / self.anfragen_gesamt * 100, 2)

    def as_dict(self) -> dict:
        return {
            "endpoint": self.endpoint,
            "kategorie": self.kategorie.value,
            "anfragen_gesamt": self.anfragen_gesamt,
            "fehler_anzahl": self.fehler_anzahl,
            "fehler_rate_pct": self.fehler_rate_pct,
            "p50_ms": self.p50_ms,
            "p95_ms": self.p95_ms,
            "p99_ms": self.p99_ms,
            "throughput_rps": self.throughput_rps,
        }


@dataclass
class LasttestErgebnis:
    """
    Vollständiges Ergebnis eines Lasttests.

    Enthält Messwerte pro Endpoint sowie aggregierte Kennzahlen.
    """
    test_id: str
    szenario: LasttestSzenario
    gleichzeitige_user: int
    status: LasttestStatus
    dauer_sekunden: float
    endpoint_ergebnisse: list[EndpointLasttestErgebnis] = field(default_factory=list)
    metadaten: dict[str, Any] = field(default_factory=dict)

    @property
    def gesamt_anfragen(self) -> int:
        return sum(e.anfragen_gesamt for e in self.endpoint_ergebnisse)

    @property
    def gesamt_fehler(self) -> int:
        return sum(e.fehler_anzahl for e in self.endpoint_ergebnisse)

    @property
    def gesamt_fehler_rate_pct(self) -> float:
        if self.gesamt_anfragen == 0:
            return 0.0
        return round(self.gesamt_fehler / self.gesamt_anfragen * 100, 2)

    @property
    def p95_max_ms(self) -> float:
        """Schlechtester p95-Wert über alle Endpoints."""
        if not self.endpoint_ergebnisse:
            return 0.0
        return max(e.p95_ms for e in self.endpoint_ergebnisse)

    @property
    def p95_avg_ms(self) -> float:
        """Durchschnittlicher p95-Wert über alle Endpoints."""
        if not self.endpoint_ergebnisse:
            return 0.0
        return round(sum(e.p95_ms for e in self.endpoint_ergebnisse) / len(self.endpoint_ergebnisse), 1)

    def get_endpoint(self, endpoint: str) -> EndpointLasttestErgebnis | None:
        return next((e for e in self.endpoint_ergebnisse if e.endpoint == endpoint), None)

    def as_dict(self) -> dict:
        return {
            "test_id": self.test_id,
            "szenario": self.szenario.value,
            "gleichzeitige_user": self.gleichzeitige_user,
            "status": self.status.value,
            "dauer_sekunden": self.dauer_sekunden,
            "gesamt_anfragen": self.gesamt_anfragen,
            "gesamt_fehler": self.gesamt_fehler,
            "gesamt_fehler_rate_pct": self.gesamt_fehler_rate_pct,
            "p95_max_ms": self.p95_max_ms,
            "p95_avg_ms": self.p95_avg_ms,
            "endpoint_ergebnisse": [e.as_dict() for e in self.endpoint_ergebnisse],
        }


# ---------------------------------------------------------------------------
# SLA-Vertrag für Lasttests
# ---------------------------------------------------------------------------

@dataclass
class LasttestSLAKriterium:
    """Ein einzelnes SLA-Kriterium für einen Lasttest."""
    name: str
    p95_ziel_ms: float | None = None        # None = nicht geprüft
    fehler_rate_ziel_pct: float | None = None
    min_throughput_rps: float | None = None
    kategorie: EndpointKategorie | None = None  # None = gilt für alle

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "p95_ziel_ms": self.p95_ziel_ms,
            "fehler_rate_ziel_pct": self.fehler_rate_ziel_pct,
            "min_throughput_rps": self.min_throughput_rps,
            "kategorie": self.kategorie.value if self.kategorie else None,
        }


@dataclass
class ErntepeakSLAContract:
    """
    Verbindlicher SLA-Vertrag für den Erntepeak-Lasttest.

    KPI: 500 gleichzeitige User stabil
    - Globale Error Rate < 1%
    - p95 globaler Durchschnitt < 2000ms
    - Dashboard-Endpoints p95 < 250ms (Gap 033)
    - Throughput > 100 RPS aggregiert
    """
    min_gleichzeitige_user: int = 500
    max_fehler_rate_pct: float = 1.0        # < 1%
    max_p95_global_ms: float = 2000.0       # < 2s
    max_p95_dashboard_ms: float = 250.0     # Gap 033: < 250ms
    min_throughput_rps: float = 100.0       # > 100 RPS

    def as_dict(self) -> dict:
        return {
            "min_gleichzeitige_user": self.min_gleichzeitige_user,
            "max_fehler_rate_pct": self.max_fehler_rate_pct,
            "max_p95_global_ms": self.max_p95_global_ms,
            "max_p95_dashboard_ms": self.max_p95_dashboard_ms,
            "min_throughput_rps": self.min_throughput_rps,
        }


# ---------------------------------------------------------------------------
# SLA-Auswertung
# ---------------------------------------------------------------------------

@dataclass
class LasttestSLAErgebnis:
    """Ergebnis der SLA-Auswertung eines Lasttests."""
    test_id: str
    szenario: LasttestSzenario
    erfuellungsgrad: SLAErfuellungsGrad
    kpi_erfuellt: bool           # Gap 037 KPI
    verletzte_kriterien: list[str] = field(default_factory=list)
    warnungen: list[str] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict:
        return {
            "test_id": self.test_id,
            "szenario": self.szenario.value,
            "erfuellungsgrad": self.erfuellungsgrad.value,
            "kpi_erfuellt": self.kpi_erfuellt,
            "verletzte_kriterien": self.verletzte_kriterien,
            "warnungen": self.warnungen,
            "details": self.details,
        }


def evaluate_erntepeak_sla(
    ergebnis: LasttestErgebnis,
    sla: ErntepeakSLAContract | None = None,
) -> LasttestSLAErgebnis:
    """
    Wertet ein Lasttest-Ergebnis gegen den Erntepeak-SLA aus.

    KPI: 500 gleichzeitige User stabil (Error Rate < 1%, p95 < 2s).
    """
    if sla is None:
        sla = ErntepeakSLAContract()

    verletzt: list[str] = []
    warnungen: list[str] = []
    details: dict[str, Any] = {}

    # Nutzerzahl
    if ergebnis.gleichzeitige_user < sla.min_gleichzeitige_user:
        verletzt.append(
            f"Zu wenige User: {ergebnis.gleichzeitige_user} < {sla.min_gleichzeitige_user}"
        )
    details["gleichzeitige_user"] = ergebnis.gleichzeitige_user

    # Error Rate
    details["gesamt_fehler_rate_pct"] = ergebnis.gesamt_fehler_rate_pct
    if ergebnis.gesamt_fehler_rate_pct > sla.max_fehler_rate_pct:
        verletzt.append(
            f"Error Rate {ergebnis.gesamt_fehler_rate_pct}% > Ziel {sla.max_fehler_rate_pct}%"
        )

    # p95 global
    details["p95_avg_ms"] = ergebnis.p95_avg_ms
    if ergebnis.p95_avg_ms > sla.max_p95_global_ms:
        verletzt.append(
            f"p95 Ø {ergebnis.p95_avg_ms}ms > Ziel {sla.max_p95_global_ms}ms"
        )

    # Dashboard p95 (Gap 033)
    dashboard_eps = [
        e for e in ergebnis.endpoint_ergebnisse
        if e.kategorie == EndpointKategorie.DASHBOARD
    ]
    if dashboard_eps:
        dashboard_p95_max = max(e.p95_ms for e in dashboard_eps)
        details["dashboard_p95_max_ms"] = dashboard_p95_max
        if dashboard_p95_max > sla.max_p95_dashboard_ms:
            verletzt.append(
                f"Dashboard p95 {dashboard_p95_max}ms > Ziel {sla.max_p95_dashboard_ms}ms"
            )

    # Throughput
    gesamt_throughput = sum(e.throughput_rps for e in ergebnis.endpoint_ergebnisse)
    details["gesamt_throughput_rps"] = round(gesamt_throughput, 1)
    if gesamt_throughput < sla.min_throughput_rps:
        warnungen.append(
            f"Throughput {gesamt_throughput:.1f} RPS < Ziel {sla.min_throughput_rps} RPS"
        )

    # Status ableiten
    if not ergebnis.endpoint_ergebnisse:
        grad = SLAErfuellungsGrad.NICHT_MESSBAR
    elif verletzt:
        grad = SLAErfuellungsGrad.VERLETZT
    elif warnungen:
        grad = SLAErfuellungsGrad.GRENZWERTIG
    else:
        grad = SLAErfuellungsGrad.ERFUELLT

    return LasttestSLAErgebnis(
        test_id=ergebnis.test_id,
        szenario=ergebnis.szenario,
        erfuellungsgrad=grad,
        kpi_erfuellt=len(verletzt) == 0 and bool(ergebnis.endpoint_ergebnisse),
        verletzte_kriterien=verletzt,
        warnungen=warnungen,
        details=details,
    )


# ---------------------------------------------------------------------------
# Vordefinierte Standard-Konfigurationen
# ---------------------------------------------------------------------------

def get_erntepeak_konfiguration() -> LasttestKonfiguration:
    """Standard-Konfiguration für den Erntepeak-Lasttest."""
    return LasttestKonfiguration(
        szenario=LasttestSzenario.ERNTEPEAK,
        gleichzeitige_user=500,
        dauer_sekunden=1800,    # 30 Minuten
        ramp_up_sekunden=120,   # 2 Minuten Hochlauf
        think_time_ms=500,
        tenant_count=10,
    )


def get_normalbetrieb_konfiguration() -> LasttestKonfiguration:
    """Standard-Konfiguration für den Normalbetrieb-Lasttest."""
    return LasttestKonfiguration(
        szenario=LasttestSzenario.NORMALBETRIEB,
        gleichzeitige_user=50,
        dauer_sekunden=600,
        ramp_up_sekunden=30,
        think_time_ms=1000,
        tenant_count=5,
    )
