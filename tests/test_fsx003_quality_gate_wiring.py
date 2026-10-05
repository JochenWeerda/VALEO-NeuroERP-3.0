"""FSX-Gates — Provenance und Belegbindung duerfen nicht hinter der Backend-Kaskade verschwinden.

Die Backend-Job-Steps in quality-gate.yml sind strikt sequentiell und brechen
beim ersten Rot ab. Dieser Test liest die YAML als Text — bewusst ohne PyYAML.
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


def test_fsx_gates_ist_ein_eigener_job() -> None:
    block = _job_block("fsx-gates")
    assert "needs: [path-guard]" in block
    assert "needs: [backend]" not in block
    assert "needs: [secret-scan]" not in block


def test_fsx_gates_haengt_nicht_hinter_der_backend_kaskade() -> None:
    backend = _job_block("backend")
    assert "fsx-gates" not in backend
    assert "fsx-003-gates" not in backend
    assert "needs: [secret-scan]" in backend


def test_fsx_gates_fuehrt_provenance_bindung_und_frontend_aus() -> None:
    block = _job_block("fsx-gates")
    assert "tests/test_flow_spine_data_provenance.py" in block
    assert "tests/test_flow_spine_document_binding.py" in block
    assert "tests/test_flow_spine_footer_steps.py" in block
    assert "tests/test_flow_spine_field_origins.py" in block
    assert "scripts/check_flow_spine_invented_frontend_values.py" in block
    assert "--noconftest" in block
    assert "requirements.txt" in block
