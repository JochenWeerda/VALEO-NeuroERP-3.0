"""
Tests für Slice-013d: Voice domain context filtering.
"""

from __future__ import annotations

from app.services.intent_resolver import intent_resolver


class TestVoiceDomainContext:
    def test_lager_domain_prefers_lager_nav(self):
        result = intent_resolver.resolve("Lager oeffnen", context={"domain": "lager"})
        assert result is not None
        assert result.action_id == "nav-lager"

    def test_sales_domain_blocks_lager_nav_on_generic_phrase(self):
        result = intent_resolver.resolve("Speichern", context={"domain": "sales"})
        assert result is not None
        assert result.action_id == "save-document"

    def test_finance_domain_resolves_fibu_intent(self):
        result = intent_resolver.resolve("Zahlungslauf", context={"domain": "finance"})
        assert result is not None
        assert result.action_id == "nav-zahlungslaeufe"

    def test_logistics_alias(self):
        result = intent_resolver.resolve("Tourenplanung", context={"domain": "logistics"})
        assert result is not None
        assert result.action_id == "nav-tourenplanung"

    def test_without_domain_still_resolves(self):
        result = intent_resolver.resolve("Inventur starten")
        assert result is not None
        assert result.action_id == "lager-inventur"
