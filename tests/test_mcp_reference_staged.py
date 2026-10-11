"""Commit contracts: working tree edits must not conceal staged MCP drift."""
import importlib.util
import subprocess
from pathlib import Path

import pytest
import yaml

spec = importlib.util.spec_from_file_location(
    "mcp_reference_generator", Path(__file__).resolve().parents[1] / "scripts/generate_mcp_tool_reference.py"
)
generator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generator)


@pytest.fixture
def repo(tmp_path, monkeypatch):
    subprocess.run(["git", "init", "--quiet", str(tmp_path)], check=True)
    registry = tmp_path / "config/mcp_erp_tools.yaml"
    output = tmp_path / "docs/schnittstellen/mcp-tools.md"
    registry.parent.mkdir(parents=True)
    output.parent.mkdir(parents=True)
    monkeypatch.setattr(generator, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(generator, "REGISTRY", registry)
    monkeypatch.setattr(generator, "OUTPUT", output)
    data = {"tools": [{"tool_id": "logistik.fahrzeug.speichern", "name": "Fahrzeug", "domain": "logistik", "description": "Prüft Mandant → Fahrzeug", "scope": "logistik:write"}]}
    registry.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")
    output.write_text(generator.render(data), encoding="utf-8")
    subprocess.run(["git", "-C", str(tmp_path), "add", "."], check=True)
    return tmp_path, data, registry, output


def test_matching_staged_reference_passes(repo):
    assert generator.main(["--check", "--staged"]) == 0


def test_staged_registry_change_fails_even_when_worktree_reference_is_fixed(repo):
    root, data, registry, output = repo
    data["tools"][0]["scope"] = "fleet:write"
    registry.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")
    subprocess.run(["git", "-C", str(root), "add", str(registry)], check=True)
    output.write_text(generator.render(data), encoding="utf-8")
    assert generator.main(["--check"]) == 0
    assert generator.main(["--check", "--staged"]) == 1


def test_unstaged_registry_wip_does_not_change_commit_verdict(repo):
    _, data, registry, _ = repo
    data["tools"][0]["scope"] = "foreign:wip"
    registry.write_text(yaml.safe_dump(data), encoding="utf-8")
    assert generator.main(["--check"]) == 1
    assert generator.main(["--check", "--staged"]) == 0


def test_missing_staged_reference_fails(repo):
    root, _, _, output = repo
    subprocess.run(["git", "-C", str(root), "rm", "--cached", str(output)], check=True)
    assert output.exists()
    assert generator.main(["--check", "--staged"]) == 1


def test_staged_check_keeps_worktree_and_index_unchanged(repo):
    root, _, _, output = repo
    output.write_text("foreign unstaged edits\n", encoding="utf-8")
    before = (root / ".git/index").read_bytes()
    assert generator.main(["--check", "--staged"]) == 0
    assert output.read_text(encoding="utf-8") == "foreign unstaged edits\n"
    assert (root / ".git/index").read_bytes() == before


def test_staged_generation_is_rejected(repo):
    with pytest.raises(SystemExit) as error:
        generator.main(["--staged"])
    assert error.value.code == 2


def test_commit_hook_enforces_staged_reference_contract():
    hook = (Path(__file__).resolve().parents[1] / "scripts/run-staged-checks.cjs").read_text(encoding="utf-8")
    assert "'config/mcp_erp_tools.yaml'" in hook
    assert "'docs/schnittstellen/mcp-tools.md'" in hook
    assert "['scripts/generate_mcp_tool_reference.py', '--check', '--staged']" in hook
