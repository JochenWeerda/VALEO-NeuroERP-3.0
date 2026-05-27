"""
Tests für Slice-012: Voice-Intent FiBu / Compliance / Agrar / Logistik.
"""
from __future__ import annotations

from app.services.action_registry import action_registry
from app.services.intent_resolver import intent_resolver


class TestActionRegistrySlice012:
    def test_finance_intents(self):
        ids = action_registry.all_ids()
        for expected in (
            "nav-fibu-hauptbuch",
            "nav-op-debitoren",
            "nav-op-kreditoren",
            "nav-zahlungslaeufe",
            "finance-booking",
            "nav-buchungsjournal",
            "nav-ustva",
            "nav-bilanz",
        ):
            assert expected in ids

    def test_compliance_intents(self):
        ids = action_registry.all_ids()
        for expected in (
            "nav-compliance-dashboard",
            "nav-verarbeitungsverzeichnis",
            "nav-datenpannen",
            "compliance-dsgvo-anfragen",
            "nav-sanktionspruefung",
        ):
            assert expected in ids

    def test_agrar_intents(self):
        ids = action_registry.all_ids()
        for expected in (
            "nav-agrar",
            "nav-ernte-annahme",
            "agrar-ernte-erfassen",
            "nav-agrar-vertraege",
            "nav-schlaege",
            "nav-silos",
            "nav-rohware-annahme",
            "nav-feldbuch",
        ):
            assert expected in ids

    def test_logistik_intents(self):
        ids = action_registry.all_ids()
        for expected in (
            "nav-logistik",
            "nav-tourenplanung",
            "nav-frachtbriefe",
            "nav-versandprofile",
            "logistik-tour-planen",
        ):
            assert expected in ids

    def test_total_actions_at_least_78(self):
        assert len(action_registry.all_ids()) >= 78


class TestResolverFinance:
    def test_buchung_erfassen(self):
        result = intent_resolver.resolve("Buchung erfassen")
        assert result is not None
        assert result.action_id == "finance-booking"

    def test_op_debitoren(self):
        result = intent_resolver.resolve("Offene Posten Debitoren")
        assert result is not None
        assert result.action_id == "nav-op-debitoren"

    def test_zahlungslaeufe(self):
        result = intent_resolver.resolve("Zahlungsläufe öffnen")
        assert result is not None
        assert result.action_id == "nav-zahlungslaeufe"

    def test_hauptbuch(self):
        result = intent_resolver.resolve("Hauptbuch öffnen")
        assert result is not None
        assert result.action_id == "nav-fibu-hauptbuch"

    def test_konto_extraktion(self):
        result = intent_resolver.resolve("Buchung erfassen Konto 1200")
        assert result is not None
        assert result.params.get("account_number") == "1200"


class TestResolverCompliance:
    def test_verarbeitungsverzeichnis(self):
        result = intent_resolver.resolve("Verarbeitungsverzeichnis")
        assert result is not None
        assert result.action_id == "nav-verarbeitungsverzeichnis"

    def test_datenpannen(self):
        result = intent_resolver.resolve("Datenpanne melden")
        assert result is not None
        assert result.action_id == "nav-datenpannen"

    def test_dsgvo_anfragen(self):
        result = intent_resolver.resolve("DSGVO Anfragen")
        assert result is not None
        assert result.action_id == "compliance-dsgvo-anfragen"

    def test_compliance_dashboard(self):
        result = intent_resolver.resolve("Compliance öffnen")
        assert result is not None
        assert result.action_id == "nav-compliance-dashboard"


class TestResolverAgrar:
    def test_ernte_erfassen(self):
        result = intent_resolver.resolve("Ernte erfassen")
        assert result is not None
        assert result.action_id == "agrar-ernte-erfassen"

    def test_ernte_annahme(self):
        result = intent_resolver.resolve("Ernte Annahme")
        assert result is not None
        assert result.action_id == "nav-ernte-annahme"

    def test_feldbuch(self):
        result = intent_resolver.resolve("Feldbuch öffnen")
        assert result is not None
        assert result.action_id == "nav-feldbuch"

    def test_silos(self):
        result = intent_resolver.resolve("Silos öffnen")
        assert result is not None
        assert result.action_id == "nav-silos"

    def test_menge_extraktion(self):
        result = intent_resolver.resolve("Ernte erfassen 12 t Weizen")
        assert result is not None
        assert result.params.get("quantity") == "12"


class TestResolverLogistik:
    def test_tour_planen(self):
        result = intent_resolver.resolve("Tour planen")
        assert result is not None
        assert result.action_id == "logistik-tour-planen"

    def test_tourenplanung(self):
        result = intent_resolver.resolve("Tourenplanung")
        assert result is not None
        assert result.action_id == "nav-tourenplanung"

    def test_frachtbriefe(self):
        result = intent_resolver.resolve("Frachtbriefe öffnen")
        assert result is not None
        assert result.action_id == "nav-frachtbriefe"

    def test_logistik_nav(self):
        result = intent_resolver.resolve("Gehe zu Logistik öffnen")
        assert result is not None
        assert result.action_id == "nav-logistik"
