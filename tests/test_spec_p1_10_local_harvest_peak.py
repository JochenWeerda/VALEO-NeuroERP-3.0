"""SPEC-P1-10: lokales Erntepeak-Lasttest-Profil ist deklarativ vorhanden."""

from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tests" / "load" / "harvest-peak.js"
RUNNER_PS1 = ROOT / "scripts" / "loadtest" / "run_harvest_peak_local.ps1"
RUNNER_SH = ROOT / "scripts" / "loadtest" / "run_harvest_peak_local.sh"


def test_harvest_peak_defines_local_and_smoke_profiles():
    text = SCRIPT.read_text(encoding="utf-8")
    assert "PROFILE" in text
    assert "local" in text
    assert "smoke" in text
    assert "buildOptions" in text
    assert "00000000-0000-0000-0000-000000000001" in text


def test_local_runners_exist():
    assert RUNNER_PS1.is_file()
    assert RUNNER_SH.is_file()
    ps1 = RUNNER_PS1.read_text(encoding="utf-8")
    assert "PROFILE=local" in ps1 or 'Profile = ' in ps1
    assert "harvest-peak.js" in ps1
    sh = RUNNER_SH.read_text(encoding="utf-8")
    assert "PROFILE=" in sh
    assert "harvest-peak.js" in sh
