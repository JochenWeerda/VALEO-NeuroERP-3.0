"""
Wave 34 — Tests: Tenant-Rate-Limits (Gap 038) + Security-Hardening (Gap 049)

AP1/AP2: tenant_rate_limits.py — RateLimitPolicy, evaluate_rate_limit(), Cache-Configs
AP3:     process_kernel_api.py — GET /process/rate-limits, POST /process/rate-limits/check
AP4/AP5: security_hardening_contracts.py — SecurityControl, RBAC, SecretKlassifikation
AP6:     process_kernel_api.py — GET /process/security/controls, POST /process/security/rbac-check
"""
import pytest
from fastapi.testclient import TestClient


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def client():
    from app.main import app
    return TestClient(app, raise_server_exceptions=True)


# ---------------------------------------------------------------------------
# AP1/AP2 — tenant_rate_limits.py
# ---------------------------------------------------------------------------

class TestTenantRateLimitsCore:

    def setup_method(self):
        from app.core.tenant_rate_limits import (
            CacheStrategie,
            RateLimitBereich,
            RateLimitGranularitaet,
            RateLimitPolicy,
            RateLimitRequest,
            RateLimitResultTyp,
            evaluate_rate_limit,
            get_default_cache_configs,
            get_default_rate_limit_policies,
        )
        self.CacheStrategie = CacheStrategie
        self.RateLimitBereich = RateLimitBereich
        self.RateLimitGranularitaet = RateLimitGranularitaet
        self.RateLimitPolicy = RateLimitPolicy
        self.RateLimitRequest = RateLimitRequest
        self.RateLimitResultTyp = RateLimitResultTyp
        self.evaluate_rate_limit = evaluate_rate_limit
        self.get_default_cache_configs = get_default_cache_configs
        self.get_default_rate_limit_policies = get_default_rate_limit_policies

    def _make_request(self, zaehlung: int, domain: str = "agrar",
                      endpoint: str = "/api/v1/agrar/contracts") -> object:
        return self.RateLimitRequest(
            tenant_id="tenant-001",
            user_id="user-42",
            endpoint=endpoint,
            domain=domain,
            aktuelle_zaehlung=zaehlung,
        )

    def _make_policy(self, soft: int, hard: int, domain: str = "agrar",
                     pattern: str = "/api/v1/agrar/*") -> object:
        return self.RateLimitPolicy(
            policy_id="TEST-001",
            domain=domain,
            endpoint_pattern=pattern,
            bereich=self.RateLimitBereich.TENANT,
            granularitaet=self.RateLimitGranularitaet.MINUTE,
            soft_limit=soft,
            hard_limit=hard,
            beschreibung="Test-Policy",
        )

    def test_erlaubt_unter_soft_limit(self):
        policy = self._make_policy(soft=50, hard=100)
        req = self._make_request(zaehlung=10)
        result = self.evaluate_rate_limit(req, [policy])
        assert result.typ == self.RateLimitResultTyp.ERLAUBT
        assert result.empfohlener_http_status == 200

    def test_gedrosselt_zwischen_soft_und_hard(self):
        policy = self._make_policy(soft=50, hard=100)
        req = self._make_request(zaehlung=60)
        result = self.evaluate_rate_limit(req, [policy])
        assert result.typ == self.RateLimitResultTyp.GEDROSSELT
        assert result.empfohlener_http_status == 200

    def test_blockiert_am_hard_limit(self):
        policy = self._make_policy(soft=50, hard=100)
        req = self._make_request(zaehlung=100)
        result = self.evaluate_rate_limit(req, [policy])
        assert result.typ == self.RateLimitResultTyp.BLOCKIERT
        assert result.empfohlener_http_status == 429

    def test_blockiert_ueber_hard_limit(self):
        policy = self._make_policy(soft=50, hard=100)
        req = self._make_request(zaehlung=150)
        result = self.evaluate_rate_limit(req, [policy])
        assert result.typ == self.RateLimitResultTyp.BLOCKIERT
        assert result.retry_after_sekunden is not None

    def test_kein_policy_match_erlaubt(self):
        req = self._make_request(zaehlung=9999, domain="unbekannt", endpoint="/xyz")
        result = self.evaluate_rate_limit(req, [])
        assert result.typ == self.RateLimitResultTyp.ERLAUBT
        assert result.angewendete_policy_id is None

    def test_global_wildcard_matcht_alle_domains(self):
        policy = self._make_policy(soft=10, hard=20, domain="*", pattern="*")
        req = self._make_request(zaehlung=25, domain="finance", endpoint="/api/v1/finance/x")
        result = self.evaluate_rate_limit(req, [policy])
        assert result.typ == self.RateLimitResultTyp.BLOCKIERT

    def test_konservativste_policy_gewinnt(self):
        # Bei mehreren Matches gewinnt das niedrigste hard_limit
        p_streng = self._make_policy(soft=5, hard=10, pattern="*")
        p_lax = self._make_policy(soft=500, hard=1000, pattern="*")
        req = self._make_request(zaehlung=15)
        result = self.evaluate_rate_limit(req, [p_lax, p_streng])
        assert result.typ == self.RateLimitResultTyp.BLOCKIERT
        assert result.hard_limit == 10

    def test_rate_limit_result_as_dict(self):
        policy = self._make_policy(soft=50, hard=100)
        req = self._make_request(zaehlung=5)
        result = self.evaluate_rate_limit(req, [policy])
        d = result.as_dict()
        assert "typ" in d
        assert "empfohlener_http_status" in d
        assert "tenant_id" in d
        assert d["schema_version"] == 1

    def test_rate_limit_policy_as_dict(self):
        policy = self._make_policy(soft=50, hard=100)
        d = policy.as_dict()
        assert "policy_id" in d
        assert "soft_limit" in d
        assert "hard_limit" in d
        assert "erlaubte_operationen" not in d  # Kein Bulk-Op-Feld

    def test_default_policies_mindestens_fuenf(self):
        policies = self.get_default_rate_limit_policies()
        assert len(policies) >= 5

    def test_default_policies_globaler_catch_all(self):
        policies = self.get_default_rate_limit_policies()
        global_policies = [p for p in policies if p.domain == "*"]
        assert len(global_policies) >= 1

    def test_default_policies_zahlungslauf_kein_override(self):
        policies = self.get_default_rate_limit_policies()
        zl = next((p for p in policies if "payment" in p.endpoint_pattern.lower()
                   or "zahlungslauf" in p.beschreibung.lower()), None)
        if zl:
            assert zl.tenant_override_erlaubt is False

    def test_default_cache_configs_drei_tier(self):
        configs = self.get_default_cache_configs()
        assert len(configs) >= 3
        tenant_ids = {c.tenant_id for c in configs}
        assert "DEFAULT" in tenant_ids

    def test_cache_config_as_dict(self):
        configs = self.get_default_cache_configs()
        d = configs[0].as_dict()
        assert "tenant_id" in d
        assert "strategie" in d
        assert "ttl_sekunden" in d

    def test_cache_strategie_tenant_isoliert(self):
        configs = self.get_default_cache_configs()
        default = next(c for c in configs if c.tenant_id == "DEFAULT")
        assert default.strategie == self.CacheStrategie.TENANT_ISOLIERT

    def test_endpoint_pattern_wildcard_suffix(self):
        policy = self._make_policy(soft=10, hard=20,
                                   pattern="/api/v1/agrar/*")
        req = self._make_request(zaehlung=5,
                                 endpoint="/api/v1/agrar/contracts/123")
        result = self.evaluate_rate_limit(req, [policy])
        assert result.typ == self.RateLimitResultTyp.ERLAUBT

    def test_endpoint_pattern_no_match(self):
        policy = self._make_policy(soft=10, hard=20,
                                   pattern="/api/v1/agrar/*")
        req = self._make_request(zaehlung=5,
                                 domain="finance",
                                 endpoint="/api/v1/finance/invoices")
        result = self.evaluate_rate_limit(req, [policy])
        # Domain agrar, endpoint finance -> kein Match
        assert result.angewendete_policy_id is None


# ---------------------------------------------------------------------------
# AP4/AP5 — security_hardening_contracts.py
# ---------------------------------------------------------------------------

class TestSecurityHardeningCore:

    def setup_method(self):
        from app.core.security_hardening_contracts import (
            RBACPermission,
            RBACPermissionCheck,
            SecretKlassifikation,
            SecurityControlKategorie,
            SecurityControlStatus,
            SecurityFindingSchwere,
            evaluate_rbac_permission,
            evaluate_security_posture,
            get_default_secret_classifications,
            get_default_security_controls,
        )
        self.RBACPermission = RBACPermission
        self.RBACPermissionCheck = RBACPermissionCheck
        self.SecretKlassifikation = SecretKlassifikation
        self.SecurityControlKategorie = SecurityControlKategorie
        self.SecurityControlStatus = SecurityControlStatus
        self.SecurityFindingSchwere = SecurityFindingSchwere
        self.evaluate_rbac_permission = evaluate_rbac_permission
        self.evaluate_security_posture = evaluate_security_posture
        self.get_default_secret_classifications = get_default_secret_classifications
        self.get_default_security_controls = get_default_security_controls

    def _check(self, rolle: str, permission: str) -> object:
        return self.RBACPermissionCheck(
            user_id="u1",
            tenant_id="t1",
            rolle=rolle,
            permission=self.RBACPermission(permission),
        )

    def test_sachbearbeiter_darf_kontrakt_lesen(self):
        result = self.evaluate_rbac_permission(
            self._check("sachbearbeiter", "KONTRAKT_LESEN")
        )
        assert result.erlaubt is True

    def test_sachbearbeiter_darf_nicht_zahlungslauf_starten(self):
        result = self.evaluate_rbac_permission(
            self._check("sachbearbeiter", "ZAHLUNGSLAUF_STARTEN")
        )
        assert result.erlaubt is False

    def test_buchhaltung_darf_settlement_freigeben(self):
        result = self.evaluate_rbac_permission(
            self._check("buchhaltung", "SETTLEMENT_FREIGEBEN")
        )
        assert result.erlaubt is True

    def test_leiter_darf_kontrakt_stornieren(self):
        result = self.evaluate_rbac_permission(
            self._check("leiter", "KONTRAKT_STORNIEREN")
        )
        assert result.erlaubt is True

    def test_admin_hat_alle_permissions(self):
        for perm in self.RBACPermission:
            result = self.evaluate_rbac_permission(self._check("admin", perm.value))
            assert result.erlaubt is True, f"Admin sollte {perm.value} haben"

    def test_unbekannte_rolle_hat_keine_permissions(self):
        result = self.evaluate_rbac_permission(
            self._check("unbekannte_rolle", "KONTRAKT_LESEN")
        )
        assert result.erlaubt is False

    def test_rbac_result_as_dict(self):
        result = self.evaluate_rbac_permission(
            self._check("buchhaltung", "BUCHUNG_ERSTELLEN")
        )
        d = result.as_dict()
        assert "erlaubt" in d
        assert "rolle" in d
        assert "permission" in d
        assert d["schema_version"] == 1

    def test_rbac_result_begruendung_nicht_leer(self):
        result = self.evaluate_rbac_permission(
            self._check("sachbearbeiter", "ZAHLUNGSLAUF_STARTEN")
        )
        assert len(result.begruendung) > 0

    def test_default_security_controls_mindestens_zehn(self):
        controls = self.get_default_security_controls()
        assert len(controls) >= 10

    def test_security_controls_kategorien_abgedeckt(self):
        controls = self.get_default_security_controls()
        kategorien = {c.kategorie for c in controls}
        assert self.SecurityControlKategorie.AUTHENTIFIZIERUNG in kategorien
        assert self.SecurityControlKategorie.AUTORISIERUNG in kategorien
        assert self.SecurityControlKategorie.INJECTION_SCHUTZ in kategorien

    def test_security_control_as_dict(self):
        controls = self.get_default_security_controls()
        d = controls[0].as_dict()
        assert "control_id" in d
        assert "kategorie" in d
        assert "status" in d
        assert "owasp_referenz" in d

    def test_evaluate_posture_gut(self):
        controls = self.get_default_security_controls()
        posture = self.evaluate_security_posture(controls)
        assert posture.implementiert_count > 0
        assert posture.gesamtbewertung in {"GUT", "AUSREICHEND", "KRITISCH"}

    def test_evaluate_posture_kritisch_bei_kritischem_finding(self):
        from app.core.security_hardening_contracts import SecurityFinding
        controls = self.get_default_security_controls()
        finding = SecurityFinding(
            finding_id="F001",
            control_id="SC-AUTH-001",
            titel="Auth-Bypass moeglich",
            beschreibung="...",
            schwere=self.SecurityFindingSchwere.KRITISCH,
            status_offen=True,
        )
        posture = self.evaluate_security_posture(controls, [finding])
        assert posture.gesamtbewertung == "KRITISCH"
        assert posture.offene_kritische_findings == 1

    def test_evaluate_posture_geschlossene_findings_zaehlen_nicht(self):
        from app.core.security_hardening_contracts import SecurityFinding
        controls = self.get_default_security_controls()
        finding = SecurityFinding(
            finding_id="F002",
            control_id="SC-AUTH-001",
            titel="Alt behoben",
            beschreibung="...",
            schwere=self.SecurityFindingSchwere.KRITISCH,
            status_offen=False,  # bereits behoben
        )
        posture = self.evaluate_security_posture(controls, [finding])
        assert posture.offene_kritische_findings == 0

    def test_posture_as_dict(self):
        controls = self.get_default_security_controls()
        posture = self.evaluate_security_posture(controls)
        d = posture.as_dict()
        assert "implementiert_count" in d
        assert "gesamtbewertung" in d
        assert d["schema_version"] == 1

    def test_default_secret_classifications_mindestens_acht(self):
        secrets = self.get_default_secret_classifications()
        assert len(secrets) >= 8

    def test_password_streng_vertraulich(self):
        secrets = self.get_default_secret_classifications()
        pw = next(s for s in secrets if s.feld_muster == "password")
        assert pw.klassifikation == self.SecretKlassifikation.STRENG_VERTRAULICH
        assert pw.loggen_erlaubt is False

    def test_iban_vertraulich(self):
        secrets = self.get_default_secret_classifications()
        iban = next(s for s in secrets if s.feld_muster == "iban")
        assert iban.loggen_erlaubt is False

    def test_tenant_id_loggbar(self):
        secrets = self.get_default_secret_classifications()
        tid = next(s for s in secrets if s.feld_muster == "tenant_id")
        assert tid.loggen_erlaubt is True

    def test_secret_klassifikation_as_dict(self):
        secrets = self.get_default_secret_classifications()
        d = secrets[0].as_dict()
        assert "feld_muster" in d
        assert "klassifikation" in d
        assert "loggen_erlaubt" in d


# ---------------------------------------------------------------------------
# AP3 — GET /process/rate-limits + POST /process/rate-limits/check
# ---------------------------------------------------------------------------

class TestRateLimitsEndpoints:

    def test_get_rate_limits_alle(self, client):
        resp = client.get("/api/v1/process/rate-limits")
        assert resp.status_code == 200
        data = resp.json()
        assert "policy_count" in data
        assert data["policy_count"] >= 5
        assert "policies" in data
        assert "cache_configs" in data

    def test_get_rate_limits_domain_agrar(self, client):
        resp = client.get("/api/v1/process/rate-limits?domain=agrar")
        assert resp.status_code == 200
        data = resp.json()
        assert "policy_count" in data
        assert data["policy_count"] >= 1

    def test_get_rate_limits_unbekannte_domain(self, client):
        resp = client.get("/api/v1/process/rate-limits?domain=unbekannt_xyz")
        assert resp.status_code == 404

    def test_post_rate_limits_check_erlaubt(self, client):
        payload = {
            "tenant_id": "t1",
            "user_id": "u1",
            "endpoint": "/api/v1/agrar/contracts",
            "domain": "agrar",
            "aktuelle_zaehlung": 5,
        }
        resp = client.post("/api/v1/process/rate-limits/check", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert "typ" in data
        assert data["empfohlener_http_status"] in {200, 429}

    def test_post_rate_limits_check_blockiert(self, client):
        payload = {
            "tenant_id": "t1",
            "user_id": "u1",
            "endpoint": "/api/v1/agrar/contracts",
            "domain": "agrar",
            "aktuelle_zaehlung": 9999,  # Weit ueber jedem Limit
        }
        resp = client.post("/api/v1/process/rate-limits/check", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["typ"] == "BLOCKIERT"
        assert data["empfohlener_http_status"] == 429

    def test_post_rate_limits_check_fehlende_pflichtfelder(self, client):
        resp = client.post(
            "/api/v1/process/rate-limits/check",
            json={"tenant_id": "t1"},
        )
        assert resp.status_code == 422

    def test_post_rate_limits_check_ungueltige_zaehlung(self, client):
        payload = {
            "tenant_id": "t1",
            "user_id": "u1",
            "endpoint": "/api/v1/agrar/x",
            "domain": "agrar",
            "aktuelle_zaehlung": "nicht_eine_zahl",
        }
        resp = client.post("/api/v1/process/rate-limits/check", json=payload)
        assert resp.status_code == 422

    def test_post_rate_limits_check_result_schema_version(self, client):
        payload = {
            "tenant_id": "t1",
            "user_id": "u1",
            "endpoint": "/api/v1/finance/x",
            "domain": "finance",
            "aktuelle_zaehlung": 1,
        }
        resp = client.post("/api/v1/process/rate-limits/check", json=payload)
        assert resp.status_code == 200
        assert resp.json()["schema_version"] == 1


# ---------------------------------------------------------------------------
# AP6 — GET /process/security/controls + POST /process/security/rbac-check
# ---------------------------------------------------------------------------

class TestSecurityEndpoints:

    def test_get_security_controls_alle(self, client):
        resp = client.get("/api/v1/process/security/controls")
        assert resp.status_code == 200
        data = resp.json()
        assert "control_count" in data
        assert data["control_count"] >= 10
        assert "posture" in data
        assert "controls" in data
        assert "secret_classifications" in data

    def test_get_security_controls_posture_bewertung(self, client):
        resp = client.get("/api/v1/process/security/controls")
        assert resp.status_code == 200
        posture = resp.json()["posture"]
        assert posture["gesamtbewertung"] in {"GUT", "AUSREICHEND", "KRITISCH"}

    def test_get_security_controls_kategorie_filter(self, client):
        resp = client.get(
            "/api/v1/process/security/controls?kategorie=AUTHENTIFIZIERUNG"
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "control_count" in data
        assert data["control_count"] >= 1
        for c in data["controls"]:
            assert c["kategorie"] == "AUTHENTIFIZIERUNG"

    def test_get_security_controls_unbekannte_kategorie(self, client):
        resp = client.get(
            "/api/v1/process/security/controls?kategorie=UNBEKANNT_XYZ"
        )
        assert resp.status_code == 404

    def test_post_rbac_check_erlaubt(self, client):
        payload = {
            "user_id": "u1",
            "tenant_id": "t1",
            "rolle": "buchhaltung",
            "permission": "SETTLEMENT_FREIGEBEN",
        }
        resp = client.post("/api/v1/process/security/rbac-check", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["erlaubt"] is True
        assert data["schema_version"] == 1

    def test_post_rbac_check_verboten(self, client):
        payload = {
            "user_id": "u1",
            "tenant_id": "t1",
            "rolle": "sachbearbeiter",
            "permission": "ZAHLUNGSLAUF_STARTEN",
        }
        resp = client.post("/api/v1/process/security/rbac-check", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["erlaubt"] is False

    def test_post_rbac_check_admin_alles_erlaubt(self, client):
        payload = {
            "user_id": "admin1",
            "tenant_id": "t1",
            "rolle": "admin",
            "permission": "TENANT_KONFIGURIEREN",
        }
        resp = client.post("/api/v1/process/security/rbac-check", json=payload)
        assert resp.status_code == 200
        assert resp.json()["erlaubt"] is True

    def test_post_rbac_check_fehlende_pflichtfelder(self, client):
        resp = client.post(
            "/api/v1/process/security/rbac-check",
            json={"user_id": "u1"},
        )
        assert resp.status_code == 422

    def test_post_rbac_check_ungueltige_permission(self, client):
        payload = {
            "user_id": "u1",
            "tenant_id": "t1",
            "rolle": "admin",
            "permission": "SUPER_MACHT",
        }
        resp = client.post("/api/v1/process/security/rbac-check", json=payload)
        assert resp.status_code == 422

    def test_post_rbac_check_begruendung_enthalten(self, client):
        payload = {
            "user_id": "u1",
            "tenant_id": "t1",
            "rolle": "sachbearbeiter",
            "permission": "KONTRAKT_LESEN",
        }
        resp = client.post("/api/v1/process/security/rbac-check", json=payload)
        assert resp.status_code == 200
        assert len(resp.json()["begruendung"]) > 0
