from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).parents[1]
SPEC = ROOT / "docs" / "specs" / "feeding"
PACKAGES = SPEC / "work-packages"


def test_feeding_reference_has_all_numbered_chapters() -> None:
    files = {path.name for path in SPEC.glob("[0-1][0-9]-*.md")}
    for number in range(18):
        assert any(name.startswith(f"{number:02d}-") for name in files), number


def test_work_program_contains_240_complete_tdd_packages() -> None:
    documents = sorted(PACKAGES.glob("*.md"))
    assert documents, "work-packages catalog is missing"
    text = "\n".join(path.read_text(encoding="utf-8") for path in documents)
    package_ids = re.findall(r"^## (FEED-WP-\d{3}) — ", text, re.MULTILINE)

    assert len(package_ids) == 240
    assert len(set(package_ids)) == 240
    assert package_ids == [f"FEED-WP-{index:03d}" for index in range(1, 241)]
    assert "TBD" not in text and "TODO" not in text

    sections = re.split(r"(?=^## FEED-WP-\d{3} — )", text, flags=re.MULTILINE)[1:]
    required_labels = (
        "**Nutzen:**", "**Requirements:**", "**Abhaengig von:**", "**Aufwand:**",
        "**Akzeptanz:**", "**Red:**", "**Green:**", "**Refactor:**",
        "**Regression:**", "**Definition of Done:**",
    )
    for section in sections:
        for label in required_labels:
            assert label in section, (section[:30], label)


def test_work_packages_only_reference_known_acceptance_tests() -> None:
    test_catalog = (SPEC / "13-tests.md").read_text(encoding="utf-8")
    known = set(re.findall(r"FEED-T\d{3}", test_catalog))
    package_text = "\n".join(
        path.read_text(encoding="utf-8") for path in PACKAGES.glob("*.md")
    )
    referenced = set(re.findall(r"FEED-T\d{3}", package_text))
    assert len(known) == 200
    assert referenced
    assert referenced <= known
