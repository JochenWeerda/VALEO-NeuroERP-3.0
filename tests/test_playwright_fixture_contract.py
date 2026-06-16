import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_playwright_fixtures_use_destructured_dependency_arguments():
    fixture_root = ROOT / "playwright-tests"
    invalid = []

    for path in fixture_root.rglob("*.ts"):
        text = path.read_text(encoding="utf-8")
        if re.search(r"async\s*\(\s*[A-Za-z_$][A-Za-z0-9_$]*\s*,\s*use\s*\)", text):
            invalid.append(path.relative_to(ROOT).as_posix())

    assert invalid == []

    setup = (fixture_root / "fixtures" / "testSetup.ts").read_text(
        encoding="utf-8"
    )
    assert "tenant: async ({}, use)" in setup
    assert "00000000-0000-0000-0000-000000000001" in setup
