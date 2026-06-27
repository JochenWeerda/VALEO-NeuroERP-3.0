"""Wave 94 — Unit-Tests fuer neuro_tool_broker, lkv_pipeline (pure domain functions)."""

from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# neuro_tool_broker — get_process_kernel_mcp_tools  (pure registry)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_get_process_kernel_mcp_tools_returns_registry() -> None:
    from app.services.neuro_tool_broker import get_process_kernel_mcp_tools
    result = get_process_kernel_mcp_tools()
    assert result is not None


@pytest.mark.unit
def test_get_process_kernel_mcp_tools_has_tools() -> None:
    from app.services.neuro_tool_broker import get_process_kernel_mcp_tools
    result = get_process_kernel_mcp_tools()
    assert hasattr(result, "tools")
    assert len(result.tools) > 0


@pytest.mark.unit
def test_get_process_kernel_mcp_tools_have_required_fields() -> None:
    from app.services.neuro_tool_broker import get_process_kernel_mcp_tools
    result = get_process_kernel_mcp_tools()
    for tool in result.tools:
        assert hasattr(tool, "tool_name")
        assert hasattr(tool, "domain")
        assert hasattr(tool, "operation")


@pytest.mark.unit
def test_get_process_kernel_mcp_tools_covers_multiple_domains() -> None:
    from app.services.neuro_tool_broker import get_process_kernel_mcp_tools
    result = get_process_kernel_mcp_tools()
    domains = {t.domain for t in result.tools}
    assert len(domains) >= 2


@pytest.mark.unit
def test_get_process_kernel_mcp_tools_has_schema_version() -> None:
    from app.services.neuro_tool_broker import get_process_kernel_mcp_tools
    result = get_process_kernel_mcp_tools()
    assert hasattr(result, "schema_version")


@pytest.mark.unit
def test_get_process_kernel_mcp_tools_tool_names_unique() -> None:
    from app.services.neuro_tool_broker import get_process_kernel_mcp_tools
    result = get_process_kernel_mcp_tools()
    names = [t.tool_name for t in result.tools]
    assert len(names) == len(set(names))


# ---------------------------------------------------------------------------
# lkv_pipeline — resolve_postal_codes  (pure in-place mutation)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_resolve_postal_codes_resolves_from_map() -> None:
    from app.services.lkv_pipeline import resolve_postal_codes
    rows = [{"ort": "Oldenburg", "postal_code": None}]
    city_plz_map = {"oldenburg": "26121"}
    stats = resolve_postal_codes(rows, city_plz_map)
    assert rows[0]["postal_code"] == "26121"
    assert rows[0]["postal_code_source"] == "resolved_gemeinde"


@pytest.mark.unit
def test_resolve_postal_codes_existing_plz_not_overwritten() -> None:
    from app.services.lkv_pipeline import resolve_postal_codes
    rows = [{"ort": "Berlin", "postal_code": "10115"}]
    city_plz_map = {"berlin": "99999"}
    stats = resolve_postal_codes(rows, city_plz_map)
    assert rows[0]["postal_code"] == "10115"
    assert rows[0]["postal_code_source"] == "pdf"


@pytest.mark.unit
def test_resolve_postal_codes_unknown_ort_marks_unresolved() -> None:
    from app.services.lkv_pipeline import resolve_postal_codes
    rows = [{"ort": "UnknownCity", "postal_code": None}]
    stats = resolve_postal_codes(rows, {})
    assert rows[0]["postal_code_source"] == "unresolved"


@pytest.mark.unit
def test_resolve_postal_codes_returns_stats_dict() -> None:
    from app.services.lkv_pipeline import resolve_postal_codes
    rows = [
        {"ort": "Berlin", "postal_code": "10115"},
        {"ort": "Hannover", "postal_code": None},
        {"ort": "Unknown", "postal_code": None},
    ]
    city_plz_map = {"hannover": "30159"}
    stats = resolve_postal_codes(rows, city_plz_map)
    assert isinstance(stats, dict)
    assert "pdf" in stats
    assert "resolved_gemeinde" in stats
    assert "unresolved" in stats


@pytest.mark.unit
def test_resolve_postal_codes_stats_counts_are_correct() -> None:
    from app.services.lkv_pipeline import resolve_postal_codes
    rows = [
        {"ort": "Berlin", "postal_code": "10115"},
        {"ort": "Hamburg", "postal_code": None},
        {"ort": "Unknown", "postal_code": None},
    ]
    city_plz_map = {"hamburg": "20095"}
    stats = resolve_postal_codes(rows, city_plz_map)
    assert stats["pdf"] == 1
    assert stats["resolved_gemeinde"] == 1
    assert stats["unresolved"] == 1


@pytest.mark.unit
def test_resolve_postal_codes_empty_rows_returns_zero_stats() -> None:
    from app.services.lkv_pipeline import resolve_postal_codes
    stats = resolve_postal_codes([], {})
    assert stats["pdf"] == 0
    assert stats["resolved_gemeinde"] == 0
    assert stats["unresolved"] == 0


@pytest.mark.unit
def test_resolve_postal_codes_modifies_in_place() -> None:
    from app.services.lkv_pipeline import resolve_postal_codes
    rows = [{"ort": "Köln", "postal_code": None}]
    city_plz_map = {"koeln": "50667"}
    original_row = rows[0]
    resolve_postal_codes(rows, city_plz_map)
    # Same object modified in-place
    assert rows[0] is original_row
