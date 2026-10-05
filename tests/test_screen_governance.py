"""Screen-Governance auf den drei Referenzmasken. Kein App-Import."""

from app.core.screen_definitions_capture import (
    build_fuhrpark_fahrzeuge_screen_definition,
    build_logistik_tourenplanung_screen_definition,
    build_transporte_fahrer_screen_definition,
)
from app.core.screen_governance import (
    derived_screen_type,
    governance_errors,
    ux_lint,
    validate_screen_definition,
)


def test_referenzmasken_sind_schema_1_ohne_zweites_format() -> None:
    screens = [
        build_logistik_tourenplanung_screen_definition(),
        build_transporte_fahrer_screen_definition(),
        build_fuhrpark_fahrzeuge_screen_definition(),
    ]
    assert [derived_screen_type(screen) for screen in screens] == ["DASHBOARD", "MASTER_DETAIL", "MASTER_DETAIL"]
    for screen in screens:
        assert screen["schemaVersion"] == 1
        assert governance_errors(screen) == []
        assert not any(finding["severity"] == "error" for finding in ux_lint(screen))


def test_unbekannter_befehl_und_paralleles_format_scheiden_in_ci() -> None:
    screen = build_fuhrpark_fahrzeuge_screen_definition()
    screen["screenType"] = "LIST"
    screen["actions"][0]["command"] = "vehicle.delete"
    errors = validate_screen_definition(screen)
    assert any("screenType" in error for error in errors)
    assert any("unknown action registry entry" in error for error in errors)
    assert any("vehicle.create" in error for error in errors)


def test_ux_lint_meldet_drei_primaeraktionen_und_storno_ohne_bestaetigung() -> None:
    screen = build_fuhrpark_fahrzeuge_screen_definition()
    screen["actions"] = [
        {"key": "a", "label": "Eins", "kind": "primary", "command": "vehicle.create", "dangerLevel": "safe"},
        {"key": "b", "label": "Zwei", "kind": "primary", "dangerLevel": "safe"},
        {"key": "c", "label": "Drei", "kind": "primary", "dangerLevel": "destructive"},
    ]
    codes = {finding["code"] for finding in ux_lint(screen) if finding["severity"] == "error"}
    assert codes == {"UX001", "UX014"}
