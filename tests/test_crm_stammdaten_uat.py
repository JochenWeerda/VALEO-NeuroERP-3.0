"""DOM-CRM-004.5 — UAT-Skript Vertrags- und Dry-Run-Tests."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
UAT_PATH = REPO_ROOT / "scripts" / "uat" / "crm_stammdaten_lifecycle_uat.py"


def _load_uat_module():
    spec = importlib.util.spec_from_file_location("crm_stammdaten_lifecycle_uat", UAT_PATH)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.mark.unit
def test_crm_uat_module_loads():
    mod = _load_uat_module()
    assert callable(mod.run)


@pytest.mark.integration
def test_crm_stammdaten_uat_dry_run():
    """Gegen laufendes Backend; skip wenn API nicht erreichbar."""
    mod = _load_uat_module()
    try:
        result = mod.run(execute=False)
    except (mod.UatFailure, TimeoutError, OSError) as exc:
        # Ohne laufendes Backend laeuft der Aufruf in einen Socket-Timeout;
        # der wirft TimeoutError/OSError, nicht UatFailure. Ohne diese Zweige
        # ist der Test rot statt uebersprungen — entgegen der Zusage oben.
        pytest.skip(f"Backend nicht erreichbar: {exc}")
    assert result.get("status") == "dry_run"
