"""Preflight Phase 0 der Rationsoptimierung (RATION-CANON-03, Skill §3/Phase 0).

Vor jeder Optimierung werden Eingabe- und Modellkonsistenz geprueft und als
**strukturierte Findings** ausgegeben – jedes Finding mit Code, Schweregrad,
betroffener Groesse, Istwert, Grenze, Einheit, Ursache und empfohlener Abhilfe
(Skill §3). Zentrale Leitplanke: **fehlende Daten werden nicht stillschweigend
als 0 interpretiert** (Skill §10.3), sondern als Finding ausgewiesen.

Deckt insbesondere die Golden Cases (Skill §11.1) ab:

* Fall 3 – Summe der Futtermittel-Minima > zulaessige TM-Aufnahme.
* Fall 4 – Summe der Futtermittel-Maxima < notwendige TM-Aufnahme.
* Fall 12 – fehlende Analysewerte als Finding, nicht als 0.

Reines Modul ohne SciPy/FastAPI-Abhaengigkeit.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Mapping, Optional, Sequence


class Severity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    BLOCKER = "blocker"


# Pflicht-Analysegroessen je Futtermittel (zum Rechnen unverzichtbar).
# me darf 0 sein (z. B. Mineralfutter) – 0 ist ein Wert, kein Fehlwert.
REQUIRED_FEED_KEYS = ("me", "sidp", "dm_frac")


@dataclass(slots=True)
class Finding:
    code: str
    severity: Severity
    metric: str
    cause: str
    remediation: str
    actual: Optional[float] = None
    limit: Optional[float] = None
    unit: str = ""
    feed_id: Optional[str] = None
    feed_name: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "severity": self.severity.value,
            "metric": self.metric,
            "actual": self.actual,
            "limit": self.limit,
            "unit": self.unit,
            "cause": self.cause,
            "remediation": self.remediation,
            "feed_id": self.feed_id,
            "feed_name": self.feed_name,
        }


@dataclass(slots=True)
class PreflightReport:
    findings: List[Finding] = field(default_factory=list)

    @property
    def has_blocker(self) -> bool:
        return any(f.severity is Severity.BLOCKER for f in self.findings)

    @property
    def ok(self) -> bool:
        return not self.has_blocker

    def by_severity(self, severity: Severity) -> List[Finding]:
        return [f for f in self.findings if f.severity is severity]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ok": self.ok,
            "has_blocker": self.has_blocker,
            "blocker_count": len(self.by_severity(Severity.BLOCKER)),
            "warning_count": len(self.by_severity(Severity.WARNING)),
            "info_count": len(self.by_severity(Severity.INFO)),
            "findings": [f.to_dict() for f in self.findings],
        }


def _is_active(feed: Mapping[str, Any]) -> bool:
    return bool(feed.get("active", True))


def _num(feed: Mapping[str, Any], key: str) -> Optional[float]:
    """Wert als float oder None. Fehlender Schluessel/None => None (kein 0!)."""
    if key not in feed:
        return None
    raw = feed[key]
    if raw is None:
        return None
    try:
        return float(raw)
    except (TypeError, ValueError):
        return None


def _feed_label(feed: Mapping[str, Any]) -> str:
    return str(feed.get("name") or feed.get("id") or "Futtermittel")


def run_preflight(
    feeds: Sequence[Mapping[str, Any]],
    *,
    dmi_min_kg: Optional[float] = None,
    dmi_max_kg: Optional[float] = None,
    profile: Optional[Mapping[str, Any]] = None,
) -> PreflightReport:
    """Fuehre die Preflight-Pruefungen aus und liefere einen Report.

    ``dmi_min_kg`` = notwendige, ``dmi_max_kg`` = maximal zulaessige TM-Aufnahme.
    """
    findings: List[Finding] = []
    active_feeds = [f for f in feeds if _is_active(f)]

    # --- (1) DMI-Band-Konsistenz -------------------------------------------
    if (
        dmi_min_kg is not None
        and dmi_max_kg is not None
        and dmi_min_kg > dmi_max_kg + 1e-9
    ):
        findings.append(
            Finding(
                code="DMI_BAND_INCONSISTENT",
                severity=Severity.BLOCKER,
                metric="TM-Aufnahme-Band",
                actual=round(float(dmi_min_kg), 3),
                limit=round(float(dmi_max_kg), 3),
                unit="kg TM/d",
                cause="Minimale TM-Aufnahme groesser als maximale TM-Aufnahme.",
                remediation="TM-Aufnahmegrenzen (Wizard/Tierdaten) korrigieren.",
            )
        )

    # --- (2) je Futtermittel: Analyse-Vollstaendigkeit, Grenzen, Plausibel. -
    for feed in active_feeds:
        label = _feed_label(feed)
        fid = feed.get("id")

        # Pflicht-Analysewerte vorhanden? (fehlend != 0)
        for key in REQUIRED_FEED_KEYS:
            if _num(feed, key) is None:
                findings.append(
                    Finding(
                        code="FEED_ANALYSIS_MISSING",
                        severity=Severity.BLOCKER,
                        metric=key,
                        cause=(
                            f"Pflicht-Analysewert '{key}' fehlt fuer '{label}' – "
                            "wird NICHT als 0 angenommen."
                        ),
                        remediation=(
                            "Analysewert nachtragen oder Futtermittel deaktivieren."
                        ),
                        unit="",
                        feed_id=fid,
                        feed_name=label,
                    )
                )

        dm_frac = _num(feed, "dm_frac")
        if dm_frac is not None and not (0.0 < dm_frac <= 1.0):
            findings.append(
                Finding(
                    code="DM_FRAC_IMPLAUSIBLE",
                    severity=Severity.BLOCKER if dm_frac <= 0 else Severity.WARNING,
                    metric="dm_frac",
                    actual=round(dm_frac, 4),
                    limit=1.0,
                    unit="Anteil (0..1)",
                    cause=f"Trockenmasseanteil fuer '{label}' ausserhalb (0..1].",
                    remediation="TM-Gehalt pruefen (g/kg oder % korrekt umgerechnet?).",
                    feed_id=fid,
                    feed_name=label,
                )
            )

        min_kg = _num(feed, "min_kg")
        max_kg = _num(feed, "max_kg")
        if min_kg is not None and min_kg < 0:
            findings.append(
                Finding(
                    code="FEED_BOUND_NEGATIVE",
                    severity=Severity.BLOCKER,
                    metric="min_kg",
                    actual=round(min_kg, 3),
                    limit=0.0,
                    unit="kg TM/d",
                    cause=f"Negative Untergrenze fuer '{label}'.",
                    remediation="Untergrenze auf >= 0 setzen.",
                    feed_id=fid,
                    feed_name=label,
                )
            )
        if (
            min_kg is not None
            and max_kg is not None
            and min_kg > max_kg + 1e-9
        ):
            findings.append(
                Finding(
                    code="FEED_MIN_GT_MAX",
                    severity=Severity.BLOCKER,
                    metric="min_kg/max_kg",
                    actual=round(min_kg, 3),
                    limit=round(max_kg, 3),
                    unit="kg TM/d",
                    cause=f"Untergrenze > Obergrenze fuer '{label}'.",
                    remediation="Min-/Max-Vorgaben je Futtermittel angleichen.",
                    feed_id=fid,
                    feed_name=label,
                )
            )

        price = _num(feed, "price")
        if price is None or price <= 0:
            findings.append(
                Finding(
                    code="FEED_PRICE_MISSING",
                    severity=Severity.WARNING,
                    metric="price",
                    actual=price,
                    limit=None,
                    unit="EUR/kg TM",
                    cause=(
                        f"Preis/Preisbasis fuer '{label}' fehlt oder <= 0 – "
                        "Kostenkennzahlen sind ohne Preisbasis nicht belastbar."
                    ),
                    remediation="Preis und Preisbasis hinterlegen.",
                    feed_id=fid,
                    feed_name=label,
                )
            )

    # --- (3) Summenkonsistenz Minima/Maxima gegen DMI-Band ------------------
    sum_min = sum(
        (_num(f, "min_kg") or 0.0) for f in active_feeds if (_num(f, "min_kg") or 0.0) > 0
    )
    if dmi_max_kg is not None and sum_min > dmi_max_kg + 1e-6:
        # Golden Case 3.
        findings.append(
            Finding(
                code="SUM_MIN_EXCEEDS_DMI_MAX",
                severity=Severity.BLOCKER,
                metric="Summe Futtermittel-Minima",
                actual=round(sum_min, 3),
                limit=round(float(dmi_max_kg), 3),
                unit="kg TM/d",
                cause=(
                    "Summe der Futtermittel-Minima uebersteigt die zulaessige "
                    "TM-Aufnahme – die Ration ist ueberbestimmt."
                ),
                remediation=(
                    "Einzel-Mindestmengen senken oder TM-Aufnahme-Obergrenze pruefen."
                ),
            )
        )

    # Notwendige TM-Aufnahme: bevorzugt dmi_min_kg (Untergrenze des Bedarfs).
    required_dmi = dmi_min_kg
    if required_dmi is not None and active_feeds:
        sum_max = 0.0
        any_max = False
        for f in active_feeds:
            mx = _num(f, "max_kg")
            if mx is not None:
                any_max = True
                sum_max += mx
        if any_max and sum_max + 1e-6 < required_dmi:
            # Golden Case 4.
            findings.append(
                Finding(
                    code="SUM_MAX_BELOW_DMI_MIN",
                    severity=Severity.BLOCKER,
                    metric="Summe Futtermittel-Maxima",
                    actual=round(sum_max, 3),
                    limit=round(float(required_dmi), 3),
                    unit="kg TM/d",
                    cause=(
                        "Summe der Futtermittel-Maxima reicht nicht fuer die "
                        "notwendige TM-Aufnahme."
                    ),
                    remediation=(
                        "Einzel-Hoechstmengen anheben oder weitere Futtermittel "
                        "zulassen."
                    ),
                )
            )

    # --- (4) Tier-/Leistungsdaten (nicht blockierend) -----------------------
    if profile is not None:
        milk = profile.get("milk_kg_day")
        if milk is None or float(milk or 0) <= 0:
            findings.append(
                Finding(
                    code="TARGET_MILK_MISSING",
                    severity=Severity.WARNING,
                    metric="milk_kg_day",
                    actual=float(milk) if milk is not None else None,
                    unit="kg/d",
                    cause="Keine positive Wunschleistung angegeben.",
                    remediation="Zielleistung setzen, sonst nur Bewertung ohne Ziel.",
                )
            )
        bw = profile.get("body_weight_kg")
        if bw is None or float(bw or 0) <= 0:
            findings.append(
                Finding(
                    code="BODY_WEIGHT_MISSING",
                    severity=Severity.WARNING,
                    metric="body_weight_kg",
                    actual=float(bw) if bw is not None else None,
                    unit="kg",
                    cause="Kein Koerpergewicht angegeben – Erhaltungsbedarf geschaetzt.",
                    remediation="Koerpergewicht der Gruppe hinterlegen.",
                )
            )

    return PreflightReport(findings=findings)


__all__ = [
    "Severity",
    "Finding",
    "PreflightReport",
    "REQUIRED_FEED_KEYS",
    "run_preflight",
]
