"""Keep fallback commands and fields derived from the canonical registry."""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def test_capture_fallbacks_are_current():
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/generate_capture_screens.py"), "--check"],
        cwd=ROOT, capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
