"""
Wave 35 — Tests: Inline-Validierung (Gap 026) + Error-Guidance (Gap 028)

AP1/AP2: inline_validation_contracts.py — Felddefinitionen, validate_inline_field(), Regeln
AP3:     process_kernel_api.py — GET /process/inline-validations, POST .../validate
AP4/AP5: error_guidance_contracts.py — Guidance-Regeln, evaluate_error_guidance()
AP6:     process_kernel_api.py — GET /process/error-guidance, POST .../evaluate
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
# AP1/AP2 — inline_validation_contracts.py
# ---------------------------------------------------------------------------

class TestInlineValidationCore:

    def setup_method(self):
        from app.core.inline_validation_contracts import (
            FeldTyp,
            InlineValidierungsFeld,
            InlineValidierungsRegel,
            ValidierungsRegelTyp,
            ValidierungsStatus,
            get_default_field_validations,
            get_field_by_id,
            validate_inline_field,
        )
        self.FeldTyp = FeldTyp
        self.InlineValidierungsFeld = InlineValidierungsFeld
        self.InlineValidierungsRegel = InlineValidierungsRegel
        self.ValidierungsRegelTyp = ValidierungsRegelTyp
        self.ValidierungsStatus = ValidierungsStatus
        self.get_default_field_validations = get_default_field_validations
        self.get_field_by_id = get_field_by_id
        self.validate_inline_field = validate_inline_field

    def _pflicht_feld(self) -> object:
        return self.InlineValidierungsFeld(
            feld_id="test-feld",
            feld_name="test",
            domain="agrar",
            typ=self.FeldTyp.TEXT,
            label="Test",
            hint="Test-Hint",
            regeln=[
                self.InlineValidierungsRegel(
                    "R1", self.ValidierungsRegelTyp.PFLICHTFELD,
                    "Pflichtfeld fehlt.", "Dieses Feld ist erforderlich.",
                ),
            ],
        )

    def test_pflichtfeld_leer_ergibt_fehler(self):
        feld = self._pflicht_feld()
        result = self.validate_inline_field(feld, "")
        assert result.status == self.ValidierungsStatus.FEHLER
        assert "Pflichtfeld" in result.fehlermeldung

    def test_pflichtfeld_none_ergibt_fehler(self):
        feld = self._pflicht_feld()
        result = self.validate_inline_field(feld, None)
        assert result.status == self.ValidierungsStatus.FEHLER

    def test_pflichtfeld_gefuellt_ergibt_gueltig(self):
        feld = self._pflicht_feld()
        result = self.validate_inline_field(feld, "beliebiger Wert")
        assert result.status == self.ValidierungsStatus.GUELTIG

    def test_format_regex_match(self):
        feld = self.InlineValidierungsFeld(
            feld_id="f1", feld_name="f", domain="agrar",
            typ=self.FeldTyp.TEXT, label="L", hint="H",
            regeln=[
                self.InlineValidierungsRegel(
                    "F1", self.ValidierungsRegelTyp.FORMAT,
                    "Falsches Format.", "Muss KT-JJJJ-NNNNN sein.",
                    format_regex=r"KT-\d{4}-\d{5}",
                ),
            ],
        )
        result = self.validate_inline_field(feld, "KT-2025-00123")
        assert result.status == self.ValidierungsStatus.GUELTIG

    def test_format_regex_kein_match(self):
        feld = self.InlineValidierungsFeld(
            feld_id="f1", feld_name="f", domain="agrar",
            typ=self.FeldTyp.TEXT, label="L", hint="H",
            regeln=[
                self.InlineValidierungsRegel(
                    "F1", self.ValidierungsRegelTyp.FORMAT,
                    "Falsches Format.", "Muss KT-JJJJ-NNNNN sein.",
                    format_regex=r"KT-\d{4}-\d{5}",
                ),
            ],
        )
        result = self.validate_inline_field(feld, "XY-2025-00123")
        assert result.status == self.ValidierungsStatus.FEHLER

    def test_format_leerer_wert_kein_format_fehler(self):
        # Leer -> Pflichtfeld-Regel zustaendig, nicht Format
        feld = self.InlineValidierungsFeld(
            feld_id="f1", feld_name="f", domain="agrar",
            typ=self.FeldTyp.TEXT, label="L", hint="H",
            regeln=[
                self.InlineValidierungsRegel(
                    "F1", self.ValidierungsRegelTyp.FORMAT,
                    "Falsches Format.", "x", format_regex=r"\d+",
                ),
            ],
        )
        result = self.validate_inline_field(feld, "")
        assert result.status == self.ValidierungsStatus.GUELTIG

    def test_bereich_innerhalb(self):
        feld = self.InlineValidierungsFeld(
            feld_id="f1", feld_name="f", domain="agrar",
            typ=self.FeldTyp.MENGE, label="L", hint="H",
            regeln=[
                self.InlineValidierungsRegel(
                    "B1", self.ValidierungsRegelTyp.BEREICH,
                    "Ausserhalb des Bereichs.", "Muss 0-100 sein.",
                    min_wert=0.0, max_wert=100.0,
                ),
            ],
        )
        result = self.validate_inline_field(feld, "50")
        assert result.status == self.ValidierungsStatus.GUELTIG

    def test_bereich_unterschritten(self):
        feld = self.InlineValidierungsFeld(
            feld_id="f1", feld_name="f", domain="agrar",
            typ=self.FeldTyp.MENGE, label="L", hint="H",
            regeln=[
                self.InlineValidierungsRegel(
                    "B1", self.ValidierungsRegelTyp.BEREICH,
                    "Zu wenig.", "Min 10.", min_wert=10.0,
                ),
            ],
        )
        result = self.validate_inline_field(feld, "5")
        assert result.status == self.ValidierungsStatus.FEHLER

    def test_bereich_nan_abgelehnt(self):
        feld = self.InlineValidierungsFeld(
            feld_id="f1", feld_name="f", domain="agrar",
            typ=self.FeldTyp.MENGE, label="L", hint="H",
            regeln=[
                self.InlineValidierungsRegel(
                    "B1", self.ValidierungsRegelTyp.BEREICH,
                    "Ungueltig.", ".", min_wert=0.0,
                ),
            ],
        )
        result = self.validate_inline_field(feld, "nan")
        assert result.status == self.ValidierungsStatus.FEHLER

    def test_warnung_statt_fehler(self):
        feld = self.InlineValidierungsFeld(
            feld_id="f1", feld_name="f", domain="agrar",
            typ=self.FeldTyp.ZAHL, label="L", hint="H",
            regeln=[
                self.InlineValidierungsRegel(
                    "W1", self.ValidierungsRegelTyp.BEREICH,
                    "Sehr hoch — pruefen.", "Warnung.",
                    max_wert=25.0, ist_warnung=True,
                ),
            ],
        )
        result = self.validate_inline_field(feld, "30")
        assert result.status == self.ValidierungsStatus.WARNUNG

    def test_laenge_zu_kurz(self):
        feld = self.InlineValidierungsFeld(
            feld_id="f1", feld_name="f", domain="compliance",
            typ=self.FeldTyp.TEXT, label="L", hint="H",
            regeln=[
                self.InlineValidierungsRegel(
                    "L1", self.ValidierungsRegelTyp.LAENGE,
                    "Zu kurz.", "Min 5 Zeichen.", min_laenge=5,
                ),
            ],
        )
        result = self.validate_inline_field(feld, "abc")
        assert result.status == self.ValidierungsStatus.FEHLER

    def test_laenge_korrekt(self):
        feld = self.InlineValidierungsFeld(
            feld_id="f1", feld_name="f", domain="compliance",
            typ=self.FeldTyp.TEXT, label="L", hint="H",
            regeln=[
                self.InlineValidierungsRegel(
                    "L1", self.ValidierungsRegelTyp.LAENGE,
                    "Zu kurz.", "Min 3 Zeichen.", min_laenge=3,
                ),
            ],
        )
        result = self.validate_inline_field(feld, "abcde")
        assert result.status == self.ValidierungsStatus.GUELTIG

    def test_redos_schutz_lange_eingabe(self):
        import time
        feld = self.InlineValidierungsFeld(
            feld_id="f1", feld_name="f", domain="agrar",
            typ=self.FeldTyp.TEXT, label="L", hint="H",
            regeln=[
                self.InlineValidierungsRegel(
                    "F1", self.ValidierungsRegelTyp.FORMAT,
                    "Falsches Format.", ".",
                    format_regex=r"[a-z]+",
                ),
            ],
        )
        # 600 Zeichen ueberschreiten _MAX_EINGABE_LEN=500 -> Fehler ohne Regex
        long_input = "a" * 600
        start = time.time()
        result = self.validate_inline_field(feld, long_input)
        elapsed = time.time() - start
        assert elapsed < 1.0
        assert result.status == self.ValidierungsStatus.FEHLER

    def test_validierungsergebnis_as_dict(self):
        feld = self._pflicht_feld()
        result = self.validate_inline_field(feld, "wert")
        d = result.as_dict()
        assert "feld_id" in d
        assert "status" in d
        assert d["schema_version"] == 1

    def test_get_default_field_validations_mindestens_sechs(self):
        felder = self.get_default_field_validations()
        assert len(felder) >= 6

    def test_default_felder_domains(self):
        felder = self.get_default_field_validations()
        domains = {f.domain for f in felder}
        assert "agrar" in domains
        assert "finance" in domains

    def test_get_field_by_id_gefunden(self):
        feld = self.get_field_by_id("ws-bruttogewicht")
        assert feld is not None
        assert feld.domain == "agrar"

    def test_get_field_by_id_nicht_gefunden(self):
        feld = self.get_field_by_id("ghost-feld-xyz")
        assert feld is None

    def test_bruttogewicht_zu_gross(self):
        feld = self.get_field_by_id("ws-bruttogewicht")
        result = self.validate_inline_field(feld, "200000")
        assert result.status == self.ValidierungsStatus.FEHLER

    def test_bruttogewicht_gueltig(self):
        feld = self.get_field_by_id("ws-bruttogewicht")
        result = self.validate_inline_field(feld, "25000")
        assert result.status == self.ValidierungsStatus.GUELTIG

    def test_feld_as_dict(self):
        felder = self.get_default_field_validations()
        d = felder[0].as_dict()
        assert "feld_id" in d
        assert "typ" in d
        assert "regeln" in d


# ---------------------------------------------------------------------------
# AP4/AP5 — error_guidance_contracts.py
# ---------------------------------------------------------------------------

class TestErrorGuidanceCore:

    def setup_method(self):
        from app.core.error_guidance_contracts import (
            FehlerKategorie,
            FehlerKontext,
            FehlerSchwere,
            LeitAktion,
            evaluate_error_guidance,
            get_default_error_guidance_rules,
        )
        self.FehlerKategorie = FehlerKategorie
        self.FehlerKontext = FehlerKontext
        self.FehlerSchwere = FehlerSchwere
        self.LeitAktion = LeitAktion
        self.evaluate_error_guidance = evaluate_error_guidance
        self.get_default_error_guidance_rules = get_default_error_guidance_rules

    def _eval(self, status: int, kategorie: str, kontext: str = "ALLGEMEIN"):
        regeln = self.get_default_error_guidance_rules()
        return self.evaluate_error_guidance(
            status,
            self.FehlerKategorie(kategorie),
            self.FehlerKontext(kontext),
            regeln,
        )

    def test_422_benutzer_fehler_eingabe_korrigieren(self):
        result = self._eval(422, "BENUTZER_FEHLER")
        assert result.leit_aktion == self.LeitAktion.EINGABE_KORRIGIEREN
        assert result.schwere == self.FehlerSchwere.BLOCKIEREND

    def test_403_berechtigung_anfragen(self):
        result = self._eval(403, "BERECHTIGUNGS_FEHLER")
        assert result.leit_aktion == self.LeitAktion.BERECHTIGUNG_ANFRAGEN

    def test_429_rate_limit_warten(self):
        result = self._eval(429, "LIMIT_FEHLER")
        assert result.leit_aktion == self.LeitAktion.WARTEN_UND_WIEDERHOLEN
        assert result.schwere == self.FehlerSchwere.WARNUNG

    def test_503_system_fehler_warten(self):
        result = self._eval(503, "SYSTEM_FEHLER")
        assert result.leit_aktion == self.LeitAktion.WARTEN_UND_WIEDERHOLEN

    def test_500_system_fehler_support(self):
        result = self._eval(500, "SYSTEM_FEHLER")
        assert result.leit_aktion == self.LeitAktion.SUPPORT_KONTAKTIEREN

    def test_kontext_spezifisch_wareneingang(self):
        result = self._eval(422, "BENUTZER_FEHLER", "WARENEINGANG")
        # Wareneingang-spezifische Regel bevorzugt
        assert result.kontext == self.FehlerKontext.WARENEINGANG

    def test_kontext_settlement_403(self):
        result = self._eval(403, "BERECHTIGUNGS_FEHLER", "SETTLEMENT")
        assert result.kontext == self.FehlerKontext.SETTLEMENT

    def test_kein_match_fallback_support(self):
        regeln = self.get_default_error_guidance_rules()
        result = self.evaluate_error_guidance(
            418,  # Teapot — keine Regel
            self.FehlerKategorie.SYSTEM_FEHLER,
            self.FehlerKontext.ALLGEMEIN,
            regeln,
        )
        assert result.leit_aktion == self.LeitAktion.SUPPORT_KONTAKTIEREN
        assert result.angewendete_regel_id is None

    def test_result_as_dict(self):
        result = self._eval(422, "BENUTZER_FEHLER")
        d = result.as_dict()
        assert "leit_aktion" in d
        assert "schwere" in d
        assert "titel" in d
        assert "handlungsanweisung" in d
        assert d["schema_version"] == 1

    def test_result_titel_nicht_leer(self):
        result = self._eval(403, "BERECHTIGUNGS_FEHLER")
        assert len(result.titel) > 0
        assert len(result.handlungsanweisung) > 0

    def test_default_regeln_mindestens_zehn(self):
        regeln = self.get_default_error_guidance_rules()
        assert len(regeln) >= 10

    def test_default_regeln_status_abdeckung(self):
        regeln = self.get_default_error_guidance_rules()
        status_codes = {r.http_status for r in regeln}
        assert 422 in status_codes
        assert 403 in status_codes
        assert 429 in status_codes
        assert 503 in status_codes
        assert 500 in status_codes

    def test_guidance_regel_as_dict(self):
        regeln = self.get_default_error_guidance_rules()
        d = regeln[0].as_dict()
        assert "regel_id" in d
        assert "leit_aktion" in d
        assert "handlungsanweisung" in d

    def test_fallback_422_ohne_regeln(self):
        result = self.evaluate_error_guidance(
            422,
            self.FehlerKategorie.BENUTZER_FEHLER,
            self.FehlerKontext.ALLGEMEIN,
            [],  # Keine Regeln
        )
        assert result.leit_aktion == self.LeitAktion.EINGABE_KORRIGIEREN

    def test_fallback_403_ohne_regeln(self):
        result = self.evaluate_error_guidance(
            403,
            self.FehlerKategorie.BERECHTIGUNGS_FEHLER,
            self.FehlerKontext.ALLGEMEIN,
            [],
        )
        assert result.leit_aktion == self.LeitAktion.BERECHTIGUNG_ANFRAGEN


# ---------------------------------------------------------------------------
# AP3 — GET /process/inline-validations + POST .../validate
# ---------------------------------------------------------------------------

class TestInlineValidationEndpoints:

    def test_get_inline_validations_alle(self, client):
        resp = client.get("/api/v1/process/inline-validations")
        assert resp.status_code == 200
        data = resp.json()
        assert "feld_count" in data
        assert data["feld_count"] >= 6
        assert "felder" in data

    def test_get_inline_validations_domain_agrar(self, client):
        resp = client.get("/api/v1/process/inline-validations?domain=agrar")
        assert resp.status_code == 200
        data = resp.json()
        assert data["feld_count"] >= 1
        for f in data["felder"]:
            assert f["domain"] == "agrar"

    def test_get_inline_validations_unbekannte_domain(self, client):
        resp = client.get("/api/v1/process/inline-validations?domain=unbekannt_xyz")
        assert resp.status_code == 404

    def test_post_inline_validate_gueltig(self, client):
        payload = {"feld_id": "ws-bruttogewicht", "wert": "25000"}
        resp = client.post("/api/v1/process/inline-validations/validate", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "GUELTIG"

    def test_post_inline_validate_fehler(self, client):
        payload = {"feld_id": "ws-bruttogewicht", "wert": ""}
        resp = client.post("/api/v1/process/inline-validations/validate", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "FEHLER"

    def test_post_inline_validate_fehlende_feld_id(self, client):
        resp = client.post(
            "/api/v1/process/inline-validations/validate",
            json={"wert": "123"},
        )
        assert resp.status_code == 422

    def test_post_inline_validate_unbekanntes_feld(self, client):
        resp = client.post(
            "/api/v1/process/inline-validations/validate",
            json={"feld_id": "ghost-feld-xyz", "wert": "123"},
        )
        assert resp.status_code == 404

    def test_post_inline_validate_schema_version(self, client):
        payload = {"feld_id": "re-iban", "wert": "DE89370400440532013000"}
        resp = client.post("/api/v1/process/inline-validations/validate", json=payload)
        assert resp.status_code == 200
        assert resp.json()["schema_version"] == 1

    def test_post_inline_validate_kontrakt_format_fehler(self, client):
        payload = {"feld_id": "ws-kontrakt-nr", "wert": "FALSCH-FORMAT"}
        resp = client.post("/api/v1/process/inline-validations/validate", json=payload)
        assert resp.status_code == 200
        assert resp.json()["status"] == "FEHLER"


# ---------------------------------------------------------------------------
# AP6 — GET /process/error-guidance + POST .../evaluate
# ---------------------------------------------------------------------------

class TestErrorGuidanceEndpoints:

    def test_get_error_guidance_alle(self, client):
        resp = client.get("/api/v1/process/error-guidance")
        assert resp.status_code == 200
        data = resp.json()
        assert "regel_count" in data
        assert data["regel_count"] >= 10
        assert "abgedeckte_status" in data

    def test_get_error_guidance_filter_422(self, client):
        resp = client.get("/api/v1/process/error-guidance?http_status=422")
        assert resp.status_code == 200
        data = resp.json()
        assert data["http_status_filter"] == 422
        assert data["regel_count"] >= 1

    def test_get_error_guidance_unbekannter_status(self, client):
        resp = client.get("/api/v1/process/error-guidance?http_status=999")
        assert resp.status_code == 404

    def test_post_error_guidance_evaluate_422(self, client):
        payload = {
            "http_status": 422,
            "fehler_kategorie": "BENUTZER_FEHLER",
            "kontext": "WARENEINGANG",
        }
        resp = client.post("/api/v1/process/error-guidance/evaluate", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert "leit_aktion" in data
        assert "handlungsanweisung" in data
        assert data["schema_version"] == 1

    def test_post_error_guidance_evaluate_403(self, client):
        payload = {
            "http_status": 403,
            "fehler_kategorie": "BERECHTIGUNGS_FEHLER",
            "kontext": "SETTLEMENT",
        }
        resp = client.post("/api/v1/process/error-guidance/evaluate", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["leit_aktion"] == "BERECHTIGUNG_ANFRAGEN"

    def test_post_error_guidance_fehlende_pflichtfelder(self, client):
        resp = client.post(
            "/api/v1/process/error-guidance/evaluate",
            json={"http_status": 422},
        )
        assert resp.status_code == 422

    def test_post_error_guidance_unbekannte_kategorie(self, client):
        payload = {
            "http_status": 422,
            "fehler_kategorie": "UNBEKANNT_XYZ",
            "kontext": "ALLGEMEIN",
        }
        resp = client.post("/api/v1/process/error-guidance/evaluate", json=payload)
        assert resp.status_code == 422

    def test_post_error_guidance_unbekannter_kontext_fallback(self, client):
        payload = {
            "http_status": 503,
            "fehler_kategorie": "SYSTEM_FEHLER",
            "kontext": "UNBEKANNTER_KONTEXT",  # -> ALLGEMEIN Fallback
        }
        resp = client.post("/api/v1/process/error-guidance/evaluate", json=payload)
        assert resp.status_code == 200

    def test_post_error_guidance_429_rate_limit(self, client):
        payload = {
            "http_status": 429,
            "fehler_kategorie": "LIMIT_FEHLER",
            "kontext": "ALLGEMEIN",
        }
        resp = client.post("/api/v1/process/error-guidance/evaluate", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["leit_aktion"] == "WARTEN_UND_WIEDERHOLEN"
