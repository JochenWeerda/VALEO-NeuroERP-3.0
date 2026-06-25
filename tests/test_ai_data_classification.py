"""Tests fuer P2.3 — AiDataClassificationService."""

import pytest
from app.services.ai_data_classification_service import (
    AiDataClassificationService,
    DataClass,
)


@pytest.fixture()
def svc() -> AiDataClassificationService:
    return AiDataClassificationService()


def test_list_all_categories(svc: AiDataClassificationService) -> None:
    cats = svc.list_categories()
    assert len(cats) >= 8
    assert all("category_id" in c and "data_class" in c for c in cats)


def test_filter_by_c5(svc: AiDataClassificationService) -> None:
    cats = svc.list_categories(data_class=DataClass.C5_NIE_MODELLKONTEXT)
    assert len(cats) >= 3
    assert all(c["data_class"] == DataClass.C5_NIE_MODELLKONTEXT.value for c in cats)


def test_filter_by_c3(svc: AiDataClassificationService) -> None:
    cats = svc.list_categories(data_class=DataClass.C3_NUR_LOKAL)
    assert len(cats) >= 2
    assert all(c["data_class"] == DataClass.C3_NUR_LOKAL.value for c in cats)


def test_get_tse_category(svc: AiDataClassificationService) -> None:
    cat = svc.get_category("cat-tse-001")
    assert cat["data_class"] == DataClass.C5_NIE_MODELLKONTEXT.value
    assert len(cat["verbotene_aktionen"]) >= 2


def test_get_passwort_category(svc: AiDataClassificationService) -> None:
    cat = svc.get_category("cat-passwort-001")
    assert cat["data_class"] == DataClass.C5_NIE_MODELLKONTEXT.value
    assert cat["erlaubte_ki_modelle"] == []


def test_get_unknown_category_raises(svc: AiDataClassificationService) -> None:
    with pytest.raises(KeyError):
        svc.get_category("does-not-exist-999")


def test_check_model_c5_always_denied(svc: AiDataClassificationService) -> None:
    result = svc.check_model_allowed("cat-tse-001", "claude-sonnet-4-6")
    assert result["allowed"] is False


def test_check_model_c1_claude_allowed(svc: AiDataClassificationService) -> None:
    result = svc.check_model_allowed("cat-crm-sum-001", "claude-sonnet-4-6")
    assert result["allowed"] is True


def test_check_model_c3_cloud_denied(svc: AiDataClassificationService) -> None:
    result = svc.check_model_allowed("cat-personal-001", "claude-sonnet-4-6")
    assert result["allowed"] is False


def test_check_model_c3_local_allowed(svc: AiDataClassificationService) -> None:
    result = svc.check_model_allowed("cat-personal-001", "ollama@localhost")
    assert result["allowed"] is True


def test_check_model_c0_any_allowed(svc: AiDataClassificationService) -> None:
    result = svc.check_model_allowed("cat-pub-001", "gpt-4o")
    assert result["allowed"] is True


def test_summary_structure(svc: AiDataClassificationService) -> None:
    s = svc.summary()
    assert s["total_categories"] >= 8
    assert s["nie_modellkontext"] >= 3
    assert s["nur_lokal"] >= 2
    assert s["extern_erlaubt"] >= 2
    assert "by_class" in s


def test_data_class_label_in_response(svc: AiDataClassificationService) -> None:
    cat = svc.get_category("cat-elster-001")
    assert "data_class_label" in cat
    assert cat["data_class_label"] != ""


def test_elster_is_c5(svc: AiDataClassificationService) -> None:
    cat = svc.get_category("cat-elster-001")
    assert cat["data_class"] == DataClass.C5_NIE_MODELLKONTEXT.value


def test_bankkonto_is_c5(svc: AiDataClassificationService) -> None:
    cat = svc.get_category("cat-bankkonto-001")
    assert cat["data_class"] == DataClass.C5_NIE_MODELLKONTEXT.value


def test_synthetic_testdata_is_c4(svc: AiDataClassificationService) -> None:
    cat = svc.get_category("cat-cov-synth-001")
    assert cat["data_class"] == DataClass.C4_ANONYMISIERT_OK.value
    assert cat["anonymisierung_ausreichend"] is True
