"""
Wave 82 — Controlling 500er eliminieren (Gap 032)

Tests für safe_kpi_response(), safe_timeseries_response(),
KpiSafeValue.from_raw(), evaluate_controlling_safety().

Gap 032: Error Rate <0.5% bei /controlling/kpis und /controlling/timeseries
"""
from __future__ import annotations

import pytest

from app.core.controlling_safe_read_contracts import (
    AmpelStatus,
    ControllingReadSafetyResult,
    KpiSafeValue,
    KpiVerfuegbarkeit,
    TimeseriesSafeEntry,
    TimeseriesSafeResult,
    evaluate_controlling_safety,
    safe_kpi_list_response,
    safe_kpi_response,
    safe_timeseries_response,
)


# ---------------------------------------------------------------------------
# TestKpiSafeValueFromRaw
# ---------------------------------------------------------------------------

class TestKpiSafeValueFromRaw:
    """KpiSafeValue.from_raw() — sichere Konvertierung ohne Exception."""

    def test_vollstaendiger_datensatz(self):
        raw = {"kpi_code": "UMSATZ", "name": "Umsatz", "current_value": "245000",
               "target_value": "250000", "unit": "EUR"}
        kpi = KpiSafeValue.from_raw(raw)
        assert kpi.kpi_code == "UMSATZ"
        assert kpi.wert == 245000.0
        assert kpi.zielwert == 250000.0
        assert kpi.einheit == "EUR"
        assert kpi.ist_verfuegbar is True

    def test_none_input_ergibt_leer(self):
        kpi = KpiSafeValue.from_raw(None, "TEST")
        assert kpi.kpi_code == "TEST"
        assert kpi.wert is None
        assert kpi.verfuegbarkeit == KpiVerfuegbarkeit.LEER

    def test_leeres_dict_ergibt_leer(self):
        kpi = KpiSafeValue.from_raw({})
        assert kpi.wert is None
        assert kpi.verfuegbarkeit == KpiVerfuegbarkeit.LEER

    def test_wert_als_string_mit_komma(self):
        raw = {"kpi_code": "X", "current_value": "1234.5"}
        kpi = KpiSafeValue.from_raw(raw)
        assert kpi.wert == 1234.5

    def test_wert_nicht_parsebar_ergibt_none(self):
        raw = {"kpi_code": "X", "current_value": "n/a"}
        kpi = KpiSafeValue.from_raw(raw)
        assert kpi.wert is None

    def test_ampel_berechnung_gruen(self):
        raw = {"kpi_code": "X", "current_value": "100", "target_value": "100"}
        kpi = KpiSafeValue.from_raw(raw)
        assert kpi.ampel == AmpelStatus.GRUEN

    def test_ampel_berechnung_gelb(self):
        raw = {"kpi_code": "X", "current_value": "85", "target_value": "100"}
        kpi = KpiSafeValue.from_raw(raw)
        assert kpi.ampel == AmpelStatus.GELB

    def test_ampel_berechnung_rot(self):
        raw = {"kpi_code": "X", "current_value": "70", "target_value": "100"}
        kpi = KpiSafeValue.from_raw(raw)
        assert kpi.ampel == AmpelStatus.ROT

    def test_ampel_unbekannt_ohne_ziel(self):
        raw = {"kpi_code": "X", "name": "Test", "current_value": None}
        kpi = KpiSafeValue.from_raw(raw)
        assert kpi.ampel == AmpelStatus.UNBEKANNT

    def test_wert_oder_null_gibt_0_statt_none(self):
        raw = {"kpi_code": "X"}
        kpi = KpiSafeValue.from_raw(raw)
        assert kpi.wert_oder_null == 0.0

    def test_alternative_feldnamen_wert(self):
        raw = {"kpi_code": "X", "wert": "42.5"}
        kpi = KpiSafeValue.from_raw(raw)
        assert kpi.wert == 42.5

    def test_as_dict_vollstaendig(self):
        raw = {"kpi_code": "X", "name": "Test", "current_value": "100", "target_value": "100"}
        d = KpiSafeValue.from_raw(raw).as_dict()
        assert "ampel" in d
        assert "verfuegbarkeit" in d
        assert "ist_verfuegbar" in d
        assert "wert_oder_null" in d


# ---------------------------------------------------------------------------
# TestSafeKpiResponse
# ---------------------------------------------------------------------------

class TestSafeKpiResponse:
    """safe_kpi_response() — niemals Exception, immer KpiSafeValue."""

    def test_normal_raw(self):
        raw = {"kpi_code": "X", "current_value": "50", "target_value": "100"}
        kpi = safe_kpi_response(raw, "X")
        assert isinstance(kpi, KpiSafeValue)

    def test_none_input(self):
        kpi = safe_kpi_response(None, "MISSING")
        assert kpi.kpi_code == "MISSING"
        assert kpi.ist_verfuegbar is False

    def test_kaputter_input_kein_500(self):
        # Absichtlich kaputte Daten — kein Exception erlaubt
        kpi = safe_kpi_response({"current_value": object()})
        assert isinstance(kpi, KpiSafeValue)

    def test_parse_fehler_in_verfuegbarkeit(self):
        kpi = safe_kpi_response(None)
        assert kpi.verfuegbarkeit in (KpiVerfuegbarkeit.LEER, KpiVerfuegbarkeit.PARSE_FEHLER)


# ---------------------------------------------------------------------------
# TestSafeTimeseriesResponse
# ---------------------------------------------------------------------------

class TestSafeTimeseriesResponse:
    """safe_timeseries_response() — niemals Exception, immer TimeseriesSafeResult."""

    def test_normale_liste(self):
        raw = [
            {"periode": "2026-01", "wert": "100", "unit": "EUR"},
            {"periode": "2026-02", "wert": "120", "unit": "EUR"},
        ]
        result = safe_timeseries_response(raw, "UMSATZ")
        assert result.anzahl == 2
        assert result.ist_leer is False
        assert result.eintraege[0].wert == 100.0

    def test_none_ergibt_leer(self):
        result = safe_timeseries_response(None)
        assert result.ist_leer is True
        assert result.anzahl == 0

    def test_leere_liste(self):
        result = safe_timeseries_response([])
        assert result.ist_leer is True

    def test_fehlerhafte_zeile_wird_uebersprungen(self):
        raw = [
            {"periode": "2026-01", "wert": "100"},
            {"periode": "2026-02", "wert": "KAPUTT"},  # ungültig
            {"periode": "2026-03", "wert": "150"},
        ]
        result = safe_timeseries_response(raw)
        assert result.anzahl == 2  # fehlerhafte Zeile übersprungen

    def test_alternative_feldnamen(self):
        raw = [{"period_start": "2026-01", "kpi_value": "99"}]
        result = safe_timeseries_response(raw, "X")
        assert result.anzahl == 1
        assert result.eintraege[0].wert == 99.0

    def test_as_dict_vollstaendig(self):
        result = safe_timeseries_response([], "TEST")
        d = result.as_dict()
        assert d["kpi_code"] == "TEST"
        assert d["ist_leer"] is True
        assert "eintraege" in d


# ---------------------------------------------------------------------------
# TestEvaluateControllingSafety
# ---------------------------------------------------------------------------

class TestEvaluateControllingSafety:
    """evaluate_controlling_safety() — Prüfung auf 500-Risiken."""

    def test_gueltiger_datensatz_ist_safe(self):
        raw = {"kpi_code": "UMSATZ", "name": "Umsatz", "current_value": "100"}
        result = evaluate_controlling_safety(raw)
        assert result.is_safe is True
        assert len(result.errors) == 0

    def test_fehlender_kpi_code_ist_nicht_safe(self):
        result = evaluate_controlling_safety({"name": "Test"})
        assert result.is_safe is False
        assert any("kpi_code" in e for e in result.errors)

    def test_nicht_parsebarer_wert_ist_nicht_safe(self):
        result = evaluate_controlling_safety({"kpi_code": "X", "current_value": "invalid"})
        assert result.is_safe is False
        assert len(result.errors) > 0

    def test_fehlender_name_ist_warnung(self):
        result = evaluate_controlling_safety({"kpi_code": "X", "current_value": "100"})
        assert result.is_safe is True
        assert len(result.warnings) > 0

    def test_as_dict(self):
        result = evaluate_controlling_safety({"kpi_code": "X"})
        d = result.as_dict()
        assert "kpi_code" in d
        assert "is_safe" in d
        assert "errors" in d


# ---------------------------------------------------------------------------
# TestSafeKpiListResponse
# ---------------------------------------------------------------------------

class TestSafeKpiListResponse:
    def test_liste_wird_konvertiert(self):
        raw = [
            {"kpi_code": "A", "current_value": "10"},
            {"kpi_code": "B", "current_value": "20"},
        ]
        result = safe_kpi_list_response(raw)
        assert len(result) == 2

    def test_none_ergibt_leere_liste(self):
        assert safe_kpi_list_response(None) == []

    def test_keine_exception_bei_kaputter_liste(self):
        # Kein Exception erlaubt
        result = safe_kpi_list_response([None, {}, {"kpi_code": "X", "current_value": "5"}])
        assert isinstance(result, list)


# ---------------------------------------------------------------------------
# TestIntegrationSzenario
# ---------------------------------------------------------------------------

class TestIntegrationSzenario:
    def test_typischer_kpi_dashboard_flow(self):
        """Simuliert: Endpoint ruft DB ab, verarbeitet Ergebnisse sicher."""
        db_ergebnis = [
            {"kpi_code": "UMSATZ", "name": "Umsatz", "current_value": "245000",
             "target_value": "250000", "unit": "EUR"},
            {"kpi_code": "MARGE",  "name": "Marge",  "current_value": None,
             "target_value": "15", "unit": "%"},
        ]
        kpis = safe_kpi_list_response(db_ergebnis)
        assert len(kpis) == 2
        assert kpis[0].ampel == AmpelStatus.GRUEN  # 98% von Ziel >= 95% → GRUEN
        assert kpis[1].ist_verfuegbar is False
        assert kpis[1].ampel == AmpelStatus.UNBEKANNT

    def test_timeseries_mit_luecken(self):
        """Zeitreihe mit einzelnen fehlerhaften Zeilen — kein 500."""
        raw = [
            {"period_start": "2026-01", "kpi_value": "100"},
            {"period_start": "2026-02"},       # wert fehlt komplett
            {"period_start": "2026-03", "kpi_value": "110"},
        ]
        result = safe_timeseries_response(raw)
        # Zeilen ohne Wert werden mit 0.0 oder übersprungen
        assert result.anzahl >= 2

    def test_keine_500_bei_leerem_schema(self):
        """Simuliert: Schema nicht vorhanden → safe_kpi_response gibt leer zurück."""
        kpi = safe_kpi_response(None, "KEIN_SCHEMA")
        assert kpi.kpi_code == "KEIN_SCHEMA"
        assert kpi.verfuegbarkeit == KpiVerfuegbarkeit.LEER
        assert kpi.fehler_meldung != ""
