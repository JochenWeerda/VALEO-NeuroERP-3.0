#!/usr/bin/env python3
"""AI-ENGINEERING-METRICS-001 — Produktivitätsmetriken für das AI-Engineering.

Berechnet aus Git-Log und Slice-YAMLs:
  - Slice Cycle Time (claim → close, in Stunden)
  - Rework-Quote (fix/revert-Commits nach einem feat-Commit je Slice)
  - Doku-Drift-Score (Slices ohne aktualisierte Doku-Dateien)
  - Agent-Produktivität (Commits je Owner)
  - Externe Gate-Blocker (Slices mit external_gates)

Aufruf:
  python scripts/ai_engineering_metrics.py [--since YYYY-MM-DD] [--json] [--csv]
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
SLICES_DIR = REPO_ROOT / "docs" / "agent-ops" / "slices"

# Commit-Konventionen
_CLAIM_RE = re.compile(r"claim\s+([\w\-\.]+)", re.IGNORECASE)
_FEAT_RE = re.compile(r"^feat\(", re.IGNORECASE)
_FIX_RE = re.compile(r"^fix\(|^revert\b", re.IGNORECASE)
_SLICE_IN_MSG_RE = re.compile(r"\b([A-Z][A-Z0-9\-]+\-\d{3}(?:\.\d+)?)\b")


# ── Datenklassen ───────────────────────────────────────────────────────────────

@dataclass
class SliceMetric:
    slice_id: str
    title: str
    owner: str
    status: str
    updated: str
    has_external_gates: bool
    cycle_time_hours: Optional[float]   # None wenn claim-Commit nicht gefunden
    rework_commits: int                  # fix/revert-Commits nach feat-Commit
    has_doc_files: bool                  # mindestens 1 docs/-Datei in file_ownership


@dataclass
class CommitRecord:
    sha: str
    ts: datetime
    subject: str
    files_changed: list[str] = field(default_factory=list)


@dataclass
class EngMetricsReport:
    generated_at: str
    since: str
    total_slices: int
    completed_slices: int
    slices_with_external_gates: int
    median_cycle_time_hours: Optional[float]
    p90_cycle_time_hours: Optional[float]
    overall_rework_rate: float           # rework_commits / total feat-commits
    slices_without_doc_files: int
    agent_commit_counts: dict[str, int]  # owner → commit count (from YAMLs)
    slice_details: list[SliceMetric]


# ── Git-Helpers ────────────────────────────────────────────────────────────────

def _run(args: list[str]) -> str:
    result = subprocess.run(args, capture_output=True, text=True, cwd=REPO_ROOT)
    return result.stdout.strip()


def _load_commits(since: Optional[str]) -> list[CommitRecord]:
    fmt = "%H\x1f%aI\x1f%s"
    cmd = ["git", "log", f"--format={fmt}"]
    if since:
        cmd += [f"--since={since}"]
    raw = _run(cmd)
    records: list[CommitRecord] = []
    for line in raw.splitlines():
        parts = line.split("\x1f", 2)
        if len(parts) < 3:
            continue
        sha, ts_str, subject = parts
        try:
            ts = datetime.fromisoformat(ts_str)
        except ValueError:
            continue
        records.append(CommitRecord(sha=sha, ts=ts, subject=subject))
    return records


def _commit_files(sha: str) -> list[str]:
    out = _run(["git", "diff-tree", "--no-commit-id", "-r", "--name-only", sha])
    return out.splitlines()


# ── YAML-Helpers ───────────────────────────────────────────────────────────────

def _load_slices() -> list[dict]:
    slices = []
    for p in sorted(SLICES_DIR.glob("*.yaml")):
        try:
            with open(p, encoding="utf-8") as f:
                data = yaml.safe_load(f)
            if isinstance(data, dict) and "slice_id" in data:
                slices.append(data)
        except Exception:
            pass
    return slices


# ── Metrik-Berechnungen ────────────────────────────────────────────────────────

def _extract_slice_ids(subject: str) -> list[str]:
    return _SLICE_IN_MSG_RE.findall(subject)


def _build_claim_map(commits: list[CommitRecord]) -> dict[str, datetime]:
    """slice_id → Timestamp des claim-Commits."""
    claim_map: dict[str, datetime] = {}
    for c in commits:
        if "claim" in c.subject.lower():
            ids = _extract_slice_ids(c.subject)
            for sid in ids:
                if sid not in claim_map:
                    claim_map[sid] = c.ts
            m = _CLAIM_RE.search(c.subject)
            if m:
                sid = m.group(1).upper()
                if sid not in claim_map:
                    claim_map[sid] = c.ts
    return claim_map


def _build_feat_map(commits: list[CommitRecord]) -> dict[str, datetime]:
    """slice_id → Timestamp des ersten feat-Commits der den Slice nennt."""
    feat_map: dict[str, datetime] = {}
    for c in commits:
        if _FEAT_RE.match(c.subject):
            for sid in _extract_slice_ids(c.subject):
                if sid not in feat_map:
                    feat_map[sid] = c.ts
    return feat_map


def _build_rework_map(commits: list[CommitRecord]) -> dict[str, int]:
    """slice_id → Anzahl fix/revert-Commits die den Slice nennen."""
    rework: dict[str, int] = {}
    for c in commits:
        if _FIX_RE.match(c.subject):
            for sid in _extract_slice_ids(c.subject):
                rework[sid] = rework.get(sid, 0) + 1
    return rework


def _median(values: list[float]) -> Optional[float]:
    if not values:
        return None
    s = sorted(values)
    n = len(s)
    mid = n // 2
    return s[mid] if n % 2 else (s[mid - 1] + s[mid]) / 2


def _percentile(values: list[float], p: int) -> Optional[float]:
    if not values:
        return None
    s = sorted(values)
    idx = int(len(s) * p / 100)
    return s[min(idx, len(s) - 1)]


# ── Agent-Commit-Zählung ───────────────────────────────────────────────────────

def _agent_commit_counts(slices: list[dict]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for s in slices:
        owner = str(s.get("owner", "unknown"))
        counts[owner] = counts.get(owner, 0) + 1
    return dict(sorted(counts.items(), key=lambda x: -x[1]))


# ── Haupt-Report ───────────────────────────────────────────────────────────────

def compute_report(since: Optional[str] = None) -> EngMetricsReport:
    commits = _load_commits(since)
    slices = _load_slices()

    claim_map = _build_claim_map(commits)
    feat_map = _build_feat_map(commits)
    rework_map = _build_rework_map(commits)

    total_feat = sum(1 for c in commits if _FEAT_RE.match(c.subject))
    total_rework = sum(1 for c in commits if _FIX_RE.match(c.subject))

    details: list[SliceMetric] = []
    cycle_times: list[float] = []

    for s in slices:
        sid = s.get("slice_id", "")
        title = s.get("title", "")
        owner = str(s.get("owner", "unknown"))
        status = str(s.get("status", "unknown"))
        updated = str(s.get("updated", ""))
        ext_gates = bool(s.get("external_gates"))
        file_ownership: list[str] = s.get("file_ownership", [])
        has_doc = any("docs/" in str(f) for f in file_ownership)

        # Cycle time: claim → feat (erstes feat mit Slice-ID)
        cycle: Optional[float] = None
        claim_ts = claim_map.get(sid)
        close_ts = feat_map.get(sid)
        if claim_ts and close_ts and close_ts >= claim_ts:
            diff = (close_ts - claim_ts).total_seconds() / 3600
            cycle = round(diff, 2)
            cycle_times.append(cycle)

        rework = rework_map.get(sid, 0)

        details.append(SliceMetric(
            slice_id=sid,
            title=title,
            owner=owner,
            status=status,
            updated=updated,
            has_external_gates=ext_gates,
            cycle_time_hours=cycle,
            rework_commits=rework,
            has_doc_files=has_doc,
        ))

    completed = [d for d in details if "complet" in d.status.lower() or "abgeschlossen" in d.status.lower()]
    ext_gate_count = sum(1 for d in details if d.has_external_gates)
    no_doc_count = sum(1 for d in details if not d.has_doc_files)
    rework_rate = round(total_rework / total_feat, 3) if total_feat else 0.0

    return EngMetricsReport(
        generated_at=datetime.now(timezone.utc).isoformat(),
        since=since or "all",
        total_slices=len(details),
        completed_slices=len(completed),
        slices_with_external_gates=ext_gate_count,
        median_cycle_time_hours=_median(cycle_times),
        p90_cycle_time_hours=_percentile(cycle_times, 90),
        overall_rework_rate=rework_rate,
        slices_without_doc_files=no_doc_count,
        agent_commit_counts=_agent_commit_counts(slices),
        slice_details=details,
    )


# ── Ausgabe-Formatter ──────────────────────────────────────────────────────────

def _print_summary(report: EngMetricsReport) -> None:
    print(f"\n{'='*60}")
    print(f"  VALEO AI Engineering Metrics — {report.generated_at[:10]}")
    print(f"  Zeitraum: seit {report.since}")
    print(f"{'='*60}")
    print(f"  Slices gesamt:           {report.total_slices}")
    print(f"  Slices abgeschlossen:    {report.completed_slices}")
    print(f"  Mit externen Gates:      {report.slices_with_external_gates}")
    print(f"  Ohne Doku-Dateien:       {report.slices_without_doc_files}")
    print(f"\n  Cycle Time (Median):     {report.median_cycle_time_hours:.1f} h" if report.median_cycle_time_hours else "\n  Cycle Time (Median):     n/a")
    print(f"  Cycle Time (P90):        {report.p90_cycle_time_hours:.1f} h" if report.p90_cycle_time_hours else "  Cycle Time (P90):        n/a")
    print(f"  Rework-Rate:             {report.overall_rework_rate:.1%}")

    print(f"\n  Slices je Owner:")
    for owner, count in report.agent_commit_counts.items():
        bar = "#" * min(count, 40)
        print(f"    {owner:<30} {count:>3}  {bar}")

    # Top-Rework-Slices
    rework_slices = sorted(report.slice_details, key=lambda d: -d.rework_commits)[:5]
    if any(d.rework_commits > 0 for d in rework_slices):
        print(f"\n  Top-Rework-Slices:")
        for d in rework_slices:
            if d.rework_commits > 0:
                print(f"    {d.slice_id:<40} {d.rework_commits} fix-Commits")

    # Langläufer (P90+)
    p90 = report.p90_cycle_time_hours
    if p90:
        longrunners = [d for d in report.slice_details if d.cycle_time_hours and d.cycle_time_hours >= p90]
        if longrunners:
            print(f"\n  Langläufer (≥ P90 = {p90:.1f} h):")
            for d in sorted(longrunners, key=lambda x: -(x.cycle_time_hours or 0))[:5]:
                print(f"    {d.slice_id:<40} {d.cycle_time_hours:.1f} h  [{d.owner}]")

    print(f"\n{'='*60}\n")


def _to_csv(report: EngMetricsReport) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow([
        "slice_id", "title", "owner", "status", "updated",
        "cycle_time_hours", "rework_commits", "has_doc_files", "has_external_gates",
    ])
    for d in report.slice_details:
        writer.writerow([
            d.slice_id, d.title, d.owner, d.status, d.updated,
            d.cycle_time_hours if d.cycle_time_hours is not None else "",
            d.rework_commits, d.has_doc_files, d.has_external_gates,
        ])
    return buf.getvalue()


# ── CLI ────────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="VALEO AI Engineering Metrics")
    parser.add_argument("--since", default=None, help="ISO-Datum ab dem Git-Log ausgewertet wird (z.B. 2026-06-01)")
    parser.add_argument("--json", dest="as_json", action="store_true", help="Ausgabe als JSON")
    parser.add_argument("--csv", dest="as_csv", action="store_true", help="Slice-Details als CSV")
    parser.add_argument("--out", default=None, help="Ausgabedatei (default: stdout)")
    args = parser.parse_args()

    report = compute_report(since=args.since)

    if args.as_json:
        output = json.dumps(asdict(report), indent=2, default=str)
    elif args.as_csv:
        output = _to_csv(report)
    else:
        _print_summary(report)
        return

    if args.out:
        Path(args.out).write_text(output, encoding="utf-8")
        print(f"Ausgabe geschrieben: {args.out}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
