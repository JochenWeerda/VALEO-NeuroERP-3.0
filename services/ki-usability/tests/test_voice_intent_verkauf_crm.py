"""
Tests für Slice-011: Voice-Intent Verkauf / CRM + Dispatch-Nachzug-Vorbereitung.
"""
from __future__ import annotations

from app.services.action_registry import action_registry
from app.services.intent_resolver import intent_resolver


class TestActionRegistryVerkaufCrm:
    def test_verkauf_intents_registered(self):
        ids = action_registry.all_ids()
        for expected in (
            "nav-verkauf",
            "nav-angebote",
            "nav-lieferscheine",
            "verkauf-angebot-neu",
            "verkauf-lieferschein-neu",
            "verkauf-kunde-suche",
            "verkauf-artikel-suche",
        ):
            assert expected in ids, f"Verkauf-Intent '{expected}' fehlt"

    def test_crm_intents_registered(self):
        ids = action_registry.all_ids()
        for expected in (
            "nav-crm",
            "nav-crm-leads",
            "nav-crm-aktivitaeten",
            "nav-crm-betriebsprofile",
            "nav-crm-kontakte",
            "crm-lead-neu",
            "crm-aktivitaet-neu",
            "crm-kontakt-suche",
        ):
            assert expected in ids, f"CRM-Intent '{expected}' fehlt"

    def test_total_actions_at_least_52(self):
        assert len(action_registry.all_ids()) >= 52

    def test_sales_domain_filter(self):
        assert len(action_registry.list_actions(domain="sales")) >= 10

    def test_crm_domain_filter(self):
        assert len(action_registry.list_actions(domain="crm")) >= 8


class TestResolverVerkauf:
    def test_neues_angebot(self):
        result = intent_resolver.resolve("Neues Angebot anlegen")
        assert result is not None
        assert result.action_id == "verkauf-angebot-neu"

    def test_neuer_lieferschein(self):
        result = intent_resolver.resolve("Neuer Lieferschein anlegen")
        assert result is not None
        assert result.action_id == "verkauf-lieferschein-neu"

    def test_angebotsliste(self):
        result = intent_resolver.resolve("Angebotsliste anzeigen")
        assert result is not None
        assert result.action_id == "nav-angebote"

    def test_lieferscheine_oeffnen(self):
        result = intent_resolver.resolve("Gehe zu Lieferscheinen öffnen")
        assert result is not None
        assert result.action_id == "nav-lieferscheine"

    def test_nav_verkauf(self):
        result = intent_resolver.resolve("Gehe zu Verkauf öffnen")
        assert result is not None
        assert result.action_id == "nav-verkauf"

    def test_kundenstamm_suchen(self):
        result = intent_resolver.resolve("Kundenstamm suchen")
        assert result is not None
        assert result.action_id == "verkauf-kunde-suche"

    def test_betrag_extraktion(self):
        result = intent_resolver.resolve("Neues Angebot Betrag 2500 Euro")
        assert result is not None
        assert result.action_id == "verkauf-angebot-neu"
        assert result.params.get("amount") == "2500"


class TestResolverCrm:
    def test_lead_anlegen(self):
        result = intent_resolver.resolve("Neuer Lead anlegen")
        assert result is not None
        assert result.action_id == "crm-lead-neu"

    def test_aktivitaet_anlegen(self):
        result = intent_resolver.resolve("Neue Aktivität anlegen")
        assert result is not None
        assert result.action_id == "crm-aktivitaet-neu"

    def test_kontakt_suchen(self):
        result = intent_resolver.resolve("Kontakt suchen")
        assert result is not None
        assert result.action_id == "crm-kontakt-suche"

    def test_leads_zeigen(self):
        result = intent_resolver.resolve("Leads anzeigen")
        assert result is not None
        assert result.action_id == "nav-crm-leads"

    def test_aktivitaeten_zeigen(self):
        result = intent_resolver.resolve("Aktivitäten anzeigen")
        assert result is not None
        assert result.action_id == "nav-crm-aktivitaeten"

    def test_betriebsprofile(self):
        result = intent_resolver.resolve("Betriebsprofile anzeigen")
        assert result is not None
        assert result.action_id == "nav-crm-betriebsprofile"

    def test_nav_crm(self):
        result = intent_resolver.resolve("CRM öffnen")
        assert result is not None
        assert result.action_id == "nav-crm"

    def test_datum_extraktion(self):
        result = intent_resolver.resolve("Neue Aktivität am 20.08.2026")
        assert result is not None
        assert result.action_id == "crm-aktivitaet-neu"
        assert result.params.get("date") == "2026-08-20"


class TestResolverRegressionSlice010:
    def test_lager_wareneingang_still_works(self):
        result = intent_resolver.resolve("Wareneingang buchen")
        assert result is not None
        assert result.action_id == "lager-wareneingang"

    def test_einkauf_bestellung_still_works(self):
        result = intent_resolver.resolve("Neue Bestellung anlegen")
        assert result is not None
        assert result.action_id == "einkauf-bestellung-neu"

    def test_neue_rechnung_still_works(self):
        result = intent_resolver.resolve("Neue Rechnung erstellen")
        assert result is not None
        assert result.action_id == "action-new-invoice"
