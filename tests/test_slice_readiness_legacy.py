from pathlib import Path
import subprocess

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/ai-slice-readiness-check.cjs"


def readiness(tmp_path: Path, before: str, after: str) -> int:
    def git(*args):
        return subprocess.check_output(["git", "-C", str(tmp_path), *args], text=True)
    folder = tmp_path / "docs/agent-ops/slices"
    folder.mkdir(parents=True)
    path = folder / "OLD.yaml"
    path.write_text(before, encoding="utf-8")
    (folder.parent / "active-workboard.md").write_text("OLD", encoding="utf-8")
    git("init", "-q")
    git("config", "user.name", "Contract Test")
    git("config", "user.email", "contract@example.invalid")
    git("add", ".")
    git("commit", "-qm", "baseline")
    base = git("rev-parse", "HEAD").strip()
    path.write_text(after, encoding="utf-8")
    return subprocess.run(
        ["node", str(SCRIPT), "--changed-only", "--base", base],
        cwd=tmp_path, capture_output=True, timeout=20,
    ).returncode


def test_reine_syntaxreparatur_abgeschlossener_legacy_hat_keinen_erfundenen_harness(tmp_path):
    assert readiness(tmp_path,
        "slice_id: OLD\nstatus: done\ngoal: text\nnotes:\n  - test: text\n---\n",
        "slice_id: OLD\nstatus: done\ngoal: text\nnotes:\n  - >-\n    test: text\n",
    ) == 0


@pytest.mark.parametrize("after", [
    "slice_id: OLD\nstatus: done\ngoal: changed\n",
    "slice_id: OLD\nstatus: in_progress\ngoal: text\n",
])
def test_inhalt_oder_statusaenderung_verlangt_vollen_harness(tmp_path, after):
    assert readiness(tmp_path, "slice_id: OLD\nstatus: done\ngoal: text\n", after) == 1
