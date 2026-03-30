"""Tests fuer Neuro Intent Engine (NC-A1/A2)."""
import pytest

from app.agents.neuro_intent_engine import (
    IntentCategory,
    IntentResult,
    RiskClass,
    classify,
    get_supported_intents,
    _extract_parameters,
)


class TestClassifyBasicIntents:
    def test_bestellung_anlegen(self):
        result = classify("Bestellung anlegen fuer Sojaschrot")
        assert result.intent == "bestellung_anlegen"
        assert result.category == IntentCategory.COMMAND
        assert result.matched_capability == "bestellvorschlag_assistant"
        assert result.confidence_score >= 0.5

    def test_nachbestellung(self):
        result = classify("Nachbestellung aufgeben")
        assert result.intent == "bestellung_anlegen"

    def test_skonto_pruefen(self):
        result = classify("Skonto bei offenen Rechnungen nutzen")
        assert result.intent == "skonto_pruefen"
        assert result.category == IntentCategory.ANALYSIS
        assert result.matched_capability == "finance_skonto_assistant"

    def test_compliance_pruefen(self):
        result = classify("Compliance-Pruefung starten")
        assert result.intent == "compliance_pruefen"
        assert result.matched_capability == "compliance_copilot"

    def test_datenqualitaet_pruefen(self):
        result = classify("Duplikate in Stammdaten suchen")
        assert result.intent == "datenqualitaet_pruefen"
        assert result.matched_capability == "data_quality_assistant"

    def test_ausnahme_behandeln(self):
        result = classify("Stoerung in der Lieferkette eskalieren")
        assert result.intent == "ausnahme_behandeln"
        assert result.risk_class in (RiskClass.HIGH, RiskClass.CRITICAL)

    def test_auftrag_anlegen(self):
        result = classify("Verkaufsauftrag anlegen")
        assert result.intent == "auftrag_anlegen"
        assert result.category == IntentCategory.COMMAND

    def test_rechnung_erstellen(self):
        result = classify("Rechnung erstellen fuer Lieferschein 4711")
        assert result.intent == "rechnung_erstellen"
        assert result.risk_class in (RiskClass.HIGH, RiskClass.CRITICAL)

    def test_lagerbestand_abfragen(self):
        result = classify("Wie viel Rapsschrot ist noch im Lager?")
        assert result.intent == "lagerbestand_abfragen"
        assert result.category == IntentCategory.QUERY

    def test_navigation(self):
        result = classify("Zeig mir die offenen Auftraege")
        assert result.intent == "navigation"
        assert result.category == IntentCategory.NAVIGATION

    def test_freigabe_erteilen(self):
        result = classify("Freigabe fuer Bestellung 1234")
        assert result.intent == "freigabe_erteilen"
        assert result.category == IntentCategory.APPROVAL

    def test_system_optimieren(self):
        result = classify("Performance der Datenbank optimieren")
        assert result.intent == "system_optimieren"
        assert result.matched_capability == "system_optimizer"


class TestClassifyEdgeCases:
    def test_empty_input(self):
        result = classify("")
        assert result.intent == "unknown"
        assert result.confidence_score == 0.0

    def test_whitespace_only(self):
        result = classify("   ")
        assert result.intent == "unknown"
        assert result.confidence_score == 0.0

    def test_none_input(self):
        result = classify(None)
        assert result.intent == "unknown"

    def test_unknown_input(self):
        result = classify("Das Wetter ist heute schoen")
        assert result.intent == "unknown"
        assert result.confidence_score < 0.5

    def test_case_insensitive(self):
        result = classify("BESTELLUNG ANLEGEN")
        assert result.intent == "bestellung_anlegen"


class TestRiskEscalation:
    def test_loeschen_escalates_to_critical(self):
        result = classify("Bestellung loeschen und neu anlegen")
        assert result.risk_class == RiskClass.CRITICAL

    def test_stornieren_escalates(self):
        result = classify("Rechnung erstellen und stornieren")
        assert result.risk_class in (RiskClass.HIGH, RiskClass.CRITICAL)


class TestParameterExtraction:
    def test_amount_extraction(self):
        params = _extract_parameters("Bestellung ueber 1500 EUR anlegen", "bestellung_anlegen")
        assert params["amount"] == 1500.0
        assert params["currency"] == "EUR"

    def test_quantity_extraction(self):
        params = _extract_parameters("50 Tonnen Sojaschrot bestellen", "bestellung_anlegen")
        assert params["quantity"] == 50.0
        assert params["unit"] == "Tonnen"

    def test_article_extraction(self):
        params = _extract_parameters("Artikel A-1234 nachbestellen", "bestellung_anlegen")
        assert params["article_ref"] == "A-1234"

    def test_no_params(self):
        params = _extract_parameters("Skonto pruefen", "skonto_pruefen")
        assert params == {}


class TestToDict:
    def test_intent_result_serialization(self):
        result = classify("Bestellung anlegen")
        d = result.to_dict()
        assert "intent" in d
        assert "category" in d
        assert "confidence_score" in d
        assert "risk_class" in d
        assert isinstance(d["confidence_score"], float)


class TestGetSupportedIntents:
    def test_returns_all_intents(self):
        intents = get_supported_intents()
        assert len(intents) == 11
        names = {i["intent"] for i in intents}
        assert "bestellung_anlegen" in names
        assert "skonto_pruefen" in names
        assert "navigation" in names

    def test_intent_structure(self):
        intents = get_supported_intents()
        for intent in intents:
            assert "intent" in intent
            assert "category" in intent
            assert "risk_class" in intent
