"""FSX-003 — das Provenance-Gate darf nicht hinter der Backend-Kaskade verschwinden.

Die Backend-Job-Steps in quality-gate.yml sind strikt sequentiell und brechen
beim ersten Rot ab. Saeße FSX-003 dort hinter Godfile, Drift oder pytest,
waere ein Rueckfall unsichtbar, sobald ein frueherer Schritt bereits rot ist.

Dieser Test liest die YAML als Text — bewusst ohne PyYAML, damit der Job
`fsx-003-gates` bei ``pytest==9.0.3`` allein lauffaehig bleibt.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

WORKFLOW = Path(__file__).resolve().parents[1] / ".github/workflows/quality-gate.yml"


def _job_block(name: str) -> str:
    text = WORKFLOW.read_text(encoding="utf-8")
    pattern = rf"(?ms)^  {re.escape(name)}:\n(.*?)(?=^  [a-z0-9-]+:|\Z)"
    match = re.search(pattern, text)
    assert match, f"Job '{name}' fehlt in quality-gate.yml"
    return match.group(1)


def test_fsx003_ist_ein_eigener_job() -> None:
    block = _job_block("fsx-003-gates")
    assert "needs: [path-guard]" in block
    assert "needs: [backend]" not in block
    assert "needs: [secret-scan]" not in block


def test_fsx003_job_haengt_nicht_hinter_der_backend_kaskade() -> None:
    backend = _job_block("backend")
    assert "fsx-003-gates" not in backend
    assert "needs: [secret-scan]" in backend


def test_fsx003_job_fuehrt_beide_haelften_aus() -> None:
    block = _job_block("fsx-003-gates")
    assert "tests/test_flow_spine_data_provenance.py" in block
    assert "scripts/check_flow_spine_invented_frontend_values.py" in block
    assert "--noconftest" in block
    assert "pytest==9.0.3" in block
