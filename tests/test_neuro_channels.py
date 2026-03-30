"""Tests fuer Channel Adapter (NC-H1/H2/H4)."""
import pytest

from app.channels.whatsapp_adapter import (
    WhatsAppIncoming,
    WhatsAppMessageType,
    parse_webhook,
    build_text_reply,
    build_template_reply,
)
from app.channels.email_channel import (
    IncomingEmail,
    EmailPriority,
    detect_priority,
    extract_intent_text,
    parse_incoming,
    build_reply,
)
from app.channels.channel_ingress import (
    ChannelMessage,
    ChannelResponse,
    ChannelType,
    _format_response,
)


class TestWhatsAppParsing:
    def test_parse_text_message(self):
        payload = {
            "entry": [{
                "changes": [{
                    "value": {
                        "messages": [{
                            "id": "msg-001",
                            "from": "491701234567",
                            "timestamp": "2026-03-27T10:00:00Z",
                            "type": "text",
                            "text": {"body": "Bestellung anlegen"},
                        }],
                        "contacts": [{"profile": {"name": "Hans Mueller"}}],
                        "metadata": {"phone_number_id": "123456"},
                    }
                }]
            }]
        }
        messages = parse_webhook(payload)
        assert len(messages) == 1
        assert messages[0].text == "Bestellung anlegen"
        assert messages[0].from_number == "491701234567"
        assert messages[0].message_type == WhatsAppMessageType.TEXT

    def test_parse_empty_payload(self):
        messages = parse_webhook({})
        assert messages == []

    def test_parse_interactive_button(self):
        payload = {
            "entry": [{
                "changes": [{
                    "value": {
                        "messages": [{
                            "id": "msg-002",
                            "from": "491709876543",
                            "timestamp": "2026-03-27T11:00:00Z",
                            "type": "interactive",
                            "interactive": {
                                "type": "button_reply",
                                "button_reply": {"title": "Ja, bestellen"},
                            },
                        }],
                        "contacts": [{"profile": {"name": "Maria"}}],
                        "metadata": {},
                    }
                }]
            }]
        }
        messages = parse_webhook(payload)
        assert len(messages) == 1
        assert messages[0].text == "Ja, bestellen"
        assert messages[0].message_type == WhatsAppMessageType.INTERACTIVE


class TestWhatsAppReply:
    def test_build_text_reply(self):
        reply = build_text_reply("491701234567", "Ihre Bestellung wurde angelegt.")
        assert reply["to"] == "491701234567"
        assert reply["type"] == "text"
        assert reply["text"]["body"] == "Ihre Bestellung wurde angelegt."

    def test_build_text_reply_with_context(self):
        reply = build_text_reply("491701234567", "OK", reply_to="msg-001")
        assert reply["context"]["message_id"] == "msg-001"

    def test_build_template_reply(self):
        reply = build_template_reply("491701234567", "order_confirmation", params={"order_id": "4711"})
        assert reply["type"] == "template"
        assert reply["template"]["name"] == "order_confirmation"


class TestEmailParsing:
    def test_parse_basic_email(self):
        email = parse_incoming(
            raw_from="kunde@example.de",
            raw_to="system@valeo-erp.de",
            subject="Bestellung Sojaschrot",
            body_text="Bitte 50 Tonnen Sojaschrot bestellen.",
        )
        assert email.from_address == "kunde@example.de"
        assert email.subject == "Bestellung Sojaschrot"
        assert email.priority == EmailPriority.NORMAL

    def test_urgent_priority(self):
        email = parse_incoming(
            raw_from="chef@example.de",
            raw_to="system@valeo-erp.de",
            subject="DRINGEND: Lieferung fehlt",
            body_text="Sofort klaeren!",
        )
        assert email.priority == EmailPriority.URGENT

    def test_high_priority(self):
        email = parse_incoming(
            raw_from="chef@example.de",
            raw_to="system@valeo-erp.de",
            subject="Wichtig: Preisanpassung",
            body_text="Bitte schnellstmoeglich bearbeiten.",
        )
        assert email.priority == EmailPriority.HIGH

    def test_thread_tracking(self):
        email = parse_incoming(
            raw_from="a@b.de",
            raw_to="system@valeo-erp.de",
            subject="Re: Bestellung",
            body_text="Danke",
            in_reply_to="original-id@mail.example.de",
        )
        assert email.in_reply_to == "original-id@mail.example.de"
        assert email.thread_id is not None


class TestEmailIntentExtraction:
    def test_strips_quotes(self):
        email = IncomingEmail(
            message_id="1",
            from_address="a@b.de",
            to_address="sys@erp.de",
            subject="Bestellung",
            body_text="Bitte Mais bestellen.\n\n> Alte Nachricht\n> Bitte ignorieren",
        )
        text = extract_intent_text(email)
        assert "Alte Nachricht" not in text
        assert "Mais" in text

    def test_subject_prepended(self):
        email = IncomingEmail(
            message_id="1",
            from_address="a@b.de",
            to_address="sys@erp.de",
            subject="Lagerbestand",
            body_text="Bitte pruefen",
        )
        text = extract_intent_text(email)
        assert "Lagerbestand" in text


class TestEmailReply:
    def test_build_reply(self):
        original = IncomingEmail(
            message_id="msg-123",
            from_address="kunde@example.de",
            to_address="sys@erp.de",
            subject="Anfrage",
            body_text="Bitte Info",
        )
        reply = build_reply(original, "Ihre Anfrage wurde bearbeitet.")
        assert reply.to_address == "kunde@example.de"
        assert reply.subject.startswith("Re:")
        assert reply.in_reply_to == "msg-123"


class TestChannelIngress:
    def test_format_low_confidence(self):
        result = {"status": "low_confidence", "intent": {}}
        text = _format_response(result, ChannelType.API)
        assert "nicht eindeutig" in text.lower() or "praezisieren" in text.lower()

    def test_format_executed(self):
        result = {
            "status": "executed",
            "intent": {"intent": "lagerbestand_abfragen"},
            "plan": {"step_count": 1},
        }
        text = _format_response(result, ChannelType.API)
        assert "lagerbestand" in text.lower()

    def test_format_whatsapp_approval(self):
        result = {
            "status": "awaiting_approval",
            "intent": {"intent": "bestellung_anlegen"},
            "plan": {"step_count": 4},
        }
        text = _format_response(result, ChannelType.WHATSAPP)
        assert "Freigabe" in text

    def test_channel_message_to_dict(self):
        msg = ChannelMessage(
            channel=ChannelType.EMAIL,
            sender_id="kunde@example.de",
            text="Bestellung",
        )
        d = msg.to_dict()
        assert d["channel"] == "email"
        assert d["sender_id"] == "kunde@example.de"
