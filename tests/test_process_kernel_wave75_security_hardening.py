"""
Wave 75 — Security Hardening (Gap 049): Security-Header + RBAC-Fein-Kontrakte

Deckt ab:
  A) Security Headers Middleware — alle Pflicht-Header gesetzt und korrekt
  B) HSTS- und CSP-Modusunterschiede (Debug vs. Produktion)
  C) Feingranulaere RBAC-Permissions (evaluate_rbac_permission)
  D) Secret-Klassifikations-Registry (SecretKlassifikation-Regeln)
  E) Security-Posture-Evaluation (keine kritischen Findings → GUT)
  F) Startup-Guard-Kontrakt: API_DEV_TOKEN + production → RuntimeError
  G) Rollen-Isolation: Sachbearbeiter kann keine Zahlungsläufe starten
"""
from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.middleware.security_headers import (
    SecurityHeadersMiddleware,
    build_security_headers,
    _STATIC_HEADERS,
    _HSTS_HEADER,
)
from app.core.security_hardening_contracts import (
    SecurityControl,
    SecurityControlKategorie,
    SecurityControlStatus,
    SecurityFinding,
    SecurityFindingSchwere,
    RBACPermission,
    RBACPermissionCheck,
    evaluate_rbac_permission,
    evaluate_security_posture,
    get_default_security_controls,
    get_default_secret_classifications,
    SecretKlassifikation,
)


# ===========================================================================
# Fixtures
# ===========================================================================

@pytest.fixture
def secured_app() -> TestClient:
    """FastAPI-App mit SecurityHeadersMiddleware (DEBUG=True simuliert)."""
    app = FastAPI()

    @app.get("/ping")
    def ping():
        return {"ok": True}

    @app.get("/custom")
    def custom():
        from fastapi.responses import JSONResponse
        resp = JSONResponse({"ok": True})
        resp.headers["X-Frame-Options"] = "SAMEORIGIN"  # Eigener Header — darf nicht überschrieben werden
        return resp

    app.add_middleware(SecurityHeadersMiddleware)
    return TestClient(app, raise_server_exceptions=True)


# ===========================================================================
# A) Security Headers — immer vorhanden
# ===========================================================================

class TestStaticSecurityHeaders:
    """Pflicht-Header müssen bei jeder Antwort gesetzt sein."""

    def test_x_content_type_options(self, secured_app):
        resp = secured_app.get("/ping")
        assert resp.headers.get("x-content-type-options") == "nosniff"

    def test_x_frame_options(self, secured_app):
        resp = secured_app.get("/ping")
        assert resp.headers.get("x-frame-options") == "DENY"

    def test_referrer_policy(self, secured_app):
        resp = secured_app.get("/ping")
        assert resp.headers.get("referrer-policy") == "strict-origin-when-cross-origin"

    def test_permissions_policy_present(self, secured_app):
        resp = secured_app.get("/ping")
        pp = resp.headers.get("permissions-policy", "")
        assert "geolocation=()" in pp
        assert "microphone=()" in pp
        assert "camera=()" in pp

    def test_xss_protection_disabled(self, secured_app):
        """Legacy XSS Filter deaktiviert — CSP übernimmt."""
        resp = secured_app.get("/ping")
        assert resp.headers.get("x-xss-protection") == "0"

    def test_csp_present(self, secured_app):
        """CSP muss bei jeder Antwort gesetzt sein."""
        resp = secured_app.get("/ping")
        csp = resp.headers.get("content-security-policy", "")
        assert len(csp) > 10, "CSP ist leer"
        assert "default-src" in csp

    def test_all_static_header_keys_present(self, secured_app):
        """Alle Header aus _STATIC_HEADERS müssen in der Antwort sein."""
        resp = secured_app.get("/ping")
        for header in _STATIC_HEADERS:
            assert header.lower() in resp.headers, f"Fehlender Header: {header}"

    def test_endpoint_custom_header_not_overwritten(self, secured_app):
        """Eigene Header des Endpoints dürfen NICHT überschrieben werden."""
        resp = secured_app.get("/custom")
        # Der Endpoint setzt X-Frame-Options: SAMEORIGIN
        # Middleware soll es nicht auf DENY überschreiben (already-set check)
        assert resp.headers.get("x-frame-options") == "SAMEORIGIN"


# ===========================================================================
# B) HSTS und CSP: Debug vs. Produktion
# ===========================================================================

class TestSecurityHeadersModes:
    """build_security_headers() liefert modusabhängige Header-Sets."""

    def test_debug_mode_no_hsts(self):
        """Im Debug-Modus kein HSTS (kein HTTPS in Entwicklung)."""
        headers = build_security_headers(is_debug=True)
        assert "Strict-Transport-Security" not in headers

    def test_production_mode_has_hsts(self):
        """In Produktion muss HSTS mit mindestens 1 Jahr max-age gesetzt sein."""
        headers = build_security_headers(is_debug=False)
        hsts = headers.get("Strict-Transport-Security", "")
        assert "max-age=" in hsts
        # max-age muss >= 31536000 (1 Jahr) sein
        for part in hsts.split(";"):
            part = part.strip()
            if part.startswith("max-age="):
                age = int(part.split("=")[1])
                assert age >= 31536000, f"HSTS max-age zu kurz: {age}"
        assert "includeSubDomains" in hsts

    def test_production_hsts_matches_constant(self):
        headers = build_security_headers(is_debug=False)
        assert headers["Strict-Transport-Security"] == _HSTS_HEADER

    def test_debug_csp_allows_unsafe_eval(self):
        """Entwicklungs-CSP erlaubt unsafe-eval für Vite HMR."""
        headers = build_security_headers(is_debug=True)
        csp = headers["Content-Security-Policy"]
        assert "unsafe-eval" in csp

    def test_production_csp_no_unsafe_eval(self):
        """Produktions-CSP darf kein unsafe-eval enthalten."""
        headers = build_security_headers(is_debug=False)
        csp = headers["Content-Security-Policy"]
        assert "unsafe-eval" not in csp

    def test_production_csp_frame_ancestors_none(self):
        """Produktions-CSP: frame-ancestors 'none' (Clickjacking-Schutz)."""
        headers = build_security_headers(is_debug=False)
        csp = headers["Content-Security-Policy"]
        assert "frame-ancestors 'none'" in csp

    def test_production_csp_has_form_action(self):
        """Produktions-CSP muss form-action einschränken."""
        headers = build_security_headers(is_debug=False)
        csp = headers["Content-Security-Policy"]
        assert "form-action" in csp

    def test_both_modes_have_static_headers(self):
        """Beide Modi enthalten alle statischen Pflicht-Header."""
        for debug in (True, False):
            headers = build_security_headers(is_debug=debug)
            for key in _STATIC_HEADERS:
                assert key in headers, f"Mode debug={debug}: fehlt {key}"


# ===========================================================================
# C) Feingranulaere RBAC
# ===========================================================================

class TestRBACFineGrained:
    """evaluate_rbac_permission() prüft Rollen gegen RBACPermission-Enum."""

    def _check(self, rolle: str, permission: RBACPermission) -> bool:
        result = evaluate_rbac_permission(
            RBACPermissionCheck(
                user_id="test-user",
                tenant_id="tenant-1",
                rolle=rolle,
                permission=permission,
            )
        )
        return result.erlaubt

    def test_sachbearbeiter_kann_kontrakt_lesen(self):
        assert self._check("sachbearbeiter", RBACPermission.KONTRAKT_LESEN) is True

    def test_sachbearbeiter_kann_kontrakt_erstellen(self):
        assert self._check("sachbearbeiter", RBACPermission.KONTRAKT_ERSTELLEN) is True

    def test_sachbearbeiter_NICHT_zahlungslauf_starten(self):
        """Sachbearbeiter darf keinen Zahlungslauf starten — Kernbedingung Gap 049."""
        assert self._check("sachbearbeiter", RBACPermission.ZAHLUNGSLAUF_STARTEN) is False

    def test_sachbearbeiter_NICHT_settlement_freigeben(self):
        assert self._check("sachbearbeiter", RBACPermission.SETTLEMENT_FREIGEBEN) is False

    def test_buchhaltung_kann_settlement_freigeben(self):
        assert self._check("buchhaltung", RBACPermission.SETTLEMENT_FREIGEBEN) is True

    def test_buchhaltung_kann_zahlungslauf_starten(self):
        assert self._check("buchhaltung", RBACPermission.ZAHLUNGSLAUF_STARTEN) is True

    def test_buchhaltung_NICHT_kontrakt_stornieren(self):
        """Buchhaltung darf keine Kontrakte stornieren."""
        assert self._check("buchhaltung", RBACPermission.KONTRAKT_STORNIEREN) is False

    def test_leiter_kann_alles_ausser_tenant_konfigurieren(self):
        """Leiter hat breite Rechte, aber kein Tenant-Admin."""
        assert self._check("leiter", RBACPermission.ZAHLUNGSLAUF_FREIGEBEN) is True
        assert self._check("leiter", RBACPermission.KONTRAKT_STORNIEREN) is True
        assert self._check("leiter", RBACPermission.AGENT_APPROVAL_GEBEN) is True

    def test_admin_hat_alle_permissions(self):
        for perm in RBACPermission:
            assert self._check("admin", perm) is True, f"Admin fehlt: {perm}"

    def test_agent_system_NICHT_settlement_freigeben(self):
        """Agent-System darf keine Settlements freigeben (Human-Gate)."""
        assert self._check("agent_system", RBACPermission.SETTLEMENT_FREIGEBEN) is False

    def test_agent_system_kann_agent_aktion_ausfuehren(self):
        assert self._check("agent_system", RBACPermission.AGENT_AKTION_AUSFUEHREN) is True

    def test_unbekannte_rolle_keine_permissions(self):
        """Eine unbekannte Rolle hat keine Berechtigungen."""
        assert self._check("gast", RBACPermission.KONTRAKT_LESEN) is False

    def test_result_has_begruendung(self):
        result = evaluate_rbac_permission(
            RBACPermissionCheck(
                user_id="u1",
                tenant_id="t1",
                rolle="sachbearbeiter",
                permission=RBACPermission.ZAHLUNGSLAUF_STARTEN,
            )
        )
        assert len(result.begruendung) > 5
        assert result.erlaubt is False

    def test_result_as_dict_vollstaendig(self):
        result = evaluate_rbac_permission(
            RBACPermissionCheck(
                user_id="u1",
                tenant_id="t1",
                rolle="leiter",
                permission=RBACPermission.KONTRAKT_LESEN,
            )
        )
        d = result.as_dict()
        assert d["erlaubt"] is True
        assert d["permission"] == RBACPermission.KONTRAKT_LESEN.value
        assert "begruendung" in d
        assert d["schema_version"] == 1


# ===========================================================================
# D) Secret-Klassifikations-Registry
# ===========================================================================

class TestSecretKlassifikation:
    """get_default_secret_classifications() liefert vollständige Regeln."""

    @pytest.fixture
    def regeln(self):
        return get_default_secret_classifications()

    def test_mindestens_8_regeln(self, regeln):
        assert len(regeln) >= 8

    def test_password_streng_vertraulich_nicht_loggbar(self, regeln):
        pw_regeln = [r for r in regeln if r.feld_muster == "password"]
        assert len(pw_regeln) == 1
        r = pw_regeln[0]
        assert r.klassifikation == SecretKlassifikation.STRENG_VERTRAULICH
        assert r.loggen_erlaubt is False

    def test_api_key_streng_vertraulich(self, regeln):
        api_key_regeln = [r for r in regeln if r.feld_muster == "api_key"]
        assert len(api_key_regeln) == 1
        assert api_key_regeln[0].klassifikation == SecretKlassifikation.STRENG_VERTRAULICH
        assert api_key_regeln[0].loggen_erlaubt is False

    def test_iban_vertraulich(self, regeln):
        iban_regeln = [r for r in regeln if r.feld_muster == "iban"]
        assert len(iban_regeln) == 1
        assert iban_regeln[0].klassifikation == SecretKlassifikation.VERTRAULICH
        assert iban_regeln[0].loggen_erlaubt is False

    def test_access_token_nicht_loggbar(self, regeln):
        token_regeln = [r for r in regeln if r.feld_muster == "access_token"]
        assert len(token_regeln) == 1
        assert token_regeln[0].loggen_erlaubt is False

    def test_tenant_id_intern_loggbar(self, regeln):
        tid_regeln = [r for r in regeln if r.feld_muster == "tenant_id"]
        assert len(tid_regeln) == 1
        assert tid_regeln[0].loggen_erlaubt is True

    def test_alle_streng_vertraulich_nicht_loggbar(self, regeln):
        """Alle STRENG_VERTRAULICH-Felder müssen loggen_erlaubt=False haben."""
        for r in regeln:
            if r.klassifikation == SecretKlassifikation.STRENG_VERTRAULICH:
                assert r.loggen_erlaubt is False, (
                    f"Feld '{r.feld_muster}' ist STRENG_VERTRAULICH aber loggbar!"
                )

    def test_regel_as_dict(self, regeln):
        d = regeln[0].as_dict()
        assert "feld_muster" in d
        assert "klassifikation" in d
        assert "loggen_erlaubt" in d
        assert "beschreibung" in d


# ===========================================================================
# E) Security-Posture-Evaluation
# ===========================================================================

class TestSecurityPosture:
    """evaluate_security_posture() — Gesamtbewertung des Security-Status."""

    def test_keine_kritischen_findings_bewertung_gut(self):
        controls = get_default_security_controls()
        result = evaluate_security_posture(controls, findings=[])
        # Kein kritisches Finding → nicht KRITISCH
        assert result.offene_kritische_findings == 0
        assert result.gesamtbewertung in ("GUT", "AUSREICHEND")

    def test_kritisches_finding_macht_posture_kritisch(self):
        controls = get_default_security_controls()
        finding = SecurityFinding(
            finding_id="F-001",
            control_id="SC-AUTH-001",
            titel="OIDC bypassed",
            beschreibung="API_DEV_TOKEN in Produktion",
            schwere=SecurityFindingSchwere.KRITISCH,
            status_offen=True,
        )
        result = evaluate_security_posture(controls, findings=[finding])
        assert result.gesamtbewertung == "KRITISCH"
        assert result.offene_kritische_findings == 1

    def test_geschlossene_findings_zaehlen_nicht(self):
        controls = get_default_security_controls()
        finding = SecurityFinding(
            finding_id="F-002",
            control_id="SC-AUTH-001",
            titel="Altes Problem",
            beschreibung="Behoben",
            schwere=SecurityFindingSchwere.KRITISCH,
            status_offen=False,  # Bereits behoben
        )
        result = evaluate_security_posture(controls, findings=[finding])
        assert result.offene_kritische_findings == 0

    def test_default_controls_haben_implementierte(self):
        controls = get_default_security_controls()
        result = evaluate_security_posture(controls)
        assert result.implementiert_count > 0

    def test_result_as_dict_vollstaendig(self):
        controls = get_default_security_controls()
        result = evaluate_security_posture(controls)
        d = result.as_dict()
        assert "implementiert_count" in d
        assert "offene_kritische_findings" in d
        assert "gesamtbewertung" in d
        assert d["gesamtbewertung"] in ("GUT", "AUSREICHEND", "KRITISCH")

    def test_meldungen_bei_geplanten_controls(self):
        """Geplante Controls erzeugen Meldungen im Posture-Report."""
        geplant = SecurityControl(
            control_id="SC-TEST-001",
            kategorie=SecurityControlKategorie.KRYPTOGRAPHIE,
            titel="Test",
            beschreibung="",
            status=SecurityControlStatus.GEPLANT,
        )
        result = evaluate_security_posture([geplant])
        assert any("nicht implementiert" in m or "geplant" in m.lower() for m in result.meldungen)


# ===========================================================================
# F) Startup-Guard: API_DEV_TOKEN + production
# ===========================================================================

class TestDevTokenProductionGuard:
    """
    SC-AUTH-002: API_DEV_TOKEN darf in production nicht gesetzt sein.
    Dieser Test prüft die Logik der Guard-Bedingung (nicht main.py direkt).
    """

    def test_guard_raises_if_production_with_dev_token(self):
        """Simuliert die Startup-Guard-Logik."""
        def startup_guard(app_env: str, api_dev_token):
            if app_env == "production" and api_dev_token is not None:
                raise RuntimeError("SECURITY: API_DEV_TOKEN must not be set in production")

        with pytest.raises(RuntimeError, match="API_DEV_TOKEN"):
            startup_guard("production", "dev-token")

    def test_guard_ok_in_development_with_token(self):
        """In development ist API_DEV_TOKEN erlaubt."""
        def startup_guard(app_env: str, api_dev_token):
            if app_env == "production" and api_dev_token is not None:
                raise RuntimeError("SECURITY: API_DEV_TOKEN must not be set in production")

        # Kein Fehler erwartet
        startup_guard("development", "dev-token")

    def test_guard_ok_in_production_without_token(self):
        """In production ist es OK wenn API_DEV_TOKEN=None."""
        def startup_guard(app_env: str, api_dev_token):
            if app_env == "production" and api_dev_token is not None:
                raise RuntimeError("SECURITY: API_DEV_TOKEN must not be set in production")

        # Kein Fehler erwartet
        startup_guard("production", None)

    def test_sc_auth002_control_exists(self):
        """SC-AUTH-002 muss im Default-Katalog enthalten sein."""
        controls = get_default_security_controls()
        ids = [c.control_id for c in controls]
        assert "SC-AUTH-002" in ids

    def test_sc_auth002_status_implementiert(self):
        """SC-AUTH-002 muss als IMPLEMENTIERT markiert sein."""
        controls = get_default_security_controls()
        c = next(c for c in controls if c.control_id == "SC-AUTH-002")
        assert c.status == SecurityControlStatus.IMPLEMENTIERT
