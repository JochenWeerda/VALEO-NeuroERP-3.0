"""
Wave-37 Contract Tests: DMS/OCR-Contracts und Agent-Integration-Contracts
Gap 045 (dms_ocr_contracts) + Gap 048 (agent_integration_contracts)

60 Tests total:
  TestConfidenceStufe              4
  TestExtrahiertesFelder           5
  TestOCRExtraktionsErgebnis       6
  TestBewertungOCRErgebnis         5
  TestKlassifiziereDokument        7
  TestDmsDefaultRegeln             3
  TestAgentToolEnums               3
  TestAgentToolDefaults            5
  TestMatchCapabilities            7
  TestDmsErkennungsregelnEndpoint  4
  TestDmsClassifyEndpoint          4
  TestAgentToolsEndpoint           4
  TestAgentToolsMatchEndpoint      3
"""
from __future__ import annotations

from datetime import datetime

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints import process_kernel_api
from app.core.dms_ocr_contracts import (
    BelegErkennungsRegel,
    BelegFeldTyp,
    ConfidenceStufe,
    DokumentKlassifikationsErgebnis,
    DokumentTyp,
    ExtrahiertesFelder,
    ExtraktionsStatus,
    OCREngine,
    OCRExtraktionsErgebnis,
    bewerte_ocr_ergebnis,
    confidence_stufe,
    get_default_erkennungsregeln,
    klassifiziere_dokument,
)
from app.core.agent_integration_contracts import (
    AgentAutorisierungsStufe,
    AgentKategorie,
    AgentTool,
    AgentUseCase,
    AgentUseCaseStatus,
    CapabilityMatchResultTyp,
    ToolParameter,
    ToolParameterTyp,
    get_default_agent_tools,
    get_default_agent_use_cases,
    match_capabilities,
)


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _make_feld(confidence: float, feld_id: str = "F1") -> ExtrahiertesFelder:
    return ExtrahiertesFelder(
        feld_id=feld_id,
        feld_typ=BelegFeldTyp.BETRAG,
        wert="100.00",
        confidence=confidence,
    )


def _make_ergebnis(felder: list[ExtrahiertesFelder]) -> OCRExtraktionsErgebnis:
    return OCRExtraktionsErgebnis(
        dokument_id="DOC-TEST",
        dokument_typ=DokumentTyp.EINGANGSRECHNUNG,
        engine=OCREngine.TESSERACT,
        status=ExtraktionsStatus.ERFOLGREICH,
        felder=felder,
        extrahiert_am=datetime(2026, 3, 15, 10, 0, 0),
    )


@pytest.fixture
def client() -> TestClient:
    app = FastAPI()
    app.include_router(process_kernel_api.router)
    return TestClient(app)


# ===========================================================================
# TestConfidenceStufe  (4 tests)
# ===========================================================================

class TestConfidenceStufe:

    def test_hoch_at_boundary(self):
        assert confidence_stufe(0.90) == ConfidenceStufe.HOCH

    def test_mittel_at_boundary(self):
        assert confidence_stufe(0.70) == ConfidenceStufe.MITTEL

    def test_niedrig_at_boundary(self):
        assert confidence_stufe(0.50) == ConfidenceStufe.NIEDRIG

    def test_unzuverlaessig_below_50(self):
        assert confidence_stufe(0.49) == ConfidenceStufe.UNZUVERLAESSIG

# ===========================================================================
# TestExtrahiertesFelder  (5 tests)
# ===========================================================================

class TestExtrahiertesFelder:

    def test_confidence_stufe_property_hoch(self):
        f = _make_feld(0.95)
        assert f.confidence_stufe == ConfidenceStufe.HOCH

    def test_confidence_stufe_property_mittel(self):
        f = _make_feld(0.75)
        assert f.confidence_stufe == ConfidenceStufe.MITTEL

    def test_ist_zuverlaessig_true_at_threshold(self):
        f = _make_feld(0.70)
        assert f.ist_zuverlaessig is True

    def test_ist_zuverlaessig_false_below_threshold(self):
        f = _make_feld(0.69)
        assert f.ist_zuverlaessig is False

    def test_as_dict_contains_all_keys(self):
        f = _make_feld(0.85)
        d = f.as_dict()
        assert "feld_id" in d
        assert "feld_typ" in d
        assert "confidence" in d
        assert "confidence_stufe" in d
        assert "ist_zuverlaessig" in d
        assert "seite" in d
        assert "bounding_box" in d


# ===========================================================================
# TestOCRExtraktionsErgebnis  (6 tests)
# ===========================================================================

class TestOCRExtraktionsErgebnis:

    def test_post_init_computes_avg_confidence(self):
        felder = [_make_feld(0.8, "F1"), _make_feld(0.6, "F2")]
        ergebnis = _make_ergebnis(felder)
        assert abs(ergebnis.durchschnittliche_confidence - 0.7) < 1e-9

    def test_post_init_does_not_override_explicit_confidence(self):
        felder = [_make_feld(0.8, "F1"), _make_feld(0.6, "F2")]
        ergebnis = OCRExtraktionsErgebnis(
            dokument_id="DOC-X",
            dokument_typ=DokumentTyp.LIEFERSCHEIN,
            engine=OCREngine.INTERN,
            status=ExtraktionsStatus.TEILWEISE,
            felder=felder,
            extrahiert_am=datetime.now(),
            durchschnittliche_confidence=0.99,
        )
        assert ergebnis.durchschnittliche_confidence == 0.99

    def test_zuverlaessige_felder_filters_correctly(self):
        felder = [_make_feld(0.95, "F1"), _make_feld(0.50, "F2"), _make_feld(0.70, "F3")]
        ergebnis = _make_ergebnis(felder)
        assert len(ergebnis.zuverlaessige_felder) == 2

    def test_vollstaendigkeits_grad_all_reliable(self):
        felder = [_make_feld(0.90, "F1"), _make_feld(0.80, "F2")]
        ergebnis = _make_ergebnis(felder)
        assert ergebnis.vollstaendigkeits_grad == 1.0

    def test_vollstaendigkeits_grad_none_reliable(self):
        felder = [_make_feld(0.40, "F1"), _make_feld(0.30, "F2")]
        ergebnis = _make_ergebnis(felder)
        assert ergebnis.vollstaendigkeits_grad == 0.0

    def test_as_dict_structure(self):
        felder = [_make_feld(0.90, "F1")]
        ergebnis = _make_ergebnis(felder)
        d = ergebnis.as_dict()
        assert d["dokument_id"] == "DOC-TEST"
        assert "felder" in d
        assert "vollstaendigkeits_grad" in d
        assert "extrahiert_am" in d


# ===========================================================================
# TestBewertungOCRErgebnis  (5 tests)
# ===========================================================================

class TestBewertungOCRErgebnis:

    def test_erfolgreich_at_80_percent(self):
        felder = [_make_feld(0.90, f"F{i}") for i in range(8)] + \
                 [_make_feld(0.40, f"G{i}") for i in range(2)]
        ergebnis = _make_ergebnis(felder)
        assert bewerte_ocr_ergebnis(ergebnis) == ExtraktionsStatus.ERFOLGREICH

    def test_teilweise_at_50_percent(self):
        felder = [_make_feld(0.90, f"F{i}") for i in range(5)] + \
                 [_make_feld(0.40, f"G{i}") for i in range(5)]
        ergebnis = _make_ergebnis(felder)
        assert bewerte_ocr_ergebnis(ergebnis) == ExtraktionsStatus.TEILWEISE

    def test_manuell_erforderlich_at_20_percent(self):
        felder = [_make_feld(0.90, f"F{i}") for i in range(2)] + \
                 [_make_feld(0.40, f"G{i}") for i in range(8)]
        ergebnis = _make_ergebnis(felder)
        assert bewerte_ocr_ergebnis(ergebnis) == ExtraktionsStatus.MANUELL_ERFORDERLICH

    def test_fehlgeschlagen_below_20_percent(self):
        felder = [_make_feld(0.90, "F1")] + \
                 [_make_feld(0.40, f"G{i}") for i in range(9)]
        ergebnis = _make_ergebnis(felder)
        assert bewerte_ocr_ergebnis(ergebnis) == ExtraktionsStatus.FEHLGESCHLAGEN

    def test_edge_case_empty_felder_returns_fehlgeschlagen(self):
        ergebnis = _make_ergebnis([])
        assert bewerte_ocr_ergebnis(ergebnis) == ExtraktionsStatus.FEHLGESCHLAGEN


# ===========================================================================
# TestKlassifiziereDokument  (7 tests)
# ===========================================================================

class TestKlassifiziereDokument:

    def test_eingangsrechnung_recognized(self):
        volltext = "Rechnung Rechnungsnummer MwSt Zahlungsziel"
        result = klassifiziere_dokument("DOC-001", volltext)
        assert result.erkannter_typ == DokumentTyp.EINGANGSRECHNUNG

    def test_wiegeschein_recognized(self):
        volltext = "Wiegeschein Waage Bruttogewicht Nettogewicht Tara"
        result = klassifiziere_dokument("DOC-002", volltext)
        assert result.erkannter_typ == DokumentTyp.WIEGESCHEIN

    def test_empty_volltext_returns_zero_confidence_and_manuell_pruefen(self):
        # Empty text matches 0 keywords in every rule → confidence 0.0 everywhere.
        # First rule wins the tie; manuell_pruefen must be True.
        result = klassifiziere_dokument("DOC-003", "")
        assert result.confidence == 0.0
        assert result.manuell_pruefen is True

    def test_manuell_pruefen_true_when_low_confidence(self):
        volltext = "irgendetwas unbekanntes xyz"
        result = klassifiziere_dokument("DOC-004", volltext)
        assert result.manuell_pruefen is True

    def test_manuell_pruefen_false_for_high_confidence(self):
        volltext = "rechnung rechnungsnummer mwst steuer zahlungsziel invoice"
        result = klassifiziere_dokument("DOC-005", volltext)
        assert result.confidence >= 0.30
        assert result.manuell_pruefen is False

    def test_case_insensitive_matching(self):
        volltext = "RECHNUNG RECHNUNGSNUMMER MWSt"
        result = klassifiziere_dokument("DOC-006", volltext)
        assert result.erkannter_typ == DokumentTyp.EINGANGSRECHNUNG

    def test_custom_regeln_override_defaults(self):
        custom_regel = BelegErkennungsRegel(
            regel_id="CUST-001",
            dokument_typ=DokumentTyp.ZOLLERKLAERUNG,
            schlagwoerter=["zoll", "export", "hs-code"],
            pflichtfelder=[BelegFeldTyp.BELEGNUMMER],
        )
        volltext = "Zoll Export HS-Code Warenwert"
        result = klassifiziere_dokument("DOC-007", volltext, regeln=[custom_regel])
        assert result.erkannter_typ == DokumentTyp.ZOLLERKLAERUNG


# ===========================================================================
# TestDmsDefaultRegeln  (3 tests)
# ===========================================================================

class TestDmsDefaultRegeln:

    def test_returns_7_regeln(self):
        regeln = get_default_erkennungsregeln()
        assert len(regeln) == 7

    def test_all_regeln_have_schlagwoerter(self):
        regeln = get_default_erkennungsregeln()
        for r in regeln:
            assert len(r.schlagwoerter) > 0

    def test_eingangsrechnung_regel_exists(self):
        regeln = get_default_erkennungsregeln()
        typen = [r.dokument_typ for r in regeln]
        assert DokumentTyp.EINGANGSRECHNUNG in typen


# ===========================================================================
# TestAgentToolEnums  (3 tests)
# ===========================================================================

class TestAgentToolEnums:

    def test_agent_kategorie_values(self):
        values = {e.value for e in AgentKategorie}
        assert "RECHERCHE" in values
        assert "TRANSAKTION" in values
        assert "COMPLIANCE" in values

    def test_capability_match_result_typ_values(self):
        values = {e.value for e in CapabilityMatchResultTyp}
        assert "VOLLSTAENDIGER_MATCH" in values
        assert "TEILWEISER_MATCH" in values
        assert "KEIN_MATCH" in values

    def test_agent_use_case_status_values(self):
        values = {e.value for e in AgentUseCaseStatus}
        assert "AKTIV" in values
        assert "BETA" in values
        assert "GEPLANT" in values
        assert "DEAKTIVIERT" in values


# ===========================================================================
# TestAgentToolDefaults  (5 tests)
# ===========================================================================

class TestAgentToolDefaults:

    def test_returns_10_tools(self):
        tools = get_default_agent_tools()
        assert len(tools) == 10

    def test_returns_10_use_cases(self):
        use_cases = get_default_agent_use_cases()
        assert len(use_cases) == 10

    def test_all_tools_have_capabilities(self):
        tools = get_default_agent_tools()
        for t in tools:
            assert len(t.capabilities) > 0, f"Tool {t.tool_id} has no capabilities"

    def test_tool_as_dict_structure(self):
        tool = get_default_agent_tools()[0]
        d = tool.as_dict()
        expected_keys = {
            "tool_id", "name", "kategorie", "autorisierung",
            "beschreibung", "endpunkt", "methode",
            "parameter", "capabilities", "rate_limit_pro_minute",
            "idempotent", "schema_version",
        }
        assert expected_keys.issubset(d.keys())

    def test_use_case_as_dict_structure(self):
        uc = get_default_agent_use_cases()[0]
        d = uc.as_dict()
        expected_keys = {
            "use_case_id", "name", "beschreibung",
            "beteiligte_tools", "benoetigte_capabilities",
            "status", "beispiel_prompt", "erwartetes_ergebnis",
        }
        assert expected_keys.issubset(d.keys())


# ===========================================================================
# TestMatchCapabilities  (7 tests)
# ===========================================================================

class TestMatchCapabilities:

    def test_vollstaendiger_match_single_known_capability(self):
        result = match_capabilities(["kontrakt_lesen"])
        assert result.match_typ == CapabilityMatchResultTyp.VOLLSTAENDIGER_MATCH
        assert result.match_score == 1.0
        assert len(result.gefundene_tools) >= 1

    def test_teilweiser_match_partial_capabilities(self):
        # "kontrakt_lesen" exists, "unbekannte_cap_xyz" does not
        result = match_capabilities(["kontrakt_lesen", "unbekannte_cap_xyz"])
        assert result.match_typ == CapabilityMatchResultTyp.TEILWEISER_MATCH
        assert 0.0 < result.match_score < 1.0

    def test_kein_match_unknown_capability(self):
        result = match_capabilities(["cap_die_es_nicht_gibt_99999"])
        assert result.match_typ == CapabilityMatchResultTyp.KEIN_MATCH
        assert result.match_score == 0.0

    def test_case_insensitive_capability_matching(self):
        result = match_capabilities(["KONTRAKT_LESEN"])
        assert result.match_typ == CapabilityMatchResultTyp.VOLLSTAENDIGER_MATCH

    def test_fehlende_capabilities_listed(self):
        result = match_capabilities(["kontrakt_lesen", "cap_fehlt_abc"])
        assert "cap_fehlt_abc" in result.fehlende_capabilities

    def test_gefundene_tool_ids_in_as_dict(self):
        result = match_capabilities(["kontrakt_lesen"])
        d = result.as_dict()
        assert "gefundene_tool_ids" in d
        assert "AT-001" in d["gefundene_tool_ids"]

    def test_custom_tools_override_defaults(self):
        custom_tool = AgentTool(
            tool_id="CT-001",
            name="custom_tool",
            kategorie=AgentKategorie.ANALYSE,
            autorisierung=AgentAutorisierungsStufe.OEFFENTLICH,
            beschreibung="Custom test tool",
            endpunkt="/test",
            methode="GET",
            capabilities=["super_special_cap"],
        )
        result = match_capabilities(["super_special_cap"], tools=[custom_tool])
        assert result.match_typ == CapabilityMatchResultTyp.VOLLSTAENDIGER_MATCH
        assert result.gefundene_tools[0].tool_id == "CT-001"


# ===========================================================================
# TestDmsErkennungsregelnEndpoint  (4 tests)
# ===========================================================================

class TestDmsErkennungsregelnEndpoint:

    def test_get_erkennungsregeln_200_and_count(self, client):
        response = client.get("/process/dms/erkennungsregeln")
        assert response.status_code == 200
        data = response.json()
        assert data["regel_count"] >= 7

    def test_get_erkennungsregeln_filter_by_typ(self, client):
        response = client.get("/process/dms/erkennungsregeln?dokument_typ=EINGANGSRECHNUNG")
        assert response.status_code == 200
        data = response.json()
        for r in data["regeln"]:
            assert r["dokument_typ"] == "EINGANGSRECHNUNG"

    def test_get_erkennungsregeln_invalid_typ_422(self, client):
        response = client.get("/process/dms/erkennungsregeln?dokument_typ=UNGUELTIG")
        assert response.status_code == 422

    def test_get_erkennungsregeln_schema_version_present(self, client):
        response = client.get("/process/dms/erkennungsregeln")
        assert response.status_code == 200
        assert "schema_version" in response.json()


# ===========================================================================
# TestDmsClassifyEndpoint  (4 tests)
# ===========================================================================

class TestDmsClassifyEndpoint:

    def test_classify_eingangsrechnung(self, client):
        body = {
            "dokument_id": "DOC-001",
            "volltext": "Rechnung Rechnungsnummer MwSt Zahlungsziel",
        }
        response = client.post("/process/dms/classify", json=body)
        assert response.status_code == 200
        data = response.json()
        assert data["erkannter_typ"] == "EINGANGSRECHNUNG"

    def test_classify_missing_volltext_422(self, client):
        body = {"dokument_id": "DOC-002"}
        response = client.post("/process/dms/classify", json=body)
        assert response.status_code == 422

    def test_classify_missing_dokument_id_422(self, client):
        body = {"volltext": "Rechnung Rechnungsnummer"}
        response = client.post("/process/dms/classify", json=body)
        assert response.status_code == 422

    def test_classify_returns_confidence_and_manuell_pruefen(self, client):
        body = {
            "dokument_id": "DOC-003",
            "volltext": "Wiegeschein Waage Bruttogewicht Nettogewicht",
        }
        response = client.post("/process/dms/classify", json=body)
        assert response.status_code == 200
        data = response.json()
        assert "confidence" in data
        assert "manuell_pruefen" in data


# ===========================================================================
# TestAgentToolsEndpoint  (4 tests)
# ===========================================================================

class TestAgentToolsEndpoint:

    def test_get_agent_tools_returns_10_tools_and_10_use_cases(self, client):
        response = client.get("/process/agent-tools")
        assert response.status_code == 200
        data = response.json()
        assert data["tool_count"] == 10
        assert data["use_case_count"] == 10

    def test_get_agent_tools_filter_by_kategorie(self, client):
        response = client.get("/process/agent-tools?kategorie=RECHERCHE")
        assert response.status_code == 200
        data = response.json()
        for t in data["tools"]:
            assert t["kategorie"] == "RECHERCHE"

    def test_get_agent_tools_invalid_kategorie_422(self, client):
        response = client.get("/process/agent-tools?kategorie=UNGUELTIG")
        assert response.status_code == 422

    def test_get_agent_tools_filter_by_autorisierung(self, client):
        response = client.get("/process/agent-tools?autorisierung=BERECHTIGT")
        assert response.status_code == 200
        data = response.json()
        for t in data["tools"]:
            assert t["autorisierung"] == "BERECHTIGT"


# ===========================================================================
# TestAgentToolsMatchEndpoint  (3 tests)
# ===========================================================================

class TestAgentToolsMatchEndpoint:

    def test_match_known_capability_returns_match(self, client):
        body = {"capabilities": ["kontrakt_lesen"]}
        response = client.post("/process/agent-tools/match", json=body)
        assert response.status_code == 200
        data = response.json()
        assert data["match_typ"] == "VOLLSTAENDIGER_MATCH"
        assert len(data["gefundene_tools"]) >= 1

    def test_match_empty_capabilities_422(self, client):
        body = {"capabilities": []}
        response = client.post("/process/agent-tools/match", json=body)
        assert response.status_code == 422

    def test_match_unknown_capability_returns_kein_match(self, client):
        body = {"capabilities": ["capability_xyz_does_not_exist_9999"]}
        response = client.post("/process/agent-tools/match", json=body)
        assert response.status_code == 200
        data = response.json()
        assert data["match_typ"] == "KEIN_MATCH"
        assert data["match_score"] == 0.0
