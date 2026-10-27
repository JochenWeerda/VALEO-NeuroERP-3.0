"""Verifier für Made-by-Studio-Gates — Struktur und Batch-Lauf."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from app.services.made_by_studio_gates import (
    CANONICAL_LAYOUT_KINDS,
    _screen_ids_from_source,
    check_gate_a,
    check_gate_b,
    check_gate_e,
    evaluate_all,
    load_registered_definitions,
    resolve_layout_kind,
    summarize,
)


def test_registered_inventory_non_empty():
    defs = load_registered_definitions()
    assert len(defs) >= 100
    # Stamm-Factories werden auch beim isolierten Gate-Aufruf registriert.
    assert {"crm/campaign", "fibu/anlage", "verkauf/kunde"} <= defs.keys()


def test_registered_inventory_is_independent_of_stamm_import_order():
    repo = Path(__file__).resolve().parents[1]

    def ids_after(prelude: str) -> list[str]:
        program = "\n".join((
            prelude,
            "from app.services.made_by_studio_gates import load_registered_definitions",
            "print('STUDIO_REGISTRY=' + json.dumps(sorted(load_registered_definitions())))",
        ))
        result = subprocess.run(
            [sys.executable, "-c", "import json\n" + program],
            cwd=repo,
            check=True,
            capture_output=True,
            text=True,
            timeout=90,
        )
        line = next(line for line in result.stdout.splitlines() if line.startswith("STUDIO_REGISTRY="))
        return json.loads(line.removeprefix("STUDIO_REGISTRY="))

    cold_ids = ids_after("")
    warm_ids = ids_after("from app.core.screen_definitions_stamm import STAMM_SCREEN_BUILDERS")
    assert cold_ids == warm_ids
    assert {"crm/campaign", "fibu/anlage", "waage/wiegeschein"} <= set(cold_ids)


def test_resolve_layout_kind_known_floorplans():
    for floorplan, expected in (
        ("worklist", "worklist"),
        ("objectPage", "objectPage"),
        ("cockpit", "overviewPage"),
        ("wizard", "wizard"),
        ("analyticalList", "listReport"),
    ):
        kind = resolve_layout_kind({"layout": {"floorplan": floorplan}, "mode": "detail"})
        assert kind == expected
        assert kind in CANONICAL_LAYOUT_KINDS


def test_gate_a_rejects_worklist_with_anchors():
    definition = {
        "schemaVersion": 1,
        "id": "test/worklist",
        "domain": "test",
        "mode": "list",
        "title": "Test",
        "layout": {"floorplan": "worklist", "sectionNavigation": "anchors", "density": "compact", "contextRail": "none"},
        "adapter": {"type": "native", "sourceId": "test/worklist", "temporary": False},
        "dataSources": [],
        "tables": [],
        "actions": [],
        "agentContract": {"businessPurpose": "Test", "testSelectors": {"screenRoot": "[data-testid='x']"}},
    }
    result = check_gate_a(definition)
    assert not result.passed
    assert any("worklist_darf_keine" in i for i in result.issues)


def test_gate_b_requires_permission_on_mutating_action():
    definition = {
        "schemaVersion": 1,
        "id": "test/action",
        "domain": "test",
        "mode": "list",
        "title": "Test",
        "layout": {"floorplan": "worklist", "density": "compact", "contextRail": "none"},
        "adapter": {"type": "native", "sourceId": "test/action", "temporary": False},
        "dataSources": [{"key": "list", "endpoint": "/api/v1/test/items"}],
        "tables": [{
            "key": "list",
            "label": "Liste",
            "dataSourceKey": "list",
            "serverPagination": True,
            "columns": [{"key": "name", "label": "Name"}, {"key": "status", "label": "Status"}],
        }],
        "actions": [{"key": "delete", "label": "Löschen", "dangerLevel": "high", "commandEndpoint": "/api/v1/test/items/{id}/actions/delete"}],
        "agentContract": {"businessPurpose": "Test", "testSelectors": {"screenRoot": "[data-testid='x']"}},
    }
    result = check_gate_b(definition)
    assert not result.passed
    assert any("aktion_ohne_permission" in i for i in result.issues)


def test_gate_e_unknown_screen_fails():
    assert not check_gate_e("definitiv/nicht/runtime-verdrahtet").passed


def test_gate_e_accepts_stamm_listen_alias_for_legacy_worklist():
    assert check_gate_e("transporte/fahrer").passed


def test_runtime_evidence_resolves_both_visible_conditional_studio_definitions():
    source = """
    const screenId = comparisonId ? 'platform/studio-history-diff' : 'platform/studio-history'
    const schema = useScreenDefinition(screenId)
    const runtime = useUniversalMaskRuntime({ screenId, schema: schema.data })
    return <UniversalMaskRenderer plan={runtime.plan} />
    """
    assert {"platform/studio-history", "platform/studio-history-diff"} <= _screen_ids_from_source(source)
    assert not {"platform/studio-history", "platform/studio-history-diff"} & _screen_ids_from_source(
        source.replace("useScreenDefinition(screenId)", "useScreenDefinition('other')")
    )


def test_real_studio_history_runtime_is_wired():
    assert check_gate_e("platform/studio-history").passed
    assert check_gate_e("platform/studio-history-diff").passed


@pytest.mark.parametrize("gate", ["A", "B", "C", "E"])
def test_batch_evaluate_runs_for_all_gates(gate):
    reports = evaluate_all()
    assert len(reports) >= 100
    assert all(gate in r.gates for r in reports)


def test_summarize_matches_reports():
    reports = evaluate_all()
    summary = summarize(reports)
    assert summary["total"] == len(reports)
    for gate in ("A", "B", "C", "E"):
        assert summary["passed"][gate] + len(summary["failed_ids"][gate]) == summary["total"]
