"""WA-NOTIFY-001 — Unit-Tests für WhatsApp Ausgehende Benachrichtigungen"""
import importlib
import sys
import pytest


def _reload():
    mod = "app.services.whatsapp_notify_service"
    if mod in sys.modules:
        del sys.modules[mod]
    return importlib.import_module(mod)


@pytest.fixture()
def svc():
    return _reload()


class TestTextTemplates:
    def test_lieferankuendigung_enthaelt_pflichtfelder(self, svc):
        text = svc._text_lieferankuendigung("Müller", "Winterweizen", 20, "t", 60)
        assert "60" in text
        assert "Winterweizen" in text
        assert "20" in text
        assert "t" in text
        assert "🚛" in text

    def test_lieferankuendigung_mit_fahrer(self, svc):
        text = svc._text_lieferankuendigung("Schmidt", "Raps", 5, "t", 45, fahrer="Hans Eder")
        assert "Hans Eder" in text

    def test_lieferankuendigung_ohne_kunden_name(self, svc):
        text = svc._text_lieferankuendigung(None, "Gerste", 10, "dt", 30)
        assert isinstance(text, str)
        assert len(text) > 20

    def test_dokument_lieferschein(self, svc):
        text = svc._text_dokument_ready("Hofmann", "Lieferschein", "LS-2026-001")
        assert "Lieferschein" in text
        assert "LS-2026-001" in text
        assert "📦" in text
        assert "portal" in text.lower() or "http" in text.lower()

    def test_dokument_rechnung(self, svc):
        text = svc._text_dokument_ready("Hofmann", "Rechnung", "RE-2026-042")
        assert "Rechnung" in text
        assert "🧾" in text
        assert "RE-2026-042" in text

    def test_dokument_custom_portal_url(self, svc):
        text = svc._text_dokument_ready(None, "Lieferschein", "LS-X", portal_url="https://mein.portal.de")
        assert "mein.portal.de" in text


class TestSendFunctions:
    def test_lieferankuendigung_in_outbox(self, svc):
        result = svc.send_lieferankuendigung(
            tenant_id="t1", phone="+4917600001", kunden_nr="K-001",
            kunden_name="Test GbR", artikel="Weizen", menge=20.0, einheit="t",
        )
        assert result["status"] in ("sent", "simulated")
        assert result["msg_id"].startswith("NOTIFY-")
        assert "Weizen" in result["text"]

    def test_dokument_ready_in_outbox(self, svc):
        result = svc.send_dokument_ready(
            tenant_id="t1", phone="+4917600001", kunden_nr="K-001",
            kunden_name="Test GbR", doc_typ="Rechnung", doc_nr="RE-2026-001",
        )
        assert result["status"] in ("sent", "simulated")
        assert "RE-2026-001" in result["text"]

    def test_outbox_wird_befuellt(self, svc):
        svc.send_lieferankuendigung("t1", "+4917600002", "K-002", "Test", "Raps", 5.0, "t")
        outbox = svc.get_outbox("t1")
        assert len(outbox) >= 1
        assert outbox[0]["notify_type"] == "lieferankuendigung"

    def test_outbox_tenant_isoliert(self, svc):
        svc.send_lieferankuendigung("tenant-A", "+4917600003", "K-003", "A", "Mais", 1.0, "t")
        svc.send_dokument_ready("tenant-B", "+4917600004", "K-004", "B", "Lieferschein", "LS-1")
        assert len(svc.get_outbox("tenant-A")) >= 1
        assert len(svc.get_outbox("tenant-B")) >= 1
        a_phones = {m["phone"] for m in svc.get_outbox("tenant-A")}
        b_phones = {m["phone"] for m in svc.get_outbox("tenant-B")}
        assert a_phones.isdisjoint(b_phones)

    def test_outbox_leer_initial(self, svc):
        assert svc.get_outbox("nonexistent-tenant") == []

    def test_mehrere_nachrichten_chronologisch(self, svc):
        svc.send_lieferankuendigung("t1", "+4900001", None, None, "Weizen", 10, "t")
        svc.send_dokument_ready("t1", "+4900001", None, None, "Lieferschein", "LS-A")
        outbox = svc.get_outbox("t1")
        assert len(outbox) >= 2
        assert outbox[0]["notify_type"] == "dokument_ready"

    def test_msg_id_eindeutig(self, svc):
        r1 = svc.send_lieferankuendigung("t1", "+4900001", None, None, "Weizen", 1, "t")
        r2 = svc.send_lieferankuendigung("t1", "+4900001", None, None, "Weizen", 1, "t")
        assert r1["msg_id"] != r2["msg_id"]
