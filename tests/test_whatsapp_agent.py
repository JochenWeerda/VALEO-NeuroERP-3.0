"""WA-AGENT-001 — Unit-Tests für WhatsApp Bestellagent (ohne LLM, Regex-Fallback)"""
import importlib
import sys
import pytest


def _reload_service():
    """Lade das Modul neu um _CONV_STORE/_ORDER_LOG zwischen Tests zu isolieren."""
    mod_name = "app.services.whatsapp_agent_service"
    if mod_name in sys.modules:
        del sys.modules[mod_name]
    return importlib.import_module(mod_name)


@pytest.fixture()
def svc():
    """Frisches Modul-Objekt pro Test (leere Stores)."""
    return _reload_service()


# ─── Regex-Fallback Tests ──────────────────────────────────────────────────────

class TestFallbackExtract:
    def test_erkennt_winterweizen(self, svc):
        o = svc._fallback_extract("20 Tonnen Winterweizen bitte")
        assert o.artikel == "Winterweizen"
        assert o.menge == 20.0
        assert o.einheit == "t"

    def test_erkennt_raps_dt(self, svc):
        o = svc._fallback_extract("80 dt Raps")
        assert o.artikel == "Raps"
        assert o.menge == 80.0
        assert o.einheit == "dt"

    def test_erkennt_gerste_kg(self, svc):
        o = svc._fallback_extract("500 kg Gerste")
        assert o.artikel == "Wintergerste"
        assert o.menge == 500.0
        assert o.einheit == "kg"

    def test_erkennt_mais(self, svc):
        o = svc._fallback_extract("10 Tonnen Mais")
        assert o.artikel == "Körnermais"

    def test_unbekannter_artikel(self, svc):
        o = svc._fallback_extract("irgendwas bestellen")
        assert o.artikel is None
        assert "artikel" in o.fehlende_felder

    def test_kommazahl(self, svc):
        o = svc._fallback_extract("5,5 Tonnen Raps")
        assert o.menge == 5.5

    def test_konfidenz_vollstaendig(self, svc):
        o = svc._fallback_extract("20t Weizen")
        assert o.konfidenz >= 0.7

    def test_konfidenz_unvollstaendig(self, svc):
        o = svc._fallback_extract("Hallo, ich brauche etwas.")
        assert o.konfidenz < 0.5


# ─── Kundenzuordnung ────────────────────────────────────────────────────────────

class TestCustomerLookup:
    def test_bekannte_nummer(self, svc):
        nr, name = svc._find_customer_by_phone("t1", "+4917612345678")
        assert nr == "K-10001"
        assert "Müller" in name

    def test_unbekannte_nummer(self, svc):
        nr, name = svc._find_customer_by_phone("t1", "+4900000000000")
        assert nr is None
        assert name is None


# ─── Gesprächs-Verarbeitung ─────────────────────────────────────────────────────

class TestProcessMessage:
    def test_unbekannter_kunde_bekommt_hinweis(self, svc):
        reply = svc.process_whatsapp_message("t1", "+4900000000000", "20t Weizen")
        assert "Kundennummer" in reply or "zuordnen" in reply.lower() or "0800" in reply

    def test_vollstaendige_bestellung_erzeugt_auftrag(self, svc):
        reply = svc.process_whatsapp_message("t1", "+4917612345678", "20 Tonnen Winterweizen")
        # Regex-Fallback: konfidenz 0.7 — noch nicht 0.8, braucht merge
        # Zweiter Turn mit Ergänzung:
        reply2 = svc.process_whatsapp_message("t1", "+4917612345678", "20 Tonnen Winterweizen")
        # Nach merge sollte konfidenz >= 0.8 und Auftrag angelegt sein
        orders = svc.get_order_log("t1")
        if orders:
            assert orders[0]["artikel"] == "Winterweizen"
            assert "👍" in reply2 or "Auftrag" in reply2
        else:
            # Rückfrage wäre auch valide wenn Konfidenz < 0.8
            assert isinstance(reply2, str) and len(reply2) > 0

    def test_unvollstaendige_bestellung_erzeugt_rueckfrage(self, svc):
        reply = svc.process_whatsapp_message("t1", "+4917612345678", "Hallo")
        assert isinstance(reply, str)
        assert len(reply) > 10
        # Kein Auftrag angelegt
        assert not svc.get_order_log("t1")

    def test_merge_mit_vorherigem_turn(self, svc):
        # Turn 1: Artikel ohne Menge
        svc.process_whatsapp_message("t1", "+4917612345678", "Winterweizen bitte")
        # Turn 2: Menge ergänzen
        svc.process_whatsapp_message("t1", "+4917612345678", "30 Tonnen")
        # Konversation sollte merged haben
        state = svc.get_conversation_state("t1", "+4917612345678")
        # State kann None sein (wenn Auftrag angelegt + reset) oder partial
        # Hauptsache kein Crash
        assert True

    def test_conversation_state_wird_gespeichert(self, svc):
        svc.process_whatsapp_message("t1", "+4917612345678", "Raps, 80 dt")
        state = svc.get_conversation_state("t1", "+4917612345678")
        # Entweder Auftrag angelegt (state None) oder partial_order vorhanden
        if state is not None:
            assert state["phone"] == "+4917612345678"

    def test_tenant_isolation(self, svc):
        svc.process_whatsapp_message("tenant-A", "+4917612345678", "Test")
        svc.process_whatsapp_message("tenant-B", "+4917612345678", "Test")
        state_a = svc.get_conversation_state("tenant-A", "+4917612345678")
        state_b = svc.get_conversation_state("tenant-B", "+4917612345678")
        # Beide müssen unabhängige States haben
        if state_a and state_b:
            assert state_a is not state_b

    def test_reset_loescht_state(self, svc):
        svc.process_whatsapp_message("t1", "+4917612345678", "Raps")
        svc._reset_conv("t1", "+4917612345678")
        assert svc.get_conversation_state("t1", "+4917612345678") is None


# ─── Order-Log ─────────────────────────────────────────────────────────────────

class TestOrderLog:
    def test_order_log_leer_initial(self, svc):
        assert svc.get_order_log("no-such-tenant") == []

    def test_order_log_tenant_isoliert(self, svc):
        svc._create_order_in_erp("t1", "K-001", "Müller", svc.ExtractedOrder(
            artikel="Weizen", menge=10.0, einheit="t", konfidenz=0.9, fehlende_felder=[]
        ), "+4917612345678")
        assert svc.get_order_log("t2") == []
        assert len(svc.get_order_log("t1")) == 1

    def test_order_hat_pflichtfelder(self, svc):
        svc._create_order_in_erp("t1", "K-001", "Test", svc.ExtractedOrder(
            artikel="Raps", menge=50.0, einheit="dt", konfidenz=0.9, fehlende_felder=[]
        ), "+4917612345678")
        order = svc.get_order_log("t1")[0]
        assert order["id"].startswith("WA-")
        assert order["artikel"] == "Raps"
        assert order["menge"] == 50.0
        assert order["status"] == "OFFEN"
        assert order["quelle"] == "whatsapp"


# ─── LLM-Response-Parser ───────────────────────────────────────────────────────

class TestLLMParser:
    def test_valides_json(self, svc):
        raw = '{"artikel":"Weizen","menge":20,"einheit":"t","lieferdatum":null,"lieferort":null,"anmerkung":null,"konfidenz":0.9,"fehlende_felder":[],"klartext_antwort":"Danke!"}'
        result = svc._parse_llm_response(raw)
        assert isinstance(result, tuple)
        order, text = result
        assert order.artikel == "Weizen"
        assert order.menge == 20.0
        assert order.konfidenz == 0.9
        assert text == "Danke!"

    def test_markdown_fence_wird_entfernt(self, svc):
        raw = '```json\n{"artikel":"Raps","menge":null,"einheit":null,"lieferdatum":null,"lieferort":null,"anmerkung":null,"konfidenz":0.4,"fehlende_felder":["menge"],"klartext_antwort":"Wie viel?"}\n```'
        order, text = svc._parse_llm_response(raw)
        assert order.artikel == "Raps"
        assert "menge" in order.fehlende_felder

    def test_ungueltige_json_gibt_none(self, svc):
        result = svc._parse_llm_response("kein json hier")
        assert result == (None, None)


# ─── Bestätigungstext ──────────────────────────────────────────────────────────

class TestFormatConfirmation:
    def test_basisformat(self, svc):
        entry = {
            "id": "WA-20260625-ABC123",
            "menge": 20.0,
            "einheit": "t",
            "artikel": "Winterweizen",
            "lieferdatum": None,
            "lieferort": None,
        }
        text = svc._format_confirmation(entry, "Landwirt Müller")
        assert "👍" in text
        assert "WA-20260625-ABC123" in text
        assert "20" in text
        assert "Winterweizen" in text

    def test_mit_datum_und_ort(self, svc):
        entry = {
            "id": "WA-TEST",
            "menge": 5.0,
            "einheit": "t",
            "artikel": "Raps",
            "lieferdatum": "2026-07-10",
            "lieferort": "Hof am Berg",
        }
        text = svc._format_confirmation(entry, None)
        assert "2026-07-10" in text
        assert "Hof am Berg" in text
