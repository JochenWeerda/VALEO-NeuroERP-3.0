"""
Agent-CRUD-Vertrag Portal-Feldbuch: stabile Pfade + operation_id für AI-Agenten.
"""
from __future__ import annotations

import os
import sys

_ROOT = os.path.join(os.path.dirname(__file__), "..")
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from app.api.v1.endpoints import portal_feldbuch as pf  # noqa: E402

# Kanonische Agent-Surface (prefix /api/v1/portal wird im Router gesetzt)
REQUIRED = {
    ("GET", "/feldbuch/schlaege", "portal_feldbuch_list_schlaege"),
    ("POST", "/feldbuch/schlaege", "portal_feldbuch_create_schlag"),
    ("GET", "/feldbuch/schlaege/{schlag_id}", "portal_feldbuch_get_schlag"),
    ("PUT", "/feldbuch/schlaege/{schlag_id}", "portal_feldbuch_update_schlag"),
    ("DELETE", "/feldbuch/schlaege/{schlag_id}", "portal_feldbuch_delete_schlag"),
    ("GET", "/feldbuch/massnahmen", "portal_feldbuch_list_massnahmen"),
    ("POST", "/feldbuch/massnahmen", "portal_feldbuch_create_massnahme"),
    ("GET", "/feldbuch/massnahmen/{massnahme_id}", "portal_feldbuch_get_massnahme"),
    ("PUT", "/feldbuch/massnahmen/{massnahme_id}", "portal_feldbuch_update_massnahme"),
    ("DELETE", "/feldbuch/massnahmen/{massnahme_id}", "portal_feldbuch_delete_massnahme"),
}


def test_agent_crud_operation_ids_and_paths():
    found: set[tuple[str, str, str]] = set()
    for route in pf.router.routes:
        methods = getattr(route, "methods", None) or set()
        path = getattr(route, "path", "")
        op_id = getattr(route, "operation_id", None)
        for method in methods:
            if method in ("HEAD", "OPTIONS"):
                continue
            if op_id:
                found.add((method, path, op_id))
    missing = REQUIRED - found
    assert not missing, f"Fehlende Agent-CRUD-Routen: {sorted(missing)}"
