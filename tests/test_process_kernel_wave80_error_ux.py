"""
Wave 80 — Leitsystem für Ausnahmefälle / Error UX (Gap 028)

Tests für classify_http_error(), classify_network_error(),
classify_business_rule_error() und ErrorUxRegistry.

Gap 028: Leitsystem für Ausnahmefälle — KPI: 50% weniger Abbruchquote bei Fehlern
"""
from __future__ import annotations

import pytest

from app.core.error_ux_contracts import (
    ErrorCategory,
    ErrorSeverity,
    ErrorUxRegistry,
    RecoveryAction,
    UserFacingError,
    classify_business_rule_error,
    classify_http_error,
    classify_network_error,
    get_default_error_registry,
)


# ---------------------------------------------------------------------------
# TestClassifyHttpError
# ---------------------------------------------------------------------------

class TestClassifyHttpError:
    """HTTP-Statuscodes werden in UserFacingErrors übersetzt."""

    def test_400_validation_error(self):
        err = classify_http_error(400)
        assert err.category == ErrorCategory.VALIDATION
        assert err.severity == ErrorSeverity.RECOVERABLE
        assert err.support_code == "ERR-VALIDATION-400"
        assert len(err.recovery_actions) >= 1

    def test_401_authorization_error(self):
        err = classify_http_error(401)
        assert err.category == ErrorCategory.AUTHORIZATION
        assert err.severity == ErrorSeverity.BLOCKING
        assert "ERR-AUTH" in err.support_code
        assert err.data_loss_risk is True

    def test_403_authorization_error(self):
        err = classify_http_error(403)
        assert err.category == ErrorCategory.AUTHORIZATION
        assert err.severity == ErrorSeverity.BLOCKING
        assert "ERR-AUTH-403" in err.support_code

    def test_404_not_found(self):
        err = classify_http_error(404)
        assert err.category == ErrorCategory.NOT_FOUND
        assert err.severity == ErrorSeverity.RECOVERABLE
        assert err.data_loss_risk is False

    def test_409_conflict(self):
        err = classify_http_error(409)
        assert err.category == ErrorCategory.CONFLICT
        assert err.data_loss_risk is True
        assert err.support_code == "ERR-CONFLICT-409"

    def test_409_hat_refresh_merge_aktion(self):
        err = classify_http_error(409)
        keys = {a.action_key for a in err.recovery_actions}
        assert "refresh_merge" in keys or "save_draft" in keys

    def test_422_fachliche_validierung(self):
        err = classify_http_error(422)
        assert err.category == ErrorCategory.VALIDATION
        assert "ERR-VALIDATION-422" in err.support_code

    def test_422_mit_detail_text(self):
        err = classify_http_error(422, detail="Menge überschreitet Kontraktlimit")
        assert "Menge" in err.detail

    def test_500_server_error(self):
        err = classify_http_error(500)
        assert err.category == ErrorCategory.SERVER
        assert err.severity == ErrorSeverity.BLOCKING
        assert err.data_loss_risk is True

    def test_502_server_error(self):
        err = classify_http_error(502)
        assert err.category == ErrorCategory.SERVER

    def test_503_unavailable(self):
        err = classify_http_error(503)
        assert err.category == ErrorCategory.NETWORK
        assert err.severity == ErrorSeverity.BLOCKING

    def test_504_timeout(self):
        err = classify_http_error(504)
        assert err.category == ErrorCategory.TIMEOUT
        assert err.data_loss_risk is True

    def test_unbekannter_code_fallback(self):
        err = classify_http_error(418)  # I'm a teapot
        assert err.category == ErrorCategory.UNKNOWN
        assert "418" in err.support_code

    def test_kontext_wird_in_titel_eingebettet(self):
        err = classify_http_error(400, context="Speichern")
        assert "Speichern" in err.title

    def test_alle_fehler_haben_mindestens_eine_aktion(self):
        for code in (400, 401, 403, 404, 409, 422, 500, 503, 504):
            err = classify_http_error(code)
            assert len(err.recovery_actions) >= 1, f"Code {code} hat keine Aktionen"


# ---------------------------------------------------------------------------
# TestClassifyNetworkError
# ---------------------------------------------------------------------------

class TestClassifyNetworkError:
    """Netzwerkfehler (offline, DNS, fetch failed)."""

    def test_netzwerkfehler_kategorie(self):
        err = classify_network_error()
        assert err.category == ErrorCategory.NETWORK
        assert err.severity == ErrorSeverity.BLOCKING

    def test_netzwerkfehler_hat_retry_aktion(self):
        err = classify_network_error()
        keys = {a.action_key for a in err.recovery_actions}
        assert "retry" in keys

    def test_netzwerkfehler_tipp_enthalten(self):
        err = classify_network_error()
        assert err.tip != ""

    def test_netzwerkfehler_support_code(self):
        err = classify_network_error()
        assert err.support_code == "ERR-NETWORK-OFFLINE"


# ---------------------------------------------------------------------------
# TestClassifyBusinessRuleError
# ---------------------------------------------------------------------------

class TestClassifyBusinessRuleError:
    """Fachliche Regelabweichungen."""

    def test_business_rule_kategorie(self):
        err = classify_business_rule_error("Kontraktlimit überschritten")
        assert err.category == ErrorCategory.BUSINESS_RULE
        assert err.severity == ErrorSeverity.RECOVERABLE

    def test_regel_name_im_titel(self):
        err = classify_business_rule_error("Mindestmenge unterschritten")
        assert "Mindestmenge" in err.title

    def test_detail_parameter_wird_genutzt(self):
        err = classify_business_rule_error(
            "Lagerlimit",
            detail="Das Lager Silo-A hat noch 50t freie Kapazität."
        )
        assert "50t" in err.detail

    def test_support_code_enthält_regel(self):
        err = classify_business_rule_error("Freigabe fehlt")
        assert "ERR-RULE-" in err.support_code


# ---------------------------------------------------------------------------
# TestUserFacingError
# ---------------------------------------------------------------------------

class TestUserFacingError:
    """UserFacingError Struktur und Hilfseigenschaften."""

    def _make_error(self, **kwargs) -> UserFacingError:
        defaults = {
            "category": ErrorCategory.SERVER,
            "severity": ErrorSeverity.BLOCKING,
            "title": "Testfehler",
            "detail": "Detailbeschreibung",
            "recovery_actions": [
                RecoveryAction("Primär", "retry", primary=True),
                RecoveryAction("Sekundär", "back", primary=False),
            ],
        }
        defaults.update(kwargs)
        return UserFacingError(**defaults)

    def test_primary_action_gibt_erste_primaere_zurueck(self):
        err = self._make_error()
        assert err.primary_action is not None
        assert err.primary_action.action_key == "retry"

    def test_primary_action_none_wenn_keine_aktionen(self):
        err = self._make_error(recovery_actions=[])
        assert err.primary_action is None

    def test_secondary_actions_listet_nicht_primaere(self):
        err = self._make_error()
        assert len(err.secondary_actions) == 1
        assert err.secondary_actions[0].action_key == "back"

    def test_as_dict_vollstaendig(self):
        err = self._make_error(support_code="ERR-TEST-001", tip="Tipp hier")
        d = err.as_dict()
        assert d["category"] == "SERVER"
        assert d["severity"] == "BLOCKING"
        assert d["support_code"] == "ERR-TEST-001"
        assert d["tip"] == "Tipp hier"
        assert "primary_action" in d
        assert "recovery_actions" in d

    def test_data_loss_risk_default_false(self):
        err = self._make_error()
        assert err.data_loss_risk is False

    def test_recovery_action_as_dict(self):
        action = RecoveryAction("Neu laden", "reload", primary=True, icon="RefreshCw")
        d = action.as_dict()
        assert d["label"] == "Neu laden"
        assert d["action_key"] == "reload"
        assert d["primary"] is True
        assert d["icon"] == "RefreshCw"


# ---------------------------------------------------------------------------
# TestErrorUxRegistry
# ---------------------------------------------------------------------------

class TestErrorUxRegistry:
    """ErrorUxRegistry: Vordefinierte Fehlerszenarien."""

    def test_default_registry_enthält_standard_szenarien(self):
        registry = get_default_error_registry()
        keys = registry.keys()
        assert "session_expired" in keys
        assert "save_conflict" in keys
        assert "loading_failed" in keys
        assert "no_permission_for_action" in keys
        assert "workflow_blocked" in keys

    def test_session_expired_hat_login_aktion(self):
        registry = get_default_error_registry()
        err = registry.get("session_expired")
        assert err is not None
        keys = {a.action_key for a in err.recovery_actions}
        assert "login" in keys

    def test_save_conflict_ist_conflict_kategorie(self):
        registry = get_default_error_registry()
        err = registry.get("save_conflict")
        assert err.category == ErrorCategory.CONFLICT

    def test_workflow_blocked_ist_blocking(self):
        registry = get_default_error_registry()
        err = registry.get("workflow_blocked")
        assert err.severity == ErrorSeverity.BLOCKING

    def test_unbekannter_key_gibt_none(self):
        registry = get_default_error_registry()
        assert registry.get("gibt_es_nicht") is None

    def test_register_eigener_fehler(self):
        registry = ErrorUxRegistry()
        eigener = UserFacingError(
            category=ErrorCategory.BUSINESS_RULE,
            severity=ErrorSeverity.RECOVERABLE,
            title="Test",
            detail="Test-Detail",
        )
        registry.register("mein_fehler", eigener)
        assert registry.get("mein_fehler") is eigener
        assert "mein_fehler" in registry.keys()


# ---------------------------------------------------------------------------
# TestIntegrationSzenario
# ---------------------------------------------------------------------------

class TestIntegrationSzenario:
    """End-to-End Fehlerbehandlungsszenarien."""

    def test_alle_fehlermeldungen_auf_deutsch(self):
        """Fehlertitel müssen deutsche Wörter enthalten, keine rein englischen Fehlermeldungen."""
        codes = [400, 401, 403, 404, 409, 422, 500, 503, 504]
        # Rein englische Fehlermeldungen die auf keinen Fall erscheinen dürfen
        verbotene_titel = ["not found", "forbidden", "unauthorized", "bad request",
                           "internal server error", "gateway timeout", "service unavailable"]
        for code in codes:
            err = classify_http_error(code)
            title_lower = err.title.lower()
            for verboten in verbotene_titel:
                assert verboten not in title_lower, \
                    f"Englischer Titel für Code {code}: '{err.title}'"
        # Stichprobe: bekannte deutsche Wörter
        assert "berechtigung" in classify_http_error(403).title.lower()
        assert "gefunden" in classify_http_error(404).title.lower() or \
               "nicht" in classify_http_error(404).title.lower()

    def test_blocking_fehler_haben_immer_tipp(self):
        """BLOCKING-Fehler müssen einen Tipp enthalten."""
        blocking_codes = [401, 403, 500, 503]
        for code in blocking_codes:
            err = classify_http_error(code)
            if err.severity == ErrorSeverity.BLOCKING:
                assert err.tip != "", f"Code {code} hat keinen Tipp"

    def test_fehler_mit_datenverlust_haben_warnung_in_dict(self):
        """Fehler mit data_loss_risk=True sollen das im Dict reflektieren."""
        err = classify_http_error(409)
        d = err.as_dict()
        assert d["data_loss_risk"] is True

    def test_vollständiger_fehlerfluss_save_conflict(self):
        """Simuliert: Benutzer speichert, erhält 409, sieht Konflikt-Panel."""
        err = classify_http_error(409, context="Speichern")
        assert err.category == ErrorCategory.CONFLICT
        assert err.data_loss_risk is True
        assert err.primary_action is not None
        # Benutzer soll Daten zusammenführen oder Entwurf retten können
        action_keys = {a.action_key for a in err.recovery_actions}
        assert len(action_keys) >= 2

    def test_kpi_abdeckung_alle_8_kategorien(self):
        """Alle ErrorCategory-Werte sollen erreichbar sein."""
        kategorien = set()
        kategorien.add(classify_http_error(400).category)
        kategorien.add(classify_http_error(401).category)
        kategorien.add(classify_http_error(404).category)
        kategorien.add(classify_http_error(409).category)
        kategorien.add(classify_http_error(500).category)
        kategorien.add(classify_http_error(504).category)
        kategorien.add(classify_network_error().category)
        kategorien.add(classify_business_rule_error("Test").category)
        kategorien.add(classify_http_error(418).category)  # UNKNOWN

        erwartete = {
            ErrorCategory.VALIDATION,
            ErrorCategory.AUTHORIZATION,
            ErrorCategory.NOT_FOUND,
            ErrorCategory.CONFLICT,
            ErrorCategory.SERVER,
            ErrorCategory.TIMEOUT,
            ErrorCategory.NETWORK,
            ErrorCategory.BUSINESS_RULE,
            ErrorCategory.UNKNOWN,
        }
        assert kategorien == erwartete
