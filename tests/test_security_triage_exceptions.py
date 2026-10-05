"""Tests fuer den Ausnahmemechanismus der Security-Triage.

Der Mechanismus darf den Gate nur fuer belegte Einzelfaelle oeffnen. Diese
Tests halten fest, wann er zufallen muss - sie sind der eigentliche Schutz
gegen eine schleichende Aufweichung.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "triage_findings", REPO / "scripts" / "security" / "triage_findings.py"
)
triage = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(triage)


def _valid_entry(**overrides):
    entry = {
        "id": "TEST-001",
        "rule_id": "CVE-2026-00000",
        "scope": {"package": "beispielpaket"},
        "reason": "Ausfuehrlich begruendet, warum der Angriffsweg hier nicht erreichbar ist.",
        "evidence": "Nachpruefbar an Datei X und dem Vertragstest Y im Repository.",
        "no_fix_available": True,
        "review_by": "2099-01-01",
        "owner": "Test",
    }
    entry.update(overrides)
    return entry


def _write(tmp_path: Path, entries) -> Path:
    path = tmp_path / "exc.json"
    path.write_text(json.dumps({"exceptions": entries}), encoding="utf-8")
    return path


@pytest.mark.unit
def test_valid_entry_loads(tmp_path: Path) -> None:
    assert len(triage.load_exceptions(_write(tmp_path, [_valid_entry()]))) == 1


@pytest.mark.unit
def test_missing_file_means_no_exceptions(tmp_path: Path) -> None:
    assert triage.load_exceptions(tmp_path / "fehlt.json") == []


@pytest.mark.unit
@pytest.mark.parametrize("field", list(triage.REQUIRED_EXCEPTION_FIELDS))
def test_missing_required_field_is_rejected(tmp_path: Path, field: str) -> None:
    entry = _valid_entry()
    del entry[field]
    with pytest.raises(triage.ExceptionConfigError):
        triage.load_exceptions(_write(tmp_path, [entry]))


@pytest.mark.unit
def test_exception_requires_absent_vendor_fix(tmp_path: Path) -> None:
    """Gibt es einen Herstellerfix, ist der Befund zu beheben, nicht auszunehmen."""
    with pytest.raises(triage.ExceptionConfigError):
        triage.load_exceptions(_write(tmp_path, [_valid_entry(no_fix_available=False)]))


@pytest.mark.unit
@pytest.mark.parametrize(
    "bad",
    [
        {"rule_id": "CVE-*"},
        {"scope": {"package": "chroma*"}},
        {"scope": {}},
        {"scope": {"package": "   "}},
    ],
)
@pytest.mark.filterwarnings("ignore")
def test_wildcards_and_empty_scope_are_rejected(tmp_path: Path, bad: dict) -> None:
    with pytest.raises(triage.ExceptionConfigError):
        triage.load_exceptions(_write(tmp_path, [_valid_entry(**bad)]))


@pytest.mark.unit
@pytest.mark.parametrize("field", ["reason", "evidence"])
def test_hollow_justification_is_rejected(tmp_path: Path, field: str) -> None:
    with pytest.raises(triage.ExceptionConfigError):
        triage.load_exceptions(_write(tmp_path, [_valid_entry(**{field: "passt schon"})]))


@pytest.mark.unit
def test_broken_json_aborts_instead_of_silently_passing(tmp_path: Path) -> None:
    path = tmp_path / "exc.json"
    path.write_text("{kaputt", encoding="utf-8")
    with pytest.raises(triage.ExceptionConfigError):
        triage.load_exceptions(path)


def _finding(rule_id="CVE-2026-00000", match="beispielpaket 1.0", severity="CRITICAL"):
    return {"rule_id": rule_id, "match": match, "severity": severity, "file": "x.txt"}


@pytest.mark.unit
def test_matching_finding_is_excluded_from_gate() -> None:
    findings = [_finding()]
    expired = triage.apply_exceptions(findings, [_valid_entry()], "2026-09-11")
    assert expired == []
    assert findings[0]["gate_excluded"] is True
    assert findings[0]["exception"]["id"] == "TEST-001"


@pytest.mark.unit
def test_expired_exception_no_longer_covers() -> None:
    """Nach dem Ueberpruefungsdatum faellt der Gate von selbst wieder zu."""
    findings = [_finding()]
    expired = triage.apply_exceptions(
        findings, [_valid_entry(review_by="2026-01-01")], "2026-09-11"
    )
    assert [e["id"] for e in expired] == ["TEST-001"]
    assert findings[0]["gate_excluded"] is False
    assert findings[0]["exception"]["expired"] is True


@pytest.mark.unit
@pytest.mark.parametrize(
    "finding",
    [
        _finding(rule_id="CVE-2026-99999"),
        _finding(match="anderespaket 1.0"),
    ],
)
def test_exception_does_not_leak_to_other_findings(finding: dict) -> None:
    triage.apply_exceptions([finding], [_valid_entry()], "2026-09-11")
    assert not finding.get("gate_excluded")
    assert "exception" not in finding


@pytest.mark.unit
def test_repository_catalog_is_valid() -> None:
    """Der echte Katalog muss jederzeit die eigenen Regeln erfuellen."""
    entries = triage.load_exceptions()
    for entry in entries:
        assert entry["no_fix_available"] is True
        assert len(str(entry["reason"]).strip()) >= 30
