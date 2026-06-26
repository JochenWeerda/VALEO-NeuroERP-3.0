"""DATA-CLASSIFICATION-001 — Tests für KI-Datenklassen-Policy."""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from scripts.validate_data_classification import load, validate, summary

pytestmark = pytest.mark.unit

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "ai_data_classification.yaml"


@pytest.fixture()
def config() -> dict:
    return load(CONFIG_PATH)


@pytest.fixture()
def minimal_valid() -> dict:
    return {
        "version": "1.0",
        "updated": "2026-06-26",
        "owner": "Test",
        "levels": [
            {"id": "PUBLIC", "label": "Öffentlich", "description": "Öffentlich",
             "external_model_allowed": True, "never_in_context": False},
            {"id": "NEVER", "label": "Niemals", "description": "Niemals",
             "external_model_allowed": False, "never_in_context": True},
            {"id": "EU_ONLY", "label": "EU", "description": "EU",
             "external_model_allowed": True, "never_in_context": False},
            {"id": "LOCAL_ONLY", "label": "Lokal", "description": "Lokal",
             "external_model_allowed": False, "never_in_context": False},
            {"id": "SYNTHETIC_ALLOWED", "label": "Synth", "description": "Synth",
             "external_model_allowed": False, "never_in_context": False},
        ],
        "categories": [
            {"id": "cred", "label": "Credentials", "examples": ["Passwort"],
             "level": "NEVER", "rationale": "Sicherheit"},
            {"id": "audit", "label": "Audit", "examples": ["Log"],
             "level": "NEVER", "rationale": "Datenschutz"},
            {"id": "payment", "label": "Zahlung", "examples": ["IBAN"],
             "level": "NEVER", "rationale": "Finanzdaten"},
            {"id": "article", "label": "Artikel", "examples": ["Artikelnummer"],
             "level": "PUBLIC", "rationale": "Öffentlich"},
        ],
    }


# ── Produktive Konfiguration ───────────────────────────────────────────────────

class TestProductiveConfig:
    def test_config_file_exists(self):
        assert CONFIG_PATH.exists(), "config/ai_data_classification.yaml nicht gefunden"

    def test_no_validation_errors(self, config):
        errors = validate(config)
        assert errors == [], f"Validierungsfehler:\n" + "\n".join(errors)

    def test_has_version(self, config):
        assert "version" in config

    def test_has_all_five_levels(self, config):
        ids = {l["id"] for l in config.get("levels", [])}
        assert {"PUBLIC", "EU_ONLY", "LOCAL_ONLY", "SYNTHETIC_ALLOWED", "NEVER"} == ids

    def test_never_level_has_never_in_context_true(self, config):
        never = next(l for l in config["levels"] if l["id"] == "NEVER")
        assert never["never_in_context"] is True

    def test_public_level_allows_external(self, config):
        pub = next(l for l in config["levels"] if l["id"] == "PUBLIC")
        assert pub["external_model_allowed"] is True

    def test_local_only_not_external(self, config):
        local = next(l for l in config["levels"] if l["id"] == "LOCAL_ONLY")
        assert local["external_model_allowed"] is False

    def test_categories_non_empty(self, config):
        assert len(config.get("categories", [])) >= 10

    def test_credentials_classified_never(self, config):
        creds = next(
            (c for c in config["categories"] if c["id"] == "system_credentials"), None
        )
        assert creds is not None
        assert creds["level"] == "NEVER"

    def test_payment_data_classified_never(self, config):
        pay = next(
            (c for c in config["categories"] if c["id"] == "transaction_payment"), None
        )
        assert pay is not None
        assert pay["level"] == "NEVER"

    def test_audit_logs_classified_never(self, config):
        audit = next(
            (c for c in config["categories"] if c["id"] == "compliance_audit_log"), None
        )
        assert audit is not None
        assert audit["level"] == "NEVER"

    def test_employee_data_classified_never(self, config):
        emp = next(
            (c for c in config["categories"] if c["id"] == "master_employee"), None
        )
        assert emp is not None
        assert emp["level"] == "NEVER"

    def test_agrar_contracts_local_only(self, config):
        con = next(
            (c for c in config["categories"] if c["id"] == "agrar_contract"), None
        )
        assert con is not None
        assert con["level"] == "LOCAL_ONLY"

    def test_article_master_public(self, config):
        art = next(
            (c for c in config["categories"] if c["id"] == "master_article"), None
        )
        assert art is not None
        assert art["level"] == "PUBLIC"

    def test_all_categories_have_rationale(self, config):
        for cat in config.get("categories", []):
            assert cat.get("rationale", "").strip(), \
                f"Kategorie '{cat.get('id')}' hat keine Begründung"

    def test_all_categories_have_examples(self, config):
        for cat in config.get("categories", []):
            assert len(cat.get("examples", [])) >= 1, \
                f"Kategorie '{cat.get('id')}' hat keine Beispiele"


# ── Validierungs-Engine ────────────────────────────────────────────────────────

class TestValidator:
    def test_valid_config_no_errors(self, minimal_valid):
        assert validate(minimal_valid) == []

    def test_missing_version_detected(self, minimal_valid):
        del minimal_valid["version"]
        errors = validate(minimal_valid)
        assert any("version" in e for e in errors)

    def test_invalid_level_id_detected(self, minimal_valid):
        minimal_valid["levels"].append({
            "id": "INVALID_LEVEL",
            "label": "X", "description": "X",
            "external_model_allowed": False, "never_in_context": False
        })
        errors = validate(minimal_valid)
        assert any("INVALID_LEVEL" in e for e in errors)

    def test_category_referencing_undefined_level(self, minimal_valid):
        minimal_valid["categories"].append({
            "id": "bad_cat", "label": "Bad", "examples": ["X"],
            "level": "NONEXISTENT", "rationale": "Test"
        })
        errors = validate(minimal_valid)
        assert any("NONEXISTENT" in e for e in errors)

    def test_empty_examples_detected(self, minimal_valid):
        minimal_valid["categories"].append({
            "id": "empty_ex", "label": "Leer", "examples": [],
            "level": "PUBLIC", "rationale": "Test"
        })
        errors = validate(minimal_valid)
        assert any("empty_ex" in e for e in errors)

    def test_duplicate_category_id_detected(self, minimal_valid):
        minimal_valid["categories"].append({
            "id": "cred", "label": "Duplikat", "examples": ["X"],
            "level": "NEVER", "rationale": "Duplikat"
        })
        errors = validate(minimal_valid)
        assert any("Duplikat" in e and "cred" in e for e in errors)

    def test_empty_rationale_detected(self, minimal_valid):
        minimal_valid["categories"].append({
            "id": "no_rationale", "label": "Leer", "examples": ["X"],
            "level": "PUBLIC", "rationale": ""
        })
        errors = validate(minimal_valid)
        assert any("no_rationale" in e for e in errors)

    def test_too_few_never_categories(self, minimal_valid):
        minimal_valid["categories"] = [
            c for c in minimal_valid["categories"] if c["level"] != "NEVER"
        ]
        minimal_valid["categories"].append({
            "id": "one_never", "label": "Eines", "examples": ["X"],
            "level": "NEVER", "rationale": "Nur eines"
        })
        errors = validate(minimal_valid)
        assert any("NEVER" in e for e in errors)


# ── Summary ────────────────────────────────────────────────────────────────────

class TestSummary:
    def test_summary_total_count(self, config):
        s = summary(config)
        assert s["total_categories"] == len(config["categories"])

    def test_summary_by_level_keys(self, config):
        s = summary(config)
        assert "by_level" in s
        assert isinstance(s["by_level"], dict)

    def test_never_count_at_least_4(self, config):
        s = summary(config)
        assert s["by_level"].get("NEVER", 0) >= 4
