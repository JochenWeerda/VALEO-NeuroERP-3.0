"""
Tests für Slice-010: Voice-Intent Lager / Einkauf / HR.

Verifiziert:
- ActionRegistry enthält alle 15 neuen Lager/Einkauf/HR-Intents
- IntentResolver matcht typische Spracheingaben korrekt
- Parameterextraktion (EAN, Menge, Lieferant, Abwesenheitstyp)
- Keyword-Fallbacks greifen bei Freitext
- Keine Regression bestehender Intents
"""
from __future__ import annotations

import pytest

from app.services.action_registry import action_registry
from app.services.intent_resolver import intent_resolver


# ---------------------------------------------------------------------------
# ActionRegistry Tests
# ---------------------------------------------------------------------------

class TestActionRegistry:
    def test_lager_intents_registered(self):
        ids = action_registry.all_ids()
        for expected in ("nav-lager", "lager-wareneingang", "lager-inventur", "lager-umlagerung", "lager-artikel-suche"):
            assert expected in ids, f"Lager-Intent '{expected}' fehlt in registry"

    def test_einkauf_intents_registered(self):
        ids = action_registry.all_ids()
        for expected in ("nav-einkauf", "einkauf-bestellung-neu", "einkauf-lieferantenrechnung", "einkauf-angebot", "einkauf-lieferant-suche"):
            assert expected in ids, f"Einkauf-Intent '{expected}' fehlt in registry"

    def test_hr_intents_registered(self):
        ids = action_registry.all_ids()
        for expected in ("nav-hr", "hr-abwesenheit", "hr-mitarbeiter-neu", "hr-lohnlauf"):
            assert expected in ids, f"HR-Intent '{expected}' fehlt in registry"

    def test_total_actions_at_least_36(self):
        assert len(action_registry.all_ids()) >= 36

    def test_lager_domain_filter(self):
        assert len(action_registry.list_actions(domain="lager")) >= 5

    def test_einkauf_domain_filter(self):
        assert len(action_registry.list_actions(domain="einkauf")) >= 5

    def test_hr_domain_filter(self):
        assert len(action_registry.list_actions(domain="hr")) >= 4

    def test_intent_phrases_not_empty(self):
        for action_id in ("lager-wareneingang", "einkauf-bestellung-neu", "hr-abwesenheit"):
            phrases = action_registry.intent_phrases_for_action(action_id)
            assert len(phrases) >= 3, f"Zu wenige Intent-Phrasen für {action_id}"


# ---------------------------------------------------------------------------
# IntentResolver — Lager
# ---------------------------------------------------------------------------

class TestResolverLager:
    def test_wareneingang_phrase_match(self):
        result = intent_resolver.resolve("Wareneingang buchen")
        assert result is not None
        assert result.action_id == "lager-wareneingang"
        assert result.confidence >= 0.85

    def test_wareneingang_natuerlich(self):
        result = intent_resolver.resolve("Ich möchte einen Wareneingang erfassen")
        assert result is not None
        assert result.action_id == "lager-wareneingang"

    def test_inventur_phrase(self):
        result = intent_resolver.resolve("Inventur starten bitte")
        assert result is not None
        assert result.action_id == "lager-inventur"

    def test_bestand_zaehlen(self):
        result = intent_resolver.resolve("Bestand zählen")
        assert result is not None
        assert result.action_id == "lager-inventur"

    def test_umlagerung(self):
        result = intent_resolver.resolve("Ware umlagern zu Stellplatz B2")
        assert result is not None
        assert result.action_id == "lager-umlagerung"

    def test_artikelsuche_lager(self):
        result = intent_resolver.resolve("Artikel im Lager suchen")
        assert result is not None
        assert result.action_id == "lager-artikel-suche"

    def test_ean_extraktion(self):
        result = intent_resolver.resolve("Wareneingang buchen EAN 4006381333931")
        assert result is not None
        assert result.action_id == "lager-wareneingang"
        assert result.params.get("ean") == "4006381333931"

    def test_menge_extraktion(self):
        result = intent_resolver.resolve("Wareneingang 50 kg buchen")
        assert result is not None
        assert "quantity" in result.params

    def test_nav_lager(self):
        result = intent_resolver.resolve("Gehe zu Lager öffnen")
        assert result is not None
        assert result.action_id == "nav-lager"


# ---------------------------------------------------------------------------
# IntentResolver — Einkauf
# ---------------------------------------------------------------------------

class TestResolverEinkauf:
    def test_neue_bestellung(self):
        result = intent_resolver.resolve("Neue Bestellung anlegen")
        assert result is not None
        assert result.action_id == "einkauf-bestellung-neu"

    def test_bestellen_shortform(self):
        result = intent_resolver.resolve("Ich möchte bestellen")
        assert result is not None
        assert result.action_id == "einkauf-bestellung-neu"

    def test_lieferantenrechnung(self):
        result = intent_resolver.resolve("Lieferantenrechnung erfassen")
        assert result is not None
        assert result.action_id == "einkauf-lieferantenrechnung"

    def test_eingangsrechnung(self):
        result = intent_resolver.resolve("Eingangsrechnung buchen")
        assert result is not None
        assert result.action_id == "einkauf-lieferantenrechnung"

    def test_angebot_anfragen(self):
        result = intent_resolver.resolve("Angebot anfragen beim Lieferant")
        assert result is not None
        assert result.action_id == "einkauf-angebot"

    def test_preisanfrage(self):
        result = intent_resolver.resolve("Preisanfrage erstellen")
        assert result is not None
        assert result.action_id == "einkauf-angebot"

    def test_lieferant_suchen(self):
        result = intent_resolver.resolve("Lieferant suchen")
        assert result is not None
        assert result.action_id == "einkauf-lieferant-suche"

    def test_nav_einkauf(self):
        result = intent_resolver.resolve("Gehe zum Einkauf öffnen")
        assert result is not None
        assert result.action_id == "nav-einkauf"

    def test_bestellung_betrag_extraktion(self):
        result = intent_resolver.resolve("Neue Bestellung Betrag 1500 Euro")
        assert result is not None
        assert result.action_id == "einkauf-bestellung-neu"
        assert result.params.get("amount") == "1500"


# ---------------------------------------------------------------------------
# IntentResolver — HR
# ---------------------------------------------------------------------------

class TestResolverHR:
    def test_abwesenheit(self):
        result = intent_resolver.resolve("Abwesenheit erfassen")
        assert result is not None
        assert result.action_id == "hr-abwesenheit"

    def test_urlaub_eintragen(self):
        result = intent_resolver.resolve("Urlaub eintragen")
        assert result is not None
        assert result.action_id == "hr-abwesenheit"
        assert result.params.get("absence_type") == "URLAUB"

    def test_krankmeldung(self):
        result = intent_resolver.resolve("Krankmeldung erfassen")
        assert result is not None
        assert result.action_id == "hr-abwesenheit"
        assert result.params.get("absence_type") == "KRANKHEIT"

    def test_fehlzeit(self):
        result = intent_resolver.resolve("Fehlzeit erfassen für morgen")
        assert result is not None
        assert result.action_id == "hr-abwesenheit"

    def test_mitarbeiter_anlegen(self):
        result = intent_resolver.resolve("Neuer Mitarbeiter anlegen")
        assert result is not None
        assert result.action_id == "hr-mitarbeiter-neu"

    def test_lohnlauf(self):
        result = intent_resolver.resolve("Lohnlauf starten")
        assert result is not None
        assert result.action_id == "hr-lohnlauf"

    def test_gehaltsabrechnung(self):
        result = intent_resolver.resolve("Gehaltsabrechnung starten")
        assert result is not None
        assert result.action_id == "hr-lohnlauf"

    def test_nav_hr(self):
        result = intent_resolver.resolve("Gehe zu Personal öffnen")
        assert result is not None
        assert result.action_id == "nav-hr"

    def test_datum_extraktion(self):
        result = intent_resolver.resolve("Urlaub eintragen ab 15.06.2026")
        assert result is not None
        assert result.action_id == "hr-abwesenheit"
        assert result.params.get("date") == "2026-06-15"


# ---------------------------------------------------------------------------
# Regression: bestehende Intents nicht kaputt
# ---------------------------------------------------------------------------

class TestResolverRegression:
    def test_speichern_still_works(self):
        result = intent_resolver.resolve("Speichern")
        assert result is not None
        assert result.action_id == "save-document"

    def test_auftrag_zeigen_still_works(self):
        result = intent_resolver.resolve("Aufträge zeigen")
        assert result is not None
        assert result.action_id == "nav-orders"

    def test_neue_rechnung_still_works(self):
        result = intent_resolver.resolve("Neue Rechnung erstellen")
        assert result is not None
        assert result.action_id == "action-new-invoice"

    def test_unbekannter_befehl_returns_none(self):
        result = intent_resolver.resolve("Xyz Nonsense Blablabla")
        assert result is None
