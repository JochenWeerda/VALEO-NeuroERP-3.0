"""Tests fuer Neuro-Core Pipeline (NC-A5)."""
import pytest

from app.agents.neuro_pipeline import run_pipeline


class TestPipelineClassification:
    def test_known_intent_returns_plan(self):
        result = run_pipeline("Bestellung anlegen fuer Mais")
        assert result["status"] in ("executed", "awaiting_approval")
        assert result["intent"]["intent"] == "bestellung_anlegen"
        assert result["plan"] is not None
        assert result["plan"]["step_count"] >= 1

    def test_unknown_intent_low_confidence(self):
        result = run_pipeline("xyz abc 123")
        assert result["status"] == "low_confidence" or result["intent"]["intent"] == "unknown"

    def test_unknown_intent_with_llm_fallback_returns_plan(self):
        result = run_pipeline(
            "Bitte analysiere rasch die faelligen Rechnungen auf Lieferantenrabattpotenzial",
            context={
                "intent_llm_resolver": lambda text, context: {
                    "intent": "skonto_pruefen",
                    "category": "analysis",
                    "risk_class": "low",
                    "confidence_score": 0.72,
                    "matched_capability": "finance_skonto_assistant",
                    "explanation": "LLM-Fallback hat einen bekannten Intent erkannt",
                }
            },
            dry_run=True,
        )
        assert result["status"] == "dry_run"
        assert result["intent"]["intent"] == "skonto_pruefen"
        assert result["plan"]["step_count"] >= 1

    def test_empty_input(self):
        result = run_pipeline("")
        assert result["status"] == "low_confidence"
        assert result["plan"] is None


class TestPipelineDryRun:
    def test_dry_run_skips_execution(self):
        result = run_pipeline("Lagerbestand abfragen", dry_run=True)
        assert result["status"] == "dry_run"
        assert result["plan"] is not None
        assert "executed_steps" not in result

    def test_dry_run_still_classifies(self):
        result = run_pipeline("Skonto bei Rechnungen nutzen", dry_run=True)
        assert result["intent"]["intent"] == "skonto_pruefen"

    def test_navigation_dry_run_uses_dynamic_plan(self):
        result = run_pipeline("Zeig mir die offenen Auftraege", dry_run=True)
        assert result["status"] == "dry_run"
        assert result["plan"]["step_count"] == 2
        assert result["plan"]["steps"][0]["action"] == "resolve_navigation_target"
        assert result["plan"]["steps"][1]["action"] == "open_navigation_target"


class TestPipelineApproval:
    def test_high_risk_requires_approval(self):
        result = run_pipeline("Rechnung erstellen fuer Lieferschein")
        assert result["status"] == "awaiting_approval"
        assert result["plan"]["requires_human_approval"] is True

    def test_critical_risk_requires_approval(self):
        result = run_pipeline("Ausnahme loeschen und eskalieren")
        assert result["status"] == "awaiting_approval"


class TestPipelineExecution:
    def test_low_risk_executes(self):
        result = run_pipeline("Lagerbestand abfragen")
        assert result["status"] == "executed"
        assert "executed_steps" in result
        assert "tool_trace" in result
        assert len(result["executed_steps"]) >= 1

    def test_skonto_executes(self):
        result = run_pipeline("Skonto-Auswertung starten")
        # Skonto braucht Finance-MCP-Tools; ohne laufende Services wird 'failed' erwartet
        assert result["status"] in ("executed", "failed")
        assert result["intent"]["intent"] == "skonto_pruefen"
        assert result["plan"]["step_count"] >= 1

    def test_executed_steps_structure(self):
        result = run_pipeline("Lagerbestand pruefen")
        if result["status"] == "executed":
            for step in result["executed_steps"]:
                assert "step_id" in step
                assert "action" in step
                assert "status" in step


class TestPipelineContext:
    def test_context_passed_through(self):
        result = run_pipeline(
            "Bestellung anlegen",
            context={"channel": "whatsapp", "extra_params": {"warehouse_id": "WH-01"}},
        )
        assert result["plan"] is not None

    def test_tenant_id_defaults(self):
        result = run_pipeline("Lagerbestand abfragen")
        assert result["status"] == "executed"


class TestPipelineResultStructure:
    def test_all_results_have_intent(self):
        for text in ["Bestellung anlegen", "Lagerbestand abfragen", "", "unbekannt xyz"]:
            result = run_pipeline(text)
            assert "intent" in result
            assert "status" in result

    def test_executed_result_includes_broker_trace(self):
        result = run_pipeline("Lagerbestand abfragen")
        assert result["tool_trace"][0]["binding_target"] == "valeo_inventory_bestand_get"
        assert result["tool_trace"][0]["result"]["mode"] == "openapi_internal"
        assert "state_summary" in result

    def test_medium_risk_step_level_approval_is_visible(self):
        result = run_pipeline("Bestellung anlegen")
        assert result["status"] == "awaiting_approval"
        assert result["tool_trace"][-1]["status"] == "pending_approval"
