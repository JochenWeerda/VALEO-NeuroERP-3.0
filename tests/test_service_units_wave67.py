"""Wave 67 — Unit-Tests fuer AiDataClassificationService und neuro_tool_execution (pure logic)."""

from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# AiDataClassificationService  (pure, keine DB)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_list_categories_returns_nonempty() -> None:
    from app.services.ai_data_classification_service import AiDataClassificationService
    svc = AiDataClassificationService()
    cats = svc.list_categories()
    assert len(cats) > 0
    assert all("category_id" in c and "data_class" in c for c in cats)


@pytest.mark.unit
def test_get_category_known_id() -> None:
    from app.services.ai_data_classification_service import AiDataClassificationService
    svc = AiDataClassificationService()
    cat_id = svc.list_categories()[0]["category_id"]
    cat = svc.get_category(cat_id)
    assert cat["category_id"] == cat_id


@pytest.mark.unit
def test_get_category_unknown_raises() -> None:
    from app.services.ai_data_classification_service import AiDataClassificationService
    svc = AiDataClassificationService()
    with pytest.raises(KeyError):
        svc.get_category("does-not-exist")


@pytest.mark.unit
def test_check_model_allowed_public_category() -> None:
    from app.services.ai_data_classification_service import AiDataClassificationService
    svc = AiDataClassificationService()
    # cat-pub-001 is C0_oeffentlich → allows any model
    result = svc.check_model_allowed("cat-pub-001", "gpt-4")
    assert result["allowed"] is True
    assert "data_class" in result


@pytest.mark.unit
def test_check_model_allowed_restricted_category() -> None:
    from app.services.ai_data_classification_service import AiDataClassificationService
    svc = AiDataClassificationService()
    # cat-passwort-001 is C5 → no models allowed
    result = svc.check_model_allowed("cat-passwort-001", "gpt-4")
    assert result["allowed"] is False


@pytest.mark.unit
def test_check_model_allowed_local_only_category() -> None:
    from app.services.ai_data_classification_service import AiDataClassificationService
    svc = AiDataClassificationService()
    # cat-personal-001 is C3_nur_lokal → only local models
    result_local = svc.check_model_allowed("cat-personal-001", "ollama@localhost")
    assert result_local["allowed"] is True
    result_cloud = svc.check_model_allowed("cat-personal-001", "gpt-4")
    assert result_cloud["allowed"] is False


@pytest.mark.unit
def test_summary_structure() -> None:
    from app.services.ai_data_classification_service import AiDataClassificationService
    svc = AiDataClassificationService()
    s = svc.summary()
    assert "total_categories" in s
    assert "by_class" in s
    assert s["total_categories"] > 0


@pytest.mark.unit
def test_summary_counts_match_categories() -> None:
    from app.services.ai_data_classification_service import AiDataClassificationService
    svc = AiDataClassificationService()
    cats = svc.list_categories()
    s = svc.summary()
    assert s["total_categories"] == len(cats)


@pytest.mark.unit
def test_categories_have_required_fields() -> None:
    from app.services.ai_data_classification_service import AiDataClassificationService
    svc = AiDataClassificationService()
    for cat in svc.list_categories():
        assert "category_id" in cat
        assert "name" in cat
        assert "data_class" in cat
        assert "erlaubte_ki_modelle" in cat


# ---------------------------------------------------------------------------
# neuro_tool_execution — validate_outbound_http_target  (pure security helper)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_validate_https_url_ok() -> None:
    from app.services.neuro_tool_execution import validate_outbound_http_target
    url = validate_outbound_http_target("https://api.example.com/v1/data")
    assert url == "https://api.example.com/v1/data"


@pytest.mark.unit
def test_validate_http_url_ok() -> None:
    from app.services.neuro_tool_execution import validate_outbound_http_target
    url = validate_outbound_http_target("http://partner.example.com/webhook")
    assert url.startswith("http://")


@pytest.mark.unit
def test_validate_ftp_scheme_rejected() -> None:
    from app.services.neuro_tool_execution import validate_outbound_http_target
    with pytest.raises(Exception):
        validate_outbound_http_target("ftp://evil.com/file")


@pytest.mark.unit
def test_validate_loopback_rejected() -> None:
    from app.services.neuro_tool_execution import validate_outbound_http_target
    with pytest.raises(Exception):
        validate_outbound_http_target("https://127.0.0.1/admin")


@pytest.mark.unit
def test_validate_localhost_rejected() -> None:
    from app.services.neuro_tool_execution import validate_outbound_http_target
    with pytest.raises(Exception):
        validate_outbound_http_target("http://localhost:8080/api")


@pytest.mark.unit
def test_validate_loopback_allowed_when_flag_set() -> None:
    from app.services.neuro_tool_execution import validate_outbound_http_target
    url = validate_outbound_http_target("http://localhost:8080/test", allow_loopback_hosts=True)
    assert "localhost" in url
