"""
Wave 81 — Policy Explainability im UI (Gap 019)

Tests für explain_policy_result(), PolicyExplanation, PolicyReasonEntry,
ExplanationVerbosity und PolicyExplainabilityCache.

Gap 019: Policy Explainability im UI — KPI: 50% weniger Support-Rückfragen
"""
from __future__ import annotations

import pytest

from app.core.policy_code_engine import (
    PolicyAktion,
    PolicyBedingung,
    PolicyBedingungsTyp,
    PolicyEvaluationResult,
    PolicyRegel,
    PolicyRegelTreffer,
    PolicySet,
    evaluate_policy_set,
    get_default_agrar_policy_sets,
)
from app.core.policy_explainability_contracts import (
    EntscheidungsErgebnis,
    ExplanationVerbosity,
    PolicyExplainabilityCache,
    PolicyExplanation,
    PolicyReasonEntry,
    explain_policy_result,
)


# ---------------------------------------------------------------------------
# Fixture-Helpers
# ---------------------------------------------------------------------------

def _make_result(
    aktion: PolicyAktion = PolicyAktion.ERLAUBT,
    treffer: list[PolicyRegelTreffer] | None = None,
    kein_treffer: bool = False,
    prozess_key: str = "test.prozess",
    policy_set_id: str = "PS-TEST",
) -> PolicyEvaluationResult:
    return PolicyEvaluationResult(
        policy_set_id=policy_set_id,
        prozess_key=prozess_key,
        wirksame_aktion=aktion,
        treffer=treffer or [],
        kein_treffer=kein_treffer,
    )


def _make_treffer(
    regel_id: str = "R-001",
    bezeichnung: str = "Testregel",
    aktion: PolicyAktion = PolicyAktion.ERLAUBT,
    begruendung: str = "Betrag im Limit",
) -> PolicyRegelTreffer:
    return PolicyRegelTreffer(
        regel_id=regel_id,
        bezeichnung=bezeichnung,
        aktion=aktion,
        prioritaet=1,
        begruendung=begruendung,
    )


# ---------------------------------------------------------------------------
# TestExplainPolicyResult — Kein Treffer
# ---------------------------------------------------------------------------

class TestExplainNoMatch:
    """kein_treffer=True → KEINE_REGEL, implizit freigegeben."""

    def test_kein_treffer_ergibt_keine_regel(self):
        result = _make_result(kein_treffer=True, aktion=PolicyAktion.ERLAUBT)
        exp = explain_policy_result(result)
        assert exp.entscheidung == EntscheidungsErgebnis.KEINE_REGEL

    def test_kein_treffer_ist_freigegeben(self):
        result = _make_result(kein_treffer=True)
        exp = explain_policy_result(result)
        assert exp.ist_freigegeben is True

    def test_kein_treffer_keine_gruende(self):
        result = _make_result(kein_treffer=True)
        exp = explain_policy_result(result)
        assert len(exp.gruende) == 0

    def test_kein_treffer_zusammenfassung_enthaelt_hinweis(self):
        result = _make_result(kein_treffer=True)
        exp = explain_policy_result(result)
        assert "keine" in exp.zusammenfassung.lower() or "freigegeben" in exp.zusammenfassung.lower()


# ---------------------------------------------------------------------------
# TestExplainPolicyResult — Erlaubt
# ---------------------------------------------------------------------------

class TestExplainErlaubt:
    """PolicyAktion.ERLAUBT → EntscheidungsErgebnis.FREIGEGEBEN."""

    def test_erlaubt_ergibt_freigegeben(self):
        result = _make_result(
            aktion=PolicyAktion.ERLAUBT,
            treffer=[_make_treffer(aktion=PolicyAktion.ERLAUBT)],
        )
        exp = explain_policy_result(result)
        assert exp.entscheidung == EntscheidungsErgebnis.FREIGEGEBEN

    def test_erlaubt_ist_freigegeben(self):
        result = _make_result(
            aktion=PolicyAktion.ERLAUBT,
            treffer=[_make_treffer(aktion=PolicyAktion.ERLAUBT)],
        )
        assert explain_policy_result(result).ist_freigegeben is True

    def test_erlaubt_gruende_vorhanden(self):
        result = _make_result(
            aktion=PolicyAktion.ERLAUBT,
            treffer=[_make_treffer(aktion=PolicyAktion.ERLAUBT, bezeichnung="Standardfreigabe")],
        )
        exp = explain_policy_result(result)
        assert len(exp.gruende) >= 1

    def test_erlaubt_entscheidende_regel_markiert(self):
        result = _make_result(
            aktion=PolicyAktion.ERLAUBT,
            treffer=[_make_treffer(aktion=PolicyAktion.ERLAUBT)],
        )
        exp = explain_policy_result(result)
        assert any(g.ist_entscheidend for g in exp.gruende)


# ---------------------------------------------------------------------------
# TestExplainPolicyResult — Abgelehnt
# ---------------------------------------------------------------------------

class TestExplainAbgelehnt:
    """PolicyAktion.ABGELEHNT → EntscheidungsErgebnis.ABGELEHNT."""

    def test_abgelehnt_ergebnis(self):
        result = _make_result(
            aktion=PolicyAktion.ABGELEHNT,
            treffer=[_make_treffer(aktion=PolicyAktion.ABGELEHNT, bezeichnung="Betragslimit")],
        )
        exp = explain_policy_result(result)
        assert exp.entscheidung == EntscheidungsErgebnis.ABGELEHNT

    def test_abgelehnt_ist_nicht_freigegeben(self):
        result = _make_result(
            aktion=PolicyAktion.ABGELEHNT,
            treffer=[_make_treffer(aktion=PolicyAktion.ABGELEHNT)],
        )
        assert explain_policy_result(result).ist_freigegeben is False

    def test_abgelehnt_zusammenfassung_enthält_regelname(self):
        result = _make_result(
            aktion=PolicyAktion.ABGELEHNT,
            treffer=[_make_treffer(aktion=PolicyAktion.ABGELEHNT, bezeichnung="Vier-Augen-Prinzip")],
        )
        exp = explain_policy_result(result)
        assert "Vier-Augen-Prinzip" in exp.zusammenfassung

    def test_abgelehnt_ergebnis_text_enthält_regelname(self):
        result = _make_result(
            aktion=PolicyAktion.ABGELEHNT,
            treffer=[_make_treffer(
                aktion=PolicyAktion.ABGELEHNT,
                bezeichnung="Kontraktlimit",
                begruendung="Menge 150t > Limit 100t",
            )],
        )
        exp = explain_policy_result(result)
        assert "Kontraktlimit" in exp.gruende[0].ergebnis_text
        assert "Menge 150t" in exp.gruende[0].ergebnis_text


# ---------------------------------------------------------------------------
# TestExplainVerbosity
# ---------------------------------------------------------------------------

class TestExplainVerbosity:
    """Detailgrad beeinflusst Anzahl der zurückgegebenen Gründe."""

    def _multi_treffer_result(self) -> PolicyEvaluationResult:
        return _make_result(
            aktion=PolicyAktion.ABGELEHNT,
            treffer=[
                _make_treffer("R-001", "Regel A", PolicyAktion.ABGELEHNT),
                _make_treffer("R-002", "Regel B", PolicyAktion.ABGELEHNT),
                _make_treffer("R-003", "Regel C", PolicyAktion.ERLAUBT),
                _make_treffer("R-004", "Regel D", PolicyAktion.ERLAUBT),
            ],
        )

    def test_brief_gibt_nur_erste_entscheidende_regel(self):
        result = self._multi_treffer_result()
        exp = explain_policy_result(result, ExplanationVerbosity.BRIEF)
        assert len(exp.gruende) <= 1

    def test_standard_gibt_bis_drei_entscheidende_regeln(self):
        result = self._multi_treffer_result()
        exp = explain_policy_result(result, ExplanationVerbosity.STANDARD)
        assert len(exp.gruende) <= 3

    def test_detailed_gibt_alle_treffer(self):
        result = self._multi_treffer_result()
        exp = explain_policy_result(result, ExplanationVerbosity.DETAILED)
        assert len(exp.gruende) == 4

    def test_anzahl_gepruefter_regeln_immer_vollständig(self):
        result = self._multi_treffer_result()
        for v in ExplanationVerbosity:
            exp = explain_policy_result(result, v)
            assert exp.anzahl_gepruefter_regeln == 4


# ---------------------------------------------------------------------------
# TestPolicyExplanation — Eigenschaften
# ---------------------------------------------------------------------------

class TestPolicyExplanation:
    """PolicyExplanation Hilfseigenschaften."""

    def test_icon_freigegeben(self):
        exp = PolicyExplanation(
            entscheidung=EntscheidungsErgebnis.FREIGEGEBEN,
            zusammenfassung="ok",
        )
        assert exp.icon == "CheckCircle2"

    def test_icon_abgelehnt(self):
        exp = PolicyExplanation(
            entscheidung=EntscheidungsErgebnis.ABGELEHNT,
            zusammenfassung="nein",
        )
        assert exp.icon == "XCircle"

    def test_badge_farbe_freigegeben(self):
        exp = PolicyExplanation(
            entscheidung=EntscheidungsErgebnis.FREIGEGEBEN,
            zusammenfassung="ok",
        )
        assert exp.badge_farbe == "green"

    def test_badge_farbe_abgelehnt(self):
        exp = PolicyExplanation(
            entscheidung=EntscheidungsErgebnis.ABGELEHNT,
            zusammenfassung="nein",
        )
        assert exp.badge_farbe == "red"

    def test_badge_farbe_warnung(self):
        exp = PolicyExplanation(
            entscheidung=EntscheidungsErgebnis.WARNUNG,
            zusammenfassung="warnung",
        )
        assert exp.badge_farbe == "amber"

    def test_entscheidende_gruende_filter(self):
        g1 = PolicyReasonEntry("R-1", "A", PolicyAktion.ABGELEHNT, "text", ist_entscheidend=True)
        g2 = PolicyReasonEntry("R-2", "B", PolicyAktion.ERLAUBT, "text", ist_entscheidend=False)
        exp = PolicyExplanation(
            entscheidung=EntscheidungsErgebnis.ABGELEHNT,
            zusammenfassung="nein",
            gruende=[g1, g2],
        )
        assert len(exp.entscheidende_gruende) == 1
        assert exp.entscheidende_gruende[0].regel_id == "R-1"

    def test_as_dict_vollstaendig(self):
        exp = PolicyExplanation(
            entscheidung=EntscheidungsErgebnis.FREIGEGEBEN,
            zusammenfassung="ok",
            prozess_key="test.prozess",
            policy_set_id="PS-TEST",
        )
        d = exp.as_dict()
        assert d["entscheidung"] == "FREIGEGEBEN"
        assert d["ist_freigegeben"] is True
        assert "icon" in d
        assert "badge_farbe" in d
        assert "schema_version" in d


# ---------------------------------------------------------------------------
# TestPolicyExplainabilityCache
# ---------------------------------------------------------------------------

class TestPolicyExplainabilityCache:
    """Cache für Policy-Erklärungen."""

    def _exp(self) -> PolicyExplanation:
        return PolicyExplanation(
            entscheidung=EntscheidungsErgebnis.FREIGEGEBEN,
            zusammenfassung="ok",
        )

    def test_put_und_get(self):
        cache = PolicyExplainabilityCache()
        exp = self._exp()
        cache.put("PS-1", "p.key", "hash123", exp)
        result = cache.get("PS-1", "p.key", "hash123")
        assert result is exp

    def test_get_unbekannt_gibt_none(self):
        cache = PolicyExplainabilityCache()
        assert cache.get("PS-X", "p.key", "hash") is None

    def test_size_wächst(self):
        cache = PolicyExplainabilityCache()
        assert cache.size == 0
        cache.put("PS-1", "p.key", "h1", self._exp())
        assert cache.size == 1
        cache.put("PS-1", "p.key", "h2", self._exp())
        assert cache.size == 2

    def test_invalidate_löscht_policy_set(self):
        cache = PolicyExplainabilityCache()
        cache.put("PS-1", "p1", "h1", self._exp())
        cache.put("PS-1", "p2", "h2", self._exp())
        cache.put("PS-2", "p1", "h1", self._exp())
        deleted = cache.invalidate("PS-1")
        assert deleted == 2
        assert cache.size == 1

    def test_invalidate_unbekanntes_set(self):
        cache = PolicyExplainabilityCache()
        assert cache.invalidate("PS-NICHT-VORHANDEN") == 0


# ---------------------------------------------------------------------------
# TestIntegrationSzenario
# ---------------------------------------------------------------------------

class TestIntegrationSzenario:
    """End-to-End: evaluate_policy_set() → explain_policy_result()."""

    def test_agrar_policy_set_erklärt_freigabe(self):
        """evaluate_policy_set() + explain_policy_result() auf echtem AgrarPolicySet."""
        policy_sets = get_default_agrar_policy_sets()
        assert len(policy_sets) > 0
        ps = policy_sets[0]

        # Kontext der alle Regeln im Freigabe-PolicySet erfüllt
        kontext = {"betrag": 500, "rolle": "sachbearbeiter", "vier_augen": True}
        result = evaluate_policy_set(ps, kontext)
        exp = explain_policy_result(result)

        assert exp.entscheidung in {
            EntscheidungsErgebnis.FREIGEGEBEN,
            EntscheidungsErgebnis.KEINE_REGEL,
            EntscheidungsErgebnis.WARNUNG,
            EntscheidungsErgebnis.ESKALATION,
            EntscheidungsErgebnis.ABGELEHNT,
        }
        assert exp.zusammenfassung != ""
        assert exp.prozess_key == ps.prozess_key

    def test_alle_ergebnisse_haben_deutsche_zusammenfassung(self):
        """Keine englischen Begriffe in zusammenfassung."""
        englisch = ["approved", "rejected", "warning", "escalation", "no rule"]
        aktionen = [
            (PolicyAktion.ERLAUBT, [_make_treffer(aktion=PolicyAktion.ERLAUBT)]),
            (PolicyAktion.ABGELEHNT, [_make_treffer(aktion=PolicyAktion.ABGELEHNT, bezeichnung="Limit")]),
            (PolicyAktion.WARNUNG, [_make_treffer(aktion=PolicyAktion.WARNUNG, bezeichnung="Grenzwert")]),
            (PolicyAktion.ESKALATION, [_make_treffer(aktion=PolicyAktion.ESKALATION, bezeichnung="Freigabe")]),
        ]
        for aktion, treffer in aktionen:
            result = _make_result(aktion=aktion, treffer=treffer)
            exp = explain_policy_result(result)
            for kw in englisch:
                assert kw not in exp.zusammenfassung.lower(), \
                    f"Englisches Keyword '{kw}' in Zusammenfassung: '{exp.zusammenfassung}'"

    def test_support_rückfrage_szenario(self):
        """Benutzer fragt: warum wurde Zahlung abgelehnt?"""
        result = _make_result(
            aktion=PolicyAktion.ABGELEHNT,
            treffer=[
                _make_treffer("R-LIMIT", "Betragslimit Zahlung",
                              PolicyAktion.ABGELEHNT, "Betrag 10.000€ > Limit 5.000€"),
            ],
            prozess_key="zahlung.freigabe",
        )
        exp = explain_policy_result(result, ExplanationVerbosity.DETAILED)

        # Benutzer sieht: Entscheidung, Zusammenfassung, Regelname, Begründung
        assert exp.ist_freigegeben is False
        assert "Betragslimit Zahlung" in exp.zusammenfassung
        assert len(exp.gruende) == 1
        assert "10.000€" in exp.gruende[0].ergebnis_text
        assert exp.badge_farbe == "red"
        assert exp.icon == "XCircle"
