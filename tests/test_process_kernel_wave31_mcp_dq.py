"""
Wave-31 Tests: MCP Tool Contracts (Gap 017) + Datenqualitaetsregeln (Gap 040)

47 Tests:
  AP1/AP2: MCPToolContract, MCPToolRegistry (20 Tests)
  AP4/AP5: DQRegel, DQRuleSet, validate_datensatz, get_default_dq_rulesets (20 Tests)
  AP3/AP6: API-Endpoints (7 Tests)
"""
from __future__ import annotations

import re

import pytest
from fastapi.testclient import TestClient
from starlette.routing import Route

from app.core.mcp_tool_contracts import (
    MCPParameterTyp,
    MCPToolContract,
    MCPToolKategorie,
    MCPToolParameter,
    get_process_kernel_mcp_tools,
)
from app.core.data_quality_rules import (
    DQRegelTyp,
    DQSeverity,
    DQRegel,
    DQRuleSet,
    DQViolation,
    DQValidationResult,
    validate_datensatz,
    get_default_dq_rulesets,
)


# ---------------------------------------------------------------------------
# AP1: MCPToolContract
# ---------------------------------------------------------------------------

class TestMCPToolContract:
    def test_validate_name_ok(self):
        t = MCPToolContract(
            tool_name="valeo_agrar_settlement_list",
            domain="agrar",
            operation="settlement_list",
            beschreibung="Listet Abrechnungen",
            kategorie=MCPToolKategorie.LESEN,
        )
        assert t.validate_name() is True

    def test_validate_name_wrong_prefix(self):
        t = MCPToolContract(
            tool_name="xvaleo_agrar_settlement_list",
            domain="agrar",
            operation="settlement_list",
            beschreibung="X",
            kategorie=MCPToolKategorie.LESEN,
        )
        assert t.validate_name() is False

    def test_validate_name_wrong_domain(self):
        t = MCPToolContract(
            tool_name="valeo_finance_settlement_list",
            domain="agrar",
            operation="settlement_list",
            beschreibung="X",
            kategorie=MCPToolKategorie.LESEN,
        )
        assert t.validate_name() is False

    def test_validate_name_too_few_parts(self):
        t = MCPToolContract(
            tool_name="valeo_agrar",
            domain="agrar",
            operation="",
            beschreibung="X",
            kategorie=MCPToolKategorie.LESEN,
        )
        assert t.validate_name() is False

    def test_as_mcp_tool_structure(self):
        param = MCPToolParameter(
            name="tenant_id",
            typ=MCPParameterTyp.STRING,
            beschreibung="Mandant",
            pflicht=True,
            beispiel="tenant_a",
        )
        t = MCPToolContract(
            tool_name="valeo_agrar_settlement_list",
            domain="agrar",
            operation="settlement_list",
            beschreibung="Listet Abrechnungen",
            kategorie=MCPToolKategorie.LESEN,
            parameter=[param],
        )
        mcp = t.as_mcp_tool()
        assert mcp["name"] == "valeo_agrar_settlement_list"
        assert "inputSchema" in mcp
        assert "tenant_id" in mcp["inputSchema"]["properties"]
        assert "tenant_id" in mcp["inputSchema"]["required"]

    def test_pflicht_parameter_filter(self):
        p1 = MCPToolParameter("a", MCPParameterTyp.STRING, "A", True)
        p2 = MCPToolParameter("b", MCPParameterTyp.STRING, "B", False)
        t = MCPToolContract(
            tool_name="valeo_agrar_test_op",
            domain="agrar",
            operation="test_op",
            beschreibung="X",
            kategorie=MCPToolKategorie.LESEN,
            parameter=[p1, p2],
        )
        assert len(t.pflicht_parameter) == 1
        assert len(t.optionale_parameter) == 1

    def test_requires_approval_default(self):
        t = MCPToolContract(
            tool_name="valeo_finance_payment_run_create",
            domain="finance",
            operation="payment_run_create",
            beschreibung="Erstellt Zahlungslauf",
            kategorie=MCPToolKategorie.SCHREIBEN,
        )
        assert t.requires_approval is False

    def test_as_mcp_tool_serializable(self):
        t = MCPToolContract(
            tool_name="valeo_compliance_policy_evaluate",
            domain="compliance",
            operation="policy_evaluate",
            beschreibung="Evaluiert Policy",
            kategorie=MCPToolKategorie.VALIDIEREN,
        )
        mcp = t.as_mcp_tool()
        assert isinstance(mcp, dict)
        assert mcp["name"].startswith("valeo_")


# ---------------------------------------------------------------------------
# AP2: MCPToolRegistry
# ---------------------------------------------------------------------------

class TestMCPToolRegistry:
    def setup_method(self):
        self.registry = get_process_kernel_mcp_tools()

    def test_minimum_20_tools(self):
        assert self.registry.as_dict()["tool_count"] >= 20

    def test_all_names_valid_convention(self):
        violations = self.registry.as_dict()["convention_violations"]
        assert violations == []

    def test_by_domain_agrar(self):
        tools = self.registry.by_domain("agrar")
        assert len(tools) >= 4
        assert all(t.domain == "agrar" for t in tools)

    def test_by_domain_finance(self):
        tools = self.registry.by_domain("finance")
        assert len(tools) >= 3

    def test_by_domain_workflow(self):
        tools = self.registry.by_domain("workflow")
        assert len(tools) >= 2

    def test_by_domain_compliance(self):
        tools = self.registry.by_domain("compliance")
        assert len(tools) >= 2

    def test_by_tool_name_found(self):
        t = self.registry.by_tool_name("valeo_agrar_settlement_list")
        assert t is not None
        assert t.tool_name == "valeo_agrar_settlement_list"

    def test_by_tool_name_not_found(self):
        t = self.registry.by_tool_name("valeo_unknown_nonexistent_tool")
        assert t is None

    def test_as_dict_domains_list(self):
        d = self.registry.as_dict()
        assert "domains" in d
        assert "agrar" in d["domains"]
        assert "finance" in d["domains"]

    def test_all_tools_have_beschreibung(self):
        d = self.registry.as_dict()
        for tool in d["tools"]:
            assert tool["beschreibung"]

    def test_all_tools_have_input_schema(self):
        # as_mcp_tools() returns MCP ToolDefinition format with inputSchema
        mcp_tools = self.registry.as_mcp_tools()
        for tool in mcp_tools:
            assert "inputSchema" in tool

    def test_validate_tool_name_ok(self):
        # validate_all_names returns empty list when all contracts are valid
        violations = self.registry.validate_all_names()
        assert violations == []

    def test_validate_tool_name_fail(self):
        # A contract with invalid name is detected by validate_name()
        t = MCPToolContract(
            tool_name="wrong_name",
            domain="agrar",
            operation="test",
            beschreibung="X",
            kategorie=MCPToolKategorie.LESEN,
        )
        assert t.validate_name() is False

    def test_all_tool_endpoints_map_to_real_fastapi_routes(self):
        from app.main import app

        def _normalize_path(path: str) -> str:
            normalized = re.sub(r"\{[^}]+\}", "{param}", path.rstrip("/"))
            return normalized or "/"

        route_index = {
            (method.upper(), _normalize_path(route.path))
            for route in app.routes
            if isinstance(route, Route)
            for method in route.methods or set()
            if method.upper() not in {"HEAD", "OPTIONS"}
        }

        missing = []
        for tool in self.registry.tools:
            assert tool.api_endpoint is not None
            method, path = tool.api_endpoint.split(" ", 1)
            if (method.upper(), _normalize_path(path)) not in route_index:
                missing.append(tool.api_endpoint)

        assert missing == []


# ---------------------------------------------------------------------------
# AP4: DQRegel, DQRuleSet, DQValidationResult
# ---------------------------------------------------------------------------

class TestDQRegel:
    def test_as_dict_keys(self):
        r = DQRegel("R-001", DQRegelTyp.PFLICHTFELD, "name", "Name Pflicht")
        d = r.as_dict()
        assert d["regel_id"] == "R-001"
        assert d["typ"] == "PFLICHTFELD"
        assert d["feld"] == "name"
        assert d["aktiv"] is True

    def test_format_regex_in_dict(self):
        r = DQRegel("R-002", DQRegelTyp.FORMAT_VERLETZUNG, "iban", "IBAN",
                    format_regex=r"DE\d{20}")
        d = r.as_dict()
        assert d["format_regex"] is not None

    def test_bereich_in_dict(self):
        r = DQRegel("R-003", DQRegelTyp.BEREICH_VERLETZUNG, "menge", "Menge",
                    min_wert=0.1, max_wert=100.0)
        d = r.as_dict()
        assert d["min_wert"] == 0.1
        assert d["max_wert"] == 100.0


class TestDQRuleSet:
    def test_as_dict_schema_version(self):
        rs = DQRuleSet("RS-001", "Test", "Test-Regelset")
        d = rs.as_dict()
        assert d["schema_version"] == 1
        assert d["entity_typ"] == "Test"

    def test_regeln_serialized(self):
        r = DQRegel("R-001", DQRegelTyp.PFLICHTFELD, "name", "Name Pflicht")
        rs = DQRuleSet("RS-001", "Test", "Test", regeln=[r])
        d = rs.as_dict()
        assert len(d["regeln"]) == 1


# ---------------------------------------------------------------------------
# AP5: validate_datensatz + get_default_dq_rulesets
# ---------------------------------------------------------------------------

class TestValidateDatensatz:
    def setup_method(self):
        self.rulesets = get_default_dq_rulesets()

    def test_valid_lieferant_passes(self):
        ds = {"lieferant_nr": "LF-001", "name": "Mustermann GmbH", "land": "DE"}
        result = validate_datensatz(self.rulesets["Lieferant"], ds)
        assert result.bestanden is True
        assert result.fehler_anzahl == 0

    def test_pflichtfeld_fehlt(self):
        ds = {"name": "Mustermann"}
        result = validate_datensatz(self.rulesets["Lieferant"], ds)
        assert result.bestanden is False
        typen = [v.typ for v in result.verletzungen]
        assert DQRegelTyp.PFLICHTFELD in typen

    def test_pflichtfeld_leer(self):
        ds = {"lieferant_nr": "", "name": "X", "land": "DE"}
        result = validate_datensatz(self.rulesets["Lieferant"], ds)
        assert result.bestanden is False

    def test_format_verletzung_iban_is_warnung(self):
        ds = {"lieferant_nr": "LF-001", "name": "X", "land": "DE", "iban": "INVALID"}
        result = validate_datensatz(self.rulesets["Lieferant"], ds)
        assert result.bestanden is True
        assert result.warnungs_anzahl >= 1
        assert any(v.typ == DQRegelTyp.FORMAT_VERLETZUNG for v in result.verletzungen)

    def test_bereich_verletzung_minimum(self):
        ds = {
            "kontrakt_nr": "K-001", "lieferant_nr": "LF-001", "ware": "Weizen",
            "menge_tonnen": -1.0, "preis_eur_pro_t": 200.0, "kontrakt_status": "AKTIV",
        }
        result = validate_datensatz(self.rulesets["Kontrakt"], ds)
        assert result.bestanden is False
        assert any(v.typ == DQRegelTyp.BEREICH_VERLETZUNG for v in result.verletzungen)

    def test_bereich_verletzung_maximum(self):
        ds = {
            "kontrakt_nr": "K-001", "lieferant_nr": "LF-001", "ware": "Weizen",
            "menge_tonnen": 999999.0, "preis_eur_pro_t": 200.0, "kontrakt_status": "AKTIV",
        }
        result = validate_datensatz(self.rulesets["Kontrakt"], ds)
        assert result.bestanden is False

    def test_referenz_fehlt(self):
        ds = {
            "kontrakt_nr": "K-001", "lieferant_nr": "LF-001", "ware": "Weizen",
            "menge_tonnen": 100.0, "preis_eur_pro_t": 200.0,
            "kontrakt_status": "UNGUELTIG_STATUS",
        }
        result = validate_datensatz(self.rulesets["Kontrakt"], ds)
        assert result.bestanden is False
        assert any(v.typ == DQRegelTyp.REFERENZ_FEHLT for v in result.verletzungen)

    def test_duplikat_verdacht(self):
        ds1 = {"lieferant_nr": "LF-001", "name": "A", "land": "DE"}
        ds2 = {"lieferant_nr": "LF-001", "name": "B", "land": "AT"}
        result = validate_datensatz(self.rulesets["Lieferant"], ds1, [ds1, ds2])
        assert any(v.typ == DQRegelTyp.DUPLIKAT_VERDACHT for v in result.verletzungen)

    def test_duplikat_kein_kontext(self):
        ds = {"lieferant_nr": "LF-001", "name": "A", "land": "DE"}
        result = validate_datensatz(self.rulesets["Lieferant"], ds, None)
        assert not any(v.typ == DQRegelTyp.DUPLIKAT_VERDACHT for v in result.verletzungen)

    def test_inaktive_regel_ignoriert(self):
        r = DQRegel("R-INV", DQRegelTyp.PFLICHTFELD, "testfeld", "X", aktiv=False)
        rs = DQRuleSet("RS-T", "Test", "Test", regeln=[r])
        result = validate_datensatz(rs, {})
        assert result.bestanden is True

    def test_default_rulesets_alle_vier(self):
        assert "Lieferant" in self.rulesets
        assert "Kontrakt" in self.rulesets
        assert "Wiegeschein" in self.rulesets
        assert "Artikel" in self.rulesets

    def test_wiegeschein_valid(self):
        ds = {
            "wiegeschein_nr": "WS-001", "kontrakt_nr": "K-001",
            "fahrzeug_kennzeichen": "AB-CD 1234",
            "brutto_gewicht_kg": 30000.0, "netto_gewicht_kg": 28000.0,
        }
        result = validate_datensatz(self.rulesets["Wiegeschein"], ds)
        assert result.bestanden is True

    def test_artikel_valid(self):
        ds = {"artikel_nr": "A-001", "bezeichnung": "Weizen", "einheit": "T",
              "mehrwertsteuersatz_pct": 7.0}
        result = validate_datensatz(self.rulesets["Artikel"], ds)
        assert result.bestanden is True

    def test_validation_result_as_dict(self):
        ds = {"artikel_nr": "A-001", "bezeichnung": "X", "einheit": "T"}
        result = validate_datensatz(self.rulesets["Artikel"], ds)
        d = result.as_dict()
        assert d["schema_version"] == 1
        assert "bestanden" in d
        assert "verletzungen" in d
        assert "fehler_anzahl" in d
        assert "warnungs_anzahl" in d

    def test_non_numeric_bereich(self):
        r = DQRegel("R-N", DQRegelTyp.BEREICH_VERLETZUNG, "menge", "Menge",
                    min_wert=0.0, max_wert=100.0)
        rs = DQRuleSet("RS-N", "Test", "Test", regeln=[r])
        result = validate_datensatz(rs, {"menge": "nicht_numerisch"})
        assert result.bestanden is False
        assert any(v.typ == DQRegelTyp.BEREICH_VERLETZUNG for v in result.verletzungen)

    def test_violation_as_dict(self):
        ds = {"name": "X"}
        result = validate_datensatz(self.rulesets["Lieferant"], ds)
        v = result.verletzungen[0]
        d = v.as_dict()
        assert "regel_id" in d
        assert "typ" in d
        assert "meldung" in d
        assert "severity" in d


# ---------------------------------------------------------------------------
# AP3/AP6: API-Endpoints
# ---------------------------------------------------------------------------

@pytest.fixture
def client():
    from app.main import app
    return TestClient(app)


class TestWave31Endpoints:
    def test_tool_registry_all(self, client):
        r = client.get("/api/v1/process/agent/tool-registry")
        assert r.status_code == 200
        body = r.json()
        assert body["tool_count"] >= 20
        assert len(body["tools"]) >= 20

    def test_tool_registry_domain_filter(self, client):
        r = client.get("/api/v1/process/agent/tool-registry?domain=agrar")
        assert r.status_code == 200
        body = r.json()
        assert body["domain_filter"] == "agrar"
        assert body["tool_count"] >= 4

    def test_tool_registry_unknown_domain(self, client):
        r = client.get("/api/v1/process/agent/tool-registry?domain=unknown_xyz")
        assert r.status_code == 200
        body = r.json()
        assert body["tool_count"] == 0

    def test_dq_rulesets(self, client):
        r = client.get("/api/v1/process/data-quality/rulesets")
        assert r.status_code == 200
        body = r.json()
        assert body["ruleset_count"] == 4
        assert "Lieferant" in body["rulesets"]

    def test_dq_validate_valid(self, client):
        payload = {
            "entity_typ": "Lieferant",
            "datensatz": {"lieferant_nr": "LF-001", "name": "Test GmbH", "land": "DE"},
        }
        r = client.post("/api/v1/process/data-quality/validate", json=payload)
        assert r.status_code == 200
        body = r.json()
        assert body["bestanden"] is True

    def test_dq_validate_missing_field(self, client):
        payload = {
            "entity_typ": "Lieferant",
            "datensatz": {"name": "Nur Name"},
        }
        r = client.post("/api/v1/process/data-quality/validate", json=payload)
        assert r.status_code == 200
        body = r.json()
        assert body["bestanden"] is False
        assert body["fehler_anzahl"] >= 1

    def test_dq_validate_unknown_entity(self, client):
        payload = {
            "entity_typ": "Unbekannt",
            "datensatz": {},
        }
        r = client.post("/api/v1/process/data-quality/validate", json=payload)
        assert r.status_code == 404

    # ------------------------------------------------------------------
    # Sicherheitstests
    # ------------------------------------------------------------------

    def test_tool_registry_no_api_endpoint_in_response(self, client):
        """api_endpoint darf im Public-Response nicht erscheinen (Informationsminimierung)."""
        r = client.get("/api/v1/process/agent/tool-registry")
        assert r.status_code == 200
        body = r.json()
        for tool in body["tools"]:
            assert "api_endpoint" not in tool

    def test_dq_rulesets_no_format_regex_in_response(self, client):
        """format_regex ist Implementierungsdetail und darf nicht im API-Response erscheinen."""
        r = client.get("/api/v1/process/data-quality/rulesets")
        assert r.status_code == 200
        body = r.json()
        for ruleset in body["rulesets"].values():
            for regel in ruleset["regeln"]:
                assert "format_regex" not in regel

    def test_dq_validate_payload_too_many_fields(self, client):
        """Mehr als 50 Felder im datensatz werden mit 422 abgelehnt (DoS-Schutz)."""
        payload = {
            "entity_typ": "Lieferant",
            "datensatz": {f"feld_{i}": f"wert_{i}" for i in range(51)},
        }
        r = client.post("/api/v1/process/data-quality/validate", json=payload)
        assert r.status_code == 422

    def test_dq_validate_feldwert_zu_lang(self, client):
        """Feldwert > 1000 Zeichen wird mit 422 abgelehnt (DoS-Schutz)."""
        payload = {
            "entity_typ": "Lieferant",
            "datensatz": {"lieferant_nr": "X" * 1001},
        }
        r = client.post("/api/v1/process/data-quality/validate", json=payload)
        assert r.status_code == 422

    def test_dq_format_redos_schutz(self):
        """Sehr langer Eingabewert loest keine ReDoS aus — wird sofort abgelehnt."""
        import time
        from app.core.data_quality_rules import DQRegel, DQRegelTyp, DQRuleSet, validate_datensatz

        r = DQRegel("WS-X", DQRegelTyp.FORMAT_VERLETZUNG, "fahrzeug_kennzeichen",
                    "Kennzeichen", format_regex=r"[A-ZÄÖÜ]{1,3}-[A-Z]{1,2}\s?\d{1,4}[EH]?")
        rs = DQRuleSet("RS-X", "Test", "Test", regeln=[r])
        langer_wert = "A" * 500 + "-" + "B" * 500 + " " + "1" * 500

        start = time.monotonic()
        result = validate_datensatz(rs, {"fahrzeug_kennzeichen": langer_wert})
        elapsed = time.monotonic() - start

        assert result.bestanden is False
        assert any(v.typ == DQRegelTyp.FORMAT_VERLETZUNG for v in result.verletzungen)
        # Muss in deutlich unter 1 Sekunde abgeschlossen sein
        assert elapsed < 1.0, f"Format-Check dauerte {elapsed:.3f}s — ReDoS-Schutz hat nicht gegriffen"

    def test_dq_bereich_nan_abgelehnt(self):
        """NaN als Feldwert wird als BEREICH_VERLETZUNG erkannt, nicht still ignoriert."""
        from app.core.data_quality_rules import DQRegel, DQRegelTyp, DQRuleSet, validate_datensatz

        r = DQRegel("K-NaN", DQRegelTyp.BEREICH_VERLETZUNG, "menge", "Menge",
                    min_wert=0.0, max_wert=100.0)
        rs = DQRuleSet("RS-NaN", "Test", "Test", regeln=[r])
        result = validate_datensatz(rs, {"menge": float("nan")})
        assert result.bestanden is False
        assert any(v.typ == DQRegelTyp.BEREICH_VERLETZUNG for v in result.verletzungen)

    def test_dq_bereich_inf_abgelehnt(self):
        """Inf als Feldwert wird als BEREICH_VERLETZUNG erkannt."""
        from app.core.data_quality_rules import DQRegel, DQRegelTyp, DQRuleSet, validate_datensatz

        r = DQRegel("K-Inf", DQRegelTyp.BEREICH_VERLETZUNG, "menge", "Menge",
                    min_wert=0.0, max_wert=100.0)
        rs = DQRuleSet("RS-Inf", "Test", "Test", regeln=[r])
        result = validate_datensatz(rs, {"menge": float("inf")})
        assert result.bestanden is False
