import json
from pathlib import Path

from scripts.generate_release_compatibility_matrix import build_matrix, render_markdown


ROOT = Path(__file__).resolve().parents[1]


def test_release_toolchain_pins_file_exists():
    pins = json.loads((ROOT / "config/release-toolchain-pins.json").read_text(encoding="utf-8"))
    assert pins["api_contract"] == "/api/v1"
    assert pins["python_packages"]["pytest-cov"] == "7.1.0"
    assert "requirements.txt" in pins["requirements_files_strict"]


def test_compatibility_matrix_contains_required_dimensions():
    matrix = build_matrix(git_sha="a" * 40)

    assert matrix["git_sha"] == "a" * 40
    assert matrix["app_version"]
    assert matrix["database_revision"]
    assert matrix["api_contract"] == "/api/v1"
    assert matrix["runtime"]["python"] == "3.11"
    assert matrix["runtime"]["node"] == "20"
    assert matrix["toolchain_pins"]["pytest-cov"] == "7.1.0"
    assert matrix["images"]["backend_digest"] == "not-built"
    assert matrix["images"]["frontend_digest"] == "not-built"


def test_compatibility_matrix_markdown_renders_key_rows():
    matrix = build_matrix(git_sha="b" * 40)
    markdown = render_markdown(matrix)

    assert "Database revision" in markdown
    assert matrix["database_revision"] in markdown
    assert "pytest-cov" in markdown


def test_quality_gate_uses_pinned_toolchain_only():
    workflow = (ROOT / ".github/workflows/quality-gate.yml").read_text(encoding="utf-8")
    assert "pip install pytest-cov" not in workflow
    assert "check_toolchain_pins.py" in workflow
    assert "generate_release_compatibility_matrix.py" in workflow


def test_release_gates_upload_compatibility_matrix():
    workflow = (ROOT / ".github/workflows/release-gates.yml").read_text(encoding="utf-8")
    assert "generate_release_compatibility_matrix.py" in workflow
    assert "release-compatibility-matrix.json" in workflow
