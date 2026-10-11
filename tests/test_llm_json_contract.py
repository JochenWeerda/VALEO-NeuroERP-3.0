"""Real JSON consumers; model/provider, DB and network boundaries replaced."""
import json

import pytest

from app.services import llm_gateway as gateway
from app.services.whatsapp_intake_service import WhatsAppIntakeService
from app.services.kaeufer_klassifikator import LLMKlassifikator, RuleBasedKlassifikator
from app.services.kaeufergruppe import Verhaltenssignale
from app.api.v1.endpoints import crm_kim


@pytest.fixture(autouse=True)
def forbid_external_access(monkeypatch):
    from sqlalchemy.engine import Engine
    import httpx
    def forbidden(*args, **kwargs):
        raise AssertionError("This JSON contract must not call a database or provider")
    monkeypatch.setattr(Engine, "connect", forbidden)
    monkeypatch.setattr(httpx.Client, "request", forbidden)


@pytest.mark.parametrize("wrapper", ["{}", "```json\n{}\n```", "```JSON\n{}\n```", "```\n{}\n```", "```json  \n{}\n  ```"])
def test_object_and_literal_fences_preserved(wrapper):
    raw = json.dumps({"kunde": "Hof Probe", "notiz": "literal ``` inside"})
    assert gateway.parse_json_object(wrapper.format(raw)) == json.loads(raw)


@pytest.mark.parametrize("raw", [
    "[]", "null", '"private response"', "42", "true", "{broken}",
    '```json\n{"kunde":"x"}', '{"kunde":"x"}\n```',
    '```python\n{"kunde":"x"}\n```', 'text before {"kunde":"x"}',
    '{"confidence":NaN}', '{"confidence":Infinity}', '{"confidence":-Infinity}',
    '{"confidence":1e999}', '{"kunde":"first","kunde":"second"}',
    '{"nested":{"id":1,"id":2}}', '{"positionen":[{"menge":NaN}]}',
])
def test_ambiguous_or_invalid_objects_rejected(raw):
    with pytest.raises(ValueError):
        gateway.parse_json_object(raw)


def reply(monkeypatch, raw):
    monkeypatch.setattr(gateway.LLMGateway, "complete_or_none", lambda *args, **kwargs: raw)


@pytest.mark.parametrize("raw", ["[]", "null", "42", '{"confidence":NaN}'])
def test_whatsapp_invalid_json_uses_real_heuristic(monkeypatch, raw):
    reply(monkeypatch, raw)
    service = WhatsAppIntakeService(None, "probe-a")
    text = "Hof Probe 20 to Weizen"
    parsed, engine, confidence = service.extract(text)
    assert parsed == service._extract_heuristik(text)
    assert engine == "heuristik" and confidence == 0.45


def test_whatsapp_object_fences_are_accepted(monkeypatch):
    expected = {"kunde": "Hof Probe", "positionen": [{"artikel": "Weizen", "menge": 20}]}
    reply(monkeypatch, "```JSON\n" + json.dumps(expected) + "\n```")
    parsed, engine, confidence = WhatsAppIntakeService(None, "probe-a").extract("20 to Weizen")
    assert parsed == expected and engine == "claude" and confidence == 0.9


@pytest.mark.parametrize("raw", ["[]", '{"gruppe":"unbekannt","confidence":NaN}', '{"gruppe":"unbekannt","confidence":"private response"}'])
def test_classifier_fallback_and_private_parse_errors(monkeypatch, raw, caplog):
    reply(monkeypatch, raw)
    signals = Verhaltenssignale()
    assert LLMKlassifikator().klassifiziere(signals) == RuleBasedKlassifikator().klassifiziere(signals)
    assert "private response" not in caplog.text


def crm_boundary(monkeypatch):
    cust = crm_kim._customer_from_row({"kunden_nr": "PROBE", "name1": "Hof Probe", "ort": "Emden"})
    monkeypatch.setattr(crm_kim, "get_customer", lambda *args: cust)
    monkeypatch.setattr(crm_kim, "list_financials", lambda *args: [])
    monkeypatch.setattr(crm_kim, "list_documents", lambda *args: [])
    monkeypatch.setattr(crm_kim.CrmKontaktService, "list_by_kunde", lambda *args: [])
    return cust


@pytest.mark.parametrize("consumer", ["summary", "email"])
@pytest.mark.parametrize("raw", ["[]", '{"confidence":NaN}'])
def test_crm_consumers_reject_invalid_json(monkeypatch, consumer, raw):
    crm_boundary(monkeypatch)
    reply(monkeypatch, raw)
    if consumer == "summary":
        result = crm_kim.neuro_summary(crm_kim.NeuroSummaryIn(customerId="PROBE"), None, "probe-a")
    else:
        result = crm_kim.draft_email(crm_kim.DraftEmailIn(customerId="PROBE"), None, "probe-a")
    assert result.engine == "fallback"


@pytest.mark.parametrize("consumer", ["summary", "email"])
def test_crm_consumers_accept_valid_fences(monkeypatch, consumer):
    crm_boundary(monkeypatch)
    data = {"healthScore": 73, "summary": "Beziehung pruefen", "subject": "Beratung", "body": "Guten Tag"}
    reply(monkeypatch, "```JSON\n" + json.dumps(data) + "\n```")
    if consumer == "summary":
        result = crm_kim.neuro_summary(crm_kim.NeuroSummaryIn(customerId="PROBE"), None, "probe-a")
        assert result.healthScore == 73 and result.summary == data["summary"]
    else:
        result = crm_kim.draft_email(crm_kim.DraftEmailIn(customerId="PROBE"), None, "probe-a")
        assert result.subject == data["subject"] and result.body == data["body"]
    assert result.engine == "llm"
