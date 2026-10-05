"""FSX-003 — Frontend-Gate gegen erfundene Anzeigewerte.

Prueft den Scanner, nicht die Masken: das verbotene Muster aus FSX-002
(``?? '92%'`` plus feste Balkenbreite) muss auffallen, strukturelle ``??``
und Layoutbreiten 0 % / 100 % nicht. Der Live-Bestand unter workflow/ muss
sauber sein — sonst ist das Muster zurueck.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts.check_flow_spine_invented_frontend_values import (
    ALLOWED_WIDTH_PERCENTS,
    SCOPE_DIRS,
    iter_scoped_files,
    main,
    scan_paths,
    scan_text,
)

pytestmark = pytest.mark.unit

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_fsx002_muster_wird_erkannt() -> None:
    text = """
      const score = node.kpis[0]?.value ?? '92%'
      return <div style={{ width: '92%' }} className="w-[88%]" />
    """
    findings = scan_text(Path("fake.tsx"), text)
    kinds = {item.kind for item in findings}
    assert "nullish-percent" in kinds
    assert "style-width-percent" in kinds
    assert "tailwind-width-percent" in kinds


def test_nullish_numeric_string_wird_erkannt() -> None:
    findings = scan_text(Path("fake.tsx"), "const n = metric ?? '92'")
    assert any(item.kind == "nullish-numeric-string" for item in findings)


def test_strukturelle_fallbacks_bleiben_erlaubt() -> None:
    text = """
      const selected = nodes.find((n) => n.id === id) ?? nodes[0]
      const rows = node.detail_rows ?? []
      const label = node.label ?? ''
      const count = items.length ?? 0
    """
    assert scan_text(Path("fake.tsx"), text) == []


def test_layoutbreiten_null_und_hundert_bleiben_erlaubt() -> None:
    text = """
      const empty = '0%'
      return <div style={{ width: '0%' }} className="w-[100%]" />
    """
    assert scan_text(Path("fake.tsx"), text) == []
    assert ALLOWED_WIDTH_PERCENTS == {0.0, 100.0}


def test_ausnahmekommentar_gilt_nur_in_derselben_zeile() -> None:
    allowed = "style={{ width: '40%' }} // fsx-invented-ok: Demo-Balken in Story"
    blocked = "style={{ width: '40%' }}"
    assert scan_text(Path("fake.tsx"), allowed) == []
    assert scan_text(Path("fake.tsx"), blocked)


def test_live_workflow_bestand_ist_sauber() -> None:
    files = iter_scoped_files(REPO_ROOT)
    assert files, "Scope-Verzeichnisse muessen existieren"
    findings = scan_paths(files)
    assert findings == [], (
        "FSX-002-Muster ist unter workflow/ zurueck. "
        + ", ".join(f"{item.path.name}:{item.line_no}" for item in findings)
    )


def test_scope_ist_auf_workflow_begrenzt() -> None:
    assert SCOPE_DIRS == (
        Path("packages/frontend-web/src/components/workflow"),
        Path("packages/frontend-web/src/pages/workflow"),
    )


def test_cli_exit_1_auf_treffer(tmp_path: Path) -> None:
    target = (
        tmp_path
        / "packages/frontend-web/src/components/workflow"
        / "FakeSpine.tsx"
    )
    target.parent.mkdir(parents=True)
    target.write_text("{node.kpis[0]?.value ?? '92%'}\n", encoding="utf-8")
    assert main(["--root", str(tmp_path)]) == 1


def test_cli_exit_0_auf_leerem_scope(tmp_path: Path) -> None:
    (
        tmp_path / "packages/frontend-web/src/components/workflow"
    ).mkdir(parents=True)
    (
        tmp_path / "packages/frontend-web/src/pages/workflow"
    ).mkdir(parents=True)
    assert main(["--root", str(tmp_path)]) == 0
