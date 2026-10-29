"""Provider usage, single execution receipts and fail-closed quota boundaries."""
from types import SimpleNamespace
from unittest.mock import Mock
from uuid import uuid4
import json

import pytest
from fastapi import HTTPException

from app.services.llm_gateway import LLMConfig, LLMGateway, LLMUnavailable, MeteredCompletion
from app.services import studio_semantic_model as model
from app.services.studio_semantic import DialogueTurn, StudioDialogueIn


@pytest.mark.parametrize("provider,payload,tokens", [
    ("anthropic", {"content": [{"text": "ok"}], "usage": {"input_tokens": 10, "output_tokens": 3, "cache_read_input_tokens": 4}}, (14, 3)),
    ("openai_compatible", {"choices": [{"message": {"content": "ok"}}], "usage": {"prompt_tokens": 11, "completion_tokens": 5}}, (11, 5)),
    ("ollama", {"message": {"content": "ok"}, "prompt_eval_count": 12, "eval_count": 6}, (12, 6)),
])
def test_actual_usage_and_existing_text_contract(monkeypatch, provider, payload, tokens):
    from app.services import llm_gateway
    response = Mock()
    response.json.return_value = payload
    post = Mock(return_value=response)
    monkeypatch.setattr(llm_gateway.httpx, "post", post)
    gateway = LLMGateway(config=LLMConfig(provider=provider, api_key="synthetic-test-key"))
    answer = gateway.complete_metered("synthetische Anforderung")
    assert (answer.input_tokens, answer.output_tokens) == tokens
    assert gateway.complete("synthetische Anforderung") == "ok"
    payload.pop("usage", None)
    payload.pop("eval_count", None)
    with pytest.raises(LLMUnavailable):
        gateway.complete_metered("synthetische Anforderung")


@pytest.fixture
def metered(monkeypatch):
    class Receipts:
        def __init__(self): self.data = {}
        def get(self, key): return self.data.get(key)
        def set(self, key, value, nx=False):
            if nx and key in self.data: return False
            self.data[key] = value
            return True
    receipts = Receipts()
    monkeypatch.setattr(model, "current_identity", lambda: SimpleNamespace(issuer="issuer", tenant_id="own", subject="synthetic-editor"))
    monkeypatch.setattr(model.identity_session, "store", lambda: receipts)
    reserve = Mock(return_value={"status": "reserved"})
    settle = Mock()
    monkeypatch.setattr(model.identity_quota, "reserve", reserve)
    monkeypatch.setattr(model.identity_quota, "settle", settle)
    text = json.dumps({"contract": model.CONTRACT, "summary": "Manuelle Getreideprobe", "unsupported": [], "question": None})
    gateway = Mock()
    gateway.available.return_value = True
    gateway.complete_metered.return_value = MeteredCompletion(text, 200, 40)
    body = StudioDialogueIn(turns=[DialogueTurn(role="user", content="Manuelle Getreideprobe")],
                           use_language_model=True, budget_id="own-budget", idempotency_key=uuid4())
    return body, gateway, reserve, settle, receipts


def test_reserve_before_call_actual_settlement_and_retry_without_second_call(metered):
    body, gateway, reserve, settle, _ = metered
    calls = []
    reserve.side_effect = lambda *args: calls.append("reserve") or {"status": "reserved"}
    original = gateway.complete_metered.return_value
    gateway.complete_metered.side_effect = lambda *args, **kwargs: calls.append("model") or original
    first = model.interpret(body, gateway)
    assert model.interpret(body, gateway) == first
    assert calls == ["reserve", "model", "reserve"]
    assert gateway.complete_metered.call_count == 1
    assert settle.call_args.args[1:] == (240, "completed")


def test_foreign_budget_is_denied_before_provider_call(metered):
    body, gateway, reserve, _, _ = metered
    reserve.side_effect = HTTPException(403, "foreign budget")
    with pytest.raises(HTTPException) as error: model.interpret(body, gateway)
    assert error.value.status_code == 403
    gateway.complete_metered.assert_not_called()


def test_unknown_provider_outcome_keeps_reservation_and_cannot_retry_spend(metered):
    body, gateway, _, settle, _ = metered
    gateway.complete_metered.side_effect = LLMUnavailable("unknown")
    with pytest.raises(HTTPException) as first: model.interpret(body, gateway)
    assert first.value.status_code == 503
    with pytest.raises(HTTPException) as retry: model.interpret(body, gateway)
    assert retry.value.status_code == 409
    gateway.complete_metered.assert_called_once()
    settle.assert_not_called()


def test_invented_binding_is_rejected_but_known_consumption_is_charged(metered):
    body, gateway, _, settle, _ = metered
    gateway.complete_metered.return_value = MeteredCompletion('{"contract":"invented.v9","summary":"bad","unsupported":[],"endpoint":"/evil"}', 12, 5)
    with pytest.raises(HTTPException) as error: model.interpret(body, gateway)
    assert error.value.status_code == 502
    assert settle.call_args.args[1:] == (17, "failed")


def test_reused_key_cannot_change_requirements(metered):
    body, gateway, _, _, _ = metered
    model.interpret(body, gateway)
    body.turns = [DialogueTurn(role="user", content="Andere Anforderungen")]
    with pytest.raises(HTTPException) as error: model.interpret(body, gateway)
    assert error.value.status_code == 409
    gateway.complete_metered.assert_called_once()
