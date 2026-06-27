"""Wave 96 — Unit-Tests fuer prompt_pack_registry, sales_match_service (pure domain functions)."""

from __future__ import annotations

import pytest
from decimal import Decimal


# ---------------------------------------------------------------------------
# Helper: create a valid PromptPack
# ---------------------------------------------------------------------------

def _make_prompt_pack(key="test_agent"):
    from app.services.prompt_pack_registry import PromptPack
    return PromptPack(
        prompt_pack_key=key,
        role_key="assistant",
        mission="Testassistent fuer Unit-Tests",
        scope="Unit-Testing fuer VALEO-Agentenrahmen, kein Produktivbetrieb",
        output_schema="text/plain: Eine Antwort als Klartext",
    )


# ---------------------------------------------------------------------------
# prompt_pack_registry — in-memory prompt pack lifecycle
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_register_prompt_pack_returns_dict() -> None:
    from app.services.prompt_pack_registry import register_prompt_pack
    result = register_prompt_pack(_make_prompt_pack("wave96_basic"), tenant_id="T-WAVE96")
    assert isinstance(result, dict)
    assert "id" in result


@pytest.mark.unit
def test_register_prompt_pack_key_preserved() -> None:
    from app.services.prompt_pack_registry import register_prompt_pack
    result = register_prompt_pack(_make_prompt_pack("wave96_key"), tenant_id="T-WAVE96")
    assert result["prompt_pack_key"] == "wave96_key"


@pytest.mark.unit
def test_list_prompt_packs_empty_for_unknown_tenant() -> None:
    from app.services.prompt_pack_registry import list_prompt_packs
    result = list_prompt_packs("T-NONEXISTENT-XYZ-WAVE96")
    assert isinstance(result, list)
    assert len(result) == 0


@pytest.mark.unit
def test_list_prompt_packs_after_register() -> None:
    from app.services.prompt_pack_registry import register_prompt_pack, list_prompt_packs
    register_prompt_pack(_make_prompt_pack("wave96_list_test"), tenant_id="T-WAVE96-LIST")
    packs = list_prompt_packs("T-WAVE96-LIST")
    assert len(packs) >= 1


@pytest.mark.unit
def test_get_active_prompt_pack_after_register() -> None:
    from app.services.prompt_pack_registry import register_prompt_pack, get_active_prompt_pack
    register_prompt_pack(_make_prompt_pack("wave96_active"), tenant_id="T-WAVE96-ACTIVE")
    active = get_active_prompt_pack("wave96_active", "T-WAVE96-ACTIVE")
    assert active is not None
    assert active["prompt_pack_key"] == "wave96_active"


@pytest.mark.unit
def test_get_active_prompt_pack_none_for_unknown() -> None:
    from app.services.prompt_pack_registry import get_active_prompt_pack
    result = get_active_prompt_pack("nonexistent_pack_xyz", "T-UNKNOWN")
    assert result is None


@pytest.mark.unit
def test_select_prompt_pack_variant_returns_entry() -> None:
    from app.services.prompt_pack_registry import register_prompt_pack, select_prompt_pack_variant
    register_prompt_pack(_make_prompt_pack("wave96_variant"), tenant_id="T-WAVE96-VAR")
    result = select_prompt_pack_variant("wave96_variant", "T-WAVE96-VAR", seed="session-42")
    assert result is not None
    assert result["prompt_pack_key"] == "wave96_variant"


@pytest.mark.unit
def test_list_active_variants_returns_list() -> None:
    from app.services.prompt_pack_registry import register_prompt_pack, list_active_variants
    register_prompt_pack(_make_prompt_pack("wave96_variants_list"), tenant_id="T-WAVE96-VL")
    result = list_active_variants("wave96_variants_list", "T-WAVE96-VL")
    assert isinstance(result, list)
    assert len(result) >= 1


# ---------------------------------------------------------------------------
# sales_match_service — match_position, match_summary
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_sales_match_position_vollstaendig() -> None:
    from app.services.sales_match_service import match_position
    result = match_position(Decimal("100"), Decimal("100"), toleranz_pct=Decimal("2"))
    assert result["status"] == "vollstaendig"
    assert result["abweichung"] is False


@pytest.mark.unit
def test_sales_match_position_teilgeliefert() -> None:
    from app.services.sales_match_service import match_position
    result = match_position(Decimal("100"), Decimal("70"), toleranz_pct=Decimal("2"))
    assert result["status"] == "teilgeliefert"
    assert result["offen"] == pytest.approx(30.0)


@pytest.mark.unit
def test_sales_match_position_abweichung_pct_computed() -> None:
    from app.services.sales_match_service import match_position
    result = match_position(Decimal("100"), Decimal("90"), toleranz_pct=Decimal("2"))
    assert result["abweichung_pct"] == pytest.approx(-10.0)


@pytest.mark.unit
def test_sales_match_summary_fully_delivered() -> None:
    from app.services.sales_match_service import match_position, match_summary
    pos = match_position(Decimal("100"), Decimal("100"), toleranz_pct=Decimal("0"))
    summary = match_summary([pos])
    assert summary["vollstaendig_geliefert"] is True
    assert summary["hat_abweichung"] is False


@pytest.mark.unit
def test_sales_match_summary_with_deviation() -> None:
    from app.services.sales_match_service import match_position, match_summary
    pos = match_position(Decimal("100"), Decimal("80"), toleranz_pct=Decimal("0"))
    summary = match_summary([pos])
    assert summary["hat_abweichung"] is True
    assert summary["offen_positionen"] >= 1


@pytest.mark.unit
def test_sales_match_summary_positionen_count() -> None:
    from app.services.sales_match_service import match_position, match_summary
    pos1 = match_position(Decimal("100"), Decimal("100"), toleranz_pct=Decimal("0"))
    pos2 = match_position(Decimal("50"), Decimal("50"), toleranz_pct=Decimal("0"))
    summary = match_summary([pos1, pos2])
    assert summary["positionen"] == 2
