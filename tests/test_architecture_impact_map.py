"""Unit-Tests fuer Architecture Impact Map (ohne DB, ohne Generator-Ausfuehrung)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = REPO_ROOT / "scripts"
FIXTURES = Path(__file__).resolve().parent / "fixtures" / "architecture_impact"
MAP_PATH = REPO_ROOT / "config" / "architecture-impact-map.yaml"

sys.path.insert(0, str(SCRIPTS))

from architecture_impact_map import (  # noqa: E402
    KNOWN_REGISTER_IDS,
    ImpactMapError,
    load_map,
    match_paths,
)

REQUIRED_CLASS_IDS = frozenset(
    {
        "api-router",
        "service-stem",
        "migration-schema",
        "table-consumer",
        "baseline-improvement",
        "frontend-masks",
        "status-process-studio",
        "finance-gobd",
        "c4-container-adr",
        "agent-handbuch-docs",
    }
)

PR232_REFS = frozenset({"R1b", "R2b", "R3b", "R4a", "R5"})


def _fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def test_map_loads_with_ten_required_classes():
    impact_map = load_map(MAP_PATH)
    ids = {c.id for c in impact_map.classes}
    assert REQUIRED_CLASS_IDS <= ids
    assert len(impact_map.classes) >= 10


def test_pr232_refs_documented_in_map():
    impact_map = load_map(MAP_PATH)
    refs = {ref for cls in impact_map.classes for ref in cls.pr232_refs}
    assert PR232_REFS <= refs


def test_schema_rejects_missing_required_field(tmp_path: Path):
    raw = yaml.safe_load(MAP_PATH.read_text(encoding="utf-8"))
    del raw["classes"][0]["description"]
    bad = tmp_path / "bad-map.yaml"
    bad.write_text(yaml.safe_dump(raw), encoding="utf-8")
    with pytest.raises(ImpactMapError, match="fehlende Pflichtfelder"):
        load_map(bad)


def test_schema_rejects_unknown_register_id(tmp_path: Path):
    raw = yaml.safe_load(MAP_PATH.read_text(encoding="utf-8"))
    raw["classes"][0]["register_ids"] = ["Nicht-Existierendes-Register"]
    bad = tmp_path / "bad-register.yaml"
    bad.write_text(yaml.safe_dump(raw), encoding="utf-8")
    with pytest.raises(ImpactMapError, match="unbekannte register_ids"):
        load_map(bad)


def test_known_register_ids_match_vor_push():
    """Whitelist darf nicht von vor_push.REGISTER abdriften (Import erlaubt, kein Wire)."""
    sys.path.insert(0, str(SCRIPTS))
    from vor_push import REGISTER

    live = {row[0] for row in REGISTER}
    assert live == set(KNOWN_REGISTER_IDS), (
        f"Whitelist drift: map-only={KNOWN_REGISTER_IDS - live} "
        f"vor_push-only={live - KNOWN_REGISTER_IDS}"
    )


def test_all_map_register_ids_are_known():
    impact_map = load_map(MAP_PATH)
    for cls in impact_map.classes:
        for rid in cls.register_ids:
            assert rid in KNOWN_REGISTER_IDS


@pytest.mark.parametrize(
    "fixture_name",
    [
        "api_only.json",
        "service_stem.json",
        "migration.json",
        "rls_consumer.json",
        "baseline_touch.json",
        "multi_class.json",
        "unmapped_structural.json",
    ],
)
def test_fixture_expectations(fixture_name: str):
    data = _fixture(fixture_name)
    report = match_paths(data["paths"], map_path=MAP_PATH)
    ids = set(report.class_ids)

    if "expect_class_ids" in data:
        assert ids == set(data["expect_class_ids"])
    if "expect_class_ids_contains" in data:
        assert set(data["expect_class_ids_contains"]) <= ids
    if "forbid_sole_class" in data:
        sole = data["forbid_sole_class"]
        assert not (ids == {sole}), f"{sole} darf nicht einzige Klasse sein"
        assert sole not in ids or len(ids) > 1
    if "expect_min_classes" in data:
        assert len(ids) >= data["expect_min_classes"]
    if "expect_requires_db" in data:
        assert report.requires_db is data["expect_requires_db"]
    if "expect_unmapped_structural" in data:
        assert report.unmapped_structural is data["expect_unmapped_structural"]
    if "expect_checks_dbfree_contains" in data:
        for item in data["expect_checks_dbfree_contains"]:
            assert item in report.checks_dbfree
    if "expect_register_ids_contains" in data:
        assert set(data["expect_register_ids_contains"]) <= set(report.register_ids)
    if "expect_pr232_refs" in data:
        assert set(data["expect_pr232_refs"]) <= set(report.pr232_refs)
    if "expect_pr232_refs_contains" in data:
        assert set(data["expect_pr232_refs_contains"]) <= set(report.pr232_refs)
    if "expect_hints_contains_any" in data:
        joined = " ".join(report.hints)
        assert any(token in joined for token in data["expect_hints_contains_any"])


def test_api_only_not_migration_schema_db_duty():
    data = _fixture("api_only.json")
    report = match_paths(data["paths"], map_path=MAP_PATH)
    assert "api-router" in report.class_ids
    assert "migration-schema" not in report.class_ids
    assert report.requires_db is False
    assert any("generate_openapi.py --check" in c for c in report.checks_dbfree)


def test_migration_requires_db():
    report = match_paths(
        ["alembic/versions/self_billing_m3_20261127.py"],
        map_path=MAP_PATH,
    )
    assert "migration-schema" in report.class_ids
    assert report.requires_db is True


def test_union_of_multiple_paths():
    report = match_paths(
        [
            "app/api/v1/endpoints/self_billing.py",
            "app/services/self_billing_buchung.py",
            "alembic/versions/self_billing_m3_20261127.py",
        ],
        map_path=MAP_PATH,
    )
    assert len(report.class_ids) >= 3
    assert {"api-router", "service-stem", "migration-schema"} <= set(report.class_ids)


def test_unmapped_structural_flag():
    report = match_paths(["app/obscure/new_thing.py"], map_path=MAP_PATH)
    assert report.unmapped_structural is True
    assert report.class_ids == []
    assert report.unmapped_paths == ["app/obscure/new_thing.py"]


def test_non_structural_unmapped_not_flagged():
    report = match_paths(["README.md", "docs/readme-only.md"], map_path=MAP_PATH)
    assert report.unmapped_structural is False
    assert report.unmapped_paths == []


def test_match_paths_to_dict_keys():
    report = match_paths(
        ["config/business_time_usage_baseline.json"],
        map_path=MAP_PATH,
    )
    payload = report.to_dict()
    for key in (
        "classes",
        "class_ids",
        "generators",
        "register_ids",
        "requires_db",
        "unmapped_structural",
        "checks_dbfree",
    ):
        assert key in payload
