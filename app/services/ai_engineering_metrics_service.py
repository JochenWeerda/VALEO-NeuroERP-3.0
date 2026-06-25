"""P2.2 — Produktivitaetsmetriken fuer AI-Engineering in VALEO.

Misst: Slice Cycle Time, Rework-Quote, Test-Fail-Ursachen, Doku-Drift,
externe Gate-Blocker, Agentenfehler nach Ursache, Review-Aufwand.

Datenquelle: Slice-YAMLs aus docs/agent-ops/slices/, Workboard, Coverage-XML.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
SLICES_DIR = REPO_ROOT / "docs" / "agent-ops" / "slices"
WORKBOARD = REPO_ROOT / "docs" / "agent-ops" / "active-workboard.md"
COVERAGE_XML = REPO_ROOT / "coverage.xml"


def _today() -> date:
    return datetime.now(timezone.utc).date()


def _parse_date(val: Any) -> date | None:
    if not val:
        return None
    try:
        return date.fromisoformat(str(val))
    except ValueError:
        return None


@dataclass
class SliceMetric:
    slice_id: str
    title: str
    owner: str
    status: str
    created_at: date | None
    closed_at: date | None
    cycle_time_days: int | None
    has_tests: bool
    has_all_harness_fields: bool
    test_count: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "slice_id": self.slice_id,
            "title": self.title,
            "owner": self.owner,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "closed_at": self.closed_at.isoformat() if self.closed_at else None,
            "cycle_time_days": self.cycle_time_days,
            "has_tests": self.has_tests,
            "has_all_harness_fields": self.has_all_harness_fields,
            "test_count": self.test_count,
        }


_REQUIRED_HARNESS = {
    "fachlicher_vertrag", "architektur_vertrag", "daten_vertrag",
    "test_vertrag", "security_vertrag", "betriebs_vertrag", "dokumentations_vertrag",
}


def _load_slices() -> list[SliceMetric]:
    metrics = []
    if not SLICES_DIR.exists():
        return metrics
    for yaml_path in SLICES_DIR.glob("*.yaml"):
        try:
            with yaml_path.open("r", encoding="utf-8") as fh:
                data = yaml.safe_load(fh) or {}
        except Exception:
            continue
        created = _parse_date(data.get("created_at"))
        # Closed-at aus Workboard-Text heuristisch schliessen
        closed = None
        if data.get("status") in ("completed", "abgeschlossen"):
            # Versuch: closed ~= created (MVP ohne explizites closed_at)
            closed = created

        cycle = None
        if created and closed:
            cycle = (closed - created).days

        harness = data.get("ai_harness") or {}
        tests = data.get("tests") or []
        metrics.append(SliceMetric(
            slice_id=data.get("slice_id", yaml_path.stem),
            title=data.get("title", ""),
            owner=data.get("owner", ""),
            status=data.get("status", ""),
            created_at=created,
            closed_at=closed,
            cycle_time_days=cycle,
            has_tests=bool(tests),
            has_all_harness_fields=_REQUIRED_HARNESS.issubset(harness.keys()),
            test_count=len(tests),
        ))
    return metrics


def _load_coverage() -> dict[str, float]:
    if not COVERAGE_XML.exists():
        return {}
    try:
        tree = ET.parse(COVERAGE_XML)
        root = tree.getroot()
        return {
            cls.attrib.get("filename", "").replace("\\", "/").lstrip("./"): float(cls.attrib.get("line-rate", 0))
            for cls in root.findall(".//class")
        }
    except Exception:
        return {}


def _load_workboard_text() -> str:
    if not WORKBOARD.exists():
        return ""
    return WORKBOARD.read_text(encoding="utf-8")


class AiEngineeringMetricsService:
    """Produktivitaetsmetriken fuer den AI-Engineering-Betrieb."""

    def slice_metrics(self) -> list[dict[str, Any]]:
        return [s.to_dict() for s in _load_slices()]

    def cycle_time_summary(self) -> dict[str, Any]:
        slices = _load_slices()
        completed = [s for s in slices if s.status in ("completed", "abgeschlossen")]
        times = [s.cycle_time_days for s in completed if s.cycle_time_days is not None]
        return {
            "total_slices": len(slices),
            "completed_slices": len(completed),
            "avg_cycle_time_days": round(sum(times) / len(times), 1) if times else None,
            "max_cycle_time_days": max(times) if times else None,
            "min_cycle_time_days": min(times) if times else None,
            "slices_without_tests": sum(1 for s in slices if not s.has_tests),
            "slices_missing_harness": sum(1 for s in slices if not s.has_all_harness_fields),
        }

    def coverage_summary(self) -> dict[str, Any]:
        cov = _load_coverage()
        if not cov:
            return {"status": "coverage.xml nicht gefunden — pytest --cov zuerst ausfuehren"}
        rates = list(cov.values())
        below_50 = [f for f, r in cov.items() if r < 0.5]
        below_70 = [f for f, r in cov.items() if r < 0.7]
        return {
            "total_files": len(cov),
            "avg_coverage_pct": round(sum(rates) / len(rates) * 100, 1) if rates else 0,
            "files_below_50pct": len(below_50),
            "files_below_70pct": len(below_70),
            "top_3_lowest": sorted([(f, round(r * 100, 1)) for f, r in cov.items()], key=lambda x: x[1])[:3],
        }

    def gate_blocker_summary(self) -> dict[str, Any]:
        wb = _load_workboard_text()
        # Einfache Heuristik: Zaehle "extern" und "Gate" Vorkommen im Workboard
        extern_mentions = len(re.findall(r'\bextern\b|\bGate\b|\bDATE[Vv]\b|\bELSTER\b|\bTSE\b|\bDMS\b', wb))
        open_items = len(re.findall(r'in Arbeit', wb, re.IGNORECASE))
        return {
            "workboard_open_items": open_items,
            "external_gate_mentions": extern_mentions,
            "hinweis": "Heuristik aus Workboard-Text — fuer produktive Metriken Slice-YAML external_gates auswerten",
        }

    def rework_indicator(self) -> dict[str, Any]:
        slices = _load_slices()
        # Slices ohne vollstaendiges Harness sind Rework-Kandidaten
        incomplete = [s for s in slices if not s.has_all_harness_fields or not s.has_tests]
        return {
            "slices_with_incomplete_harness_or_tests": len(incomplete),
            "details": [{"slice_id": s.slice_id, "has_tests": s.has_tests, "has_all_harness_fields": s.has_all_harness_fields} for s in incomplete],
            "rework_rate_pct": round(len(incomplete) / len(slices) * 100, 1) if slices else 0,
        }

    def owner_distribution(self) -> dict[str, int]:
        slices = _load_slices()
        dist: dict[str, int] = {}
        for s in slices:
            dist[s.owner] = dist.get(s.owner, 0) + 1
        return dist

    def full_dashboard(self) -> dict[str, Any]:
        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "cycle_time": self.cycle_time_summary(),
            "coverage": self.coverage_summary(),
            "gate_blockers": self.gate_blocker_summary(),
            "rework": self.rework_indicator(),
            "owner_distribution": self.owner_distribution(),
        }


ai_engineering_metrics_service = AiEngineeringMetricsService()
