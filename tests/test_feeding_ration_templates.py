from __future__ import annotations

import pytest

from app.agrar.rations.ration_templates import (
    RationTemplateValidationError,
    normalize_template_name,
    validate_copy_reason,
)
from app.core.screen_definitions import get_screen_definition


def test_template_name_and_copy_reason_are_normalized_and_auditable() -> None:
    assert normalize_template_name("  Frischmelker   Sommer  ") == "Frischmelker Sommer"
    assert validate_copy_reason("  Anpassung   nach neuer Analyse  ") == "Anpassung nach neuer Analyse"


@pytest.mark.parametrize("value", ["", "   "])
def test_empty_template_name_is_rejected(value: str) -> None:
    with pytest.raises(RationTemplateValidationError, match="erforderlich"):
        normalize_template_name(value)


def test_short_copy_reason_is_rejected() -> None:
    with pytest.raises(RationTemplateValidationError, match="mindestens 10"):
        validate_copy_reason("zu kurz")


def test_template_migration_guards_immutable_records() -> None:
    migration = open("alembic/versions/feed_editor_templates_20260716.py", encoding="utf-8").read()
    assert "source_ration_version_id" in migration
    assert "BEFORE UPDATE OR DELETE" in migration
    assert "guard_immutable_ration_template" in migration


def test_business_file_is_a_native_meridian_object_page() -> None:
    definition = get_screen_definition("agrar/feeding-business")
    assert definition["adapter"] == {
        "type": "native", "sourceId": "agrar/feeding-business", "temporary": False,
    }
    assert definition["layout"]["floorplan"] == "objectPage"
    assert definition["layout"]["contextRail"] == "findings"
    assert [tab["key"] for tab in definition["tabs"]] == [
        "overview", "groups", "rations", "findings", "templates",
    ]
    assert {action["key"] for action in definition["actions"]} == {"create_template", "apply_template"}
