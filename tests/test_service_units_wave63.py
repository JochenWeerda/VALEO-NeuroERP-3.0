"""Wave 63 — Unit-Tests fuer Service-Module ohne DB-Abhaengigkeit:
fast_track, compat_helpers (pure utility functions).
"""

from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# fast_track  (pure functions — keine DB, kein HTTP)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_is_fast_track_get_whitelist_path() -> None:
    from app.services.fast_track import is_fast_track
    assert is_fast_track("GET", "/api/v1/articles") is True


@pytest.mark.unit
def test_is_fast_track_get_pattern_match() -> None:
    from app.services.fast_track import is_fast_track
    assert is_fast_track("GET", "/api/v1/articles/ART-001") is True


@pytest.mark.unit
def test_is_fast_track_unknown_path_is_false() -> None:
    from app.services.fast_track import is_fast_track
    assert is_fast_track("GET", "/api/v1/some/unknown/endpoint") is False


@pytest.mark.unit
def test_is_fast_track_never_fast_track_path() -> None:
    from app.services.fast_track import is_fast_track
    assert is_fast_track("GET", "/api/v1/neuro/something") is False


@pytest.mark.unit
def test_is_fast_track_post_whitelist() -> None:
    from app.services.fast_track import is_fast_track
    assert is_fast_track("POST", "/api/v1/articles") is True


@pytest.mark.unit
def test_is_fast_track_post_unknown_is_false() -> None:
    from app.services.fast_track import is_fast_track
    assert is_fast_track("POST", "/api/v1/some/other") is False


@pytest.mark.unit
def test_classify_request_with_ai_context() -> None:
    from app.services.fast_track import classify_request
    result = classify_request("GET", "/api/v1/articles", has_ai_context=True)
    assert result["route"] == "neuro-core"
    assert "AI" in result["reason"]


@pytest.mark.unit
def test_classify_request_fast_track() -> None:
    from app.services.fast_track import classify_request
    result = classify_request("GET", "/api/v1/articles", has_ai_context=False)
    assert result["route"] == "fast-track"


@pytest.mark.unit
def test_classify_request_neuro_core_fallback() -> None:
    from app.services.fast_track import classify_request
    result = classify_request("GET", "/api/v1/some/exotic/endpoint")
    assert result["route"] == "neuro-core"


# ---------------------------------------------------------------------------
# compat_helpers  (pure utility functions)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_now_iso_returns_valid_timestamp() -> None:
    from app.services.compat_helpers import now_iso
    ts = now_iso()
    assert isinstance(ts, str)
    assert "T" in ts  # ISO format


@pytest.mark.unit
def test_cache_key_basic() -> None:
    from app.services.compat_helpers import cache_key
    key = cache_key("order", "ORD-001", "tenant1")
    assert key == "compat:order:ORD-001:tenant1"


@pytest.mark.unit
def test_cache_key_skips_none() -> None:
    from app.services.compat_helpers import cache_key
    key = cache_key("order", None, "tenant1")
    assert "None" not in key
    assert key == "compat:order:tenant1"


@pytest.mark.unit
def test_safe_float_valid() -> None:
    from app.services.compat_helpers import safe_float
    assert safe_float("3.14") == pytest.approx(3.14)


@pytest.mark.unit
def test_safe_float_none_returns_zero() -> None:
    from app.services.compat_helpers import safe_float
    assert safe_float(None) == 0.0


@pytest.mark.unit
def test_safe_float_invalid_string_returns_zero() -> None:
    from app.services.compat_helpers import safe_float
    assert safe_float("not-a-number") == 0.0


@pytest.mark.unit
def test_safe_float_integer() -> None:
    from app.services.compat_helpers import safe_float
    assert safe_float(42) == 42.0
