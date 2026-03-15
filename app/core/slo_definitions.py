"""
SLO/SLI-Definitionen — Wave 30 AP4/AP5

Typisierte Service-Level-Objectives und -Indicators fuer den Process-Kernel.
Gap 050: Produktive Betriebsfuehrung mit SLO/SLI — Verfuegbarkeit >=99.9%.

SLO: Was wir zusagen (z.B. Verfuegbarkeit >= 99.9% im 30-Tage-Fenster)
SLI: Wie wir messen (z.B. erfolgreiche_anfragen / gesamt_anfragen * 100)

Alle Werte normiert:
  - Verfuegbarkeit, Erfolgsrate: 0.0 – 100.0 (Prozent)
  - Latenz: Millisekunden (p50/p95/p99)
  - Durchsatz: Anfragen/Sekunde oder Transaktionen/Minute
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


SLO_SCHEMA_VERSION = 1


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class SLOTyp(str, Enum):
    VERFUEGBARKEIT = "VERFUEGBARKEIT"   # Uptime in %
    LATENZ_P95     = "LATENZ_P95"       # 95th Percentile Latenz (ms)
    LATENZ_P99     = "LATENZ_P99"       # 99th Percentile Latenz (ms)
    FEHLERRATE     = "FEHLERRATE"       # Fehler in % (kleiner = besser)
    DURCHSATZ      = "DURCHSATZ"        # Transaktionen/Minute


class SLOMessfenster(str, Enum):
    STUNDE_1   = "1h"
    STUNDEN_24 = "24h"
    TAGE_7     = "7d"
    TAGE_30    = "30d"
    TAGE_90    = "90d"


class SLOViolationCode(str, Enum):
    ZIELWERT_NEGATIV          = "ZIELWERT_NEGATIV"
    TOLERANZ_GROESSER_ZIEL    = "TOLERANZ_GROESSER_ZIEL"
    DIENST_LEER               = "DIENST_LEER"
    VERFUEGBARKEIT_UEBER_100  = "VERFUEGBARKEIT_UEBER_100"


class SLOComplianceStatus(str, Enum):
    ERFUELLT          = "ERFUELLT"
    VERLETZT          = "VERLETZT"
    TOLERANZBEREICH   = "TOLERANZBEREICH"   # Zwischen Ziel und Toleranz
    UNBEKANNT         = "UNBEKANNT"         # Kein Messwert vorhanden


# ---------------------------------------------------------------------------
# AP4: SLIDefinition + SLODefinition
# ---------------------------------------------------------------------------

@dataclass
class SLIDefinition:
    """Beschreibt wie ein SLI gemessen wird (welche Metrik, welche Quelle)."""
    sli_id: str
    bezeichnung: str
    metrik_name: str       # z.B. "http_requests_total", "settlement_duration_ms"
    metrik_quelle: str     # z.B. "prometheus", "opentelemetry", "db_query"
    berechnungsformel: str # z.B. "sum(rate(http_200[5m])) / sum(rate(http_total[5m])) * 100"
    einheit: str           # z.B. "%", "ms", "req/s"

    def as_dict(self) -> dict:
        return {
            "sli_id": self.sli_id,
            "bezeichnung": self.bezeichnung,
            "metrik_name": self.metrik_name,
            "metrik_quelle": self.metrik_quelle,
            "berechnungsformel": self.berechnungsformel,
            "einheit": self.einheit,
        }


@dataclass
class SLODefinition:
    """
    Service-Level-Objective fuer einen Dienst/Prozess.

    zielwert: Angestrebter Grenzwert.
    toleranz_pct: Toleranzband bis zum Alarm (0.0 = kein Toleranzband).
      - Fuer VERFUEGBARKEIT/DURCHSATZ: Wert darf hoechstens zielwert - toleranz_pct unterschreiten.
      - Fuer LATENZ/FEHLERRATE: Wert darf hoechstens zielwert + toleranz_pct ueberschreiten.
    """
    slo_id: str
    dienst: str
    prozess_key: Optional[str]       # None = dienstweites SLO
    typ: SLOTyp
    bezeichnung: str
    zielwert: float
    toleranz_pct: float              # Absoluter Toleranz-Delta (z.B. 0.1 bei 99.9%)
    messfenster: SLOMessfenster
    sli: Optional[SLIDefinition] = None
    runbook_url: Optional[str] = None
    schema_version: int = SLO_SCHEMA_VERSION

    @property
    def toleranz_grenze(self) -> float:
        """Wert ab dem ein Alarm ausgeloest wird."""
        if self.typ in (SLOTyp.VERFUEGBARKEIT, SLOTyp.DURCHSATZ):
            return self.zielwert - self.toleranz_pct
        # Latenz und Fehlerrate: kleiner ist besser
        return self.zielwert + self.toleranz_pct

    def as_dict(self) -> dict:
        d: dict = {
            "slo_id": self.slo_id,
            "dienst": self.dienst,
            "prozess_key": self.prozess_key,
            "typ": self.typ.value,
            "bezeichnung": self.bezeichnung,
            "zielwert": self.zielwert,
            "toleranz_pct": self.toleranz_pct,
            "toleranz_grenze": self.toleranz_grenze,
            "messfenster": self.messfenster.value,
            "runbook_url": self.runbook_url,
            "schema_version": self.schema_version,
        }
        if self.sli:
            d["sli"] = self.sli.as_dict()
        return d


# ---------------------------------------------------------------------------
# AP5: check_slo_compliance() + validate_slo_definition()
# ---------------------------------------------------------------------------

@dataclass
class SLOComplianceResult:
    """Ergebnis der SLO-Compliance-Pruefung."""
    slo_id: str
    dienst: str
    typ: str
    zielwert: float
    ist_wert: Optional[float]
    status: SLOComplianceStatus
    abweichung: Optional[float]        # Absoluter Abstand zum Zielwert (signed)
    toleranz_grenze: float
    schema_version: int = SLO_SCHEMA_VERSION

    @property
    def verletzt(self) -> bool:
        return self.status == SLOComplianceStatus.VERLETZT

    @property
    def im_toleranzbereich(self) -> bool:
        return self.status == SLOComplianceStatus.TOLERANZBEREICH

    def as_dict(self) -> dict:
        return {
            "slo_id": self.slo_id,
            "dienst": self.dienst,
            "typ": self.typ,
            "zielwert": self.zielwert,
            "ist_wert": self.ist_wert,
            "status": self.status.value,
            "verletzt": self.verletzt,
            "im_toleranzbereich": self.im_toleranzbereich,
            "abweichung": self.abweichung,
            "toleranz_grenze": self.toleranz_grenze,
            "schema_version": self.schema_version,
        }


def check_slo_compliance(
    slo: SLODefinition,
    ist_wert: Optional[float],
) -> SLOComplianceResult:
    """
    Prueft ob ein gemessener Ist-Wert das SLO erfuellt.

    Semantik:
    - VERFUEGBARKEIT/DURCHSATZ: ist_wert >= zielwert → ERFUELLT;
      >= toleranz_grenze → TOLERANZBEREICH; sonst VERLETZT
    - LATENZ/FEHLERRATE: ist_wert <= zielwert → ERFUELLT;
      <= toleranz_grenze → TOLERANZBEREICH; sonst VERLETZT
    - ist_wert == None → UNBEKANNT
    """
    if ist_wert is None:
        return SLOComplianceResult(
            slo_id=slo.slo_id,
            dienst=slo.dienst,
            typ=slo.typ.value,
            zielwert=slo.zielwert,
            ist_wert=None,
            status=SLOComplianceStatus.UNBEKANNT,
            abweichung=None,
            toleranz_grenze=slo.toleranz_grenze,
        )

    abweichung = ist_wert - slo.zielwert

    if slo.typ in (SLOTyp.VERFUEGBARKEIT, SLOTyp.DURCHSATZ):
        if ist_wert >= slo.zielwert:
            status = SLOComplianceStatus.ERFUELLT
        elif ist_wert >= slo.toleranz_grenze:
            status = SLOComplianceStatus.TOLERANZBEREICH
        else:
            status = SLOComplianceStatus.VERLETZT
    else:
        # LATENZ, FEHLERRATE: kleinere Werte sind besser
        if ist_wert <= slo.zielwert:
            status = SLOComplianceStatus.ERFUELLT
        elif ist_wert <= slo.toleranz_grenze:
            status = SLOComplianceStatus.TOLERANZBEREICH
        else:
            status = SLOComplianceStatus.VERLETZT

    return SLOComplianceResult(
        slo_id=slo.slo_id,
        dienst=slo.dienst,
        typ=slo.typ.value,
        zielwert=slo.zielwert,
        ist_wert=ist_wert,
        status=status,
        abweichung=round(abweichung, 4),
        toleranz_grenze=slo.toleranz_grenze,
    )


@dataclass
class SLOViolation:
    code: SLOViolationCode
    message: str

    def as_dict(self) -> dict:
        return {"code": self.code.value, "message": self.message}


@dataclass
class SLOValidationResult:
    slo_id: str
    valid: bool
    violations: list[SLOViolation] = field(default_factory=list)
    schema_version: int = SLO_SCHEMA_VERSION

    def as_dict(self) -> dict:
        return {
            "slo_id": self.slo_id,
            "valid": self.valid,
            "violation_count": len(self.violations),
            "violations": [v.as_dict() for v in self.violations],
            "schema_version": self.schema_version,
        }


def validate_slo_definition(slo: SLODefinition) -> SLOValidationResult:
    """
    Prueft Konsistenz einer SLO-Definition.

    Checks:
    - dienst nicht leer
    - zielwert > 0
    - toleranz_pct <= zielwert (kein negatives Toleranz-Ziel)
    - VERFUEGBARKEIT: zielwert <= 100.0
    """
    violations: list[SLOViolation] = []

    if not slo.dienst or not slo.dienst.strip():
        violations.append(SLOViolation(
            code=SLOViolationCode.DIENST_LEER,
            message="dienst darf nicht leer sein",
        ))

    if slo.zielwert < 0:
        violations.append(SLOViolation(
            code=SLOViolationCode.ZIELWERT_NEGATIV,
            message=f"zielwert muss >= 0 sein (ist: {slo.zielwert})",
        ))

    if slo.toleranz_pct > slo.zielwert and slo.typ in (SLOTyp.VERFUEGBARKEIT, SLOTyp.DURCHSATZ):
        violations.append(SLOViolation(
            code=SLOViolationCode.TOLERANZ_GROESSER_ZIEL,
            message=f"toleranz_pct ({slo.toleranz_pct}) > zielwert ({slo.zielwert}): Toleranz-Grenze waere negativ",
        ))

    if slo.typ == SLOTyp.VERFUEGBARKEIT and slo.zielwert > 100.0:
        violations.append(SLOViolation(
            code=SLOViolationCode.VERFUEGBARKEIT_UEBER_100,
            message=f"Verfuegbarkeit kann nicht > 100% sein (ist: {slo.zielwert})",
        ))

    return SLOValidationResult(
        slo_id=slo.slo_id,
        valid=len(violations) == 0,
        violations=violations,
    )


# ---------------------------------------------------------------------------
# AP4: SLORegistry + get_process_kernel_slos()
# ---------------------------------------------------------------------------

@dataclass
class SLORegistry:
    """Registry aller definierten SLODefinitions."""
    slos: list[SLODefinition] = field(default_factory=list)
    schema_version: int = SLO_SCHEMA_VERSION

    def by_dienst(self, dienst: str) -> list[SLODefinition]:
        return [s for s in self.slos if s.dienst == dienst]

    def by_typ(self, typ: SLOTyp) -> list[SLODefinition]:
        return [s for s in self.slos if s.typ == typ]

    def by_slo_id(self, slo_id: str) -> Optional[SLODefinition]:
        for s in self.slos:
            if s.slo_id == slo_id:
                return s
        return None

    def as_dict(self) -> dict:
        return {
            "slo_count": len(self.slos),
            "dienste": sorted({s.dienst for s in self.slos}),
            "slos": [s.as_dict() for s in self.slos],
            "schema_version": self.schema_version,
        }


def get_process_kernel_slos() -> SLORegistry:
    """
    Liefert alle verbindlichen SLO-Definitionen des Process-Kernels.

    Abdeckung: API-Gateway, agrar_settlement, wareneingang,
               ap_invoice, workflow_engine, compliance_service.
    """
    slos: list[SLODefinition] = [

        # ---------------------------------------------------------------
        # API-Gateway: Verfuegbarkeit + Latenz
        # ---------------------------------------------------------------
        SLODefinition(
            slo_id="SLO-API-VERF-01",
            dienst="api_gateway",
            prozess_key=None,
            typ=SLOTyp.VERFUEGBARKEIT,
            bezeichnung="API-Gateway Verfuegbarkeit (30 Tage)",
            zielwert=99.9,
            toleranz_pct=0.1,
            messfenster=SLOMessfenster.TAGE_30,
            runbook_url="runbooks/api-gateway-verfuegbarkeit.md",
            sli=SLIDefinition(
                sli_id="SLI-API-VERF-01",
                bezeichnung="HTTP 2xx Rate",
                metrik_name="http_requests_total",
                metrik_quelle="prometheus",
                berechnungsformel="sum(rate(http_2xx[30d])) / sum(rate(http_total[30d])) * 100",
                einheit="%",
            ),
        ),

        SLODefinition(
            slo_id="SLO-API-LAT-01",
            dienst="api_gateway",
            prozess_key=None,
            typ=SLOTyp.LATENZ_P95,
            bezeichnung="API-Gateway Latenz P95 (24h)",
            zielwert=200.0,
            toleranz_pct=50.0,
            messfenster=SLOMessfenster.STUNDEN_24,
            sli=SLIDefinition(
                sli_id="SLI-API-LAT-01",
                bezeichnung="HTTP P95 Response Time",
                metrik_name="http_request_duration_ms",
                metrik_quelle="opentelemetry",
                berechnungsformel="histogram_quantile(0.95, http_request_duration_ms)",
                einheit="ms",
            ),
        ),

        SLODefinition(
            slo_id="SLO-API-ERR-01",
            dienst="api_gateway",
            prozess_key=None,
            typ=SLOTyp.FEHLERRATE,
            bezeichnung="API-Gateway Fehlerrate (7 Tage)",
            zielwert=0.5,         # Maximal 0.5% Fehler
            toleranz_pct=0.5,
            messfenster=SLOMessfenster.TAGE_7,
            sli=SLIDefinition(
                sli_id="SLI-API-ERR-01",
                bezeichnung="HTTP 5xx Rate",
                metrik_name="http_requests_total",
                metrik_quelle="prometheus",
                berechnungsformel="sum(rate(http_5xx[7d])) / sum(rate(http_total[7d])) * 100",
                einheit="%",
            ),
        ),

        # ---------------------------------------------------------------
        # agrar_settlement: Durchsatz + Latenz
        # ---------------------------------------------------------------
        SLODefinition(
            slo_id="SLO-AS-VERF-01",
            dienst="agrar_settlement",
            prozess_key="agrar_settlement",
            typ=SLOTyp.VERFUEGBARKEIT,
            bezeichnung="Settlement-Service Verfuegbarkeit Erntesaison",
            zielwert=99.5,
            toleranz_pct=0.5,
            messfenster=SLOMessfenster.TAGE_30,
        ),

        SLODefinition(
            slo_id="SLO-AS-LAT-01",
            dienst="agrar_settlement",
            prozess_key="agrar_settlement",
            typ=SLOTyp.LATENZ_P99,
            bezeichnung="Settlement-Berechnungs-Latenz P99",
            zielwert=500.0,        # ms
            toleranz_pct=200.0,
            messfenster=SLOMessfenster.STUNDEN_24,
            sli=SLIDefinition(
                sli_id="SLI-AS-LAT-01",
                bezeichnung="Settlement compute P99",
                metrik_name="valeo_agrar_settlement_duration_ms",
                metrik_quelle="opentelemetry",
                berechnungsformel="histogram_quantile(0.99, valeo_agrar_settlement_duration_ms)",
                einheit="ms",
            ),
        ),

        # ---------------------------------------------------------------
        # wareneingang: Verfuegbarkeit + Durchsatz
        # ---------------------------------------------------------------
        SLODefinition(
            slo_id="SLO-WE-VERF-01",
            dienst="wareneingang",
            prozess_key="wareneingang",
            typ=SLOTyp.VERFUEGBARKEIT,
            bezeichnung="Wareneingang-Service Verfuegbarkeit (Erntepeak)",
            zielwert=99.9,
            toleranz_pct=0.1,
            messfenster=SLOMessfenster.TAGE_7,
            runbook_url="runbooks/wareneingang-erntepeak.md",
        ),

        SLODefinition(
            slo_id="SLO-WE-DURCH-01",
            dienst="wareneingang",
            prozess_key="wareneingang",
            typ=SLOTyp.DURCHSATZ,
            bezeichnung="Wiegescheine pro Minute (Erntepeak)",
            zielwert=20.0,          # 20 Wiegescheine/Minute
            toleranz_pct=5.0,
            messfenster=SLOMessfenster.STUNDE_1,
            sli=SLIDefinition(
                sli_id="SLI-WE-DURCH-01",
                bezeichnung="Wiegeschein-Durchsatz",
                metrik_name="valeo_wareneingang_wiegescheine_total",
                metrik_quelle="prometheus",
                berechnungsformel="rate(valeo_wareneingang_wiegescheine_total[1m])",
                einheit="req/min",
            ),
        ),

        # ---------------------------------------------------------------
        # workflow_engine: Verfuegbarkeit
        # ---------------------------------------------------------------
        SLODefinition(
            slo_id="SLO-WF-VERF-01",
            dienst="workflow_engine",
            prozess_key=None,
            typ=SLOTyp.VERFUEGBARKEIT,
            bezeichnung="Workflow-Engine Verfuegbarkeit (90 Tage)",
            zielwert=99.9,
            toleranz_pct=0.1,
            messfenster=SLOMessfenster.TAGE_90,
            runbook_url="runbooks/workflow-engine-verfuegbarkeit.md",
        ),

        # ---------------------------------------------------------------
        # compliance_service: Fehlerrate
        # ---------------------------------------------------------------
        SLODefinition(
            slo_id="SLO-COM-ERR-01",
            dienst="compliance_service",
            prozess_key=None,
            typ=SLOTyp.FEHLERRATE,
            bezeichnung="Compliance-Service Fehlerrate (30 Tage)",
            zielwert=0.1,           # Max 0.1% Fehler
            toleranz_pct=0.1,
            messfenster=SLOMessfenster.TAGE_30,
        ),
    ]

    return SLORegistry(slos=slos)
