"""
Drift-Gate: Adaptive Fachaktionen YAML ↔ TS-Alias-Spiegel.

Kein Server-Write, keine Secrets. Spiegelt den Vitest-Vertrag
packages/frontend-web/src/__tests__/workspace/fachaktion-alias-parity.test.ts.

Extrahiert FACHAKTION_CATALOG_ALIASES aus fachaktion-resolve.ts per Regex
(keine Frontend-Runtime) und erzwingt action_id- + Alias-Paritaet gegen
config/adaptive_workspace_fachaktionen.yaml.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
YAML_PATH = REPO_ROOT / "config" / "adaptive_workspace_fachaktionen.yaml"
TS_PATH = (
    REPO_ROOT
    / "packages"
    / "frontend-web"
    / "src"
    / "workspace"
    / "fachaktion-resolve.ts"
)


def _load_yaml_aliases() -> dict[str, list[str]]:
    catalog = yaml.safe_load(YAML_PATH.read_text(encoding="utf-8"))
    assert isinstance(catalog, dict)
    actions = catalog.get("actions")
    assert isinstance(actions, list) and actions
    out: dict[str, list[str]] = {}
    for action in actions:
        assert isinstance(action, dict)
        action_id = action.get("action_id")
        assert isinstance(action_id, str) and action_id
        aliases = action.get("aliases") or []
        assert isinstance(aliases, list)
        out[action_id] = [str(alias) for alias in aliases]
    return out


def _load_ts_aliases() -> dict[str, list[str]]:
    text = TS_PATH.read_text(encoding="utf-8")
    match = re.search(
        r"export const FACHAKTION_CATALOG_ALIASES: Record<string, readonly string\[]> = \{([\s\S]*?)\n\}",
        text,
    )
    assert match, "FACHAKTION_CATALOG_ALIASES-Block in fachaktion-resolve.ts nicht gefunden"
    body = match.group(1)
    out: dict[str, list[str]] = {}
    for entry in re.finditer(r"'([^']+)':\s*\[([\s\S]*?)\],", body):
        action_id = entry.group(1)
        aliases = re.findall(r"'([^']*)'", entry.group(2))
        out[action_id] = aliases
    assert out, "keine TS-Alias-Eintraege geparst"
    return out


@pytest.mark.unit
def test_fachaktion_catalog_aliases_yaml_ts_parity() -> None:
    yaml_aliases = _load_yaml_aliases()
    ts_aliases = _load_ts_aliases()

    assert sorted(yaml_aliases) == sorted(ts_aliases)
    assert len(yaml_aliases) >= 15

    for action_id in sorted(yaml_aliases):
        assert ts_aliases[action_id] == yaml_aliases[action_id], action_id
        assert len(set(yaml_aliases[action_id])) == len(yaml_aliases[action_id]), action_id
        assert len(set(ts_aliases[action_id])) == len(ts_aliases[action_id]), action_id


@pytest.mark.unit
def test_fachaktion_alias_keys_are_unique_across_actions() -> None:
    yaml_aliases = _load_yaml_aliases()
    owners: dict[str, str] = {}
    for action_id, aliases in yaml_aliases.items():
        for alias in aliases:
            key = alias.strip().lower()
            assert key, f"leerer Alias bei {action_id}"
            previous = owners.get(key)
            assert previous is None, f"Alias-Kollision '{alias}' ({previous} vs {action_id})"
            owners[key] = action_id
    assert len(owners) >= 40
